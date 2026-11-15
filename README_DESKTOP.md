# 404: PATH NOT FOUND — Mars Habitat V7 Desktop

This release uses the original Jezero 2D Atlas and interactive Mission 3D renderer inside a desktop window owned by Python. FastAPI serves the bundled assets and computes expedition plans on loopback. Three.js, OpenLayers and React are included as built local assets. The desktop does not need Node.js, an external browser, internet maps, or a cloud backend at runtime.

## Windows

1. Extract the ZIP. Use 64-bit Python 3.11 or 3.12 and Microsoft Edge WebView2 Runtime.
2. Double-click **setup_desktop.bat** once. This installs the Python packages. If the habitat is already offline, bring a wheelhouse prepared on a connected Windows computer with the same Python version. Run `py -3 -m pip download --only-binary=:all: -r requirements-desktop.txt -d wheelhouse` there, then place that directory beside the batch file.
3. Double-click **start_desktop.bat**. Use the native window. The standard ZIP contains the app and Mars assets. Python packages and WebView2 are system prerequisites.

For a separate campaign database, set `MARS_HABITAT_DB` before launch. By default the database is `MarsHabitat/desktop.sqlite3` in the user home directory.

## Run the campaign

- **Atlas:** select a sector or click a custom circle. Switch between locally bundled NASA map layers, including the Jezero panorama and infrared views.
- **Mission 3D:** choose the crew and rover science goals, load, weather, and EVA time. Click **Run expedition**. The system fits required gear, checks feasibility, and begins playback. Open **Optional kit and plan review** to inspect a draft before launch. Use orbit, asset follow, zoom, terrain overlays, playback speed, and the timeline to inspect the simulated scout, rover and astronaut pair.
- **Habitat campaign panel:** see the remaining supplies and the estimated expedition usage. Expand **Why routes were passed over** for alternative route, target, and resource decisions. When live playback reaches the end, it saves and debits supplies automatically. Scrubbing and replaying archives do not debit supplies. Replaying an archived expedition does not debit it again.
- The crew works toward **120 recorded expeditions with an EVA**. Each expedition can include multiple EVAs plus a separate rover loop. The persistent ledger records plans, inventory, and playback reports. Record rover/UAV-only expeditions to debit their usage and retain their data. Choose subsequent sectors and objectives in the dashboard.
- **Scout or Skip**, **Rewind**, and **404-SVNet** remain research views. They demonstrate the V2.1 decision experiment and its evaluation. Research episodes are separate from campaign accounting.

All crew resource values and field reports are simulation assumptions. Oxygen and water draw estimates increase with time and load. Suit and kit power are estimated from elapsed sortie time. Robot battery use is estimated from UAV and rover route length. The reserves and resource settings are not validated for life-support operations.

For a first demo, select a circle just northeast of the fixed habitat, use about **850 m** radius and **Clear day**, and start the survey. Watch **Simulated field readings** during the EVA. Then preview an alternative route, record the expedition, and run one habitat sol to see base supplies change.

## Crew terminals on a trusted LAN

From Command Prompt on the habitat, run `start_desktop.bat --listen-lan 192.168.1.10`, substituting the habitat's LAN address. The title bar displays the session code. On a crew device, use Python and a copy of `crew_link.py`:

```cmd
py -3 crew_link.py 192.168.1.10 --watch
```

Enter the session code. Watch mode retrieves the current simulated crew and asset positions, consumption, and observations once a second. Omit --watch for one snapshot. The server reveals UAV and rover observations as playback reaches them. The GUI and API remain local to the habitat. TCP port 4040 serves a read-only JSON Lines protocol, using plaintext on a trusted isolated network.

## Live crew and habitat telemetry

The playback cursor advances a simulated mission clock and publishes a snapshot. Crew usage follows the actual replayed EVA segment and the time assigned to its edges and science stops, including exits and retries. The field HUD shows the estimated per-sortie pack remaining while the crew is out, and projected stock at the end. Scrubbing reconstructs readings for the selected point. Recording commits the full debit exactly once. The estimates model the astronaut pair together. They are not individual biometrics, and the simulated clock is approximate.

At base, **Advance ¼ sol** advances one quarter of a 1,479.6-minute sol. **Run 1 habitat sol** plays through four quarters, debiting each as it completes. Each quarter consumes 28 L-equivalent of oxygen, 1.25 L of water, and 540 Wh of habitat power. A reserve breach stops further advancement. Habitat cycles are stored in the same SQLite campaign ledger. Expedition transit and idle habitat consumption are separate accounting phases. There are no simulated recharges or resupply in this release.

Use **Why routes were passed over** to preview candidate routes in purple and compare risk, distance, reachability and resource rejection reasons. The deterministic **Decision assistant** explains the planner's outcomes. The **Mission Q&A** panel answers questions about preflight.

## Why this planner

The terrain search uses Dijkstra on the measured CTX mesh after EVA and rover slope checks and the crew risk screen. The first UAV footprint includes the full science circle and a tapered approach. The search widens if too few ground cells are reachable. Several risk/distance trade-offs and target orderings generate candidate routes. The planner prioritizes more visits, then ranks competing routes by modeled tail loss and distance. Per-sortie oxygen, water, suit power and kit power can tighten the time budget before planning. The final resource gate checks campaign stock across all sorties and assets before recording. The resource gate holds an over-budget expedition so the operator can revise the plan. It does not optimize a multi-resource campaign itinerary across all future expeditions.

