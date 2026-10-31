"""Animastery Art Coach - web server.

Run:  python -m artcoach.app   then open http://localhost:5000
"""

from __future__ import annotations

import os

from flask import Flask, jsonify, request, send_from_directory

from . import coach, exercises, scoring, styles

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
MAX_POINTS = 20000

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


def resolve_exercise(exercise_id):
    """Built-in exercise, or an uploaded style reference ("style:<id>")."""
    if isinstance(exercise_id, str) and exercise_id.startswith("style:"):
        meta = styles.load(exercise_id.split(":", 1)[1])
        return styles.as_exercise(meta) if meta else None
    return exercises.get_exercise(exercise_id)


@app.get("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.get("/api/exercises")
def list_exercises():
    return jsonify(exercises.public_list())


# --------------------------------------------------------------------------- style references

@app.get("/api/styles")
def list_styles():
    return jsonify([styles.as_exercise(m) for m in styles.list_all()])


@app.post("/api/styles")
def upload_style():
    f = request.files.get("image")
    if not f:
        return jsonify({"error": "Choose an image to upload."}), 400
    if request.form.get("study_ack") != "yes":
        return jsonify({"error": "Please confirm the reference is for personal study."}), 400
    try:
        meta = styles.create(f.read(styles.MAX_UPLOAD_BYTES + 1), request.form.get("name"),
                             request.form.get("artist"), request.form.get("source"))
    except styles.StyleError as exc:
        return jsonify({"error": str(exc)}), 400
    _analyze(meta)
    return jsonify(styles.as_exercise(meta))


def _analyze(meta):
    profile, source = coach.analyze_style(styles.image_bytes(meta["id"]), meta["name"],
                                          meta.get("artist"), exercises.EXERCISES)
    meta["profile"], meta["profile_source"] = profile, source
    styles.save(meta)


@app.post("/api/styles/<style_id>/analyze")
def reanalyze_style(style_id):
    meta = styles.load(style_id)
    if not meta:
        return jsonify({"error": "Unknown style."}), 404
    _analyze(meta)
    return jsonify(styles.as_exercise(meta))


@app.get("/api/styles/<style_id>/image")
def style_image(style_id):
    try:
        path = styles.image_path(style_id)
    except styles.StyleError:
        return jsonify({"error": "Unknown style."}), 404
    if not path.exists():
        return jsonify({"error": "Unknown style."}), 404
    return send_from_directory(path.parent, path.name, mimetype="image/png")


@app.delete("/api/styles/<style_id>")
def delete_style(style_id):
    try:
        ok = styles.delete(style_id)
    except styles.StyleError:
        ok = False
    return (jsonify({"ok": True}), 200) if ok else (jsonify({"error": "Unknown style."}), 404)


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
    ex = resolve_exercise(body.get("exercise_id"))
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
    ex = resolve_exercise(body.get("exercise_id"))
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
