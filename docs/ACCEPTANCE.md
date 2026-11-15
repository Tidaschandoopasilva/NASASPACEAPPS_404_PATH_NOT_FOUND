# Acceptance — V2

| Item | Status | Evidence |
|---|---|---|
| Real NASA Jezero imagery | Acquired, cached, used | 20 WMTS tiles, capabilities, imagery metadata |
| Real CTX DEM | Acquired, cropped, used | data/jezero-ctx-crop.tif; source XML; 8,015,040 transferred bytes; SHA256 |
| DEM alignment / slope / mesh | Implemented; numeric checks pass | common ROI bounds; native affine; slope tests; evidence/dem-alignment-v2.png visually inspected |
| Mission route + return constraints | Implemented | A*, live routes, source-bearing exports, budget tests |
| Science stop membership | Partial | geological rationale cited; proposed positions, no verified polygon intersection |
| Real rover / astronaut assets | Included and loaded by code | NASA catalog GLBs, hashes, credits; visual runtime unverified |
| Trained SVNet artifacts | PASS | actual model.joblib, calibration.joblib, metadata, fitted-model tests |
| Leakage / split separation | PASS | feature-contract, seed, spatial-window and sibling-action tests |
| Calibration / independent test | PASS | separate 100-scenario calibration and test regions; saved predictions and Brier/reliability metrics |
| Baselines / abstention / regret | PASS for documented scope | forced and constraint-matched policies, paired CIs, raw records |
| Model-connected UI | Implemented / API tested | live recommendations can update mission; held-out exploration and outcome reveal; production build passes |
| Physics-based validation | NOT RUN | three PyBullet installation failures; optional stress script, PHYSICS_STATUS.md |
| Browser QA / screenshots | BLOCKED | repeated managed preview uv_interface_addresses failure; no screenshots fabricated |
| Windows launch | Provided, not executed on Windows | scripts/setup.bat and start_all.bat |
| Submission materials | Draft complete | sources, code license, method, measured results, demo script |

Current exact test/build output: docs/evidence/pytest-v2.txt and build-v2.txt. Model data/training/evaluation logs are alongside them. Stage A–D reports and docs/archive-v1 describe the superseded first build.

Final V2 verification: 36 Python tests passed; TypeScript/Vite production build exited 0. See docs/evidence/pytest-v2.txt and build-v2.txt.
