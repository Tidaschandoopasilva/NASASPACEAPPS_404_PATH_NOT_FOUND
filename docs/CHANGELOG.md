# V2 — 2026-11-14

Real CTX elevation, NASA photo cards, trained/calibrated 404-SVNet, spatially separated data pipeline, independent baseline evaluation, model console and live route application. Physics and browser limits explicitly retained.

# Changelog

## 1.0.0 — 2026-11-14

- New React/TypeScript local app with Atlas, Mission 3D, Scout or Skip and Rewind.
- Cached 20 real NASA HiRISE WMTS tiles; downloaded catalog rover and astronaut GLBs.
- Added synthetic elevation fallback with explicit labels and a genuine-raster import pipeline.
- Implemented A* loop routing, time reserve, corridor beliefs, seeded scout observation and replan.
- Added 2,400-episode paired-seed sensitivity study and raw logs, replay, exports and source drawer.
- Added Windows setup/start scripts, tests, license, source provenance and submission draft.
- Known blockers: real DEM, exact mapped geology at stops and browser evidence. Full acceptance gate not passed.
