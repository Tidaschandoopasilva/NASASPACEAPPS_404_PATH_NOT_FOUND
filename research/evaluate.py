import os
os.environ.setdefault('OMP_NUM_THREADS','2')
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from sklearn.metrics import brier_score_loss,mean_absolute_error,log_loss
from app.terrain import ROOT
from app.ml.inference import artifacts,predict
from research.baselines import actions
from app.ml.features import feature_dict

def ci(values):
    values=np.asarray(values);rng=np.random.default_rng(404);b=rng.choice(values,(2000,len(values)),replace=True).mean(1);return np.quantile(b,[.025,.975]).tolist()
def main():
    scenarios=[json.loads(s) for s in (ROOT/'data/svnet/scenarios.jsonl').read_text().splitlines()];test=[s for s in scenarios if s['split']=='test'];records=[];predictions=[]
    for s in test:
        prediction=predict(s['public']);policy=actions(s['public']);policy['404-SVNet']=prediction['recommendation'].lower();hindsight=max(0.,max(o['utility'] for o in s['outcomes'].values()))
        for name,chosen in [('uncertainty-threshold-constrained',policy['uncertainty-threshold']),('risk-astar-constrained','risk')]:
            if chosen=='risk':
                r=s['public']['routes']['risk'];ok=r['feasible'] and r['minutes']<=s['public']['budget']*.8 and .5*r['minutes']+.01*r['ascent']<=s['public']['energy_budget']
            else:
                f=feature_dict(s['public'],chosen);ok=f['graph_feasible']>.999 and f['nominal_return_margin']>=0 and f['nominal_energy']<=s['public']['energy_budget']
            policy[name]=chosen if ok else 'human review'
        for name,action in policy.items():
            result=s['outcomes'].get(action,{'success':0,'return_feasible':1,'minutes':0.,'energy':0.,'science':0.,'utility':0.,'scouting_overhead':0.})
            records.append({'scenario_id':s['id'],'policy':name,'action':action,'abstained':action=='human review','regret':hindsight-result['utility'],**result})
        for candidate in prediction['candidates']:
            a=candidate['action'].lower();predictions.append({'scenario_id':s['id'],'action':a,'predicted':candidate['predicted'],'truth':s['outcomes'][a]})
    policies=[]
    for name in policy:
        rows=[r for r in records if r['policy']==name];policies.append({'policy':name,'n':len(rows),**{k:float(np.mean([r[k] for r in rows])) for k in ['success','return_feasible','minutes','energy','science','utility','scouting_overhead','regret','abstained']},'utility_ci95':ci([r['utility'] for r in rows])})
    calibration={}
    for target in ['success','return_feasible']:
        y=np.array([r['truth'][target] for r in predictions]);p=np.array([r['predicted'][target] for r in predictions]);bins=[]
        for i in range(10):
            m=(p>=i/10)&(p<(i+1)/10 if i<9 else p<=1)
            if m.any():bins.append({'mean_predicted':float(p[m].mean()),'observed_fraction':float(y[m].mean()),'n':int(m.sum())})
        calibration[target]={'brier_score':float(brier_score_loss(y,p)),'log_loss':float(log_loss(y,p)),'ece10':sum(b['n']*abs(b['mean_predicted']-b['observed_fraction']) for b in bins)/len(p),'reliability_bins':bins}
    mae={k:float(mean_absolute_error([r['truth'][k] for r in predictions],[r['predicted'][k] for r in predictions])) for k in ['minutes','energy','science']}
    by=lambda name:{r['scenario_id']:r['utility'] for r in records if r['policy']==name};learned=by('404-SVNet');baseline=by('uncertainty-threshold-constrained');delta=[learned[k]-baseline[k] for k in learned]
    report={'model_version':artifacts()[0]['model_version'],'source_ids':['usgs-ctx-dem'],'label_provenance':'SIMULATED, real CTX terrain','test_scenarios':len(test),'test_action_rows':len(predictions),'test_region':'Southeast quadrant, disjoint from model fitting, selection and calibration','policies':policies,'calibration':calibration,'regression_mae':mae,'paired_vs_uncertainty_threshold':{'baseline':'uncertainty-threshold-constrained','mean_delta':float(np.mean(delta)),'ci95':ci(delta)},'abstention_accounting':'Human review earns zero science/utility and incurs zero travel; return-feasible is 1 because no excursion starts. Coverage is reported. This can favor conservative policies.','limitations':['Single binary uncertain corridor per scenario','Synthetic traction, delay and failure labels','Only Jezero crop; no global Mars generalization','Three-model spread is heuristic epistemic uncertainty, not a statistical guarantee'],'policy_records':records}
    out=ROOT/'models/svnet_v1';(out/'evaluation.json').write_text(json.dumps(report,indent=2));(out/'test_predictions.json').write_text(json.dumps(predictions,indent=2));(ROOT/'apps/web/public/data/svnet-evaluation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='policy_records'},indent=2))
if __name__=='__main__':main()
