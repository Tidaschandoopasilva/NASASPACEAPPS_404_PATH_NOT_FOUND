# Submission packet — review before publication

**Title:** 404: PATH NOT FOUND  
**Team:** Team 404  
**Research feature:** Scout or Skip  
**Challenge:** Interplanetary Survival Guide: Martian Map  
**Purpose:** Explore when a simulated rover's observations are worth their cost while planning a human Marswalk and return.

## Abstract

404: PATH NOT FOUND is a local research prototype that explores how a human Marswalk might use robotic scouting to reduce uncertainty before committing to a route. Its Atlas uses cached NASA Mars Trek HiRISE imagery of the Jezero landing region, with explicit source, coverage and resolution information. A linked three-dimensional simulation lets participants define a fictional habitat and two proposed science targets, compare shortest and risk-aware return routes, and reserve time for returning to base. The Scout or Skip demonstration uses a standard expected-value-of-information calculation, a seeded noisy slip observation and a Bayesian update. The route planner then recomputes a path from the updated belief without accessing hidden simulator hazards. Rewind exposes before-and-after routes, exports and paired-seed experiment results, including scenarios in which scouting is more expensive than proceeding. This build includes genuine NASA-catalog rover and astronaut models. Real elevation acquisition was blocked, so the 3D surface and experiment terrain are explicitly synthetic, and the exact geological membership of the science targets remains unverified. The project emphasizes traceable data and explainable decisions, rather than operational safety claims. It is an educational research simulator and is not validated for mission operations. Original code is open source, with AI assistance and third-party sources disclosed.

## NASA data actually used

NASA Mars Trek Jezero HiRISE controlled mosaic: 20 tiles acquired using published WMTS capabilities, cached for the Atlas. See DATA_SOURCES.md for exact layer, bounds, source IDs and effective resolution. NASA/JPL Perseverance GLB and DigitalSpace astronaut GLB distributed through NASA are used as visual models. USGS SIM 3464 motivates the science objectives; no mapped-unit overlay is claimed.

## Method and measured simulator results

A* over an 8-connected elevation grid; slope/validity constraints, risk and uncertainty penalties; round trip with a time reserve. Bayesian binary sensor updates are separate from hidden state. Standard expected value of sample information is used; no novelty claim for the equation.

2,400 synthetic episodes, 100 paired seeds for each of 8 regimes. Baseline mean scout−proceed utility: 10.433; expensive-scout: -54.567. These are assumed-model results, not evidence of safety on Mars. Full uncertainty intervals and raw records are in EXPERIMENTS.md.

## Limitations / outstanding gate

Real DEM acquisition blocked; elevation synthetic. Science target unit membership unverified. Browser QA and screenshots blocked by preview infrastructure. Rover telemetry is a simplified local trace, with illustrative 3D traversal. No operational EVA or traction validation. Full Stage D acceptance is not met. Review ACCEPTANCE.md; do not present this package as all-MUST-complete.

## Tools, rights and AI

React, TypeScript, Vite, Three.js, React Three Fiber/Drei, OpenLayers, Recharts; Python, FastAPI, Pydantic, NumPy, Pillow, Rasterio and pytest. Exact resolved frontend versions: package-lock.json; build environment versions: evidence/versions.json. Original code Apache-2.0; imagery and models retain source terms. See NOTICE.

## Links to fill in manually

- Public repository: [ADD PUBLIC REPOSITORY URL]
- Public <=30-second video or <=7-slide presentation: [ADD DEMO URL]
- Public app, if hosting separately: [OPTIONAL; current app runs locally]
- Team project page: [ADD TEAM PAGE]

## Official-site checks, 2026-11-14

https://www.spaceappschallenge.org/2026/ states a maximum of 6 participants and submission close on November 15, 2026 at 11:59 PM local time. For Sri Lanka, use Asia/Colombo local time. Official NASA discussion: https://github.com/nasa/spaceapps/discussions/1973 describes <=30 seconds or <=7 slides. Terms: https://www.spaceappschallenge.org/legal/ require open/free original work and source attribution. Review the portal's current submission guide directly before submission; no portal actions were taken.

## YOU STILL NEED TO DO

- Run the Windows setup/start scripts and inspect the app; browser QA was blocked here.
- Resolve the real DEM / precise geology work if claiming full real-terrain acceptance.
- Capture actual screenshots and record/upload the public demo, or prepare <=7 slides.
- Submit through the Space Apps portal before the applicable local deadline.
