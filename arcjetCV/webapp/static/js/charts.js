/* Tiny dependency-free SVG chart library for arcjetCV Web.
 *
 *   const c = new MiniChart(el, {series: [{name, color, x, y, mode}], xLabel, yLabel});
 *   c.update(newOpts);
 *
 * series.mode: "line" | "markers" | "both"; series.dash: "4 3"; series.hidden
 * opts.vlines: [{x, color, label, dash}], opts.bands: [{x0, x1, color}]
 * opts.invertY, opts.equal (equal axis scaling), opts.onClick(x, y), opts.legend
 */
(function () {
  const NS = "http://www.w3.org/2000/svg";

  function el(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  function niceStep(span, count) {
    if (!(span > 0)) return 1;
    const raw = span / Math.max(1, count);
    const mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const r = raw / mag;
    return (r >= 5 ? 10 : r >= 2 ? 5 : r >= 1 ? 2 : 1) * mag;
  }

  function ticks(lo, hi, count) {
    const step = niceStep(hi - lo, count);
    const out = [];
    for (let v = Math.ceil(lo / step) * step; v <= hi + step * 1e-9; v += step) out.push(+v.toPrecision(12));
    return { values: out, step };
  }

  function fmt(v, step) {
    if (v === null || v === undefined || !isFinite(v)) return "-";
    const a = Math.abs(v);
    if (a !== 0 && (a >= 1e5 || a < 1e-3)) return v.toExponential(1);
    const d = step ? Math.max(0, Math.min(6, -Math.floor(Math.log10(step) + 1e-9))) : (a < 1 ? 3 : a < 100 ? 2 : 1);
    return v.toFixed(d);
  }

  class MiniChart {
    constructor(container, opts) {
      this.box = container;
      this.box.innerHTML = "";
      this.svg = el("svg", {}, this.box);
      this.tip = document.createElement("div");
      this.tip.className = "chart-tip";
      this.box.appendChild(this.tip);
      this.legendEl = document.createElement("div");
      this.legendEl.className = "chart-legend";
      this.box.after(this.legendEl);
      this.opts = {};
      this.ro = new ResizeObserver(() => this.render());
      this.ro.observe(this.box);
      this.svg.addEventListener("mousemove", (e) => this.hover(e));
      this.svg.addEventListener("mouseleave", () => { this.tip.style.display = "none"; if (this.cross) this.cross.style.display = "none"; });
      this.svg.addEventListener("click", (e) => this.click(e));
      this.update(opts || {});
    }

    update(opts) {
      this.opts = Object.assign({ legend: true }, opts);
      this.render();
      this.renderLegend();
    }

    extent() {
      const o = this.opts;
      let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
      for (const s of o.series || []) {
        if (s.hidden) continue;
        for (let i = 0; i < s.x.length; i++) {
          const x = s.x[i], y = s.y[i];
          if (x === null || y === null || !isFinite(x) || !isFinite(y)) continue;
          if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y;
        }
      }
      for (const v of o.vlines || []) { if (isFinite(v.x)) { x0 = Math.min(x0, v.x); x1 = Math.max(x1, v.x); } }
      if (o.xRange) { [x0, x1] = o.xRange; }
      if (o.yRange) { [y0, y1] = o.yRange; }
      if (!isFinite(x0)) { x0 = 0; x1 = 1; }
      if (!isFinite(y0)) { y0 = 0; y1 = 1; }
      if (x0 === x1) { x0 -= 0.5; x1 += 0.5; }
      if (y0 === y1) { y0 -= 0.5; y1 += 0.5; }
      if (!o.yRange) { const p = (y1 - y0) * 0.06; y0 -= p; y1 += p; }
      if (!o.xRange && o.padX) { const p = (x1 - x0) * 0.03; x0 -= p; x1 += p; }
      return { x0, x1, y0, y1 };
    }

    render() {
      const o = this.opts, svg = this.svg;
      const W = this.box.clientWidth, H = this.box.clientHeight;
      if (!W || !H) return;
      svg.innerHTML = "";
      svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
      const m = { l: o.compact ? 44 : 58, r: 14, t: 10, b: o.xLabel ? 40 : 26 };
      const pw = Math.max(10, W - m.l - m.r), ph = Math.max(10, H - m.t - m.b);
      let { x0, x1, y0, y1 } = this.extent();

      if (o.equal) {
        const ux = (x1 - x0) / pw, uy = (y1 - y0) / ph;
        if (ux > uy) { const c = (y0 + y1) / 2, h = ux * ph / 2; y0 = c - h; y1 = c + h; }
        else { const c = (x0 + x1) / 2, h = uy * pw / 2; x0 = c - h; x1 = c + h; }
      }
      const sx = (x) => m.l + ((x - x0) / (x1 - x0)) * pw;
      const sy = o.invertY ? (y) => m.t + ((y - y0) / (y1 - y0)) * ph : (y) => m.t + ph - ((y - y0) / (y1 - y0)) * ph;
      this.geom = { m, pw, ph, x0, x1, y0, y1, sx, sy };

      const clipId = "clip" + Math.random().toString(36).slice(2, 8);
      const defs = el("defs", {}, svg);
      el("rect", { x: m.l, y: m.t, width: pw, height: ph }, el("clipPath", { id: clipId }, defs));

      // grid + axes
      const xt = ticks(x0, x1, Math.max(2, Math.floor(pw / 90)));
      const yt = ticks(y0, y1, Math.max(3, Math.floor(ph / 40)));
      const grid = el("g", { class: "grid" }, svg);
      const axis = el("g", { class: "axis" }, svg);
      for (const v of yt.values) {
        const y = sy(v);
        el("line", { x1: m.l, x2: m.l + pw, y1: y, y2: y }, grid);
        el("text", { x: m.l - 8, y: y + 3.5, "text-anchor": "end" }, axis).textContent = fmt(v, yt.step);
      }
      for (const v of xt.values) {
        const x = sx(v);
        el("line", { x1: x, x2: x, y1: m.t, y2: m.t + ph }, grid);
        el("text", { x, y: m.t + ph + 16, "text-anchor": "middle" }, axis).textContent = fmt(v, xt.step);
      }
      el("path", { d: `M${m.l},${m.t}V${m.t + ph}H${m.l + pw}`, fill: "none" }, axis);
      if (o.xLabel) el("text", { class: "axis-label", x: m.l + pw / 2, y: H - 6, "text-anchor": "middle" }, svg).textContent = o.xLabel;
      if (o.yLabel) el("text", { class: "axis-label", x: 12, y: m.t + ph / 2, "text-anchor": "middle", transform: `rotate(-90 12 ${m.t + ph / 2})` }, svg).textContent = o.yLabel;

      const plot = el("g", { "clip-path": `url(#${clipId})` }, svg);
      for (const b of o.bands || []) {
        const a = sx(Math.min(b.x0, b.x1)), z = sx(Math.max(b.x0, b.x1));
        el("rect", { x: a, y: m.t, width: Math.max(0, z - a), height: ph, fill: b.color || "rgba(78,115,223,0.1)" }, plot);
      }
      for (const v of o.vlines || []) {
        if (!isFinite(v.x)) continue;
        el("line", { x1: sx(v.x), x2: sx(v.x), y1: m.t, y2: m.t + ph, stroke: v.color || "#111827", "stroke-width": v.width || 1.2, "stroke-dasharray": v.dash || "5 4" }, plot);
        if (v.label) el("text", { x: sx(v.x) + 5, y: m.t + 13, "font-size": 11, fill: v.color || "#111827", "font-weight": 600 }, plot).textContent = v.label;
      }

      this.points = [];
      for (const s of o.series || []) {
        if (s.hidden) continue;
        const mode = s.mode || "line";
        const color = s.color || "#4e73df";
        if (mode !== "markers") {
          let d = "", pen = false;
          for (let i = 0; i < s.x.length; i++) {
            const x = s.x[i], y = s.y[i];
            if (x === null || y === null || !isFinite(x) || !isFinite(y)) { pen = false; continue; }
            d += (pen ? "L" : "M") + sx(x).toFixed(1) + "," + sy(y).toFixed(1);
            pen = true;
          }
          if (d) el("path", { d, fill: "none", stroke: color, "stroke-width": s.width || 2, "stroke-dasharray": s.dash, "stroke-linejoin": "round", "stroke-linecap": "round", opacity: s.opacity }, plot);
        }
        const r = s.size || 3;
        const g = mode !== "line" ? el("g", { fill: color, opacity: s.opacity }, plot) : null;
        const step = s.x.length > 6000 ? Math.ceil(s.x.length / 6000) : 1;
        for (let i = 0; i < s.x.length; i += step) {
          const x = s.x[i], y = s.y[i];
          if (x === null || y === null || !isFinite(x) || !isFinite(y)) continue;
          const px = sx(x), py = sy(y);
          if (g) el("circle", { cx: px.toFixed(1), cy: py.toFixed(1), r }, g);
          if (s.tooltip !== false) this.points.push({ px, py, x, y, s });
        }
      }
      this.cross = el("line", { y1: m.t, y2: m.t + ph, stroke: "#94a3b8", "stroke-dasharray": "3 3", style: "display:none" }, svg);
      this.dot = el("circle", { r: 5, fill: "none", stroke: "#111827", "stroke-width": 2, style: "display:none" }, svg);
    }

    renderLegend() {
      const o = this.opts;
      this.legendEl.innerHTML = "";
      if (!o.legend) return;
      (o.series || []).forEach((s) => {
        if (!s.name || s.legend === false) return;
        const sp = document.createElement("span");
        if (s.hidden) sp.className = "off";
        sp.innerHTML = `<i style="background:${s.color || "#4e73df"}"></i>${s.name}`;
        sp.onclick = () => { s.hidden = !s.hidden; this.render(); this.renderLegend(); };
        this.legendEl.appendChild(sp);
      });
    }

    local(e) {
      const r = this.svg.getBoundingClientRect();
      return { x: e.clientX - r.left, y: e.clientY - r.top };
    }

    hover(e) {
      if (!this.geom || this.opts.tooltip === false) return;
      const p = this.local(e), g = this.geom;
      if (p.x < g.m.l || p.x > g.m.l + g.pw) { this.tip.style.display = "none"; return; }
      let best = null, bd = Infinity;
      for (const q of this.points) {
        const d = (q.px - p.x) ** 2 + ((q.py - p.y) ** 2) * 0.25;
        if (d < bd) { bd = d; best = q; }
      }
      if (this.opts.onClick) {
        this.cross.setAttribute("x1", p.x); this.cross.setAttribute("x2", p.x); this.cross.style.display = "";
      }
      if (!best || bd > 2500) { this.tip.style.display = "none"; this.dot.style.display = "none"; return; }
      this.dot.setAttribute("cx", best.px); this.dot.setAttribute("cy", best.py); this.dot.style.display = "";
      const xl = this.opts.xName || this.opts.xLabel || "x";
      this.tip.innerHTML = `<span class="sw" style="background:${best.s.color || "#4e73df"}"></span><b>${best.s.name || ""}</b><br>${xl}: ${fmt(best.x)}<br>${this.opts.yName || "y"}: ${fmt(best.y)}`;
      this.tip.style.display = "block";
      const bw = this.box.clientWidth;
      const tw = this.tip.offsetWidth;
      this.tip.style.left = Math.min(bw - tw - 4, best.px + 12) + "px";
      this.tip.style.top = Math.max(0, best.py - 50) + "px";
    }

    click(e) {
      if (!this.opts.onClick || !this.geom) return;
      const p = this.local(e), g = this.geom;
      const x = g.x0 + ((p.x - g.m.l) / g.pw) * (g.x1 - g.x0);
      this.opts.onClick(x);
    }
  }

  window.MiniChart = MiniChart;
  window.MiniChart.fmt = fmt;
})();
