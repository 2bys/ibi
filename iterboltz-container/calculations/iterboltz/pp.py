import numpy as np
from rpy2 import robjects
import matplotlib.pylab as plt

# Code from pp
import rpy2
from rpy2.robjects.packages import importr
import numpy as np

# generally import spatstat package
spatstat = importr("spatstat")

import matplotlib.pylab as plt

def create_dict(obj):
    """generate dictionary"""
    return dict(zip(obj.names, list(obj)))

def is_rpy2_object(x):
    """test if rpy2 ListVector"""
    return type(x) is rpy2.robjects.vectors.ListVector

class PP():
    def __init__(self, X):
        self.pp_r = None
        self.pp = None
        self.window = None
        self.n = None
        self.x = None
        self.y = None
        
        if is_rpy2_object(X):
            self.initialize(X)
        else:
           raise ValueError("Input is no r object.") 

    def initialize(self, X):
        # Pass point pattern to python
        # Create pp_dict for r pp X
        self.pp_r = X
        self.pp = create_dict(X)
        self.window = create_dict(self.pp["window"])
        self.n = np.array(self.pp["n"])[0]
        self.x = np.array(self.pp["x"])
        self.y = np.array(self.pp["y"])

        self.window["type"] = np.array(self.window["type"])[0]
        self.window["xrange"] = np.array(self.window["xrange"])
        self.window["yrange"] = np.array(self.window["yrange"])
        self.window["units"] = np.array(self.window["units"])

    def plot(self):
        fig = plt.figure()
        plt.scatter(self.x, self.y, marker=".")
        plt.gca().set_aspect("equal")

    def get_coords(self):
        return np.array([self.x,self.y]).T