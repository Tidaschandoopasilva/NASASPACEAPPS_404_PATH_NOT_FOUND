# Current progress / resume — V2

Real DEM blocker resolved. Current surface is observed/derived CTX, not synthetic. NASA imagery and real catalog models retained; two context photos added. SVNet data, trained/calibrated artifacts and independent evaluation completed. Live ML recommendation can update route; conservative human-review gate remains available.

Source: data/dem-acquisition.json; output model: models/svnet_v1. Dataset: 400/100/100/100 geographically disjoint scenarios, 2,100 rows. Test 100 scenarios. Strongest constrained risk-A* baseline exceeds SVNet mean utility; keep this honest result. No test-based retraining performed.

Current checks: docs/evidence/*v2.txt and svnet-*.txt. Browser preview blocked; no screenshot evidence. PyBullet installation failed; optional script only. Next manual work: Windows/browser inspection and public demo/submission. Further R&D: mapped geology and better physical validation, without changing frozen test outcomes silently.

Historical first-build reports are marked superseded; current acceptance is docs/ACCEPTANCE.md and STAGE_V2_REPORT.md.
