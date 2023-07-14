# general class for iterative boltzmann inversoin
import numpy as np
from .pair import PairPotential
from .mh import SimulationParameters, simulate
from .estimators import get_min_r
import pickle

def store_history(obj, i):
    params = obj.parameters
    hist = obj.pair.hist
    with open(params.get_hist_name(i), "wb") as f:
        pickle.dump(hist, f)

class IterativeBoltzmannInversion():
    def __init__(self, parameters):
        self.parameters = parameters

    def run(self, n_iterations=10, nstates=None, store=False):
        # run n_iterations of IBI
        if nstates is None:
            nstates = self.parameters.nstates
            
        for i in range(n_iterations):
            self._step(nstates)
            if store:
                store_history(self, i)
            else:
                if i == n_iterations - 1:
                    store_history(self, i)

    def _step(self, nstates=1):
        # simulate new patterns
        self.parameters.patterns = self.pair.patterns
        simControl = SimulationParameters(runparams=self.parameters)
        patterns = simulate(
            self.pair.radius[1:],
            self.pair.potential[:-1],
            simControl,
        )
        # update potential
        self.pair.patterns = patterns.copy()
        self.pair.update_potential(patterns)

    def initialize_from_rdf(self, rdf, radius, hardcore):
        self.parameters.hardcore = self.hardcore = hardcore
        # initialize pair potential object
        self.pair = PairPotential(None, self.parameters, rdf, radius)
        # create initial patterns
        simControl = SimulationParameters()
        simControl.set_params(self.parameters, method="parallel")
        simControl.nstates = 8
        simControl.nreps = 20000
        patterns = simulate(
            self.pair.radius[1:],
            self.pair.potential[:-1],
            simControl,
        )
        self.parameters.patterns = self.pair.patterns = patterns.copy()
        

    def initialize(self, patterns):
        # if array, convert to list
        if isinstance(patterns, np.ndarray):
            patterns = [patterns]
        
        # get hardcore range
        self.hardcore = min([get_min_r(pattern) for pattern in patterns])        
        self.parameters.hardcore = max(self.hardcore, self.parameters.hardcore)
        
        # initialize pair potential object
        self.pair = PairPotential(patterns, self.parameters)
