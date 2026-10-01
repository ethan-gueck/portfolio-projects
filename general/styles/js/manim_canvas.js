/*
 * manim_canvas.js — a tiny Manim-flavoured 2D engine for <canvas>.
 *
 * Topic-agnostic: pages describe a scene as a Timeline of steps, and each
 * step draws itself at progress p ∈ [0, 1] using ManimCanvas primitives.
 * Colours and fonts come from a theme (general.themes Theme.to_dict()):
 *   { stage: { background, grid, axes, text, muted, primary, ... }, stageGradient, fonts }
 * The camera is sticky and sprung: pages ask Manim.view.follow() whether to move
 * it, and scene.moveTo() eases there with a critically damped spring that keeps
 * its velocity when retargeted mid-move. Tick spacing follows the visible span
 * and crossfades when it changes, so the grid never pops.
 * Exposes window.Manim = { ManimCanvas, Timeline, rate, view }.
 */
(function (global) {
  "use strict";

  // ---- Rate functions (same shapes as manim.utils.rate_functions) ----------
  const sigmoid = (x) => 1 / (1 + Math.exp(-x));
  const clamp01 = (t) => Math.min(Math.max(t, 0), 1);
  const rate = {
    linear: (t) => t,
    smooth(t, inflection = 10) {
      const err = sigmoid(-inflection / 2);
      return clamp01((sigmoid(inflection * (t - 0.5)) - err) / (1 - 2 * err));
    },
    rushInto: (t) => 2 * rate.smooth(t / 2),
    rushFrom: (t) => 2 * rate.smooth(t / 2 + 0.5) - 1,
    thereAndBack: (t) => rate.smooth(t < 0.5 ? 2 * t : 2 * (1 - t)),
  };

  // ---- Viewport helpers: keep the camera steady while values change ---------
  const lerp = (a, b, t) => a + (b - a) * t;
  const span = (v, axis) => v[`${axis}_max`] - v[`${axis}_min`];
  const view = {
    /** True if every [x, y] point lies inside `v`, at least `margin` (fraction of span) from the edges. */
    contains(v, points, margin = 0.06) {
      const mx = span(v, "x") * margin, my = span(v, "y") * margin;
      return points.every(([x, y]) => x >= v.x_min + mx && x <= v.x_max - mx && y >= v.y_min + my && y <= v.y_max - my);
    },
    /**
     * Should the camera move from `current` to `ideal`? Only when a key point would
     * leave the view, or the content has shrunk to a small part of it (`zoomIn`).
     * Small changes keep the axes fixed, so sliders feel steady.
     */
    shouldRefit(current, ideal, points, { margin = 0.06, zoomIn = 0.4 } = {}) {
      if (!current) return true;
      if (!view.contains(current, points, margin)) return true;
      return span(ideal, "x") < span(current, "x") * zoomIn || span(ideal, "y") < span(current, "y") * zoomIn * 0.75;
    },
    /** `v` widened by `factor` around its centre, snapped outward to its ticks. */
    roomy(v, factor = 1.2) {
      const hx = (span(v, "x") * factor) / 2, hy = (span(v, "y") * factor) / 2;
      const cx = (v.x_min + v.x_max) / 2, cy = (v.y_min + v.y_max) / 2;
      return {
        x_min: Math.floor((cx - hx) / v.x_step) * v.x_step, x_max: Math.ceil((cx + hx) / v.x_step) * v.x_step,
        y_min: Math.floor((cy - hy) / v.y_step) * v.y_step, y_max: Math.ceil((cy + hy) / v.y_step) * v.y_step,
        x_step: v.x_step, y_step: v.y_step,
      };
    },
    /**
     * Where the camera should go as values change: `null` to stay put, else the
     * ideal view with some `slack`, so the next few changes also fit without moving.
     */
    follow(current, ideal, points, { slack = 1.2, margin = 0.06, zoomIn = 0.4 } = {}) {
      if (!view.shouldRefit(current, ideal, points, { margin, zoomIn: zoomIn / slack })) return null;
      return view.roomy(ideal, slack);
    },
    /** Interpolated view; tick spacing switches to the target's straight away. */
    lerp(a, b, t) {
      const out = { x_step: b.x_step, y_step: b.y_step };
      for (const key of ["x_min", "x_max", "y_min", "y_max"]) out[key] = lerp(a[key], b[key], t);
      return out;
    },
  };
  /** 1/2/5 × 10ⁿ tick spacing for roughly `target` ticks (same as general.plotting.nice_step). */
  function niceStep(extent, target = 8) {
    if (!(extent > 0)) return 1;
    const raw = extent / target;
    const magnitude = Math.pow(10, Math.floor(Math.log10(raw)));
    for (const m of [1, 2, 5, 10]) if (raw <= m * magnitude) return m * magnitude;
    return 10 * magnitude;
  }

  /**
   * Critically damped spring step (Game Programming Gems 4, "SmoothDamp").
   * Returns [position, velocity]; retargeting keeps velocity, so motion stays fluid.
   */
  function smoothDamp(current, target, velocity, smoothTime, dt) {
    const omega = 2 / smoothTime;
    const x = omega * dt;
    const decay = 1 / (1 + x + 0.48 * x * x + 0.235 * x * x * x);
    const change = current - target;
    const temp = (velocity + omega * change) * dt;
    return [target + (change + temp) * decay, (velocity - omega * temp) * decay];
  }

  const EDGES = ["x_min", "x_max", "y_min", "y_max"];
  const TICK_FADE_MS = 320;
  const reduceMotion = () => global.matchMedia && global.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---- Canvas + coordinate system ------------------------------------------
  class ManimCanvas {
    constructor(canvas, { theme, view, aspect = 16 / 9, margin = 44 } = {}) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.setTheme(theme);
      this.aspect = aspect;
      this.margin = margin;
      this.onResize = null;
      this.setView(view || { x_min: -5, x_max: 5, y_min: -5, y_max: 5, x_step: 1, y_step: 1 });
      const refresh = () => { this.resize(); if (this.onResize) this.onResize(); };
      new ResizeObserver(refresh).observe(canvas);
      if (document.fonts) document.fonts.ready.then(refresh);  // redraw once web fonts arrive
      this.resize();
    }

    setTheme(theme) {
      this.theme = theme.stage;
      this.gradient = theme.stageGradient || [];
      this.fonts = theme.fonts || { sans: "system-ui, sans-serif", mono: "monospace" };
    }

    font(size, weight = 400) { return `${weight} ${size}px ${this.fonts.sans}`; }

    /** Jump straight to a view (cancels any camera move). */
    setView(v) {
      this._stopCamera();
      this.view = { ...v };
      this.targetView = { ...v };
    }

    /**
     * Ease the camera toward `target` on a critically damped spring. `onFrame`
     * redraws each step. Calling again mid-move just retargets: the camera keeps
     * its current velocity, so rapid slider changes stay fluid instead of
     * restarting from rest. `smoothTime` ≈ seconds to cover most of the distance.
     */
    moveTo(target, { onFrame, smoothTime = 0.3 } = {}) {
      this.targetView = { ...target };
      this._onCamera = onFrame;
      this.smoothTime = smoothTime;
      if (reduceMotion()) {
        this.setView(target);
        if (onFrame) onFrame();
        return;
      }
      if (!this._cameraRunning) this._startCamera();
    }

    _stopCamera() {
      cancelAnimationFrame(this._cameraRaf);
      clearTimeout(this._cameraTimer);
      this._cameraRunning = false;
      this._velocity = Object.fromEntries(EDGES.map((k) => [k, 0]));
    }

    _startCamera() {
      this._cameraRunning = true;
      this._velocity = this._velocity || Object.fromEntries(EDGES.map((k) => [k, 0]));
      let last = performance.now();
      this._lastCameraTick = last;
      const tick = (now) => {
        const dt = Math.min(Math.max((now - last) / 1000, 0), 0.05);  // cap dt after tab switches
        last = now;
        this._lastCameraTick = now;
        const target = this.targetView;
        const tolerance = 1e-4 * Math.max(target.x_max - target.x_min, target.y_max - target.y_min);
        let moving = false;
        for (const key of EDGES) {
          const [position, velocity] = smoothDamp(this.view[key], target[key], this._velocity[key], this.smoothTime, dt);
          if (Math.abs(position - target[key]) < tolerance && Math.abs(velocity) < tolerance) {
            this.view[key] = target[key];
            this._velocity[key] = 0;
          } else {
            this.view[key] = position;
            this._velocity[key] = velocity;
            moving = true;
          }
        }
        this.view.x_step = target.x_step;
        this.view.y_step = target.y_step;
        if (this._onCamera) this._onCamera();
        if (moving || this.ticksFading()) this._cameraRaf = requestAnimationFrame(tick);
        else this._cameraRunning = false;
      };
      this._cameraRaf = requestAnimationFrame(tick);
      // Background tabs (and headless browsers) pause rAF: if no frame arrives, land directly.
      clearTimeout(this._cameraTimer);
      this._cameraTimer = setTimeout(() => {
        if (!this._cameraRunning || performance.now() - this._lastCameraTick < 250) return;
        this.setView(this.targetView);
        if (this._onCamera) this._onCamera();
      }, 400);
    }

    /**
     * Tick positions for `axis` ("x" | "y") with an opacity each. Spacing follows
     * the visible span; when it changes, new ticks fade in while old ones fade out.
     */
    ticks(axis) {
      const lo = this.view[`${axis}_min`], hi = this.view[`${axis}_max`];
      const step = niceStep(hi - lo);
      this._tickState = this._tickState || {};
      const state = this._tickState[axis] || (this._tickState[axis] = { step, prev: null, since: 0 });
      const now = performance.now();
      if (step !== state.step) Object.assign(state, { prev: state.step, step, since: now });
      const k = state.prev === null ? 1 : clamp01((now - state.since) / TICK_FADE_MS);
      if (k >= 1) state.prev = null;
      const onGrid = (value, s) => Math.abs(value / s - Math.round(value / s)) < 1e-6;
      const out = [];
      const add = (s, alphaFor) => {
        for (let i = Math.ceil(lo / s - 1e-9); i * s <= hi + 1e-9; i++) {
          const value = i * s;
          const alpha = alphaFor(value);
          if (alpha > 0) out.push({ value, alpha });
        }
      };
      add(step, (value) => (state.prev !== null && onGrid(value, state.prev) ? 1 : k));
      if (state.prev !== null) {
        const prev = state.prev;
        add(prev, (value) => (onGrid(value, step) ? 0 : 1 - k));
      }
      return out;
    }

    ticksFading() {
      return Object.values(this._tickState || {}).some((s) => s.prev !== null);
    }

    resize() {
      const dpr = global.devicePixelRatio || 1;
      const w = this.canvas.clientWidth || 800;
      const h = w / this.aspect;
      this.canvas.style.height = `${h}px`;
      this.canvas.width = Math.round(w * dpr);
      this.canvas.height = Math.round(h * dpr);
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      this.width = w;
      this.height = h;
    }

    // Math coordinates -> CSS pixels.
    px(x) { const v = this.view; return this.margin + ((x - v.x_min) / (v.x_max - v.x_min)) * (this.width - 2 * this.margin); }
    py(y) { const v = this.view; return this.height - this.margin - ((y - v.y_min) / (v.y_max - v.y_min)) * (this.height - 2 * this.margin); }

    clear() {
      this._placed = [];  // label rectangles drawn this frame, for collision avoidance
      const { ctx } = this;
      ctx.clearRect(0, 0, this.width, this.height);
      if (this.gradient.length) {
        const g = ctx.createLinearGradient(0, 0, this.width, this.height);  // 135deg, like the CSS
        this.gradient.forEach(([color, stop]) => g.addColorStop(stop, color));
        ctx.fillStyle = g;
      } else {
        ctx.fillStyle = this.theme.background;
      }
      ctx.fillRect(0, 0, this.width, this.height);
    }

    withClip(fn) {
      const { ctx, margin } = this;
      ctx.save();
      ctx.beginPath();
      ctx.rect(margin, margin, this.width - 2 * margin, this.height - 2 * margin);
      ctx.clip();
      fn();
      ctx.restore();
    }

    // ---- Primitives: each takes progress p (0 = hidden, 1 = fully drawn) ---

    /** NumberPlane-style background grid, fading in. */
    grid(p, color = this.theme.grid) {
      const { ctx, view: v } = this;
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth = 1;
      for (const { value: x, alpha } of this.ticks("x")) {
        ctx.globalAlpha = p * alpha;
        ctx.beginPath();
        ctx.moveTo(this.px(x), this.py(v.y_min));
        ctx.lineTo(this.px(x), this.py(v.y_max));
        ctx.stroke();
      }
      for (const { value: y, alpha } of this.ticks("y")) {
        ctx.globalAlpha = p * alpha;
        ctx.beginPath();
        ctx.moveTo(this.px(v.x_min), this.py(y));
        ctx.lineTo(this.px(v.x_max), this.py(y));
        ctx.stroke();
      }
      ctx.restore();
    }

    /** Axes that "Create" outward from their start, with ticks and numbers fading in. */
    axes(p, color = this.theme.axes) {
      const { ctx, view: v } = this;
      const x0 = Math.min(Math.max(0, v.x_min), v.x_max);
      const y0 = Math.min(Math.max(0, v.y_min), v.y_max);
      ctx.save();
      ctx.strokeStyle = color;
      ctx.fillStyle = color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(this.px(v.x_min), this.py(y0));
      ctx.lineTo(this.px(v.x_min + (v.x_max - v.x_min) * p), this.py(y0));
      ctx.moveTo(this.px(x0), this.py(v.y_min));
      ctx.lineTo(this.px(x0), this.py(v.y_min + (v.y_max - v.y_min) * p));
      ctx.stroke();

      if (p > 0.6) {
        const a = (p - 0.6) / 0.4;
        ctx.globalAlpha = a;
        ctx.fillStyle = this.theme.muted;
        ctx.font = this.font(12);
        ctx.lineWidth = 1.5;
        const fmt = (n) => String(Math.round(n * 1e6) / 1e6);
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        for (const { value: x, alpha } of this.ticks("x")) {
          if (Math.abs(x) < 1e-9) continue;
          ctx.globalAlpha = a * alpha;
          ctx.beginPath();
          ctx.moveTo(this.px(x), this.py(y0) - 4);
          ctx.lineTo(this.px(x), this.py(y0) + 4);
          ctx.stroke();
          ctx.fillText(fmt(x), this.px(x), this.py(y0) + 7);
        }
        ctx.textAlign = "right";
        ctx.textBaseline = "middle";
        for (const { value: y, alpha } of this.ticks("y")) {
          if (Math.abs(y) < 1e-9) continue;
          ctx.globalAlpha = a * alpha;
          ctx.beginPath();
          ctx.moveTo(this.px(x0) - 4, this.py(y));
          ctx.lineTo(this.px(x0) + 4, this.py(y));
          ctx.stroke();
          ctx.fillText(fmt(y), this.px(x0) - 8, this.py(y));
        }
      }
      ctx.restore();
    }

    /** Create(axes.plot(f)): traces the function left to right. */
    curve(f, p, color = this.theme.primary, { width = 4, samples = 400 } = {}) {
      const { ctx, view: v } = this;
      const n = Math.max(2, Math.ceil(samples * p));
      this.withClip(() => {
        ctx.strokeStyle = color;
        ctx.lineWidth = width;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.beginPath();
        for (let i = 0; i < n; i++) {
          const x = v.x_min + ((v.x_max - v.x_min) * (i / (samples - 1)));
          const y = f(x);
          i === 0 ? ctx.moveTo(this.px(x), this.py(y)) : ctx.lineTo(this.px(x), this.py(y));
        }
        ctx.stroke();
      });
    }

    /** Create(Line / DashedLine) from (x1, y1) toward (x2, y2). */
    line(x1, y1, x2, y2, p, color, { width = 2, dash = null } = {}) {
      const { ctx } = this;
      this.withClip(() => {
        ctx.strokeStyle = color;
        ctx.lineWidth = width;
        if (dash) ctx.setLineDash(dash);
        ctx.beginPath();
        ctx.moveTo(this.px(x1), this.py(y1));
        ctx.lineTo(this.px(x1 + (x2 - x1) * p), this.py(y1 + (y2 - y1) * p));
        ctx.stroke();
      });
    }

    /** GrowFromCenter(Dot). */
    dot(x, y, p, color, radius = 7) {
      const { ctx } = this;
      ctx.save();
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(this.px(x), this.py(y), radius * p, 0, 2 * Math.PI);
      ctx.fill();
      ctx.restore();
    }

    /** Flash: rays burst outward then fade, like manim.animation.indication.Flash. */
    flash(x, y, p, color, { rays = 12, inner = 10, outer = 26 } = {}) {
      if (p <= 0 || p >= 1) return;
      const { ctx } = this;
      const cx = this.px(x), cy = this.py(y);
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2.5;
      ctx.globalAlpha = 1 - p;
      ctx.beginPath();
      for (let i = 0; i < rays; i++) {
        const t = (i / rays) * 2 * Math.PI;
        const r1 = inner + (outer - inner) * p * 0.5, r2 = inner + (outer - inner) * p;
        ctx.moveTo(cx + r1 * Math.cos(t), cy + r1 * Math.sin(t));
        ctx.lineTo(cx + r2 * Math.cos(t), cy + r2 * Math.sin(t));
      }
      ctx.stroke();
      ctx.restore();
    }

    /** FadeIn(Text, shift=UP): label near a point, offset in pixels. */
    label(text, x, y, p, color = this.theme.text, { dx = 10, dy = -14, align = "left", size = 15 } = {}) {
      const { ctx } = this;
      ctx.save();
      ctx.globalAlpha = p;
      ctx.fillStyle = color;
      ctx.font = this.font(size, 500);
      ctx.textAlign = align;
      ctx.textBaseline = "middle";
      const w = ctx.measureText(text).width;
      const px = Math.min(Math.max(this.px(x) + dx, 8), this.width - 8);
      const left = align === "center" ? px - w / 2 : align === "right" ? px - w : px;
      let py = Math.min(Math.max(this.py(y) + dy + (1 - p) * 10, 12), this.height - 12);
      // Nudge away (in the direction of dy) from labels already placed this frame.
      const rect = () => ({ x: left - 4, y: py - size * 0.7, w: w + 8, h: size * 1.4 });
      const hits = (r) => this._placed.some((o) => r.x < o.x + o.w && o.x < r.x + r.w && r.y < o.y + o.h && o.y < r.y + r.h);
      for (let tries = 0; tries < 6 && hits(rect()); tries++) py += (dy < 0 ? -1 : 1) * size * 1.4;
      const plate = rect();
      this._placed.push(plate);
      // Background plate (like Manim's add_background_rectangle) keeps labels readable over ticks.
      ctx.fillStyle = this.theme.plate;
      ctx.globalAlpha = p;
      ctx.fillRect(plate.x, plate.y, plate.w, plate.h);
      ctx.globalAlpha = p;
      ctx.fillStyle = color;
      ctx.fillText(text, px, py);
      ctx.restore();
    }

    /** Screen-space caption, like a Text pinned to_corner(UL). */
    caption(text, p, color = this.theme.text) {
      const { ctx } = this;
      ctx.save();
      ctx.globalAlpha = p;
      ctx.fillStyle = color;
      ctx.font = this.font(16);
      ctx.textBaseline = "top";
      ctx.fillText(text, 12, 10);
      ctx.restore();
    }
  }

  // ---- Timeline: ordered steps, like a chain of self.play(...) calls --------
  class Timeline {
    /**
     * @param {ManimCanvas} scene
     * @param {object} opts  onFrame(t, total), onStep(step|null), onDone()
     */
    constructor(scene, { onFrame, onStep, onDone } = {}) {
      this.scene = scene;
      this.steps = [];
      this.cursor = 0;          // end time of the last sequential step
      this.time = 0;
      this.speed = 1;
      this.playing = false;
      this.hooks = { onFrame, onStep, onDone };
      this._activeStep = undefined;
    }

    /**
     * Add a step. `draw(p)` renders it at progress p.
     *   duration  seconds (like run_time)
     *   rate      rate function (default smooth)
     *   parallel  true = start with the previous step (like AnimationGroup)
     *   wait      pause after the step (like self.wait())
     *   id, caption  optional metadata surfaced through onStep
     */
    add({ draw, duration = 1, rate: rf = rate.smooth, parallel = false, wait = 0, ...meta }) {
      const prev = this.steps[this.steps.length - 1];
      const start = parallel && prev ? prev.start : this.cursor;
      const step = { draw, duration, rate: rf, start, end: start + duration, ...meta };
      this.steps.push(step);
      this.cursor = Math.max(this.cursor, step.end + wait);
      return this;
    }

    get total() { return this.cursor; }

    /** Draw the scene at absolute time t (seconds). */
    render(t = this.time) {
      this.time = Math.min(Math.max(t, 0), this.total);
      this.scene.clear();
      let active = null;
      for (const step of this.steps) {
        if (this.time < step.start) continue;
        const local = step.duration ? clamp01((this.time - step.start) / step.duration) : 1;
        step.draw(step.rate(local), local);
        if (step.caption && this.time <= step.end + 1e-9) active = step;
      }
      if (!active) active = [...this.steps].reverse().find((s) => s.caption && this.time >= s.start) || null;
      if (active !== this._activeStep) {
        this._activeStep = active;
        if (this.hooks.onStep) this.hooks.onStep(active);
      }
      if (this.hooks.onFrame) this.hooks.onFrame(this.time, this.total);
    }

    play({ from = 0 } = {}) {
      this.stop();
      this.time = from >= this.total ? 0 : from;
      this.playing = true;
      let last = performance.now();
      const tick = (now) => {
        if (!this.playing) return;
        this.render(this.time + ((now - last) / 1000) * this.speed);
        last = now;
        if (this.time >= this.total) {
          this.playing = false;
          if (this.hooks.onDone) this.hooks.onDone();
          return;
        }
        this._raf = requestAnimationFrame(tick);
      };
      this._raf = requestAnimationFrame(tick);
    }

    stop() { this.playing = false; cancelAnimationFrame(this._raf); }
    seek(fraction) { this.stop(); this.render(fraction * this.total); }
    finish() { this.stop(); this.render(this.total); }
  }

  global.Manim = { ManimCanvas, Timeline, rate, view, niceStep, smoothDamp };
})(window);
