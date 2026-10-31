"""User-uploaded style references.

A style is a reference image (art in a style the user wants to learn) plus
attribution and, when AI is available, a style profile describing how to draw
in that style. The reference's line art is auto-traced into guide strokes so it
can be practised with the same scoring as the built-in exercises.

Everything is stored locally under data/styles/<id>/ (not committed to git).
"""

from __future__ import annotations

import io
import json
import math
import os
import re
import secrets
import shutil
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

from .scoring import CANVAS_H, CANVAS_W

DATA_DIR = Path(os.environ.get("ARTCOACH_DATA", Path(__file__).resolve().parent.parent / "data"))
STYLES_DIR = DATA_DIR / "styles"
ID_RE = re.compile(r"^[0-9a-f]{12}$")
MAX_UPLOAD_BYTES = 8 * 1024 * 1024
MAX_STROKES = 80
MIN_STROKE_PX = 18

Image.MAX_IMAGE_PIXELS = 40_000_000   # refuse decompression bombs


class StyleError(ValueError):
    pass


# --------------------------------------------------------------------------- image prep

def normalize_image(data: bytes) -> Image.Image:
    """Decode an upload and letterbox it onto a white 800x600 canvas."""
    if len(data) > MAX_UPLOAD_BYTES:
        raise StyleError("Image is too large (max 8 MB).")
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except Exception as exc:
        raise StyleError("That file isn't an image I can read (use PNG, JPG or WebP).") from exc
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, img)
    img = img.convert("RGB")
    scale = min(CANVAS_W / img.width, CANVAS_H / img.height)
    size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
    img = img.resize(size, Image.LANCZOS)
    out = Image.new("RGB", (CANVAS_W, CANVAS_H), "white")
    out.paste(img, ((CANVAS_W - size[0]) // 2, (CANVAS_H - size[1]) // 2))
    return out


# --------------------------------------------------------------------------- line extraction

def _line_mask(img: Image.Image) -> np.ndarray:
    """Pixels noticeably darker than their surroundings: ink lines and fill edges."""
    gray = img.convert("L")
    g = np.asarray(gray, dtype=np.float32)
    local = np.asarray(gray.filter(ImageFilter.BoxBlur(5)), dtype=np.float32)
    contrast = local - g
    # Adapt the threshold to the image: keep roughly the strongest line pixels.
    thresh = max(14.0, float(np.percentile(contrast, 93)))
    return contrast > thresh


def _thin(mask: np.ndarray) -> np.ndarray:
    """Zhang-Suen skeletonisation: reduce lines to 1px-wide centrelines."""
    img = np.pad(mask.astype(np.uint8), 1)
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            c = img[1:-1, 1:-1]
            p2, p3, p4 = img[:-2, 1:-1], img[:-2, 2:], img[1:-1, 2:]
            p5, p6, p7 = img[2:, 2:], img[2:, 1:-1], img[2:, :-2]
            p8, p9 = img[1:-1, :-2], img[:-2, :-2]
            ring = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
            b = sum(p.astype(np.int16) for p in ring[:8])
            a = sum(((ring[i] == 0) & (ring[i + 1] == 1)).astype(np.int16) for i in range(8))
            if step == 0:
                m = ((p2 & p4 & p6) == 0) & ((p4 & p6 & p8) == 0)
            else:
                m = ((p2 & p4 & p8) == 0) & ((p2 & p6 & p8) == 0)
            remove = (c == 1) & (b >= 2) & (b <= 6) & (a == 1) & m
            if remove.any():
                c[remove] = 0
                changed = True
    return img[1:-1, 1:-1].astype(bool)


_OFFSETS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def _trace(skel: np.ndarray):
    """Walk the skeleton into polylines, following the straightest continuation."""
    ys, xs = np.nonzero(skel)
    pixels = set(zip(xs.tolist(), ys.tolist()))
    unvisited = set(pixels)

    def neighbours(p, pool):
        x, y = p
        return [(x + dx, y + dy) for dx, dy in _OFFSETS if (x + dx, y + dy) in pool]

    def walk(start):
        path = [start]
        unvisited.discard(start)
        direction = None
        cur = start
        while True:
            cands = neighbours(cur, unvisited)
            if not cands:
                return path
            if direction is None:
                nxt = cands[0]
            else:
                nxt = max(cands, key=lambda q: ((q[0] - cur[0]) * direction[0] + (q[1] - cur[1]) * direction[1])
                          / math.hypot(q[0] - cur[0], q[1] - cur[1]))
            # Swallow staircase pixels that touch both cur and nxt so they don't spawn fragments.
            for q in cands:
                if q != nxt and max(abs(q[0] - nxt[0]), abs(q[1] - nxt[1])) <= 1:
                    unvisited.discard(q)
            unvisited.discard(nxt)
            path.append(nxt)
            back = path[-4] if len(path) >= 4 else path[0]
            dx, dy = nxt[0] - back[0], nxt[1] - back[1]
            norm = math.hypot(dx, dy) or 1.0
            direction = (dx / norm, dy / norm)
            cur = nxt

    paths = []
    endpoints = sorted(p for p in pixels if len(neighbours(p, pixels)) == 1)
    for p in endpoints:
        if p in unvisited:
            paths.append(walk(p))
    for p in sorted(pixels):            # branches whose ends were consumed, then closed loops
        if p in unvisited and len(neighbours(p, unvisited)) <= 1:
            paths.append(walk(p))
    for p in sorted(pixels):
        if p in unvisited:
            paths.append(walk(p))
    return paths


def _smooth(path, window=5):
    if len(path) < window:
        return [list(map(float, p)) for p in path]
    half = window // 2
    out = [list(map(float, path[0]))]
    for i in range(1, len(path) - 1):
        lo, hi = max(0, i - half), min(len(path), i + half + 1)
        seg = path[lo:hi]
        out.append([sum(p[0] for p in seg) / len(seg), sum(p[1] for p in seg) / len(seg)])
    out.append(list(map(float, path[-1])))
    return out


def _simplify(points, eps=0.8):
    """Ramer-Douglas-Peucker."""
    if len(points) < 3:
        return points
    a, b = points[0], points[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    norm = math.hypot(dx, dy)
    best_i, best_d = 0, -1.0
    for i in range(1, len(points) - 1):
        p = points[i]
        if norm == 0:
            d = math.hypot(p[0] - a[0], p[1] - a[1])
        else:
            d = abs(dy * p[0] - dx * p[1] + b[0] * a[1] - b[1] * a[0]) / norm
        if d > best_d:
            best_i, best_d = i, d
    if best_d <= eps:
        return [a, b]
    left = _simplify(points[:best_i + 1], eps)
    return left[:-1] + _simplify(points[best_i:], eps)


def _length(points):
    return sum(math.hypot(points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1])
               for i in range(len(points) - 1))


def _merge(strokes, gap=4.0):
    """Join fragments whose ends nearly touch and continue in the same direction."""
    def end_dir(s, at_end):
        a, b = (s[-1], s[max(0, len(s) - 4)]) if at_end else (s[0], s[min(len(s) - 1, 3)])
        dx, dy = a[0] - b[0], a[1] - b[1]
        n = math.hypot(dx, dy) or 1.0
        return dx / n, dy / n

    merged = True
    while merged:
        merged = False
        for i in range(len(strokes)):
            for j in range(len(strokes)):
                if i == j:
                    continue
                s, t = strokes[i], strokes[j]
                for t_oriented in (t, t[::-1]):
                    if math.hypot(s[-1][0] - t_oriented[0][0], s[-1][1] - t_oriented[0][1]) > gap:
                        continue
                    d1 = end_dir(s, True)
                    d2 = end_dir(t_oriented, False)
                    if d1[0] * -d2[0] + d1[1] * -d2[1] > 0.5:   # outward directions roughly opposite
                        strokes[i] = s + t_oriented[1:]
                        del strokes[j]
                        merged = True
                        break
                if merged:
                    break
            if merged:
                break
    return strokes


def extract_strokes(img: Image.Image):
    """Auto-trace the reference's line art into guide strokes (800x600 space)."""
    skel = _thin(_line_mask(img))
    strokes = [_simplify(_smooth(p)) for p in _trace(skel) if len(p) >= 4]
    strokes = [s for s in strokes if _length(s) >= MIN_STROKE_PX / 2]
    strokes = _merge(strokes)
    strokes = [s for s in strokes if _length(s) >= MIN_STROKE_PX]
    strokes.sort(key=_length, reverse=True)
    return [[[round(x, 1), round(y, 1)] for x, y in s] for s in strokes[:MAX_STROKES]]


# --------------------------------------------------------------------------- storage

def _dir(style_id: str) -> Path:
    if not ID_RE.match(style_id or ""):
        raise StyleError("Unknown style.")
    return STYLES_DIR / style_id


def _clean(text, limit):
    return re.sub(r"\s+", " ", str(text or "")).strip()[:limit]


def create(data: bytes, name: str, artist: str, source: str) -> dict:
    img = normalize_image(data)
    strokes = extract_strokes(img)
    if not strokes:
        raise StyleError("I couldn't find clear lines in that image. Line art or sketches work best.")
    style_id = secrets.token_hex(6)
    d = STYLES_DIR / style_id
    d.mkdir(parents=True, exist_ok=False)
    img.save(d / "reference.png", optimize=True)
    meta = {
        "id": style_id,
        "name": _clean(name, 80) or "Untitled style",
        "artist": _clean(artist, 80),
        "source": _clean(source, 300),
        "created": int(time.time()),
        "strokes": strokes,
        "profile": None,
        "profile_source": None,
    }
    save(meta)
    return meta


def save(meta: dict) -> None:
    d = _dir(meta["id"])
    tmp = d / "meta.json.tmp"
    tmp.write_text(json.dumps(meta), encoding="utf-8")
    tmp.replace(d / "meta.json")


def load(style_id: str):
    try:
        return json.loads((_dir(style_id) / "meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, StyleError):
        return None


def image_path(style_id: str) -> Path:
    return _dir(style_id) / "reference.png"


def image_bytes(style_id: str) -> bytes:
    return image_path(style_id).read_bytes()


def delete(style_id: str) -> bool:
    d = _dir(style_id)
    if not d.exists():
        return False
    shutil.rmtree(d)
    return True


def list_all():
    if not STYLES_DIR.exists():
        return []
    out = []
    for d in STYLES_DIR.iterdir():
        meta = load(d.name) if ID_RE.match(d.name) else None
        if meta:
            out.append(meta)
    out.sort(key=lambda m: m["created"], reverse=True)
    return out


# --------------------------------------------------------------------------- as exercises

def exercise_id(style_id: str) -> str:
    return f"style:{style_id}"


def as_exercise(meta: dict) -> dict:
    """Present a style reference as a practice exercise."""
    profile = meta.get("profile") or {}
    tips = [f"{f['feature']}: {f['how_to_draw']}" for f in profile.get("signature_features", [])][:4]
    if not tips:
        tips = [
            "Trace slowly the first time to learn where the lines go, then trace again at a confident speed.",
            "Notice where the artist's lines are thick and where they thin out.",
            "Switch to Memory mode once you can trace it cleanly.",
        ]
    by = f" by {meta['artist']}" if meta.get("artist") else ""
    return {
        "id": exercise_id(meta["id"]),
        "style_id": meta["id"],
        "name": meta["name"],
        "style": "Your styles",
        "level": 3,
        "description": (profile.get("style_summary")
                        or f"Study the line work of this reference{by} by tracing it, then drawing it from memory."),
        "tips": tips,
        "pressure_profile": "taper",
        "directional": False,
        "strokes": meta["strokes"],
        "reference_image": f"/api/styles/{meta['id']}/image",
        "artist": meta.get("artist", ""),
        "source": meta.get("source", ""),
        "profile": meta.get("profile"),
        "profile_source": meta.get("profile_source"),
    }
