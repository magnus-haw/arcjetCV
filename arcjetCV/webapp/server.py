"""arcjetCV Web: a local, browser-based interface for arcjetCV.

Everything runs on the user's own machine. The server binds to 127.0.0.1 by
default, reads videos straight from disk and writes outputs next to them,
exactly like the desktop GUI.

Launch with ``arcjetcv-web`` (or ``python -m arcjetCV.webapp``).

The same page can also be hosted on a website while the processing still runs
here: ``arcjetcv-web --site https://example.org/arcjetcv/`` allows that site to
talk to this engine (with an access token) and opens it already connected.
``arcjetcv-web --export-site DIR`` writes the static files to upload.
"""

import argparse
import base64
import ipaddress
import json
import os
import secrets
import shutil
import threading
import time
import traceback
import uuid
import webbrowser
from urllib.parse import urlsplit

import cv2 as cv
import numpy as np

try:
    from flask import Flask, Response, jsonify, request, send_from_directory
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "arcjetCV Web needs Flask. Install it with:\n\n"
        "    pip install flask\n\n"
        "or  pip install 'arcjetcv[web]'"
    ) from exc

import arcjetCV
from arcjetCV.utils.output import NumpyEncoder
from arcjetCV.utils.utils import annotate_image_with_frame_number, annotateImage
from arcjetCV.utils.video import Video, VideoMeta
from arcjetCV.webapp import analysis
from arcjetCV.webapp import calibration as calib
from arcjetCV.webapp import native_dialog

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".arcjetCV")
RECENT_FILE = os.path.join(CONFIG_DIR, "web_recent.json")
WORKSPACE_DIR = os.path.join(os.path.expanduser("~"), "arcjetCV_workspace")
TOKEN_FILE = os.path.join(CONFIG_DIR, "web_token")
SITES_FILE = os.path.join(CONFIG_DIR, "web_sites.json")

# Websites allowed to use this engine without passing --site. Add the
# official hosted page here once it has a permanent address.
DEFAULT_SITES = ["https://flying-squirrel.space"]

VIDEO_EXT = {".mp4", ".avi", ".mov", ".m4v", ".mkv", ".png", ".jpg", ".jpeg",
             ".bmp", ".tif", ".tiff"}
JSON_EXT = {".json"}

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
app.json.sort_keys = False

SESSIONS = {}  # sid -> dict(video, meta, processor, lock, path)
JOBS = {}  # jid -> dict(status, progress, message, result, error, cancel)
_state_lock = threading.Lock()

# Access control for the hosted page (see _guard below).
ACCESS = {"token": None, "origins": set(), "loopback": True}
PUBLIC_PATHS = {"/api/ping", "/api/calibration/pattern.pdf"}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _json(obj, status=200):
    return Response(json.dumps(obj, cls=NumpyEncoder, allow_nan=False, default=str),
                    status=status, mimetype="application/json")


def _err(msg, status=400):
    return _json({"error": str(msg)}, status)


def _safe(obj):
    """Replace NaN/inf so JSON stays valid."""
    if isinstance(obj, dict):
        return {k: _safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_safe(v) for v in obj]
    if isinstance(obj, (float, np.floating)):
        return float(obj) if np.isfinite(obj) else None
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return _safe(obj.tolist())
    return obj


def _load_recent():
    try:
        with open(RECENT_FILE) as f:
            return json.load(f)
    except Exception:
        return {"videos": [], "outputs": []}


