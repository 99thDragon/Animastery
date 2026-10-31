"""Built-in drawing exercises.

Each exercise is a set of guide strokes in the logical 800x600 canvas space plus
the teaching metadata the scorer and the AI coach use.
"""

from __future__ import annotations

import math


def line(x1, y1, x2, y2, n=40):
    return [[x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n] for i in range(n + 1)]


def ellipse(cx, cy, rx, ry, start=0.0, end=2 * math.pi, rot=0.0, n=120):
    pts = []
    for i in range(n + 1):
        a = start + (end - start) * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append([cx + x * math.cos(rot) - y * math.sin(rot),
                    cy + x * math.sin(rot) + y * math.cos(rot)])
    return pts


def bezier(p0, p1, p2, p3, n=60):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        pts.append([
            u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1],
        ])
    return pts


FUNDAMENTALS = "Fundamentals"
ANIME = "Anime / idol style"

EXERCISES = [
    {
        "id": "straight-lines",
        "name": "Confident straight lines",
        "style": FUNDAMENTALS,
        "level": 1,
        "description": "Pull three straight lines left to right, one stroke each.",
        "tips": [
            "Draw from the shoulder, not the wrist, for long lines.",
            "Place your pen at the start dot, look at the end point, then pull in one motion.",
            "Speed helps: slow lines wobble.",
        ],
        "pressure_profile": "even",
        "directional": True,
        "strokes": [line(150, 200, 650, 200), line(150, 300, 650, 300), line(150, 400, 650, 400)],
    },
    {
        "id": "ellipse",
        "name": "Tilted ellipse",
        "style": FUNDAMENTALS,
        "level": 1,
        "description": "Ellipses are the base of heads, eyes and perspective. Trace it in one loop.",
        "tips": [
            "Ghost the motion in the air a few times before touching down.",
            "Keep both ends equally round. Pointy ends usually mean you slowed down there.",
        ],
        "pressure_profile": "even",
        "directional": False,
        "strokes": [ellipse(400, 300, 220, 130, rot=-0.2)],
    },
    {
        "id": "line-of-action",
        "name": "Line of action (S-curve)",
        "style": FUNDAMENTALS,
        "level": 2,
        "description": "The flowing S-curve behind dynamic poses. Pull it bottom to top with a taper.",
        "tips": [
            "Start light, press through the middle, lift off light.",
            "Keep the curve continuous. Don't flatten it into straight segments.",
        ],
        "pressure_profile": "taper",
        "directional": True,
        "strokes": [bezier((200, 500), (250, 100), (550, 500), (600, 100))],
    },
    {
        "id": "hair-strands",
        "name": "Tapered hair strands",
        "style": ANIME,
        "level": 2,
        "description": "Anime hair is drawn as clumps of tapered C-curves, pulled from the root to the tip.",
        "tips": [
            "Every strand starts at the root (the dot) and flicks off at the tip.",
            "Taper both ends: light, heavier, light.",
            "Draw each strand in a single stroke. Overlapping pieces read as messy.",
        ],
        "pressure_profile": "taper",
        "directional": True,
        "strokes": [
            bezier((380, 120), (300, 180), (280, 330), (330, 470)),
            bezier((410, 120), (360, 220), (360, 360), (420, 480)),
            bezier((440, 120), (500, 200), (520, 330), (480, 460)),
            bezier((470, 125), (560, 170), (600, 300), (580, 420)),
        ],
    },
    {
        "id": "anime-eye",
        "name": "Large anime eye",
        "style": ANIME,
        "level": 3,
        "description": "Big, expressive eyes: a heavy upper lash line, light lower lid, tall iris and a highlight.",
        "tips": [
            "The upper lash line is the heaviest line in the face, so press hardest there.",
            "Keep the lower lid light and broken. It should be suggested, not outlined.",
            "The iris is a tall oval tucked under the upper lid.",
            "The sparkle highlight sits on the same side as the light source.",
        ],
        "pressure_profile": "taper",
        "directional": False,
        "strokes": [
            bezier((260, 280), (320, 190), (480, 180), (560, 250)),
            bezier((300, 360), (370, 395), (470, 395), (530, 350)),
            ellipse(410, 300, 70, 90),
            ellipse(385, 265, 16, 16, n=40),
        ],
    },
    {
        "id": "anime-face",
        "name": "Front-view anime face",
        "style": ANIME,
        "level": 3,
        "description": "Rounded cranium, soft jaw tapering to a small chin, and the eye line set low on the face.",
        "tips": [
            "Youthful proportions: the eye line sits at or just below the middle of the head.",
            "Draw each side of the jaw as one smooth curve that meets at the chin.",
            "Keep both sides symmetrical. Flip the canvas in your head to check.",
        ],
        "pressure_profile": "even",
        "directional": False,
        "strokes": [
            ellipse(400, 260, 150, 150, start=0.9 * math.pi, end=2.1 * math.pi),
            bezier((257, 306), (265, 400), (345, 470), (400, 482)),
            bezier((543, 306), (535, 400), (455, 470), (400, 482)),
            line(285, 330, 515, 330),
        ],
    },
]

_BY_ID = {e["id"]: e for e in EXERCISES}


def get_exercise(exercise_id):
    return _BY_ID.get(exercise_id)


def public_list():
    """Exercises with rounded coordinates, for the browser."""
    out = []
    for e in EXERCISES:
        item = dict(e)
        item["strokes"] = [[[round(x, 1), round(y, 1)] for x, y in s] for s in e["strokes"]]
        out.append(item)
    return out
