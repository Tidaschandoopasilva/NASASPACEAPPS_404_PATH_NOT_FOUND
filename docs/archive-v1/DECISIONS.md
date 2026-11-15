# Decisions and fallbacks

- Earlier Stage 01 ZIP contained specifications, not executable source. Preserved under previous_stage01; the app is new original code.
- Windows project path in the brief is not mounted here. Built an extractable `path-not-found` directory with Windows CMD scripts.
- NASA imagery and both catalog GLBs were downloaded successfully. No tile proxy is needed for the cached ROI. Acquisition script restricts requests to NASA Trek and uses byte/time limits.
- DEM attempts: published Planetarymaps endpoint HTTP 403; same endpoint with browser user agent/query HTTP 403; Astropedia mirror HTTP 503. HiRISE catalog pages returned 403. No elevation was inferred from imagery. Stage A's real-DEM gate remains BLOCKED.
- Synthetic surface is available for explicit test/simulation behavior; it is always labelled. Atlas imagery remains OBSERVED. No synthetic elevation is advertised as Jezero relief.
- Science targets use cited Jezero geology as motivation, but exact unit memberships were not verified. Labels say proposed; M3 is PARTIAL.
- Root app package implements FastAPI to support the exact requested project-root uvicorn command. apps/api contains a pointer, avoiding duplicate Python packages.
- Rover GLB node graph contains one combined `Wheels_objs` node, not six separable wheel pivots. Animate body only; no false wheel rotation. Model textures are replaced at render time to suppress insignia.
- Browser preview startup failed in the managed environment with Node `uv_interface_addresses` error. No app code was changed to bypass that infrastructure issue. Browser appearance, screenshot evidence, FPS and Windows launch remain unverified. A local capture script is supplied.
- Experiments use one uncertain corridor and two cached route choices; the UI card uses an assumed detour. These are scoped educational models, documented explicitly.
- Stage checkpoints were assembled after implementation and verification in this session, rather than pretending staged approvals or real-data gates had passed. Stage D's full acceptance gate is NOT met because the DEM and browser evidence blockers remain.
- Optional raw-photo cards, geologic polygons, adaptive mesh resolution and rigged character gait are not implemented.

- Experiment verification caught an infeasible rerun after shortening interactive waypoints: the avoid policy excluded the new Science A cell. Fixed by retaining the original fixed experiment itinerary, recording it in metadata, refusing empty-log overwrite and testing CSV as well as JSONL row counts. Final rerun passed.
