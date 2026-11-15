import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from PIL import Image
from app.terrain import ROOT
from sim.scenario_generator import make_public
from sim.mission_outcomes import paired_outcomes
from app.ml.features import vector,FEATURES

def main():
    out=ROOT/'data/svnet';out.mkdir(exist_ok=True)
    with Image.open(ROOT/'data/jezero-ctx-crop.tif') as image:
        z = np.asarray(image, dtype=np.float32)
        nodata = float(image.tag_v2.get(42113, '-3.4028234663852886e+38'))
    valid = (z != np.float32(nodata)) & np.isfinite(z)
    h,w = z.shape
    affine = json.loads((ROOT/'data/dem-acquisition.json').read_text())['crop_transform']
    
    regions={'train':[0,h//2-6,0,w//2-6],'validation':[0,h//2-6,w//2+6,w], 'calibration':[h//2+6,h,0,w//2-6],'test':[h//2+6,h,w//2+6,w]}
    counts={'train':1600,'validation':200,'calibration':200,'test':300};scenarios=[];rows=[];attempts={}
    for split_index,(split,count) in enumerate(counts.items()):
        rmin,rmax,cmin,cmax=regions[split];accepted=0;attempt=0
        while accepted<count and attempt<count*20:
            seed=100000*(split_index+1)+attempt;rng=np.random.default_rng(seed);attempt+=1
            step=int(rng.integers(1,4));size=64*step
            r=int(rng.integers(rmin,rmax-size+1));c=int(rng.integers(cmin,cmax-size+1));patch=z[r:r+size:step,c:c+size:step].astype(float);mask=valid[r:r+size:step,c:c+size:step]
            patch[~mask]=np.nan
            result=make_public(patch,mask,20.*step,20.*step,rng)
            if result is None:continue
            public,geometry=result;outcomes=paired_outcomes(public,seed+7000000);sid=f'{split}-{accepted:04d}';world_seed=seed+7000000
            scenario={'id':sid,'split':split,'seed':seed,'world_seed':world_seed,'region':split,'source_window':[r,c,size,size],'public':public,'geometry':geometry,'outcomes':outcomes}
            scenarios.append(scenario)
            for action in ['proceed','avoid','scout']:
                rows.append({'scenario_id':sid,'split':split,'action':action,'features':vector(public,action),'labels':{k:outcomes[action][k] for k in ['success','return_feasible','minutes','energy','science','utility']}})
            accepted+=1
            if accepted%50==0:print(split,accepted,flush=True)
        attempts[split]={'accepted':accepted,'attempts':attempt,'excluded_no_route':attempt-accepted};print(split,attempts[split],flush=True)
        if accepted<count:raise RuntimeError('Insufficient graph-feasible scenarios; no output committed')
    (out/'scenarios.jsonl').write_text('\n'.join(json.dumps(s) for s in scenarios)+'\n');(out/'rows.jsonl').write_text('\n'.join(json.dumps(s) for s in rows)+'\n')
    manifest={'version':'404-svnet-data-2','features':FEATURES,'scenarios':len(scenarios),'action_rows':len(rows),'counts':counts,'regions_native_pixels':regions,'source_affine':list(affine),'source_sha256':hashlib.sha256((ROOT/'data/jezero-ctx-crop.tif').read_bytes()).hexdigest(),'source_ids':['usgs-ctx-dem'],'geometry':'DERIVED from NASA MRO CTX / USGS DEM','labels':'SIMULATED; not observed astronaut outcomes','effective_resolution_m':[20,40,60],'attempts':attempts,'split_method':'Separate geographic quadrants, 12-pixel gap, disjoint seeds; action siblings kept together'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('Wrote',len(rows),'action records',flush=True)
if __name__=='__main__':main()
