"""Turn arcjetCV output JSON files into plot-ready time series.

The math mirrors ``MainWindow.plot_outputs`` / ``MainWindow.fit_data`` in the
desktop GUI so both interfaces report the same numbers.
"""

import csv
import io
import json
import os
import threading

import numpy as np

from arcjetCV.utils.utils import getOutlierMask

_cache = {}
_cache_lock = threading.Lock()

# key, label, unit kind ("len" or "area")
SERIES = [
    ("MODEL_-0.95R", "Model -95%R", "len"),
    ("MODEL_-0.50R", "Model -50%R", "len"),
    ("MODEL_CENTER", "Model center", "len"),
    ("MODEL_0.50R", "Model +50%R", "len"),
    ("MODEL_0.95R", "Model +95%R", "len"),
    ("SHOCK_CENTER", "Shock center", "len"),
    ("SHOCK_TO_MODEL", "Shock-model distance", "len"),
    ("MODEL_RADIUS", "Model radius", "len"),
    ("MODEL_YPOS", "Axis position", "len"),
    ("MODEL_AREA", "Model area", "area"),
    ("SHOCK_AREA", "Shock area", "area"),
]


def load_outputs(paths):
    """Load and concatenate output JSON lists (cached by path + mtime)."""
    frames = []
    for path in paths:
        path = os.path.abspath(os.path.expanduser(path))
        mtime = os.path.getmtime(path)
        with _cache_lock:
            hit = _cache.get(path)
        if hit is None or hit[0] != mtime:
            with open(path, "r") as fin:
                data = json.load(fin)
            with _cache_lock:
                _cache[path] = (mtime, data)
        else:
            data = hit[1]
        frames.extend(data)
    frames.sort(key=lambda d: d.get("INDEX", 0))
    return frames


def flow_sign(flow_direction):
    flow = str(flow_direction or "").strip().lower()
    return -1.0 if flow in {"left", "up"} else 1.0


def kalman(series):
    """Same scalar Kalman smoother as the desktop GUI (NaN-aware)."""
    data = np.array(series, dtype=float)
    valid = np.isfinite(data)
    if np.count_nonzero(valid) <= 1:
        return data
    measurement_var = np.nanvar(data[valid])
    if not np.isfinite(measurement_var) or measurement_var <= 1e-12:
        measurement_var = 1.0
    process_var = measurement_var * 0.05 or 1e-3
    err = measurement_var
    idx = np.flatnonzero(valid)
    est = data[idx[0]]
    out = data.copy()
    for i in idx[1:]:
        err += process_var
        gain = err / (err + measurement_var)
        est = est + gain * (data[i] - est)
        err = (1.0 - gain) * err
        out[i] = est
    return out


def _clean(arr):
    return [None if not np.isfinite(v) else round(float(v), 6) for v in arr]


