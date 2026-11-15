# CODEX AUTOPILOT PROMPT v3.0 — 404: PATH NOT FOUND (build everything, end to end)

Date 2026-11-14 | Windows CMD | Mode: AUTOPILOT (all stages in one run, self-gated)
This file is self-contained. It supersedes v1.0 and v2.0. Do not delete earlier files.
Paste it into Codex, or run: `Read CODEX_AUTOPILOT_PROMPT_v3.md and execute it completely.`

---

## 0. Mission and operating mode

You are the lead full-stack, geospatial, 3D-graphics and robotics-simulation engineer for Team 404's entry to the
2026 NASA Space Apps Challenge, **Interplanetary Survival Guide: Martian Map**. Build an original app,
**404: PATH NOT FOUND**, with research feature **Scout or Skip**, and prepare the full submission packet.

Project root: `C:\Users\User\Desktop\Nasa Space APPS`. App goes in `path-not-found/`. Inspect existing files first
(`team404_codex_stage01/`, `TEAM404_HANDOVER/`, any earlier `path-not-found/`). Extend viable work; never destructively overwrite.

**AUTOPILOT RULES (the user wants minimal back-and-forth):**
1. Run Stages A -> B -> C -> D in order WITHOUT waiting for approval between them. Do not ask questions. Use the defaults in this file.
2. After each stage: run the tests/build, fix failures, commit (`git init` if needed; semantic message), append to `PROGRESS.md`
   (stage, status, what works, what failed, next step), write `STAGE_X_REPORT.md`, then continue to the next stage.
3. **Fix budget:** on any failure, try up to 3 distinct fixes. If still failing, apply the documented FALLBACK for that item, record it in
   `docs/DECISIONS.md` and the stage report, and keep going. Never stall the whole build on one item.
4. **Timeboxes** (advisory, keep moving): Stage A ~3 h, B ~4 h, C ~6 h, D ~3 h. The submission-critical items are MUST items (section 2).
5. If the session is interrupted, `PROGRESS.md` must be enough for `codex resume` to continue exactly where it stopped. Update it often.
6. Never claim what you did not run. Report real commands, exit codes and real output. Never invent numbers, screenshots or test results.
7. At the very end print a **"YOU STILL NEED TO DO"** checklist (manual items only: portal submission, video recording, anything you could not do).
8. Do not stop early because the app "looks done": stop only when Stage D's gate is met or a hard blocker is documented.

Global ground rules:
- Never present synthetic data as real Mars data; label SYNTHETIC in UI and files. Tag all data OBSERVED / DERIVED / ASSUMED / SIMULATED.
- Planner must never read `truth_map` (enforced by a test).
- Windows CMD commands only in docs. No paid APIs, keys, or GPU requirement. Everything runs on localhost.
- No NASA logos/emblems/brand marks; no "NASA-approved/validated" claims. Visible note in Rover/Scout views and exports:
  **"Research simulator; not validated for mission operations."**

---

## 1. Product

A cinematic **3D mission-control app (not a basic dashboard)**: plan a human Marswalk on real Jezero terrain, watch a 3D astronaut walk the route,
and when part of the route is uncertain the app decides **PROCEED / AVOID / SCOUT** (send a simulated Perseverance-style rover first), replans,
and explains why. Primary deliverable = a layered, georeferenced NASA map for a HUMAN Marswalk with science objectives and a return route.
The rover supports the human mission.

Views sharing one mission state:
- **ATLAS (2D, OpenLayers):** real Mars Trek imagery, layer/source/coverage panel, coordinates.
- **MISSION 3D (Three.js via @react-three/fiber + drei):** DEM-displaced terrain with real imagery, habitat, science stops, routes, 3D astronaut, 3D rover, uncertainty overlay.
- **SCOUT OR SKIP:** decision panel (VoS breakdown, plain-English recommendation) over the 3D view.
- **REWIND:** timeline, belief/route before vs after, paired-seed charts, JSON/CSV export.

---

## 2. Scope

