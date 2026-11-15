# 30-second demo storyboard

Use the actual app on your machine after visually reviewing it. Do not hide the synthetic-elevation badge. The Guided demo button changes views on this sequence; manual narration below describes only implemented behavior.

| Time | Screen / action | Suggested narration |
|---|---|---|
| 0–5 s | ATLAS, cached Jezero orbital image | “Start with NASA's real Jezero imagery.” |
| 5–11 s | MISSION 3D, return route | “Plan a human excursion and reserve time to return. This terrain is a labelled test simulation.” |
| 11–18 s | SCOUT OR SKIP, observed slip and belief | “A simulated scout changes our belief about an uncertain corridor.” |
| 18–24 s | Replay at 65%+, posterior route | “Replan with the new evidence and see the reason.” |
| 24–30 s | REWIND, change to expensive-scout | “Across paired simulations, scouting sometimes helps—and sometimes costs too much.” |

The currently included 3D terrain is synthetic because source elevation downloads were blocked. Do not narrate it as NASA elevation. The recommendation card uses an assumed local detour, while the experiment chart uses actual candidate-route time differences.

## Alternative seven-slide outline

1. Title / Team 404 / purpose.
2. Actual Atlas screenshot; source and coverage.
3. Actual mission screenshot; synthetic-terrain badge and return reserve.
4. Actual scout screenshot; observation, prior and posterior.
5. Actual replay screenshot; before/after route.
6. Chart from saved experiment logs, including expensive scouting losses.
7. Sources, current limitations and public project link.

No UI screenshots were captured here because preview startup failed. Capture actual screenshots on your computer; do not create illustrative screenshots and present them as working-app evidence.

```cmd
.venv\Scripts\activate
python -m pip install playwright
python -m playwright install chromium
python scripts\capture_evidence.py
```

Record and upload a public <=30-second video, or prepare <=7 slides, then test the public link in a private browser window. Review the official current submission guide before submitting.
