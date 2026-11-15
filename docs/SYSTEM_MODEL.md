# 404-SVNet system model

Observed CTX elevation and HiRISE imagery → derived geometry → candidate round trips → public action features → trained outcomes → constrained utility decision → simulated observation → posterior route selection.

The route generator is A*, not a learned controller. The learned component is a three-member gradient-boosted outcome ensemble. Inputs comprise 31 numeric features: geometry, route metrics, validity/coverage, prior/noise, budgets, science value, scout distance/time/cost, and action identity. The input contract excludes scenario IDs, seeds, source-window identifiers, realized slip, hidden hazards and labels. The hidden world exists only inside the outcome/observation simulator.

The model predicts mission success, return feasibility, minutes, arbitrary resource units and science. Utility = predicted science − minutes − 0.2 × resources − 100 × (1 − success) − scout effort. Candidate acceptance requires a graph path, nominal time within 80% of budget, nominal resource compliance, calibrated return probability >=0.8, ensemble spread <=0.18 and in-domain inputs. Otherwise the system requests HUMAN REVIEW.

The live ML console constructs a single uncertain corridor crossed by the candidate route and excluding endpoints, matching the training problem. It may differ from the legacy three-corridor overlay. Applying PROCEED/AVOID updates the route. Applying SCOUT samples a new noisy observation, updates the belief and chooses between precomputed proceed/avoid candidate routes. This is a restricted candidate replan, not an exhaustive sequential POMDP solver. The legacy scout still runs full grid replanning.

Scouting is not triggered by uncertainty alone. For the simulated scout action, both possible observations are integrated before acting to form expected candidate features. The actual post-observation route selection uses only the posterior belief. Learning labels come from paired simulated outcomes, not real astronaut missions.

The narrower research contribution is an integrated and reproducible experiment for human science objectives and return constraints. It does not claim invention of value of information, uncertainty-aware planning, calibration or robot cooperation. Scientific novelty and operational usefulness are not established by this prototype.
