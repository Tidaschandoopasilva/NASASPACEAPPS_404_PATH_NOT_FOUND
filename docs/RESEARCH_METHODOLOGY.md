# Research methodology

1. Acquire real USGS/NASA CTX 20 m elevations with byte-range requests. Verify TIFF format, CRS, affine, pixel size, source XML and hash. Cache a 446×450 native-pixel crop; no raster is generated from image brightness.
2. Partition the native crop into northwest training, northeast validation, southwest calibration and southeast test regions, separated by a 12-pixel gap. Sample complete 64×64 windows at native steps 1/2/3 (effective 20/40/60 m). A window belongs to one region only.
3. Generate 400/100/100/100 graph-feasible scenarios with disjoint seed ranges. Exclude geometries with no initial route before sampling hidden outcomes; record exclusions. Each scenario has one binary uncertain corridor and complete science/return paths.
4. Randomize known assumptions (hazard prior, sensor sigma, science priority, resource and time budgets, scouting distance/cost). Generate shortest, avoidance and risk-weighted routes using only the public map/belief.
5. Sample one hidden hazard, delay, resource multiplier, failure event and noisy sensor observation per scenario. Reuse that world across actions. Features are built exclusively from public values; outcomes remain labels.
6. Fit 100-iteration histogram gradient-boosted classifiers/regressors. Select max-leaf-nodes 7 versus 15 on validation log loss + normalized time MAE. Bootstrap whole scenarios for two additional ensemble members, keeping action siblings together.
7. Fit logistic calibration on the independent calibration region. Return threshold 0.8, spread threshold 0.18 and domain tolerance were specified before test evaluation.
8. Evaluate the frozen pipeline on all 100 test scenarios / 300 actions. Compare forced baselines and constraint-matched baselines. Report completion, return, science, resource/time overhead, regret, abstention, Brier/log loss/ECE and paired bootstrap intervals.

The model uses outcome supervision, not LLM fine-tuning or RL. Hidden traction coefficients are not input features. Coverage probability is explicitly assumed and is distinct from DEM validity and hazard prior. Success and return labels coincide in this initial simulator; a richer abort/science model should separate them later.

CIs resample scenarios, never independent action rows. Geography within a quadrant can overlap, so these are conditional simulation intervals over one Mars crop. They do not establish broad geological generalization. Best-in-hindsight regret uses the four simulated route strategies plus no-launch utility 0. There is no guarantee the hindsight oracle resembles an available real-time policy.

References: NASA/USGS source registry; scikit-learn calibration guidance https://scikit-learn.org/stable/modules/calibration.html ; gradient boosting https://scikit-learn.org/stable/modules/ensemble.html . Model metadata pins the actually used version, 1.8.0, rather than assuming the online documentation version.
