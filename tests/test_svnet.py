import json,hashlib,inspect
from collections import defaultdict
import numpy as np
from fastapi.testclient import TestClient
from app.terrain import ROOT,load
from app.ml import features,inference,policy
from app.ml.features import FEATURES,feature_dict
from app.ml.inference import predict
from app.main import app

def scenarios():return [json.loads(x) for x in (ROOT/'data/svnet/scenarios.jsonl').read_text().splitlines()]
def test_spatial_and_seed_disjointness():
    rows=scenarios();seeds=defaultdict(set);regions=json.loads((ROOT/'data/svnet/manifest.json').read_text())['regions_native_pixels']
    for r in rows:
        seeds[r['split']].add(r['seed']);a,b,c,d=regions[r['split']];y,x,h,w=r['source_window'];assert a<=y<y+h<=b and c<=x<x+w<=d
    for a in seeds:
        for b in seeds:
            if a!=b:assert seeds[a].isdisjoint(seeds[b])
    vals=list(regions.values())
    for i,(a,b,c,d) in enumerate(vals):
        for aa,bb,cc,dd in vals[i+1:]:assert min(b,bb)<=max(a,aa) or min(d,dd)<=max(c,cc)
def test_all_actions_stay_in_split():
    rows=[json.loads(x) for x in (ROOT/'data/svnet/rows.jsonl').read_text().splitlines()];groups=defaultdict(list)
    for r in rows:groups[r['scenario_id']].append(r)
    manifest=json.loads((ROOT/'data/svnet/manifest.json').read_text())
    assert len(rows)==manifest['action_rows'] and len(groups)==manifest['scenarios']
    for g in groups.values():assert {r['action'] for r in g}=={'proceed','avoid','scout'} and len({r['split'] for r in g})==1

def test_feature_leakage_boundary():
    for module in [features,inference,policy]:
        source=inspect.getsource(module);assert 'sim.mission_outcomes' not in source and 'HiddenWorld' not in source
    assert len(FEATURES)==31
    for forbidden in ['truth','actual_slip','traction','outcome','label','world_seed','scenario_id']:assert not any(forbidden in f for f in FEATURES)
    s=scenarios()[0];x=feature_dict(s['public'],'scout');s['outcomes']={};s['world_seed']=999
    assert x==feature_dict(s['public'],'scout')
def test_artifacts_are_trained():
    m,b,c=inference.artifacts();assert m['trained'];assert b['features']==FEATURES
    assert all(model.n_iter_==100 for model in b['ensemble'][0].values())
    assert len(b['ensemble'])==3

def test_predict_without_labels_and_determinism():
    s=next(s for s in scenarios() if s['split']=='test');a=predict(s['public']);b=predict(s['public']);assert a==b
    for r in a['candidates']:
        assert 0<=r['predicted']['success']<=1 and 0<=r['predicted']['return_feasible']<=1
        assert 'utility' not in r['features']

def test_return_gate_rejects_impossible_budget():
    s=scenarios()[0];s['public']['budget']=.01;r=predict(s['public']);assert r['recommendation']=='HUMAN REVIEW';assert not any(c['accepted'] for c in r['candidates'])
def test_model_api():
    manifest=json.loads((ROOT/'data/svnet/manifest.json').read_text())
    c=TestClient(app);assert c.get('/api/v1/ml/model').json()['trained'];assert len(c.get('/api/v1/ml/scenarios').json())==manifest['counts']['test']
    result=c.get('/api/v1/ml/scenarios/test-0000');assert result.status_code==200
    assert c.get('/api/v1/ml/scenarios/train-0000').status_code==404
    r=c.post('/api/v1/ml/predict',json={});assert r.status_code==200 and len(r.json()['candidates'])==3

def test_real_dem_metadata_and_alignment():
    t=load()[0];assert t['data_state']=='DERIVED' and t['source_ids']==['usgs-ctx-dem']
    assert t['native']['resolution']==[20.,20.] and t['standard_parallel_deg']==18.4663
    import rasterio
    from rasterio.warp import transform
    meta=json.loads((ROOT/'data/dem-acquisition.json').read_text());assert meta['downloaded_bytes']<50*1024**2
    assert hashlib.sha256((ROOT/'data/jezero-ctx-crop.tif').read_bytes()).hexdigest()==meta['sha256']
    with rasterio.open(ROOT/'data/jezero-ctx-crop.tif') as ds:
        xs,ys=transform('+proj=longlat +R=3396190 +no_defs',ds.crs,[77.40,77.48],[18.42,18.49])
        assert all(ds.bounds.left<=x<=ds.bounds.right for x in xs) and all(ds.bounds.bottom<=y<=ds.bounds.top for y in ys)
def test_metrics_recomputed_from_records():
    report=json.loads((ROOT/'models/svnet_v1/evaluation.json').read_text());records=report['policy_records']
    assert len(records)==report['test_scenarios']*len(report['policies'])
    for p in report['policies']:
        actual=np.mean([r['utility'] for r in records if r['policy']==p['policy']]);assert abs(actual-p['utility'])<1e-8
    assert report['paired_vs_uncertainty_threshold']['baseline']=='uncertainty-threshold-constrained'

def test_learned_action_can_update_mission():
    c=TestClient(app);r=c.post('/api/v1/ml/execute',json={});assert r.status_code==200
    out=r.json();assert out['kind'] in ['route','episode']
    if out['kind']=='route':assert out['route']['path'][0]==out['route']['path'][-1]
