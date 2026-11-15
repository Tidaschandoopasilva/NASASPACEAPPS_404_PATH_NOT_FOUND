"""Public pre-action feature contract. Never accepts a simulator or outcome record."""
import math
import numpy as np
from app.decision import sensor_rates,posterior
ACTIONS=('proceed','avoid','scout')
FEATURES=['distance_m','nominal_minutes','ascent_m','mean_slope_deg','max_slope_deg','p90_slope_deg','nodata_fraction','observed_fraction','resolution_m','detour_minutes','hazard_prior','hazard_entropy','sensor_sigma','sensor_tpr','sensor_fpr','budget_minutes','reserve_fraction','science_value','energy_budget','scout_distance_m','scout_minutes','scout_cost','return_leg_fraction','crosses_corridor','nominal_return_margin','graph_feasible','mission_distance_m','nominal_energy','action_proceed','action_avoid','action_scout']

def describe_route(t,z,s,route,mask):
    path=route.get('path',[])
    if not path:return {'distance':0.,'minutes':0.,'ascent':0.,'mean_slope':0.,'max_slope':0.,'p90_slope':0.,'crosses':False,'feasible':False,'return_fraction':0.}
    cells=np.array(path);height=z[cells[:,0],cells[:,1]];sl=s[cells[:,0],cells[:,1]]
    return {'distance':float(route['meters']),'minutes':float(route['minutes']),'ascent':float(np.maximum(0,np.diff(height)).sum()),'mean_slope':float(sl.mean()),'max_slope':float(sl.max()),'p90_slope':float(np.quantile(sl,.9)),'crosses':bool(mask[cells[:,0],cells[:,1]].any()),'feasible':True,'return_fraction':route['legs'][-1]['minutes']/max(route['minutes'],1e-6)}

def choose_after_observation(proceed,avoid,p):
    score=lambda r: -r['minutes']-100*p*int(r['crosses']) if r['feasible'] else -1e9
    return 'avoid' if score(avoid)>score(proceed) else 'proceed'

def feature_dict(public,action):
    if action not in ACTIONS:raise ValueError('Unknown candidate action')
    p=public['prior'];tpr,fpr=sensor_rates(public['sigma']);routes=public['routes'];direct=routes['proceed'];detour=routes['avoid']['minutes']-direct['minutes'] if routes['avoid']['feasible'] else 600.
    if action=='scout':
        prob=tpr*p+fpr*(1-p);weighted=[]
        for o,q in [(1,prob),(0,1-prob)]:
            key=choose_after_observation(direct,routes['avoid'],posterior(p,o,tpr,fpr));weighted.append((q,routes[key]))
        geom={k:sum(q*float(r[k]) for q,r in weighted) for k in direct};geom['feasible']=all(r['feasible'] for _,r in weighted);extra=public['scout_minutes']
    else:geom=routes[action];extra=0.
    nominal=geom['minutes']+extra;energy=.5*geom['minutes']+.01*geom['ascent']+.25*extra
    values=[geom['distance'],nominal,geom['ascent'],geom['mean_slope'],geom['max_slope'],geom['p90_slope'],public['nodata_fraction'],public['observed_fraction'],public['resolution_m'],detour,p,-p*math.log(max(p,1e-8))-(1-p)*math.log(max(1-p,1e-8)),public['sigma'],tpr,fpr,public['budget'],.2,public['science_value'],public['energy_budget'],public['scout_distance'],public['scout_minutes'],public['cost'],geom['return_fraction'],geom['crosses'],public['budget']*.8-nominal,float(geom['feasible']),direct['distance'],energy,*[float(action==a) for a in ACTIONS]]
    return dict(zip(FEATURES,map(float,values)))

def vector(public,action):return [feature_dict(public,action)[k] for k in FEATURES]