MUST (build these first; they define success):
- M1 Real NASA imagery of Jezero rendered, credited, source/coverage panel (Mars Trek).
- M2 Real Jezero DEM crop aligned to imagery; slope; nodata handled; 3D terrain.
- M3 Habitat + 2 science stops (justified by cited geology) + outbound AND return route; shortest vs risk-aware (A*).
- M4 3D astronaut walking the route; 3D Perseverance model scouting.
- M5 Belief map + simulated scout observation + replan + "why" explanation.
- M6 Paired-seed experiment (>=30 seeds x proceed/avoid/scout) from saved logs; honest result including a regime where scouting loses.
- M7 Credits, license, README, demo materials, submission packet.

SHOULD: Rewind scrubber with before/after route; Perseverance raw-photo cards; geologic-unit overlay; keyboard access; reduced-motion.
WON'T: trained neural models, PyBullet as a requirement, multi-rover, operational safety/radiation claims, global Mars map.
Cut order if time runs out: SHOULD items from the bottom, then polish. Never cut Stage D.

---

## 3. NASA data contract (MANDATORY)

At least one NASA source from the challenge Resources tab must be actually used (not just linked). Maintain `docs/DATA_SOURCES.md`:
URL, owner, product, acquisition date, bounds, projection, resolution, rights, USED/NOT USED, cache path, where used in the app.

| Source | URL | Role |
|---|---|---|
| NASA/JPL Mars Trek | https://trek.nasa.gov/mars/ (WMTS docs: https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=mars) | PRIMARY imagery (+ elevation if a covering product exists) |
| USGS-NASA Planetary Geologic Mapping | https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars | Jezero geologic units to justify science stops |
| Mars Perseverance Raw Images | https://mars.nasa.gov/mars2020/multimedia/raw-images/ | 2-5 ground photos on science-stop cards with sol/camera metadata |
| Curiosity Mount Sharp route graphic | https://science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp/ | UX reference ONLY, not Jezero data |
| NASA Worldview | https://worldview.earthdata.nasa.gov/ | NOT USED (Earth imagery); say so in DATA_SOURCES.md |

Additional (verify before use): USGS Jezero HiRISE DEM + orthomosaic releases (links in `TEAM404_HANDOVER` docs / usgs.gov data pages).

Procedure and defaults (decide yourself, do not ask):
1. Fetch WMTS `GetCapabilities` for Mars Trek. Layer IDs, bbox, tile matrix set, format and tile size come FROM CAPABILITIES. Never invent them.
2. ROI: a few km across near the Perseverance landing region in Jezero Crater (approx 18.44 N, 77.45 E planetocentric; verify against the dataset
   bounds and a known landmark). Choose the ROI so imagery AND DEM overlap.
3. Science stops: choose two locations on documented Jezero geology (e.g., a sedimentary/delta unit and a crater-floor unit such as those named
   in published Jezero mapping). Cite the geologic map/source in the stop card. Do not use uncited AI labels.
4. If tiles are blocked by CORS, add an **allowlisted** caching proxy (host allowlist, size limit, timeout). No arbitrary URL forwarding.
5. Stitch the ROI tiles on the backend into one cached texture + metadata JSON (bounds, CRS, zoom, layer ID, source IDs).
6. DEM: bounded crop (<= ~50 MB download, <= 512x512 working grid). If the high-res DEM is too slow, use an authentic lower-resolution Jezero DEM
   and say so. Preprocess once into `heightmap.npy`, a 16-bit PNG and `metadata.json`.
7. Raw images: inspect the site's real feed behavior; use only credible-context photos; mark as "approximate regional context" if not georeferenced.
8. If a source is unreachable after the fix budget: designed "data unavailable" state, log it, and use a SYNTHETIC-labelled surface for tests only.
   The demo must never silently use synthetic terrain as real Mars.

---

## 4. 3D assets contract

Verified catalog pages (confirm file name and usage terms on the page before use):
- Perseverance rover GLB: https://nasa3d.arc.nasa.gov/detail/perseverance
- Astronaut GLB (DigitalSpace Corporation via NASA): https://nasa3d.arc.nasa.gov/detail/astronaut
- Other suits: https://nasa3d.arc.nasa.gov/search/suit (EMU, Z2, Mark III)
- Mirror: https://github.com/nasa/NASA-3D-Resources (the rover is under a `perseverance-GLB` folder in `3D Models`; search the tree for the astronaut)

