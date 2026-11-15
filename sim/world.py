"""Hidden states exist exclusively in simulator instances; never passed to planner."""
import numpy as np
class HiddenWorld:
    def __init__(self,seed,priors):
        self.rng=np.random.default_rng(seed);self.__truth_map=self.rng.random(len(priors))<np.array(priors)
    def observation(self,k,sigma=.08):
        slip=float(self.rng.normal(.282915 if self.__truth_map[k] else .09748,sigma));return int(slip>.2),slip
    def evaluate_crossings(self,indices):return int(sum(self.__truth_map[k] for k in set(indices)))
