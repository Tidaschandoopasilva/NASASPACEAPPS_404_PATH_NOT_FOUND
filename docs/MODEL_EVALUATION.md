# 404-SVNet model evaluation

**Historical V1 report.** See [V2 evaluation](SVNET_V2_EVALUATION.md) for the retrained desktop model.

**Actual trained artifact; simulated labels on real NASA/USGS CTX terrain.**

700 scenarios / 2100 action records. Train 400, validation 100, calibration 100, test 100. Geographic quadrants and random seeds are disjoint. Three sibling action records never cross splits. Random scene windows can overlap within each split; uncertainty intervals are conditional on this single crop and simulator, not global geographic uncertainty.

| Policy | Utility | 95% CI | Completion | Return* | Abstain | Regret |
|---|---:|---|---:|---:|---:|---:|
| shortest-distance | -65.88 | -92.83 to -37.36 | 40% | 40% | 0% | 121.29 |
| risk-weighted-astar | 3.90 | -19.92 to 27.82 | 64% | 64% | 0% | 51.50 |
| always-scout | -56.32 | -79.04 to -34.49 | 49% | 49% | 0% | 111.73 |
| uncertainty-threshold | -58.31 | -81.43 to -34.60 | 47% | 47% | 0% | 113.72 |
| 404-SVNet | 40.52 | 29.11 to 53.66 | 54% | 100% | 46% | 14.89 |
| uncertainty-threshold-constrained | 14.97 | 0.02 to 29.21 | 47% | 96% | 49% | 40.44 |
| risk-astar-constrained | 49.82 | 36.71 to 63.69 | 64% | 100% | 36% | 5.59 |


*Human review/abstention starts no expedition, so return feasibility is counted as 1 with zero science, time and utility. Report completion and coverage alongside return. Constraint-matched baselines also refuse nominally infeasible actions. Raw forced baselines are retained for transparency.

The learned policy minus constraint-matched uncertainty heuristic averages **25.54** utility units (paired bootstrap 95% CI 13.91 to 38.88). The highest mean utility is **risk-astar-constrained**, not automatically the learned model. These results do not establish that SVNet is superior to strong model-free planning.

## Prediction checks

Return Brier score 0.0997; log loss 0.2972; ten-bin ECE 0.0586. Reliability bins are saved in evaluation.json and shown in the console. Brier mixes calibration and discrimination; it is not a safety certification. Success and return labels are identical in this v1 simulator, so those two classifier metrics coincide; they are not independent achievements.

Regression MAE: {"minutes": 8.816540836363748, "energy": 6.242974126080655, "science": 29.02049723297034}.

## Methods and limitations

Three scenario-bootstrap gradient-boosted models per output; two leaf-count candidates selected using validation loss. Logistic probability calibration uses only the separate calibration split. Test records are never loaded by the training script. Return threshold 0.8 and spread threshold 0.18 were fixed before test evaluation. Domain checks exclude features beyond the training min/max envelope plus 10% range tolerance. Ensemble spread is heuristic, not calibrated epistemic coverage.

The single binary hazard, friction consequences, delay, mission resource units, science values and sensor noise are ASSUMED/SIMULATED. Real input is CTX terrain geometry. Coverage fraction is an independent scenario assumption, not inferred rock safety. Candidate routes retain a full return leg. Hidden state is sampled only in sim/mission_outcomes.py; feature builders receive only public data. No raw-image neural model, reinforcement learning or operational astronaut safety system is claimed.

The 2,400-run legacy policy sweep is separate from this 700-scenario ML dataset. Do not combine their denominators.

## Files

- data/svnet/manifest.json: split/window/source-hash contract.
- data/svnet/scenarios.jsonl and rows.jsonl: public scenarios, logged labels and action features.
- models/svnet_v1/model.joblib and calibration.joblib: actual trained artifacts.
- models/svnet_v1/test_predictions.json: all 300 test action predictions and outcomes.
- models/svnet_v1/evaluation.json: policy rows and reproducible summary.

Only load the included trusted joblib artifacts; Python deserialization is not a general untrusted-model upload service.