Procedure:
1. Check whether the files already exist in `apps/web/public/models/` (the user may have placed them). If so, use them.
2. Otherwise try to fetch them yourself (e.g., shallow `git clone --depth 1 --filter=blob:none` with sparse checkout of the needed folders, or direct download).
   Network may be blocked in your sandbox: if so, do not fail. Write `scripts\download_assets.py` and `docs\MANUAL_DOWNLOADS.md` with the exact page URLs and target paths,
   add the items to the "YOU STILL NEED TO DO" list, and run with clearly labelled procedural placeholders (box rover, capsule human) until the files appear.
   The loader must automatically prefer real GLBs when present and fall back otherwise.
3. Write `apps/web/public/models/CREDITS.md` (title, author/origin, URL, usage note, date, any modification). Show credits in the Sources drawer.
4. The NASA astronaut is a generic static model, not a validated biomechanics rig. Animate with a procedural gait (heel-toe bob, lateral sway, cadence tied to speed).
   Never call it a digital twin. Optional: support a rigged walking character as an alternate skin ONLY if a verified CC0/CC-BY file is supplied, with credit.
5. Rover GLB: inspect the node graph at load. If wheel nodes are separable, rotate them by `distance / wheel_radius`; otherwise animate the body only.
   Align the body to the terrain normal (pitch/roll).
6. Habitat, markers, hazard volumes: original primitives; label the habitat FICTIONAL.

---

## 5. Stack and layout

```
path-not-found/
  apps/web/   Vite + React + TypeScript; OpenLayers; @react-three/fiber + drei; Recharts; token-driven CSS
  apps/api/   Python 3.11+, FastAPI, Pydantic, NumPy, SciPy, Pillow, Pandas, pytest (Rasterio/PyProj only if they install cleanly)
  sim/        pure-Python kinematic + slip rover on the DEM grid (PyBullet optional, last, never required)
  data/       metadata + tiny fixtures only (large rasters/caches git-ignored)
  scripts/    download_data.py, process_dem.py, download_assets.py, run_experiments.py, capture_evidence.py, start_all.bat
  docs/       DATA_SOURCES, ASSUMPTIONS, ACCEPTANCE, DECISIONS, METHODS, EXPERIMENTS, CHANGELOG, DEMO_SCRIPT, SUBMISSION_PACKET, MANUAL_DOWNLOADS, evidence/
  tests/      unit, integration, fixtures
```
Must work: `python -m pytest`, `npm run build`, `npm run dev`, `python -m uvicorn app.main:app --port 8000`, and one `scripts\start_all.bat` that launches both.
Provide `.env.example` (no secrets), `.gitignore`, README with CMD instructions. Prefer simple robust code over elaborate untested code.

---

## 6. Geospatial rules

- Not Earth: no EPSG:4326/Web Mercator/OSM assumptions. Use dataset metadata. USGS Jezero products commonly use a Mars-centered equirectangular projection (sphere radius 3,396,190 m),
  planetocentric latitude, positive-east longitude; verify per dataset.
- Cell spacing in meters from the raster affine transform, never from degrees. No Earth geodesics.
- No-data/unobserved cells flagged invalid/unknown. **Unknown is never safe.**
- Report effective resolution after resampling; never present a coarse cell as a fine measurement.
- Keep planetary (lat/lon) and local meter coordinates in every feature.
- Tests: meters-per-cell, pixel<->world round trip, flat DEM = 0 slope, synthetic ramp = correct grade, nodata excluded.

---

## 7. Algorithms, equations and DEFAULT constants (all ASSUMED; record in docs/ASSUMPTIONS.md)

Slope: `z_x=(z[i,j+1]-z[i,j-1])/(2dx); z_y=(z[i+1,j]-z[i-1,j])/(2dy); theta=atan(sqrt(z_x^2+z_y^2))`.
Graph: 8-connected; edge distance `d=sqrt(dx^2+dy^2+dz^2)`; remove edges with nodata or `theta>theta_max` (default 20 deg).
```
edge_cost = w_d*d + w_s*(theta/theta_max)^2*d + w_h*p_haz*d + w_u*u_gap*d     defaults: w_d=1, w_s=2, w_h=4, w_u=1
```
A* with `h(n)=w_d*planar_distance_to_goal` (consistent). Walking time: base 1.0 m/s on flat, slowed by a documented slope factor; EVA time budget default 3 h
with a 20% return reserve. Routes: `PROCEED` (prior as-is), `AVOID` (risk-adjusted). Out-and-back H->S1->S2->H.
Infeasible -> **"no feasible path under these model assumptions"**; never silently relax constraints.

