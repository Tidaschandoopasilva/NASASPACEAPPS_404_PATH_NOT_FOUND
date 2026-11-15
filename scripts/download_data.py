"""Bounded NASA WMTS acquisition; no arbitrary URL proxy. Run from any directory."""
from pathlib import Path
import json, math, urllib.request, urllib.parse, xml.etree.ElementTree as ET, io
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; PUBLIC=ROOT/'apps/web/public/data'
LAYER='JEZ_hirise_soc_006_orthoMosaic_25cm_Eqc_latTs0_lon0_first_dd'
CAP=f'https://trek.nasa.gov/tiles/Mars/EQ/{LAYER}/1.0.0/WMTSCapabilities.xml'
BOUNDS=[77.40,18.42,77.48,18.49]
def fetch(url,limit=8*1024*1024):
    if urllib.parse.urlparse(url).hostname not in {'trek.nasa.gov','astro.arcgis.com'}: raise ValueError('Host not allowlisted')
    with urllib.request.urlopen(url,timeout=25) as r:
        b=r.read(limit+1)
    if len(b)>limit: raise ValueError('Download exceeds limit')
    return b

def main(filename='imagery', level='13'):
    DATA.mkdir(exist_ok=True);PUBLIC.mkdir(parents=True,exist_ok=True)
    
    raw=fetch(CAP);(DATA/(filename+'-wmts.xml')).write_bytes(raw)
    ns={'w':'http://www.opengis.net/wmts/1.0','o':'http://www.opengis.net/ows/1.1'}
    root=ET.fromstring(raw);layer=root.find('.//w:Layer',ns);ms=root.find('.//w:Contents/w:TileMatrixSet',ns)
    ident=lambda e:e.find('o:Identifier',ns).text
    matrix=[m for m in ms.findall('w:TileMatrix',ns) if ident(m)==level][0]
    mw=int(float(matrix.find('w:MatrixWidth',ns).text));mh=int(float(matrix.find('w:MatrixHeight',ns).text))
    tw=int(matrix.find('w:TileWidth',ns).text);th=int(matrix.find('w:TileHeight',ns).text)
    left,top=map(float,matrix.find('w:TopLeftCorner',ns).text.split());sx=360/mw;sy=180/mh
    west,south,east,north=BOUNDS;c0=math.floor((west-left)/sx);c1=math.floor((east-left)/sx);r0=math.floor((top-north)/sy);r1=math.floor((top-south)/sy)
    image=Image.new('RGBA',((c1-c0+1)*tw,(r1-r0+1)*th))
    template=layer.find('w:ResourceURL',ns).attrib['template'];tiles=[]
    for row in range(r0,r1+1):
        for col in range(c0,c1+1):
            url=template.format(Style=ident(layer.find('w:Style',ns)),TileMatrixSet=ident(ms),TileMatrix=ident(matrix),TileRow=row,TileCol=col)
            b=fetch(url);tile=Image.open(io.BytesIO(b)).convert('RGBA');image.paste(tile,((col-c0)*tw,(row-r0)*th));tiles.append({'url':url,'bytes':len(b)})
    px=lambda lon:(lon-left-c0*sx)/sx*tw
    py=lambda lat:(top-r0*sy-lat)/sy*th
    image=image.transform((1024,896),Image.Transform.EXTENT,(px(west),py(north),px(east),py(south)),Image.Resampling.BILINEAR)
    image.save(PUBLIC/(filename+'.png'))
    meta={'id':'nasa-trek-'+filename,'source_ids':['nasa-trek-hirise' if filename=='imagery' else 'nasa-trek-'+filename],'data_state':'OBSERVED','bounds':BOUNDS,'coordinate_system':ms.find('o:SupportedCRS',ns).text,'layer_id':ident(layer),'matrix':ident(matrix),'tile_size':[tw,th],'tiles':tiles,'acquired':'2026-11-14','credit':'NASA/JPL/USGS, Mars Trek','effective_resolution_degrees':[sx/tw,sy/th]}
    (DATA/(filename+'-metadata.json')).write_text(json.dumps(meta,indent=2));print('Imagery acquired:',len(tiles),'tiles')
if __name__=='__main__':
    import urllib.parse
    urllib.request.urlparse=urllib.parse.urlparse
    main()
