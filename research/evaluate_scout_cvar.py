"""Frozen-split candidate replay. The historical data lacks per-cell observations."""
import json
from pathlib import Path

import numpy as np
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
THRESHOLDS = np.linspace(0,1,11)
DELTA = .10


def select(public):
    candidates = []
    for action in ('proceed','avoid','risk'):
        route = public['routes'][action]
        if not route['feasible'] or route['minutes']>.8*public['budget']:
            continue
        if .5*route['minutes']+.01*route['ascent'] > public['energy_budget']:
            continue
        
        probability = min(1., .02 + .1*route['max_slope']/35 +
                          public['prior']*route['crosses'])
        score = route['minutes']/public['budget'] + min(1., probability/.1)
        candidates.append((score,probability,action))
    return min(candidates)[1:] if candidates else (float('inf'),None)


def main():
    rows = [json.loads(line) for line in (ROOT/'data/svnet/scenarios.jsonl').read_text().splitlines()]
    splits = {name:[(s,*select(s['public'])) for s in rows if s['split']==name]
              for name in ('calibration','test')}
    curve = []
    for threshold in THRESHOLDS:
        accepted = [s for s,p,a in splits['calibration'] if a and p<=threshold]
        failures = sum(not s['outcomes'][select(s['public'])[1]]['return_feasible'] for s in accepted)
        upper = float(beta.ppf(1-.05/len(THRESHOLDS),failures+1,len(accepted)-failures)) if failures<len(accepted) else 1.
        curve.append({'threshold':float(threshold),'accepted':len(accepted),'failures':failures,'upper':upper})
    certified = [row for row in curve if row['upper']<=DELTA]
    cutoff = max((row['threshold'] for row in certified),default=-1.)
    def summarize(policy):
        outcomes = []
        for s,p,a in splits['test']:
            if policy=='risk-astar':
                route = s['public']['routes']['risk']
                public = s['public']
                eligible = (route['feasible'] and route['minutes'] <= .8*public['budget']
                            and .5*route['minutes']+.01*route['ascent'] <= public['energy_budget'])
                a = 'risk' if eligible else None
            elif p>cutoff:
                a = None
            if a:
                outcomes.append(s['outcomes'][a])
        utilities = sorted(o['utility'] for o in outcomes)
        k = max(1,int(np.ceil(len(utilities)*.1)))
        return {'coverage':len(outcomes)/len(splits['test']),
                'accepted':len(outcomes),
                'return_failure_rate':float(np.mean([not o['return_feasible'] for o in outcomes])) if outcomes else None,
                'utility_cvar90':float(np.mean(utilities[:k])) if outcomes else None}
    report = {'scope':'Archived candidate-replay proxy, not full mesh SCOUT-CVaR evaluation',
              'delta':DELTA,'confidence':.95,'curve':curve,'selected_threshold':cutoff if certified else None,
              'test_scenarios':len(splits['test']),
              'candidate_cvar_replay':summarize('candidate-cvar'),'risk_astar':summarize('risk-astar')}
    (ROOT/'apps/web/public/data/scout-cvar-evaluation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
