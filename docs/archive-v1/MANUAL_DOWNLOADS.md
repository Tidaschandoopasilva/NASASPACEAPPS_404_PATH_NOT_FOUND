# Manual data recovery

NASA imagery and GLBs are already included. No manual model download is required.

Real elevation remains unavailable. The verified source reference is the USGS Jezero CTX 20 m model, cited by the Caltech dataset at https://data.caltech.edu/records/h2xd4-zbd29 . Source URL:

https://planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/ScienceInvestigationMaps_JPL/M20_JezeroCrater_CTXDEM_20m.tif

Alternative catalog: https://www.usgs.gov/data/mars-2020-terrain-relative-navigation-hirise-dtm-mosaic

If the source is reachable on your connection, verify bounds, nodata, CRS, radius and download size (prefer a <=50 MB crop). Save to `data\real-dem.tif` and run:

```cmd
python scripts\process_dem.py --dem data\real-dem.tif
python -m pytest -q
npm run build
```

**Integration review still required:** update the source registry, conditional UI labels and experiment provenance after a successful real-raster import; verify imagery alignment against a landmark; rerun experiments and inspect the mesh. Current UI intentionally remains labelled synthetic. The current synthetic-specific API test should be revised only after verifying the new data state. Do not remove the synthetic warnings simply because a file exists.

Model catalog pages (for future refresh):
- https://science.nasa.gov/3d-resources/mars-2020-perseverance-rover/
- https://science.nasa.gov/3d-resources/astronaut/

Targets: `apps\web\public\models\rover.glb` and `astronaut.glb`. GLB loader attempts the real models and uses a primitive placeholder if loading fails. Credits still apply.
