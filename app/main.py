from pathlib import Path
from typing import Literal
import json,re
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field,field_validator
from fastapi.middleware.cors import CORSMiddleware
from app.service import compare,simulate,DEFAULT_POINTS,NOTE
from app.terrain import ROOT,load,planetary,world
from app.decision import estimate
app=FastAPI(title='404: PATH NOT FOUND',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_methods=['GET','POST'],allow_headers=['Content-Type'])
class Request(BaseModel):
    seed:int=Field(default=7,ge=0,le=2147483647)
    prior:float=Field(default=.3,ge=.001,le=.999)
    cost:float=Field(default=5,ge=0,le=500)
    sigma:float=Field(default=.08,ge=.01,le=.5)
    budget:float=Field(default=180,ge=1,le=600)
    max_slope:float=Field(default=20,ge=1,le=45)
    points:list[list[int]]=Field(default_factory=lambda:DEFAULT_POINTS.copy(),min_length=3,max_length=3)
    @field_validator('points')
    @classmethod
    def bounded(cls,v):
        if any(len(p)!=2 or any(x<0 or x>=96 for x in p) for p in v):raise ValueError('Exactly 3 [row,column] points, indices 0..95')
        return v
@app.get('/health')
def health():return {'status':'ok','version':'1.0.0','note':NOTE}
@app.get('/api/v1/terrain')
def terrain():return load()[0]
@app.get('/api/v1/sources')
def sources():return json.loads((ROOT/'apps/web/public/data/sources.json').read_text())
@app.get('/api/v1/layers')
def layers():return [{'id':'imagery','data_state':'OBSERVED','source_ids':['nasa-trek-hirise']},{'id':'terrain','data_state':load()[0]['data_state'],'source_ids':load()[0]['source_ids']},{'id':'uncertainty','data_state':'ASSUMED','source_ids':load()[0]['source_ids']}]
@app.get('/api/v1/sites')
def sites():
    t=load()[0];return [{'id':n,'position_m':world(t,*p),'latitude_deg':planetary(t,*p)[0],'longitude_east_deg':planetary(t,*p)[1],'grid':p,'data_state':'ASSUMED','coordinate_system':t['coordinate_system'],'units':'meters and degrees','source_ids':['usgs-geology']} for n,p in zip(['Fictional habitat','Science A: sedimentary investigation','Science B: crater-floor investigation'],DEFAULT_POINTS)]
@app.post('/api/v1/routes/compare')
def routes(r:Request):return compare(r.points,r.budget,r.prior,r.max_slope)
@app.post('/api/v1/scout/estimate')
def scout(r:Request):return estimate(r.prior,r.cost,sigma=r.sigma)
@app.post('/api/v1/simulations')
def simulation(r:Request):return simulate(r.seed,r.prior,r.cost,r.sigma,r.points,r.budget)
@app.get('/api/v1/simulations/{run_id}')
def read_simulation(run_id:str):
    if not re.fullmatch('[a-f0-9]{32}',run_id):raise HTTPException(404)
    f=ROOT/'data/runs'/f'{run_id}.json'
    if not f.exists():raise HTTPException(404)
    return json.loads(f.read_text())
@app.get('/api/v1/experiments/summary')
def experiments():
    p=ROOT/'apps/web/public/data/experiments.json'
    if not p.exists():raise HTTPException(404,'Run scripts\\run_experiments.py first')
    return json.loads(p.read_text())

@app.get('/api/v1/ml/model')
def ml_model():
    p=ROOT/'models/svnet_v1/metadata.json'
    if not p.exists():raise HTTPException(503,'404-SVNet has not been trained')
    return json.loads(p.read_text())
@app.post('/api/v1/ml/predict')
def ml_predict(r:Request):
    from app.ml.policy import live_decision
    try:return live_decision(r.points,r.budget,r.prior,r.cost,r.sigma)
    except FileNotFoundError:raise HTTPException(503,'Run research/train_svnet.py first')
@app.get('/api/v1/ml/evaluation')
def ml_evaluation():return json.loads((ROOT/'models/svnet_v1/evaluation.json').read_text())
@app.get('/api/v1/ml/scenarios')
def ml_scenarios():
    rows=[json.loads(x) for x in (ROOT/'data/svnet/scenarios.jsonl').read_text().splitlines()]
    return [{'id':x['id'],'region':x['region'],'source_window':x['source_window']} for x in rows if x['split']=='test']
