# Data sources and provenance

Acquisition / verification date: 2026-11-14. No Earth map projection is used. All sources retain their own rights.

## Jezero HiRISE controlled mosaic

- ID: `nasa-trek-hirise`
- Owner: NASA/JPL/USGS
- URL: https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=mars
- Status: **USED / OBSERVED**
- Use: 20 WMTS tiles acquired 2026-11-14 from published capabilities. ROI 77.40–77.48 E, 18.42–18.49 N; matrix 13. Texture cached locally. Effective WMTS sample spacing about 5.09 m; 0.25 m source product is not the rendered resolution.

## Jezero CTX 20 m elevation model

- ID: `usgs-ctx-dem`
- Owner: USGS Astrogeology
- URL: https://planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/ScienceInvestigationMaps_JPL/M20_JezeroCrater_CTXDEM_20m.tif
- Status: **UNAVAILABLE / NOT USED**
- Use: Direct endpoint returned 403; Astropedia mirror returned 503. No real elevation raster is included. Import tool provided.

## Geologic map of Jezero and Nili Planum

- ID: `usgs-geology`
- Owner: Sun & Stack / USGS, 2020
- URL: https://pubs.usgs.gov/publication/sim3464
- Status: **USED / CONTEXT ONLY**
- Use: Geological motivation for sedimentary and crater-floor investigations. Proposed waypoints have not been intersected with mapped units; they are assumed study targets.

## Mars 2020 Perseverance rover

- ID: `rover-model`
- Owner: NASA / Jet Propulsion Laboratory
- URL: https://science.nasa.gov/3d-resources/mars-2020-perseverance-rover/
- Status: **USED / 3D ASSET**
- Use: Original GLB downloaded; all materials replaced with neutral material at rendering to remove texture-based insignia. Animation is kinematic, with enlarged character scale.

## Astronaut

- ID: `astronaut-model`
- Owner: DigitalSpace Corporation via NASA
- URL: https://science.nasa.gov/3d-resources/astronaut/
- Status: **USED / 3D ASSET**
- Use: Static GLB with procedural bob/sway, not a biomechanics rig. All textured materials replaced in renderer.

## Perseverance raw images

- ID: `raw-photos`
- Owner: NASA/JPL-Caltech
- URL: https://mars.nasa.gov/mars2020/multimedia/raw-images/
- Status: **NOT USED**
- Use: Ground photo cards deferred; no inferred georeferencing.

## NASA Worldview

- ID: `worldview`
- Owner: NASA Earthdata
- URL: https://worldview.earthdata.nasa.gov/
- Status: **NOT USED**
- Use: Earth imagery; not a Mars basemap.

## Curiosity Mount Sharp route

- ID: `curiosity-reference`
- Owner: NASA
- URL: https://science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp/
- Status: **REFERENCE ONLY / NOT USED AS DATA**
- Use: A different landing site; not Jezero terrain.

## Cached NASA WMTS metadata

```json
{
  "id": "nasa-trek-hirise",
  "source_ids": [
    "nasa-trek-hirise"
  ],
  "data_state": "OBSERVED",
  "bounds": [
    77.4,
    18.42,
    77.48,
    18.49
  ],
  "coordinate_system": "urn:ogc:def:crs:EPSG::104905",
  "layer_id": "JEZ_hirise_soc_006_orthoMosaic_25cm_Eqc_latTs0_lon0_first_dd",
  "matrix": "13",
  "tile_size": [
    256,
    256
  ],
  "acquired": "2026-11-14",
  "credit": "NASA/JPL/USGS, MRO HiRISE; Mars Trek",
  "effective_resolution_degrees": [
    8.58306884765625e-05,
    8.58306884765625e-05
  ]
}
```

Cache: `apps/web/public/data/imagery.png`; full exact tile request list/byte counts: `data/imagery-metadata.json`; capabilities snapshot: `data/wmts-capabilities.xml`. Native product: 25 cm/pixel, but acquired WMTS samples are about 5.09 m (sphere equirectangular). Display texture is resampled to roughly 4.63 m horizontally; this does not add detail. Capabilities coverage: 77.2229331–77.583964 E, 18.3067994–18.669315 N. ROI lies within that envelope; cached texture visually inspected.

## DEM status

No acquired raster, so acquisition date/bounds/projection/resolution/rights cannot be claimed from a downloaded DEM. Candidate CTX model source is documented in MANUAL_DOWNLOADS.md. Synthetic fallback metadata has no native raster transform and is SIMULATED. `heightmap.npy`, `metadata.json` and the 16-bit PNG correspond only to this fixture.

## Usage terms

NASA media usage: https://www.nasa.gov/nasa-brand-center/images-and-media/ . NASA 3D repository states the model assets are free and without copyright; see model-terms.txt and public/models/CREDITS.md. USGS geological map attribution: Sun, V.Z., and Stack, K.M., 2020, SIM 3464, DOI 10.3133/sim3464. No geological polygon file is redistributed. The USGS 2020 HiRISE DEM catalog lists CC0, but that dataset was not acquired or used.
