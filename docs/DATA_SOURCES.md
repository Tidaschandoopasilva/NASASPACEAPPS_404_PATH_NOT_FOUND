# Source registry — V2

Acquired/verified 2026-11-14. Real observations and simulated labels are distinguished throughout.

## Jezero HiRISE controlled mosaic

ID `nasa-trek-hirise` · **USED / OBSERVED** · NASA/JPL/USGS

https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=mars

20 WMTS tiles acquired 2026-11-14 from published capabilities. ROI 77.40–77.48 E, 18.42–18.49 N; matrix 13. Texture cached locally. Effective WMTS sample spacing about 5.09 m; 0.25 m source product is not the rendered resolution.

## Jezero CTX 20 m elevation model

ID `usgs-ctx-dem` · **USED / OBSERVED + DERIVED** · USGS Astrogeology

https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/mars2020_trn/CTX/ScienceInvestigationMaps_JPL/M20_JezeroCrater_CTXDEM_20m.tif

USGS/NASA CTX 20 m DEM acquired by bounded HTTP range requests (8,015,040 bytes). Cropped GeoTIFF drives the 3D terrain, slopes, A* and SVNet scenarios. Native Mars sphere, equirectangular standard parallel 18.4663 degrees; planetocentric/east-positive. UI resampled to about 47.35 × 43.68 m.

## Geologic map of Jezero and Nili Planum

ID `usgs-geology` · **USED / CONTEXT ONLY** · Sun & Stack / USGS, 2020

https://pubs.usgs.gov/publication/sim3464

Geological motivation for sedimentary and crater-floor investigations. Proposed waypoints have not been intersected with mapped units; they are assumed study targets.

## Mars 2020 Perseverance rover

ID `rover-model` · **USED / 3D ASSET** · NASA / Jet Propulsion Laboratory

https://science.nasa.gov/3d-resources/mars-2020-perseverance-rover/

Original GLB downloaded; all materials replaced with neutral material at rendering to remove texture-based insignia. Animation is kinematic, with enlarged character scale.

## Astronaut

ID `astronaut-model` · **USED / 3D ASSET** · DigitalSpace Corporation via NASA

https://science.nasa.gov/3d-resources/astronaut/

Static GLB with procedural bob/sway, not a biomechanics rig. All textured materials replaced in renderer.

## Perseverance Mastcam-Z regional context

ID `raw-photos` · **USED / OBSERVED CONTEXT** · NASA/JPL-Caltech

https://science.nasa.gov/resource/perseverance-view-of-the-delta-in-jezero-crater/

NASA products PIA24485 (Sol 4) and PIA25212 (Sol 406) cached on science cards. Regional context only; not registered to proposed stop coordinates.

## NASA Worldview

ID `worldview` · **NOT USED** · NASA Earthdata

https://worldview.earthdata.nasa.gov/

Earth imagery; not a Mars basemap.

## Curiosity Mount Sharp route

ID `curiosity-reference` · **REFERENCE ONLY / NOT USED AS DATA** · NASA

https://science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp/

A different landing site; not Jezero terrain.

## 404-SVNet v1.0 trained models

ID `404-svnet` · **TRAINED / SIMULATED LABELS** · Team 404 / simulation research

https://scikit-learn.org/stable/modules/ensemble.html

Three-member gradient-boosted ensemble, 31 public pre-action features; separate spatial train, validation, calibration and test regions. No real astronaut safety outcomes.

## Actual DEM acquisition

```json
{
  "id": "usgs-ctx-dem",
  "url": "https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/mars2020_trn/CTX/ScienceInvestigationMaps_JPL/M20_JezeroCrater_CTXDEM_20m.tif",
  "acquired": "2026-11-14",
  "owner": "USGS / NASA MRO CTX",
  "source_ids": [
    "usgs-ctx-dem"
  ],
  "data_state": "OBSERVED",
  "native_crs": "PROJCS[\"Jezero_Crater_Projection\",GEOGCS[\"GCS_Mars_2000_Sphere\",DATUM[\"Mars_2000_(Sphere)\",SPHEROID[\"Mars_2000_Sphere\",3396190,0]],PRIMEM[\"Reference_Meridian\",0],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]]],PROJECTION[\"Equirectangular\"],PARAMETER[\"standard_parallel_1\",18.4663],PARAMETER[\"central_meridian\",0],PARAMETER[\"false_easting\",0],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"Easting\",EAST],AXIS[\"Northing\",NORTH]]",
  "native_affine": [
    20.0,
    0.0,
    4328999.999999998,
    0.0,
    -20.0,
    1143420.0000000028,
    0.0,
    0.0,
    1.0
  ],
  "native_resolution_m": [
    20,
    20
  ],
  "source_shape": [
    5067,
    4456
  ],
  "window": [
    1019,
    2252,
    450,
    446
  ],
  "requested_bounds": [
    77.36,
    18.38,
    77.52,
    18.53
  ],
  "crop_transform": [
    20.0,
    0.0,
    4349379.999999998,
    0.0,
    -20.0,
    1098380.0000000028,
    0.0,
    0.0,
    1.0
  ],
  "downloaded_bytes": 8015040,
  "crop_bytes": 640983,
  "sha256": "c5c4368c9fabdbb81233d6c0c565bfe1eaf5ffcb3160d0997426ce6e089758e5",
  "nodata": -3.4028234663852886e+38,
  "method": "HTTP byte ranges; verified TIFF strip layout; pixel values copied without resampling"
}
```

The original TIFF is 90,345,300 bytes; only 8,015,040 bytes were requested. Cropped TIFF: 640,983 bytes. Native pixel values are copied from verified uncompressed strips. Source XML is in data/ctx-source.xml, documenting 20 m pixels, standard parallel 18.4663°, Mars sphere radius 3,396,190 m, planetocentric latitude and positive-east longitude. The crop covers the requested 77.36–77.52 E, 18.38–18.53 N envelope, rounded outward to native pixels.

UI ROI is 77.40–77.48 E, 18.42–18.49 N, resampled to 96×96. Working spacing: 47.3454 × 43.6761 meters. Native transform and output PNG scale/nodata are recorded in data/metadata.json. No vertical-datum equivalence beyond the source metadata is asserted; visual terrain heights are relative to crop minimum.

The HiRISE matrix-13 WMTS texture is also cached locally. It is not native 25 cm sampling; see data/imagery-metadata.json for the effective acquired resolution. Both layers are mapped to the same planetary bounds. A contour alignment figure was visually inspected (docs/evidence/dem-alignment-v2.png); this is not subpixel co-registration validation.

## Ground photos

- PIA24485: Delta remnant from the landing site, Sol 4, Mastcam-Z, 2021-02-22. NASA/JPL-Caltech/ASU/MSSS. https://science.nasa.gov/resource/perseverance-view-of-the-delta-in-jezero-crater/ Cached 2,264,934 bytes; spatial context only.
- PIA25212: Jezero delta panorama, Sol 406, Mastcam-Z, 2022-04-11. NASA/JPL-Caltech/ASU/MSSS. https://science.nasa.gov/resource/jezero-craters-delta-is-getting-closer/ Cached 78,513 bytes; spatial context only.

## Rights

NASA imagery/media guidelines: https://www.nasa.gov/nasa-brand-center/images-and-media/ . USGS data source ownership retained, with source XML and attribution. NASA catalog 3D files retain original authors; see apps/web/public/models/CREDITS.md and docs/model-terms.txt. Open-source code/model artifacts are Apache-2.0; third-party assets are not relicensed. No NASA endorsement.