See the bundled methods, data sources, and model evaluation documentation for the original terrain pipeline and research experiments. The aircraft, rover and field events are simulated from terrain and scenario settings. Their displayed movements replay the computed plan locally.

## Retrained SVNet

The desktop loads SVNet V2. Its training cohort increased from 400 to 1,600 scenarios. The [paired evaluation](docs/SVNET_V2_EVALUATION.md) compares both models on 300 identical held-out cases and reports the trade-off between probability error and decision utility. The **Decision assistant** in the mission HUD uses explicit offline rules independently of SVNet.


## V5 preflight and equipment

The expedition counter changes when live playback finishes and saves automatically. An analysis creates a draft with zero resource debit. A launched draft can be resumed after restart. Use **Resume unrecorded expedition** when a draft exists or explicitly discard it before planning another. Playback and telemetry can be scrubbed, but the committed ledger debits each recorded expedition once.

| Scenario | Assumed ambient | Required kit | Added EVA power draw for the pair |
| --- | ---: | --- | ---: |
| Clear day | −20 °C | — | 0 Wh/min |
| Cold night | −75 °C | Suit heater | 1.6 Wh/min |
| Sun-exposed heat | +8 °C | Cooling pack | 2.4 Wh/min |
| Dust haze | −35 °C | Navigation beacon | 0.6 Wh/min |

These scenario values are editable simulation assumptions in `app/environment.py`. Sun-exposed heat models an increased suit workload, including a 35% hydration multiplier. Equipment adds mass to the walking calculation. Required items must be selected before launching. Selected equipment activates in the matching environment during EVA. A colored pack appears on the astronauts while it is active. The effective sortie budget and telemetry include the added battery draw. Scenario temperatures are not live readings or operational suit limits. The API defaults to fitting required equipment when older clients omit the equipment field.

## Atlas outcomes and local relief

**Local relief · CTX DEM** displays north-up hillshade from the exact Jezero elevation mesh used for routing. The lighting is derived from local slope. **Regional context · MOLA / HRSC** remains the broad comparison layer. The two represent different resolutions. Render the CTX image again with `python scripts/render_local_relief.py`.

Choose **Campaign survey outcomes** in Atlas, or overlay **Recorded campaign sectors** on HiRISE, CTX, infrared or local relief. Hover a sector for the source expedition, reason, coverage, and peak risk. The backend groups recorded estimates into a 16 × 16 sector grid. Red marks a simulated closure or at least 20% EVA-excluded surveyed cells. Amber marks pending targets, less than 35% coverage, or isolated exclusion. Blue marks a recorded ground visit in a sector that passes those screens. Green marks modeled passability without a recorded ground visit. Ground markers and category labels describe the simulation. A historical red sector remains flagged until a later recorded ground visit covers at least 85% of that sector and passes the screens. Existing V4 records with hazard rasters are migrated on first open.

## Mission Q&A

Analyze the mesh and ask a question in the preflight panel. The bundled offline classifier uses word and character TF-IDF with logistic regression. It was fitted on 144 authored example questions across 16 topics. A further 48 authored phrasings were held out from training. The resulting intent accuracy measures this dataset only. Low-confidence questions show supported topics.

Answers use the active draft's equipment, estimates, and route comparisons. A held preflight can explain its reported holds and required gear. All replies are generated from checked application values and authored response logic. The model does not control dispatch. The packaged Python environment loads it directly via the existing scikit-learn dependency.

Training examples and evaluation are under `models/mission_qa`. Run `python scripts/train_mission_qa.py` to reproduce the fit.

## V7 Jezero weather and campaign starting behavior

**Run expedition** builds a new plan from the selected area. A successful new plan supersedes the unfinished draft without debiting it. Resume in Mission Control is an explicit action. Recorded expeditions remain available in Campaign replay.

The Jezero weather panel opens offline with NASA Perseverance MEDA temperature pairs for sols 1130–1133, from the public NASA Mars 2020 weather feed. Refresh NASA archive is optional and requires connectivity. The app displays the Earth acquisition date and archive age. An unsuccessful refresh leaves the previous readings available. Historical results support scenario replay and stress testing.

The model estimates low and high temperatures separately. It takes the median pairwise temperature slope per sol (Theil–Sen), clips it to ±8 °C/sol, fits a median intercept and extrapolates one sol. It reports max(4 °C, 1.4826 × median absolute residual) as a heuristic spread. The lower edge at or below −70 °C suggests cold-night simulation; the upper edge at or above 0 °C suggests heat simulation. Selecting the recommendation uses the simulator’s gear and resource rules. The spread is not a confidence interval. Rover temperature is local and does not establish a crater-wide forecast. No measured values imply crew safety.

Odyssey THEMIS and MRO HiRISE/CTX remain bundled map context. This release does not subscribe to satellites or ingest raw orbital products automatically. To add regional evidence from an orbital archive, create a small JSON file with instrument (Odyssey THEMIS, MRO MARCI or MRO MCS), product (archive identifier), date (YYYY-MM-DD), bounds ([south, west, north, east] with east-positive longitude), and dust_flag (true/false). Run `python -m app.weather observation.json` in the desktop Python environment and reopen the panel. The app checks Jezero footprint and age. A MARCI/MCS dust flag within three Earth days takes priority as a dust **simulation suggestion**. It is an operator interpretation, not automatic dust detection. THEMIS infrared browse pixels do not estimate air temperature.
