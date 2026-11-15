# Acceptance — full gate NOT MET

| MUST | Status | Evidence / remaining work |
|---|---|---|
| M1 NASA Jezero imagery, credits | IMPLEMENTED; render QA limited | 20 downloaded tiles, data/wmts-capabilities.xml, imagery-metadata.json and cached PNG; PNG visually inspected. Atlas code and source drawer build. Browser runtime unverified. |
| M2 genuine aligned DEM, slope, mesh | BLOCKED | Real endpoint HTTP 403/503. Synthetic mesh and slope tests pass. No real DEM claimed. |
| M3 habitat, two geological stops, return/A* | PARTIAL | API route metrics and tests; editable markers. Exact geology membership unverified. |
| M4 astronaut/rover models and motion | IMPLEMENTED; visual QA pending | 762,988-byte astronaut and 4,987,176-byte rover GLBs, node manifests, procedural motion code. Browser unavailable. |
| M5 belief, scout, replan, why | PARTIAL | Seeded integration test, saved episode. VoS card is an assumed local decision; rover trace and scene traversal are illustrative, not a coupled complete scout trajectory. |
| M6 >=30 paired seeds, honest outcomes | PASS for documented synthetic scope | 100 seeds × 3 policies × 8 regimes; JSONL/CSV; expensive-scout loses. Single-corridor experiment, not operational Mars evaluation. |
| M7 packet, credits, license, disclosure | PASS as a draft packet | README, Apache-2.0, NOTICE, model credits, DEMO_SCRIPT, SUBMISSION_PACKET. Public demo/portal submission manual. |

## Checks actually run

- `python -m pytest -q`: final result recorded in evidence/pytest.txt.
- `npm run build`: TypeScript and Vite, exit 0; evidence/build.txt. Bundle-size advisory remains, no 60 fps claim.
- `python scripts\run_experiments.py`: exit 0 after the infeasible-itinerary correction; evidence/experiment-run.txt and raw logs.
- Model GLB headers/nodes, imagery dimensions/variance and exact asset hashes verified.
- Preview: failed startup, Node uv_interface_addresses. Browser screenshot/UI interaction checks NOT RUN. Windows scripts NOT RUN on Windows.

No unverified item is counted as a passed visual or real-terrain gate.
