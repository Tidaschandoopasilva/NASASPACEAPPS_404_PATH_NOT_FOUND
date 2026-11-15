"""Regenerate human-readable evaluation and model card from real artifacts."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.terrain import ROOT

def main():
    folder=ROOT/'models/svnet_v1';m=json.loads((folder/'metadata.json').read_text());e=json.loads((folder/'evaluation.json').read_text());manifest=json.loads((ROOT/'data/svnet/manifest.json').read_text())
    table='| Policy | Utility | 95% CI | Completion | Return* | Abstain | Regret |\n|---|---:|---|---:|---:|---:|---:|\n'
    for p in e['policies']:table+=f"| {p['policy']} | {p['utility']:.2f} | {p['utility_ci95'][0]:.2f} to {p['utility_ci95'][1]:.2f} | {p['success']:.0%} | {p['return_feasible']:.0%} | {p['abstained']:.0%} | {p['regret']:.2f} |\n"
    delta=e['paired_vs_uncertainty_threshold'];cal=e['calibration']['return_feasible'];best=max(e['policies'],key=lambda p:p['utility'])
    text=f'''# 404-SVNet model evaluation

**Actual trained artifact; simulated labels on real NASA/USGS CTX terrain.**

{manifest['scenarios']} scenarios / {manifest['action_rows']} action records. Train 400, validation 100, calibration 100, test 100. Geographic quadrants and random seeds are disjoint. Three sibling action records never cross splits. Random scene windows can overlap within each split; uncertainty intervals are conditional on this single crop and simulator, not global geographic uncertainty.

{table}

*Human review/abstention starts no expedition, so return feasibility is counted as 1 with zero science, time and utility. Report completion and coverage alongside return. Constraint-matched baselines also refuse nominally infeasible actions. Raw forced baselines are retained for transparency.

The learned policy minus constraint-matched uncertainty heuristic averages **{delta['mean_delta']:.2f}** utility units (paired bootstrap 95% CI {delta['ci95'][0]:.2f} to {delta['ci95'][1]:.2f}). The highest mean utility is **{best['policy']}**, not automatically the learned model. These results do not establish that SVNet is superior to strong model-free planning.

## Prediction checks

Return Brier score {cal['brier_score']:.4f}; log loss {cal['log_loss']:.4f}; ten-bin ECE {cal['ece10']:.4f}. Reliability bins are saved in evaluation.json and shown in the console. Brier mixes calibration and discrimination; it is not a safety certification. Success and return labels are identical in this v1 simulator, so those two classifier metrics coincide; they are not independent achievements.

Regression MAE: {json.dumps(e['regression_mae'])}.

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
'''
    (ROOT/'docs/MODEL_EVALUATION.md').write_text(text)
    (folder/'model_card.md').write_text(f'''# {m['model_version']}

Status: trained and evaluated on simulated mission outcomes over observed NASA MRO CTX terrain.

- Algorithm: {m['model_type']}.
- Inputs: {len(m['features'])} named public features; exact order in metadata.json.
- Outputs: success probability, return-feasible probability, time, resource expenditure, science value. Utility is assembled explicitly from those outcomes.
- Splits: 400/100/100/100 scenarios, distinct terrain quadrants and seeds.
- Model selection: validation only; calibration: separate geographic set.
- Runtime: scikit-learn {m['sklearn_version']}; CPU, no GPU/API key required.
- Measured training time in this environment: {m['seconds']:.2f} seconds (excludes data generation).
- Intended use: explainable research and educational comparison.
- Not intended for actual astronaut safety, navigation commands or flight operations.
- Predictions outside the documented feature range or below return constraints request HUMAN REVIEW.
- Results and caveats: ../../docs/MODEL_EVALUATION.md.
- Original code/artifact license: Apache-2.0; source terrain retains NASA/USGS attribution.

Best mean-utility baseline in this held-out comparison: {best['policy']}. Do not advertise universal learned-policy superiority.
''')
    print('Updated model card and evaluation report from saved results')
if __name__=='__main__':main()
