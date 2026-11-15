# TEAM 404 — PRODUCT SPEC V1.0

## Concept
**404: PATH NOT FOUND** — an evidence-aware Marswalk planning platform.
Main NASA deliverable: an interactive map of a specific Martian study location (Jezero Crater) integrating real NASA mission datasets, real science targets, and planned astronaut excursions.
Research feature: **Scout or Skip**, evaluating when a rover scout's observations can improve the value of an astronaut expedition versus proceeding directly or avoiding terrain.

## Experience
1. Select Mars study region and see truthful source provenance.
2. Explore NASA optical and elevation layers; inspect map coordinates and known-data coverage.
3. Choose hypothetical habitat and 2-3 science objectives, distinguished from observed rover targets.
4. Compute an outbound + return EVA route and compare modeled tradeoffs.
5. Identify high-uncertainty segment and run a *simulated* rover scout (Python dynamics).
6. Replan based on simulated observations and compare policies under repeated controlled trials.
7. Export findings, assumptions, data citations and a replayable experiment record.

## Product screens
- **ATLAS:** A real, correctly projected Mars map; layers, location, provenance, no-data labels.
- **EXPEDITION:** Habitat, science targets, outgoing/return routes, resource envelope, route explanations.
- **ROVER LAB:** Six-wheel rover-inspired Python simulation (not a flight-grade Perseverance digital twin), environmental controls and telemetry.
- **MISSION REWIND:** Compare Proceed / Scout / Avoid, replay policy experiments, metrics and assumptions.

## Design language
Identity: `404 / PATH NOT FOUND`, original brand (no NASA logos).
Colors: void #0B111B, panel #172537, rust #D46D4B, telemetry #6CDDE2, sand #E9C994, warning #F1B85B, white #F1F6FA.
Typography: Space Grotesk + IBM Plex Mono (with accessible fallbacks).
Dark command-console aesthetic, calm restrained motion, source chips, route legends and accessibility.
Responsive: Desktop split-pane map, tablet single-panel map with drawers, mobile simplified dashboard.

## Research constraints
- Safety estimates are model outputs, not verified astronaut safety assurances.
- Mars orbit imagery lacks the resolution to resolve all rocks/hazards and should not be claimed otherwise.
- Use separate simulation truth versus inferred hazard belief in experiments.
- Value-of-information mathematics is established; novelty must come from the evaluated Marswalk workflow and tested integration, not the equation alone.

## Software
Frontend: Vite, React, TypeScript, OpenLayers, lightweight CSS or Tailwind.
Backend: Python FastAPI, Pydantic; later NumPy, SciPy, rasterio, PyBullet, Gymnasium.
Map: NASA Mars Trek WMTS / verified Mars CRS; optional backend tile proxy if required by CORS.
No Earth basemap fallback. No fake NASA photos or magic metrics.

## Timeline
Stage 01 foundation + real Martian map; 02 DEM terrain; 03 route planning; 04 uncertainty; 05 rover physics; 06 research replay; 07 evaluation and submission.
