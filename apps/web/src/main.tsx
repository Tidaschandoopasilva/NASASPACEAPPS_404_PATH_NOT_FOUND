import { conditionInfo, equipmentLabels, sectorStyles } from './conditions';
import HabitatHud from './HabitatHud';
import SVNetConsole from './SVNetConsole';
import SciencePhotos from './SciencePhotos';
import React, { useState, useEffect, useMemo, useRef, Suspense } from 'react';
import { createRoot } from 'react-dom/client';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Line, Html, Stars } from '@react-three/drei';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import Map from 'ol/Map';
import View from 'ol/View';
import ImageLayer from 'ol/layer/Image';
import ImageStatic from 'ol/source/ImageStatic';
import Projection from 'ol/proj/Projection';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Feature from 'ol/Feature';
import { LineString, Point, Polygon } from 'ol/geom';
import { Style, Stroke, Circle as CircleStyle, Fill, Text } from 'ol/style';
import 'ol/ol.css';
import './style.css';
const NOTE = 'Research simulator; not validated for mission operations.';
const INITIAL = [[68, 27], [40, 34], [42, 61]];
async function api(path: string, body?: any) { const res = await fetch('/api/v1/' + path, body ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) } : {}); if (!res.ok) {
    const payload = await res.json().catch(() => ({}));
    throw new Error(typeof payload.detail === 'string' ? payload.detail : `${path}: ${res.status}`);
} return res.json(); }
function download(name: string, content: string, type = 'application/json') { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([content], { type })); a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000); }
function coords(t: any, p: number[], ex = 1): [
    number,
    number,
    number
] {
    const native = t.nativeMesh as Float32Array | undefined;
    const row = Math.round(p[0] * 208 / 95), col = Math.round(p[1] * 225 / 95);
    const elevation = native?.[row * 226 + col] ?? t.elevation[Math.round(p[0])][Math.round(p[1])];
    return [(p[1] - 47.5) * t.dx_m / 100, (elevation - t.height_min_m) * ex / 100 + .06, (p[0] - 47.5) * t.dy_m / 100];
}
const modelLoader = new GLTFLoader().setDRACOLoader(new DRACOLoader().setDecoderPath("/draco/"));
const modelNames: Record<string, string> = {
    astronaut: 'EVA astronaut', rover: 'Perseverance', ingenuity: 'Ingenuity'
};
function Model({ kind }: {
    kind: string;
}) {
    const [object, setObject] = useState<THREE.Group | null>(null);
    const [failed, setFailed] = useState(false);
    useEffect(() => {
        let mounted = true;
        modelLoader.load('/models/' + kind + '.glb', ({ scene }) => {
            if (!mounted)
                return;
            const bounds = new THREE.Box3().setFromObject(scene);
            const size = bounds.getSize(new THREE.Vector3());
            scene.position.sub(bounds.getCenter(new THREE.Vector3()));
            scene.position.y += size.y / 2;
            const group = new THREE.Group();
            group.add(scene);
            group.scale.setScalar(({ rover: .15, astronaut: .09, ingenuity: .07 }[kind] ?? .09) / Math.max(size.x, size.y, size.z));
            setObject(group);
        }, undefined, () => { if (mounted)
            setFailed(true); });
        return () => { mounted = false; };
    }, [kind]);
    return object ? <primitive object={object}/> : failed ?
        <Html center><span className="scene-tag">{modelNames[kind]}: model unavailable</span></Html> : null;
}
function Terrain({ t, ex, slope, wire }: {
    t: any;
    ex: number;
    slope: boolean;
    wire: boolean;
}) {
    const [texture, setTexture] = useState<THREE.Texture | null>(null);
    useEffect(() => { new THREE.TextureLoader().load('/data/imagery.png', tx => { tx.colorSpace = THREE.SRGBColorSpace; setTexture(tx); }); }, []);
    const [native, setNative] = useState<Float32Array | null>(null);
    useEffect(() => { if (t.data_state === 'DERIVED')
        fetch('/data/terrain-native.f32').then(r => { if (!r.ok)
            throw Error(); return r.arrayBuffer(); }).then(b => { if (b.byteLength === 226 * 209 * 4)
            setNative(new Float32Array(b)); }).catch(() => { }); }, [t.data_state]);
    const geom = useMemo(() => {
        const g = new THREE.BufferGeometry();
        const pos: number[] = [];
        const colors: number[] = [];
        const uv: number[] = [];
        const idx: number[] = [];
        const fine = native && !slope && !wire;
        const width = fine ? 226 : 96, height = fine ? 209 : 96;
        for (let r = 0; r < height; r++)
            for (let c = 0; c < width; c++) {
                const row = Math.round(r * 95 / (height - 1)), col = Math.round(c * 95 / (width - 1));
                const p = coords(t, [row, col], ex);
                if (fine) {
                    p[0] = (c / (width - 1) - .5) * 95 * t.dx_m / 100;
                    p[2] = (r / (height - 1) - .5) * 95 * t.dy_m / 100;
                    p[1] = (native[r * width + c] - t.height_min_m) * ex / 100 + .06;
                }
                pos.push(...p);
                uv.push(c / (width - 1), 1 - r / (height - 1));
                const s = t.slope[row][col];
                const shade = new THREE.Color(slope ? (s > 10 ? '#d46d4b' : s > 4 ? '#e9c994' : '#627e87') : '#b18c70');
                shade.multiplyScalar(.64 + Math.min(.45, (t.elevation[row][col] - t.height_min_m) / Math.max(1, t.height_max_m - t.height_min_m) * .45));
                colors.push(shade.r, shade.g, shade.b);
                if (r < height - 1 && c < width - 1) {
                    const a = r * width + c;
                    const ok = fine ? [a, a + 1, a + width, a + width + 1].every(i => Number.isFinite(native[i])) : t.valid[r][c] && t.valid[r + 1][c] && t.valid[r][c + 1] && t.valid[r + 1][c + 1];
                    if (ok)
                        idx.push(a, a + width, a + 1, a + 1, a + width, a + width + 1);
                }
            }
        g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
        g.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
        g.setIndex(idx);
        g.computeVertexNormals();
        return g;
    }, [t, ex, slope, wire, native]);
    return <mesh geometry={geom} receiveShadow><meshStandardMaterial map={t.data_state === 'DERIVED' && !slope && !wire ? texture : undefined} vertexColors={t.data_state !== 'DERIVED' || slope || wire} color={!slope && !wire ? '#967d6a' : 'white'} wireframe={wire} roughness={.95} side={THREE.DoubleSide}/></mesh>;
}
function Moving({ t, path, progress, ex, kind, follow, zoom = 1, lateral = 0, equipment = [] }: {
    t: any;
    path: number[][];
    progress: number;
    ex: number;
    kind: string;
    follow: boolean;
    zoom?: number;
    lateral?: number;
    equipment?: string[];
}) { const ref = useRef<THREE.Group>(null); const { camera } = useThree(); useFrame(() => { if (!ref.current || !path?.length)
    return; const f = Math.max(0, Math.min(1, progress)) * (path.length - 1); const i = Math.floor(f); const a = coords(t, path[i], ex); const b = coords(t, path[Math.min(i + 1, path.length - 1)], ex); ref.current.position.set(a[0] + (b[0] - a[0]) * (f - i), a[1] + (b[1] - a[1]) * (f - i) + (kind === 'ingenuity' ? .15 * Math.sin(Math.PI * progress) + (progress > 0 && progress < 1 ? .08 : 0) : 0), a[2] + (b[2] - a[2]) * (f - i)); ref.current.position.x += lateral; ref.current.rotation.y = Math.atan2(b[0] - a[0], b[2] - a[2]); if (kind === 'rover')
    ref.current.rotation.x = -Math.atan2(b[1] - a[1], Math.hypot(b[0] - a[0], b[2] - a[2]) || 1); if (follow) {
    camera.position.lerp(ref.current.position.clone().add(new THREE.Vector3(.14, .09, .16).divideScalar(zoom)), .08);
    camera.lookAt(ref.current.position);
} }); return <group ref={ref}><Model kind={kind}/>{equipment.length > 0 && <mesh position={[0,.052,-.034]}>
        <boxGeometry args={[.036,.032,.022]}/><meshStandardMaterial color={equipment.includes('heater')?'#ff8248':equipment.includes('cooler')?'#65d8fa':'#e9da64'}/></mesh>}
        <Html position={[0, .07, 0]} center><span className="scene-tag">{modelNames[kind]}{equipment.length ? ' · '+equipment.map(item=>equipmentLabels[item]).join(', ') : ''}</span></Html></group>; }
