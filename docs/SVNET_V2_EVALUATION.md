# 404-SVNet V2 evaluation

The model uses three histogram gradient-boosting members for each of five outcomes, with 31 pre-action features. The release includes 2,300 CTX-derived simulated scenarios and 6,900 action records. The spatial split contains 1,600 training, 200 validation, 200 calibration and 300 test scenarios. Actions from the same world stay in the same split. Validation selected 23 leaf nodes from 7, 15 and 23. Logistic calibration fits on the separate calibration set. Return threshold and abstention accounting match V1.

## Same-case comparison on 300 held-out scenarios

| Measure | V1 | V2 |
| --- | ---: | ---: |
| Return Brier (lower is better) | 0.0936 | 0.0887 |
| Return log loss (lower is better) | 0.2821 | 0.2873 |
| Mean simulated utility | 43.1034 | 40.7248 |
| Decision coverage | 0.5767 | 0.5467 |

V2 reduced squared return-probability error. Its policy accepted fewer cases and scored lower in utility. Return log loss increased slightly. The paired V2 − V1 95% utility interval was −4.92 to −0.26 on the expanded test. Constrained risk-weighted A* scored 52.22 utility on those same 300 worlds. These outcomes describe the simulator and this terrain crop.

The first 100 test cases reproduce the original held-out scenario seeds and outcomes. The remaining 200 extend the same held-out region. The benchmark scores both models on the same regenerated inputs. The labels measure synthetic hazards and resource outcomes rather than field astronaut data. Holding at base earns zero utility and contributes no real excursion.

Raw metrics: [model comparison](../models/svnet_v1/comparison.json), [evaluation](../models/svnet_v1/evaluation.json). V1 weights are under `models/svnet_baseline`.

To reproduce using the desktop Python environment:

```text
python research/generate_dataset.py
python research/train_svnet.py
python research/evaluate.py
python -m research.compare_svnet
```
