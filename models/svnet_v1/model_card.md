# 404-SVNet V2.0

Trained research model for simulated Jezero mission actions. Each of the three ensemble members uses histogram gradient-boosted trees. Inputs are 31 pre-action features. Outputs cover mission success, return feasibility, time, energy, and science value. Logistic calibration is fitted separately for the success and return outputs.

The dataset contains 1,600 training, 200 validation, 200 calibration, and 300 test scenarios. Runtime is pinned to scikit-learn 1.8.0. The inference policy can defer to human review. Model estimates do not certify field risk.

[Paired evaluation and reproduction workflow](../../docs/SVNET_V2_EVALUATION.md)