def _push_recent(kind, path):
    data = _load_recent()
    items = [p for p in data.get(kind, []) if p != path]
    data[kind] = ([path] + items)[:12]
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(RECENT_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


def _new_job(kind):
    jid = uuid.uuid4().hex[:12]
    job = {"id": jid, "kind": kind, "status": "running", "progress": 0,
           "message": "Starting...", "result": None, "error": None,
           "cancel": threading.Event(), "started": time.time()}
    with _state_lock:
        JOBS[jid] = job
    return job


def _run_job(job, fn):
    def target():
        try:
            job["result"] = fn(job)
            if job["cancel"].is_set():
                job["status"] = "cancelled"
                job["message"] = "Cancelled."
            else:
                job["status"] = "done"
                job["progress"] = 100
        except Exception as exc:
            traceback.print_exc()
            job["status"] = "error"
            job["error"] = f"{type(exc).__name__}: {exc}"
    threading.Thread(target=target, daemon=True).start()


def _session(sid):
    s = SESSIONS.get(sid)
    if s is None:
        raise KeyError("Video session not found. Please reopen the video.")
    return s


def _options_from(params):
    """Build the processor option dict exactly like MainWindow.grab_ui_values."""
    p = params or {}
    method = p.get("method", "AutoHSV")
    model = p.get("hsv_model", [[0, 0, 150], [121, 125, 255]])
    shock = p.get("hsv_shock", [[125, 40, 85], [170, 80, 230]])
    opts = {
        "SEGMENT_METHOD": method,
        "HSV_MODEL_RANGE": [tuple(int(v) for v in model[0]), tuple(int(v) for v in model[1])],
        "HSV_SHOCK_RANGE": [tuple(int(v) for v in shock[0]), tuple(int(v) for v in shock[1])],
        "THRESHOLD": int(p.get("threshold", model[0][2])),
    }
    return opts


def _apply_geometry(sess, params):
    meta, proc = sess["meta"], sess["processor"]
    crop = params.get("crop")
    if crop:
        ymin, ymax, xmin, xmax = (int(crop[k]) for k in ("ymin", "ymax", "xmin", "xmax"))
        h, w = meta["HEIGHT"], meta["WIDTH"]
        ymin, ymax = sorted((max(0, min(h, ymin)), max(0, min(h, ymax))))
        xmin, xmax = sorted((max(0, min(w, xmin)), max(0, min(w, xmax))))
        if ymax - ymin < 4 or xmax - xmin < 4:
            raise ValueError("Crop region is too small.")
        meta.set_frame_crop(ymin, ymax, xmin, xmax)
    flow = params.get("flow_direction")
    if flow in ("left", "right"):
        meta["FLOW_DIRECTION"] = flow
    proc.update_video_meta(meta)
    if proc.flow_dir is None:
        proc.flow_dir = "right"
    ppm = params.get("pixels_per_mm")
    if ppm not in (None, ""):
        try:
            ppm = float(ppm)
            if ppm > 0:
                meta["PIXELS_PER_MM"] = ppm
                proc.pixels_per_mm = ppm
        except (TypeError, ValueError):
            pass


def _encode_jpeg(rgb, max_w=1400, quality=85):
    img = cv.cvtColor(rgb, cv.COLOR_RGB2BGR)
    h, w = img.shape[:2]
    if w > max_w:
        img = cv.resize(img, (max_w, int(h * max_w / w)), interpolation=cv.INTER_AREA)
    ok, buf = cv.imencode(".jpg", img, [cv.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("Could not encode frame.")
    return buf.tobytes()


def _session_summary(sid):
    s = SESSIONS[sid]
    meta, video = s["meta"], s["video"]
    return _safe({
        "sid": sid,
        "path": s["path"],
        "name": video.name,
        "folder": video.folder,
        "width": meta["WIDTH"],
        "height": meta["HEIGHT"],
        "nframes": meta["NFRAMES"],
        "fps": video.fps,
        "first_good": meta["FIRST_GOOD_FRAME"],
        "last_good": min(meta["LAST_GOOD_FRAME"] or 0, max(0, (meta["NFRAMES"] or 1) - 1)),
        "flow_direction": meta.get("FLOW_DIRECTION") or "right",
        "crop": {"ymin": meta["CROP_YMIN"], "ymax": meta["CROP_YMAX"],
                 "xmin": meta["CROP_XMIN"], "xmax": meta["CROP_XMAX"]},
        "pixels_per_mm": meta.get("PIXELS_PER_MM"),
        "brightness": meta.get("BRIGHTNESS") or [],
        "outputs": _list_outputs(video.folder, video.name),
    })


def _list_outputs(folder, name):
    try:
        out = []
        for f in sorted(os.listdir(folder)):
            if f.startswith(name) and f.endswith(".json"):
                p = os.path.join(folder, f)
                out.append({"name": f, "path": p, "size": os.path.getsize(p),
                            "mtime": os.path.getmtime(p)})
        return out
    except Exception:
        return []


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# Access control
#
# The page served by this engine (same origin) needs nothing extra. A page
# hosted on an allowed website must send the access token. Everything else is
# refused, which also stops random websites from driving the local engine.
# --------------------------------------------------------------------------
def _origin_of(url):
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ValueError(f"Not a web address: {url}")
    return f"{parts.scheme}://{parts.netloc}".lower()


def _load_token():
    try:
        with open(TOKEN_FILE) as f:
            tok = f.read().strip()
        if len(tok) >= 20:
            return tok
    except OSError:
        pass
    tok = secrets.token_urlsafe(24)
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        f.write(tok)
    try:
        os.chmod(TOKEN_FILE, 0o600)
    except OSError:
        pass
    return tok


def _load_sites():
    try:
        with open(SITES_FILE) as f:
            return [s for s in json.load(f) if isinstance(s, str)]
    except (OSError, ValueError):
        return []


def _save_sites(sites):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(SITES_FILE, "w") as f:
        json.dump(sorted(set(sites)), f, indent=2)


def _is_loopback_host(host_header):
    host = (host_header or "").rsplit(":", 1)[0].strip("[]").lower()
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _request_token():
    return request.headers.get("X-ArcjetCV-Token") or request.args.get("token")


def _token_ok():
    tok = _request_token()
    return bool(tok and ACCESS["token"] and secrets.compare_digest(tok, ACCESS["token"]))


def _same_origin():
    site = request.headers.get("Sec-Fetch-Site")
    if site is not None:
        return site in ("same-origin", "none")
    origin = request.headers.get("Origin")
    return origin is None or urlsplit(origin).netloc == request.host


def _cors(resp):
    origin = request.headers.get("Origin")
    if origin and (origin.lower() in ACCESS["origins"] or request.path == "/api/ping"):
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-ArcjetCV-Token"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        resp.headers["Access-Control-Allow-Private-Network"] = "true"
        resp.headers["Access-Control-Max-Age"] = "600"
    return resp


@app.before_request
def _guard():
    # DNS rebinding: when bound to this computer only, refuse other host names.
    if ACCESS["loopback"] and not _is_loopback_host(request.host):
        return _err("Unknown host.", 403)
    if not request.path.startswith("/api/"):
        return None
    if request.method == "OPTIONS":
        return _cors(Response(status=204))
    if request.path in PUBLIC_PATHS or _same_origin():
        return None
    origin = (request.headers.get("Origin") or "").lower()
    if origin and origin not in ACCESS["origins"]:
        return _cors(_err("This website is not allowed to use this arcjetCV engine. "
                          f"Start it with: arcjetcv-web --site {origin}", 403))
    if not _token_ok():
        return _cors(_err("Missing or wrong access token.", 401))
    return None


@app.after_request
def _after(resp):
    return _cors(resp)


@app.get("/api/ping")
def api_ping():
    origin = (request.headers.get("Origin") or "").lower()
    return _json({
        "app": "arcjetCV",
        "version": arcjetCV.__version__,
        "origin_allowed": _same_origin() or origin in ACCESS["origins"],
        "token_ok": _same_origin() or _token_ok(),
        "native_dialogs": native_dialog.available(),
    })


# --------------------------------------------------------------------------
# Native file windows
# --------------------------------------------------------------------------
@app.post("/api/dialog")
def api_dialog():
    """Open the operating system's own Open/Save window on this computer."""
    if not ipaddress.ip_address(request.remote_addr or "0.0.0.0").is_loopback:
        return _err("Native file windows are only available on this computer.", 501)
    p = request.get_json(force=True) or {}
    mode = "save" if p.get("mode") == "save" else "open"
    kind = p.get("kind", "video")
    exts = {"json": JSON_EXT, "image": calib.IMAGE_EXT, "video": VIDEO_EXT}.get(kind, set())
    try:
        paths = native_dialog.ask(
            mode=mode, title=str(p.get("title") or ("Save" if mode == "save" else "Open")),
            start=p.get("start"), multi=bool(p.get("multi")), exts=exts,
            name=str(p.get("name") or "calibration.json"))
    except native_dialog.DialogUnavailable as exc:
        return _err(exc, 501)
    except native_dialog.DialogBusy as exc:
        return _err(exc, 409)
    except Exception as exc:
        return _err(f"The file window failed: {exc}", 500)
    if not paths:
        return _json({"cancelled": True, "paths": []})
    return _json({"cancelled": False, "paths": paths})


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(STATIC_DIR, "img"), "favicon.ico")


# --------------------------------------------------------------------------
# General API
# --------------------------------------------------------------------------
@app.get("/api/info")
def api_info():
    recent = _load_recent()
    recent = {k: [p for p in v if os.path.exists(p)] for k, v in recent.items()}
    try:
        import torch  # noqa: F401
        cnn = True
    except Exception:
        cnn = False
    return _json({
        "version": arcjetCV.__version__,
        "home": os.path.expanduser("~"),
        "workspace": WORKSPACE_DIR,
        "cwd": os.getcwd(),
        "recent": recent,
        "cnn_available": cnn,
        "open_sessions": len(SESSIONS),
        "jobs_running": sum(1 for j in JOBS.values() if j["status"] == "running"),
    })


@app.get("/api/browse")
def api_browse():
    kind = request.args.get("kind", "video")
    path = request.args.get("path") or os.getcwd()
    path = os.path.abspath(os.path.expanduser(path))
    if os.path.isfile(path):
        path = os.path.dirname(path)
    if not os.path.isdir(path):
        return _err(f"Folder not found: {path}", 404)
    exts = {"json": JSON_EXT, "image": calib.IMAGE_EXT}.get(kind, VIDEO_EXT)
    dirs, files = [], []
    try:
        names = sorted(os.listdir(path), key=str.lower)
    except PermissionError:
        return _err(f"Permission denied: {path}", 403)
    for n in names:
        if n.startswith("."):
            continue
        p = os.path.join(path, n)
        try:
            if os.path.isdir(p):
                dirs.append({"name": n, "path": p, "type": "dir"})
            elif os.path.splitext(n)[1].lower() in exts:
                st = os.stat(p)
                files.append({"name": n, "path": p, "type": "file",
                              "size": st.st_size, "mtime": st.st_mtime})
        except OSError:
            continue
    parent = os.path.dirname(path)
    return _json({"path": path, "parent": parent if parent != path else None,
                  "entries": dirs + files})


@app.post("/api/upload")
def api_upload():
    f = request.files.get("file")
    if f is None or not f.filename:
        return _err("No file received.")
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    name = os.path.basename(f.filename).replace(" ", "_")
    dest = os.path.join(WORKSPACE_DIR, name)
    f.save(dest)
    return _json({"path": dest})


@app.get("/api/jobs/<jid>")
def api_job(jid):
    job = JOBS.get(jid)
    if job is None:
        return _err("Job not found.", 404)
    return _json(_safe({k: v for k, v in job.items() if k != "cancel"}))


@app.post("/api/jobs/<jid>/cancel")
def api_job_cancel(jid):
    job = JOBS.get(jid)
    if job is None:
        return _err("Job not found.", 404)
    job["cancel"].set()
    job["message"] = "Cancelling..."
    return _json({"ok": True})


# --------------------------------------------------------------------------
# Video API
# --------------------------------------------------------------------------
@app.post("/api/video/open")
def api_video_open():
    body = request.get_json(force=True) or {}
    path = os.path.abspath(os.path.expanduser(body.get("path", "")))
    if not os.path.isfile(path):
        return _err(f"File not found: {path}", 404)

    job = _new_job("open")

    def work(job):
        from arcjetCV.utils.processor import ArcjetProcessor

        def progress(pct, msg):
            job["progress"] = int(pct)
            job["message"] = msg
            if job["cancel"].is_set():
                raise RuntimeError("Loading cancelled.")

        job["message"] = "Opening video file..."
        video = Video(path)
        meta = VideoMeta(video, os.path.join(video.folder, video.name + ".meta"),
                         progress_callback=progress)
        if meta.get("FLOW_DIRECTION") is None:
            meta["FLOW_DIRECTION"] = "right"
        job["message"] = "Initializing processor..."
        proc = ArcjetProcessor(meta)
        sid = uuid.uuid4().hex[:12]
        with _state_lock:
            SESSIONS[sid] = {"video": video, "meta": meta, "processor": proc,
                             "lock": threading.Lock(), "path": path}
        _push_recent("videos", path)
        return _session_summary(sid)

    _run_job(job, work)
    return _json({"job": job["id"]})


@app.get("/api/video/<sid>")
def api_video(sid):
    try:
        _session(sid)
    except KeyError as e:
        return _err(e, 404)
    return _json(_session_summary(sid))


@app.post("/api/video/<sid>/close")
def api_video_close(sid):
    s = SESSIONS.pop(sid, None)
    if s:
        try:
            s["video"].close()
        except Exception:
            pass
    return _json({"ok": True})


@app.get("/api/video/<sid>/frame/<int:idx>")
def api_frame(sid, idx):
    try:
        s = _session(sid)
    except KeyError as e:
        return _err(e, 404)
    with s["lock"]:
        frame = s["video"].get_frame(int(idx))
    if frame is None:
        return _err("Frame not available.", 404)
    return Response(_encode_jpeg(frame), mimetype="image/jpeg")


@app.post("/api/video/<sid>/preview")
def api_preview(sid):
    try:
        s = _session(sid)
    except KeyError as e:
        return _err(e, 404)
    p = request.get_json(force=True) or {}
    idx = int(p.get("index", 0))
    try:
        with s["lock"]:
            _apply_geometry(s, p)
            frame = s["video"].get_frame(idx)
            if frame is None:
                return _err("Frame not available.", 404)
            t0 = time.time()
            edges, argdict = s["processor"].process(frame, _options_from(p))
            elapsed = time.time() - t0
    except Exception as exc:
        traceback.print_exc()
        return _err(f"Segmentation failed: {type(exc).__name__}: {exc}", 500)

    thick = max(1, frame.shape[1] // 500)
    if edges.get("MODEL") is not None:
        cv.drawContours(frame, edges["MODEL"], -1, (0, 255, 0), thick + 1)
    if p.get("show_shock", True) and edges.get("SHOCK") is not None:
        cv.drawContours(frame, edges["SHOCK"], -1, (255, 0, 255), thick + 1)
    annotate_image_with_frame_number(frame, idx)
    if p.get("annotate", False):
        annotateImage(frame, argdict, top=True, left=True)
    if p.get("show_crop", True):
        c = s["processor"].crop
        cv.rectangle(frame, (c[1][0], c[0][0]), (c[1][1], c[0][1]), (255, 255, 255), thick)

    jpg = base64.b64encode(_encode_jpeg(frame)).decode("ascii")
    keep = ["MODEL_VISIBLE", "OVEREXPOSED", "UNDEREXPOSED", "PIXEL_MIN", "PIXEL_MAX",
            "MODEL_AREA", "SHOCK_AREA", "MODEL_RADIUS", "MODEL_YCENTER",
            "MODEL_INTERP_XPOS", "SHOCK_INTERP_XPOS", "MODEL_CENTROID_X", "MODEL_CENTROID_Y"]
    metrics = {k: argdict.get(k) for k in keep if k in argdict}
    metrics["MODEL_FOUND"] = edges.get("MODEL") is not None
    metrics["SHOCK_FOUND"] = edges.get("SHOCK") is not None
    metrics["ELAPSED_S"] = round(elapsed, 3)
    return _json(_safe({"image": "data:image/jpeg;base64," + jpg, "metrics": metrics}))


@app.post("/api/video/<sid>/meta")
def api_video_meta(sid):
    try:
        s = _session(sid)
    except KeyError as e:
        return _err(e, 404)
    p = request.get_json(force=True) or {}
    try:
        with s["lock"]:
            _apply_geometry(s, p)
            meta = s["meta"]
            if "first_good" in p:
                meta["FIRST_GOOD_FRAME"] = int(p["first_good"])
            if "last_good" in p:
                meta["LAST_GOOD_FRAME"] = int(p["last_good"])
            if "notes" in p:
                meta["NOTES"] = p["notes"]
            meta.write()
    except Exception as exc:
        return _err(exc)
    return _json(_session_summary(sid))


@app.post("/api/video/<sid>/process")
def api_process(sid):
    from arcjetCV.utils.processor import ArcjetProcessor

    try:
        s = _session(sid)
    except KeyError as e:
        return _err(e, 404)
    p = request.get_json(force=True) or {}
    try:
        with s["lock"]:
            _apply_geometry(s, p)
            meta = s["meta"]
            nmax = max(0, meta["NFRAMES"] - 1)
            first = max(0, min(nmax, int(p.get("first", meta["FIRST_GOOD_FRAME"]))))
            last = max(first, min(nmax, int(p.get("last", meta["LAST_GOOD_FRAME"]))))
            stride = max(1, int(p.get("stride", 1)))
            meta["FIRST_GOOD_FRAME"], meta["LAST_GOOD_FRAME"] = first, last
            meta.write()
            proc = ArcjetProcessor(meta)
            proc.flow_dir = meta.get("FLOW_DIRECTION") or "right"
            proc.pixels_per_mm = meta.get("PIXELS_PER_MM", 1.0)
            proc.cnn = s["processor"].cnn  # reuse a loaded CNN model
    except Exception as exc:
        return _err(exc)

    options = _options_from(p)
    prefix = (p.get("output_prefix") or s["video"].name).strip().replace(" ", "_")
    write_video = bool(p.get("write_video", False))
    show_shock = bool(p.get("show_shock", True))
    path = s["path"]
    job = _new_job("process")
    job["message"] = f"Processing frames {first}-{last} (stride {stride})"
    job["meta"] = {"sid": sid, "first": first, "last": last, "stride": stride,
                   "method": options["SEGMENT_METHOD"]}

    def work(job):
        video = Video(path)  # private capture so previews stay responsive
        try:
            def progress(pct, frame_index):
                job["progress"] = int(pct)
                job["message"] = f"Frame {frame_index} of {last}  ({options['SEGMENT_METHOD']})"

            proc.process_all(video, options, first, last, stride,
                             output_prefix=prefix, write_json=True,
                             write_video=write_video, display_shock=show_shock,
                             progress_callback=progress, cancel_event=job["cancel"])
            out_path = os.path.join(video.folder, proc.filename)
            if not job["cancel"].is_set():
                _push_recent("outputs", out_path)
            return {"output": out_path, "sid": sid}
        finally:
            video.close()

    _run_job(job, work)
    return _json({"job": job["id"]})


# --------------------------------------------------------------------------
# Results API
# --------------------------------------------------------------------------
def _analysis_args(p):
    paths = p.get("paths") or []
    if not paths:
        raise ValueError("Select at least one output file.")
    for path in paths:
        if not os.path.isfile(os.path.expanduser(path)):
            raise ValueError(f"File not found: {path}")
    return dict(paths=paths, fps=p.get("fps", 30), mask_n=p.get("mask_n", 1),
                units=p.get("units", "px"), ppm=p.get("pixels_per_mm"),
                flow_direction=p.get("flow_direction"),
                use_kalman=bool(p.get("kalman", False)),
                outlier_mask=bool(p.get("outlier_mask", True)))


@app.post("/api/results/analyze")
def api_results_analyze():
    p = request.get_json(force=True) or {}
    try:
        res = analysis.build(**_analysis_args(p))
        for path in p["paths"]:
            _push_recent("outputs", os.path.abspath(os.path.expanduser(path)))
    except Exception as exc:
        traceback.print_exc()
        return _err(exc)
    return _json(_safe(res))


@app.post("/api/results/fit")
def api_results_fit():
    p = request.get_json(force=True) or {}
    try:
        res = analysis.build(**_analysis_args(p))
        fits = analysis.linear_fits(res, p.get("t0", 0), p.get("t1", 1e9), p.get("keys"))
    except Exception as exc:
        return _err(exc)
    return _json(_safe({"fits": fits, "units": res["units"]}))


@app.post("/api/results/csv")
def api_results_csv():
    p = request.get_json(force=True) or {}
    try:
        res = analysis.build(**_analysis_args(p))
    except Exception as exc:
        return _err(exc)
    name = os.path.splitext(os.path.basename(p["paths"][0]))[0] + "_timeseries.csv"
    return Response(analysis.to_csv(res), mimetype="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{name}"'})


# --------------------------------------------------------------------------
# Calibration API (mirrors the desktop Calibration tab)
# --------------------------------------------------------------------------
def _image_payload(rgb):
    h, w = rgb.shape[:2]
    jpg = base64.b64encode(_encode_jpeg(rgb, max_w=1800, quality=88)).decode("ascii")
    return {"image": "data:image/jpeg;base64," + jpg, "width": w, "height": h}


@app.post("/api/calibration/image")
def api_calibration_image():
    p = request.get_json(force=True) or {}
    try:
        bgr = calib.read_image(os.path.abspath(os.path.expanduser(p.get("path", ""))))
    except ValueError as exc:
        return _err(exc)
    out = _image_payload(cv.cvtColor(bgr, cv.COLOR_BGR2RGB))
    out["path"] = p.get("path")
    return _json(out)


@app.post("/api/calibration/pattern")
def api_calibration_pattern():
    p = request.get_json(force=True) or {}
    path = os.path.abspath(os.path.expanduser(p.get("path", "")))
    try:
        data, rgb, diag_px, ptype = calib.measure_pattern(
            path, p.get("cols", 4), p.get("rows", 9), p.get("diagonal_mm"))
    except ValueError as exc:
        return _err(exc)
    except Exception as exc:
        traceback.print_exc()
        return _err(f"Pattern calibration failed: {type(exc).__name__}: {exc}", 500)
    out = _image_payload(rgb)
    out.update({"calibration": data, "diagonal_px": diag_px, "pattern_type": ptype,
                "pixels_per_mm": data.get("pixels_per_mm")})
    return _json(_safe(out))


@app.post("/api/calibration/load")
def api_calibration_load():
    p = request.get_json(force=True) or {}
    path = os.path.abspath(os.path.expanduser(p.get("path", "")))
    try:
        data = calib.load_calibration(path)
    except ValueError as exc:
        return _err(exc)
    return _json(_safe({"path": path, "calibration": data,
                        "pixels_per_mm": data.get("pixels_per_mm"),
                        "has_camera_model": calib.has_camera_model(data),
                        "keys": sorted(data.keys())}))


@app.post("/api/calibration/save")
def api_calibration_save():
    p = request.get_json(force=True) or {}
    try:
        path = calib.save_calibration(p.get("path", ""), p.get("calibration") or {})
    except ValueError as exc:
        return _err(exc)
    except OSError as exc:
        return _err(f"Could not write file: {exc}")
    return _json({"path": path})


@app.get("/api/calibration/pattern.pdf")
def api_calibration_pdf():
    if not calib.PATTERN_PDF.exists():
        return _err("Calibration pattern PDF is not installed.", 404)
    return send_from_directory(str(calib.PATTERN_PDF.parent), calib.PATTERN_PDF.name)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
def export_site(dest):
    """Copy the page to a folder ready to upload to a website (hosted mode)."""
    dest = os.path.abspath(os.path.expanduser(dest))
    if os.path.exists(dest) and os.listdir(dest):
        raise SystemExit(f"Folder is not empty: {dest}")
    shutil.copytree(STATIC_DIR, os.path.join(dest, "static"),
                    ignore=shutil.ignore_patterns("index.html", ".DS_Store"))
    with open(os.path.join(STATIC_DIR, "index.html"), encoding="utf-8") as f:
        html = f.read()
    html = html.replace('<meta name="arcjetcv-mode" content="local">',
                        '<meta name="arcjetcv-mode" content="hosted">', 1)
    with open(os.path.join(dest, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    # Lets GitHub Pages serve the folder as is.
    open(os.path.join(dest, ".nojekyll"), "w").close()
    return dest


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="arcjetcv-web",
        description="Launch the arcjetCV browser interface (runs locally).")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Interface to bind (default 127.0.0.1, this computer only).")
    parser.add_argument("--port", type=int, default=5050, help="Port (default 5050).")
    parser.add_argument("--no-browser", action="store_true",
                        help="Do not open a browser window automatically.")
    parser.add_argument("--site", metavar="URL",
                        help="Use the arcjetCV page hosted at URL: allow that website to "
                             "use this engine (remembered) and open it connected.")
    parser.add_argument("--forget-sites", action="store_true",
                        help="Remove all remembered websites, then continue.")
    parser.add_argument("--export-site", metavar="DIR",
                        help="Write the static page for hosting on a website, then exit.")
    parser.add_argument("--debug", action="store_true", help="Flask debug mode.")
    args = parser.parse_args(argv)

    if args.export_site:
        dest = export_site(args.export_site)
        print(f"\n  Hosted page written to {dest}")
        print("  Upload the folder's contents to your website. Users then run:")
        print("      pip install 'arcjetcv[web]'")
        print("      arcjetcv-web --site https://<your site>/<path>/\n")
        return

    if args.forget_sites:
        _save_sites([])
    sites = set(_load_sites())
    site_url = None
    if args.site:
        try:
            origin = _origin_of(args.site)
        except ValueError as exc:
            parser.error(str(exc))
        sites.add(origin)
        _save_sites(sites)
        site_url = args.site.split("#", 1)[0]

    ACCESS["token"] = _load_token()
    ACCESS["origins"] = {o.lower() for o in sites} | {_origin_of(s) for s in DEFAULT_SITES}
    ACCESS["loopback"] = args.host in ("127.0.0.1", "localhost", "::1")

    local_url = f"http://{'localhost' if args.host in ('127.0.0.1', '0.0.0.0') else args.host}:{args.port}"
    print("\n  arcjetCV Web " + arcjetCV.__version__)
    print(f"  Local page:  {local_url}")
    if ACCESS["origins"]:
        print("  Websites allowed to use this engine: " + ", ".join(sorted(ACCESS["origins"])))
    open_url = local_url
    if site_url:
        open_url = f"{site_url}#connect={args.port}:{ACCESS['token']}"
        print(f"  Hosted page: {site_url}")
        print(f"  Connect link (keep private): {open_url}")
    print("  Press Ctrl+C to stop.\n")
    if not args.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(open_url)).start()
    app.run(host=args.host, port=args.port, debug=args.debug,
            threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