function groundClock(run:any, progress:number) {
    return run?.uav_follow_up_path?.length ? Math.min(1,progress/.85) : progress;
}
function joint(run: any) { return run?.mesh_survey && !run.ground_verify; }
function roverProgress(run: any, progress: number) {
    progress=groundClock(run,progress);
    return joint(run) ? Math.max(0, (progress - .35) / .65) : Math.max(0, Math.min(1, (progress - .35) / .30));
}
function evaProgress(run: any, progress: number) {
    progress=groundClock(run,progress);
    return joint(run) ? Math.max(0, (progress - .35) / .65) : Math.max(0, (progress - .65) / .35);
}
function StopCamera({t, cell, ex}:any) {
    const {camera}=useThree();
    useEffect(()=>{
        const [x,y,z]=coords(t,cell,ex);
        camera.position.set(x,y+.017,z);
        camera.lookAt(x,y+.005,z-.35);
    },[camera,t,cell,ex]);
    return null;
}
function DecisionTimeline({run,progress}:any) {
    const [asset,setAsset]=useState('All');
    const audit=run?.decision_audit;
    if(!audit)return null;
    const visible=audit.timeline.filter((entry:any)=>entry.t<=progress+1e-9&&(asset==='All'||entry.asset===asset));
    return <details className="mission-detail" open>
        <summary>Decision timeline · {visible.length} revealed</summary>
        <label>Asset <select value={asset} onChange={e=>setAsset(e.target.value)}>
            {['All','Mission','UAV','EVA','ROVER'].map(value=><option key={value}>{value}</option>)}
        </select></label>

        <ol style={{maxHeight:240,overflow:'auto'}}>{visible.slice().reverse().map((entry:any,index:number)=>
            <li key={index}><strong>{(100*entry.t).toFixed(1)}% · {entry.asset} · {entry.label}</strong><div>{entry.detail}</div></li>
        )}</ol>
        {progress>=.35&&<details><summary>Route calculations</summary>
            <p>Rover loop: {audit.rover_route_m} m. Initial spacing preference: {audit.minimum_target_spacing_m} m before fallback.</p>
            {audit.sorties.map((sortie:any)=><p key={sortie.sortie}>EVA {sortie.sortie}: {sortie.distance_m} m · {sortie.walking_minutes} min walking + {sortie.science_minutes} min science · {sortie.remaining_minutes} min remaining / {sortie.required_reserve_minutes} min required.</p>)}
            {audit.route_candidates.map((candidate:any,index:number)=><p key={index}>Candidate {index+1}: {candidate.distance_m} m · tail loss {candidate.tail_loss.toFixed(3)}{candidate.selected?' · selected':''}</p>)}
            <ul>{audit.formulas.map((formula:string)=><li key={formula}>{formula}</li>)}</ul>
        </details>}
    </details>;
}
function SurveyLog({run,progress}:any) {
    const readings = run?.uav_readings ?? [];
    const visible = readings.filter((reading:any)=>reading.progress<=progress);
    return <section className="mission-detail" aria-label="UAV survey log">
        <strong>UAV survey log</strong>

        <p>{run?.mesh_survey ? `${visible.length}/${readings.length} samples · ${progress < .35 ? 'Surveying' : 'Survey complete'}` : 'Start a mesh survey to collect readings.'}</p>
        {visible.slice(-4).reverse().map((reading:any)=><div className="site-status" key={reading.progress}>
            Grid {reading.cell.map((value:number)=>value.toFixed(1)).join(' / ')} · elevation {reading.elevation_m} m · slope {reading.slope_deg}° · risk index {reading.risk_index}/100
        </div>)}
    </section>;
}
function Scene({ t, routes, run, progress, ex, overlay, layer, camera, points, zoom, condition, comparisonPath, activeEquipment }: any) {
    const playback=progress;
    const followUp=!!run?.uav_follow_up_path?.length&&playback>=.85;
    progress=groundClock(run,progress);
    const route = (run ? progress >= (run.mesh_survey ? (run.change_progress ?? 1) : .65) ? run.after : (progress >= .35) ? run.aerial ?? run.before : run.before : null)?.path || [];
    const walking = run?.after?.feasible && !!run.after.path.length && progress >= (joint(run) ? .35 : .65);
    const walkProgress = walking ? Math.min(run.monitor_change_cell && !run.mesh_survey ? .48 : 1, evaProgress(run, playback)) : 0;
    const stageBase = run?.base ?? [Math.round(points[0][0] * 208 / 95) * 95 / 208, Math.round(points[0][1] * 225 / 95) * 95 / 225];
    const sampled = (run?.uav_readings ?? []).filter((reading:any)=>reading.progress<=progress);
    const surveyPath = run?.uav_path?.length ? run.uav_path : [[points[0][0], Math.max(0, points[0][1] - 1)]];
    const monitoringPath = run?.after?.path?.length ? run.after.path : surveyPath;
    const displayedSites = run?.mesh_survey ? (run.base ? [run.base, ...((progress >= .35) ? run.sites.map((site: any) => site.cell) : [])] : []) : [stageBase];
    const short: number[][] = [];
    const roverPath = run?.rover_path?.length ? run.rover_path : [[points[0][0], Math.min(95, points[0][1] + 1)]];
    return <>{camera.startsWith('stop:')&&<div className="map-credit">Simulated stop view<br/>{run?.sites?.filter((site:any)=>site.cell.join(',')===camera.slice(5)).map((site:any)=><span key={site.id}>{site.label} · {site.bearing_deg}° from habitat · {site.habitat_distance_m} m · slope {site.slope_deg}°</span>)}</div>}<div className="mission-phase" role="status">{run?.habitat && !run.habitat.started && !run.habitat.recorded
        ? (run.habitat.rejections.length ? 'Preflight held · review warnings' : 'Preflight ready · start expedition')
        : run?.mesh_survey && run.events?.length ? run.events.filter((event:any)=>event.t<=playback+1e-9).at(-1)?.label : !run ? 'Select a survey circle in Atlas, then start the survey' : progress < .35 ? 'UAV survey · terrain geometry' : !joint(run) && progress < .65 ? (run?.ground_verify ? 'Rover EVA verification and science' : 'Perseverance · independent science route') : !walking ? 'EVA unavailable · check survey findings' : progress >= (run.mesh_survey ? (run.change_progress ?? 1) : .818) && run.monitor_change_cell ? (progress >= 1 ? 'Returned to staging base' : 'Dust warning · crew returns and retries after clearance') : 'EVA traverse · UAV monitoring ahead'}</div><Canvas shadows dpr={[1, 1.5]} camera={{ near: .001, position: camera === 'top' ? [0, 55, .01] : [26, 24, 32], fov: 45 }} key={camera}><color attach="background" args={['#0b111b']}/><fog attach="fog" args={condition === 'dust' ? ['#76533b', 12, 72] : ['#0b111b', 70, 140]}/><hemisphereLight args={[condition === 'night' ? '#9daed9' : condition === 'heat' ? '#ffd5a0' : '#ded6c9', '#423126', condition === 'night' ? .25 : .65]}/><directionalLight position={[20, 30, -20]} intensity={condition === 'night' ? .35 : condition === 'dust' ? .8 : 1.45} castShadow shadow-mapSize={[1024, 1024]}/><Terrain t={t} ex={ex} slope={layer === 'slope'} wire={layer === 'mesh'}/>{short.length > 1 && <Line points={short.map((p: any) => { const q = coords(t, p, ex); q[1] += .06; return q; })} color="#e9c994" lineWidth={1.4} dashed dashSize={.3} gapSize={.2}/>} {route.length > 1 && <Line points={route.map((p: any) => { const q = coords(t, p, ex); q[1] += .12; return q; })} color="#398cff" lineWidth={3}/>} {run?.mesh_survey && (progress >= .35) && roverPath.length > 1 && <Line points={roverPath.map((p: any) => { const q = coords(t, p, ex); q[1] += .09; return q; })} color="#ff4545" lineWidth={3}/>}{overlay && (run?.corridor_center_grid ? [run.corridor_center_grid] : [[47, 42], [26, 62], [70, 27]]).map((p, k) => <group key={k} position={coords(t, p, ex)}><mesh rotation={[-Math.PI / 2, 0, 0]}><ringGeometry args={[2, 2.1, 64]}/><meshBasicMaterial color={run && k === run.observation?.corridor ? (run.observation.positive ? '#d46d4b' : '#6cdde2') : '#f1b85b'} transparent opacity={.8} side={THREE.DoubleSide}/></mesh><Html position={[0, .4, 0]} center><span className="corridor">C0{k + 1} · {run && k === run.observation?.corridor ? 'OBSERVED IN SIM' : 'UNCERTAIN'}</span></Html></group>)}{run?.monitor_change_cell && progress >= (run.mesh_survey ? (run.change_progress ?? 1) : .818) && <Html center position={coords(t, run.monitor_change_cell, ex)}><span className="corridor">SIMULATED CHANGE · EVA EXCLUSION</span></Html>}{displayedSites.map((p: any, k: number) => <group key={k} position={coords(t, p, ex)}>{k ? <Html center position={[0,.04,0]}><span aria-hidden="true" className={run.sites[k-1].kind==='ROVER'?'target-spot rover-spot':run.sites[k-1].kind==='UAV'?'target-spot uav-spot':'target-spot eva-spot'}/></Html> : <mesh position={[0,.22,0]}><cylinderGeometry args={[.6,.6,.44,6]}/><meshStandardMaterial color="#edf3f8"/></mesh>}<Html position={[0, 1, 0]} center><span className="scene-tag">{k === 0 ? 'Fixed habitat' : run.sites[k - 1].label + ' HOTSPOT'}</span></Html></group>)}<Moving t={t} path={walking && route.length ? (run.mesh_survey ? run.after.path : route) : [stageBase]} progress={walkProgress} ex={ex} kind="astronaut" equipment={activeEquipment} zoom={zoom} follow={camera === 'astronaut'}/><Moving t={t} path={walking && route.length ? (run.mesh_survey ? run.after.path : route) : [stageBase]} progress={walkProgress} ex={ex} kind="astronaut" equipment={activeEquipment} lateral={.055} follow={false}/><Moving t={t} path={run?.mesh_survey && !joint(run) && progress < .35 ? [stageBase] : run ? roverPath : [[points[0][0], Math.min(95, points[0][1] + 4)]]} progress={roverProgress(run, playback)} ex={ex} kind="rover" zoom={zoom} follow={camera === 'rover'}/>
    {comparisonPath?.length > 1 && <Line color="#c895ff" lineWidth={3} points={comparisonPath.map((cell:number[])=>{
        const point=coords(t,cell,ex); point[1]+=.014; return point;
    })}/>}
    {followUp&&<Line color="#36d66b" lineWidth={3} points={run.uav_follow_up_path.map((cell:number[])=>{const point=coords(t,cell,ex);point[1]+=.15;return point})}/>}
    <Moving t={t} path={followUp ? run.uav_follow_up_path : walking ? monitoringPath : surveyPath} progress={followUp ? (playback-.85)/.15 : walking ? walkProgress : Math.min(1, progress / .35)} ex={ex} kind="ingenuity" zoom={zoom} follow={camera === 'ingenuity'}/>{camera.startsWith('stop:')&&<StopCamera t={t} ex={ex} cell={camera.slice(5).split(',').map(Number)}/>}{sampled.length>1&&<Line points={sampled.map((reading:any)=>{const point=coords(t,reading.cell,ex);point[1]+=.15;return point})} color="#e4b95d" lineWidth={2}/>}<OrbitControls enabled={camera === 'orbit' || camera === 'top'} target={[0, 0, 0]} maxPolarAngle={Math.PI / 2.1} minDistance={.04} maxDistance={100}/><gridHelper args={[60, 12, '#334450', '#1d2c39']} position={[0, -.12, 0]}/></Canvas></>;
}
function Atlas({ t, routes, points, edit, onMove, center, radius, onCenter, mapLayer, mission, progress, history, sectors }: any) {
    const element = useRef<HTMLDivElement>(null);
    const [position, setPosition] = useState('18.45500° N / 77.44000° E');
    const [showSectors,setShowSectors] = useState(false);
    const [sectorFilter,setSectorFilter] = useState('all');
    const [section,setSection] = useState<any>(null);
    const showCoverage = showSectors || mapLayer === 'campaign';
    useEffect(() => {
        const [w, s, e, n] = t.bounds;
        const projection = new Projection({ code: 'MARS:PLANETOCENTRIC', units: 'degrees', extent: [-180, -90, 180, 90], metersPerUnit: Math.PI * t.radius_m / 180 });
        const geo = (p: any) => [w + p[1] / 95 * (e - w), n - p[0] / 95 * (n - s)];
        const ring = Array.from({ length: 97 }, (_, i) => {
            const angle = i * Math.PI / 48;
            return geo([center[0] + Math.sin(angle) * radius / t.dy_m, center[1] + Math.cos(angle) * radius / t.dx_m]);
        });
        const features: any[] = [new Feature({ geometry: new Polygon([ring]) })];
        if (showCoverage) for (const sector of sectors ?? []) {
            if (sectorFilter !== 'all' && sector.status !== sectorFilter) continue;
            const top = sector.row*95/16, left = sector.col*95/16;
            const right = (sector.col+1)*95/16, bottom = (sector.row+1)*95/16;
            const outline = [[top,left],[top,right],[bottom,right],[bottom,left],[top,left]].map(geo);
            const style = sectorStyles[sector.status];
            features.push(new Feature({geometry:new Polygon([outline]), sector, fill:style.fill, color:style.stroke}));
            if (sector.status === 'hazard' && sector.peak_cell)
                features.push(new Feature({geometry:new Point(geo(sector.peak_cell)),color:style.stroke,sector}));
        }
        for (const survey of history) {
            for (const path of [survey.eva, survey.rover]) {
                if (path.length > 1)
                    features.push(new Feature({ geometry: new LineString(path.map(geo)), archived: true }));
            }
            for (const check of survey.checks) {
                features.push(new Feature({ geometry: new Point(geo(check.cell)), name: '', archived: true }));
            }
        }
        const activePath = mission?.mesh_survey ? (progress >= (mission.change_progress ?? 1) ? mission.after.path : (progress >= .35) ? mission.aerial.path : []) : null;
        if (activePath?.length > 1)
            features.push(new Feature({ geometry: new LineString(activePath.map(geo)), color: '#246de1' }));
        if (mission?.mesh_survey && (progress >= .35)) {
            if (mission.rover_path?.length > 1)
                features.push(new Feature({ geometry: new LineString(mission.rover_path.map(geo)), color: '#df3030' }));
            if (mission.uav_follow_up_path?.length && progress>=.85)
                features.push(new Feature({geometry:new LineString(mission.uav_follow_up_path.map(geo)),color:"#36d66b"}));
            if (mission.base)
                features.push(new Feature({ geometry: new Point(geo(mission.base)), name: 'Base' }));
            mission.sites.forEach((site: any) => features.push(new Feature({ geometry: new Point(geo(site.cell)), name: site.label + " HOTSPOT", color: site.kind === 'ROVER' ? '#df3030' : site.kind === 'UAV' ? '#d6a242' : '#246de1', hotspot: true })));
        }
        (mission?.mesh_survey ? [] : points.slice(0, 1)).forEach((p: any, k: number) => features.push(new Feature({ geometry: new Point(geo(p)), name: ['H', 'A', 'B'][k] })));
        const basemap = mapLayer === 'thermal' ? '/data/themis-context.png' : mapLayer === 'ctx' ? '/data/ctx-context.png' : mapLayer === 'relief' ? '/data/ctx-relief.png' : mapLayer === 'mola' ? '/data/mola-context.png' : '/data/imagery.png';
        const overlays: any[] = [];
        if (mapLayer === 'hazard' && mission?.hazard && progress >= .35) {
            const raster = document.createElement('canvas');
            raster.width = 226;
            raster.height = 209;
            const ctx = raster.getContext('2d')!;
            const frame = ctx.createImageData(226, 209);
            const values = progress >= (mission.change_progress ?? 1) && mission.hazard_updated ? mission.hazard_updated : mission.hazard;
            values.forEach((value: number, i: number) => {
                if (value < 0)
                    return;
                const rgb = value >= 68 ? [225, 35, 28] : value >= 40 ? [243, 157, 29] : [37, 165, 100];
                frame.data.set([...rgb, 150], i * 4);
            });
            ctx.putImageData(frame, 0, 0);
            overlays.push(new ImageLayer({ source: new ImageStatic({ url: raster.toDataURL(), projection, imageExtent: [w, s, e, n] }) }));
        }
        const map = new Map({ target: element.current!, layers: [new ImageLayer({ source: new ImageStatic({ url: basemap, projection, imageExtent: [w, s, e, n] }) }), ...overlays, new VectorLayer({ source: new VectorSource({ features }), style: (f) => new Style({ fill: f.get('fill') ? new Fill({color:f.get('fill')}) : undefined, stroke: new Stroke({ color: f.get('color') || (f.get('archived') ? '#c79648' : '#6cdde2'), width: f.get('archived') ? 2 : 3 }), image: new CircleStyle({ radius: f.get('hotspot') ? 12 : 3, fill: new Fill({ color: f.get('color') || '#0b111b' }), stroke: new Stroke({ color: '#e9c994', width: 2 }) }), zIndex: f.get('hotspot') ? 10 : 1, text: new Text({ text: f.get('name') || '', offsetY: -18, fill: new Fill({ color: '#fff' }), stroke: new Stroke({ color: '#0b111b', width: 3 }) }) }) })], view: new View({ projection, center: [(w + e) / 2, (n + s) / 2], zoom: 12, extent: [w, s, e, n] }) });
        map.getView().fit([w, s, e, n], { padding: [80, 80, 80, 80] });
        map.on('pointermove', ev => {
            setPosition(`${ev.coordinate[1].toFixed(5)}° N / ${ev.coordinate[0].toFixed(5)}° E`);
            const hit = map.forEachFeatureAtPixel(ev.pixel, feature => feature.get('sector') || undefined);
            setSection(hit ?? null);
        });
        map.on('singleclick', ev => { const c = Math.round((ev.coordinate[0] - w) / (e - w) * 95), r = Math.round((n - ev.coordinate[1]) / (n - s) * 95); if (r >= 0 && c >= 0 && r < 96 && c < 96)
            (edit < 0 ? onCenter([r, c]) : onMove(edit, [r, c])); });
        return () => map.setTarget(undefined);
    }, [t, routes, points, edit, center, radius, mapLayer, mission, history, sectors, showCoverage, sectorFilter, progress >= .85, progress >= .35, progress >= (mission?.change_progress ?? 1)]);
    return <><div ref={element} className="atlas"/>
        <section className="atlas-survey-legend">
            <label><input type="checkbox" checked={showCoverage} disabled={mapLayer==='campaign'} onChange={e=>setShowSectors(e.target.checked)}/> Recorded campaign sectors</label>
            {showCoverage && <><select aria-label="Filter recorded campaign sectors" value={sectorFilter} onChange={e=>setSectorFilter(e.target.value)}>
                <option value="all">All outcomes</option>{Object.entries(sectorStyles).map(([key,style])=><option key={key} value={key}>{style.label}</option>)}</select>
                <div className="sector-keys">{Object.values(sectorStyles).map(style=><span key={style.label}><i style={{background:style.stroke}}/>{style.label}</span>)}</div>
                {section ? <p><b>{sectorStyles[section.status].label}</b> · Expedition {section.expedition} · {section.condition}<br/>{section.reason}. Coverage {section.coverage_pct}% · peak risk {section.peak_risk}/100.</p>
                : <p>{sectors?.length ? 'Hover a sector for its recorded evidence.' : 'Record an expedition to populate the map.'}</p>}</>}
        </section><div className="map-credit">NASA / JPL / USGS · {mapLayer === 'thermal' ? 'Mars Odyssey THEMIS daytime infrared · image brightness, not temperature' : mapLayer === 'ctx' ? 'MRO CTX mosaic' : mapLayer === 'relief' ? 'Local CTX hillshade · aligned to planner mesh' : mapLayer === 'mola' ? 'Regional MOLA / HRSC context · coarse resolution' : mapLayer === 'campaign' ? 'Campaign survey sectors over HiRISE' : mapLayer === 'hazard' ? 'HiRISE + derived hazard overlay · green lower / amber moderate / red EVA exclusion' : 'MRO HiRISE mosaic'}<br />{position}<br />{t.data_state === 'DERIVED' ? 'Route overlay uses USGS CTX elevations; mission assumptions are simulated.' : 'Route overlay uses SYNTHETIC fallback elevation.'}</div></>;
}
const surveyAreas = [
    { name: 'Northwest sector', center: [37, 37] },
    { name: 'Northeast sector', center: [33, 63] },
    { name: 'Southwest sector', center: [66, 37] },
    { name: 'Southeast sector', center: [66, 66] },
    { name: 'Central traverse', center: [50, 50] },
];
function App() {
    const [payloadKg,setPayloadKg]=useState(10), [objective,setObjective]=useState("relief");
    const [groundVerify, setGroundVerify] = useState(false);
    const [history, setHistory] = useState<any[]>(() => {
        try {
            const saved = JSON.parse(localStorage.getItem('404-surveys-v9') || '[]');
            return Array.isArray(saved) ? saved : [];
        }
        catch {
            return [];
        }
    });
    const recordedRun = useRef<any>(null);
    const [evaGoals, setEvaGoals] = useState(3), [roverGoals, setRoverGoals] = useState(3), [area, setArea] = useState('custom');
    const [condition, setCondition] = useState("day");
    const [mapLayer, setMapLayer] = useState("hirise");
    const [center, setCenter] = useState([54, 44]), [radius, setRadius] = useState(1800), [zoom, setZoom] = useState(1);
    const [t, setT] = useState<any>(null), [routes, setRoutes] = useState<any>(null), [run, setRun] = useState<any>(null), [sources, setSources] = useState<any[]>([]), [experiments, setExperiments] = useState<any>(null);
    const [view, setView] = useState('MISSION 3D'), [drawer, setDrawer] = useState(false), [seed, setSeed] = useState(7), [prior, setPrior] = useState(.3), [cost, setCost] = useState(5), [budget, setBudget] = useState(180), [points, setPoints] = useState(INITIAL), [edit, setEdit] = useState(-1), [estimate, setEstimate] = useState<any>(null), [progress, setProgress] = useState(0), [playing, setPlaying] = useState(false), [camera, setCamera] = useState('orbit'), [ex, setEx] = useState(1), [overlay, setOverlay] = useState(true), [layer, setLayer] = useState('terrain'), [error, setError] = useState(''), [busy, setBusy] = useState(false), [demo, setDemo] = useState(false), [regime, setRegime] = useState('baseline');
    const [habitat, setHabitat] = useState<any>(null);
    const [finishedId,setFinishedId] = useState<string | null>(null);
    const [saveFailed,setSaveFailed] = useState(false);
    const [weather,setWeather] = useState<any>(null);
    const [weatherBusy,setWeatherBusy] = useState(false);
    const [weatherError,setWeatherError] = useState('');
    useEffect(() => { api('weather').then(setWeather).catch(e=>setWeatherError(e.message)); }, []);
    async function refreshWeather() {
        setWeatherBusy(true);
        setWeatherError('');
        try { setWeather(await api('weather/refresh',{})); }
        catch(e:any) { setWeatherError(e.message); }
        finally { setWeatherBusy(false); }
    }
    const [equipment,setEquipment] = useState<string[]>([]);
    const [briefing,setBriefing] = useState<any>(null);
    const [briefingBusy,setBriefingBusy] = useState(false);
    const [telemetry, setTelemetry] = useState<any>(null);
    const [baseRunning, setBaseRunning] = useState(false);
    const [comparisonPath,setComparisonPath] = useState<number[][] | null>(null);
    const telemetryBucket = Math.round(progress * 50) / 50;
    const telemetryId = run?.habitat?.phase_bounds && !run.habitat.rejections.length ? run.habitat.id : null;
    useEffect(() => {
        if (!telemetryId) { setTelemetry(null); return; }
        let valid = true;
        api('habitat/telemetry', {id:telemetryId, progress:telemetryBucket, sequence:Date.now()})
            .then(reading => { if (valid) setTelemetry({...reading, id:telemetryId}); })
            .catch(e => { if (valid) setError(e.message); });
        return () => { valid = false; };
    }, [telemetryId, telemetryBucket]);
    async function advanceBase(quarters: number) {
        setBaseRunning(true);
        reset();
        setError('');
        let current = habitat;
        try {
            for (let step = 0; step < quarters; step++) {
                if (quarters > 1) await new Promise(resolve => setTimeout(resolve, 900));
                current = await api('habitat/advance', {revision:current.revision});
                setHabitat(current);
            }
        } catch (e: any) { setError(e.message); }
        finally { setBaseRunning(false); }
    }
    async function discardDraft() {
        setBusy(true);
        try {
            setHabitat(await api('habitat/discard', {id:habitat.active_draft}));
            reset();
        } catch (e: any) { setError(e.message); }
        finally { setBusy(false); }
    }
    useEffect(() => { api('habitat').then(setHabitat).catch(e => setError(e.message)); }, []);
    async function startPlayback(plan: any) {
        const approved = await api('habitat/start',{id:plan.habitat.id});
        setRun({...plan,habitat:approved});
        setView('MISSION 3D');
        setProgress(0);
        setPlaying(true);
    }
    async function launchExpedition() {
        if (!run?.habitat || busy) return;
        setBusy(true);
        setError('');
        try { await startPlayback(run); }
        catch (e: any) {setError(e.message);}
        finally {setBusy(false);}
    }
    async function resumeDraft() {
        setBusy(true);
        setError('');
        try {
            const draft = await api('habitat/draft');
            setCenter(draft.request.center);
            setRadius(draft.request.radius);
            setRun(draft);
            setProgress(draft.habitat.progress ?? 0);
            setView('MISSION 3D');
            setPlaying(!!draft.habitat.started && draft.habitat.progress < 1);
            if (draft.habitat.started && draft.habitat.progress >= 1) setSaveFailed(true);
        } catch (e: any) {setError(e.message);}
        finally {setBusy(false);}
    }
    async function requestBriefing(question: string) {
        const plan = run;
        setBriefing({id: plan.habitat.id});
        setBriefingBusy(true);
        try {
            const answer = await api('habitat/briefing', {...plan.request, question, plan_id:plan.habitat.id, rejections:plan.habitat.rejections.slice(0,12)});
            setBriefing({id:plan.habitat.id,...answer});
        } catch (e: any) {setError(e.message);}
        finally {setBriefingBusy(false);}
    }
    async function recordExpedition() {
        if (!run?.habitat || progress < 1 || busy) return;
        setBusy(true);
        setSaveFailed(false);
        try {
            await api('habitat/telemetry', {id:run.habitat.id, progress:1, sequence:Date.now()+1});
            setHabitat(await api('habitat/record', {id:run.habitat.id}));
            setRun({...run,habitat:{...run.habitat,recorded:true}});
        } catch (e: any) { setSaveFailed(true); setError(e.message); }
        finally { setBusy(false); }
    }
    useEffect(() => {
        if (!finishedId || finishedId !== run?.habitat?.id || run.habitat.recorded || busy) return;
        setFinishedId(null);
        void recordExpedition();
    }, [finishedId, run, busy]);
    async function replayExpedition(id: string) {
        setComparisonPath(null);
        setBusy(true);
        try {
            const archived = await api('habitat/replay/' + id);
            setCenter(archived.request.center);
            setRadius(archived.request.radius);
            setRun(archived);
            setView('MISSION 3D');
            setProgress(0);
            setPlaying(false);
        } catch (e: any) { setError(e.message); }
        finally { setBusy(false); }
    }
    const demoTimers = useRef<any[]>([]);
    const reduced = useMemo(() => matchMedia('(prefers-reduced-motion: reduce)').matches, []);
    useEffect(() => {
        if (progress < 1 || !run?.mesh_survey || run?.habitat?.rejections?.length || recordedRun.current === (run?.habitat?.id ?? run) || run?.habitat?.recorded)
            return;
        recordedRun.current = run?.habitat?.id ?? run;
        const entry = { center: [...center], radius, eva: run.after.path, rover: run.rover_path,
            checks: [...(run.ground_checks ?? []), ...(run.scout_updates ?? []), ...(run.monitor_checks ?? [])],
            sites: run.sites, decision_audit: run.decision_audit, request: run.request, events: run.events, uav_readings: run.uav_readings, campaign_complete: run.campaign_complete, recorded_at: new Date().toISOString(), completed_at: run.campaign_complete ? new Date().toISOString() : null };
        setHistory(previous => {
            const next = [...previous, entry].slice(-30);
            try {
                localStorage.setItem('404-surveys-v9', JSON.stringify(next));
            }
            catch { }
            return next;
        });
    }, [run, progress, center, radius]);
    const req = { seed, prior, cost, budget, points };
    useEffect(() => { Promise.all([Promise.all([fetch('/data/terrain.json').then(r => r.json()), fetch('/data/terrain-native.f32').then(r => r.ok ? r.arrayBuffer() : null).catch(() => null)]).then(([terrain, buffer]) => ({ ...terrain, nativeMesh: terrain.data_state === 'DERIVED' && buffer?.byteLength === 226 * 209 * 4 ? new Float32Array(buffer) : undefined })), fetch('/data/sources.json').then(r => r.json()), fetch('/data/experiments.json').then(r => r.json())]).then(([a, b, c]) => { setT(a); setSources(b); setExperiments(c); }).catch(e => setError('Data package missing: ' + e.message)); }, []);
    useEffect(() => { let valid = true; setRun(null); setProgress(0); setPlaying(false); Promise.all([api('routes/compare', req), api('scout/estimate', req)]).then(([r, e]) => { if (valid) {
        setRoutes(r);
        setEstimate(e);
        setError('');
    } }).catch(e => { if (valid)
        setError(e.message); }); return () => { valid = false; }; }, [seed, prior, cost, budget, points]);
    const [playbackRate, setPlaybackRate] = useState(1);
    const playbackSeconds = run?.mesh_survey
        ? Math.max(1, (run.uav_path?.length ?? 0)*.35 + Math.max(run.rover_path?.length ?? 0, run.after?.path?.length ?? 0)*.15)
        : 30;
    useEffect(() => {
        if (!playing) return;
        let current = progress, previous = performance.now(), frame: number;
        const tick = (now: number) => {
            const next = Math.min(1, current + (now - previous) / 1000 * playbackRate / playbackSeconds);
            setProgress(next);
            if (next >= 1) {
                setPlaying(false);
                if (current < 1 && run?.habitat?.started && !run.habitat.recorded) setFinishedId(run.habitat.id);
                return;
            }
            current = next;
            previous = now;
            frame = requestAnimationFrame(tick);
        };
        frame = requestAnimationFrame(tick);
        return () => cancelAnimationFrame(frame);
    }, [playing, playbackRate, playbackSeconds, run]);
    useEffect(() => () => demoTimers.current.forEach(clearTimeout), []);
    async function scout() { setBusy(true); setError(''); try {
        const r = await api('simulations', req);
        setRun(r);
        setView('MISSION 3D');
        setProgress(0);
        if (!reduced)
            setPlaying(true);
        return r;
    }
    catch (e: any) {
        setError(e.message);
    }
    finally {
        setBusy(false);
    } }
    function reset() { setFinishedId(null); setSaveFailed(false); setComparisonPath(null); demoTimers.current.forEach(clearTimeout); setDemo(false); setProgress(0); setPlaying(false); setRun(null); }
    async function guided(roverSite?: number, sortie = 1, launch = false) {
        if (baseRunning || busy) return;
        reset();
        setBusy(true);
        setError('');
        try {
            const request = { ...req, center, radius, rover_site: roverSite, condition, eva_goals: evaGoals, rover_goals: roverGoals, sortie, ground_verify: groundVerify, payload_kg:payloadKg, objective,
                new_expedition:launch, equipment: Array.from(new Set([...equipment, ...[conditionInfo[condition]?.gear].filter(Boolean)])) };
            const result = await api('habitat/plan', request);
            const plan = {...result,request:result.request ?? request};
            setRun(plan);
            setView('MISSION 3D');
            setHabitat(await api('habitat'));
            if (result.habitat?.rejections?.length) {
                setError(result.habitat.rejections.join(' '));
                setView('MISSION 3D');
                return;
            }
            setView('MISSION 3D');
            if (launch && plan.habitat) await startPlayback(plan);
            else if (!result.aerial.feasible) setError(result.aerial.reason);
        }
        catch (e: any) {
            setError(e.message);
        }
        finally {
            setBusy(false);
        }
    }
    function exportRun(csv = false) { const payload = { note: NOTE, source_manifest: sources, terrain_metadata: t ? { ...t, elevation: undefined, slope: undefined, valid: undefined } : null, request: run?.request ?? req, simulation: run, routes }; if (csv) {
        const manifest = '# ' + JSON.stringify({ note: NOTE, source_manifest: sources, request: run?.request ?? req }) + '\n';
        const rows = run?.decision_audit?.timeline ?? run?.telemetry ?? (run?.events ?? []).map((event:any)=>({progress:event.t,event:event.label}));
        const keys = rows.length ? Object.keys(rows[0]) : [];
        download('404-telemetry.csv', manifest + keys.join(',') + '\n' + rows.map((r: any) => keys.map(k => '"'+String(r[k]??'').replaceAll('"','""')+'"').join(',')).join('\n'), 'text/csv');
    }
    else
        download('404-mission.json', JSON.stringify(payload, null, 2)); }
    const active = (run?.mesh_survey ? (progress >= .65 ? run.after : progress >= .35 ? run.aerial : null) : run && progress >= .65 ? run.after : null);
    const exp = experiments?.regimes?.find((x: any) => x.regime === regime);
    const move = (i: number, p: number[]) => setPoints(prev => prev.map((a, k) => k === i ? p : a));
    return <main><header><a className="brand" href="#" onClick={e => { e.preventDefault(); setView('MISSION 3D'); }}><span className="brand-mark">404</span><span>PATH NOT FOUND<small>TEAM 404 / SCOUT OR SKIP</small></span></a><div className="location"><i /> JEZERO CRATER <span>18.455° N &nbsp; 77.440° E</span></div><button className="quiet" onClick={() => setDrawer(true)}>Sources & credits ↗</button><button onClick={() => { setEdit(-1); setView('ATLAS'); }}>Select survey circle</button><select aria-label="Atlas layer" value={mapLayer} onChange={e => { setMapLayer(e.target.value); setView('ATLAS'); }}><option value="hirise">HiRISE imagery</option><option value="ctx">CTX imagery</option><option value="thermal">THEMIS daytime infrared</option><option value="relief">Local relief · CTX DEM</option><option value="mola">Regional context · MOLA / HRSC</option><option value="campaign">Campaign survey outcomes</option><option value="hazard">Survey hazard map</option><option value="panorama">Jezero delta panorama</option></select><select aria-label="Simulation conditions" value={condition} onChange={e => { reset(); setCondition(e.target.value); }}><option value="day">Clear day</option><option value="night">Cold night</option><option value="heat">Sun-exposed heat</option><option value="dust">Dust haze</option></select><label>Radius <input aria-label="Survey radius meters" type="number" min="100" max="3500" step="50" value={radius} onChange={e => setRadius(+e.target.value)}/> m</label><button className="demo" onClick={() => guided(undefined,1,true)}
            disabled={busy || demo || baseRunning || !!run?.habitat?.started && !run.habitat.recorded}>
            {busy ? 'Working…' : run?.habitat?.started && !run.habitat.recorded ? 'Expedition in progress' : '▶ Run expedition'}</button></header><nav>{['ATLAS', 'MISSION 3D', 'SCOUT OR SKIP', 'REWIND', '404-SVNET'].map((v, i) => <button className={v === view ? 'selected' : ''} key={v} onClick={() => setView(v)}>{v}</button>)}</nav><div className={view === '404-SVNET' ? 'workspace model-mode' : 'workspace'}><section className="viewport">{view === '404-SVNET' ? <SVNetConsole request={req} onApply={(result: any) => { if (result.kind === 'episode') {
        setRun(result.episode);
        setView('SCOUT OR SKIP');
        setProgress(0);
        setPlaying(!reduced);
    }
    else {
        setRoutes((previous: any) => ({ ...previous, risk: result.route }));
        setRun(null);
        setView('MISSION 3D');
        setProgress(0);
        setPlaying(false);
    } }}/> : t ? (view === 'ATLAS' && mapLayer === 'panorama' ? <figure className="delta-panorama"><a href="/photos/PIA25212.jpg" target="_blank" rel="noreferrer"><img src="/photos/PIA25212.jpg" alt="Perseverance panorama of the Jezero delta"/></a><figcaption>Jezero delta panorama · Mastcam-Z · Sol 406 · NASA/JPL-Caltech/ASU/MSSS. Ground-level reference view.</figcaption></figure> : view === 'ATLAS' ? <Atlas t={t} routes={routes} points={points} edit={edit} onMove={move} center={center} radius={radius} onCenter={(point: number[]) => { reset(); setArea('custom'); setCenter(point); }} mapLayer={mapLayer} mission={run} progress={progress} history={habitat?.history ?? history} sectors={habitat?.atlas_sectors}/> : <Scene t={t} routes={routes} run={run} progress={progress} ex={ex} overlay={overlay} layer={layer} camera={camera} points={points} zoom={zoom} condition={run?.condition ?? condition} comparisonPath={comparisonPath} activeEquipment={telemetry?.id === telemetryId ? telemetry.equipment_active : []}/>) : <div className="loading">Loading mission terrain…</div>}<div className={view === '404-SVNET' ? 'hidden' : 'scene-heading'}><div className="eyebrow">JEZERO CRATER</div><h1>{view === 'ATLAS' ? 'Jezero atlas' : view === 'SCOUT OR SKIP' ? 'Scout operations' : view === 'REWIND' ? 'Mission replay' : 'Jezero traverse'}</h1></div><div className={view === '404-SVNET' ? 'hidden' : 'state-banner'}>{view === 'ATLAS' ? (mapLayer === 'relief' ? 'CTX-DERIVED LOCAL RELIEF' : mapLayer === 'campaign' ? 'RECORDED SURVEY OUTCOMES' : 'NASA OBSERVED IMAGERY') : t?.data_state === 'DERIVED' ? 'NASA-DERIVED CTX TERRAIN' : 'SYNTHETIC TEST TERRAIN'}<span>{view === 'ATLAS' ? (mapLayer === 'relief' ? 'USGS / NASA DEM' : mapLayer === 'campaign' ? 'Simulated campaign evidence' : 'Jezero basemap') : t?.data_state === 'DERIVED' ? '20 m CTX elevation source' : 'Synthetic fallback; not measured Jezero relief'}</span></div>{view !== 'ATLAS' && view !== '404-SVNET' && <div className="view-tools"><select aria-label="Camera mode" value={camera} onChange={e => setCamera(e.target.value)}>{camera.startsWith('stop:')&&<option value={camera}>Simulated stop POV</option>}<option value="orbit">Orbit camera</option><option value="top">Top down</option><option value="astronaut">Follow astronaut</option><option value="rover">Follow Perseverance</option><option value="ingenuity">Follow Ingenuity</option></select><label>Follow zoom <input aria-label="Follow zoom" type="range" min=".5" max="4" step=".1" value={zoom} onChange={e => setZoom(+e.target.value)}/></label><select aria-label="Terrain layer" value={layer} onChange={e => setLayer(e.target.value)}><option value="terrain">Terrain shading</option><option value="slope">Slope heatmap</option><option value="mesh">Terrain mesh</option></select><label><input type="checkbox" checked={overlay} onChange={e => setOverlay(e.target.checked)}/> Uncertainty</label><label>Height {ex}× <input aria-label="Vertical exaggeration" type="range" min="1" max="3" step=".25" value={ex} onChange={e => setEx(+e.target.value)}/></label></div>}<div className={view === '404-SVNET' ? 'hidden' : 'legend'}><span className="line cyan"/>Human route (blue) · Rover route (red) <span className="line sand"/>Shortest <span className="dot amber"/>Uncertain </div></section><aside className="inspector"><div className="panel-heading"><span>MISSION CONTROL</span><span className="live">● LOCAL</span></div><div className="mission-title"><h2>Jezero traverse</h2><p>Fixed habitat · Jezero survey sectors</p></div>{error && <div role="alert" className="error">{error}<button onClick={() => location.reload()}>Retry connection</button></div>}{view === 'REWIND' ? <><div className="section-label">PAIRED-SEED EXPERIMENT</div><select aria-label="Experiment regime" value={regime} onChange={e => setRegime(e.target.value)}>{experiments?.regimes?.map((r: any) => <option key={r.regime}>{r.regime}</option>)}</select><p className="muted">100 paired seeds per regime. Saved simulator results; NASA-derived terrain.</p><div className="chart"><ResponsiveContainer width="100%" height={175}><BarChart data={exp?.policies || []}><CartesianGrid stroke="#263b4c" vertical={false}/><XAxis dataKey="strategy" stroke="#92a7b9" fontSize={11}/><YAxis stroke="#92a7b9" fontSize={10} width={35}/><Tooltip contentStyle={{ background: '#142233', border: '1px solid #395164' }}/><Bar dataKey="utility" fill="#6cdde2" radius={[4, 4, 0, 0]}/></BarChart></ResponsiveContainer></div><div className="metric"><span>Scout − proceed</span><strong>{exp?.paired_delta_mean?.toFixed(2) ?? '—'}</strong></div><p className="muted">Bootstrap 95% CI: {exp?.bootstrap_95_ci?.map((x: number) => x.toFixed(2)).join(' to ')}. Mixed outcomes are retained.</p><button onClick={() => download('404-experiments.json', JSON.stringify(experiments, null, 2))}>Export experiment results ↓</button><div className="section-label">EPISODE EVENTS</div>{run ? run.events.map((e: any) => <button key={e.t} className="event" onClick={() => { setPlaying(false); setProgress(e.t); }}><span>{Math.round(e.t * 100)}%</span>{e.label}</button>) : <p className="muted">Run a scout episode to inspect belief and route changes.</p>}</> : <><section className="mission-planner">
        <h3>Mission planner</h3>
        {weather && <details className="mission-detail">
            <summary>Jezero weather · {weather.status}</summary>
            <p>Perseverance MEDA · sol {weather.sol} · {weather.date} · {weather.age_days} Earth days old.</p>
            <p>One-sol scenario estimate from {weather.samples} samples: low {weather.low_c} ± {weather.low_spread} °C, high {weather.high_c} ± {weather.high_spread} °C. Spread is a residual estimate.</p>
            <p>{weather.guidance}</p>
            {weather.orbital.map((item:any)=><p key={item.instrument+item.product}>{item.instrument} · {item.product} · {item.age_days} days old · curated product</p>)}
            <div className="export-row"><button disabled={busy || weatherBusy || playing} onClick={()=>{reset();setCondition(weather.condition);}}>Use suggested simulation</button>
            <button disabled={weatherBusy} onClick={refreshWeather}>{weatherBusy?'Checking NASA…':'Refresh NASA archive'}</button></div>
            {weatherError && <p role="status">{weatherError}</p>}
        </details>}<details className="mission-detail equipment-preflight">
            <summary>Optional kit and plan review</summary>
            <button onClick={() => guided()} disabled={busy || baseRunning || (!!run?.habitat?.started && !run.habitat.recorded)}>Analyze only</button>
            {Object.entries(equipmentLabels).map(([key,label])=><label key={key}>
                <input type="checkbox" checked={equipment.includes(key) || conditionInfo[condition]?.gear===key} disabled={conditionInfo[condition]?.gear===key} onChange={e=>{
                    setEquipment(e.target.checked ? [...equipment,key] : equipment.filter(item=>item!==key));
                    reset();
                }}/>{label}{conditionInfo[condition]?.gear===key?' · required':''}</label>)}
            <p>Required kit is fitted automatically. Add optional items here or review the plan before launch.</p>
        </details><HabitatHud state={habitat} run={run} progress={progress} busy={busy || baseRunning} reading={telemetry?.id === telemetryId ? telemetry : null} baseRunning={baseRunning} saveFailed={saveFailed} onPreview={(path: number[][] | null) => { setComparisonPath(path); setView("MISSION 3D"); }} briefing={briefing?.id===run?.habitat?.id ? briefing : null} briefingBusy={briefingBusy} onBriefing={requestBriefing} onLaunch={launchExpedition} onResume={resumeDraft} onAdvance={advanceBase} onDiscard={discardDraft} onRecord={recordExpedition} onReplay={replayExpedition}/><SurveyLog run={run} progress={progress}/><DecisionTimeline run={run} progress={progress}/>{run?.campaign && <p>{run.sortie_count} EVA sorties · one rover loop · {run.outstanding_eva} unassigned EVA targets</p>}<p>{habitat?.revision ?? history.length} survey records saved · gold routes in Atlas</p>
        <button onClick={() => {
                const index = (area === 'custom' ? 0 : (+area + 1) % surveyAreas.length);
                reset();
                setArea(String(index));
                setCenter(surveyAreas[index].center);
                setRadius(700);
                setMapLayer('hirise');
                setView('ATLAS');
            }}>Select next survey sector</button>
        <label>Jezero survey area<select value={area} onChange={e => {
                const value = e.target.value;
                reset();
                setArea(value);
                if (value !== 'custom') {
                    setCenter(surveyAreas[+value].center);
                    setRadius(700);
                    setView('ATLAS');
                }
            }}><option value="custom">Custom circle</option>{surveyAreas.map((zone, index) => <option key={zone.name} value={index}>{zone.name}</option>)}</select></label>
        <label>Science objective<select value={objective} onChange={e=>setObjective(e.target.value)}><option value="relief">Compare landform relief</option><option value="texture">Investigate surface texture</option></select></label>
        <p className="muted">{objective==='relief'?'Where does elevation depart most from the surrounding terrain?':'Where does optical texture vary most across the survey?'}</p>
        <label>Equipment load (kg)<input type="number" min="0" max="40" value={payloadKg} onChange={e=>setPayloadKg(+e.target.value)}/></label>
        <label>Human + UAV goals<input type="number" min="0" max="6" value={evaGoals} onChange={e => setEvaGoals(+e.target.value)}/></label>
        <label>Rover goals<input type="number" min="0" max="6" value={roverGoals} onChange={e => setRoverGoals(+e.target.value)}/></label>
        <label>Rover verifies EVA route <input type="checkbox" checked={groundVerify} onChange={e => setGroundVerify(e.target.checked)}/></label><p className="muted">Habitat fixed at grid {points[0].join(' / ')}. Routes appear after survey.</p>
        {run?.mesh_survey && <p>UAV search: {run.survey_attempts.map((attempt: any) => attempt.mode + ' (' + attempt.reachable_cells + ' reachable cells)').join(' → ')}</p>}
        {!run?.campaign && run?.sortie_count > 1 && <div className="sortie-selector" aria-label="EVA sorties">{Array.from({ length: run.sortie_count }, (_, index) => <button key={index} disabled={busy || run.sortie === index + 1} onClick={() => guided(undefined, index + 1)}>EVA sortie {index + 1}</button>)}</div>}
        </section><div className="metric-grid"><div><small>ROUTE DISTANCE</small><strong>{active?.meters ? (active.meters / 1000).toFixed(2) : '—'} <em>km</em></strong></div><div><small>WALK ESTIMATE</small><strong>{active?.minutes?.toFixed(0) ?? '—'} <em>min</em></strong></div><div><small>RETURN MARGIN</small><strong>{active?.return_margin_min?.toFixed(0) ?? '—'} <em>min</em></strong></div><div><small>RESERVE</small><strong>20 <em>%</em></strong></div></div><p className={active?.feasible ? 'status' : 'error'}>{active?.reason || (run ? 'UAV survey underway' : 'Awaiting survey')}</p><label className="control">EVA budget <input aria-label="EVA budget minutes" type="number" min="1" max="600" value={budget} onChange={e => setBudget(+e.target.value)}/><span>min</span></label><details className="mission-detail"><summary>Scout controls and model</summary><button className="model-link" onClick={() => setView('404-SVNET')}>Open trained 404-SVNet decision console →</button><div className="section-label">SCOUT OR SKIP <span>SIMULATED</span></div><div className="decision"><div><span className="eyebrow">ANALYTIC BASELINE · ASSUMED DETOUR</span><strong>{estimate?.recommendation || '…'} <small>{estimate?.vos?.toFixed(2)} VoS</small></strong></div><p>{estimate?.why}</p></div><label className="slider">Corridor prior <b>{(prior * 100).toFixed(0)}%</b><input aria-label="Hazard prior" type="range" min=".01" max=".95" step=".01" value={prior} onChange={e => setPrior(+e.target.value)}/></label><div className="control-row"><label>Seed<input aria-label="Simulation seed" type="number" min="0" max="2147483647" value={seed} onChange={e => setSeed(+e.target.value)}/></label><label>Scout cost<input aria-label="Scout cost" type="number" min="0" max="500" value={cost} onChange={e => setCost(+e.target.value)}/></label></div><button className="primary" disabled={busy} onClick={scout}>{busy ? 'Running episode…' : 'Deploy simulated scout →'}</button>{run?.observation && <div className="observation"><b>C0{run.observation?.corridor + 1}: {run.observation.positive ? 'hazard-like slip' : 'low slip'} observed</b><p>Belief: {(run.observation?.prior * 100).toFixed(1)}% → {(run.observation?.posterior * 100).toFixed(1)}%. Route recalculated after observation.</p><small>Slip {run.observation.slip.toFixed(3)} · seeded Gaussian observation</small></div>}</details></>}{run?.mesh_survey && (progress >= .35) && <section><div className="section-label">MISSION ITINERARY</div><p className="muted">Blue EVA targets are crew science stops. Red rover targets are a separate robotic science assignment.</p>{run.posterior_cvar90 != null && <p>Simulated CVaR₉₀ of route failure: {(run.posterior_cvar90 * 100).toFixed(1)}% · {run.scout_updates.length} field probes</p>}{run.sites.map((site: any) => <div key={site.id}><span><strong>{site.label}</strong> · risk {Math.round(site.risk * 100)}/100</span><small className="site-status">{site.uav_inspection_t!=null && progress>=site.uav_inspection_t ? 'Inspected by UAV · EVA outstanding' : site.visit_fraction != null ? ((site.kind === 'EVA' ? evaProgress(run, progress) : site.kind === 'UAV' ? progress/.35 : roverProgress(run, progress)) >= site.visit_fraction ? 'Visited' : 'Scheduled') : site.status === 'Interrupted by visibility closure' && progress < (run.change_progress ?? 1) ? 'Scheduled' : site.status}</small> {site.kind === 'ROVER' && <button disabled={busy} onClick={() => guided(site.id)}>Send Perseverance</button>}</div>)}<button onClick={() => { setMapLayer('hazard'); setView('ATLAS'); }}>Open hazard map</button>
        {progress >= .65 && <p aria-live="polite">Monitoring confirmations: {run.monitor_checks.filter((check: any) => !check.warning && .65 + .35 * check.fraction <= progress).length}{run.change_progress != null && progress >= run.change_progress ? ' · Dust warning, EVA returning' : ''}</p>}{run.change_source && <p><a href={run.change_source} target="_blank" rel="noreferrer">NASA/JPL Jezero dust observations behind the simulated warning</a></p>}{progress >= .65 && <p>{run.after.reason}</p>}</section>}{run?.ground_checks?.length > 0 && (progress >= .35) && <details className="mission-detail"><summary>Rover evaluations ({run.ground_checks.filter((check: any) => check.fraction <= roverProgress(run, progress)).length}/{run.ground_checks.length})</summary>
        <ul>{run.ground_checks.filter((check: any) => check.fraction <= roverProgress(run, progress)).map((check: any, index: number) => <li key={index}>Check {index + 1} · slope {check.slope_deg.toFixed(1)}° · relief {check.relief_m.toFixed(2)} m · {check.eva_eligible ? 'EVA eligible' : 'EVA excluded'}</li>)}</ul></details>}{run?.sites?.length > 0 && <details><summary>Surface views by destination</summary>{run.sites.map((site: any) => <figure key={site.id}>
            <strong>{site.label}</strong>
            <p>{site.why}</p><p>CTX elevation {site.elevation_m} m · {site.height_above_habitat_m} m relative to habitat{site.kind==='UAV'?' · UAV only: no eligible ground route':''}</p>
            <p>Bearing from habitat {site.bearing_deg}° · straight-line distance {site.habitat_distance_m} m · local slope {site.slope_deg}°</p>
            <button onClick={()=>{setCamera('stop:'+site.cell.join(','));setView('MISSION 3D')}}>View simulated stop POV</button>

            </figure>)}</details>}
    <details><summary>Radiation and mineral observations</summary>
    <p>Curiosity RAD measured an average dose equivalent of 0.67 mSv/day at Gale Crater (August 2012–June 2013). Historical reference only. The UAV does not measure radiation in this simulation. Georeferenced radiation and mineral layers: future work.</p>
    <p><a href="https://www.nasa.gov/news-release/nasa-rover-results-include-first-age-measurement-on-mars-and-help-for-human-exploration/" target="_blank" rel="noreferrer">NASA RAD measured exposure comparison</a></p>
    <p>Perseverance SHERLOC spectra reported carbonate and olivine signatures in Séítah samples. This is a regional science reference.</p>
    <p><a href="https://ntrs.nasa.gov/citations/20220003568" target="_blank" rel="noreferrer">NASA SHERLOC spectral results</a></p></details><details className="mission-detail"><summary>Regional reference photos</summary><SciencePhotos /></details><details className="mission-detail"><summary>Export mission data</summary><div className="export-row"><button onClick={() => exportRun()}>Mission JSON ↓</button><button disabled={!run} onClick={() => exportRun(true)}>Telemetry CSV ↓</button></div></details></aside></div><footer><div className="playback"><button aria-label={playing ? 'Pause' : 'Play'} onClick={() => setPlaying(!playing)} disabled={!routes || (!!run?.habitat && (!run.habitat.started || !!run.habitat.rejections?.length) && !run.habitat.recorded)}>{playing ? 'Ⅱ' : '▶'}</button><button onClick={reset}>↺ Reset</button><input aria-label="Replay timeline" disabled={!!run?.habitat && (!run.habitat.started || !!run.habitat.rejections?.length) && !run.habitat.recorded} type="range" min="0" max="1" step=".001" value={progress} onChange={e => { setPlaying(false); setProgress(+e.target.value); }}/><span>{Math.round(progress * 100).toString().padStart(3, '0')}%</span><label>Playback speed <select aria-label="Playback speed" value={playbackRate} onChange={e=>setPlaybackRate(+e.target.value)}><option value=".5">0.5×</option><option value="1">1×</option><option value="2">2×</option><option value="4">4×</option></select></label></div></footer>{drawer && <div className="modal-backdrop" onClick={() => setDrawer(false)}><section role="dialog" aria-modal="true" aria-label="Sources and credits" className="drawer" onClick={e => e.stopPropagation()}><button className="close" onClick={() => setDrawer(false)} autoFocus>Close ×</button><span className="eyebrow">PROVENANCE / COVERAGE / ASSUMPTIONS</span><h2>Every layer has a source.</h2>{sources.map((s: any) => <article key={s.id}><span className="badge">{s.status}</span><h3>{s.name}</h3><p>{s.description}</p><a href={s.url} target="_blank" rel="noreferrer">{s.owner} ↗</a></article>)}<article><h3>Elevation coverage</h3><p>Real USGS CTX elevation crop acquired from the public archive. The 96 × 96 working grid is DERIVED, with {t?.dx_m?.toFixed(1)} × {t?.dy_m?.toFixed(1)} m spacing on a Mars sphere (radius 3,396,190 m). Native DEM sampling is 20 m. Relief is derived from the observed CTX stereo product; simulated hazards are separate.</p></article><article><h3>3D asset credits</h3><p>Perseverance: NASA/JPL. Astronaut: DigitalSpace Corporation via NASA. Neutral materials replace all textures to remove insignia. Procedural gait; enlarged visual markers, not digital twins.</p></article><p>{NOTE}</p></section></div>}</main>;
}
createRoot(document.getElementById('root')!).render(<App />);
