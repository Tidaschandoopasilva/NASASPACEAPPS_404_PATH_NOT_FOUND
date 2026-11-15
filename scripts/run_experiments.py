"""Fixed seeds 0..99; paired binary-corridor policy study. No outcome-based seed selection."""
import sys,json,csv,statistics
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from app.decision import estimate,posterior,sensor_rates
from app.service import setup,DEFAULT_POINTS,NOTE
from app.planner import mission
from app.terrain import ROOT
from sim.world import HiddenWorld

def run():
    rows=[];summaries=[]
    experiment_points=[[78,22],[30,34],[42,72]]  
    
    regimes=[('baseline',.3,5,.08,1,1),('expensive-scout',.3,70,.08,1,1),('rare-hazard',.03,5,.08,1,1),('common-hazard',.7,5,.08,1,1),('noisy-sensor',.3,5,.2,1,1),('no-uncertainty-penalty',.3,5,.08,0,1),('flat-terrain',.3,5,.08,1,0),('steeper-terrain',.3,5,.08,1,2)]
    for name,p,cost,sigma,wu,severity in regimes:
        t,z,s,v,b,u,cs=setup(p);z=z*severity;s=s*severity
        direct=mission(t,z,s,v,b,u,experiment_points,mode='shortest',budget=600,w_u=wu)
        blocked=v.copy();blocked[cs[0]]=False
        avoid=mission(t,z,s,blocked,b,u,experiment_points,budget=600,w_u=wu)
        
        if not direct['path'] or not avoid['path']:summaries.append({'regime':name,'status':'infeasible'});continue
        crosses=any(cs[0][tuple(q)] for q in direct['path'])
        detour=max(0,avoid['minutes']-direct['minutes']);effective_p=p if crosses else 0
        est=estimate(effective_p,cost,detour,sigma);tpr,fpr=sensor_rates(sigma)
        for seed in range(100):
            
            world=HiddenWorld(seed,[p]);obs,slip=world.observation(0,sigma);post=posterior(p,obs,tpr,fpr)
            for strategy in ['proceed','avoid','scout']:
                use_avoid=strategy=='avoid' or (strategy=='scout' and 100*post*crosses>detour)
                route=avoid if use_avoid else direct;loss=world.evaluate_crossings([0]) if crosses and not use_avoid else 0
                scout_penalty=cost+3 if strategy=='scout' else 0
                rows.append({'regime':name,'seed':seed,'strategy':strategy,'science_completion':1.,'safe_return':int(loss==0),'route_minutes':route['minutes']+(3 if strategy=='scout' else 0),'meters':route['meters'],'slip_events':int(strategy=='scout' and obs),'uncertainty_reduction':4*p*(1-p)-4*post*(1-post) if strategy=='scout' else 0,'utility':200-route['minutes']-100*loss-scout_penalty,'chose_avoid':use_avoid,'prior':p,'sigma':sigma,'scout_cost':cost,'w_u':wu,'slope_factor':severity,'terrain_state':t['data_state']})
        part=[r for r in rows if r['regime']==name];by={k:[r for r in part if r['strategy']==k] for k in ['proceed','avoid','scout']}
        delta=np.array([a['utility']-b['utility'] for a,b in zip(by['scout'],by['proceed'])]);rng=np.random.default_rng(404);boots=rng.choice(delta,(2000,100),replace=True).mean(1)
        summaries.append({'regime':name,'status':'completed','n_seeds':100,'crosses_uncertain_corridor':crosses,'detour_minutes':detour,'estimate':est,'policies':[{ 'strategy':k,**{m:float(np.mean([r[m] for r in rr])) for m in ['science_completion','safe_return','route_minutes','meters','slip_events','uncertainty_reduction','utility']}} for k,rr in by.items()],'paired_delta_mean':float(delta.mean()),'paired_delta_median':float(np.median(delta)),'bootstrap_95_ci':np.quantile(boots,[.025,.975]).tolist()})
    output=ROOT/'data/experiments';output.mkdir(exist_ok=True)
    if not rows: raise RuntimeError('All regimes infeasible; refusing to overwrite prior logs')
    with (output/'episodes.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    (output/'episodes.jsonl').write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
    report={'note':NOTE,'provenance':'simulation-on-observed-terrain','data_state':'SIMULATED','source_ids':t['source_ids'],'seeds':list(range(100)),'waypoints_grid':experiment_points,'episodes':len(rows),'regimes':summaries,'method':'Single binary corridor, two precomputed routes; Gaussian slip sensor. Research sensitivity study, not Mars performance evidence.'}
    (ROOT/'apps/web/public/data/experiments.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':run()
