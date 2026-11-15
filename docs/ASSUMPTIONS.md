# Assumptions — V2

Real observation: CTX elevation / native 20 m, Mars sphere R=3,396,190 m, equirectangular standard parallel 18.4663°; HiRISE imagery and contextual Mastcam-Z photographs.

Derived: slope, relief, route distances/ascent, candidate travel estimates, 96×96 UI grid and 20/40/60 m research samples.

Assumed: 20° maximum route slope; 1 m/s flat walking with time factor 1+3*slope/20; 180-min UI budget and 20% reserve; route weights 1/2/4/1; science priorities and arbitrary resource units; coverage fraction; corridor hazard prior; rover prepositioning and observation cost. None are flight-validated constants.

Simulated: hidden Bernoulli hazard, Gaussian slip signal, delay, resource multiplier and catastrophic event. Safe/slip Gaussian means .09748/.282915; threshold .20; scenario sigma .04–.20. Delay 8–45 min, hazardous resource multiplier 1.05–1.6, catastrophic hazard event probability .25. Labels follow the simulator equations in sim/mission_outcomes.py.

Training budgets/science/costs are randomized publicly and never inferred from hidden realization. Resources: 0.5*walking-minutes + .01*ascent-meters, with a hidden multiplier only after a hazardous crossing; scout overhead adds .25*scout-minutes. Utility: science − total minutes − .2*resources −100*failure − scouting effort. These are experiment design units.

Learned return threshold .8 and ensemble-spread threshold .18 are research decision settings, not safety guarantees. Live rover assumed prepositioned 60 m from corridor, 5-minute scout overhead and resource allowance .45*EVA budget. Training scout distances span 5–250 m at .25 m/s plus .5–3 min observation.

Static NASA GLBs are enlarged visual glyphs with procedural movement. Rover local trace and animation are simplified and not a coupled six-wheel dynamics simulation. Habitat is fictional; science positions proposed.

## EVA timing

| Parameter | Simulator setting | Evidence status |
|---|---|---|
| Clear-day reference walking speed | 1 m/s | Adjustable placeholder, not a measured value |
| Weather speed factors | Day 1.0, night 0.75, dust 0.60 | Adjustable placeholders, not measured values |
| Equipment load multiplier on time | 1 + load in kg / 80, load control 0–40 kg | Adjustable placeholder, not a measured value |
| Grade multiplier on time | 1 + 3 × absolute grade + positive uphill grade, as rise/run | Adjustable placeholder, not a measured value |
| Science stop work | 3 minutes per target | Adjustable placeholder, not a measured value |
| Return reserve | 20% of the time budget per sortie | Simulator planning rule |

Minutes proxy for resources. Oxygen, other consumables, fatigue, and tool handling are outside the model. Hazards, outcomes, and weather factors are simulated. See [Mobility and objective checks](MOBILITY_CHECKS.md).
