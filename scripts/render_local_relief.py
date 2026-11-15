"""Render a north-up Atlas relief tile from the Jezero route mesh."""
from pathlib import Path
import json

import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[1]
data = root / "apps/web/public/data"
meta = json.loads((data / "terrain.json").read_text())
z = np.fromfile(data / "terrain-native.f32", dtype="<f4").reshape(209, 226)
dy, dx = meta["dy_m"] * 95 / 208, meta["dx_m"] * 95 / 225
south, east = np.gradient(z, dy, dx)
# Light falls from northwest, at 45 degrees of altitude.
norm = np.sqrt(1 + (2 * south)**2 + (2 * east)**2)
shade = np.clip((.707 + south + east) / norm, 0, 1)
lo, hi = np.percentile(z, [2, 98])
ramp = np.clip((z - lo) / (hi - lo), 0, 1)
low, high = np.array([81, 103, 119]), np.array([238, 214, 169])
pixels = (low + (high - low) * ramp[..., None]) * (.54 + .56 * shade[..., None])
Image.fromarray(pixels.clip(0, 255).astype("uint8")).save(data / "ctx-relief.png")
(data / "ctx-relief.json").write_text(json.dumps({"bounds":meta["bounds"], "shape":list(z.shape),
    "height_range_m":[float(z.min()),float(z.max())], "display_scale_m":[float(lo),float(hi)],
    "source":"USGS/NASA CTX Jezero DEM", "lighting":"Synthetic northwest hillshade, 2× vertical exaggeration"},indent=2))
