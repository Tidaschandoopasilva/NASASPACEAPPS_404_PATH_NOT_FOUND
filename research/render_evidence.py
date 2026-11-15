"""Create scientific figures from acquired data and saved model evaluations."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from app.terrain import ROOT,load

def main():
    out=ROOT/'docs/evidence';t,z,s,v=load();w,so,e,n=t['bounds'];xx=np.linspace(w,e,96);yy=np.linspace(n,so,96)
    fig,ax=plt.subplots(figsize=(10,8));ax.imshow(Image.open(ROOT/'apps/web/public/data/imagery.png'),extent=[w,e,so,n]);cs=ax.contour(xx,yy,z-z.min(),levels=8,colors='#6cdde2',linewidths=.7);ax.clabel(cs,fontsize=7,fmt='%d m');ax.set(xlabel='East longitude (degrees)',ylabel='Planetocentric latitude (degrees)',title='Jezero: NASA HiRISE imagery + USGS CTX relative relief\nCommon georeferenced ROI; contours above crop minimum, not absolute datum');fig.text(.1,.015,'NASA/JPL/USGS • Real observed imagery and derived CTX elevations • Coordinate alignment check, not precision co-registration validation',fontsize=8);fig.savefig(out/'dem-alignment-v2.png',dpi=160,bbox_inches='tight');plt.close(fig)
    report=json.loads((ROOT/'models/svnet_v1/evaluation.json').read_text());policies=report['policies'];fig,ax=plt.subplots(figsize=(11,5));means=[p['utility'] for p in policies];err=np.array([[p['utility']-p['utility_ci95'][0] for p in policies],[p['utility_ci95'][1]-p['utility'] for p in policies]]);ax.barh([p['policy'] for p in policies],means,xerr=err,color=['#92a7b9']*4+['#21868c','#d49a54','#d49a54']);ax.axvline(0,color='#555',lw=.7);ax.set(xlabel='Mean simulated utility (paired scenarios; bootstrap 95% intervals)',title='404-SVNet: mixed results on 100 held-out Jezero-derived scenarios');fig.tight_layout();fig.savefig(out/'svnet-policy-comparison.png',dpi=150);plt.close(fig)
if __name__=='__main__':main()
