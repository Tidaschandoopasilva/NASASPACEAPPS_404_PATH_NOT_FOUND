# Legacy paired-policy sweep — rerun on real CTX terrain

This separate experiment is not the SVNet train/test dataset. 2,400 simulated episodes: 100 seeds × 3 strategies × 8 regimes. Geometry now derives from the real USGS/NASA CTX DEM. Hazard and utility labels remain simulated. Fixed itinerary [78,22] → [30,34] → [42,72] → home.

| Regime | Scout − proceed mean | 95% paired bootstrap CI |
|---|---:|---|
| baseline | 7.477 | 0.865 to 14.604 |
| expensive-scout | -57.523 | -64.135 to -50.396 |
| rare-hazard | -7.823 | -9.070 to -5.741 |
| common-hazard | 49.296 | 40.296 to 58.296 |
| noisy-sensor | 3.296 | -4.704 to 11.296 |
| no-uncertainty-penalty | 7.861 | 1.190 to 15.120 |
| flat-terrain | 7.342 | 0.751 to 14.422 |
| steeper-terrain | 6.513 | -1.487 to 14.513 |

Inputs, raw CSV/JSONL, waypoints and assumptions are saved. A single hidden corridor is evaluated; science is 1 by construction for feasible routes. This is not clinical/physical astronaut safety validation. The stronger ML policy comparison with abstention and matching constraints is in MODEL_EVALUATION.md. The synthetic v1 summary is historical under data/archive-v1.
