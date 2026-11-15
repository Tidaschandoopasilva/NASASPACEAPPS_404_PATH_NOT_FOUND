import os
os.environ.setdefault('OMP_NUM_THREADS','2')
import sys,json,time,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np,joblib,sklearn
from sklearn.ensemble import HistGradientBoostingClassifier,HistGradientBoostingRegressor
from sklearn.metrics import log_loss,mean_absolute_error
from app.terrain import ROOT
from app.ml.features import FEATURES
from research.calibrate import fit_calibrator,calibrate
TARGETS=['success','return_feasible','minutes','energy','science']

def fit_bundle(X,Y,leaf,seed):
    out={}
    for i,key in enumerate(TARGETS):
        cls=HistGradientBoostingClassifier if i<2 else HistGradientBoostingRegressor
        model=cls(max_iter=100,max_leaf_nodes=leaf,l2_regularization=3.,learning_rate=.07,random_state=seed,early_stopping=False)
        
        model.fit(X,Y[:,i]);out[key]=model
    return out

def main():
    start=time.time();rows=[json.loads(x) for x in (ROOT/'data/svnet/rows.jsonl').read_text().splitlines()]
    split=lambda k:[r for r in rows if r['split']==k]
    arr=lambda rr:(np.array([r['features'] for r in rr]),np.array([[r['labels'][k] for k in TARGETS] for r in rr]))
    X,Y=arr(split('train'));V,W=arr(split('validation'));C,D=arr(split('calibration'));trials=[];selected=None
    for leaf in [7,15,23]:
        model=fit_bundle(X,Y,leaf,404);score=log_loss(W[:,0],model['success'].predict_proba(V)[:,1])+mean_absolute_error(W[:,2],model['minutes'].predict(V))/100
        trials.append({'max_leaf_nodes':leaf,'validation_score':score});print(trials[-1],flush=True)
        if selected is None or score<selected[0]:selected=(score,leaf,model)
    ensemble=[selected[2]]
    for seed in [405,406]:
        rng=np.random.default_rng(seed);idx=rng.integers(0,len(X)//3,len(X)//3);indices=np.concatenate([np.arange(i*3,i*3+3) for i in idx]);ensemble.append(fit_bundle(X[indices],Y[indices],selected[1],seed))
    calibrators={}
    for key,i in [('success',0),('return_feasible',1)]:
        pred=np.mean([m[key].predict_proba(C)[:,1] for m in ensemble],axis=0);calibrators[key]=fit_calibrator(pred,D[:,i])
    
    p=calibrate(calibrators['return_feasible'],np.mean([m['return_feasible'].predict_proba(V)[:,1] for m in ensemble],axis=0))
    threshold=.8 
    output=ROOT/'models/svnet_v1';output.mkdir(exist_ok=True)
    joblib.dump({'ensemble':ensemble,'features':FEATURES,'targets':TARGETS},output/'model.joblib',compress=3);joblib.dump(calibrators,output/'calibration.joblib',compress=3)
    metadata={'model_version':'404-SVNet v2.0','model_type':'3-member gradient-boosted action-conditional outcome ensemble','trained':True,'features':FEATURES,'targets':TARGETS,'training_scenarios':len(X)//3,'validation_scenarios':len(V)//3,'calibration_scenarios':len(C)//3,'test_scenarios':sum(r['split']=='test' for r in rows)//3,'selected_max_leaf_nodes':selected[1],'selection_trials':trials,'return_threshold':threshold,'uncertainty_threshold':.18,'domain_min':X.min(0).tolist(),'domain_max':X.max(0).tolist(),'sklearn_version':sklearn.__version__,'seconds':time.time()-start,'source_ids':['usgs-ctx-dem'],'label_provenance':'SIMULATED on NASA-derived terrain','files':{f:hashlib.sha256((output/f).read_bytes()).hexdigest() for f in ['model.joblib','calibration.joblib']}}
    (output/'metadata.json').write_text(json.dumps(metadata,indent=2));print('TRAINED',metadata['seconds'],'seconds',flush=True)
if __name__=='__main__':main()
