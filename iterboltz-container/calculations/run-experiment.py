from iterboltz.utils import get_config, config2dict
from parameter_handler import Parameters
import sys
import pickle
def get_example(path):
    with open(path, 'rb') as f:
        obj_init = pickle.load(f)
    return obj_init

from iterboltz.ibi import IterativeBoltzmannInversion

def run_ibi(runparams):
    obj_ini = get_example(RunParams.example)
    IBI = IterativeBoltzmannInversion(runparams)
    if RunParams.pcf_initialization:
        print("running from potential")
        radius = obj_ini["radius"]
        pcf = obj_ini["rdf"]
        hardcore = obj_ini["hardcore"]
        IBI.initialize_from_rdf(pcf, radius, hardcore)
    else:
        print("running from patterns")
        # lookup = {
        #     "h": obj_ini["rdf"],
        #     "r": obj_ini["radius"],
        #     }
        
        patterns = obj_ini["patterns"]
        if RunParams.pattern_index is not None:
            # use specified pattern
            try:
                patterns = [patterns[int(RunParams.pattern_index)]]
            except:
                raise ValueError("pattern index does not exist")
            
        if RunParams.beta is not None:
            # use specified activity
            obj_ini["beta"] = RunParams.beta

        runparams.set_true_data(obj_ini)
        IBI.initialize(patterns)
    
    IBI.run(nstates=runparams.nstates, n_iterations=runparams.niter, store=False)

# load config
# get config from input
CONFIGPATH = sys.argv[1]
config = get_config(CONFIGPATH)
RunParams = Parameters()
RunParams.set_params(config2dict(config))

import os
if not os.path.exists(RunParams.get_folder_path()):
    os.makedirs(RunParams.get_folder_path())

run_ibi(RunParams)
