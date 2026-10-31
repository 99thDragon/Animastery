import io
import os
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

os.environ["ARTCOACH_AI"] = "off"   # never call the API from tests

from artcoach import app as app_module, styles  # noqa: E402


def line_art_png(size=(1200, 900)):
    im = Image.new("RGB", size, (250, 246, 240))
    d = ImageDraw.Draw(im)
    d.ellipse((380, 160, 820, 640), fill=(255, 224, 205))           # soft fill: should not trace
    d.arc((380, 160, 820, 640), 180, 360, fill=(30, 25, 40), width=6)
    d.line([(300, 750), (900, 750)], fill=(30, 25, 40), width=5)
    for cx in (500, 700):
        d.ellipse((cx - 35, 430, cx + 35, 520), outline=(60, 40, 90), width=4)
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()


class ExtractionTests(unittest.TestCase):
    def test_normalizes_to_canvas(self):
        img = styles.normalize_image(line_art_png((300, 900)))
        self.assertEqual(img.size, (800, 600))

    def test_rejects_non_images(self):
        with self.assertRaises(styles.StyleError):
            styles.normalize_image(b"not an image")

    def test_extracts_the_drawn_lines(self):
        strokes = styles.extract_strokes(styles.normalize_image(line_art_png()))
        self.assertGreaterEqual(len(strokes), 3)
        self.assertLessEqual(len(strokes), styles.MAX_STROKES)
        # The long horizontal line (y=750 of 900 -> 500 on the 800x600 canvas) is found.
        horizontal = [s for s in strokes
                      if abs(s[0][1] - 500) < 4 and abs(s[-1][1] - 500) < 4 and styles._length(s) > 300]
        self.assertTrue(horizontal)

    def test_blank_image_is_rejected(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        old = styles.STYLES_DIR
        styles.STYLES_DIR = Path(tmp.name)
        self.addCleanup(setattr, styles, "STYLES_DIR", old)
        buf = io.BytesIO()
        Image.new("RGB", (400, 300), "white").save(buf, "PNG")
        with self.assertRaises(styles.StyleError):
            styles.create(buf.getvalue(), "Blank", "", "")


class StyleApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = styles.STYLES_DIR
        styles.STYLES_DIR = Path(self.tmp.name)
        self.client = app_module.app.test_client()

    def tearDown(self):
        styles.STYLES_DIR = self.old
        self.tmp.cleanup()

    def upload(self, **extra):
        data = {"image": (io.BytesIO(line_art_png()), "ref.png"), "name": "Test style",
                "artist": "Some Artist", "source": "https://example.com/art", "study_ack": "yes"}
        data.update(extra)
        return self.client.post("/api/styles", data=data, content_type="multipart/form-data")

    def test_requires_study_acknowledgement(self):
        r = self.upload(study_ack="")
        self.assertEqual(r.status_code, 400)

    def test_upload_score_and_delete(self):
        r = self.upload()
        self.assertEqual(r.status_code, 200, r.get_json())
        ex = r.get_json()
        self.assertTrue(ex["id"].startswith("style:"))
        self.assertEqual(ex["artist"], "Some Artist")
        self.assertIsNone(ex["profile"])
        self.assertEqual(ex["profile_source"], "disabled")

        listed = self.client.get("/api/styles").get_json()
        self.assertEqual([s["id"] for s in listed], [ex["id"]])

        img = self.client.get(ex["reference_image"])
        self.assertEqual(img.status_code, 200)
        self.assertEqual(img.mimetype, "image/png")
        img.close()

        # Tracing the extracted guide perfectly scores well through the normal scoring route.
        attempt = [[[x, y, i * 8, 0.5] for i, (x, y) in enumerate(s)] for s in ex["strokes"]]
        score = self.client.post("/api/score", json={"exercise_id": ex["id"], "strokes": attempt}).get_json()
        self.assertTrue(score["ok"])
        self.assertGreaterEqual(score["overall"], 85)

        fb = self.client.post("/api/coach", json={"exercise_id": ex["id"], "result": score}).get_json()
        self.assertEqual(fb["source"], "local")

        self.assertEqual(self.client.delete(f"/api/styles/{ex['style_id']}").status_code, 200)
        self.assertEqual(self.client.get("/api/styles").get_json(), [])

    def test_bad_ids_are_rejected(self):
        self.assertEqual(self.client.get("/api/styles/../../etc/image").status_code, 404)
        self.assertEqual(self.client.get("/api/styles/zzz/image").status_code, 404)
        self.assertEqual(self.client.delete("/api/styles/zzz").status_code, 404)
        r = self.client.post("/api/score", json={"exercise_id": "style:nope", "strokes": [[[1, 2]]]})
        self.assertEqual(r.status_code, 404)


if __name__ == "__main__":
    unittest.main()
