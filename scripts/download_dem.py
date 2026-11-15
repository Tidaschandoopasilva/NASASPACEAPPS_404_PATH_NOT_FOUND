"""Download only the required strips of the verified USGS CTX GeoTIFF (<50 MiB)."""
from pathlib import Path
import urllib.request,struct,json,hashlib,math
import numpy as np
import rasterio
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds,Window
ROOT=Path(__file__).resolve().parents[1]
URL='https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/mars2020_trn/CTX/ScienceInvestigationMaps_JPL/M20_JezeroCrater_CTXDEM_20m.tif'
def get_range(start,end):
    request=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{end}'})
    with urllib.request.urlopen(request,timeout=60) as r:
        if r.status!=206 or not r.headers.get('Content-Range','').startswith(f'bytes {start}-{end}/'):raise ValueError('Server did not honor exact byte range')
        b=r.read(end-start+2)
    if len(b)!=end-start+1:raise ValueError('Truncated or oversized response')
    return b

def main():
    data=ROOT/'data';data.mkdir(exist_ok=True)
    header=get_range(0,65535);temp=data/'ctx-header.tif';temp.write_bytes(header)
    with rasterio.open(temp) as ds:
        profile=ds.profile.copy();crs=ds.crs;affine=ds.transform
        geographic='+proj=longlat +R=3396190 +no_defs'
        requested=[77.36,18.38,77.52,18.53]
        bounds=transform_bounds(geographic,crs,*requested)
        win=from_bounds(*bounds,affine)
        c0=max(0,math.floor(win.col_off));r0=max(0,math.floor(win.row_off));c1=min(ds.width,math.ceil(win.col_off+win.width));r1=min(ds.height,math.ceil(win.row_off+win.height))
        width=ds.width;source_shape=[ds.height,ds.width];nodata=ds.nodata
    offset=struct.unpack('<I',header[4:8])[0];count=struct.unpack('<H',header[offset:offset+2])[0];tags={}
    for i in range(count):
        tag,typ,n,value=struct.unpack('<HHII',header[offset+2+i*12:offset+14+i*12]);tags[tag]=(typ,n,value)
    if tags[259][2]!=1 or tags[278][2]!=1 or tags[258][2]!=32 or tags[339][2]!=3:raise ValueError('Source layout changed; expected uncompressed float32 single-row strips')
    _,n,pos=tags[273];offsets=struct.unpack(f'<{n}I',header[pos:pos+4*n])
    start=offsets[r0];end=offsets[r1-1]+width*4-1
    if end-start+1+len(header)>50*1024**2:raise ValueError('Crop exceeds download budget')
    raw=get_range(start,end);rows=np.frombuffer(raw,dtype='<f4').reshape(r1-r0,width);crop=rows[:,c0:c1].copy()
    crop_transform=rasterio.windows.transform(Window(c0,r0,c1-c0,r1-r0),affine)
    profile.update(width=c1-c0,height=r1-r0,transform=crop_transform,compress='deflate')
    output=data/'jezero-ctx-crop.tif'
    with rasterio.open(output,'w',**profile) as ds:ds.write(crop,1)
    meta={'id':'usgs-ctx-dem','url':URL,'acquired':'2026-11-14','owner':'USGS / NASA MRO CTX','source_ids':['usgs-ctx-dem'],'data_state':'OBSERVED','native_crs':crs.to_wkt(),'native_affine':list(affine),'native_resolution_m':[20,20],'source_shape':source_shape,'window':[c0,r0,c1-c0,r1-r0],'requested_bounds':requested,'crop_transform':list(crop_transform),'downloaded_bytes':len(header)+len(raw),'crop_bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'nodata':nodata,'method':'HTTP byte ranges; verified TIFF strip layout; pixel values copied without resampling'}
    (data/'dem-acquisition.json').write_text(json.dumps(meta,indent=2));temp.unlink();print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
