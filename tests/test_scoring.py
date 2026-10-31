import math
import random
import unittest

from artcoach import exercises, scoring


def as_attempt(polyline, *, dt=8.0, pressure=0.5, offset=(0.0, 0.0), jitter=0.0, seed=0):
    rng = random.Random(seed)
    pts = []
    for i, (x, y) in enumerate(polyline):
        pts.append([x + offset[0] + rng.uniform(-jitter, jitter),
                    y + offset[1] + rng.uniform(-jitter, jitter),
                    i * dt,
                    pressure(i / max(1, len(polyline) - 1)) if callable(pressure) else pressure])
    return pts


def taper(f):
    return 0.2 + 0.8 * math.sin(math.pi * f)


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.lines = exercises.get_exercise("straight-lines")
        self.hair = exercises.get_exercise("hair-strands")

    def score(self, ex, attempt):
        return scoring.analyze(ex["strokes"], attempt,
                               pressure_profile=ex["pressure_profile"],
                               directional=ex["directional"])

    def test_perfect_trace_scores_high(self):
        r = self.score(self.lines, [as_attempt(s) for s in self.lines["strokes"]])
        self.assertTrue(r["ok"])
        self.assertGreaterEqual(r["metrics"]["accuracy"]["score"], 98)
        self.assertGreaterEqual(r["metrics"]["coverage"]["score"], 98)
        self.assertGreaterEqual(r["metrics"]["smoothness"]["score"], 95)
        self.assertEqual(r["metrics"]["direction"]["score"], 100)
        self.assertGreaterEqual(r["overall"], 95)

    def test_offset_lowers_accuracy(self):
        good = self.score(self.lines, [as_attempt(s) for s in self.lines["strokes"]])
        off = self.score(self.lines, [as_attempt(s, offset=(0, 12)) for s in self.lines["strokes"]])
        self.assertLess(off["metrics"]["accuracy"]["score"], good["metrics"]["accuracy"]["score"] - 30)
        self.assertAlmostEqual(off["metrics"]["accuracy"]["mean_deviation_px"], 12, delta=1)

    def test_jitter_lowers_smoothness(self):
        r = self.score(self.lines, [as_attempt(s, jitter=4, seed=i)
                                    for i, s in enumerate(self.lines["strokes"])])
        self.assertLess(r["metrics"]["smoothness"]["score"], 60)

    def test_curved_guide_is_not_penalised_for_its_own_curvature(self):
        ellipse = exercises.get_exercise("ellipse")
        r = self.score(ellipse, [as_attempt(s) for s in ellipse["strokes"]])
        self.assertGreaterEqual(r["metrics"]["smoothness"]["score"], 95)

    def test_partial_drawing_lowers_coverage_and_names_the_gap(self):
        half = [as_attempt(s[: len(s) // 2]) for s in self.lines["strokes"]]
        r = self.score(self.lines, half)
        self.assertLess(r["metrics"]["coverage"]["score"], 60)
        self.assertTrue(any("end" in n and "skipped" in n for n in r["notes"]))

    def test_reversed_strokes_fail_direction(self):
        r = self.score(self.hair, [as_attempt(list(reversed(s))) for s in self.hair["strokes"]])
        self.assertEqual(r["metrics"]["direction"]["score"], 0)

    def test_feathered_strokes_lower_confidence(self):
        one = self.score(self.lines, [as_attempt(s) for s in self.lines["strokes"]])
        chopped = []
        for s in self.lines["strokes"]:
            for i in range(0, len(s) - 1, 3):
                chopped.append(as_attempt(s[i:i + 4]))
        r = self.score(self.lines, chopped)
        self.assertLess(r["metrics"]["confidence"]["score"], one["metrics"]["confidence"]["score"] - 30)

    def test_hesitation_detected(self):
        slow = [as_attempt(s, dt=400) for s in self.lines["strokes"]]   # ~0.03 px/ms
        r = self.score(self.lines, slow)
        self.assertLess(r["metrics"]["confidence"]["hesitation_score"], 20)

    def test_pressure(self):
        no_pen = self.score(self.hair, [as_attempt(s) for s in self.hair["strokes"]])
        self.assertIsNone(no_pen["metrics"]["pressure"]["score"])
        tapered = self.score(self.hair, [as_attempt(s, pressure=taper) for s in self.hair["strokes"]])
        self.assertGreaterEqual(tapered["metrics"]["pressure"]["score"], 90)
        backwards = self.score(self.hair, [as_attempt(s, pressure=lambda f: 1.2 - taper(f))
                                           for s in self.hair["strokes"]])
        self.assertEqual(backwards["metrics"]["pressure"]["score"], 0)

    def test_empty_attempt(self):
        r = self.score(self.lines, [])
        self.assertFalse(r["ok"])

    def test_every_exercise_scores_a_perfect_trace_well(self):
        for ex in exercises.EXERCISES:
            with self.subTest(ex["id"]):
                r = self.score(ex, [as_attempt(s) for s in ex["strokes"]])
                self.assertGreaterEqual(r["overall"], 90)


class CoachFallbackTests(unittest.TestCase):
    def test_local_feedback_shape(self):
        from artcoach import coach
        ex = exercises.get_exercise("straight-lines")
        r = scoring.analyze(ex["strokes"], [as_attempt(s, offset=(0, 15), jitter=3)
                                            for s in ex["strokes"]], directional=True)
        fb = coach.local_feedback(ex, r)
        for key in ("summary", "strengths", "fixes", "style_note", "next_step"):
            self.assertIn(key, fb)
        self.assertTrue(fb["fixes"])


if __name__ == "__main__":
    unittest.main()
