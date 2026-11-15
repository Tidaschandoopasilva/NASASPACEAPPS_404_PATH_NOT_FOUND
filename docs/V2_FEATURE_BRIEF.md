# **404: PATH NOT FOUND — Core Novelty, AI Training & System Model**

TEAM 404 • NASA SPACE APPS 2026 • RESEARCH ARCHITECTURE V2.0

I would make a significant upgrade to our project: **give 404: PATH NOT FOUND its own trainable decision-making model**, rather than relying entirely on hand-designed A\* route-planning rules.

But I would not train an LLM to generate routes or simply fine-tune a vision model. Our strongest direction is a **hybrid physics-informed, uncertainty-aware decision system** that learns when gathering new information changes the best astronaut exploration decision.

## **1. What is our actual core novelty?**

## **Learning the value of robotic scouting for human Mars exploration**

Our central research question:

> Given incomplete orbital observations of Martian terrain, can a learned decision model determine whether an astronaut should proceed, avoid an uncertain region, or deploy a robotic scout—while preserving scientific objectives and the ability to return?

We can call the trainable component:

# **404-SVNet**

Scouting Value Network

**Model type:** Learned mission-outcome and scouting-value estimator

**Input:** NASA-derived terrain features, observation uncertainty, proposed routes, science objectives and mission constraints.

**Output:** Predicted outcomes for alternative strategies, their uncertainty, and a recommended action with an explanation.

**Decision options:** PROCEED / AVOID / SCOUT.

This is a proposed architecture and model name. We have not trained or validated it yet.

### **Why this is more interesting than AI route planning**

NASA has already demonstrated generative-AI waypoint planning using orbital imagery and elevation models. In December 2025, Perseverance executed two such drives, following verification through JPL's digital twin.&#x20;

NASA Jet Propulsion Laboratory (JPL)



Recent research also goes beyond conventional navigation:

- **Scout–rover cooperation (February 2026):** Researchers demonstrated how a mobile robot can gather terrain-strength information that informs another robot's traversal planning.&#x20;

  arXiv

- **Probabilistic rover traversability (February 2026):** Researchers integrated uncertainty-aware slip prediction, route planning and online adaptation.&#x20;

  Nature

- **Information-versus-risk valuation (September 2026):** Research examined when hazardous robotic information gathering is worth its cost and risk.&#x20;

  arXiv



This means we **cannot claim to have invented uncertainty-aware scouting, value of information, or rover cooperation**.

Our narrower proposed contribution is their application and quantitative evaluation in an integrated **human Marswalk, science-target and returnability planning system**, rather than treating rover traversal as the end goal.

**Proposed R&D contribution**

A mission-aware scouting decision model that explicitly evaluates:

1. Whether the astronaut can complete the scientific expedition and return.
2. Whether available orbital observations are sufficient for route selection.
3. Whether sending a robot to investigate would improve the subsequent decision enough to justify the time and risk.
4. Whether the model can recognize when its predictions are too uncertain to recommend a particular action.

The mathematical methods behind these ideas are established. The work we can contribute is a reproducible implementation, a well-defined experimental problem and measured comparisons on NASA-grounded Martian terrain.

**That is a defensible research direction, not yet a verified claim of scientific novelty.**

## **2. Complete system model**

I propose a hybrid architecture rather than one neural network controlling everything.

## **404-SVNet — System Architecture**

Real observations → model prediction → mission decision → simulation feedback

**NASA DATA FOUNDATION**

CTX/HiRISE elevation · Orbital imagery · Science targets · Optional thermal layer

**Terrain model**

Elevation, slope, coverage and observed features

**Belief model**

What is known, unknown, or uncertain

## **404-SVNet**

**TRAINABLE AI MODEL**

Predict mission outcomes and the value of acquiring additional terrain information

**PROCEED**

Use existing map

**AVOID**

Select another route

**SCOUT**

Gather observations

**PYTHON SIMULATION + EXPERIMENT ENGINE**

Rover dynamics · Hidden terrain scenarios · Sensor measurements · Mission outcome logs

**UPDATE PLANNING INFORMATION + REPLAN**

Compare predicted and simulated outcomes · Update terrain belief · Explain expedition decisions

The physics simulator supplies observations and training outcomes, but it must not expose its hidden terrain truth directly to the decision model.

### **System components**

| Component                   | Method                                              | Trainable?                   |
| --------------------------- | --------------------------------------------------- | ---------------------------- |
| Mars terrain representation | DEM, optical imagery, spatial metadata              | Not initially                |
| Route candidate generator   | A\*, resource-constrained search                    | No                           |
| Terrain uncertainty model   | Observation mask and probabilistic hazard estimates | Partly                       |
| **404-SVNet**               | Gradient boosting or compact neural network         | **Yes**                      |
| Scouting decision optimizer | Expected mission utility and information value      | Uses trained predictions     |
| Rover motion simulator      | PyBullet or simplified dynamics                     | Parameters, not initially ML |
| Mission Rewind              | Deterministic event replay and analysis             | No                           |

