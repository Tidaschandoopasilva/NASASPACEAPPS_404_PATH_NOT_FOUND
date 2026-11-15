"""Fixed-step kinematic approximation, not rocker-bogie dynamics."""
import math,numpy as np
class Rover:
    def __init__(self,seed=0):self.x=0.;self.y=0.;self.heading=0.;self.rng=np.random.default_rng(seed)
    def step(self,speed=.2,steering=0,slope_deg=0,mu=.6,dt=.5):
        pitch=math.radians(slope_deg);slip=max(0.,min(.95,(math.tan(abs(pitch))-mu)*1.5)) if speed else 0.
        self.heading+=steering*dt;actual=speed*(1-slip);self.x+=actual*math.cos(self.heading)*dt;self.y+=actual*math.sin(self.heading)*dt
        return {'x_m':self.x,'y_m':self.y,'heading_rad':self.heading,'slip':slip,'pitch_deg':slope_deg,'roll_deg':0.,'speed_m_s':actual,'wheel_omega_rad_s':speed/.2625,'dt_s':dt,'data_state':'SIMULATED'}