Hazard prior `p_haz`: DERIVED from slope and data-gap flags (document the function; state that the DEM cannot see wheel-sized rocks).
Aggregate into 3-6 **corridor regions** crossing candidate routes; each corridor has prior `p_k` and an uncertainty flag.

Hidden world (per seed): `truth_hazard_k ~ Bernoulli(p_k)`. `truth_map` lives only inside the simulator.

Sensor: rover measures slip `s = s_true + N(0, sigma^2)` (default sigma=0.08), observation `o = 1 if s > tau`. Derive `TPR`, `FPR` from sigma, tau and the slip distributions
under hazard/safe (document them; defaults give TPR~0.85, FPR~0.10).
```
p|o=1 = TPR*p / (TPR*p + FPR*(1-p));    p|o=0 = (1-TPR)*p / ((1-TPR)*p + (1-FPR)*(1-p))
U = R_science - lambda_t*T_route - lambda_h*E[hazard_loss] - c_scout     defaults: lambda_t=1, lambda_h=100 (loss per hazardous crossing), c_scout=5 (+ rover time)
V_now = max_a E[U(a)|p];  V_scout = sum_o P(o) max_a E[U(a)|p|o] - c_scout;  VoS = V_scout - V_now;  scout iff VoS > 0
```
VoS is computed from the PRIOR only, never from the current episode's hidden truth. This is standard expected value of sample information, not a new equation.

---

## 8. 3D scene and UX

- Terrain mesh from the heightmap (<= 512x512 vertices) with real imagery texture and DEM hillshade; labelled **vertical exaggeration** slider (default 1x, max 3x).
- Layer toggles: imagery / slope heatmap / geologic units (if integrated) / uncertainty ghost overlay / routes.
- Habitat (fictional), Science A/B (sand), corridor volumes: amber = uncertain, cyan = confirmed safe, rust = confirmed hazardous, always with text labels.
- Astronaut follows the A* polyline; HUD shows ETA and return margin. Rover drives the scout corridor; HUD shows slip, pitch, roll, speed, events.
  Any time acceleration is labelled "visualization acceleration".
- Camera modes: orbit, follow-astronaut, follow-rover, top-down. Play/Pause/Reset/Seed controls must really drive the simulation.
- Cinematic: the 3D scene fills the screen; slim collapsible overlay panels; a guided "Demo" button that runs the full 30-second story automatically
  (map -> routes -> uncertain corridor -> scout -> replan -> comparison) using real computed results.
- Performance target 60 fps on a laptop iGPU; auto-reduce mesh resolution if slow. Respect `prefers-reduced-motion`.
- Tokens: VOID `#0B111B`, PANEL `#142233`, SURFACE `#1B2C3D`, MARS `#D46D4B`, CYAN `#6CDDE2`, SAND `#E9C994`, AMBER `#F1B85B`, TEXT `#EDF3F8`, MUTED `#92A7B9`.
  8px spacing, 12px radius, monospace telemetry. Never encode safety by color alone. Visible focus, keyboard navigation.
- Badges on every feature: NASA OBSERVED / DERIVED / ASSUMED / SIMULATED. Designed loading/empty/error states.

---

## 9. Rover simulation

- Simplified Perseverance-inspired six-wheel rocker-bogie (reference ~1025 kg, wheel diameter ~0.525 m); Mars gravity 3.71 m/s^2 in config.
  Note: slip threshold `tan(theta) > mu` is independent of g; gravity matters for dynamics only.
- Kinematic + slip model on the DEM grid: `slip = 1 - v_actual/(r*omega)`; friction `mu` from the scenario; slope from the DEM; pitch/roll from the terrain normal.
  Fixed time step, seeded RNG, JSONL logs. A Gymnasium-style interface is optional. PyBullet only if everything else passes and it installs cleanly.
- Sanity tests: rests on flat ground; forward command moves forward; steering changes heading; low friction + steep slope raises slip; same seed reproduces the trace within tolerance.
- Label everything "approximation". Never call it a Mars safety model.

---

## 10. Experiment