This separation is important: **not every intelligent component should be a neural network.**

## **3. The mathematical system model**

We can represent the exploration problem as a partially observable sequential decision process.

### **A. System state**

At time \\(t\\):

\\[ s_t=(p_A,p_R,M^\*,b_t,E_t,G) \\]

Where:

- \\(p_A\\): astronaut position
- \\(p_R\\): rover position
- \\(M^\*\\): true terrain state inside the simulator, hidden from the decision model
- \\(b_t\\): current belief about uncertain terrain
- \\(E_t\\): remaining mission resources
- \\(G\\): scientific targets and mission objectives

The distinction between \\(M^\*\\) and \\(b_t\\) is essential. The simulator knows which hidden hazards exist, but the decision system should only have access to the information a real explorer could reasonably possess.

### **B. Physical state evolution**

The simulator controls the underlying movement:

\\[ s\_{t+1}=f\_{\mathrm{physics}}(s_t,u_t,\xi_t) \\]

Where \\(u_t\\) represents rover controls or mission actions and \\(\xi_t\\) represents modeled disturbances.

For a rover, this includes position, velocity, wheel commands, contact response and selected regolith assumptions.

Mars gravity is approximately \\(3.71\\,\mathrm{m/s^2}\\). A PyBullet rover would be a physics approximation using published vehicle properties, not a flight-validated Perseverance digital twin.

### **C. Belief updating**

When the rover investigates uncertain terrain, it receives an observation \\(o\_{t+1}\\).

The ideal Bayesian update is:

\\[ b\_{t+1}(M)\propto P(o\_{t+1}\mid M,a_t)b_t(M) \\]

For the MVP, we can use a simpler probability-grid update with an explicitly defined observation-noise model.

We should not confuse map coverage with the probability of terrain being safe. Those are different things.

### **D. Mission utility**

For any completed simulated expedition, define:

\\[ U = w_s S -\lambda_t T -\lambda_e E -\lambda_f F -\lambda_c C\_{\mathrm{scout}} \\]

Here \\(S\\) is science value obtained, \\(T\\) is travel duration, \\(E\\) is modeled resource expenditure, \\(F\\) is a failure or failure-severity measure, and \\(C\_{\mathrm{scout}}\\) is scouting cost.

The weights are chosen design parameters. We would report sensitivity to those weights rather than pretending there is a universally correct numerical value.

**Safe return should also be a planning constraint, not merely a small penalty.** A route that reaches a scientific destination but cannot return within its simulated resource budget is not a feasible mission under that scenario.

### **E. Value of scouting**

This is the main decision concept.

\\[ \mathrm{VoS}(b)= \mathbb{E}\_{o}\left[ \max\_{\pi} U(\pi\mid b^{\\,o}) \right] - \max\_{\pi} U(\pi\mid b) - C\_{\mathrm{scout}} \\]

The first term represents expected mission value after receiving possible scouting observations and replanning. The second represents the best decision using current knowledge. The last accounts for scouting costs, including modeled rover exposure and time.

The key principle:

**The system should scout when new information is expected to improve the mission decision, not merely because uncertainty is high.**

An uncertain region far away from every useful route might not be worth investigating. A smaller uncertainty near a critical return corridor might be much more important.

## **4. What exactly do we train?**

I recommend starting with a **supervised, action-conditional outcome model** rather than training a deep reinforcement-learning agent from scratch.

### **404-SVNet v1 — Practical model**

Inputs to the model should be information available *before* the action.

| Input group         | Example features                                          |
| ------------------- | --------------------------------------------------------- |
| Terrain geometry    | Mean slope, maximum slope, ascent, descent                |
| Route structure     | Distance, detour distance, difficult segments             |
| Observation quality | NoData fraction, coverage, source resolution              |
| Uncertainty         | Estimated hazard probability and uncertainty              |
| Mission             | Return budget, science priority, travel allowance         |
| Scouting            | Rover distance to survey area, expected coverage and time |
| Candidate action    | Proceed, avoid or scout a particular region               |

The model could use 20–40 carefully chosen numerical features rather than raw orbital images initially.

Its outputs would be:

\\[ f\_\theta(x,a)= \begin{bmatrix} P(\mathrm{mission\ success})\\\ P(\mathrm{return\ feasible})\\\ \widehat{T}\\\ \widehat{E}\\\ \widehat{S} \end{bmatrix} \\]

These represent predictions **under the simulation model**. They are not validated probabilities of real astronaut safety.

For the first implementation, use separate gradient-boosted classification and regression models. This is easier to train, inspect and debug on a laptop than a large transformer.

