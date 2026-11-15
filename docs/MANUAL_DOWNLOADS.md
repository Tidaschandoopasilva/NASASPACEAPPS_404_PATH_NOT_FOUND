# Cached resources and optional refresh

No manual NASA download is required for this V2 package. It contains the real CTX crop, NASA HiRISE image mosaic, two Mastcam-Z context photographs and both catalog GLBs. Real-data acquisition in V2 resolves the earlier elevation blocker.

```cmd
python scripts\download_dem.py
python scripts\process_dem.py --dem data\jezero-ctx-crop.tif
python scripts\download_data.py
python scripts\download_assets.py
```

Inspect resulting metadata and rerun tests/build after a refresh. The DEM script limits transferred bytes to 50 MiB and verifies byte ranges and TIFF layout. The original source GeoTIFF is larger than the transferred crop.

Photograph download URLs, source pages, Sol/camera information and hashes are in apps/web/public/photos/manifest.json. They are contextual images, not exact registered views of the proposed science targets.
