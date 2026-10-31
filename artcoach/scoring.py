"""Stroke accuracy analysis.

Compares a user's drawn strokes against an exercise's guide strokes and breaks
the result down into the skills an art teacher would look at:

- accuracy    how far the line strays from the guide
- coverage    how much of the guide was actually drawn
- smoothness  wobble / jitter in the line (beyond the guide's own curvature)
- confidence  stroke economy (one clean stroke vs. sketchy feathering) and hesitation
- pressure    line-weight control (tapering or evenness), when a pen reports pressure
- direction   whether strokes were pulled the intended way (e.g. hair root -> tip)

All coordinates are in the shared logical canvas space (CANVAS_W x CANVAS_H).
Attempt points are [x, y, t_ms, pressure].
"""

from __future__ import annotations

import math
from collections import defaultdict

CANVAS_W, CANVAS_H = 800, 600

GUIDE_SPACING = 3.0     # px between resampled guide points
ATTEMPT_SPACING = 4.0   # px between resampled attempt points
SMOOTH_WINDOW = 7       # samples in the moving average used to measure wobble
PAUSE_SPEED = 0.05      # px/ms (50 px/s); slower than this counts as hesitation

WEIGHTS = {
    "accuracy": 0.35,
    "coverage": 0.20,
    "smoothness": 0.20,
    "confidence": 0.15,
    "pressure": 0.10,
    "direction": 0.10,
}

SECTION_NAMES = ("start", "middle", "end")


# --------------------------------------------------------------------------- geometry