Strategies: `proceed`, `avoid`, `scout`. Paired seeds: identical terrain crop, hidden hazards, waypoints, budgets per seed; only the policy differs.
Default seed list: integers 0..99 chosen now (fixed before seeing results); run >=30 (use 100 if it finishes in reasonable time).
Sweeps (documented): prior uncertainty, hazard prevalence, sensor sigma, scout cost, slope severity.
Metrics: science-completion fraction, safe return, route time, total meters, slip events, uncertainty reduction, mean utility; `Delta_i = U_scout,i - U_proceed,i`.
Report mean, median, bootstrap 95% CI (only with enough episodes), raw logs. Required checks: (a) a regime where scouting cost exceeds value, (b) ablation with uncertainty penalty on/off,
(c) flat-terrain sanity case, (d) planner-cannot-read-truth test. Charts come from saved logs, never hardcoded. If results are mixed, ship them as mixed. No fabricated gains.

---

## 11. API (versioned, Pydantic, OpenAPI)

`GET /health`, `/api/v1/sources`, `/api/v1/sites`, `/api/v1/layers`, `/api/v1/terrain`; `POST /api/v1/routes/compare`, `/api/v1/scout/estimate`, `/api/v1/simulations`;
`GET /api/v1/simulations/{id}`, `/api/v1/experiments/summary`. Validate bounds/units/budgets/episode size. No sample statistics without `demo=true` and `provenance="synthetic-example"`.
Typed fields: `id, source_ids, coordinate_system, position_m, latitude_deg, longitude_east_deg, units, data_state, model_assumptions, sim_seed, run_id, trial_status`.
Propagate `source_ids` into derived layers and exports. Exports (JSON/CSV) carry a source manifest and the research-simulator note.

---

## 12. Stages (run all, in order, self-gated)

**STAGE A — Real data + 3D terrain.** Skeleton, design system, source registry; Mars Trek imagery via WMTS (or documented fallback); DEM crop + alignment + slope + tests;
Atlas and 3D terrain with real texture; asset acquisition + credits; Sources drawer. Gate: real imagery and 3D terrain render with credits; geospatial tests pass; `npm run build` passes.

**STAGE B — EVA planning + 3D astronaut.** Editable habitat/science markers; A* shortest vs risk-aware; outbound and return; budgets; NASA geology/photo cards on science stops; astronaut walking; HUD.
Gate: A* fixture tests pass; infeasible case reported honestly.

**STAGE C — Scout or Skip + rover.** Corridors, prior, hidden world, belief update, VoS, kinematic/slip rover with the 3D Perseverance model, replan + "why".
Gate: truth-leakage test passes; sim sanity tests pass; saved seed telemetry.

**STAGE D — Rewind, experiments, ship.** Paired-seed runs, charts from logs, Rewind timeline/export, `scripts\capture_evidence.py` (Playwright screenshots into `docs/evidence/` if it installs; otherwise documented manual capture),
Apache-2.0 license for original code (do not relicense third-party data/models), README, `docs/DEMO_SCRIPT.md` (second-by-second 30 s storyboard + a <=7-slide outline using only real screenshots/results),
and `docs/SUBMISSION_PACKET.md` pre-filled: title, one-sentence purpose, ~200-word abstract, NASA data used and how, other assets/tools with versions, method, measured results, limitations, license, links to fill in.
Gate: every MUST item true in `docs/ACCEPTANCE.md` with proof (command, screenshot path, metadata link). Then print the final summary and the "YOU STILL NEED TO DO" list.

---

## 13. Compliance (Space Apps 2026) — verify on the official site and note any differences in the report

Submission closes **Nov 15, 2026, 11:59 PM local time**; demo = publicly viewable video up to 30 s or up to 7 slides; check team-size limit and legal terms.
Keep NASA/USGS credits, identifiers and versions. Check NASA media/3D usage guidelines for the models. Do not imply NASA endorsement. Do not use recognizable people's images or voices.

---

## 14. Stage report contract (`STAGE_X_REPORT.md`)

Files changed; data/asset sources with real success or failure (bytes loaded?); assumptions and decisions; commands run with exit codes and real output; screenshot paths;
known issues and precise failures; what was NOT verified; exact CMD commands to start everything from the project root.

BEGIN NOW WITH STAGE A AND CONTINUE THROUGH STAGE D WITHOUT WAITING.