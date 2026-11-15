"""Compare both models on the same unseen scenarios."""
import json

import joblib
import numpy as np
from sklearn.metrics import brier_score_loss, log_loss

from app.ml.inference import artifacts, predict
from app.terrain import ROOT
from research.evaluate import ci


def evaluate(model, scenarios):
    utility, labels, probabilities, performed = [], [], [], []
    for scenario in scenarios:
        result = predict(scenario["public"], model)
        action = result["recommendation"].lower()
        performed.append(action != "human review")
        utility.append(scenario["outcomes"].get(action, {}).get("utility", 0))
        for candidate in result["candidates"]:
            truth = scenario["outcomes"][candidate["action"].lower()]
            labels.append(truth["return_feasible"])
            probabilities.append(candidate["predicted"]["return_feasible"])
    return ({"mean_utility": float(np.mean(utility)),
             "coverage": float(np.mean(performed)),
             "return_brier": float(brier_score_loss(labels, probabilities)),
             "return_log_loss": float(log_loss(labels, probabilities))}, np.array(utility))


def main():
    old = ROOT / "models/svnet_baseline"
    baseline = (json.loads((old / "metadata.json").read_text()),
                joblib.load(old / "model.joblib"), joblib.load(old / "calibration.joblib"))
    current = artifacts()
    scenarios = [json.loads(line) for line in (ROOT / "data/svnet/scenarios.jsonl").read_text().splitlines()]
    test = [s for s in scenarios if s["split"] == "test"]
    result = {}
    for name, cases in (("expanded_test",test), ("original_100",test[:100]), ("additional_test",test[100:])):
        old_scores, old_utility = evaluate(baseline,cases)
        new_scores, new_utility = evaluate(current,cases)
        result[name] = {"scenarios":len(cases), "v1":old_scores, "v2":new_scores,
                        "paired_utility_delta_ci95":ci(new_utility-old_utility)}
    (ROOT / "models/svnet_v1/comparison.json").write_text(json.dumps(result, indent=2))
    report_path = ROOT / "models/svnet_v1/evaluation.json"
    report = json.loads(report_path.read_text())
    report["model_comparison"] = result["expanded_test"]
    report_path.write_text(json.dumps(report, indent=2))
    (ROOT / "apps/web/public/data/svnet-evaluation.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
