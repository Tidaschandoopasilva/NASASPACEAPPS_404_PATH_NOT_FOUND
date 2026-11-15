"""Mission routing on the rendered CTX triangle mesh."""
import math

import numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

from app.terrain import ROOT, load
from app.scout_cvar import field_prior, scout_options
from app.environment import PROFILES

WIDTH, HEIGHT = 226, 209
PUBLIC = ROOT / 'apps/web/public/data'


def plan_survey(center, radius, stops, seed, budget, max_slope, rover_site=None, condition="day", eva_goals=3, rover_goals=3, sortie=1, ground_verify=False, payload_kg=10., objective="relief", speed_scale=1.):
    terrain = load()[0]
    z = np.fromfile(PUBLIC / 'terrain-native.f32', dtype='<f4').reshape(HEIGHT, WIDTH)
    dx = terrain['dx_m'] * 95 / (WIDTH-1)
    dy = terrain['dy_m'] * 95 / (HEIGHT-1)
    y, x = np.indices(z.shape)
    distance_center = np.hypot((y-center[0]*(HEIGHT-1)/95)*dy,
                               (x-center[1]*(WIDTH-1)/95)*dx)
    habitat_y, habitat_x = stops[0]
    base_row = round(habitat_y*(HEIGHT-1)/95)
    base_col = round(habitat_x*(WIDTH-1)/95)
    base = base_row*WIDTH + base_col
    from_base_y, from_base_x = (y-base_row)*dy, (x-base_col)*dx
    vector_y = (center[0]*(HEIGHT-1)/95-base_row)*dy
    vector_x = (center[1]*(WIDTH-1)/95-base_col)*dx
    reach = math.hypot(vector_y,vector_x)
    along = (from_base_y*vector_y + from_base_x*vector_x)/max(1,reach)
    lateral = np.abs(from_base_x*vector_y - from_base_y*vector_x)/max(1,reach)
    zone = distance_center <= radius
    coverage_modes = [
        ('Cone', zone | ((along>=0)&(along<=reach)&(lateral<=40+.22*along))),
        ('Cylinder', zone | ((along>=-40)&(along<=reach+40)&(lateral<=max(120,radius*.35)))),
        ('Wide search', zone | ((along>=-radius)&(along<=reach+radius)&(lateral<=radius))),
    ]
    covered = zone & np.isfinite(z)
    gy, gx = np.gradient(z, dy, dx)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    rough = np.abs(z - uniform_filter(z, size=3))
    pixels = np.asarray(Image.open(PUBLIC/'imagery.png').convert('L').resize((WIDTH, HEIGHT)), dtype=float)
    texture = np.sqrt(np.maximum(0, uniform_filter(pixels**2,3)-uniform_filter(pixels,3)**2))
    risk = np.clip(.62*slope/max_slope + .25*rough/3 + .13*texture/15, 0, 1)
    foot = covered & np.isfinite(risk) & (slope <= max_slope) & (risk < .68)
    rover = covered & np.isfinite(risk) & (slope <= min(35,max_slope+10))
    alpha,beta = field_prior(np.nan_to_num(risk,nan=1).ravel(),condition)
    ids = np.arange(z.size).reshape(z.shape)

    def graph(mask, limit, time_weight=0.):
        a, b, costs, reverse = [], [], [], []
        for one,two,span in [
            ((slice(None,-1),slice(None)),(slice(1,None),slice(None)),dy),
            ((slice(None),slice(None,-1)),(slice(None),slice(1,None)),dx),
            ((slice(None,-1),slice(1,None)),(slice(1,None),slice(None,-1)),math.hypot(dx,dy)),
        ]:
            grade = np.degrees(np.arctan2(np.abs(z[two]-z[one]),span))
            valid = mask[one] & mask[two] & (grade <= limit)
            a.extend(ids[one][valid])
            b.extend(ids[two][valid])
            probability = alpha[ids[two][valid]]/(alpha[ids[two][valid]]+beta[ids[two][valid]])
            costs.extend((-np.log1p(-probability)+time_weight*span).tolist())
            reverse_probability = alpha[ids[one][valid]]/(alpha[ids[one][valid]]+beta[ids[one][valid]])
            reverse.extend((-np.log1p(-reverse_probability)+time_weight*span).tolist())
        return coo_matrix((costs+reverse,(a+b,b+a)),shape=(z.size,z.size)).tocsr()

    def coord(i):
        r,c = divmod(int(i),WIDTH)
        return [r*95/(HEIGHT-1),c*95/(WIDTH-1)]

    def path_to(parent, origin, goal):
        route = [int(goal)]
        while route[-1] != origin:
            previous = int(parent[route[-1]])
            if previous < 0:
                return []
            route.append(previous)
        return route[::-1]

    safe = np.isfinite(risk) & (slope<=max_slope) & (risk<.68)
    survey_attempts = []
    covered = np.zeros_like(zone)
    for mode, footprint in coverage_modes:
        covered |= footprint & np.isfinite(z)
        foot = covered & safe
        rover = covered & np.isfinite(risk) & (slope<=min(35,max_slope+10))
        walking_graph = graph(foot,max_slope)
        walk_cost, _ = dijkstra(walking_graph,indices=base,return_predecessors=True)
        reachable = int(np.count_nonzero(zone.ravel() & np.isfinite(walk_cost) & (walk_cost>0)))
        survey_attempts.append({'mode':mode,'reachable_cells':reachable})
        if reachable >= max(1,eva_goals)*8:
            break
    scans = [coord(base)]
    for attempt in survey_attempts:
        footprint = dict(coverage_modes)[attempt['mode']]
        for r in range(0,HEIGHT,6):
            columns = np.flatnonzero(footprint[r] & np.isfinite(z[r]))
            if len(columns):
                ends = [int(ids[r,columns[0]]),int(ids[r,columns[-1]])]
                scans.extend(map(coord,ends if (r//6)%2==0 else ends[::-1]))
    scans.append(coord(base))
    readings = []
    for index, (grid_row, grid_col) in enumerate(scans):
        row = round(grid_row*(HEIGHT-1)/95)
        col = round(grid_col*(WIDTH-1)/95)
        if not np.isfinite([z[row,col], slope[row,col], risk[row,col]]).all():
            continue
        readings.append({
            'cell': [grid_row,grid_col],
            'progress': .35*index/max(1,len(scans)-1),
            'elevation_m': round(float(z[row,col]),1),
            'slope_deg': round(float(slope[row,col]),1),
            'risk_index': round(float(risk[row,col])*100),
        })
    heat = np.where(covered,np.nan_to_num(np.maximum(risk,np.where(foot,0,.85)),nan=1),-1)
    result = {'mesh_survey':True,'before':{'path':[]},'uav_path':scans,'uav_readings':readings,'rover_path':[],
              'monitor_checks':[],'sites':[],'hazard':np.rint(heat*100).astype(int).ravel().tolist(),
              'hazard_shape':[HEIGHT,WIDTH],'survey_cells':int(covered.sum()),
              'survey_attempts':survey_attempts,'survey_mode':mode,'base':coord(base),
              'source_ids':['usgs-ctx-dem','nasa-trek-hirise'],'data_state':'SIMULATED',
              'events':[{'t':0,'label':'UAV survey'},{'t':.35,'label':'Independent rover departure'},
                        {'t':.65,'label':'Astronaut departure and UAV monitoring'}]}
    _, home_parent = dijkstra(walking_graph.T.tocsr(),indices=base,return_predecessors=True)
    ground_graph = graph(rover,min(35,max_slope+10),.0002)
    rover_cost, rover_parent = dijkstra(ground_graph,indices=base,return_predecessors=True)
    relief = z - uniform_filter(z, size=11)
    signals = {'relief': np.abs(relief)/10, 'texture': texture/15}
    interest = np.nan_to_num(signals[objective]).ravel()

    spacing_m = max(40., radius*.30)

    def discover(mask, cost, count, existing=(), preferred=None):
        candidates = np.flatnonzero(zone.ravel() & mask & np.isfinite(cost) & (cost>0))
        priority = interest[candidates]
        if preferred is not None:
            priority = priority + preferred[candidates]*(1+priority.max(initial=0))
        ranked = candidates[np.argsort(-priority,kind='stable')]
        chosen = []
        for spacing in (spacing_m, spacing_m*.65, spacing_m*.4, dx):
            for cell in ranked:
                if len(chosen)>=count:
                    return chosen
                r,c = divmod(int(cell),WIDTH)
                if all(math.hypot((r-i//WIDTH)*dy,(c-i%WIDTH)*dx)>=spacing
                       for i in [*existing,*chosen]):
                    chosen.append(int(cell))
        return chosen

    human_sites = discover(foot.ravel(),walk_cost,eva_goals)
    robot_sites = discover(rover.ravel(),rover_cost,rover_goals,human_sites,(~foot).ravel())
    aerial_only = covered.ravel() & ~np.isfinite(walk_cost) & ~np.isfinite(rover_cost)
    uav_sites = discover(aerial_only,np.ones(z.size),2,[*human_sites,*robot_sites],
                         (z>z.ravel()[base]).ravel())
    if uav_sites:
        survey = result['uav_path']
        survey[-1:-1] = [coord(vertex) for vertex in uav_sites]
        readings[:] = [
            {'cell':cell,'progress':.35*index/(len(survey)-1),
             'elevation_m':round(float(z[row,col]),1),
             'slope_deg':round(float(slope[row,col]),1),
             'risk_index':round(float(risk[row,col])*100)}
            for index,cell in enumerate(survey)
            for row,col in [(round(cell[0]*(HEIGHT-1)/95),round(cell[1]*(WIDTH-1)/95))]
            if np.isfinite([z[row,col],slope[row,col],risk[row,col]]).all()
        ]
    sites = [{'id':cell,'cell':coord(cell),'kind':kind,'risk':float(risk.ravel()[cell])}
             for kind,cells in [('EVA',human_sites),('ROVER',robot_sites),('UAV',uav_sites)] for cell in cells]
    def length(route):
        return sum(math.hypot((b//WIDTH-a//WIDTH)*dy,(b%WIDTH-a%WIDTH)*dx)
                   for a,b in zip(route,route[1:]))

    speed = PROFILES[condition].speed*speed_scale
    def effort(route):
        total = 0.
        for start, end in zip(route, route[1:]):
            horizontal = math.hypot((end//WIDTH-start//WIDTH)*dy,(end%WIDTH-start%WIDTH)*dx)
            if horizontal:
                grade = float(z.ravel()[end]-z.ravel()[start])/horizontal
                total += horizontal*(1+3*abs(grade)+max(0,grade))*(1+payload_kg/80)
        return total

    max_distance = budget*48*speed
    
    sorties = []
    pending = []
    distance = 0.
    for target in human_sites:
        outbound = path_to(home_parent,base,target)[::-1]
        _, parents = dijkstra(walking_graph,indices=base,return_predecessors=True)
        leg = path_to(parents,base,target)
        loop_distance = effort(leg)+effort(outbound)+180*speed
        if not leg or not outbound or loop_distance>max_distance:
            continue
        if pending and distance+loop_distance>max_distance:
            sorties.append(pending)
            pending,distance = [],0.
        pending.append(target)
        distance += loop_distance
    if pending:
        sorties.append(pending)
    active_goals = sorties[0] if sorties else []
    alternatives = []
    rejected_routes = []
    for time_weight in (0., .00002, .0002, .002):
        network = graph(foot,max_slope,time_weight)
        for targets in (active_goals, active_goals[::-1]):
            itinerary, current = [base], base
            for target in targets:
                _, predecessors = dijkstra(network, indices=current, return_predecessors=True)
                leg = path_to(predecessors,current,target)
                home = path_to(home_parent,base,target)[::-1]
                if leg and home and effort(itinerary+leg[1:]+home[1:]) + 60*speed*3*(len(set(itinerary+leg)&set(active_goals))) <= max_distance:
                    itinerary.extend(leg[1:])
                    current = target
                else:
                    rejected_routes.append({'target':coord(target),'distance_weight':time_weight,
                                            'reason':'Missing outbound or return connection' if not leg or not home
                                            else 'Round trip and science exceed the usable sortie time'})
            if current != base:
                home = path_to(home_parent,base,current)[::-1]
                option = (itinerary, itinerary+home[1:])
                if option not in alternatives:
                    alternatives.append(option)
    best_count = max((sum(site in route for site in human_sites) for _,route in alternatives),default=0)
    rejected_routes.extend({'distance_m':round(length(option[1]),1),
                            'reason':'Visits fewer science stops than another candidate','path':list(map(coord,option[1]))}
                           for option in alternatives if sum(site in option[1] for site in human_sites)<best_count)
    alternatives = [option for option in alternatives
                    if sum(site in option[1] for site in human_sites)==best_count]
    scores, probe_log = scout_options([route for _,route in alternatives],alpha,beta,seed)
    picked = min(range(len(scores)),key=lambda i:scores[i]+.1*length(alternatives[i][1])/max_distance) if scores else None
    out, initial = alternatives[picked] if picked is not None else ([],[])
    
    selected_robot = rover_site if rover_site in robot_sites else None
    robot_targets = ([selected_robot] + [target for target in robot_sites if target != selected_robot]
                     if selected_robot is not None else robot_sites)
    rover_route = list(initial) if ground_verify and initial else [base]
    current = base
    for target in robot_targets:
        if target in rover_route:
            continue
        _, parents = dijkstra(ground_graph,indices=current,return_predecessors=True)
        leg = path_to(parents,current,target)
        if leg:
            rover_route.extend(leg[1:])
            current = target
    if current!=base:
        _, parents = dijkstra(ground_graph,indices=current,return_predecessors=True)
        rover_route.extend(path_to(parents,current,base)[1:])
    if len(rover_route)==1:
        rover_route=[]
    final = initial
    checks = []
    changed = None
    change_progress = None
    if len(out)>5 and condition in ('day','dust'):
        rng = np.random.default_rng(seed)
        indices = sorted(rng.choice(range(2,len(out)-1),min(6,len(out)-3),replace=False))
        for index in indices:
            warning = changed is None and rng.random()<.24
            checks.append({'cell':coord(out[index]),'warning':bool(warning),'fraction':float(index/max(1,len(initial)-1))})
            if warning:
                changed = out[index]
                
                travelled = out[:index]
                updated = foot.copy()
                updated.ravel()[changed] = False
                heat.ravel()[changed] = 1
                _, return_parents = dijkstra(graph(updated,max_slope).T.tocsr(), indices=base,
                                              return_predecessors=True)
                home = path_to(return_parents,base,travelled[-1])[::-1]
                
                known = set(initial)
                if not home or not set(home).issubset(known):
                    home = travelled[::-1]
                final = travelled + home[1:]
                change_progress = .65 + .35*(len(travelled)-1)/max(1,len(final)-1)
                break
    if changed is not None:
        for check in checks:
            if not check['warning']:
                check['fraction'] *= (len(initial)-1)/max(1,len(final)-1)
    
    
    campaign = list(final)
    completed_sorties = [final] if final else []
    sortie_offsets = [0] if final else []
    hold_index = None
    if changed is not None and campaign:
        hold_index = len(campaign)-1
        campaign.extend([base]*12)
    departures = []
    sortie_speeds = [speed] if final else []
    weather_hold = None
    _, outbound_parent = dijkstra(walking_graph,indices=base,return_predecessors=True)
    fast_graph = graph(foot,max_slope,1.)
    _, fast_out = dijkstra(fast_graph,indices=base,return_predecessors=True)
    _, fast_home = dijkstra(fast_graph.T.tocsr(),indices=base,return_predecessors=True)
    for goal in human_sites:
        if goal in campaign:
            continue
        leg = path_to(outbound_parent,base,goal)
        home = path_to(home_parent,base,goal)[::-1]
        if not leg or not home:
            continue
        loop = leg+home[1:]
        fast_leg = path_to(fast_out,base,goal)
        fast_return = path_to(fast_home,base,goal)[::-1]
        if fast_leg and fast_return:
            alternative = fast_leg+fast_return[1:]
            if effort(alternative)+180*speed_scale*len(set(alternative)&set(human_sites)) < effort(loop)+180*speed_scale*len(set(loop)&set(human_sites)):
                loop = alternative
        stop_minutes = 3*len(set(loop)&set(human_sites))
        sortie_speed = speed
        if effort(loop)/(60*speed)+stop_minutes > budget*.8:
            if condition in ("night","heat"):
                continue
            sortie_speed = speed_scale
            if effort(loop)/(60*sortie_speed)+stop_minutes > budget*.8:
                continue
            if weather_hold is None:
                if not campaign:
                    campaign.append(base)
                weather_hold = len(campaign)-1
                campaign.extend([base]*18)
        sortie_speeds.append(sortie_speed)
        if campaign:
            campaign.extend([base]*3)
            departures.append(len(campaign)-1)
            sortie_offsets.append(len(campaign)-1)
            campaign.extend(loop[1:])
        else:
            sortie_offsets.append(0)
            campaign.extend(loop)
        completed_sorties.append(loop)
    if change_progress is not None:
        change_progress = .65+.35*(len(travelled)-1)/max(1,len(campaign)-1)
    final = campaign
    outstanding = [goal for goal in human_sites if goal not in final]
    route = lambda seq: list(map(coord,seq))
    after = {'path':route(final),'feasible':bool(final),
             'reason':('Campaign pending · remaining targets need a feasible sortie' if outstanding else 'All assigned EVA targets visited; crew returned to base') if final else 'No EVA site met slope, risk and return limits. Rover science can still proceed.',
             'meters':length(final),'minutes':sum(effort(loop)/(60*pace)+3*len(set(loop)&set(human_sites)) for loop,pace in zip(completed_sorties,sortie_speeds)),
             'return_margin_min':budget-max((effort(loop)/(60*pace)+3*len(set(loop)&set(human_sites)) for loop,pace in zip(completed_sorties,sortie_speeds)),default=0)}
    for number, site in enumerate(sites,1):
        row, col = divmod(site['id'], WIDTH)
        east, north = (col-base_col)*dx, (base_row-row)*dy
        site['elevation_m'] = round(float(z[row,col]),1)
        site['height_above_habitat_m'] = round(float(z[row,col]-z.ravel()[base]),1)
        site['bearing_deg'] = round(math.degrees(math.atan2(east,north))%360,1)
        site['habitat_distance_m'] = round(math.hypot(east,north),1)
        site['slope_deg'] = round(float(slope[row,col]),1)
        signal = f"{abs(relief[row,col]):.1f} m from the surrounding ~220 m DEM window mean" if objective=='relief' else f"{texture[row,col]:.1f} grayscale levels of local image contrast (standard deviation)"
        site['why'] = f"{'Compare landform relief' if objective=='relief' else 'Investigate surface texture'}: {signal}; slope {site['slope_deg']}°."
        site['science_signal'] = float(interest[site['id']])
        site['label'] = f"{site['kind']} {number:02d}"
        vertex = site['id']
        visited_route = final if site['kind']=='EVA' else rover_route
        site['visit_fraction'] = visited_route.index(vertex)/max(1,len(visited_route)-1) if vertex in visited_route else None
        if site['kind']=='UAV':
            site['visit_fraction'] = scans.index(site['cell'])/max(1,len(scans)-1)
            site['status'] = 'UAV only · no eligible ground route'
            continue
        site['sortie'] = next((i for i, goals in enumerate(sorties,1) if vertex in goals),None)
        site['status'] = ('Scheduled' if vertex in visited_route else
                          'Rover dispatch required' if site['kind']=='ROVER' else
                          'Interrupted by visibility closure' if vertex in initial else
                          f"Planned for EVA sortie {site['sortie']}" if site['sortie'] and site['sortie']!=sortie else
                          'Outside the chosen return-budget itinerary')
    
    checkpoints = []
    if rover_route:
        distinct_indices = {}
        for index, vertex in enumerate(rover_route):
            if vertex != base and vertex not in robot_targets:
                distinct_indices.setdefault(vertex,index)
        positions = list(distinct_indices.values())
        for sample in np.linspace(0,len(positions)-1,min(12,len(positions)),dtype=int):
            index = positions[sample]
            vertex = rover_route[index]
            checkpoints.append({'cell':coord(vertex),'fraction':float(index/max(1,len(rover_route)-1)),
                                'slope_deg':float(slope.ravel()[vertex]),
                                'relief_m':float(rough.ravel()[vertex]),
                                'risk':float(risk.ravel()[vertex]),
                                'eva_eligible':bool(foot.ravel()[vertex])})
    if not ground_verify:
        result['events'] = [{'t':0,'label':'UAV survey and return'},
                            {'t':.35,'label':'Rover departure and UAV-escorted EVA'},
                            {'t':1,'label':'Mission complete'}]
        if change_progress is not None:
            change_progress = .35 + .65*(change_progress-.65)/.35
    start = .65 if ground_verify else .35
    events = [
        {'t':0,'label':'UAV surveys Jezero'},
        {'t':.35,'label':'Rover departs' if rover_route else 'UAV survey complete'},
        {'t':start,'label':'Crew departs · UAV escort' if final else 'No feasible EVA'},
    ]
    if hold_index is not None:
        events.extend([
            {'t':change_progress,'label':'Dust warning · crew returning to habitat'},
            {'t':start+(1-start)*hold_index/max(1,len(final)-1),
             'label':'Crew at habitat · waiting for visibility clearance' if departures else 'Crew returned to habitat'},
        ])
    if weather_hold is not None:
        events.extend([
            {'t':start+(1-start)*weather_hold/max(1,len(final)-1),'label':'Crew at habitat · waiting for clear-day conditions'},
            {'t':start+(1-start)*(weather_hold+18)/max(1,len(final)-1),'label':'Clear conditions · preparing next EVA sortie'},
        ])
    for number, index in enumerate(departures):
        events.append({'t':start+(1-start)*index/max(1,len(final)-1),
                       'label':'Visibility cleared · crew retries with UAV escort' if number==0 and hold_index is not None else 'Next EVA sortie · crew departs with UAV escort'})
    outstanding_rover = [goal for goal in robot_targets if goal not in rover_route]
    missing_eva = max(0,eva_goals-len(human_sites))
    missing_rover = max(0,rover_goals-len(robot_targets))
    complete = not (outstanding or outstanding_rover or missing_eva or missing_rover)
    events.append({'t':1,'label':'Mission complete · all targets visited and assets returned' if complete else
                   f'Campaign pending · {len(outstanding)+missing_eva} EVA and {len(outstanding_rover)+missing_rover} rover objectives remaining'})
    result['events'] = sorted(events,key=lambda event:event['t'])
    sortie_details = []
    for number,(loop,pace) in enumerate(zip(completed_sorties,sortie_speeds),1):
        moving_minutes = effort(loop)/(60*pace)
        science_minutes = 3*len(set(loop)&set(human_sites))
        elapsed = [0.]
        visited = set()
        for a, b in zip(loop, loop[1:]):
            stop = 3 if b in human_sites and b not in visited else 0
            visited.add(b)
            elapsed.append(round(elapsed[-1] + effort([a,b])/(60*pace) + stop, 6))
        sortie_details.append({'sortie':number,'route_index':sortie_offsets[number-1],
                               'elapsed_minutes':elapsed,'distance_m':round(length(loop),1),
                               'pace_m_s':pace,'walking_minutes':round(moving_minutes,2),
                               'science_minutes':science_minutes,
                               'remaining_minutes':round(budget-moving_minutes-science_minutes,2),
                               'required_reserve_minutes':budget*.2})
    timeline = [dict(event, asset='Mission', detail='Simulated playback milestone') for event in result['events']]
    timeline += [{'t':sample['progress'],'asset':'UAV','label':'Terrain sample',
                  'detail':f"Grid {sample['cell'][0]:.1f}/{sample['cell'][1]:.1f} · CTX elevation {sample['elevation_m']} m · slope {sample['slope_deg']}° · risk index {sample['risk_index']}/100"}
                 for sample in readings]
    for site in sites:
        kind = site['kind']
        eligibility = ('Crew slope, risk, and habitat connectivity checks passed' if kind=='EVA' else
                       'Rover ground graph permits access on a separate science route' if kind=='ROVER' else
                       'Neither ground graph connects this site to the habitat')
        timeline.append({'t':.35,'asset':kind,'label':site['label']+' selected',
                         'detail':f"{site['why']} {eligibility}. {site['height_above_habitat_m']} m relative to habitat."})
        fraction = site['visit_fraction']
        if fraction is not None:
            begin, end = (0,.35) if kind=='UAV' else (start,1) if kind=='EVA' else (.35, .65 if ground_verify else 1)
            timeline.append({'t':begin+(end-begin)*fraction,'asset':kind,
                             'label':site['label']+' visited','detail':'First arrival on the assigned route'})
        else:
            timeline.append({'t':1,'asset':kind,'label':site['label']+' outstanding','detail':site['status']})
    for check in checkpoints:
        timeline.append({'t':.35+(.30 if ground_verify else .65)*check['fraction'],
                         'asset':'ROVER','label':'Ground checkpoint',
                         'detail':f"Slope {check['slope_deg']}° · CTX relief {check['relief_m']} m · risk {check['risk']*100:.1f}/100"})
    fallback_path = [coord(base), *map(coord,outstanding), coord(base)] if outstanding else []
    if fallback_path:
        follow_up_start = .85
        for entry in [*timeline,*result['events']]:
            entry['t'] *= follow_up_start
        for entry in [*timeline,*result['events']]:
            if entry['t']==follow_up_start:
                entry['label'] = 'Ground phase finalized' if entry.get('asset','Mission')=='Mission' else entry['label']
        follow_up = [{'t':follow_up_start,'asset':'UAV','label':'UAV follow-up departs after final EVA return',
                      'detail':'Inspect objectives the crew could not reach within the sortie constraints.'}]
        for index, goal in enumerate(outstanding,1):
            site = next(site for site in sites if site['id']==goal)
            site['uav_inspection_t'] = follow_up_start+(1-follow_up_start)*index/(len(fallback_path)-1)
            follow_up.append({'t':site['uav_inspection_t'],'asset':'UAV','label':site['label']+' inspected by UAV',
                              'detail':'Simulated aerial inspection. Crew visit remains outstanding.'})
        follow_up.append({'t':1,'asset':'UAV','label':'Ingenuity returned · aerial follow-up complete',
                          'detail':'Ground objectives remain pending.'})
        timeline.extend(follow_up)
        result['events'].extend(follow_up)
    timeline.sort(key=lambda event:event['t'])
    inside = zone.ravel()
    covered_inside = inside & covered.ravel()
    slope_ok = slope.ravel() <= max_slope
    risk_ok = risk.ravel() < .68
    coverage_checks = {
        'science_circle_cells':int(inside.sum()),
        'outside_survey':int((inside & ~covered.ravel()).sum()),
        'eva_slope_excluded':int((covered_inside & ~slope_ok).sum()),
        'eva_risk_excluded':int((covered_inside & slope_ok & ~risk_ok).sum()),
        'eva_disconnected':int((inside & foot.ravel() & ~np.isfinite(walk_cost)).sum()),
        'eva_reachable':int((inside & np.isfinite(walk_cost)).sum()),
        'rover_reachable':int((inside & np.isfinite(rover_cost)).sum()),
    }
    audit = {'coverage_checks':coverage_checks,'timeline':timeline,'sorties':sortie_details,'minimum_target_spacing_m':spacing_m,'rejected_routes':rejected_routes,
             'rover_route_m':round(length(rover_route),1),'route_candidates':[
                 {'distance_m':round(length(option[1]),1),'path':route(option[1]),'tail_loss':score,'ranking_score':round(score+.1*length(option[1])/max_distance,5),'selected':index==picked,
                  'reason':'Best combined tail-risk and distance score' if index==picked else 'Higher combined tail-risk and distance score'}
                 for index,(option,score) in enumerate(zip(alternatives,scores))],
             'formulas':[
                 'Risk index = clamp(0.62 × slope / EVA slope limit + 0.25 × local DEM residual / 3 m + 0.13 × image contrast / 15, 0, 1).',
                 'Mesh edge cost = −log(1 − model probability) + time weight × horizontal distance.',
                 'Walking minutes sum edge distance × (1 + 3 × absolute grade + uphill grade) × (1 + load kg / 80), divided by pace and 60.',
                 'Science takes 3 minutes per stop. Time remaining must meet the 20% return reserve.']}
    return {**result,'uav_follow_up_path':fallback_path,'decision_audit':audit,'ground_checks' :checkpoints,'ground_verify':ground_verify,'condition':condition,'sortie':sortie,'sortie_count':len(completed_sorties),'campaign':True,'outstanding_eva':len(outstanding),'campaign_complete':complete,'outstanding_rover':len(outstanding_rover),'unassigned_eva':missing_eva,'unassigned_rover':missing_rover,'scout_updates':[{**entry,'cell':coord(entry['vertex'])} for entry in probe_log],
            'posterior_cvar90':scores[picked] if picked is not None else None,'base':coord(base),'sites':sites,'rover_site':selected_robot,
            'aerial':{'path':route(initial),'feasible':bool(initial or rover_route),'reason':after['reason']},
            'rover_path':route(rover_route),'after':after,
            'monitor_change_cell':coord(changed) if changed is not None else None,
            'monitor_checks':checks,'change_progress':change_progress,
            'change_source':'https://www.jpl.nasa.gov/news/nasas-perseverance-studies-the-wild-winds-of-jezero-crater/',
            'change_model':'Simulated dust-related visibility closure inspired by recorded Jezero gust-lifting events',
            'hazard_updated':np.rint(heat*100).astype(int).ravel().tolist() if changed is not None else None}
