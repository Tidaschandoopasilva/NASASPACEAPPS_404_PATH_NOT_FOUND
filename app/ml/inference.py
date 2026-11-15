import os
os.environ.setdefault('OMP_NUM_THREADS','2')
from functools import lru_cache
import json,hashlib
import numpy as np,joblib
from threadpoolctl import threadpool_limits
from app.terrain import ROOT
from app.ml.features import FEATURES,ACTIONS,vector,feature_dict
from research.calibrate import calibrate

@lru_cache(maxsize=1)
def artifacts():
    p=ROOT/'models/svnet_v1';meta=json.loads((p/'metadata.json').read_text())
    for f,h in meta['files'].items():
        if hashlib.sha256((p/f).read_bytes()).hexdigest()!=h:raise ValueError('Model integrity mismatch')
    return meta,joblib.load(p/'model.joblib'),joblib.load(p/'calibration.joblib')

@threadpool_limits.wrap(limits=2)
def predict(public, model_artifacts=None):
    meta,bundle,cals=model_artifacts or artifacts();X=np.array([vector(public,a) for a in ACTIONS]);out=[]
    low=np.array(meta['domain_min']);high=np.array(meta['domain_max']);tol=np.maximum((high-low)*.1,1e-5)
    
    for i,action in enumerate(ACTIONS):
        preds={};spread={}
        for target in bundle['targets']:
            raw=np.array([m[target].predict_proba(X)[:,1] if target in cals else m[target].predict(X) for m in bundle['ensemble']])
            if target in cals:
                values=np.array([calibrate(cals[target],row) for row in raw]);preds[target]=float(calibrate(cals[target],raw.mean(0))[i]);spread[target]=float(values[:,i].std())
            else:preds[target]=max(0.,float(raw[:,i].mean()));spread[target]=float(raw[:,i].std())
        feature=feature_dict(public,action);preds['science']=min(public['science_value'],preds['science'])
        utility=preds['science']-preds['minutes']-.2*preds['energy']-100*(1-preds['success'])-(public['cost'] if action=='scout' else 0)
        graph_ok=feature['graph_feasible']>.999 and feature['nominal_return_margin']>=0 and feature['nominal_energy']<=public['energy_budget']
        ood=[FEATURES[j] for j in np.where((X[i]<low-tol)|(X[i]>high+tol))[0]]
        if public['source_ids']!=meta['source_ids']:ood.append('terrain_source')
        uncertainty=max(spread['success'],spread['return_feasible'])
        accepted=graph_ok and preds['return_feasible']>=meta['return_threshold'] and uncertainty<=meta['uncertainty_threshold'] and not ood
        out.append({'action':action.upper(),'predicted':preds,'ensemble_std':spread,'expected_utility':utility,'nominal_constraints_met':bool(graph_ok),'out_of_domain_features':ood,'accepted':bool(accepted),'features':feature})
    accepted=[r for r in out if r['accepted']];best=max(accepted,key=lambda r:r['expected_utility']) if accepted else None
    return {'model_version':meta['model_version'],'trained':True,'source_ids':public['source_ids'],'data_state':'DERIVED','prediction_scope':'SIMULATED outcomes on NASA-derived terrain; not astronaut safety probabilities','recommendation':best['action'] if best else 'HUMAN REVIEW','why':f"{best['action']} has the highest predicted utility among candidates passing nominal return/resource constraints, calibrated return threshold and domain checks." if best else 'No candidate passes all nominal, learned-return, uncertainty and domain checks. Review constraints or gather more evidence.','return_threshold':meta['return_threshold'],'uncertainty_threshold':meta['uncertainty_threshold'],'candidates':out}
