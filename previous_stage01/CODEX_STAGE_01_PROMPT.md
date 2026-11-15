# STAGE 01 — CODEX PROMPT

You are implementing Stage 01 of the Team 404 NASA Space Apps Challenge 2026 project **404: PATH NOT FOUND — Scout or Skip**. Start in the current empty working directory. Implement the project, not a proposal. Work incrementally and run tests/builds before reporting completion.

Read `docs/PRODUCT_SPEC.md` and `docs/DATA_SOURCES.md` if present. If not present, create them with this brief: a georeferenced Jezero Crater Mars atlas integrating official NASA Mars Trek WMTS imagery, with later astronaut route planning and a Python rover simulation. Keep NASA observed data distinct from derived or simulated quantities.

## Scope — Stage 01 only

1. Scaffold `/frontend` using Vite + React + TypeScript, and `/backend` using Python FastAPI + Pydantic. Add a root README with Windows CMD/PowerShell setup and run commands, a gitignore, and `.env.example` for each app. Use only widely supported packages.
2. Implement a responsive, genuinely usable Mars mission-control shell using original Team 404 branding. Top bar: `404 / PATH NOT FOUND`, `Jezero Crater`, small `RESEARCH PROTOTYPE` designation. Left rail tabs `ATLAS`, `EXPEDITION`, `ROVER LAB`, `MISSION REWIND`; only ATLAS is functional for now, and other screens visibly say `Upcoming stage` rather than showing fake functionality. Main: real Mars map. Right inspector: selected layer, mission location, source, data classification, projection, coverage, scale and limitations. Dark colors: #0B111B, #172537, #D46D4B, #6CDDE2, #E9C994, #F1B85B. Accessible contrast, keyboard navigation, responsive layout.
3. Use **OpenLayers**, not Google Maps/Earth or default EPSG:3857 OpenStreetMap. Integrate at least one authentic NASA Mars Trek WMTS imagery layer for Jezero. Discover the correct GetCapabilities metadata, endpoint, style, matrix set, bounding box, image format, and Mars-specific projection. Start by trying `JEZ_hirise_soc_006_orthoMosaic_25cm_Eqc_latTs0_lon0_first_dd` from https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=mars . Implement WMTS correctly using native Mars coordinates and a suitable source-native projection. If CORS blocks direct tiles, implement a minimal *allowlisted* FastAPI tile proxy rather than an open URL fetcher. Do not invent endpoints. If the external service is unavailable, show a clear source-unavailable state, retain a diagnostic report in `docs/MAP_INTEGRATION.md` and do not substitute Earth tiles or an uncredited mock map.
4. Atlas interactions: pan/zoom, Mars coordinates on click, change layer if more than one verified WMTS source is available, toggle labels, click `Sources` to view a searchable source register. On-screen map must indicate `NASA data / observed` and display a link to the original source. No simulated values on this stage's map.
5. Backend endpoints: GET `/api/health`, GET `/api/sources`, and GET `/api/map/layers` returning typed JSON (actual source status). Only add a tile proxy if necessary; lock it to approved NASA host(s) and fixed layer/zoom constraints.
6. Store a machine-readable data provenance catalog in `/data/source_catalog.json`, including the five original links and both technical links from docs/DATA_SOURCES.md. Use classifications `primary_data`, `reference`, `inspiration`, `earth_only_not_mars`. Expose through `/api/sources`. Never state that ground photos are precisely geolocated if not verified.
7. Write smoke tests for FastAPI health/sources and a frontend build. Add `docs/MAP_INTEGRATION.md` with exact working endpoints, planet CRS, coverage, capabilities URL, and any remaining limitations. Add clear manual QA steps in README.

## Critical limitations
- No fake rover simulation, safe-route scores, habitat coordinates, or telemetry in Stage 01.
- No NASA logo or claim of NASA endorsement. Source attributions visible.
- Do not download enormous DEM files or use NASA Worldview as a Mars basemap.
- Avoid implementation of later stages now. Keep directory structure extensible.
- If the API or service fails, be explicit and preserve a runnable UI. Do not claim the Mars map is successfully connected unless it actually loads.

## Definition of done
- `npm run build` in frontend succeeds.
- Backend tests succeed.
- Frontend and FastAPI run locally with documented commands.
- Authentic Mars imagery appears in the map if service is accessible; otherwise UI visibly reports why not, with details in the integration log.
- Source register is present and accurate.
- Report final changed files, executed commands, test results, exact live data source, and unresolved blockers. Stop after Stage 01.
