"""Crop a verified Mars projected GeoTIFF to the imagery ROI; preserve invalid cells."""
from pathlib import Path
import argparse,json,math
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
R=3396190.0
BOUNDS=[77.40,18.42,77.48,18.49]
def process(path=None):
    out=ROOT/'apps/web/public/data';out.mkdir(parents=True,exist_ok=True)
    w,s,e,n=BOUNDS; ncell=96
    
    standard_parallel=18.4663 if path else 0.
    xscale=math.cos(math.radians(standard_parallel))
    dx=math.radians(e-w)*R*xscale/(ncell-1);dy=math.radians(n-s)*R/(ncell-1)
    state='SIMULATED'; source=['synthetic-fixture']; native=None
    if path:
        import rasterio
        from rasterio.warp import reproject,Resampling
        from rasterio.transform import from_bounds
        crs=f'+proj=eqc +lat_ts={standard_parallel} +lat_0=0 +lon_0=0 +R={R} +units=m +no_defs'
        with rasterio.open(path) as ds:
            if not ds.crs or '3396190' not in ds.crs.to_wkt():raise ValueError('Verify Mars radius and datum before import')
            z=np.full((ncell,ncell),np.nan,dtype=np.float32)
            
            tr=from_bounds(math.radians(w)*R*xscale-dx/2,math.radians(s)*R-dy/2,math.radians(e)*R*xscale+dx/2,math.radians(n)*R+dy/2,ncell,ncell)
            reproject(rasterio.band(ds,1),z,src_transform=ds.transform,src_crs=ds.crs,src_nodata=ds.nodata,dst_transform=tr,dst_crs=crs,dst_nodata=np.nan,resampling=Resampling.bilinear)
            native={'crs':ds.crs.to_wkt(),'affine':list(ds.transform),'resolution':list(ds.res),'filename':Path(path).name}
            state='DERIVED';source=['usgs-ctx-dem']
    else:
        y,x=np.mgrid[:ncell,:ncell];z=24*np.sin(x/13)*np.cos(y/19)+55*np.exp(-((x-60)**2+(y-40)**2)/230)-20*np.exp(-((x-22)**2+(y-66)**2)/90)
    valid=np.isfinite(z);gy,gx=np.gradient(z,dy,dx);slope=np.degrees(np.arctan(np.hypot(gx,gy)));valid &= np.isfinite(slope)
    np.save(ROOT/'data/heightmap.npy',z)
    lo=float(np.nanmin(z));hi=float(np.nanmax(z));scaled=np.where(valid,(z-lo)/max(hi-lo,1)*65534,65535).astype('uint16');Image.fromarray(scaled).save(out/'heightmap16.png')
    meta={'id':'jezero-roi','data_state':state,'label':'SYNTHETIC TEST TERRAIN — real elevation unavailable' if not path else 'USGS CTX DEM, resampled','source_ids':source,'bounds':BOUNDS,'coordinate_system':'Mars sphere equirectangular; planetocentric; east positive','radius_m':R,'standard_parallel_deg':standard_parallel,'dx_m':dx,'dy_m':dy,'width':ncell,'height':ncell,'height_min_m':lo,'height_max_m':hi,'native':native,'png_nodata':65535,'png_scale_m':(hi-lo)/65534,'png_offset_m':lo,'effective_resolution_m':[dx,dy],'units':'meters / degrees'}
    (ROOT/'data/metadata.json').write_text(json.dumps(meta,indent=2))
    safe=lambda a:np.where(np.isfinite(a),a,0).round(5).tolist()
    payload={**meta,'elevation':safe(z),'slope':safe(slope),'valid':valid.tolist()}
    (out/'terrain.json').write_text(json.dumps(payload,separators=(',',':')))
    print(meta['label'],z.shape,'valid',int(valid.sum()),'of',z.size)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dem');a=p.parse_args();process(a.dem)
