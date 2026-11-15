"""NASA DEM geometry + public scenario assumptions, with spatially disjoint splits."""
from pathlib import Path
import numpy as np
from app.terrain import slopes
from app.planner import mission
from app.ml.features import describe_route

def make_public(z,valid,dx,dy,rng):
    slope=slopes(z,dx,dy);valid=valid & np.isfinite(slope);z=np.nan_to_num(z);slope=np.nan_to_num(slope,nan=90.)
    n=z.shape[0];points=[[n-12,12],[12,16],[20,n-12]];t={'dx_m':dx,'dy_m':dy}
    prior=float(rng.uniform(.03,.85));b=np.zeros(z.shape)+.06;u=np.zeros(z.shape)
    direct=mission(t,z,slope,valid,b,u,points,mode='shortest',budget=600)
    if not direct['path']:return None
    first_goal=direct['path'].index(points[1]);center=direct['path'][max(1,first_goal//2)]
    yy,xx=np.indices(z.shape);mask=(xx-center[1])**2+(yy-center[0])**2<=int(rng.integers(4,9))**2
    b[mask]=prior;u[mask]=1
    risk=mission(t,z,slope,valid,b,u,points,mode='risk',budget=600)
    avoid=mission(t,z,slope,valid & ~mask,b,u,points,mode='risk',budget=600)
    routes={k:describe_route(t,z,slope,r,mask) for k,r in [('proceed',direct),('avoid',avoid),('risk',risk)]}
    
    budget=float(rng.uniform(.8,1.8)*direct['minutes']/ .8);scout_distance=float(rng.uniform(5,250));scout_minutes=scout_distance/(.25*60)+float(rng.uniform(.5,3))
    public={'routes':routes,'prior':prior,'sigma':float(rng.uniform(.04,.2)),'budget':budget,'science_value':float(rng.uniform(100,300)),'energy_budget':float(rng.uniform(.75,1.8)*(.5*direct['minutes']+.01*routes['proceed']['ascent'])),'scout_distance':scout_distance,'scout_minutes':scout_minutes,'cost':float(rng.uniform(0,35)),'nodata_fraction':float(1-valid.mean()),'observed_fraction':float(rng.uniform(.45,1)),'resolution_m':max(dx,dy),'data_state':'DERIVED','source_ids':['usgs-ctx-dem']}
    geometry={'points':points,'corridor_center':center,'shape':list(z.shape),'paths':{'proceed':direct['path'],'avoid':avoid['path'],'risk':risk['path']}}
    return public,geometry
