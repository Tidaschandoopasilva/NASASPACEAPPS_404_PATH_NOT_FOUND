# TEAM 404 — DATA SOURCES & PROVENANCE

Project: **404: PATH NOT FOUND — Scout or Skip**
Event: NASA Space Apps Challenge 2026 — Interplanetary Survival Guide: Martian Map
Study site: Jezero Crater, Mars
Last source verification: 2026-11-14

## Mandatory source-provenance principles

- Real planetary imagery/DEM must be properly georeferenced and credited.
- Treat observed measurements, processed/derived fields, and simulated scenario values as separate classes of data.
- Do not label pre-recorded observations as live Mars conditions.
- Do not combine Mars and terrestrial coordinate systems (Earth EPSG:3857 etc.). Confirm projection, longitude convention, pixel spacing, extent, units, and no-data.
- Never fabricate citations, positions of rover images, NASA layers, measured uncertainties or mission outcomes.
- Do not imply endorsement by NASA. Record credits and use-permission/licensing per source.
- At least one NASA resource from the challenge Resources tab must appear in the actual project and final submission references to meet the organizer's Global Awards requirement.

## User-supplied NASA challenge resources

| ID | URL | Planned use | Status |
| --- | --- | --- | --- |
| NASA-MARS-TREK | https://trek.nasa.gov/mars/ | Official Mars mapping reference and Mars WMTS basemap | Primary, NASA challenge resource |
| USGS-MARS-MAPS | https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars | Discover mapping layers and geological context | Reference; confirm data services before use |
| CURIOSITY-MOUNT-SHARP | https://science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp/ | Inspiration for route depiction, science-label hierarchy | Design reference only; DIFFERENT SITE from Jezero |
| P2020-RAW-IMAGES | https://mars.nasa.gov/mars2020/multimedia/raw-images/ | Contextual ground-level Perseverance photographs | Primary; do not assume photos are spatially registered |
| EARTHDATA-WORLDVIEW | https://worldview.earthdata.nasa.gov/ | General interface inspiration | Earth data platform; NOT Mars layers |

## Additional technical sources

| ID | URL | Planned use |
| --- | --- | --- |
| MARS-TREK-WMTS | https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=mars | Discover WMTS layer metadata/capabilities and tile URLs; use native Martian projection |
| USGS-JEZERO-DEM | https://www.usgs.gov/data/mars-sample-return-hirise-mosaics-terrain-relative-navigation | HiRISE DEM and orthomosaic data; small site crop after checking native projection and license |
| CHALLENGE | https://www.spaceappschallenge.org/2026/challenges/interplanetary-survival-guide-martian-map/ | Official task scope |
| EVENT | https://www.spaceappschallenge.org/2026/ | 2026 event and timeline |

## Initial WMTS layer to investigate

Layer ID: `JEZ_hirise_soc_006_orthoMosaic_25cm_Eqc_latTs0_lon0_first_dd` (NASA Mars Trek — MRO HiRISE Jezero Controlled Mosaic)
Published bbox (lon/lat): approx 77.2229331, 18.3067994, 77.583964, 18.669315.
Use GetCapabilities to resolve the actual endpoint, style, matrix set, zoom identifiers, tile format, coverage and coordinate reference system. Do NOT invent URL templates without reading the corresponding capabilities document.

## Data model

Record: `id, title, agency, mission, instrument, url, retrieved_utc, source_type, crs, extent, units, resolution, licence_or_rights, processing_steps, known_limits, status`.

Classification `observed | derived | simulated` is required for every visualized layer or metric. Never equate map mosaic confidence with empirically calibrated terrain-traversal risk.

## Submission citation checklist

- Direct URL and provider for each NASA data source used
- Links to any scientific research or method used
- Licenses for imagery, code, iconography and third-party models
- AI/Codex assistance declared in project write-up as appropriate
- All simulated scenarios and unsupported assumptions labeled
