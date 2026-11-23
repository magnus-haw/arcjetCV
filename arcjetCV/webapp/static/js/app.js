/* arcjetCV Web front end (vanilla JS, no build step). */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const fmt = (v, d = 2) => (v === null || v === undefined || !isFinite(v) ? "-" : (+v).toFixed(d));
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const icon = (id) => `<svg class="icon"><use href="#i-${id}"/></svg>`;
  const basename = (p) => String(p).split(/[\\/]/).pop();
  const dirname = (p) => String(p).replace(/[\\/][^\\/]*$/, "");
  const human = (n) => { if (!isFinite(n)) return ""; const u = ["B", "KB", "MB", "GB"]; let i = 0; while (n >= 1024 && i < 3) { n /= 1024; i++; } return n.toFixed(i ? 1 : 0) + " " + u[i]; };
  const ago = (t) => { const s = Date.now() / 1000 - t; if (s < 60) return "just now"; if (s < 3600) return Math.floor(s / 60) + " min ago"; if (s < 86400) return Math.floor(s / 3600) + " h ago"; return new Date(t * 1000).toLocaleDateString(); };
  const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };

  // ------------------------------------------------------------------ Engine
  // "local": this page is served by the arcjetCV engine itself.
  // "hosted": this page lives on a website and talks to the engine running on
  // the user's computer at http://127.0.0.1:<port>, using an access token.
  const HOSTED = ($('meta[name="arcjetcv-mode"]') || {}).content === "hosted";
  const store = {
    get: (k) => { try { return localStorage.getItem(k) || ""; } catch (e) { return ""; } },
    set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} },
  };
  const ENG = { port: +store.get("acv-port") || 5050, token: store.get("acv-token") };
  function readConnectLink() { // Link opened by `arcjetcv-web --site URL`: #connect=<port>:<token>
    const m = location.hash.match(/^#connect=(\d+):([\w-]+)/);
    if (!m) return false;
    ENG.port = +m[1]; ENG.token = m[2];
    store.set("acv-port", ENG.port); store.set("acv-token", ENG.token);
    history.replaceState(null, "", location.pathname + location.search + "#home");
    return true;
  }
  readConnectLink();
  const engineBase = () => (HOSTED ? `http://127.0.0.1:${ENG.port}` : "");
  // URL for things the browser loads directly (images, links), which cannot send headers.
  function engineUrl(path) {
    if (!HOSTED) return path;
    return engineBase() + path + (ENG.token ? (path.includes("?") ? "&" : "?") + "token=" + encodeURIComponent(ENG.token) : "");
  }

  // ------------------------------------------------------------------ API
  async function api(url, body, opts = {}) {
    const init = body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
    Object.assign(init, opts);
    if (HOSTED) {
      init.targetAddressSpace = "loopback"; // Chrome local network access: the engine is on this computer
      if (ENG.token) init.headers = Object.assign({}, init.headers, { "X-ArcjetCV-Token": ENG.token });
    }
    let res;
    try { res = await fetch(engineBase() + url, init); }
    catch (e) {
      setServer(false);
      if (HOSTED) showConnect("offline");
      throw new Error(HOSTED ? "Cannot reach arcjetCV on this computer. Is arcjetcv-web running?" : "Cannot reach the arcjetCV server. Is the terminal still running?");
    }
    setServer(true);
    if (HOSTED && (res.status === 401 || res.status === 403) && url !== "/api/ping") showConnect(res.status === 401 ? "token" : "origin");
    const fail = (msg) => Object.assign(new Error(msg || res.statusText), { status: res.status });
    if (opts.raw) { if (!res.ok) throw fail((await res.json().catch(() => ({}))).error); return res; }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw fail(data.error);
    return data;
  }

  function pollJob(jid, onUpdate) {
    return new Promise((resolve, reject) => {
      const tick = async () => {
        try {
          const j = await api(`/api/jobs/${jid}`);
          onUpdate && onUpdate(j);
          if (j.status === "done") return resolve(j.result);
          if (j.status === "cancelled") return reject(Object.assign(new Error("Cancelled"), { cancelled: true }));
          if (j.status === "error") return reject(new Error(j.error));
          setTimeout(tick, 350);
        } catch (e) { reject(e); }
      };
      tick();
    });
  }

  function toast(title, msg = "", kind = "info", ms = 4500) {
    const t = document.createElement("div");
    t.className = "toast " + kind;
    const ic = { success: "check", error: "x", warn: "info", info: "info" }[kind];
    t.innerHTML = `${icon(ic)}<div><b>${esc(title)}</b>${msg ? `<div class="small muted">${msg}</div>` : ""}</div>`;
    $("#toasts").appendChild(t);
    setTimeout(() => t.remove(), ms);
    return t;
  }

  function setServer(ok) {
    const p = $("#server-status");
    p.classList.toggle("off", !ok);
    p.textContent = ok ? "Local server" : "Server offline";
  }

  // ------------------------------------------------------------------ Router
  const TITLES = { home: "Home", video: "Video Analysis", calibration: "Calibration", results: "Results & Plots", help: "Documentation" };
  function go(page) {
    if (!TITLES[page]) page = "home";
    $$(".page").forEach((p) => p.classList.toggle("active", p.id === "page-" + page));
    $$(".nav-link[data-go]").forEach((a) => a.classList.toggle("active", a.dataset.go === page));
    $("#topbar-title").textContent = TITLES[page];
    if (location.hash !== "#" + page) history.replaceState(null, "", "#" + page);
    document.body.classList.remove("sidebar-open");
    if (page === "home") refreshInfo();
  }
  window.addEventListener("hashchange", () => {
    if (readConnectLink()) { connect().then((ok) => ok && refreshInfo()).then(() => go("home")); return; }
    go(location.hash.slice(1));
  });
  document.addEventListener("click", (e) => {
    const g = e.target.closest("[data-go]");
    if (g) { e.preventDefault(); go(g.dataset.go); }
    const a = e.target.closest("[data-action]");
    if (a) {
      if (a.dataset.action === "open-video") pickVideo();
      if (a.dataset.action === "open-results") pickResults();
    }
  });
  $("#sidebar-toggle").onclick = () => {
    document.body.classList.toggle("sidebar-collapsed");
    try { localStorage.setItem("acv-collapsed", document.body.classList.contains("sidebar-collapsed") ? "1" : ""); } catch (e) {}
  };
  $("#menu-btn").onclick = () => document.body.classList.toggle("sidebar-open");
  try { if (localStorage.getItem("acv-collapsed")) document.body.classList.add("sidebar-collapsed"); } catch (e) {}

  $("#open-path-form").onsubmit = (e) => {
    e.preventDefault();
    const p = $("#open-path-input").value.trim().replace(/^["']|["']$/g, "");
    if (!p) return;
    if (/\.json$/i.test(p)) { setResultFiles([p]); go("results"); } else openVideo(p);
    $("#open-path-input").value = "";
  };

  // ------------------------------------------------------------------ Home
  let INFO = null;
  async function refreshInfo() {
    try {
      INFO = await api("/api/info");
      $("#stat-version").textContent = INFO.version;
      $("#brand-version").textContent = "v" + INFO.version;
      $("#footer-version").textContent = "v" + INFO.version;
      $("#stat-sessions").textContent = INFO.open_sessions;
      $("#stat-jobs").textContent = INFO.jobs_running;
      $("#stat-cnn").textContent = INFO.cnn_available ? "Ready" : "Off";
      renderRecent("#recent-videos", INFO.recent.videos || [], "film", (p) => openVideo(p), "No videos opened yet.");
      renderRecent("#recent-outputs", INFO.recent.outputs || [], "file", (p) => { setResultFiles([p]); go("results"); }, "No outputs analyzed yet.");
    } catch (e) { /* offline pill already shown */ }
  }
  function renderRecent(sel, paths, ic, onClick, emptyMsg) {
    const ul = $(sel);
    ul.innerHTML = paths.length ? "" : `<li class="empty-state">${emptyMsg}</li>`;
    paths.slice(0, 6).forEach((p) => {
      const li = document.createElement("li");
      li.className = "clickable";
      li.innerHTML = `<div class="li-icon">${icon(ic)}</div><div class="li-main"><div class="li-title">${esc(basename(p))}</div><div class="li-sub path"><span dir="ltr">${esc(dirname(p))}/</span></div></div>${icon("play")}`;
      li.onclick = () => onClick(p);
      ul.appendChild(li);
    });
  }

  // ------------------------------------------------------------------ File browser
  const B = { kind: "video", multi: false, sel: new Set(), path: null, resolve: null };
  function browse({ kind = "video", multi = false, title = "Open", start } = {}) {
    B.kind = kind; B.multi = multi; B.sel = new Set();
    $("#browser-title").textContent = title;
    $("#browser-modal").classList.add("open");
    $("#browser-open").disabled = true;
    $("#browser-sel").textContent = multi ? "Select one or more files (click to toggle)" : "Nothing selected";
    const recent = (INFO && INFO.recent && (kind === "json" ? INFO.recent.outputs : INFO.recent.videos)) || [];
    let first = start || localStorage.getItem("acv-dir-" + kind) || (recent[0] ? dirname(recent[0]) : null) || (INFO && INFO.cwd);
    const sc = $("#browser-shortcuts"); sc.innerHTML = "";
    const add = (label, p) => { if (!p) return; const b = document.createElement("button"); b.className = "btn btn-xs"; b.type = "button"; b.innerHTML = icon("folder") + esc(label); b.onclick = () => loadDir(p); sc.appendChild(b); };
    if (INFO) { add("Home", INFO.home); add("Launch folder", INFO.cwd); add("Workspace", INFO.workspace); }
    [...new Set(recent.map(dirname))].slice(0, 3).forEach((d) => add(basename(d), d));
    loadDir(first);
    return new Promise((res) => (B.resolve = res));
  }
  function closeBrowser(result) {
    $("#browser-modal").classList.remove("open");
    if (B.resolve) { B.resolve(result || null); B.resolve = null; }
  }
  async function loadDir(path) {
    const ul = $("#browser-list");
    try {
      const d = await api("/api/browse?kind=" + B.kind + "&path=" + encodeURIComponent(path || ""));
      B.path = d.path; B.parent = d.parent;
      $("#browser-path").value = d.path;
      try { localStorage.setItem("acv-dir-" + B.kind, d.path); } catch (e) {}
      ul.innerHTML = d.entries.length ? "" : `<li class="muted">No ${B.kind === "json" ? "output JSON" : "video or image"} files here.</li>`;
      d.entries.forEach((en) => {
        const li = document.createElement("li");
        li.className = en.type;
        if (B.sel.has(en.path)) li.classList.add("sel");
        li.innerHTML = en.type === "dir" ? `${icon("folder")}<span>${esc(en.name)}</span>` :
          `${icon(B.kind === "json" ? "file" : "film")}<span>${esc(en.name)}</span><span class="meta">${human(en.size)} &middot; ${ago(en.mtime)}</span>`;
        li.onclick = () => {
          if (en.type === "dir") return loadDir(en.path);
          if (B.multi) { B.sel.has(en.path) ? B.sel.delete(en.path) : B.sel.add(en.path); li.classList.toggle("sel"); }
          else { B.sel = new Set([en.path]); $$("#browser-list li").forEach((x) => x.classList.remove("sel")); li.classList.add("sel"); }
          $("#browser-open").disabled = B.sel.size === 0;
          $("#browser-sel").textContent = B.sel.size === 1 ? basename([...B.sel][0]) : B.sel.size + " files selected";
        };
        li.ondblclick = () => { if (en.type === "file") closeBrowser(B.multi ? [...new Set([...B.sel, en.path])] : en.path); };
        ul.appendChild(li);
      });
    } catch (e) { toast("Cannot open folder", esc(e.message), "error"); }
  }
  $("#browser-up").onclick = () => B.parent && loadDir(B.parent);
  $("#browser-path-form").onsubmit = (e) => { e.preventDefault(); loadDir($("#browser-path").value.trim()); };
  $("#browser-open").onclick = () => closeBrowser(B.multi ? [...B.sel] : [...B.sel][0]);
  $$("#browser-modal [data-close]").forEach((b) => (b.onclick = () => closeBrowser(null)));
  $("#browser-modal").addEventListener("mousedown", (e) => { if (e.target.id === "browser-modal") closeBrowser(null); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && $("#browser-modal").classList.contains("open")) closeBrowser(null); });
  const dz = $("#dropzone");
  ["dragenter", "dragover"].forEach((ev) => dz.addEventListener(ev, (e) => { e.preventDefault(); dz.classList.add("over"); }));
  ["dragleave", "drop"].forEach((ev) => dz.addEventListener(ev, (e) => { e.preventDefault(); dz.classList.remove("over"); }));
  dz.addEventListener("drop", async (e) => {
    const files = [...e.dataTransfer.files]; if (!files.length) return;
    const out = [];
    for (const f of files) {
      dz.innerHTML = `<span class="spinner dark"></span> Copying ${esc(f.name)} (${human(f.size)})...`;
      const fd = new FormData(); fd.append("file", f);
      try { const r = await api("/api/upload", undefined, { method: "POST", body: fd }); out.push(r.path); }
      catch (err) { toast("Upload failed", esc(err.message), "error"); }
    }
    dz.textContent = "Or drag a file here to copy it into your arcjetCV workspace";
    if (out.length) closeBrowser(B.multi ? out : out[0]);
  });

  // Use the computer's own Open/Save window (Finder, Explorer) through the local
  // engine; fall back to the in-page browser when that is not possible.
  let NATIVE = true;
  function lastDir(kind) {
    const recent = (INFO && INFO.recent && (kind === "json" ? INFO.recent.outputs : INFO.recent.videos)) || [];
    return store.get("acv-dir-" + kind) || (recent[0] ? dirname(recent[0]) : "") || (INFO ? INFO.cwd : "");
  }
  async function nativeDialog(req) {
    const note = toast("File window open", "Choose in the window that opened on your computer. It may be behind the browser.", "info", 4000);
    try {
      const r = await api("/api/dialog", req);
      if (r.paths && r.paths.length) store.set("acv-dir-" + (req.kind || "json"), dirname(r.paths[0]));
      return r;
    } finally { note && note.remove && note.remove(); }
  }
  async function pickFiles({ kind = "video", multi = false, title = "Open" } = {}) {
    if (NATIVE) {
      try {
        const r = await nativeDialog({ mode: "open", kind, multi, title, start: lastDir(kind) });
        if (r.cancelled) return null;
        return multi ? r.paths : r.paths[0];
      } catch (e) {
        if (e.status === 501) NATIVE = false;
        else if (e.status === 409) { toast("A file window is already open", "Finish or cancel it first.", "warn"); return null; }
        else { toast("File window failed", esc(e.message) + " Using the built-in browser instead.", "warn"); }
      }
    }
    return browse({ kind, multi, title });
  }
  async function pickSavePath({ kind = "json", title = "Save", name = "calibration.json", start = "" } = {}) {
    if (!NATIVE) return null;
    try {
      const r = await nativeDialog({ mode: "save", kind, title, name, start: start || lastDir(kind) });
      return r.cancelled ? "" : r.paths[0];
    } catch (e) { if (e.status === 501) NATIVE = false; else toast("File window failed", esc(e.message), "warn"); return null; }
  }

  async function pickVideo() { const p = await pickFiles({ kind: "video", title: "Open video or image" }); if (p) openVideo(p); }
  async function pickResults() { const p = await pickFiles({ kind: "json", multi: true, title: "Load output JSON files" }); if (p && p.length) { setResultFiles(p); go("results"); } }

  // ------------------------------------------------------------------ Video page
  const V = { sid: null, info: null, frame: 0, method: "AutoHSV", flow: "right", seq: 0, cropMode: false, lastElapsed: null, job: null };
  const DEFAULT_HSV = { model: [[0, 0, 150], [121, 125, 255]], shock: [[125, 40, 85], [170, 80, 230]] };
  const METHOD_HINT = {
    CNN: "U-Net neural network. Most robust, slower on CPU.",
    AutoHSV: "Automatic colour thresholds. No tuning required.",
    HSV: "Manual hue / saturation / intensity ranges for model and shock.",
    GRAY: "Grayscale threshold using the model minimum intensity.",
  };
  let brightChart = null;

  function videoControls(on) {
    $$("#page-video input, #page-video .seg button, #btn-crop-mode, #frame-prev, #frame-next, #btn-process, #btn-set-first, #btn-set-last, #btn-crop-reset, #btn-save-meta")
      .forEach((x) => (x.disabled = !on));
    if (on && V.method === "CNN" && INFO && !INFO.cnn_available) {}
  }

  async function openVideo(path) {
    go("video");
    if (V.job) { toast("Processing in progress", "Wait for the current job to finish or cancel it first.", "warn"); return; }
    const empty = $("#viewer-empty");
    $("#viewer-img").classList.add("hidden");
    $("#viewer-legend").classList.add("hidden");
    empty.classList.remove("hidden");
    empty.innerHTML = `<span class="spinner" style="width:2rem;height:2rem;border-width:3px"></span><div class="mt-1"><b>Opening ${esc(basename(path))}</b></div><div class="small" id="load-msg">Starting...</div><div class="progress mt-1" style="width:18rem;margin:0.6rem auto 0"><div id="load-bar"></div></div>`;
    $("#video-title").textContent = basename(path);
    $("#video-subtitle").textContent = "Loading video and computing metadata...";
    videoControls(false);
    try {
      if (V.sid) api(`/api/video/${V.sid}/close`, {}).catch(() => {});
      const { job } = await api("/api/video/open", { path });
      const info = await pollJob(job, (j) => { const m = $("#load-msg"); if (m) m.textContent = `${j.message} (${j.progress}%)`; const b = $("#load-bar"); if (b) b.style.width = j.progress + "%"; });
      V.sid = info.sid; V.info = info;
      applyVideoInfo(info);
      toast("Video loaded", `${esc(info.name)}: ${info.nframes} frames, ${info.width}x${info.height}`, "success");
    } catch (e) {
      empty.innerHTML = `${icon("x")}<div><b>Could not open video</b></div><div class="small">${esc(e.message)}</div>`;
      $("#video-subtitle").textContent = "Loading failed.";
      toast("Could not open video", esc(e.message), "error", 8000);
    }
  }

  function applyVideoInfo(info) {
    $("#viewer-empty").classList.add("hidden");
    $("#nav-video-dot").classList.remove("hidden");
    videoControls(true);
    $("#video-title").textContent = info.name;
    $("#video-subtitle").textContent = info.folder;
    $("#video-kv").innerHTML = [
      ["File", esc(basename(info.path))], ["Resolution", `${info.width} &times; ${info.height}`], ["Frames", info.nframes],
      ["Frame rate", info.fps ? fmt(info.fps, 2) + " fps" : "-"], ["Duration", info.fps ? fmt(info.nframes / info.fps, 1) + " s" : "-"],
      ["Good frames", `${info.first_good} &ndash; ${info.last_good}`],
    ].map(([k, v]) => `<dt>${k}</dt><dd title="${typeof v === "string" ? v.replace(/<[^>]+>/g, "") : v}">${v}</dd>`).join("");
    const max = Math.max(0, info.nframes - 1);
    const sl = $("#frame-slider"); sl.max = max;
    $("#frame-index").max = max;
    ["#proc-first", "#proc-last"].forEach((s) => ($(s).max = max));
    $("#proc-first").value = info.first_good;
    $("#proc-last").value = Math.min(max, info.last_good);
    $("#proc-prefix").value = info.name;
    V.flow = info.flow_direction || "right";
    setSeg("#flow-seg", V.flow);
    setCropInputs(info.crop);
    $("#ppm").value = info.pixels_per_mm || "";
    $("#res-fps").value = info.fps ? +info.fps.toFixed(3) : 30;
    renderVideoOutputs(info.outputs);
    drawBrightness();
    setFrame(Math.min(max, info.first_good || 0));
    updateEstimate();
  }

  function setSeg(sel, v) { $$(sel + " button").forEach((b) => b.classList.toggle("on", b.dataset.v === v)); }
  function setCropInputs(c) { $("#crop-xmin").value = c.xmin; $("#crop-xmax").value = c.xmax; $("#crop-ymin").value = c.ymin; $("#crop-ymax").value = c.ymax; }
  function getCrop() { return { xmin: +$("#crop-xmin").value, xmax: +$("#crop-xmax").value, ymin: +$("#crop-ymin").value, ymax: +$("#crop-ymax").value }; }
  function getHSV() {
    const out = { model: [[0, 0, 0], [0, 0, 0]], shock: [[0, 0, 0], [0, 0, 0]] };
    $$(".hsv").forEach((i) => (out[i.dataset.r][+i.dataset.b][+i.dataset.i] = +i.value));
    return out;
  }
  function params() {
    const hsv = getHSV();
    return {
      index: V.frame, method: V.method, flow_direction: V.flow, crop: getCrop(),
      hsv_model: hsv.model, hsv_shock: hsv.shock, threshold: hsv.model[0][2],
      show_shock: $("#opt-shock").checked, show_crop: $("#opt-crop").checked, annotate: $("#opt-annotate").checked,
      pixels_per_mm: $("#ppm").value || null,
    };
  }

  function setFrame(i) {
    if (!V.info) return;
    i = Math.max(0, Math.min(V.info.nframes - 1, Math.round(+i || 0)));
    V.frame = i;
    $("#frame-slider").value = i;
    $("#frame-index").value = i;
    drawBrightness();
    preview();
  }

  const preview = debounce(async () => {
    if (!V.sid) return;
    const seq = ++V.seq;
    $("#viewer").classList.add("loading");
    try {
      const r = await api(`/api/video/${V.sid}/preview`, params());
      if (seq !== V.seq) return;
      const img = $("#viewer-img");
      img.src = r.image; img.classList.remove("hidden");
      $("#viewer-legend").classList.remove("hidden");
      renderFlags(r.metrics);
      V.lastElapsed = r.metrics.ELAPSED_S;
      $("#preview-time").textContent = `Frame ${V.frame}` + (V.info.fps ? ` · ${fmt(V.frame / V.info.fps, 2)} s` : "") + ` · ${Math.round(r.metrics.ELAPSED_S * 1000)} ms`;
      updateEstimate();
    } catch (e) {
      if (seq !== V.seq) return;
      $("#preview-flags").innerHTML = `<span class="badge red">${esc(e.message)}</span>`;
    } finally { if (seq === V.seq) $("#viewer").classList.remove("loading"); }
  }, 90);

  function renderFlags(m) {
    const b = (cls, txt) => `<span class="badge ${cls}">${txt}</span>`;
    const out = [];
    out.push(m.MODEL_FOUND ? b("green", icon("check") + "Model found") : b("red", icon("x") + "No model"));
    out.push(m.SHOCK_FOUND ? b("green", icon("check") + "Shock found") : b("gray", "No shock"));
    if (m.OVEREXPOSED) out.push(b("amber", "Overexposed"));
    if (m.UNDEREXPOSED) out.push(b("amber", "Underexposed"));
    if (m.MODEL_RADIUS) out.push(b("", "Radius " + fmt(m.MODEL_RADIUS, 1) + " px"));
    if (m.MODEL_INTERP_XPOS) out.push(b("", "Center x " + fmt(m.MODEL_INTERP_XPOS[2], 1) + " px"));
    if (m.SHOCK_INTERP_XPOS && m.MODEL_INTERP_XPOS) out.push(b("", "Standoff " + fmt(Math.abs(m.SHOCK_INTERP_XPOS[0] - m.MODEL_INTERP_XPOS[2]), 1) + " px"));
    $("#preview-flags").innerHTML = out.join("");
  }

  function drawBrightness() {
    if (!V.info) return;
    const y = V.info.brightness || [];
    const x = y.map((_, i) => i);
    const first = +$("#proc-first").value, last = +$("#proc-last").value;
    const opts = {
      series: [{ name: "Mean brightness", color: "#4e73df", x, y, width: 1.6 }],
      bands: [{ x0: first, x1: last, color: "rgba(28,200,138,0.12)" }],
      vlines: [{ x: V.frame, color: "#e74a3b", dash: "0", width: 1.5 }],
      xRange: [0, Math.max(1, V.info.nframes - 1)], legend: false, compact: true,
      xName: "Frame", yName: "Brightness", onClick: (f) => setFrame(f),
    };
    if (!brightChart) brightChart = new MiniChart($("#chart-brightness"), opts); else brightChart.update(opts);
  }

  function updateEstimate() {
    if (!V.info) return;
    const f = +$("#proc-first").value, l = +$("#proc-last").value, s = Math.max(1, +$("#proc-stride").value);
    const n = l >= f ? Math.floor((l - f) / s) + 1 : 0;
    let t = `${n} frames to process`;
    if (V.lastElapsed) { const sec = n * V.lastElapsed * 1.15; t += ` · about ${sec < 90 ? Math.ceil(sec) + " s" : Math.ceil(sec / 60) + " min"}`; }
    $("#proc-estimate").textContent = t;
    drawBrightness();
  }

  function renderVideoOutputs(outs) {
    const ul = $("#video-outputs");
    ul.innerHTML = outs && outs.length ? "" : `<li class="empty-state">No outputs yet. Process the video to create one.</li>`;
    (outs || []).slice().reverse().forEach((o) => {
      const li = document.createElement("li");
      li.className = "clickable";
      li.innerHTML = `<div class="li-icon">${icon("file")}</div><div class="li-main"><div class="li-title">${esc(o.name)}</div><div class="li-sub">${human(o.size)} · ${ago(o.mtime)}</div></div><button class="btn btn-xs">${icon("chart")}Plot</button>`;
      li.onclick = () => { setResultFiles([o.path]); go("results"); };
      ul.appendChild(li);
    });
  }

  async function refreshVideoInfo() {
    if (!V.sid) return;
    try { const info = await api(`/api/video/${V.sid}`); V.info = info; renderVideoOutputs(info.outputs); } catch (e) {}
  }

  // events
  $("#frame-slider").oninput = (e) => setFrame(e.target.value);
  $("#frame-index").onchange = (e) => setFrame(e.target.value);
  $("#frame-prev").onclick = () => setFrame(V.frame - 1);
  $("#frame-next").onclick = () => setFrame(V.frame + 1);
  document.addEventListener("keydown", (e) => {
    if (!$("#page-video").classList.contains("active") || !V.sid) return;
    if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName) && document.activeElement.type !== "range") return;
    const step = e.shiftKey ? 10 : 1;
    if (e.key === "ArrowLeft") { e.preventDefault(); setFrame(V.frame - step); }
    if (e.key === "ArrowRight") { e.preventDefault(); setFrame(V.frame + step); }
  });
  $$("#flow-seg button").forEach((b) => (b.onclick = () => { V.flow = b.dataset.v; setSeg("#flow-seg", V.flow); preview(); }));
  $$("#method-seg button").forEach((b) => (b.onclick = () => setMethod(b.dataset.v)));
  function setMethod(m) {
    V.method = m; setSeg("#method-seg", m);
    $("#hsv-panel").classList.toggle("hidden", !(m === "HSV" || m === "GRAY"));
    $$("#hsv-panel .range-row[data-ch='h'], #hsv-panel .range-row[data-ch='s']").forEach((r) => r.classList.toggle("hidden", m === "GRAY"));
    let hint = METHOD_HINT[m];
    if (m === "CNN" && INFO && !INFO.cnn_available) hint += " PyTorch was not found, so CNN will fail.";
    if (m === "GRAY") hint += " Only the intensity minimum is used.";
    $("#method-hint").textContent = hint;
    preview();
  }
  $$(".tabs button").forEach((b) => (b.onclick = () => {
    $$(".tabs button").forEach((x) => x.classList.toggle("on", x === b));
    $$(".tab-panel").forEach((p) => p.classList.toggle("on", p.id === b.dataset.tab));
  }));
  $$(".hsv").forEach((i) => (i.oninput = debounce(preview, 200)));
  $("#btn-hsv-reset").onclick = () => { $$(".hsv").forEach((i) => (i.value = DEFAULT_HSV[i.dataset.r][+i.dataset.b][+i.dataset.i])); preview(); };
  $$(".geo").forEach((i) => (i.onchange = preview));
  ["#opt-shock", "#opt-crop", "#opt-annotate"].forEach((s) => ($(s).onchange = preview));
  $("#ppm").onchange = preview;
  $("#btn-crop-reset").onclick = () => {
    const w = V.info.width, h = V.info.height;
    setCropInputs({ xmin: Math.round(w * 0.1), xmax: Math.round(w * 0.9), ymin: Math.round(h * 0.1), ymax: Math.round(h * 0.9) });
    preview();
  };
  $("#btn-save-meta").onclick = async () => {
    try {
      const p = params(); p.first_good = +$("#proc-first").value; p.last_good = +$("#proc-last").value;
      V.info = await api(`/api/video/${V.sid}/meta`, p);
      toast("Saved", "Crop, flow direction and frame range written to the .meta file.", "success");
    } catch (e) { toast("Save failed", esc(e.message), "error"); }
  };
  ["#proc-first", "#proc-last", "#proc-stride"].forEach((s) => ($(s).oninput = updateEstimate));
  $("#btn-set-first").onclick = () => { $("#proc-first").value = V.frame; updateEstimate(); };
  $("#btn-set-last").onclick = () => { $("#proc-last").value = V.frame; updateEstimate(); };

  // crop drawing
  $("#btn-crop-mode").onclick = () => {
    V.cropMode = !V.cropMode;
    $("#btn-crop-mode").classList.toggle("btn-primary", V.cropMode);
    if (V.cropMode) toast("Draw crop", "Drag a rectangle on the frame to set the region of interest.");
  };
  (() => {
    const img = $("#viewer-img"), box = $("#crop-box"), viewer = $("#viewer");
    let start = null;
    const toImg = (e) => {
      const r = img.getBoundingClientRect();
      const x = Math.max(0, Math.min(r.width, e.clientX - r.left)), y = Math.max(0, Math.min(r.height, e.clientY - r.top));
      return { x, y, ix: Math.round((x / r.width) * V.info.width), iy: Math.round((y / r.height) * V.info.height) };
    };
    img.addEventListener("mousedown", (e) => { if (!V.cropMode || !V.info) return; e.preventDefault(); start = toImg(e); });
    window.addEventListener("mousemove", (e) => {
      if (!start) return;
      const p = toImg(e), r = img.getBoundingClientRect(), vr = viewer.getBoundingClientRect();
      Object.assign(box.style, { display: "block", left: r.left - vr.left + Math.min(start.x, p.x) + "px", top: r.top - vr.top + Math.min(start.y, p.y) + "px", width: Math.abs(p.x - start.x) + "px", height: Math.abs(p.y - start.y) + "px" });
    });
    window.addEventListener("mouseup", (e) => {
      if (!start) return;
      const p = toImg(e);
      box.style.display = "none";
      if (Math.abs(p.ix - start.ix) > 8 && Math.abs(p.iy - start.iy) > 8) {
        setCropInputs({ xmin: Math.min(start.ix, p.ix), xmax: Math.max(start.ix, p.ix), ymin: Math.min(start.iy, p.iy), ymax: Math.max(start.iy, p.iy) });
        V.cropMode = false; $("#btn-crop-mode").classList.remove("btn-primary");
        preview();
      }
      start = null;
    });
  })();

  // processing
  $("#btn-process").onclick = async () => {
    if (!V.sid) return;
    const p = params();
    Object.assign(p, { first: +$("#proc-first").value, last: +$("#proc-last").value, stride: +$("#proc-stride").value || 1,
      output_prefix: $("#proc-prefix").value, write_video: $("#proc-write-video").checked });
    $("#btn-process").disabled = true;
    $("#proc-progress").classList.remove("hidden");
    $("#proc-bar").style.width = "0%"; $("#proc-pct").textContent = "0%"; $("#proc-msg").textContent = "Starting...";
    try {
      const { job } = await api(`/api/video/${V.sid}/process`, p);
      V.job = job;
      const t0 = Date.now();
      const res = await pollJob(job, (j) => {
        $("#proc-bar").style.width = j.progress + "%";
        $("#proc-pct").textContent = j.progress + "%";
        let eta = "";
        if (j.progress > 2) { const s = ((Date.now() - t0) / 1000) * (100 - j.progress) / j.progress; eta = ` · ${s < 90 ? Math.ceil(s) + " s" : Math.ceil(s / 60) + " min"} left`; }
        $("#proc-msg").textContent = j.message + eta;
      });
      toast("Processing complete", `Output written to <span class="mono">${esc(basename(res.output))}</span>. <a href="#results" data-plot="${esc(res.output)}">Plot results</a>`, "success", 9000);
      $("#proc-msg").innerHTML = `Done. <a href="#results" data-plot="${esc(res.output)}">Open ${esc(basename(res.output))} in Results</a>`;
      refreshVideoInfo();
    } catch (e) {
      if (e.cancelled) { toast("Processing cancelled", "", "warn"); $("#proc-msg").textContent = "Cancelled."; }
      else { toast("Processing failed", esc(e.message), "error", 9000); $("#proc-msg").textContent = "Failed: " + e.message; }
    } finally {
      V.job = null;
      $("#btn-process").disabled = false;
      $("#proc-progress .progress").classList.remove("striped");
      setTimeout(() => $("#proc-progress .progress").classList.add("striped"), 50);
    }
  };
  $("#btn-cancel").onclick = () => V.job && api(`/api/jobs/${V.job}/cancel`, {}).catch(() => {});
  $("#btn-refresh-outputs").onclick = refreshVideoInfo;
  document.addEventListener("click", (e) => {
    const a = e.target.closest("[data-plot]");
    if (a) { e.preventDefault(); setResultFiles([a.dataset.plot]); go("results"); }
  });

  // ------------------------------------------------------------------ Results page
  const R = { paths: [], data: null, units: "px", flow: "auto", visible: new Set(["MODEL_CENTER", "SHOCK_CENTER", "MODEL_-0.50R", "MODEL_0.50R"]) };
  const COLORS = {
    "MODEL_-0.95R": "#d946ef", "MODEL_-0.50R": "#4e73df", "MODEL_CENTER": "#111827", "MODEL_0.50R": "#36b9cc", "MODEL_0.95R": "#1cc88a",
    "SHOCK_CENTER": "#7e63bf", "SHOCK_TO_MODEL": "#f6a623", "MODEL_RADIUS": "#e74a3b", "MODEL_YPOS": "#8b5cf6", "MODEL_AREA": "#0ea5e9", "SHOCK_AREA": "#f97316",
  };
  let recChart = null, serChart = null, profChart = null;

  function setResultFiles(paths) {
    R.paths = paths;
    const ul = $("#res-files");
    ul.innerHTML = "";
    paths.forEach((p) => {
      const li = document.createElement("li");
      li.innerHTML = `<div class="li-icon">${icon("file")}</div><div class="li-main"><div class="li-title">${esc(basename(p))}</div><div class="li-sub path"><span dir="ltr">${esc(dirname(p))}/</span></div></div><button class="btn btn-xs btn-ghost" title="Remove">${icon("x")}</button>`;
      li.querySelector("button").onclick = () => setResultFiles(R.paths.filter((x) => x !== p));
      ul.appendChild(li);
    });
    if (!paths.length) { ul.innerHTML = `<li class="empty-state">No files selected.</li>`; }
    const add = document.createElement("li");
    add.innerHTML = `<button class="btn btn-sm btn-block" data-action="open-results">${icon("folder")}Add or replace files</button>`;
    ul.appendChild(add);
    analyze();
  }

  function resultArgs() {
    return {
      paths: R.paths, fps: +$("#res-fps").value || 30, mask_n: +$("#res-mask").value || 1, units: R.units,
      pixels_per_mm: $("#res-ppm").value || null, flow_direction: R.flow === "auto" ? null : R.flow,
      kalman: $("#res-kalman").checked, outlier_mask: $("#res-outliers").checked,
    };
  }

  async function analyze() {
    if (!R.paths.length) { R.data = null; renderResults(); return; }
    $("#results-subtitle").innerHTML = `<span class="spinner"></span> Analyzing ${R.paths.length} file(s)...`;
    try {
      R.data = await api("/api/results/analyze", resultArgs());
      if (R.data.mm_requested_but_missing) toast("No calibration", "Pixels per mm is not in the output. Showing pixels; enter a value to convert.", "warn");
      const t = R.data.time.filter((v) => v !== null);
      if (t.length) { $("#fit-t0").value = (R.data.recession ? R.data.recession.swell_time : t[0]).toFixed(3); $("#fit-t1").value = t[t.length - 1].toFixed(3); }
      renderResults();
    } catch (e) {
      R.data = null; renderResults();
      $("#results-subtitle").textContent = "Analysis failed.";
      toast("Analysis failed", esc(e.message), "error", 8000);
    }
  }

  function renderResults() {
    const d = R.data;
    $("#btn-csv").disabled = $("#btn-fit").disabled = !d;
    if (!d) {
      $("#results-title").textContent = "No outputs loaded";
      $("#results-subtitle").textContent = "Load one or more arcjetCV output JSON files to plot recession and shock data.";
      ["#m-frames", "#m-swell", "#m-maxrec", "#m-rate"].forEach((s) => ($(s).textContent = "-"));
      return;
    }
    const u = d.units;
    $("#results-title").textContent = R.paths.length === 1 ? basename(R.paths[0]) : `${R.paths.length} output files`;
    $("#results-subtitle").textContent = `${d.n_raw} frames · ${d.fps} fps · flow ${d.flow_direction} · ${d.outliers} outliers masked` + (d.ppm ? ` · ${fmt(d.ppm, 3)} px/mm` : "");
    $("#m-frames").innerHTML = `${d.n} <small>of ${d.n_raw}</small>`;
    const rc = d.recession;
    $("#m-swell").innerHTML = rc ? `${fmt(rc.swell_time, 2)} <small>s</small>` : "-";
    $("#m-maxrec").innerHTML = rc ? `${fmt(rc.max_recession, 2)} <small>${u}</small>` : "-";
    $("#m-rate").innerHTML = rc && rc.rate !== undefined ? `${fmt(rc.rate, 3)} <small>${u}/s</small>` : "-";

    // Recession chart
    const recSeries = [];
    const vlines = [];
    if (rc) {
      const T = d.time, Z = rc.zeroed;
      const gx = [], gy = [], rx = [], ry = [];
      T.forEach((t, i) => { if (Z[i] === null || t === null) return; (t <= rc.swell_time ? (gx.push(t), gy) : (rx.push(t), ry)).push(Z[i]); });
      recSeries.push({ name: "Growth", color: "#2e8b57", x: gx, y: gy, mode: "markers", size: 3.2 });
      recSeries.push({ name: "Recession", color: "#4e73df", x: rx, y: ry, mode: "markers", size: 3.2 });
      if (rc.rate !== undefined && rx.length) {
        const a = rx[0], b = rx[rx.length - 1];
        recSeries.push({ name: `Fit: ${fmt(rc.rate, 3)} ${u}/s`, color: "#e74a3b", x: [a, b], y: [rc.rate * a + rc.intercept, rc.rate * b + rc.intercept], width: 2, tooltip: false });
      }
      vlines.push({ x: rc.swell_time, label: `Recess start ${fmt(rc.swell_time, 2)} s`, color: "#111827" });
      $("#rec-sub").textContent = `Max expansion ${fmt(rc.max_expansion, 2)} ${u} · max recession ${fmt(rc.max_recession, 2)} ${u} at ${fmt(rc.max_recession_time, 2)} s`;
    } else $("#rec-sub").textContent = "Not enough model detections.";
    const recOpts = { series: recSeries, vlines, xLabel: "Time (s)", yLabel: `Model center displacement (${u})`, xName: "t (s)", yName: u, padX: true };
    if (!recChart) recChart = new MiniChart($("#chart-recession"), recOpts); else recChart.update(recOpts);

    renderSeriesChips(); renderSeries();

    // Profiles chart
    const prof = [];
    const colorFor = (r, k, n) => r === "first" ? "#e74a3b" : r === "swell" ? "#2e8b57" : r === "last" ? "#1f77b4" : `hsla(220, 10%, ${55 + (k / Math.max(1, n)) * 20}%, 0.7)`;
    d.profiles.forEach((p, k) => {
      const c = colorFor(p.role, k, d.profiles.length);
      const named = p.role !== "mid";
      prof.push({ name: named ? `${p.role === "swell" ? "Recess start" : p.role[0].toUpperCase() + p.role.slice(1)} (${fmt(p.time, 2)} s)` : `t = ${fmt(p.time, 2)} s`, legend: named, color: c, x: p.model.map((q) => q[0]), y: p.model.map((q) => q[1]), width: named ? 2.2 : 1.2 });
      if (p.shock) prof.push({ name: `Shock ${fmt(p.time, 2)} s`, legend: false, color: c, dash: "5 4", x: p.shock.map((q) => q[0]), y: p.shock.map((q) => q[1]), width: named ? 1.6 : 1, opacity: 0.8 });
    });
    const profOpts = { series: prof, invertY: true, equal: true, xLabel: `X (${u})`, yLabel: `Y (${u})`, xName: "x", yName: "y", padX: true };
    if (!profChart) profChart = new MiniChart($("#chart-profiles"), profOpts); else profChart.update(profOpts);
  }

  function renderSeriesChips() {
    const row = $("#series-chips");
    row.innerHTML = "";
    R.data.series.forEach((s) => {
      const has = s.values.some((v) => v !== null);
      const c = document.createElement("button");
      c.className = "chip" + (R.visible.has(s.key) ? " on" : "");
      c.disabled = !has;
      if (!has) c.style.opacity = 0.45;
      c.innerHTML = `<i style="background:${COLORS[s.key]}"></i>${esc(s.label)} <span class="muted">(${esc(s.unit)})</span>`;
      c.onclick = () => { R.visible.has(s.key) ? R.visible.delete(s.key) : R.visible.add(s.key); c.classList.toggle("on"); renderSeries(); };
      row.appendChild(c);
    });
  }

  function renderSeries() {
    const d = R.data; if (!d) return;
    const vis = d.series.filter((s) => R.visible.has(s.key));
    const units = [...new Set(vis.map((s) => s.unit))];
    const series = vis.map((s) => ({ name: s.label, color: COLORS[s.key], x: d.time, y: s.values, mode: "markers", size: 2.6 }));
    const opts = { series, xLabel: "Time (s)", yLabel: units.join(" / ") || "", xName: "t (s)", yName: units.join("/"), legend: false, padX: true };
    if (!serChart) serChart = new MiniChart($("#chart-series"), opts); else serChart.update(opts);
  }

  $$("#units-seg button").forEach((b) => (b.onclick = () => { R.units = b.dataset.v; setSeg("#units-seg", R.units); analyze(); }));
  $$("#res-flow-seg button").forEach((b) => (b.onclick = () => { R.flow = b.dataset.v; setSeg("#res-flow-seg", R.flow); analyze(); }));
  $$(".res-opt").forEach((i) => (i.onchange = analyze));

  $("#btn-fit").onclick = async () => {
    try {
      const args = Object.assign(resultArgs(), { t0: +$("#fit-t0").value, t1: +$("#fit-t1").value, keys: [...R.visible] });
      const r = await api("/api/results/fit", args);
      const rows = r.fits.map((f) => f.slope === undefined
        ? `<tr><td><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${COLORS[f.key]};margin-right:6px"></i>${esc(f.label)}</td><td colspan="5" class="muted">Not enough points (${f.n})</td></tr>`
        : `<tr><td><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${COLORS[f.key]};margin-right:6px"></i>${esc(f.label)}</td><td><b>${fmt(f.slope, 4)}</b> &plusmn; ${fmt(f.slope_err, 4)} <span class="muted">${esc(f.unit)}/s</span></td><td>${fmt(f.intercept, 3)} &plusmn; ${fmt(f.intercept_err, 3)}</td><td>${fmt(f.min, 3)}</td><td>${fmt(f.max, 3)}</td><td>${fmt(f.delta, 3)}</td><td>${f.n}</td></tr>`).join("");
      $("#fit-table").innerHTML = `<thead><tr><th>Series</th><th>Slope m</th><th>Intercept b</th><th>Min</th><th>Max</th><th>Delta</th><th>N</th></tr></thead><tbody>${rows}</tbody>`;
      $("#fit-sub").textContent = `${fmt(args.t0, 2)} s to ${fmt(args.t1, 2)} s`;
      $("#fit-card").classList.remove("hidden");
      $("#fit-card").scrollIntoView({ behavior: "smooth", block: "nearest" });
    } catch (e) { toast("Fit failed", esc(e.message), "error"); }
  };

  $("#btn-csv").onclick = async () => {
    try {
      const res = await api("/api/results/csv", resultArgs(), { raw: true });
      const blob = await res.blob();
      const name = (res.headers.get("Content-Disposition") || "").match(/filename="([^"]+)"/);
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob); a.download = name ? name[1] : "arcjetcv_timeseries.csv";
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 2000);
    } catch (e) { toast("Export failed", esc(e.message), "error"); }
  };

  // ------------------------------------------------------------------ Calibration
  // Mirrors the desktop Calibration tab: load a calibration JSON, measure
  // pixels per mm from a pattern (diagonal) or a ruler line, then apply or save.
  const C = { mode: "pattern", img: null, pts: [], data: null, source: null, measuredPx: null };

  function calPpm() { const v = parseFloat($("#cal-ppm").value); return isFinite(v) && v > 0 ? v : null; }

  function renderCalibration() {
    const ppm = calPpm();
    const d = C.data || {};
    const camera = !!(d.camera_matrix && d.dist_coeffs);
    $("#cal-kv").innerHTML = [
      ["Source", C.source ? esc(C.source) : "-"],
      ["Pixels per mm", ppm ? fmt(ppm, 4) + " px/mm" : "-"],
      ["mm per pixel", ppm ? fmt(1 / ppm, 6) + " mm/px" : "-"],
      ["Camera model", camera ? "Yes" + (d.pattern_size ? ` (${d.pattern_size.join(" x ")} pattern)` : "") : "No"],
    ].map(([k, v]) => `<dt>${k}</dt><dd title="${String(v).replace(/<[^>]+>/g, "")}">${v}</dd>`).join("");
    $("#cal-title").textContent = ppm ? `${fmt(ppm, 3)} px/mm` : "No calibration";
    $("#cal-subtitle").textContent = ppm ? `${fmt(1 / ppm, 5)} mm per pixel` + (C.source ? ` · ${C.source}` : "")
      : "Load a calibration file, or measure pixels per mm from a calibration pattern or a known length.";
    $("#cal-apply").disabled = !ppm;
    $("#cal-save").disabled = !ppm && !camera;
    $("#nav-calib-dot").classList.toggle("hidden", !ppm);
    const len = C.measuredPx;
    $("#cal-measure-kv").innerHTML = `<dt>Measured length</dt><dd>${len ? fmt(len, 2) + " px" : "-"}</dd><dt>Pixels per mm</dt><dd>${ppm ? fmt(ppm, 4) : "-"}</dd>`;
    $("#cal-detect").disabled = !(C.img && C.img.path);
  }

  function setCalImage(img) {
    // img: { src, width, height, path?, label }
    C.img = img; C.pts = []; C.measuredPx = null;
    $("#cal-empty").classList.add("hidden");
    $("#cal-stage").classList.remove("hidden");
    $("#cal-img").src = img.src;
    $("#cal-img-sub").textContent = `${img.label} · ${img.width} x ${img.height}`;
    $("#cal-overlay").setAttribute("viewBox", `0 0 ${img.width} ${img.height}`);
    drawRuler();
    if (img.path && !$("#cal-save-path").value) $("#cal-save-path").value = dirname(img.path) + "/calibration.json";
    renderCalibration();
  }

  function setCalMode(m) {
    C.mode = m; setSeg("#cal-mode-seg", m);
    $("#cal-pattern-panel").classList.toggle("hidden", m !== "pattern");
    $("#cal-ruler-panel").classList.toggle("hidden", m !== "ruler");
    $("#cal-img-hint").textContent = m === "ruler"
      ? "Click two points on the image to draw the reference line. Click again to start a new line."
      : "Open a photo of the calibration pattern, then press Detect pattern.";
    drawRuler();
  }
  $$("#cal-mode-seg button").forEach((b) => (b.onclick = () => setCalMode(b.dataset.v)));

  function drawRuler() {
    const svg = $("#cal-overlay");
    if (C.mode !== "ruler" || !C.img) { svg.innerHTML = ""; return; }
    const r = Math.max(4, C.img.width / 160);
    let h = "";
    if (C.pts.length === 2) {
      const [a, b] = C.pts;
      h += `<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" style="stroke-width:${r / 2}"/>`;
    }
    C.pts.forEach((p) => (h += `<circle cx="${p.x}" cy="${p.y}" r="${r}"/>`));
    svg.innerHTML = h;
  }

  function updateRulerPpm() {
    if (C.mode !== "ruler" || C.pts.length !== 2) return;
    const [a, b] = C.pts;
    C.measuredPx = Math.hypot(b.x - a.x, b.y - a.y);
    const mm = parseFloat($("#cal-ruler-mm").value);
    if (isFinite(mm) && mm > 0) { $("#cal-ppm").value = +(C.measuredPx / mm).toFixed(6); C.source = "Ruler measurement"; }
    renderCalibration();
  }

  $("#cal-img").addEventListener("click", (e) => {
    if (C.mode !== "ruler" || !C.img) return;
    const r = e.target.getBoundingClientRect();
    const p = { x: ((e.clientX - r.left) / r.width) * C.img.width, y: ((e.clientY - r.top) / r.height) * C.img.height };
    C.pts = C.pts.length >= 2 ? [p] : [...C.pts, p];
    if (C.pts.length < 2) C.measuredPx = null;
    drawRuler(); updateRulerPpm(); renderCalibration();
  });
  $("#cal-ruler-mm").oninput = updateRulerPpm;
  $("#cal-ruler-clear").onclick = () => { C.pts = []; C.measuredPx = null; drawRuler(); renderCalibration(); };
  $("#cal-ppm").oninput = () => { C.source = C.source || "Typed value"; renderCalibration(); };

  $("#cal-open-image").onclick = async () => {
    const p = await pickFiles({ kind: "image", title: "Open calibration image" });
    if (!p) return;
    try {
      const r = await api("/api/calibration/image", { path: p });
      setCalImage({ src: r.image, width: r.width, height: r.height, path: p, label: basename(p) });
    } catch (e) { toast("Could not open image", esc(e.message), "error"); }
  };

  $("#cal-use-frame").onclick = () => {
    if (!V.sid || !V.info) { toast("No video loaded", "Open a video in Video Analysis first.", "warn"); return; }
    setCalImage({ src: engineUrl(`/api/video/${V.sid}/frame/${V.frame}?t=${Date.now()}`), width: V.info.width, height: V.info.height,
      path: null, label: `${V.info.name} frame ${V.frame}` });
    if (!$("#cal-save-path").value) $("#cal-save-path").value = V.info.folder + "/calibration.json";
    setCalMode("ruler");
    toast("Ruler mode", "Click two points of known distance on the frame.");
  };

  $("#cal-detect").onclick = async () => {
    if (!C.img || !C.img.path) return;
    const viewer = $("#cal-viewer");
    viewer.classList.add("loading");
    $("#cal-detect").disabled = true;
    try {
      const r = await api("/api/calibration/pattern", {
        path: C.img.path, cols: +$("#cal-cols").value, rows: +$("#cal-rows").value, diagonal_mm: $("#cal-diag-mm").value || null,
      });
      const path = C.img.path;
      setCalImage({ src: r.image, width: r.width, height: r.height, path, label: `${basename(path)} (rectified)` });
      C.data = r.calibration; C.measuredPx = r.diagonal_px; C.source = basename(path);
      if (r.pixels_per_mm) $("#cal-ppm").value = +r.pixels_per_mm.toFixed(6);
      renderCalibration();
      toast("Pattern detected", `${esc(r.pattern_type.replace(/_/g, " "))}, diagonal ${fmt(r.diagonal_px, 2)} px` +
        (r.pixels_per_mm ? `, ${fmt(r.pixels_per_mm, 3)} px/mm` : ". Enter the real diagonal length to get pixels per mm."), r.pixels_per_mm ? "success" : "warn", 7000);
    } catch (e) { toast("Pattern detection failed", esc(e.message), "error", 8000); }
    finally { viewer.classList.remove("loading"); renderCalibration(); }
  };
  $("#cal-diag-mm").oninput = () => {
    const mm = parseFloat($("#cal-diag-mm").value);
    if (C.mode === "pattern" && C.measuredPx && isFinite(mm) && mm > 0) {
      $("#cal-ppm").value = +(C.measuredPx / mm).toFixed(6);
      renderCalibration();
    }
  };

  $("#cal-load").onclick = async () => {
    const p = await pickFiles({ kind: "json", title: "Load calibration file" });
    if (!p) return;
    try {
      const r = await api("/api/calibration/load", { path: p });
      C.data = r.calibration; C.source = basename(r.path); C.measuredPx = null;
      $("#cal-ppm").value = r.pixels_per_mm ? +(+r.pixels_per_mm).toFixed(6) : "";
      $("#cal-save-path").value = r.path;
      renderCalibration();
      if (r.pixels_per_mm) toast("Calibration loaded", `${esc(C.source)}: ${fmt(r.pixels_per_mm, 4)} px/mm`, "success");
      else toast("Calibration loaded", "This file has camera parameters but no pixels per mm. Measure it with Pattern or Ruler mode.", "warn", 7000);
    } catch (e) { toast("Could not load calibration", esc(e.message), "error", 8000); }
  };

  $("#cal-apply").onclick = async () => {
    const ppm = calPpm(); if (!ppm) return;
    $("#ppm").value = ppm;
    $("#res-ppm").value = ppm;
    const done = [];
    if (V.sid) {
      try {
        const p = params(); p.first_good = +$("#proc-first").value; p.last_good = +$("#proc-last").value;
        V.info = await api(`/api/video/${V.sid}/meta`, p);
        done.push(`written to the .meta of ${esc(V.info.name)}`);
        preview();
      } catch (e) { toast("Could not update video", esc(e.message), "error"); }
    }
    if (R.paths.length) { done.push("used for the loaded results"); analyze(); }
    toast("Calibration applied", `${fmt(ppm, 4)} px/mm ` + (done.length ? done.join(" and ") + "." : "will be used for the next video and results."), "success", 7000);
  };

  $("#cal-save").onclick = async () => {
    let path = $("#cal-save-path").value.trim();
    const picked = await pickSavePath({ title: "Save calibration", name: path ? basename(path) : "calibration.json", start: path ? dirname(path) : "" });
    if (picked === "") return; // cancelled
    if (picked) { path = picked; $("#cal-save-path").value = picked; }
    if (!path) { toast("Choose a file name", "Type the path of the calibration JSON to write.", "warn"); return; }
    const data = Object.assign({}, C.data || {});
    const ppm = calPpm(); if (ppm) data.pixels_per_mm = ppm;
    try {
      const r = await api("/api/calibration/save", { path, calibration: data });
      $("#cal-save-path").value = r.path; C.source = C.source || basename(r.path);
      renderCalibration();
      toast("Calibration saved", `<span class="mono">${esc(r.path)}</span>`, "success", 7000);
    } catch (e) { toast("Save failed", esc(e.message), "error"); }
  };

  // Keep the calibration page in sync with a video's stored pixels per mm.
  $("#ppm").addEventListener("change", () => {
    const v = parseFloat($("#ppm").value);
    if (isFinite(v) && v > 0 && !calPpm()) { $("#cal-ppm").value = v; C.source = "Video .meta"; renderCalibration(); }
  });

  // ------------------------------------------------------------------ Connect (hosted page)
  const pageUrl = () => location.origin + location.pathname;
  function showConnect(reason) {
    if (!HOSTED) return;
    const msg = {
      offline: ["red", "arcjetCV is not running on this computer (port " + ENG.port + ")."],
      origin: ["amber", "arcjetCV is running but has not allowed this website yet. Run the command above."],
      token: ["amber", "arcjetCV is running but this page is not paired. Run the command above, or paste the token under Advanced."],
      checking: ["gray", "Looking for the engine..."],
    }[reason] || ["gray", reason];
    $("#connect-cmd").textContent = `arcjetcv-web --site ${pageUrl()}`;
    $("#connect-status").className = "badge " + msg[0];
    $("#connect-status").textContent = msg[1];
    $("#connect-port").value = ENG.port;
    $("#connect-token").value = ENG.token;
    $("#connect-modal").classList.add("open");
  }
  async function connect() {
    if (!HOSTED) return true;
    showConnect("checking");
    let r;
    try { r = await api("/api/ping"); } catch (e) { showConnect("offline"); return false; }
    if (!r.origin_allowed) { showConnect("origin"); return false; }
    if (!r.token_ok) { showConnect("token"); return false; }
    $("#connect-modal").classList.remove("open");
    return true;
  }
  $("#connect-retry").onclick = async () => {
    ENG.port = +$("#connect-port").value || 5050;
    ENG.token = $("#connect-token").value.trim();
    store.set("acv-port", ENG.port); store.set("acv-token", ENG.token);
    if (await connect()) { $("#cal-print").href = engineUrl("/api/calibration/pattern.pdf"); refreshInfo().then(() => go(location.hash.slice(1) || "home")); }
  };

  // ------------------------------------------------------------------ Boot
  $("#cal-print").href = engineUrl("/api/calibration/pattern.pdf");
  setMethod("AutoHSV");
  setCalMode("pattern");
  renderCalibration();
  renderResults();
  setResultFiles([]);
  connect().then(() => refreshInfo()).then(() => go(location.hash.slice(1) || "home"));
  setInterval(() => {
    if ($("#connect-modal").classList.contains("open")) { connect().then((ok) => ok && refreshInfo()); return; }
    if ($("#page-home").classList.contains("active")) refreshInfo(); else api("/api/info").catch(() => {});
  }, 8000);
})();