An optional v2 could use a compact PyTorch network that encodes local terrain patches and candidate routes, but that is not necessary to establish the first research result.

## **5. How to generate the training dataset**

We have real NASA elevation, but we do **not** have labels describing how thousands of future astronaut expeditions succeeded or failed.

So our initial training labels must come from simulation.

**1**

**Import actual NASA terrain**

Select georeferenced Jezero DEM crops and derive slope

**2**

**Generate hidden scenario conditions**

Sample hypothetical friction, obstacles and sensor uncertainties

**3**

**Build the observation map**

Reveal only data available to the planner; keep hidden truth separate

**4**

**Generate candidate expeditions**

Compute proceed, avoid and scout options using the same initial information

**5**

**Run paired simulations**

Execute strategies under the same underlying scenario and record results

**6**

**Construct supervised labels**

Mission completion, return feasibility, time, science value and scouting cost

**7**

**Train and evaluate 404-SVNet**

Predict outcomes and compare the learned policy against fixed baselines

### **A crucial experimental safeguard**

Imagine our hidden simulation terrain includes an area of very loose soil.

The simulator knows its traction coefficient. The planner does not.

The planner might initially know only that this region is poorly characterized.

If the rover scouts the area, it receives a simulated measurement with noise. Only then may the belief map change.

If we accidentally include the hidden traction coefficient among the training inputs, the AI would be learning with information that a real astronaut could never possess. That would invalidate our experiment.

This is the same sort of leakage problem we've taken care to avoid in our earlier robotics research.

## **6. Training strategy**

I would train in two levels.

Level 1 — Fast simulation training

Use a 2D terrain-grid simulator with route planning, resource accounting, modeled traction/hazard events and noisy scouting observations.

This produces enough examples to train the decision model efficiently on a CPU.

Level 2 — Physics-based validation

Replay a smaller number of selected scenarios in PyBullet using a Perseverance-inspired six-wheel model.

Compare the simplified simulator's predictions with the physics simulator's behavior. The two models may disagree; that disagreement is itself useful research evidence.

A practical initial data plan:

| Dataset             | Proposed quantity                  | Purpose                                  |
| ------------------- | ---------------------------------- | ---------------------------------------- |
| Training            | 400 scenarios × 3 strategies       | First functioning model                  |
| Validation          | 100 scenarios × 3 strategies       | Model selection                          |
| Independent test    | 100 scenarios × 3 strategies       | Unseen outcome evaluation                |
| Expanded training   | 1,500+ scenarios if feasible       | Improve coverage of simulated conditions |
| PyBullet validation | 30–100 targeted trials if feasible | Dynamics stress tests                    |

These are proposed targets, not already generated data or guaranteed execution volumes.

Split by **scenario, spatial region and random seed**, not by randomly distributing the three action records from the same simulation across training and test.

If we only train and test inside Jezero, our results should be described as performance on held-out Jezero-derived scenarios, not generalization to all Martian environments.

### **What loss functions?**

For mission-success prediction, use binary cross-entropy:

\\[ \mathcal L\_{\mathrm{success}} =-y\log p-(1-y)\log(1-p) \\]

For continuous quantities such as time and simulated resource expenditure, use MAE or Huber loss.

If building a multi-output neural model, a possible combined loss is:

\\[ \mathcal L = \alpha \mathcal L\_{\mathrm{success}} +\beta \mathcal L\_{\mathrm{return}} +\gamma \mathcal L\_{\mathrm{time}} +\delta \mathcal L\_{\mathrm{resources}} \\]

The weights and target scales require tuning. We should avoid making the model look good by optimizing a metric that ignores costly mission failures.

I would also calibrate the predicted probabilities using a separate held-out calibration set, then evaluate Brier score and reliability curves. Scikit-learn supports probability calibration, but emphasizes keeping calibration data independent of model fitting.&#x20;

scikit-learn 1.9.1 documentation



## **7. How the trained model actually makes decisions**

The application should not simply run:

`model.predict()` → choose the highest-scoring class.

Instead:

1. Generate candidate routes with A\*.
2. Build candidate actions: proceed, avoid, and scout specific uncertain segments.
3. Estimate outcomes using 404-SVNet.
4. For scouting, model possible sensor observations, update the terrain belief and replan.
5. Estimate expected mission utility and evaluate simulated return constraints.
6. Choose a feasible strategy; if none meets the configured criteria, report that no acceptable simulated plan was found.

This architecture gives us **a trained model inside a structured decision-making system**, rather than a black-box algorithm claiming to know the safest path.

The decision policy would explicitly incorporate model uncertainty. For example, a high uncertainty estimate may trigger additional investigation or a request for human review rather than an unsupported safety guarantee.

## **8. How we prove whether 404-SVNet is useful**

We need to compare against baselines, not just show that our model produces answers.

