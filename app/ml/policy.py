"""Build live public route descriptors and apply SVNet constraints; no hidden world."""
import numpy as np
from app.service import setup,DEFAULT_POINTS
from app.planner import mission
from app.ml.features import describe_route
from app.ml.inference import predict

def live_decision(points=None,budget=180,prior=.3,cost=5,sigma=.08):
    t,z,s,v,b,u,cs=setup(prior);points=points or DEFAULT_POINTS
    direct=mission(t,z,s,v,b,u,points,mode='shortest',budget=budget)
    
    hits=[mask for mask in cs if any(mask[tuple(p)] for p in direct['path']) and not any(mask[tuple(p)] for p in points)]
    if hits:mask=hits[0]
    elif direct['path']:
        end=direct['path'].index(points[1]);center=direct['path'][max(1,end//2)];yy,xx=np.indices(z.shape);mask=(yy-center[0])**2+(xx-center[1])**2<=5**2
    else:mask=cs[0]
    b=np.full(z.shape,.06);u=np.zeros(z.shape);b[mask]=prior;u[mask]=1
    avoid=mission(t,z,s,v & ~mask,b,u,points,mode='risk',budget=budget)
    risk=mission(t,z,s,v,b,u,points,mode='risk',budget=budget)
    routes={k:describe_route(t,z,s,r,mask) for k,r in [('proceed',direct),('avoid',avoid),('risk',risk)]}
    
    public={'routes':routes,'prior':prior,'sigma':sigma,'budget':budget,'science_value':200.,'energy_budget':budget*.45,'scout_distance':60.,'scout_minutes':5.,'cost':cost,'nodata_fraction':float(1-v.mean()),'observed_fraction':.8,'resolution_m':max(t['dx_m'],t['dy_m']),'data_state':t['data_state'],'source_ids':t['source_ids']}
    result=predict(public);result['public_inputs']=public;result['route_candidates']={'proceed':direct,'avoid':avoid,'risk':risk};result['corridor_center_grid']=np.argwhere(mask).mean(0).round().astype(int).tolist();result['assumptions']=['Rover prepositioned 60 m from survey area','5-minute scouting overhead','Resource allowance 0.45 × EVA budget, arbitrary units','Observed fraction 0.8 is scenario assumption, distinct from DEM validity'];return result
