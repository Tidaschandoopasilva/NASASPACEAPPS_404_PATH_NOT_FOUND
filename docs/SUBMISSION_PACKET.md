# Submission packet — V2 draft

**Title:** 404: PATH NOT FOUND  
**Team:** Team 404  
**Model:** 404-SVNet, Scouting Value Network  
**Challenge:** Interplanetary Survival Guide: Martian Map  
**Purpose:** Learn when robotic scouting is worth its cost for a science-driven human Marswalk with return constraints.

## Abstract

404: PATH NOT FOUND combines real observations of Jezero Crater with an explainable research simulator for human exploration. NASA Mars Trek HiRISE imagery and a USGS/NASA CTX elevation crop provide the mapping and terrain foundation. Participants propose a habitat and science targets, compare round-trip routes, and preserve a return reserve. The project introduces 404-SVNet, a compact trained outcome estimator that compares proceeding, avoiding an uncertain corridor, and sending a simulated robotic scout. Its inputs contain only information available before an action. Hidden hazards remain inside the simulator; scouting supplies a noisy observation that changes the planning belief. Gradient-boosted models estimate mission completion, return feasibility, time, resources and science, with independent probability calibration. Geographic and seed separation protect a held-out evaluation from sibling-action leakage. The interface exposes predicted outcomes, feature values, constraints, domain warnings and replayable decisions. Results are deliberately mixed: the learned policy improves on a constrained uncertainty heuristic but does not outperform the strongest constrained risk-planning baseline in this test. All outcome labels are simulated, while terrain and imagery are real observations or derivatives. Code, model artifacts, experiment records, source credits are included for reproducibility. This is an educational research system, not an operational astronaut safety or rover control system.

## NASA resources actually used

- NASA/JPL/USGS HiRISE Jezero WMTS mosaic, 20 cached tiles, actual capabilities-derived tile requests.
- NASA MRO CTX / USGS Jezero science-investigation DEM, actual 20 m native crop downloaded by HTTP ranges. Source metadata preserved.
- NASA/JPL Perseverance and DigitalSpace astronaut models distributed through NASA's catalog.
- NASA Mastcam-Z products PIA24485 and PIA25212 as regional science context.
- USGS Jezero geological map as science motivation; precise waypoint unit membership remains unverified.

## Actual research result

700 distinct scenarios: 400 train, 100 validation, 100 calibration, 100 independent test, with three paired action records per scenario. 31 input features; fitted CPU gradient-boosted ensemble and separate calibrators. See MODEL_EVALUATION.md for exact frozen metrics, paired CIs, all baselines and abstention accounting. Do not present the separate 2,400-episode legacy sweep as additional ML test examples.

## Limits

Traction, hazards, resources and future human outcomes are simulated. No global Mars generalization or operational safety claim. The six-wheel PyBullet extension did not run because dependencies failed; current rover behavior is approximate. Browser/Windows QA is pending because preview infrastructure failed. Original code/models Apache-2.0; NASA/USGS resources retain source rights and credits. No endorsement.

## Public links to fill

- Repository: [ADD PUBLIC URL]
- <=30-second video or <=7-slide demo: [ADD PUBLIC URL]
- Project page: [ADD TEAM PAGE]

Official references checked 2026-11-14: https://www.spaceappschallenge.org/2026/ (maximum six participants; submission closes November 15 at 11:59 PM local time), https://github.com/nasa/spaceapps/discussions/1973 (demo format), https://www.spaceappschallenge.org/legal/ (source attribution and open work). Review the current portal guide before submission.

## YOU STILL NEED TO DO

- Run the Windows launch scripts and inspect the actual app, including the SVNet tab.
- Record/upload the demo, publish source, fill public links and submit through the portal.
- If claiming physics validation, complete the optional tests and independently review the dynamics assumptions first; none is claimed in this build.

Stops are terrain-derived candidates for two stated objectives. Assigning them to geologic units is future work. Each candidate shows its ranking signal and local slope. The stop POV uses the 20 m terrain mesh with a habitat-to-stop bearing and straight-line distance. Mastcam-Z images are grouped as regional reference photos. RAD (Gale) and SHERLOC (Jezero) are instrument references. Georeferenced radiation and mineral layers: future work. Route feasibility applies within the simulator.
