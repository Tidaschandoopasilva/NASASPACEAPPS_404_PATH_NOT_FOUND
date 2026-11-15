"""Export full-resolution terrain for display while preserving the planner grid."""
import math
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds

ROOT = Path(__file__).resolve().parents[1]
with rasterio.open(ROOT / 'data/jezero-ctx-crop.tif') as source:
    west, south, east, north = map(math.radians, [77.40, 18.42, 77.48, 18.49])
    radius = 3396190
    x_scale = radius * math.cos(math.radians(18.4663))
    width, height = 226, 209
    dx = (east-west)*x_scale/(width-1)
    dy = (north-south)*radius/(height-1)
    transform = from_bounds(west*x_scale-dx/2, south*radius-dy/2,
                            east*x_scale+dx/2, north*radius+dy/2, width, height)
    grid = np.full((height,width), np.nan, dtype='<f4')
    reproject(rasterio.band(source,1), grid, dst_transform=transform, dst_crs=source.crs,
              dst_nodata=np.nan, resampling=Resampling.bilinear)
    grid.tofile(ROOT / 'apps/web/public/data/terrain-native.f32')
