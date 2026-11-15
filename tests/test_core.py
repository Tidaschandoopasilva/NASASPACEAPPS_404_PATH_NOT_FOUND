import inspect,math,json
import numpy as np
import pytest
from fastapi.testclient import TestClient
from app import planner
from app.planner import astar,mission
from app.terrain import slopes,load,world,pixel,planetary
from app.decision import sensor_rates,posterior,estimate
from sim.rover import Rover
from sim.world import HiddenWorld
from app.main import app

def fixture(n=8):
    z=np.zeros((n,n));return z,z.copy(),np.ones((n,n),bool),z.copy(),z.copy()
def test_flat_slope():assert np.allclose(slopes(np.zeros((8,8)),20,30),0)
def test_ramp():
    y,x=np.mgrid[:8,:8];assert np.allclose(slopes(x*20*.1,20,30),math.degrees(math.atan(.1)))
def test_world_roundtrip():
    t=load()[0]
    for p in [(0,0),(33,44),(95,95)]:assert pixel(t,*world(t,*p))==list(p)
def test_meter_spacing():
    t=load()[0];assert math.isclose(t['dx_m']*95,math.radians(.08)*3396190*math.cos(math.radians(t.get('standard_parallel_deg',0))))
def test_planetary_bounds():
    t=load()[0];assert np.allclose(planetary(t,0,0),[18.49,77.40]);assert np.allclose(planetary(t,95,95),[18.42,77.48])
def test_astar_diagonal():
    a=fixture();p=astar(*a,(0,0),(7,7),20,20,'shortest');assert p==[(i,i) for i in range(8)]
def test_nodata_excluded():
    z,s,v,b,u=fixture();v[3,:]=False;assert astar(z,s,v,b,u,(0,0),(7,7),20,20) is None
def test_no_corner_cutting():
    z,s,v,b,u=fixture(2);v[0,1]=v[1,0]=False;assert astar(z,s,v,b,u,(0,0),(1,1),20,20) is None
def test_max_slope():
    z,s,v,b,u=fixture();s[3,:]=21;assert astar(z,s,v,b,u,(0,0),(7,7),20,20) is None
def test_unknown_start():
    z,s,v,b,u=fixture();v[0,0]=False;assert astar(z,s,v,b,u,(0,0),(7,7),20,20) is None
def test_budget_and_return():
    a=fixture();t={'dx_m':20,'dy_m':20};points=[[0,0],[0,7],[7,7]]
    r=mission(t,*a,points,budget=180);assert r['path'][0]==r['path'][-1];assert len(r['legs'])==3;assert r['feasible']
    assert not mission(t,*a,points,budget=1)['feasible']
def test_planner_cannot_read_truth():
    source=inspect.getsource(planner);assert 'truth_map' not in source;assert 'sim.' not in source;assert 'HiddenWorld' not in source
    assert set(inspect.signature(astar).parameters)=={'z','slope','valid','belief','uncertainty','start','goal','dx','dy','mode','w_u','max_slope'}
def test_hazard_belief_changes_route():
    z,s,v,b,u=fixture();b[1:7,3:5]=.99;p=astar(z,s,v,b,u,(4,0),(4,7),20,20);assert any(r==0 or r==7 for r,c in p)
def test_sensor_rates():
    a,b=sensor_rates();assert a==pytest.approx(.85,abs=.001);assert b==pytest.approx(.1,abs=.001)
def test_bayes_direction():
    a,b=sensor_rates();assert posterior(.3,1,a,b)>.3;assert posterior(.3,0,a,b)<.3
def test_vos_cost_regime():assert estimate(cost=100)['vos']<0;assert estimate(cost=0)['vos']>0
def test_uninformative_sensor():assert posterior(.3,1,.5,.5)==pytest.approx(.3)
def test_rover_rest():
    r=Rover();a=r.step(speed=0);assert a['x_m']==a['y_m']==0
def test_rover_forward():assert Rover().step()['x_m']>0
def test_steering():assert Rover().step(steering=.2)['y_m']>0
def test_slip():assert Rover().step(slope_deg=25,mu=.1)['slip']>Rover().step(slope_deg=0,mu=.6)['slip']
def test_reproducibility():
    a=HiddenWorld(7,[.3]*3);b=HiddenWorld(7,[.3]*3);assert a.observation(0)==b.observation(0)
    a=Rover(7);b=Rover(7);assert [a.step() for _ in range(10)]==[b.step() for _ in range(10)]
def test_api():
    c=TestClient(app);assert c.get('/health').status_code==200;assert c.get('/api/v1/terrain').json()['data_state']=='DERIVED'
    assert c.post('/api/v1/scout/estimate',json={'prior':2}).status_code==422
    assert c.post('/api/v1/routes/compare',json={'points':[[0,0],[96,0],[0,0]]}).status_code==422
    assert c.get('/api/v1/simulations/not-valid').status_code==404
    assert c.get('/api/v1/sources').status_code==200

def test_simulation_integration():
    c=TestClient(app);r=c.post('/api/v1/simulations',json={'seed':7}).json();assert r['trial_status']=='completed';assert len(r['telemetry'])==80
    assert c.get('/api/v1/simulations/'+r['id']).json()['sim_seed']==7
    assert 'truth_map' not in json.dumps(r)

def test_saved_experiments_are_paired():
    from app.terrain import ROOT
    rows=[json.loads(s) for s in (ROOT/'data/experiments/episodes.jsonl').read_text().splitlines()]
    from collections import defaultdict
    groups=defaultdict(set)
    for r in rows:groups[(r['regime'],r['seed'])].add(r['strategy'])
    assert len(groups)==800
    import csv
    with (ROOT/'data/experiments/episodes.csv').open() as f: assert len(list(csv.DictReader(f)))==2400
    assert all(s=={'proceed','avoid','scout'} for s in groups.values())
    assert {r['seed'] for r in rows}==set(range(100))
    expensive=[r for r in rows if r['regime']=='expensive-scout']
    avg=lambda k:np.mean([r['utility'] for r in expensive if r['strategy']==k])
    assert avg('scout')<avg('proceed')

def test_source_assets_present():
    from app.terrain import ROOT
    from PIL import Image
    img=Image.open(ROOT/'apps/web/public/data/imagery.png');assert img.size==(1024,896)
    assert np.array(img)[:,:,:3].std()>10
    for name in ['rover','astronaut']:assert (ROOT/f'apps/web/public/models/{name}.glb').read_bytes()[:4]==b'glTF'
