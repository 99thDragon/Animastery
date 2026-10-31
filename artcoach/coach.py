"""AI coaching feedback.

Sends Claude a snapshot of the attempt (guide + user's lines) together with the
measured stroke metrics, and asks for structured, teacher-style feedback.
If the API isn't configured or the call fails, falls back to rule-based tips
built from the same metrics, so the app always works offline.
"""

from __future__ import annotations

import base64
import json
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)

MODEL = os.environ.get("ARTCOACH_MODEL", "claude-opus-5-5")
STYLE_NOTES_PATH = Path(__file__).resolve().parent.parent / "love_live_style_notes.txt"

FEEDBACK_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "fixes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "issue": {"type": "string"},
                    "why_it_matters": {"type": "string"},
                    "drill": {"type": "string"},
                },
                "required": ["issue", "why_it_matters", "drill"],
                "additionalProperties": False,
            },
        },
        "style_note": {"type": "string"},
        "next_step": {"type": "string"},
    },
    "required": ["summary", "strengths", "fixes", "style_note", "next_step"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = """You are a patient, specific drawing coach helping a student learn line work and \
art styles through guided tracing and memory-drawing exercises.

You get a snapshot of the student's attempt: the faint guide lines and the student's strokes \
(colored green-to-red by how far each part strayed from the guide). You also get measured metrics \
from a stroke analyzer. Treat the metrics as ground truth for numbers. Use the image to see *what* \
the error looks like: overshooting the ends, flattening a curve, wobbling at a specific spot, \
sketchy re-strokes, and so on.

Coach like a good art teacher:
- Name the 1-3 most important problems, in priority order. Don't list everything.
- Tie each problem to a concrete physical cause (wrist vs. shoulder, speed, hesitation, \
  ghosting, pressure) and give one short drill to fix it.
- Point out real strengths so the student knows what to keep doing.
- When the exercise belongs to a specific style, relate the advice to that style's conventions.
- Be warm but direct. Plain language, no filler, and keep each field to a sentence or two."""


def _style_notes():
    try:
        return STYLE_NOTES_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""


def _call_claude(system, content, schema):
    """One structured-output request to Claude. Returns the parsed dict, or None if declined."""
    import anthropic

    client = anthropic.Anthropic()
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=system,
        messages=[{"role": "user", "content": content}],
        output_config={
            "effort": "medium",
            "format": {"type": "json_schema", "schema": schema},
        },
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        log.warning("Claude declined the request: %s", response.stop_details)
        return None
    text = next((b.text for b in response.content if b.type == "text"), None)
    return json.loads(text) if text else None


def _png_block(data_b64):
    return {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": data_b64}}


# --------------------------------------------------------------------------- style analysis

STYLE_SYSTEM_PROMPT = """You are an art teacher who helps students learn an art style by studying a \
reference, the way art students do master studies.

Analyze the visual style of the reference image: the technique and conventions, not the subject \
matter or story. Describe what is observable so a student can reproduce the *style* in their own \
original drawings: line quality and weight, how lines taper, shape language, proportions, how \
signature features (eyes, hair, hands, faces, folds, etc.) are constructed, and color/shading \
approach. Be concrete and visual ("upper lash line is a single heavy stroke that flicks out at the \
outer corner"), not vague ("expressive eyes").

Don't try to identify real people in the image. If the student named the artist, you can mention \
widely known characteristics of their style, but ground everything in what this image shows.

Then write a short, progressive lesson plan. Each step picks one exercise: one of the built-in \
exercise ids, "reference-trace" (trace this reference's lines) or "reference-memory" (draw this \
reference from memory). Order the steps from fundamentals to the full study."""


def style_schema(exercise_ids):
    return {
        "type": "object",
        "properties": {
            "style_summary": {"type": "string"},
            "line_work": {"type": "string"},
            "shape_language": {"type": "string"},
            "proportions": {"type": "string"},
            "signature_features": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"feature": {"type": "string"}, "how_to_draw": {"type": "string"}},
                    "required": ["feature", "how_to_draw"],
                    "additionalProperties": False,
                },
            },
            "color_and_shading": {"type": "string"},
            "common_mistakes": {"type": "array", "items": {"type": "string"}},
            "lesson_plan": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "exercise": {"type": "string",
                                     "enum": list(exercise_ids) + ["reference-trace", "reference-memory"]},
                        "focus": {"type": "string"},
                    },
                    "required": ["title", "exercise", "focus"],
                    "additionalProperties": False,
                },
            },
            "coaching_focus": {"type": "string"},
        },
        "required": ["style_summary", "line_work", "shape_language", "proportions",
                     "signature_features", "color_and_shading", "common_mistakes",
                     "lesson_plan", "coaching_focus"],
        "additionalProperties": False,
    }


def analyze_style(image_png: bytes, name, artist, builtin_exercises):
    """Ask Claude for a style profile + lesson plan. Returns (profile_or_None, source)."""
    if not _ai_enabled():
        return None, "disabled"
    catalog = "\n".join(f"- {e['id']}: {e['name']} ({e['style']}). {e['description']}"
                        for e in builtin_exercises)
    content = [
        _png_block(base64.b64encode(image_png).decode("ascii")),
        {"type": "text", "text": (
            f"Style reference name: {name}\n"
            f"Artist / creator (as given by the student): {artist or 'not given'}\n\n"
            f"Built-in exercises you can assign:\n{catalog}\n\n"
            "Analyze this style and build the lesson plan."
        )},
    ]
    try:
        profile = _call_claude(STYLE_SYSTEM_PROMPT, content,
                               style_schema([e["id"] for e in builtin_exercises]))
    except Exception as exc:
        log.warning("Style analysis unavailable: %s", exc)
        return None, "unavailable"
    return (profile, "claude") if profile else (None, "declined")


