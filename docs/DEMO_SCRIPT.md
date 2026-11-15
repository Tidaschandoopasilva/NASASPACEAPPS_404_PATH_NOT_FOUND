# V2 demo: 30-second storyboard

| Seconds | Actual app action | Narration |
|---|---|---|
| 0–5 | ATLAS: real Jezero imagery | “Start with NASA observations of Jezero.” |
| 5–10 | MISSION 3D: textured real elevation | “Plan a human science excursion with a complete return route.” |
| 10–18 | 404-SVNET: current mission predictions | “Our trained model estimates the outcomes of proceeding, avoiding and scouting.” |
| 18–23 | Apply AVOID; inspect updated route | “Use an eligible decision—or request human review when constraints fail.” |
| 23–30 | Model evaluation: utility and calibration | “Tested on held-out terrain scenarios, with calibrated predictions and honest baseline comparisons.” |

Do not call simulated success probabilities real astronaut safety guarantees. The trained model does not beat every baseline. The context photos are real NASA products but not exact registered waypoint views.

Alternative seven-slide outline: (1) purpose/team, (2) real data/coverage, (3) human return route, (4) trained model inputs/outputs, (5) leakage-resistant splits/calibration, (6) actual policy comparison including strongest baseline, (7) sources/AI/limitations/public links.

Use screenshots from a locally inspected running app. Browser preview was unavailable here. Scientific data figures in docs/evidence are actual rendered data/results, not application screenshots. The legacy Guided demo button still shows the original map/scout/replay flow; use the manual sequence above for the new model story.

```cmd
python -m pip install playwright
python -m playwright install chromium
python scripts\capture_evidence.py
```

Capture the new SVNet tab manually as well. Upload a publicly viewable <=30-second video or <=7-slide demo, and verify the link before portal submission.

Opening slide caption: **Real terrain, simulated hazards.** Show a stop's selection reason and simulated terrain POV. Keep the Mastcam-Z regional photographs separate. Describe the equipment and weather timing as adjustable assumptions, and the reserve as a simulator rule.
