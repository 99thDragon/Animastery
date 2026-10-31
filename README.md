# Animastery

Learn art styles by drawing. Animastery gives you guided line-work exercises, measures every stroke
you make, and gives you coaching feedback on what to fix, with an AI coach on the back end.

## Art Coach (web app)

Pick an exercise, then trace over the guide (**Trace** mode) or study it for 4 seconds and draw it
from memory (**Memory** mode). Press **Check my lines** to get:

- **A score breakdown** of your line work:
  | Metric | What it measures |
  |---|---|
  | Accuracy | How far your line strays from the guide (average and 90th-percentile px) |
  | Coverage | How much of the guide you actually drew, and which parts you skipped |
  | Smoothness | Wobble/jitter in your line beyond the guide's own curvature |
  | Confidence | One clean stroke per line vs. sketchy feathering, plus time spent hesitating |
  | Line weight | Pen-pressure control: tapering (light-heavy-light) or evenness, depending on the exercise |
  | Direction | Whether strokes were pulled the intended way (e.g. hair from root to tip) |
- **An error heatmap** painted over your strokes (green = on the line, red = drifted)
- **Coach feedback**: what you're doing well, the 1-3 most important fixes, a drill for each,
  and a style note. When an Anthropic API key is configured, Claude looks at a snapshot of your
  drawing plus the measured metrics. Without a key, the app gives rule-based tips instead.
- **Progress tracking**: your best score per exercise is saved in the browser.

Exercises are grouped by style:

- **Fundamentals**: confident straight lines, tilted ellipse, line of action (S-curve)
- **Anime / idol style**: tapered hair strands, large anime eye, front-view anime face.
  The AI coach uses `love_live_style_notes.txt` as its style reference here.

A stylus (iPad + Pencil, Wacom, Surface pen) unlocks line-weight scoring. A mouse or finger works
for everything else.

### Run it

```bash
python -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # optional, enables the AI coach
```

```bash
.venv/bin/python -m artcoach.app
```

Then open http://localhost:5000.

Settings (environment variables):

| Variable | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | (none) | Enables AI coaching. Without it you get offline tips. |
| `ARTCOACH_AI` | `on` | Set to `off` to force offline tips |
| `ARTCOACH_MODEL` | `claude-opus-5-5` | Claude model used for coaching |
| `HOST` / `PORT` | `127.0.0.1` / `5000` | Where the server listens. Use `HOST=0.0.0.0` to draw from a tablet on your network. |

### Tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

### How it works

```
browser canvas (pointer events: x, y, time, pressure)
   │  POST /api/score
   ▼
artcoach/scoring.py   resample strokes → compare to guide → per-skill metrics + heatmap
   │  POST /api/coach  (metrics + PNG snapshot)
   ▼
artcoach/coach.py     Claude (vision + structured JSON output) → coaching feedback
                      └─ falls back to rule-based tips if the API is unavailable
```

| Path | Purpose |
|---|---|
| `artcoach/app.py` | Flask server and API routes |
| `artcoach/scoring.py` | Stroke analysis engine |
| `artcoach/exercises.py` | Exercise definitions (guide strokes + teaching notes) |
| `artcoach/coach.py` | AI coach and offline fallback |
| `artcoach/static/` | Drawing UI (HTML/CSS/JS, no build step) |
| `tests/` | Scoring and fallback tests |

### Adding an exercise

Add an entry to `EXERCISES` in `artcoach/exercises.py`. Guide strokes live in an 800×600 space
and are built from the `line`, `ellipse` and `bezier` helpers. Set `pressure_profile`
(`"taper"` or `"even"`) and `directional` to choose what gets scored.

## Original style-guide search (legacy)

The first version of this project is still here: a keyword search over
`love_live_style_notes.txt`.

```bash
python simple_rag_gui.py    # tkinter GUI
```

```bash
python simple_rag.py        # command line
```

## Roadmap

- Upload your own reference image and auto-trace guide strokes from it
- Auto-align memory drawings (score shape even if drawn shifted or scaled)
- More styles: manga inking, chibi proportions, gesture drawing with timed poses
- Per-exercise progress charts and spaced-repetition practice plans
- Stroke-order replay comparing your stroke against an ideal one

## License

MIT
