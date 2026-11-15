from pathlib import Path
import json,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def load():
    t=json.loads((ROOT/'apps/web/public/data/terrain.json').read_text())
    return t,np.array(t['elevation']),np.array(t['slope']),np.array(t['valid'])
def world(t,r,c):return [c*t['dx_m'],r*t['dy_m']]
def pixel(t,x,y):return [round(y/t['dy_m']),round(x/t['dx_m'])]
def planetary(t,r,c):
    w,s,e,n=t['bounds'];return [n-r*t['dy_m']/t['radius_m']*180/math.pi,w+c*t['dx_m']/(t['radius_m']*math.cos(math.radians(t.get('standard_parallel_deg',0))))*180/math.pi]
def slopes(z,dx,dy):
    gy,gx=np.gradient(z,dy,dx);return np.degrees(np.arctan(np.hypot(gx,gy)))
def priors(slope):return np.clip(.06+.24*(slope/20)**2,.06,.6)
def corridors(shape):
    y,x=np.indices(shape);return [((x-42)**2/13**2+(y-47)**2/18**2)<1,((x-62)**2/12**2+(y-26)**2/12**2)<1,((x-27)**2/10**2+(y-70)**2/12**2)<1]