| Strategy                               | Purpose                                            |
| -------------------------------------- | -------------------------------------------------- |
| Shortest-distance planning             | Baseline without terrain risk                      |
| Risk-weighted A\*                      | Baseline using known terrain costs                 |
| Always scout                           | Measures cost of unnecessary information gathering |
| Scout if uncertainty exceeds threshold | Simple information-gathering heuristic             |
| **404-SVNet policy**                   | Learned outcome/value-guided scouting              |

We then compare outcomes on identical held-out simulated worlds.

PROPOSED PRIMARY MEASUREMENTS

Mission completion

Percentage of simulated expeditions completed

Safe-return feasibility

Fraction returning within modeled constraints

Science achieved

Weighted science targets completed

Scouting overhead

Additional simulated time and resource cost

Prediction calibration

Brier score and reliability error

Decision regret

Utility gap against the best simulated decision in hindsight

Use paired seeds and bootstrap confidence intervals over independent scenarios. Report where scouting helps and where it wastes time or introduces additional risk.

Also run one important ablation:

**Remove the learned model and replace it with a simple uncertainty threshold.**

If the learned system cannot outperform that baseline on meaningful outcomes, then the extra model complexity may not be justified.

## **9. What does the final AI experience look like?**

404 / SCOUT OR SKIP

## **Expedition Decision Console**

Illustrative interface with hypothetical predictions, not trained-model results.

Decision rationale

Simulation scenario

PROCEEDExisting mapAVOIDAlternative routeSCOUTGather information

SCOUT — Scenario explanation

Send the modeled rover to observe uncertain terrain, then replan the human expedition.

The real dashboard would display model version, confidence calibration, predicted outcomes, source IDs and the measured or assumed inputs behind this recommendation.

This gives Team 404 a real R&D identity: its AI would not just announce a route. It would explain **whether additional knowledge is worth obtaining before the astronaut commits to that route**.

## **10. Where this fits into our current Codex project**

I would add the following architecture after the existing terrain-engine stage:

```
path-not-found/
├── apps/
│   ├── web/
│   │   └── src/
│   │       ├── AtlasMap.tsx
│   │       ├── ScoutOrSkip.tsx
│   │       └── MissionRewind.tsx
│   └── api/
│       └── app/
│           ├── terrain/
│           ├── planning/
│           ├── belief/
│           ├── ml/
│           │   ├── features.py
│           │   ├── inference.py
│           │   └── policy.py
│           └── main.py
├── sim/
│   ├── mars_rover_env.py
│   ├── scenario_generator.py
│   ├── observation_model.py
│   └── experiment_runner.py
├── research/
│   ├── generate_dataset.py
│   ├── train_svnet.py
│   ├── calibrate.py
│   ├── evaluate.py
│   └── baselines.py
├── models/
│   └── svnet_v1/
│       ├── model.joblib
│       ├── calibration.joblib
│       └── model_card.md
└── docs/
    ├── SYSTEM_MODEL.md
    ├── RESEARCH_METHODOLOGY.md
    └── MODEL_EVALUATION.md
```

The final model artifacts and simulation datasets should be generated by the training pipeline. We should not create placeholder model files that pretend training already happened.

### **Proposed next implementation order**

| Stage        | Deliverable                                                         |
| ------------ | ------------------------------------------------------------------- |
| 02 — Current | Authentic CTX elevation, slope and map alignment                    |
| 03           | Science-driven human expedition planner with return constraints     |
| 04           | Partial-observation belief map and uncertainty representation       |
| 05           | Fast simulation, scenario generator and supervised training dataset |
| 06           | Train 404-SVNet, compare policies and add PyBullet validation       |
| 07           | Complete Scout or Skip interface, experiment results and submission |

For the 36-hour hackathon, prioritize the small supervised model and fast simulator. A complete articulated PyBullet rover and deep-RL policy are worthwhile extensions only after the functioning Marswalk experience and basic research comparison are complete.

## **Final research identity**

TEAM 404 • RESEARCH SYSTEM

# **404: PATH NOT FOUND**

## **404-SVNet**

An uncertainty-aware scouting-value model for science-driven human Mars surface exploration.

Core hypothesis

A learned, mission-aware value-of-scouting policy can improve science-versus-resource outcomes and simulated return feasibility compared with fixed scouting heuristics under partially observed Martian terrain conditions.

Hypothesis to be tested. No improvement is claimed until independent experimental results exist.

**My recommendation:** Keep the physical rover and the learning system separate, but connect them through observations and outcome data. Train the first 404-SVNet model from controlled, NASA-terrain-grounded simulation scenarios; evaluate it against simple baselines; then use PyBullet for selected higher-fidelity tests.

That gives us the three things you asked for: **a clear proposed novelty, a trainable AI model, and a complete mathematical and software system model**—without making claims our current data cannot support.