def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _point_segment(p, a, b):
    """Distance from p to segment ab, and the projection parameter t in [0, 1]."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    seg2 = dx * dx + dy * dy
    if seg2 == 0:
        return math.hypot(p[0] - a[0], p[1] - a[1]), 0.0
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / seg2
    t = max(0.0, min(1.0, t))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy)), t


def resample(points, spacing):
    """Resample a polyline to evenly spaced (x, y) points."""
    pts = [(float(p[0]), float(p[1])) for p in points]
    if len(pts) < 2:
        return pts
    out = [pts[0]]
    prev = pts[0]
    carry = 0.0
    for cur in pts[1:]:
        seg = _dist(prev, cur)
        while seg > 0 and carry + seg >= spacing:
            t = (spacing - carry) / seg
            nxt = (prev[0] + t * (cur[0] - prev[0]), prev[1] + t * (cur[1] - prev[1]))
            out.append(nxt)
            prev, carry = nxt, 0.0
            seg = _dist(prev, cur)
        carry += seg
        prev = cur
    if _dist(out[-1], pts[-1]) > spacing * 0.25:
        out.append(pts[-1])
    return out


def polyline_length(points):
    return sum(_dist(points[i], points[i + 1]) for i in range(len(points) - 1))


def _wobble(samples):
    """Mean distance between each sample and a moving average of its neighbours."""
    half = SMOOTH_WINDOW // 2
    if len(samples) < SMOOTH_WINDOW:
        return None
    total, n = 0.0, 0
    for i in range(half, len(samples) - half):
        window = samples[i - half:i + half + 1]
        mx = sum(p[0] for p in window) / len(window)
        my = sum(p[1] for p in window) / len(window)
        total += math.hypot(samples[i][0] - mx, samples[i][1] - my)
        n += 1
    return total / n if n else None


class _Guide:
    """Pre-resampled guide strokes with cumulative arc length, for nearest-point queries."""

    def __init__(self, strokes):
        self.strokes = []
        for stroke in strokes:
            pts = resample(stroke, GUIDE_SPACING)
            cum = [0.0]
            for i in range(1, len(pts)):
                cum.append(cum[-1] + _dist(pts[i - 1], pts[i]))
            self.strokes.append((pts, cum))

    def nearest(self, p):
        """Return (distance, stroke_index, fraction_along_stroke)."""
        best = (float("inf"), -1, 0.0)
        for si, (pts, cum) in enumerate(self.strokes):
            total = cum[-1] or 1.0
            if len(pts) == 1:
                d = _dist(p, pts[0])
                if d < best[0]:
                    best = (d, si, 0.0)
                continue
            for i in range(len(pts) - 1):
                d, t = _point_segment(p, pts[i], pts[i + 1])
                if d < best[0]:
                    s = cum[i] + t * (cum[i + 1] - cum[i])
                    best = (d, si, s / total)
        return best


class _Grid:
    """Spatial hash of points for 'is anything within r of p' queries."""

    def __init__(self, points, cell):
        self.cell = cell
        self.buckets = defaultdict(list)
        for p in points:
            self.buckets[(int(p[0] // cell), int(p[1] // cell))].append(p)

    def any_within(self, p, r):
        cx, cy = int(p[0] // self.cell), int(p[1] // self.cell)
        for gx in (cx - 1, cx, cx + 1):
            for gy in (cy - 1, cy, cy + 1):
                for q in self.buckets.get((gx, gy), ()):
                    if _dist(p, q) <= r:
                        return True
        return False


def _clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))


def _section(frac):
    return SECTION_NAMES[min(2, int(frac * 3))]


# --------------------------------------------------------------------------- analysis

def analyze(guide_strokes, attempt_strokes, *, pressure_profile=None,
            directional=False, tolerance=10.0):
    """Score an attempt against a guide. Returns a JSON-serialisable dict."""
    attempts = [s for s in attempt_strokes if len(s) >= 2]
    if not attempts:
        return {"ok": False, "error": "Draw at least one stroke before submitting."}

    guide = _Guide(guide_strokes)
    metrics = {}
    notes = []

    # ---- accuracy: deviation of every attempt sample from the nearest guide line
    samples = []        # (x, y, dev, guide_stroke, frac) per resampled attempt point
    per_stroke = []     # resampled points of each attempt stroke
    for stroke in attempts:
        pts = resample(stroke, ATTEMPT_SPACING)
        per_stroke.append(pts)
        for p in pts:
            d, si, frac = guide.nearest(p)
            samples.append((p[0], p[1], d, si, frac))

    devs = sorted(s[2] for s in samples)
    mean_dev = sum(devs) / len(devs)
    p90_dev = devs[min(len(devs) - 1, int(len(devs) * 0.9))]
    within = sum(1 for d in devs if d <= tolerance) / len(devs)
    metrics["accuracy"] = {
        "score": round(_clamp(100 * math.exp(-mean_dev / 15.0))),
        "mean_deviation_px": round(mean_dev, 1),
        "p90_deviation_px": round(p90_dev, 1),
        "on_line_pct": round(100 * within),
        "label": "Accuracy",
        "detail": f"Average {mean_dev:.1f}px off the guide; {round(100 * within)}% of your line "
                  f"is within {tolerance:.0f}px.",
    }

    # ---- coverage: fraction of guide drawn over
    grid = _Grid([(s[0], s[1]) for s in samples], cell=max(tolerance, 1.0))
    covered = total = 0
    missed_sections = defaultdict(int)
    section_totals = defaultdict(int)
    for si, (pts, cum) in enumerate(guide.strokes):
        length = cum[-1] or 1.0
        for p, c in zip(pts, cum):
            key = (si, _section(c / length))
            section_totals[key] += 1
            total += 1
            if grid.any_within(p, tolerance * 1.5):
                covered += 1
            else:
                missed_sections[key] += 1
    coverage = covered / total if total else 0.0
    metrics["coverage"] = {
        "score": round(100 * coverage),
        "covered_pct": round(100 * coverage),
        "label": "Coverage",
        "detail": f"You drew over {round(100 * coverage)}% of the guide.",
    }
    for (si, sec), miss in sorted(missed_sections.items()):
        if miss / section_totals[(si, sec)] > 0.6:
            notes.append(f"The {sec} of guide line {si + 1} was mostly skipped.")

    # ---- smoothness: wobble beyond the guide's own curvature
    # Measure the guide at the same spacing as the attempt so curvature cancels out.
    guide_wobbles = [w for w in (_wobble(resample(s, ATTEMPT_SPACING)) for s in guide_strokes)
                     if w is not None]
    baseline = sum(guide_wobbles) / len(guide_wobbles) if guide_wobbles else 0.0
    wobbles = [w for w in (_wobble(pts) for pts in per_stroke) if w is not None]
    if wobbles:
        excess = max(0.0, sum(wobbles) / len(wobbles) - baseline)
        metrics["smoothness"] = {
            "score": round(_clamp(100 * math.exp(-excess / 1.2))),
            "wobble_px": round(excess, 2),
            "label": "Smoothness",
            "detail": f"Line wobble of about {excess:.2f}px beyond the guide's natural curve.",
        }
    else:
        metrics["smoothness"] = {
            "score": None, "label": "Smoothness",
            "detail": "Strokes too short to judge smoothness.",
        }

    # ---- confidence: stroke economy + hesitation
    n_guide = len(guide_strokes)
    short = sum(1 for pts in per_stroke if polyline_length(pts) < 20)
    extra = max(0, len(attempts) - n_guide)
    economy = 100 * math.exp(-0.8 * extra / max(1, n_guide))
    pause_ms = draw_ms = 0.0
    dist_px = 0.0
    has_time = any(len(p) > 2 and p[2] for s in attempts for p in s)
    if has_time:
        for stroke in attempts:
            for a, b in zip(stroke, stroke[1:]):
                dt = float(b[2]) - float(a[2])
                if dt <= 0:
                    continue
                d = _dist(a, b)
                draw_ms += dt
                dist_px += d
                if d / dt < PAUSE_SPEED:
                    pause_ms += dt
    if draw_ms > 0:
        hesitation = 100 * (1 - pause_ms / draw_ms)
        confidence = 0.5 * economy + 0.5 * hesitation
        speed = 1000 * dist_px / draw_ms
        detail = (f"{len(attempts)} stroke(s) for {n_guide} guide line(s); "
                  f"{round(100 * pause_ms / draw_ms)}% of drawing time spent hesitating; "
                  f"average speed {speed:.0f}px/s.")
    else:
        hesitation, speed = None, None
        confidence = economy
        detail = f"{len(attempts)} stroke(s) for {n_guide} guide line(s)."
    metrics["confidence"] = {
        "score": round(_clamp(confidence)),
        "strokes_used": len(attempts),
        "guide_strokes": n_guide,
        "short_strokes": short,
        "hesitation_score": None if hesitation is None else round(hesitation),
        "avg_speed_px_s": None if speed is None else round(speed),
        "label": "Confidence",
        "detail": detail,
    }
    if short >= 2:
        notes.append(f"{short} very short strokes - that's feathering/sketchy lines. "
                     "Try one committed pull per line.")

    # ---- pressure / line weight
    pressures = [float(p[3]) for s in attempts for p in s if len(p) > 3]
    has_pressure = len(pressures) > 4 and (max(pressures) - min(pressures)) > 0.05
    if not has_pressure:
        metrics["pressure"] = {
            "score": None, "label": "Line weight",
            "detail": "No pen pressure detected (mouse or finger). Use a stylus to train line weight.",
        }
    elif pressure_profile == "taper":
        scores = []
        for stroke in attempts:
            ps = [float(p[3]) for p in stroke if len(p) > 3]
            if len(ps) < 6:
                continue
            k = len(ps) // 3
            ends = (sum(ps[:k]) / k + sum(ps[-k:]) / k) / 2
            mid = sum(ps[k:-k]) / max(1, len(ps) - 2 * k)
            ratio = mid / max(ends, 1e-3)
            scores.append(_clamp((ratio - 1.0) / 0.4 * 100))
        score = sum(scores) / len(scores) if scores else None
        metrics["pressure"] = {
            "score": None if score is None else round(score),
            "label": "Line weight",
            "detail": "Tapered lines should start light, swell in the middle and lift off light."
                      + ("" if score is None else f" Taper quality: {round(score)}/100."),
        }
    else:
        mean_p = sum(pressures) / len(pressures)
        std_p = math.sqrt(sum((p - mean_p) ** 2 for p in pressures) / len(pressures))
        cv = std_p / max(mean_p, 1e-3)
        metrics["pressure"] = {
            "score": round(_clamp(100 * math.exp(-cv / 0.3))),
            "variation_pct": round(100 * cv),
            "label": "Line weight",
            "detail": f"Pressure varied by about {round(100 * cv)}% - aim for an even line here.",
        }

    # ---- direction
    if directional:
        right = counted = 0
        for pts in per_stroke:
            if polyline_length(pts) < 15:
                continue
            _, s0, f0 = guide.nearest(pts[0])
            _, s1, f1 = guide.nearest(pts[-1])
            if s0 != s1 or abs(f1 - f0) < 0.1:
                continue
            counted += 1
            right += f1 > f0
        if counted:
            metrics["direction"] = {
                "score": round(100 * right / counted),
                "label": "Direction",
                "detail": f"{right} of {counted} strokes pulled in the intended direction.",
            }
            if right < counted:
                notes.append("Some strokes went the wrong way. Pull from the start dot toward the arrow.")

    # ---- where the error concentrates
    region = defaultdict(list)
    for x, y, d, si, frac in samples:
        region[(si, _section(frac))].append(d)
    worst = None
    for key, ds in region.items():
        if len(ds) >= 5:
            m = sum(ds) / len(ds)
            if worst is None or m > worst[1]:
                worst = (key, m)
    if worst and worst[1] > tolerance * 0.8:
        (si, sec), m = worst
        notes.append(f"Most drift is in the {sec} of guide line {si + 1} (about {m:.0f}px off).")

    # ---- overall
    num = den = 0.0
    for name, w in WEIGHTS.items():
        m = metrics.get(name)
        if m and m.get("score") is not None:
            num += w * m["score"]
            den += w
    overall = round(num / den) if den else 0

    return {
        "ok": True,
        "overall": overall,
        "grade": _grade(overall),
        "metrics": metrics,
        "notes": notes,
        "heatmap": [[round(x, 1), round(y, 1), round(d, 1)] for x, y, d, _, _ in samples],
        "tolerance": tolerance,
    }


def _grade(score):
    for cutoff, letter in ((90, "S"), (80, "A"), (65, "B"), (50, "C")):
        if score >= cutoff:
            return letter
    return "D"
