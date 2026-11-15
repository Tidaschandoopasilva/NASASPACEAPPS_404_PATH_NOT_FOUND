import json,uuid
import numpy as np
from app.terrain import load,priors,corridors,planetary,world,ROOT
from app.planner import mission, astar
from app.decision import estimate,posterior,sensor_rates
from sim.world import HiddenWorld
from sim.rover import Rover
NOTE='Research simulator; not validated for mission operations.'
DEFAULT_POINTS=[[68,27],[40,34],[42,61]]
def setup(p=.3):
    t,z,s,v=load();b=priors(s);u=np.zeros(z.shape);cs=corridors(z.shape)
    for c in cs:b[c]=p;u[c]=1
    return t,z,s,v,b,u,cs

def compare(points=None,budget=180,p=.3,max_slope=20):
    t,z,s,v,b,u,cs=setup(p);points=points or DEFAULT_POINTS
    return {'shortest':mission(t,z,s,v,b,u,points,'shortest',budget,max_slope),'risk':mission(t,z,s,v,b,u,points,'risk',budget,max_slope),'source_ids':t['source_ids'],'data_state':t['data_state'],'note':NOTE}

def simulate(seed=7,p=.3,cost=5,sigma=.08,points=None,budget=180):
    t,z,s,v,b,u,cs=setup(p);points=points or DEFAULT_POINTS
    before=mission(t,z,s,v,b,u,points,budget=budget)
    
    surveyed = np.zeros(z.shape, dtype=bool)
    for row, col in before['path']:
        surveyed[max(0,row-3):row+4,max(0,col-3):col+4] = True
    surveyed &= v
    u[surveyed] *= .25
    aerial = mission(t,z,s,v,b,u,points,budget=budget)
    
    hit=[k for k,c in enumerate(cs) if any(c[tuple(x)] for x in aerial['path'])];k=hit[0] if hit else 0
    hidden=HiddenWorld(seed,[p]*3);obs,slip=hidden.observation(k,sigma);tpr,fpr=sensor_rates(sigma);post=posterior(p,obs,tpr,fpr)
    b[cs[k]]=post;u[cs[k]]=4*post*(1-post)
    after=mission(t,z,s,v,b,u,points,budget=budget)
    targets = [cell for cell in aerial['path'] if cs[k][tuple(cell)]]
    rover_path = astar(z,s,v,b,u,points[0],targets[0],t['dx_m'],t['dy_m']) if targets else None
    if not rover_path:
        after = {**after, 'feasible': False, 'reason': 'EVA held: rover could not verify a corridor'}
    
    change_cell = after['path'][int(len(after['path'])*.58)] if after['feasible'] and len(after['path']) > 5 else None
    rover=Rover(seed);telemetry=[{'step':i,**rover.step(slope_deg=float(s[47,42]),mu=.12 if obs else .6)} for i in range(80)]
    result={'id':uuid.uuid4().hex,'run_id':uuid.uuid4().hex,'sim_seed':seed,'trial_status':'completed','data_state':'SIMULATED','source_ids':t['source_ids'],'note':NOTE,'before':before,'aerial':aerial,'after':after,'uav_path':before['path'],'rover_path':rover_path or [],'survey_cells':int(surveyed.sum()),'monitor_change_cell':change_cell,'estimate':estimate(p,cost,sigma=sigma),'observation':{'corridor':k,'positive':bool(obs),'slip':slip,'prior':p,'posterior':post,'data_state':'SIMULATED'},'telemetry':telemetry,'events':[{'t':0,'label':'UAV surveying route geometry'},{'t':.35,'label':'Aerial route selected; rover scout starts'},{'t':.65,'label':'Rover evidence applied; begin feasible EVA'},{'t':1,'label':'Monitoring complete or EVA held for review'}]}
    directory=ROOT/'data/runs';directory.mkdir(exist_ok=True);(directory/f"{result['id']}.json").write_text(json.dumps(result));return result