def _metrics_for_prompt(result):
    """Metrics without the bulky heatmap."""
    return {
        "overall": result.get("overall"),
        "grade": result.get("grade"),
        "metrics": result.get("metrics"),
        "analyzer_notes": result.get("notes"),
    }


def _ai_enabled():
    return os.environ.get("ARTCOACH_AI", "on").lower() not in ("0", "off", "false", "no")


def get_feedback(exercise, result, image_data_url=None, mode="trace"):
    """Return feedback dict with a `source` of "claude" or "local"."""
    if _ai_enabled():
        try:
            fb = _claude_feedback(exercise, result, image_data_url, mode)
            if fb:
                fb["source"] = "claude"
                return fb
        except Exception as exc:  # any failure -> offline feedback, never a broken page
            log.warning("AI feedback unavailable, using local feedback: %s", exc)
    fb = local_feedback(exercise, result)
    fb["source"] = "local"
    return fb


def _claude_feedback(exercise, result, image_data_url, mode):
    content = []
    if image_data_url and image_data_url.startswith("data:image/png;base64,"):
        data = image_data_url.split(",", 1)[1]
        base64.b64decode(data, validate=True)  # reject garbage before sending
        content.append(_png_block(data))

    style_block = ""
    if exercise.get("profile"):
        by = f" by {exercise['artist']}" if exercise.get("artist") else ""
        style_block = (f"\n\nThis is a study of an uploaded style reference{by}. The snapshot shows the "
                       "faded reference under the student's lines. Style profile (JSON):\n"
                       f"{json.dumps(exercise['profile'], indent=1)}")
    elif exercise.get("style_id"):
        style_block = ("\n\nThis is a study of an uploaded style reference (shown faded under the "
                       "student's lines). Judge how well the student captured its line work.")
    elif exercise.get("style") != "Fundamentals":
        style_block = f"\n\nStyle reference notes for this style:\n{_style_notes()}"

    content.append({
        "type": "text",
        "text": (
            f"Exercise: {exercise['name']} ({exercise['style']}, level {exercise['level']})\n"
            f"Goal: {exercise['description']}\n"
            f"Teaching points: {json.dumps(exercise['tips'])}\n"
            f"Mode: {'tracing over a visible guide' if mode == 'trace' else 'drawing from memory after the guide was hidden'}\n"
            f"Intended pressure: {exercise.get('pressure_profile') or 'any'}; "
            f"direction matters: {exercise.get('directional')}\n\n"
            f"Analyzer metrics (JSON):\n{json.dumps(_metrics_for_prompt(result), indent=1)}"
            f"{style_block}\n\n"
            "Give your coaching feedback."
        ),
    })
    return _call_claude(SYSTEM_PROMPT, content, FEEDBACK_SCHEMA)


# --------------------------------------------------------------------------- offline

_DRILLS = {
    "accuracy": (
        "Your line drifts off the guide.",
        "Accuracy is what lets your drawings match what you intend, like proportions and features lining up.",
        "Ghost the stroke 3 times above the paper, then draw it. Aim at the end point, not the pen tip.",
    ),
    "coverage": (
        "Parts of the guide were left undrawn or stopped short.",
        "Missing pieces break the silhouette and make forms read as unfinished.",
        "Before each stroke, find both end dots and commit to drawing all the way between them.",
    ),
    "smoothness": (
        "The line wobbles.",
        "Wobbly lines look hesitant. Clean line art depends on smooth, continuous curves.",
        "Draw 20 lines a little faster than feels comfortable, moving from the elbow or shoulder instead of the wrist.",
    ),
    "confidence": (
        "Lots of short, sketchy strokes and pauses.",
        "Feathered lines add visual noise and make line weight impossible to control.",
        "Use one stroke per line. If it's wrong, undo and redraw it instead of patching over it.",
    ),
    "pressure": (
        "Line weight isn't controlled.",
        "Line weight gives a drawing depth and that polished, inked anime look.",
        "Practise 'light-heavy-light' strokes: touch down softly, press through the middle, and lift off while still moving.",
    ),
    "direction": (
        "Some strokes are pulled the wrong way.",
        "Stroke direction controls where the taper lands. Hair should flick off at the tips, not the roots.",
        "Always start at the dot and finish toward the arrow, even if it feels awkward at first.",
    ),
}


def local_feedback(exercise, result):
    metrics = result.get("metrics", {})
    scored = [(k, m["score"]) for k, m in metrics.items() if m.get("score") is not None]
    scored.sort(key=lambda kv: kv[1])
    fixes = []
    for name, score in scored:
        if score < 75 and name in _DRILLS and len(fixes) < 3:
            issue, why, drill = _DRILLS[name]
            fixes.append({"issue": issue, "why_it_matters": why, "drill": drill})
    strengths = [f"{metrics[name]['label']} is solid ({score}/100)."
                 for name, score in reversed(scored) if score >= 80][:2]
    overall = result.get("overall", 0)
    if overall >= 85:
        summary = "Clean attempt. Try memory mode next, or move up a level."
    elif overall >= 65:
        summary = "Good foundation. Tighten up the weakest area below and repeat this exercise."
    else:
        summary = "Keep at it. Slow, careful reps on this exercise will pay off quickly."
    next_step = ("Try this exercise in memory mode." if overall >= 80
                 else "Repeat this exercise 3 more times, focusing on the first fix.")
    return {
        "summary": summary,
        "strengths": strengths or ["You completed the exercise. Every rep builds muscle memory."],
        "fixes": fixes,
        "style_note": exercise["tips"][0] if exercise.get("tips") else "",
        "next_step": next_step,
    }