def _contour_xy(contour, scale):
    pts = np.asarray(contour, dtype=float).reshape(-1, 2) * scale
    # Downsample long contours so the browser stays responsive
    step = max(1, len(pts) // 400)
    return pts[::step].round(3).tolist()


def build(paths, fps=30.0, mask_n=1, units="px", ppm=None, flow_direction=None,
          use_kalman=False, outlier_mask=True):
    raw = load_outputs(paths)
    if len(raw) == 0:
        raise ValueError("No frames found in the selected output files.")

    fps = float(fps) if fps else 30.0
    mask_n = max(1, int(mask_n or 1))
    if flow_direction in (None, "", "auto"):
        flow_direction = raw[0].get("FLOW_DIRECTION") or "right"
    sign = flow_sign(flow_direction)

    if not ppm:
        ppm = raw[0].get("PIXELS_PER_MM")
    try:
        ppm = float(ppm) if ppm not in (None, 0, "") else None
    except (TypeError, ValueError):
        ppm = None
    use_mm = units == "mm" and ppm not in (None, 0) and np.isfinite(ppm)
    scale = (1.0 / ppm) if use_mm else 1.0
    unit_label = "mm" if use_mm else "px"

    cols = {k: [] for k, _, _ in SERIES}
    index, time = [], []
    model_profiles, shock_profiles, centroids = [], {}, []

    for loop_idx, i in enumerate(range(0, len(raw), mask_n)):
        fr = raw[i]
        index.append(fr.get("INDEX", i))
        time.append(fr.get("INDEX", i) / fps)
        has_model = fr.get("MODEL") is not None and fr.get("MODEL_INTERP_XPOS") is not None
        has_shock = fr.get("SHOCK") is not None and fr.get("SHOCK_INTERP_XPOS") is not None

        if has_model:
            xpos = sign * np.asarray(fr["MODEL_INTERP_XPOS"], dtype=float)
            for k, v in zip(["MODEL_-0.95R", "MODEL_-0.50R", "MODEL_CENTER",
                             "MODEL_0.50R", "MODEL_0.95R"], xpos[:5]):
                cols[k].append(v)
            cols["MODEL_YPOS"].append(fr.get("MODEL_YCENTER", np.nan))
            cols["MODEL_RADIUS"].append(fr.get("MODEL_RADIUS", np.nan))
            cols["MODEL_AREA"].append(fr.get("MODEL_AREA", np.nan))
            model_profiles.append((loop_idx, fr["MODEL"]))
            centroids.append((len(model_profiles) - 1, fr.get("MODEL_CENTROID_X")))
        else:
            for k in ["MODEL_-0.95R", "MODEL_-0.50R", "MODEL_CENTER", "MODEL_0.50R",
                      "MODEL_0.95R", "MODEL_YPOS", "MODEL_RADIUS", "MODEL_AREA"]:
                cols[k].append(np.nan)

        if has_shock:
            sc = sign * float(np.asarray(fr["SHOCK_INTERP_XPOS"], dtype=float).ravel()[0])
            cols["SHOCK_CENTER"].append(sc)
            cols["SHOCK_AREA"].append(fr.get("SHOCK_AREA", np.nan))
            shock_profiles[loop_idx] = fr["SHOCK"]
        else:
            cols["SHOCK_CENTER"].append(np.nan)
            cols["SHOCK_AREA"].append(np.nan)

        if has_model and has_shock:
            cols["SHOCK_TO_MODEL"].append(abs(cols["SHOCK_CENTER"][-1] - cols["MODEL_CENTER"][-1]))
        else:
            cols["SHOCK_TO_MODEL"].append(np.nan)

    n = len(time)
    time = np.asarray(time, dtype=float)
    arrays = {k: np.asarray(v, dtype=float) for k, v in cols.items()}

    # Outlier mask (LOF), same metrics as the GUI
    mask = np.ones(n, dtype=int)
    if outlier_mask and n > 10:
        try:
            mask = np.asarray(getOutlierMask([
                arrays["MODEL_AREA"], arrays["MODEL_YPOS"],
                arrays["MODEL_RADIUS"], arrays["MODEL_CENTER"]]))
        except Exception:
            mask = np.ones(n, dtype=int)
    bad = mask < 0

    for k, _, kind in SERIES:
        a = arrays[k].copy()
        a[bad] = np.nan
        if kind == "len":
            a = a * scale
        if use_kalman:
            a = kalman(a)
        arrays[k] = a

    # Recession summary from the model center (zeroed at the first valid sample)
    recession = None
    mc = arrays["MODEL_CENTER"]
    valid = np.isfinite(mc)
    if valid.sum() >= 2:
        tv, cv = time[valid], mc[valid] - mc[valid][0]
        swell = int(np.argmin(cv))
        recession = {
            "zeroed": _clean(np.where(valid, mc - mc[valid][0], np.nan)),
            "swell_time": float(tv[swell]),
            "max_expansion": float(cv[swell]),
            "max_recession": float(cv.max()),
            "max_recession_time": float(tv[int(np.argmax(cv))]),
        }
        if len(tv) - swell - 1 >= 2:
            m, b = np.polyfit(tv[swell + 1:], cv[swell + 1:], 1)
            recession["rate"] = float(m)
            recession["intercept"] = float(b)

    # Pick up to ~10 representative profiles (+ first, last, swell)
    profiles = []
    if model_profiles:
        swell_idx = None
        vc = [(j, c) for j, c in centroids if c is not None and np.isfinite(c)]
        if vc:
            swell_idx = min(vc, key=lambda x: x[1])[0]
        stride = max(1, len(model_profiles) // 10)
        chosen = set(range(0, len(model_profiles), stride)) | {0, len(model_profiles) - 1}
        if swell_idx is not None:
            chosen.add(swell_idx)
        for j in sorted(chosen):
            loop_idx, contour = model_profiles[j]
            role = "mid"
            if j == 0:
                role = "first"
            elif j == len(model_profiles) - 1:
                role = "last"
            elif j == swell_idx:
                role = "swell"
            entry = {
                "time": float(time[loop_idx]),
                "index": int(index[loop_idx]),
                "role": role,
                "model": _contour_xy(contour, scale),
            }
            if loop_idx in shock_profiles:
                entry["shock"] = _contour_xy(shock_profiles[loop_idx], scale)
            profiles.append(entry)

    return {
        "n_raw": len(raw),
        "n": n,
        "fps": fps,
        "units": unit_label,
        "ppm": ppm,
        "mm_requested_but_missing": units == "mm" and not use_mm,
        "flow_direction": flow_direction,
        "index": [int(i) for i in index],
        "time": _clean(time),
        "outliers": int(bad.sum()),
        "series": [
            {"key": k, "label": label,
             "unit": unit_label if kind == "len" else "px^2",
             "values": _clean(arrays[k])}
            for k, label, kind in SERIES
        ],
        "recession": recession,
        "profiles": profiles,
    }


def linear_fits(result, t0, t1, keys=None):
    time = np.array([np.nan if v is None else v for v in result["time"]], dtype=float)
    sel = (time >= float(t0)) & (time <= float(t1))
    fits = []
    for s in result["series"]:
        if keys and s["key"] not in keys:
            continue
        y = np.array([np.nan if v is None else v for v in s["values"]], dtype=float)
        ok = sel & np.isfinite(y) & np.isfinite(time)
        entry = {"key": s["key"], "label": s["label"], "unit": s["unit"], "n": int(ok.sum())}
        if ok.sum() > 2:
            (m, b), cov = np.polyfit(time[ok], y[ok], 1, cov=True)
            err = np.sqrt(np.abs(np.diag(cov)))
            entry.update({
                "slope": float(m), "slope_err": float(err[0]),
                "intercept": float(b), "intercept_err": float(err[1]),
                "min": float(y[ok].min()), "max": float(y[ok].max()),
                "delta": float(y[ok].max() - y[ok].min()),
            })
        fits.append(entry)
    return fits


def to_csv(result):
    buf = io.StringIO()
    w = csv.writer(buf)
    header = ["INDEX", "TIME [s]"] + [f"{s['key']} [{s['unit']}]" for s in result["series"]]
    w.writerow(header)
    for i in range(result["n"]):
        row = [result["index"][i], result["time"][i]]
        row += ["" if s["values"][i] is None else s["values"][i] for s in result["series"]]
        w.writerow(row)
    return buf.getvalue()
