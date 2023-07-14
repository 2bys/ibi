import numpy as np
import json
from iterboltz.estimators import get_min_r
from iterboltz.estimators import get_pcf_by_r

class Parameters():
    def __init__(self):
        # path variables
        self.path = "./"
        self.id = 1

        # pcf relevant 
        self.bw = False
        self.kernel = "epanechnikov"
        self.divisor = "d"
        self.rdf_cutoff = 1.0
        self.dr = 0.01
        self.rdf = get_pcf_by_r

        # mh parameters 
        self.nstates = 8
        self.niter = 10 
        self.method = "only_shift"
        self.nreps = self.niter
        self.hardcore = 0.0

        # update parameters
        self.gamma0 = float(1.)
        self.gamma = float(0.1)
        self.alpha = float(0.)

        # correction parameters
        self.r_switch = float(0.9)

        # set smoothing options
        self.list_of_smoother = ["tail_correction"]

    def set_params(self, params):
        self.path = params["path"]
        self.id = params["id"]
        self.gamma0 = float(params["gamma0"])
        self.gamma = float(params["gamma"])
        self.alpha = float(params["alpha"])
        self.r_switch = float(params["r_switch"])
        self.dr = float(params["dr"])
        self.rdf_cutoff = float(params["rdf_cutoff"])
        self.nstates = int(params["nstates"])
        self.niter = int(params["niter"])
        self.method = params["method"]
        self.nreps = int(params["nreps"])
        self.pcf_initialization = params["pcf"] == 'True' #bool(params["pcf"])
        self.example = params["example"]
        self.example_id = int(params["example_id"])
        self.experiment_id = int(params["experiment_id"])
        self.hardcore = float(params["hardcore"])
        if params["beta"] != "False":
            self.beta = float(params["beta"])
        else:
            self.beta = None
        if params["pattern_index"] != "False":
            self.pattern_index = int(params["pattern_index"])
        else:
            self.pattern_index = None

        self.size = float(params["size"])

        # set smoothing options
        self.list_of_smoother = ["tail_correction"]

    def set_current_example(self, example):
        self.current_example = example
    
    def set_example(self, true_data, pattern, exampleId = 1):
        self.true_data = true_data
        self.pattern = pattern
        self.beta = true_data["beta"]
        self.size = true_data["size"]
        self.current_example = exampleId

    def set_true_data(self, true_data, beta=None):
        self.true_data = true_data
        if beta is not None:
            self.beta = beta
        else:
            self.beta = true_data["beta"]
        self.size = true_data["size"]

    def get_folder_path(self):
        return f"{self.path}example{self.example_id}/experiment{self.experiment_id}/run{self.id}/"
    
    def get_name(self):
        return f"{self.path}example{self.example_id}/experiment{self.experiment_id}/run{self.id}/run{self.id}"
        
    def get_hist_name(self, i):
        return f"{self.path}example{self.example_id}/experiment{self.experiment_id}/run{self.id}/run{self.id}_iter{i}.pickle"

