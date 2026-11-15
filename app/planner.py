"""Planning accepts only public terrain and belief arrays. No simulator import."""
import heapq, math
import numpy as np

def astar(z,slope,valid,belief,uncertainty,start,goal,dx,dy,mode='risk',w_u=1,max_slope=20):
    h,w=z.shape;start=tuple(start);goal=tuple(goal)
    def ok(a):return 0<=a[0]<h and 0<=a[1]<w and bool(valid[a]) and slope[a]<=max_slope
    if not ok(start) or not ok(goal):return None
    def heuristic(a):return math.hypot((a[0]-goal[0])*dy,(a[1]-goal[1])*dx)
    q=[(heuristic(start),0,start)];cost={start:0};parent={}
    while q:
        _,g,a=heapq.heappop(q)
        if g>cost.get(a,float('inf')):continue
        if a==goal:
            path=[a]
            while a in parent:a=parent[a];path.append(a)
            return list(reversed(path))
        for dr,dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            b=(a[0]+dr,a[1]+dc)
            if not ok(b):continue
            if dr and dc and (not ok((a[0]+dr,a[1])) or not ok((a[0],a[1]+dc))):continue
            d=math.sqrt((dr*dy)**2+(dc*dx)**2+float(z[b]-z[a])**2)
            theta=max(float(slope[a]),float(slope[b]));edge=d if mode=='shortest' else d*(1+2*(theta/max_slope)**2+4*(belief[a]+belief[b])/2+w_u*(uncertainty[a]+uncertainty[b])/2)
            ng=g+edge
            if ng<cost.get(b,float('inf')):cost[b]=ng;parent[b]=a;heapq.heappush(q,(ng+heuristic(b),ng,b))
    return None

def mission(t,z,slope,valid,belief,uncertainty,points,mode='risk',budget=180,max_slope=20,w_u=1):
    path=[];legs=[];distance=0;seconds=0
    for start,end in zip(points,points[1:]+points[:1]):
        leg=astar(z,slope,valid,belief,uncertainty,start,end,t['dx_m'],t['dy_m'],mode,w_u,max_slope)
        if leg is None:return {'feasible':False,'reason':'no feasible path under these model assumptions','path':[]}
        length=0;duration=0
        for a,b in zip(leg,leg[1:]):
            d=math.sqrt(((b[0]-a[0])*t['dy_m'])**2+((b[1]-a[1])*t['dx_m'])**2+float(z[b]-z[a])**2);length+=d;duration+=d*(1+3*float(slope[b])/20)
        path+=leg if not path else leg[1:];legs.append({'from':list(start),'to':list(end),'meters':length,'minutes':duration/60});distance+=length;seconds+=duration
    feasible=seconds/60<=budget*.8
    return {'feasible':feasible,'reason':'Return included; 20% time reserve enforced' if feasible else 'no feasible path under these model assumptions: EVA budget + reserve exceeded','path':[list(p) for p in path],'legs':legs,'meters':distance,'minutes':seconds/60,'return_margin_min':budget-seconds/60,'reserve_min':budget*.2,'mode':mode}
