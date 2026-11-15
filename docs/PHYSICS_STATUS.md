# Physics status — not validated

Fast seeded kinematic/slip tests and mission outcome generation ran. PyBullet did not install in this environment:

1. Default source installation failed because clang++ was unavailable.
2. Binary-only PyBullet 3.2.7 had no compatible wheel for the supplied Python runtime.
3. Retrying compilation with gcc/g++ failed at NumPy C-API pointer compatibility.

No physics result file was fabricated. `research/validate_physics.py` is an optional executable 30-case stress test for a compatible PyBullet installation. It builds a six-wheel rigid chassis, uses Mars gravity 3.71 m/s², and derives a constant incline from each held-out route's mean slope. It is not an articulated rocker-bogie, a full DEM replay, or a Perseverance digital twin. Even if it runs locally, its output alone does not validate learned mission probabilities.

The current 3D rover uses the real NASA catalog GLB as a visual model, with neutral materials and body movement. Displayed animation is not a dynamics solution. This limitation does not prevent use of the trained CPU model and real-data map.
