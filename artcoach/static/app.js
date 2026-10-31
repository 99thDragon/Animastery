(() => {
  "use strict";

  const W = 800, H = 600;               // logical canvas space shared with the server
  const MEMORY_PREVIEW_MS = 4000;

  const canvas = document.getElementById("canvas");
  const ctx = canvas.getContext("2d");
  const els = {
    list: document.getElementById("exercise-list"),
    name: document.getElementById("ex-name"),
    desc: document.getElementById("ex-desc"),
    tips: document.getElementById("ex-tips"),
    results: document.getElementById("results"),
    submit: document.getElementById("submit"),
    showHeat: document.getElementById("show-heat"),
    countdown: document.getElementById("countdown"),
    penStatus: document.getElementById("pen-status"),
  };

  const state = {
    exercises: [],
    current: null,
    mode: "trace",
    strokes: [],          // [[x, y, t, pressure], ...] per stroke
    active: null,         // stroke in progress
    guideVisible: true,
    result: null,
    countdownTimer: null,
    sawPressure: false,
    hover: null,          // [x, y] of a hovering mouse/pen, for the on-canvas cursor ring
  };

  // ------------------------------------------------------------------ storage (best-effort)
  const store = {
    get(key, fallback) {
      try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; }
    },
    set(key, value) {
      try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* private mode etc. */ }
    },
  };

  // ------------------------------------------------------------------ canvas setup
  function resizeCanvas() {
    const dpr = window.devicePixelRatio || 1;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    render();
  }

  function toLogical(e) {
    const r = canvas.getBoundingClientRect();
    return [((e.clientX - r.left) / r.width) * W, ((e.clientY - r.top) / r.height) * H];
  }

  // ------------------------------------------------------------------ rendering
  function heatColor(d, tol) {
    const k = Math.min(1, d / (tol * 2));
    return `hsl(${Math.round(130 * (1 - k))}, 75%, 42%)`;
  }

  function drawGuide(c, ex) {
    c.save();
    c.lineCap = "round";
    c.lineJoin = "round";
    c.strokeStyle = "rgba(90, 140, 230, 0.35)";
    c.lineWidth = 6;
    for (const s of ex.strokes) {
      c.beginPath();
      s.forEach(([x, y], i) => (i ? c.lineTo(x, y) : c.moveTo(x, y)));
      c.stroke();
    }
    if (ex.directional) {
      for (const s of ex.strokes) {
        const [sx, sy] = s[0];
        c.fillStyle = "rgba(90, 140, 230, 0.9)";
        c.beginPath(); c.arc(sx, sy, 6, 0, Math.PI * 2); c.fill();
        const [ax, ay] = s[s.length - 2], [bx, by] = s[s.length - 1];
        const ang = Math.atan2(by - ay, bx - ax);
        c.beginPath();
        c.moveTo(bx, by);
        c.lineTo(bx - 14 * Math.cos(ang - 0.45), by - 14 * Math.sin(ang - 0.45));
        c.lineTo(bx - 14 * Math.cos(ang + 0.45), by - 14 * Math.sin(ang + 0.45));
        c.closePath(); c.fill();
      }
    }
    c.restore();
  }

  function drawInk(c, strokes) {
    c.save();
    c.lineCap = "round";
    c.strokeStyle = "#1d1b2b";
    for (const s of strokes) {
      if (s.length === 1) {
        c.fillStyle = "#1d1b2b";
        c.beginPath(); c.arc(s[0][0], s[0][1], 1.5, 0, Math.PI * 2); c.fill();
        continue;
      }
      for (let i = 1; i < s.length; i++) {
        const p = (s[i][3] + s[i - 1][3]) / 2;
        c.lineWidth = 1 + p * 5;
        c.beginPath();
        c.moveTo(s[i - 1][0], s[i - 1][1]);
        c.lineTo(s[i][0], s[i][1]);
        c.stroke();
      }
    }
    c.restore();
  }

  function drawHeat(c, result) {
    c.save();
    for (const [x, y, d] of result.heatmap) {
      c.fillStyle = heatColor(d, result.tolerance);
      c.beginPath(); c.arc(x, y, 3.2, 0, Math.PI * 2); c.fill();
    }
    c.restore();
  }

  function paint(c, { forSnapshot = false } = {}) {
    c.fillStyle = "#fffdf8";
    c.fillRect(0, 0, W, H);
    const ex = state.current;
    if (!ex) return;
    if (state.guideVisible || forSnapshot) drawGuide(c, ex);
    drawInk(c, state.active ? [...state.strokes, state.active] : state.strokes);
    if (state.result && (els.showHeat.checked || forSnapshot)) drawHeat(c, state.result);
    if (!forSnapshot) {
      drawHint(c);
      drawCursor(c);
    }
  }

  function drawHint(c) {
    if (state.strokes.length || state.active) return;
    const text = state.guideVisible
      ? (state.mode === "memory" ? "Memorize the shape…" : "Click and drag along the blue lines")
      : "Now draw it from memory: click and drag";
    c.save();
    c.font = "600 18px system-ui, sans-serif";
    c.textAlign = "center";
    c.fillStyle = "rgba(29, 27, 43, 0.45)";
    c.fillText(text, W / 2, 40);
    c.restore();
  }

  function drawCursor(c) {
    if (!state.hover) return;
    const [x, y] = state.hover;
    c.save();
    c.lineWidth = 4;
    c.strokeStyle = "rgba(255, 255, 255, 0.9)";
    c.beginPath(); c.arc(x, y, 9, 0, Math.PI * 2); c.stroke();
    c.lineWidth = 2;
    c.strokeStyle = "#e8508f";
    c.beginPath(); c.arc(x, y, 9, 0, Math.PI * 2); c.stroke();
    c.fillStyle = "#1d1b2b";
    c.beginPath(); c.arc(x, y, 2, 0, Math.PI * 2); c.fill();
    c.restore();
  }

  function render() { paint(ctx); }

  function snapshot() {
    const off = document.createElement("canvas");
    off.width = W; off.height = H;
    paint(off.getContext("2d"), { forSnapshot: true });
    return off.toDataURL("image/png");
  }

  // ------------------------------------------------------------------ input
  function pointFrom(e) {
    const [x, y] = toLogical(e);
    let p = e.pressure;
    if (e.pointerType === "pen" && p > 0 && p !== 0.5) state.sawPressure = true;
    if (!p) p = 0.5;
    return [Math.round(x * 10) / 10, Math.round(y * 10) / 10, Math.round(e.timeStamp), Math.round(p * 1000) / 1000];
  }

  canvas.addEventListener("pointerdown", (e) => {
    if (e.button !== 0 && e.pointerType === "mouse") return;
    canvas.setPointerCapture(e.pointerId);
    if (state.result) clearResult();
    state.active = [pointFrom(e)];
    updatePenStatus(e);
    render();
  });

  canvas.addEventListener("pointermove", (e) => {
    state.hover = e.pointerType === "touch" ? null : toLogical(e);
    if (!state.active) { render(); return; }
    const events = e.getCoalescedEvents ? e.getCoalescedEvents() : [e];
    for (const ev of events.length ? events : [e]) state.active.push(pointFrom(ev));
    render();
  });

  function endStroke() {
    if (!state.active) return;
    state.strokes.push(state.active);
    state.active = null;
    render();
  }
  canvas.addEventListener("pointerup", endStroke);
  canvas.addEventListener("pointercancel", endStroke);
  canvas.addEventListener("pointerleave", () => {
    if (state.active) return;   // pointer capture keeps the stroke going
    state.hover = null;
    render();
  });

  function updatePenStatus(e) {
    const label = e.pointerType === "pen"
      ? (state.sawPressure ? "Stylus with pressure detected" : "Stylus detected")
      : e.pointerType === "touch" ? "Finger input (no pressure)" : "Mouse input (no pressure)";
    els.penStatus.textContent = label;
  }

  // ------------------------------------------------------------------ exercises
  function bestScores() { return store.get("animastery.best", {}); }

  function renderExerciseList() {
    const best = bestScores();
    const groups = {};
    for (const ex of state.exercises) (groups[ex.style] ||= []).push(ex);
    els.list.replaceChildren();
    for (const [style, list] of Object.entries(groups)) {
      const t = document.createElement("div");
      t.className = "group-title";
      t.textContent = style;
      els.list.append(t);
      for (const ex of list) {
        const b = document.createElement("button");
        b.className = "ex-item" + (state.current && state.current.id === ex.id ? " active" : "");
        const name = document.createElement("span");
        name.textContent = ex.name;
        const meta = document.createElement("span");
        meta.className = "ex-meta";
        meta.innerHTML = best[ex.id] != null
          ? `<span class="best">${Number(best[ex.id])}</span>`
          : `Lv ${Number(ex.level)}`;
        b.append(name, meta);
        b.addEventListener("click", () => selectExercise(ex.id));
        els.list.append(b);
      }
    }
  }

  function selectExercise(id) {
    state.current = state.exercises.find((e) => e.id === id) || state.exercises[0];
    store.set("animastery.last", state.current.id);
    els.name.textContent = state.current.name;
    els.desc.textContent = state.current.description +
      (state.current.directional ? " Start at the dot, finish at the arrow." : "");
    els.tips.replaceChildren(...state.current.tips.map((t) => {
      const li = document.createElement("li"); li.textContent = t; return li;
    }));
    resetAttempt();
    renderExerciseList();
  }

  function clearResult() {
    state.result = null;
    if (state.mode === "memory") state.guideVisible = false;
  }

  function resetAttempt() {
    state.strokes = [];
    state.active = null;
    state.result = null;
    clearInterval(state.countdownTimer);
    els.countdown.hidden = true;
    showEmptyResults();
    if (state.mode === "memory") startMemoryPreview();
    else state.guideVisible = true;
    render();
  }

  function startMemoryPreview() {
    state.guideVisible = true;
    let left = MEMORY_PREVIEW_MS / 1000;
    els.countdown.hidden = false;
    els.countdown.textContent = `Memorize… ${left}`;
    state.countdownTimer = setInterval(() => {
      left -= 1;
      if (left <= 0) {
        clearInterval(state.countdownTimer);
        els.countdown.hidden = true;
        state.guideVisible = false;
        render();
      } else {
        els.countdown.textContent = `Memorize… ${left}`;
      }
    }, 1000);
  }

  // ------------------------------------------------------------------ scoring + coaching
  async function submit() {
    if (!state.current) return;
    if (!state.strokes.length) {
      showMessage("Draw something first. Trace over the blue guide lines.");
      return;
    }
    els.submit.disabled = true;
    els.submit.textContent = "Checking…";
    try {
      const res = await fetch("/api/score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exercise_id: state.current.id, strokes: state.strokes }),
      });
      const result = await res.json();
      if (!result.ok) { showMessage(result.error || "Couldn't score that attempt."); return; }
      state.result = result;
      state.guideVisible = true;   // reveal the guide for comparison
      clearInterval(state.countdownTimer);
      els.countdown.hidden = true;
      recordAttempt(result.overall);
      render();
      renderResults(result);
      requestCoaching(result);
    } catch (err) {
      showMessage("Couldn't reach the server. Is it still running?");
    } finally {
      els.submit.disabled = false;
      els.submit.textContent = "Check my lines";
    }
  }

  function recordAttempt(score) {
    const best = bestScores();
    const id = state.current.id;
    if (best[id] == null || score > best[id]) best[id] = score;
    store.set("animastery.best", best);
    const hist = store.get("animastery.history", []);
    hist.push({ id, score, mode: state.mode, at: Date.now() });
    store.set("animastery.history", hist.slice(-200));
    renderExerciseList();
  }

  function scoreColor(s) {
    return s >= 80 ? "var(--good)" : s >= 60 ? "var(--warn)" : "var(--bad)";
  }

  function el(tag, attrs = {}, ...children) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "style") n.style.cssText = v; else n.setAttribute(k, v);
    }
    for (const c of children) n.append(c);
    return n;
  }

  function renderResults(result) {
    const ring = el("div", { class: "score-ring", style: `background:${scoreColor(result.overall)}22;color:${scoreColor(result.overall)}` },
      String(result.overall));
    const head = el("div", { class: "score-head" }, ring,
      el("div", {}, el("div", { class: "grade" }, `Grade ${result.grade}`),
        el("div", { class: "muted small" }, `${state.mode === "memory" ? "Memory" : "Trace"} mode · overall score`)));

    const metrics = el("div");
    const order = ["accuracy", "coverage", "smoothness", "confidence", "pressure", "direction"];
    for (const key of order) {
      const m = result.metrics[key];
      if (!m) continue;
      const scoreText = m.score == null ? "n/a" : `${m.score}`;
      const bar = el("div", { class: "bar" },
        el("span", { style: `width:${m.score ?? 0}%;background:${m.score == null ? "transparent" : scoreColor(m.score)}` }));
      metrics.append(el("div", { class: "metric" },
        el("div", { class: "metric-top" }, el("span", {}, m.label), el("span", {}, scoreText)),
        bar,
        el("div", { class: "metric-detail" }, m.detail)));
    }

    const parts = [head, metrics];
    if (result.notes.length) {
      const ul = el("ul");
      result.notes.forEach((n) => ul.append(el("li", {}, n)));
      parts.push(el("div", { class: "notes" }, ul));
    }
    parts.push(el("div", { class: "coach", id: "coach" },
      el("h2", {}, "Coach"), el("p", { class: "spinner" }, "Looking at your strokes…")));
    els.results.replaceChildren(...parts);
  }

  async function requestCoaching(result) {
    const exId = state.current.id;
    let fb;
    try {
      const { heatmap, ...lean } = result;
      const res = await fetch("/api/coach", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exercise_id: exId, result: lean, image: snapshot(), mode: state.mode }),
      });
      fb = await res.json();
    } catch {
      fb = null;
    }
    const box = document.getElementById("coach");
    if (!box || state.current.id !== exId || state.result !== result) return;  // user moved on
    if (!fb || fb.error) {
      box.replaceChildren(el("h2", {}, "Coach"), el("p", { class: "muted" }, "Coach feedback unavailable right now."));
      return;
    }
    const badge = el("span", { class: "badge" }, fb.source === "claude" ? "AI coach" : "Offline tips");
    const nodes = [el("h2", {}, "Coach", badge), el("p", {}, fb.summary)];
    if (fb.strengths?.length) {
      const ul = el("ul");
      fb.strengths.forEach((s) => ul.append(el("li", {}, s)));
      nodes.push(el("h3", {}, "Keep doing"), ul);
    }
    if (fb.fixes?.length) {
      nodes.push(el("h3", {}, "Work on"));
      for (const f of fb.fixes) {
        nodes.push(el("div", { class: "fix" },
          el("strong", {}, f.issue), el("div", { class: "muted small" }, f.why_it_matters),
          el("div", { class: "drill" }, `Drill: ${f.drill}`)));
      }
    }
    if (fb.style_note) nodes.push(el("h3", {}, "Style note"), el("p", {}, fb.style_note));
    if (fb.next_step) nodes.push(el("h3", {}, "Next"), el("p", {}, fb.next_step));
    box.replaceChildren(...nodes);
  }

  function showEmptyResults() {
    els.results.replaceChildren(el("div", { class: "empty muted" },
      el("p", {}, state.mode === "memory"
        ? "Memorize the guide, then draw it from memory and press Check my lines."
        : "Trace over the blue guide, then press Check my lines."),
      el("p", { class: "small" }, "A stylus with pressure unlocks line-weight scoring.")));
  }

  function showMessage(msg) {
    els.results.replaceChildren(el("div", { class: "empty" }, el("p", {}, msg)));
  }

  // ------------------------------------------------------------------ controls
  document.getElementById("undo").addEventListener("click", () => {
    state.strokes.pop();
    if (state.result) clearResult();
    render();
  });
  document.getElementById("clear").addEventListener("click", resetAttempt);
  els.submit.addEventListener("click", submit);
  els.showHeat.addEventListener("change", render);
  document.querySelectorAll(".mode-btn").forEach((b) => b.addEventListener("click", () => {
    state.mode = b.dataset.mode;
    document.querySelectorAll(".mode-btn").forEach((x) => {
      x.classList.toggle("active", x === b);
      x.setAttribute("aria-checked", String(x === b));
    });
    resetAttempt();
  }));
  window.addEventListener("resize", resizeCanvas);

  // ------------------------------------------------------------------ boot
  (async () => {
    resizeCanvas();
    const res = await fetch("/api/exercises");
    state.exercises = await res.json();
    selectExercise(store.get("animastery.last", null) || state.exercises[0].id);
  })();
})();