@app.get('/api/v1/ml/scenarios/{scenario_id}')
def ml_scenario(scenario_id:str):
    from app.ml.inference import predict
    if not re.fullmatch('test-[0-9]{4}',scenario_id):raise HTTPException(404)
    for line in (ROOT/'data/svnet/scenarios.jsonl').read_text().splitlines():
        scenario=json.loads(line)
        if scenario['id']==scenario_id:
            return {'id':scenario_id,'source_window':scenario['source_window'],'prediction':predict(scenario['public']),'observed_simulated_outcomes':scenario['outcomes'],'geometry':scenario['geometry'],'note':'Held-out evaluation episode; outcomes are displayed only after inference and never passed to model.'}
    raise HTTPException(404)

@app.post('/api/v1/ml/execute')
def ml_execute(r:Request):
    from app.ml.policy import live_decision
    from app.ml.features import choose_after_observation
    from app.decision import sensor_rates,posterior
    from sim.world import HiddenWorld
    from sim.rover import Rover
    import uuid
    decision=live_decision(r.points,r.budget,r.prior,r.cost,r.sigma);action=decision['recommendation'].lower()
    if action=='human review':raise HTTPException(409,'No acceptable simulated plan; review constraints')
    if action!='scout':return {'kind':'route','action':action.upper(),'route':decision['route_candidates'][action],'source_ids':decision['source_ids'],'model_version':decision['model_version']}
    public=decision['public_inputs'];hidden=HiddenWorld(r.seed,[r.prior]);obs,slip=hidden.observation(0,r.sigma);tpr,fpr=sensor_rates(r.sigma);post=posterior(r.prior,obs,tpr,fpr)
    chosen=choose_after_observation(public['routes']['proceed'],public['routes']['avoid'],post);robot=Rover(r.seed);run_id=uuid.uuid4().hex
    episode={'id':run_id,'run_id':run_id,'sim_seed':r.seed,'trial_status':'completed','model_version':decision['model_version'],'data_state':'SIMULATED','source_ids':decision['source_ids'],'note':NOTE,'before':decision['route_candidates']['proceed'],'after':decision['route_candidates'][chosen],'observation':{'corridor':0,'positive':bool(obs),'slip':slip,'prior':r.prior,'posterior':post},'corridor_center_grid':decision['corridor_center_grid'],'estimate':decision,'telemetry':[{'step':i,**robot.step()} for i in range(80)],'events':[{'t':0,'label':'Learned SCOUT selected'},{'t':.35,'label':'Simulated observation'},{'t':.65,'label':'Posterior candidate route selected'},{'t':1,'label':'Return route'}]}
    directory=ROOT/'data/runs';directory.mkdir(exist_ok=True);(directory/f'{run_id}.json').write_text(json.dumps(episode));return {'kind':'episode','episode':episode}

class MeshSurveyRequest(Request):
    payload_kg: float = Field(default=10, ge=0, le=50)
    objective: Literal["relief", "texture"] = "relief"
    center: tuple[float, float] = (54, 44)
    radius: float = Field(default=1800, ge=100, le=3500)
    rover_site: int | None = None
    ground_verify: bool = False
    eva_goals: int = Field(default=3, ge=0, le=6)
    rover_goals: int = Field(default=3, ge=0, le=6)
    sortie: int = Field(default=1, ge=1, le=6)
    condition: Literal["day","night","heat","dust"] = "day"
    new_expedition: bool = False
    equipment: list[Literal["heater","cooler","visibility"]] | None = Field(default=None,max_length=3)

    @field_validator('center')
    @classmethod
    def center_in_grid(cls, value):
        if not all(0 <= coordinate <= 95 for coordinate in value):
            raise ValueError('Survey center must be inside the map')
        return value


@app.post('/api/v1/mesh-survey')
def mesh_survey(request: MeshSurveyRequest):
    from app.mesh_survey import plan_survey
    return plan_survey(request.center, request.radius, request.points, request.seed,
                       request.budget, request.max_slope, request.rover_site, request.condition, request.eva_goals, request.rover_goals, request.sortie, request.ground_verify, request.payload_kg, request.objective)


