# Assumptions and units

All mission and hazard values below are ASSUMED, not NASA safety thresholds.

| Quantity | Value / interpretation |
|---|---|
| Sphere radius | 3,396,190 m; Mars equirectangular local frame |
| Synthetic working grid | 96 × 96, ROI 77.40–77.48 E / 18.42–18.49 N |
| Grid spacing | From projected angular extent on this sphere; synthetic fixture has no raster affine |
| Max traversable slope | 20 degrees; invalid and steep cells excluded |
| Walking speed | 1 m/s on flat; time multiplier 1 + 3 × slope / 20 |
| EVA budget / reserve | 180 minutes / 20%; return leg always included |
| Edge weights | distance 1; normalized squared slope 2; hazard 4; uncertainty 1 |
| Hazard prior outside corridors | clip(0.06 + 0.24 × (slope / 20)^2, 0.06, 0.6) |
| Three uncertain corridors | Ellipses defined in app/terrain.py; user prior overrides their cells |
| Slip means | safe 0.09748; hazardous 0.282915 |
| Slip observation | unbounded Gaussian research signal; sigma 0.08, threshold 0.20 |
| TPR / FPR | Gaussian tails give approximately 0.85 / 0.10 |
| Utility | science reward 200 for full route; 1 unit per route minute; 100 per hazardous corridor |
| Interactive VoS card | assumed detour 28 min; scout effort 5 + 3 min, user can change effort |
| Experiment detour | actual time difference between shortest route and a route excluding corridor 0 |
| Rover | kinematic approximation, wheel radius 0.2625 m; nominal mass 1025 kg, gravity 3.71 m/s² documented only, not used in kinematics |
| Rover trace | dt 0.5 s, 80 steps; straight local 16 m-command trace at 0.2 m/s, slope sampled at grid [47,42] |
| Animation | route-relative glyph motion over 30 seconds, not real time; model size enlarged |

The rover animation is illustrative, not driven by a full traversal dynamics trace. Its straight telemetry trace is a separate sanity demonstration. Sensor slip is a statistical observation, distinct from the kinematic friction slip. This release does not equate either with measured Jezero traction.

Unknown DEM cells are excluded. The synthetic test grid has no holes; tests explicitly inject holes. DEMs do not resolve all wheel-sized rocks. A credible mission planner needs reviewed geology, terrain and EVA performance models beyond this prototype.
