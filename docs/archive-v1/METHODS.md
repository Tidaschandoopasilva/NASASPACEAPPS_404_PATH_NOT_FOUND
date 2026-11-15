# Methods

## Map

NASA Mars Trek capabilities supply the layer identifier, style, matrix identifier, tile size, degree-coordinate bounds and URL template. Matrix 13 is stitched into a 1024 × 896 RGBA texture. The map uses a custom Mars degree projection in OpenLayers, not Earth Web Mercator. Longitude is east-positive. The capabilities use `EPSG::104905`; we retain that string as supplied rather than assuming Earth EPSG:4326.

## Terrain

A real elevation endpoint could not be downloaded. `process_dem.py` therefore constructs a labelled deterministic synthetic test fixture. With `--dem`, it verifies a Mars radius in the raster CRS, reprojects into a sphere-centered equirectangular frame and preserves nodata. Output: heightmap.npy, 16-bit PNG (65535 invalid), JSON metadata and renderable terrain JSON. PNG offset and scale are in metadata. The import path has not been exercised with a genuine source raster in this environment.

## Planning

Eight-neighbor A* rejects invalid cells and cells above 20 degrees. Diagonal movement also requires valid adjacent cardinal cells, preventing corner cutting. Three-dimensional edge distance is weighted by slope, hazard belief and uncertainty. The heuristic is planar Euclidean distance in meters; all additional costs are nonnegative. Shortest mode retains physical constraints but omits risk penalties. Route H→A→B→H is rejected as budget-infeasible when its walking time exceeds 80% of the EVA budget. Candidate geometry remains visible with an explicit infeasible message.

## Beliefs and decision

The planner receives elevation, slope, validity, hazard probability and uncertainty arrays; it imports no simulator. Hidden Bernoulli states live in `sim/world.py`. A noisy slip observation updates one corridor with Bayes' rule. Replanning uses only its posterior. The UI decision card computes standard expected value of sample information for an explicitly assumed binary proceed/avoid decision (28-minute detour); it is an illustrative local decision model, not a full value-iteration solver over the three corridors. Deploy forces a scout diagnostic irrespective of that recommendation.

The interactive full-route replan and experimental policy comparison are separate documented calculations. The experiment derives detour minutes from candidate paths and tests one hidden corridor. It does not claim end-to-end rover scouting performance.

## Reproducibility

Experiment seeds 0–99 are fixed in code before outcome evaluation. Each seed's hidden state and sensor observation are shared across all three strategies. Two thousand bootstrap resamples of paired deltas use fixed seed 404. Raw JSONL and CSV records are included. No seed is removed after seeing results.
