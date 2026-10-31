"""Animastery Art Coach - web server.

Run:  python -m artcoach.app   then open http://localhost:5000
"""

from __future__ import annotations

import os

from flask import Flask, jsonify, request, send_from_directory

from . import coach, exercises, scoring

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
MAX_POINTS = 20000

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024


@app.get("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.get("/api/exercises")
def list_exercises():
    return jsonify(exercises.public_list())


def _parse_strokes(raw):
    strokes, total = [], 0
    for s in raw or []:
        pts = []
        for p in s:
            x, y = float(p[0]), float(p[1])
            t = float(p[2]) if len(p) > 2 else 0.0
            pr = float(p[3]) if len(p) > 3 else 0.5
            pts.append([x, y, t, pr])
        total += len(pts)
        strokes.append(pts)
    if total > MAX_POINTS:
        raise ValueError("Too many points.")
    return strokes


@app.post("/api/score")
def score():
    body = request.get_json(silent=True) or {}
    ex = exercises.get_exercise(body.get("exercise_id"))
    if not ex:
        return jsonify({"ok": False, "error": "Unknown exercise."}), 404
    try:
        strokes = _parse_strokes(body.get("strokes"))
    except (TypeError, ValueError, IndexError):
        return jsonify({"ok": False, "error": "Malformed stroke data."}), 400
    result = scoring.analyze(
        ex["strokes"], strokes,
        pressure_profile=ex.get("pressure_profile"),
        directional=ex.get("directional", False),
    )
    return jsonify(result)


@app.post("/api/coach")
def coach_feedback():
    body = request.get_json(silent=True) or {}
    ex = exercises.get_exercise(body.get("exercise_id"))
    result = body.get("result")
    if not ex or not isinstance(result, dict):
        return jsonify({"error": "Missing exercise or result."}), 400
    fb = coach.get_feedback(ex, result, body.get("image"), body.get("mode", "trace"))
    return jsonify(fb)


def main():
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=port, debug=False)


if __name__ == "__main__":
    main()
