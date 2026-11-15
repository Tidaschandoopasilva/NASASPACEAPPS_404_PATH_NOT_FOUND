"""Hidden state is sampled only here. Caller receives outcomes, never feature values."""
import numpy as np
from app.decision import sensor_rates,posterior
from app.ml.features import choose_after_observation

def paired_outcomes(public,seed):
    rng=np.random.default_rng(seed);hazard=bool(rng.random()<public['prior']);delay=float(rng.uniform(8,45));resource_factor=float(rng.uniform(1.05,1.6));catastrophic=bool(rng.random()<.25)
    slip=float(rng.normal(.282915 if hazard else .09748,public['sigma']));observation=int(slip>.2);tpr,fpr=sensor_rates(public['sigma']);post=posterior(public['prior'],observation,tpr,fpr)
    outcomes={}
    for action in ['proceed','avoid','scout','risk']:
        chosen=choose_after_observation(public['routes']['proceed'],public['routes']['avoid'],post) if action=='scout' else action
        route=public['routes'][chosen];crossing=hazard and route['crosses'];extra=public['scout_minutes'] if action=='scout' else 0.
        if not route['feasible']:
            outcomes[action]={'success':0,'return_feasible':0,'minutes':public['budget'],'energy':public['energy_budget'],'science':0.,'utility':-100-public['budget'],'chosen_route':chosen,'scouting_overhead':extra};continue
        time=route['minutes']+(delay if crossing else 0)+extra;energy=(.5*route['minutes']+.01*route['ascent'])*(resource_factor if crossing else 1)+.25*extra
        returned=time<=public['budget']*.8 and energy<=public['energy_budget'] and not(crossing and catastrophic)
        success=returned;science=public['science_value'] if success else public['science_value']*.5 if not(crossing and catastrophic) else 0.
        cost=public['cost'] if action=='scout' else 0.;utility=science-time-.2*energy-100*(not success)-cost
        outcomes[action]={'success':int(success),'return_feasible':int(returned),'minutes':time,'energy':energy,'science':science,'utility':utility,'chosen_route':chosen,'scouting_overhead':extra}
    return outcomes