class ExpeditionCommit(BaseModel):
    id: str = Field(pattern=r"^[a-f0-9]{32}$")


@app.get("/api/v1/habitat")
def habitat_status():
    from app.habitat import status
    return status()


@app.post("/api/v1/habitat/plan")
def habitat_plan(request: MeshSurveyRequest):
    from app.habitat import prepare
    try:
        return prepare(request.model_dump(), lambda config: mesh_survey(MeshSurveyRequest(**config)), load()[0])
    except ValueError as error:
        raise HTTPException(409, str(error)) from error


@app.post("/api/v1/habitat/record")
def habitat_record(request: ExpeditionCommit):
    from app.habitat import commit
    try:
        return commit(request.id)
    except ValueError as error:
        raise HTTPException(409, str(error)) from error


@app.get("/api/v1/habitat/replay/{expedition_id}")
def habitat_replay(expedition_id: str):
    from app.habitat import replay
    try:
        return replay(expedition_id)
    except ValueError as error:
        raise HTTPException(404, str(error)) from error


class ExpeditionProgress(ExpeditionCommit):
    progress: float = Field(ge=0, le=1)
    sequence: int = Field(ge=1)


class HabitatAdvance(BaseModel):
    revision: int = Field(ge=0)


@app.post("/api/v1/habitat/telemetry")
def habitat_telemetry(request: ExpeditionProgress):
    from app.habitat import publish_progress
    try:
        return publish_progress(request.id, request.progress, request.sequence)
    except ValueError as error:
        raise HTTPException(409, str(error)) from error


@app.post("/api/v1/habitat/advance")
def habitat_advance(request: HabitatAdvance):
    from app.habitat import advance_habitat
    try:
        return advance_habitat(request.revision)
    except ValueError as error:
        raise HTTPException(409, str(error)) from error


@app.post("/api/v1/habitat/discard")
def habitat_discard(request: ExpeditionCommit):
    from app.habitat import discard
    return discard(request.id)


@app.post("/api/v1/habitat/start")
def habitat_start(request: ExpeditionCommit):
    from app.habitat import start_expedition
    try:
        return start_expedition(request.id)
    except ValueError as error:
        raise HTTPException(409, str(error)) from error


class MissionQuestion(MeshSurveyRequest):
    question: str = Field(min_length=3,max_length=250)
    plan_id: str | None = Field(default=None,pattern=r"^[a-f0-9]{32}$")
    rejections: list[str] = Field(default_factory=list,max_length=12)


@app.post("/api/v1/habitat/briefing")
def habitat_briefing(request: MissionQuestion):
    from app.mission_qa import answer
    from app.habitat import load_draft
    draft = None
    if request.plan_id:
        try:
            candidate = load_draft()
            if candidate["habitat"]["id"] == request.plan_id:
                draft = candidate
        except ValueError:
            pass
    rejections = draft["habitat"]["rejections"] if draft else [line[:200] for line in request.rejections]
    return answer(request.question, draft["request"] if draft else request.model_dump(), draft, rejections)


@app.get("/api/v1/habitat/draft")
def habitat_draft():
    from app.habitat import load_draft
    try:
        return load_draft()
    except ValueError as error:
        raise HTTPException(404, str(error)) from error


def weather_cache():
    from app.habitat import database_path
    database = database_path()
    return database.parent / (database.stem + "-weather")


@app.get("/api/v1/weather")
def weather_status():
    from app.weather import report
    return report(weather_cache())


@app.post("/api/v1/weather/refresh")
def weather_refresh():
    from app.weather import refresh
    try:
        return refresh(weather_cache())
    except (OSError,ValueError,KeyError,TypeError) as error:
        raise HTTPException(502, "NASA refresh unavailable or invalid. Cached readings are retained.") from error


class OrbitalContext(BaseModel):
    instrument: Literal["Odyssey THEMIS","MRO MARCI","MRO MCS"]
    product: str = Field(min_length=2,max_length=150)
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    bounds: tuple[float,float,float,float]
    dust_flag: bool = False


@app.post("/api/v1/weather/orbital")
def weather_orbital(entry: OrbitalContext):
    from app.weather import import_orbital
    try:
        return import_orbital(weather_cache(),entry.model_dump())
    except ValueError as error:
        raise HTTPException(422,str(error)) from error
