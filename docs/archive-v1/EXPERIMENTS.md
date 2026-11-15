# Paired-seed experiment results

**SIMULATED, synthetic test terrain.** No measured Mars safety or traction claims.

Single binary corridor, two precomputed routes; Gaussian slip sensor. Research sensitivity study, not Mars performance evidence.

Fixed seeds 0–99; 8 regimes × 100 seeds × 3 strategies = 2400 episodes. Utility = 200 − walking minutes − 100 × hazardous crossing − scout effort/time. The scout strategy is forced, even when expected information has negative value. Avoid excludes corridor 0. Other corridors affect path-cost beliefs but are not hidden hazards in this single-corridor experiment.

| Regime | Scout − proceed mean | Median | Bootstrap 95% CI | Scout mean utility |
|---|---:|---:|---|---:|
| baseline | 10.433 | -10.567 | 2.433 to 18.433 | 9.003 |
| expensive-scout | -54.567 | -75.567 | -62.567 to -46.567 | -55.997 |
| rare-hazard | -7.183 | -8.000 | -8.238 to -5.165 | 10.388 |
| common-hazard | 54.821 | 87.821 | 45.821 to 63.821 | 7.392 |
| noisy-sensor | 10.433 | -10.567 | 2.433 to 18.433 | 9.003 |
| no-uncertainty-penalty | 11.169 | -9.831 | 3.169 to 19.169 | 9.740 |
| flat-terrain | 7.574 | -8.000 | 0.948 to 14.735 | 60.766 |
| steeper-terrain | 16.991 | -4.009 | 8.991 to 24.991 | -39.307 |

Raw evidence: data/experiments/episodes.csv and episodes.jsonl. Frontend chart loads apps/web/public/data/experiments.json. Regimes fix prior, scout cost, sensor sigma, uncertainty weight and slope multiplier; see run_experiments.py for exact values. Flat terrain tests all-zero elevations; no-uncertainty uses w_u=0. The simulation always completes a planned route when graph-feasible; science completion is therefore 1 by construction, and safe_return only means no modelled binary hazard crossing. Experiments use a 600-minute route feasibility ceiling to isolate strategy costs; interactive EVA default is 180 minutes. No human health, oxygen or vehicle failure model is simulated.

Noise-regime outcomes may coincide when the policy chooses the same route for both possible observations; this is a property of this coarse decision model, not proof of sensor robustness. Uncertainty reduction can be negative for an individual surprising observation.

Fixed experiment itinerary: [78,22] → [30,34] → [42,72] → [78,22]. This is distinct from the shorter interactive default mission, so avoiding corridor 0 remains graph-feasible at every stop. An attempted run with interactive waypoints was infeasible because a science target lay inside the excluded corridor; it produced no valid episodes. The runner now explicitly rejects empty results without overwriting logs.
