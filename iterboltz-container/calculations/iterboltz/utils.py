# utils
from configparser import ConfigParser
from pathlib import Path
import numpy as np
import json

# ---------------------------------------
# config handler
# ---------------------------------------

def get_config(config_path: str):
    # create config parser
    config = ConfigParser()
    config.read(config_path)
    return config

def config2dict(config: ConfigParser):
    # pass config parser to create settings dict
    settings = {}
    for section in config.sections():
        for key, item in config.items(section):
            settings[key] = item
    return settings

# ---------------------------------------
# load example
# ---------------------------------------

import pickle

def load_example(PATH):
    """function loads examples from pickle files"""
    with open(f"{PATH}/lookup.pickle", "rb") as f:
        lookup = pickle.load(f)
    with open(f"{PATH}/pattern.pickle", "rb") as f:
        pattern = pickle.load(f)
    return lookup, pattern


# ---------------------------------------
# data objects
# ---------------------------------------

class Parameters():
    def __init__(self, params):
        # set essential path strings
        self.path = params["path"]
        self.id = params["id"]
        self.gamma0 = np.float(params["gamma0"])
        self.gamma = np.float(params["gamma"])
        self.alpha = np.float(params["alpha"])
        self.r_switch = np.float(params["r_switch"])
        self.dr = np.float(params["dr"])
        self.rdf_cutoff = np.float(params["rdf_cutoff"])
        self.nstates = np.int(params["nstates"])
        self.niter = np.int(params["niter"])
        self.method = params["method"]
        self.nreps = np.int(params["nreps"])

        # set examples
        self.examples = []
        for key in params.keys():
            if key.startswith("example"):
                self.examples.append(params[key])

        # set smoothing options
        self.list_of_smoother = ["tail_correction"]

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    def set_current_example(self, example):
        self.current_example = example
    
    def set_true_data(self, true_data):
        self.true_data = true_data
        self.beta = true_data["beta"]
        self.size = true_data["size"]

    def storepath(self):
        print(self.current_example)
        return f"{self.path}results/{self.current_example}/run{self.id}"