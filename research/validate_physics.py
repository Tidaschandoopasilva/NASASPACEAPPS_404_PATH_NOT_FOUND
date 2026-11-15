"""Optional 30-trial six-wheel rigid-body stress test; NOT model validation by itself.
Install PyBullet in a compatible Python environment. This script is not a flight model.
"""
import sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.terrain import ROOT

def main():
    try:import pybullet as p
    except ImportError:raise SystemExit('PyBullet unavailable. Use a compatible Python 3.11 environment; no physics results generated.')
    scenarios=[json.loads(x) for x in (ROOT/'data/svnet/scenarios.jsonl').read_text().splitlines() if json.loads(x)['split']=='test'][:30]
    results=[]
    for i,s in enumerate(scenarios):
        client=p.connect(p.DIRECT);p.setGravity(0,0,-3.71);p.setTimeStep(1/240)
        slope=min(20.,s['public']['routes']['proceed']['mean_slope']);mu=[.15,.4,.8][i%3]
        ground=p.createCollisionShape(p.GEOM_BOX,halfExtents=[20,20,.1]);p.createMultiBody(baseMass=0,baseCollisionShapeIndex=ground,basePosition=[0,0,-.1],baseOrientation=p.getQuaternionFromEuler([0,-math.radians(slope),0]))
        body=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.9,.65,.2]);wheel=p.createCollisionShape(p.GEOM_CYLINDER,radius=.2625,height=.18)
        positions=[[x,y,-.28] for x in [-.7,0,.7] for y in [-.75,.75]]
        robot=p.createMultiBody(baseMass=905,baseCollisionShapeIndex=body,basePosition=[0,0,.8],linkMasses=[20]*6,linkCollisionShapeIndices=[wheel]*6,linkVisualShapeIndices=[-1]*6,linkPositions=positions,linkOrientations=[p.getQuaternionFromEuler([math.pi/2,0,0])]*6,linkInertialFramePositions=[[0,0,0]]*6,linkInertialFrameOrientations=[[0,0,0,1]]*6,linkParentIndices=[0]*6,linkJointTypes=[p.JOINT_REVOLUTE]*6,linkJointAxis=[[0,1,0]]*6)
        for j in range(6):p.changeDynamics(robot,j,lateralFriction=mu);p.setJointMotorControl2(robot,j,p.VELOCITY_CONTROL,targetVelocity=0,force=20)
        for _ in range(240):p.stepSimulation()
        start=p.getBasePositionAndOrientation(robot)[0]
        for j in range(6):p.setJointMotorControl2(robot,j,p.VELOCITY_CONTROL,targetVelocity=.2/.2625,force=35)
        for _ in range(2400):p.stepSimulation()
        end,orientation=p.getBasePositionAndOrientation(robot);distance=math.dist(start,end);pitch=p.getEulerFromQuaternion(orientation)[1]
        results.append({'scenario_id':s['id'],'slope_deg':slope,'assumed_friction':mu,'command_m_s':.2,'duration_s':10,'displacement_m':distance,'slip_proxy':1-distance/2,'final_pitch_deg':math.degrees(pitch),'physics':'PyBullet six-wheel rigid chassis on constant-slope plane, no rocker-bogie articulation','source_ids':['usgs-ctx-dem']});p.disconnect(client)
    out=ROOT/'data/svnet/physics_trials.json';out.write_text(json.dumps({'note':'Approximation; stress tests, not validated Perseverance dynamics. Constant slope is derived from each route mean, not full DEM replay.','trials':results},indent=2));print('Wrote',len(results),'actual PyBullet trials')
if __name__=='__main__':main()
