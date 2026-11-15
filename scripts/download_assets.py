"""Refresh verified NASA catalog assets. 20 MiB ceiling per GLB."""
from pathlib import Path
import urllib.request,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
ASSETS={
 'rover':('https://science.nasa.gov/3d-resources/mars-2020-perseverance-rover/','https://assets.science.nasa.gov/content/dam/science/cds/3d/resources/model/mars-2020-perseverance-rover/Mars%202020%20Perseverance%20Rover.glb'),
 'astronaut':('https://science.nasa.gov/3d-resources/astronaut/','https://assets.science.nasa.gov/content/dam/science/cds/3d/resources/model/astronaut/Astronaut.glb')}
def main():
    logs=[]
    for name,(page,url) in ASSETS.items():
        try:
            with urllib.request.urlopen(url,timeout=30) as r:b=r.read(20*1024*1024+1)
            if len(b)>20*1024*1024 or b[:4]!=b'glTF':raise ValueError('Invalid/oversized GLB')
            (ROOT/f'apps/web/public/models/{name}.glb').write_bytes(b);logs.append({'asset':name,'page':page,'url':url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'status':'acquired'})
        except Exception as e:logs.append({'asset':name,'status':'unavailable','error':str(e)})
    (ROOT/'data/asset-acquisition.json').write_text(json.dumps(logs,indent=2));print(json.dumps(logs,indent=2))
if __name__=='__main__':main()
