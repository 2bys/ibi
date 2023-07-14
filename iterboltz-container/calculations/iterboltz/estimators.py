# ---------------------------------------------------------------------
# utils
# ---------------------------------------------------------------------

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects import numpy2ri
numpy2ri.activate()
import numpy as np

spatstat = importr("spatstat")

def create_dict(obj):
    """generate dictionary"""
    return dict(zip(obj.names, list(obj)))

patternObj = robjects.r(
    """   
    pattern <- function(x, y, size, size1)  {
          X <- ppp(x, y, c(0,size),c(0,size1))
          X
      }    
    """
)

pattern_r = robjects.r["pattern"]


def pattern2ppp(pattern, size):
    """take numpy array and convert to ppp

    Parameters
    ----------
    pattern : numpy array
        [description]
    size : int
        [description]
        
    Returns
    -------
    ppp : rpy2 object
        [description]
    """
    x_coord = pattern[:,0]
    y_coord = pattern[:,1]

    return pattern_r(x_coord, y_coord, size, size)

# ---------------------------------------------------------------------
# hardcore estimator
# ---------------------------------------------------------------------

from scipy.spatial import distance

def get_min_r(coords):
    """calculate hardcore distance"""
    # [TODO] use scipy.spatial.distance.cdist
    dist_r = []
    for i, pt1 in enumerate(coords):
        for pt2 in coords[i+1:]:
            r = distance.euclidean(
                np.array(pt1), np.array(pt2)
                )
            dist_r.append(r)
    return np.min(dist_r)

# ---------------------------------------------------------------------
# pair correlation function estimator (via kernel smoothing - spatstat)
# ---------------------------------------------------------------------

objects1 = robjects.r("""
pcf_calc <- function(pp, xrange, kernel, divisor, correction) {

        pcf(pp,
        r=xrange,
        kernel=kernel,
        divisor=divisor,
        correction=correction)

        }
"""
)

objects2 = robjects.r(
   """
    pcf_calc_loh_ci <- function(pp, maxval, rnmb) {
        lohboot(pp, pcf, rmax=maxval, nr=rnmb, confidence=0.95)
        }
    """ 
)

# set methods
pcf_r = robjects.r["pcf_calc"]
pcf_calc_loh_ci = robjects.r["pcf_calc_loh_ci"]

def get_pcf_by_r(pattern, size, dr=.01, cutoff=1., ci=True, 
                 kernel="epanechnikov", 
                 divisor="d", 
                 correction="isotropic"):
    # pass points to r ppp
    ppp = pattern2ppp(pattern, size)
    # create range
    xrange = np.arange(0.,cutoff,dr)
    # calculate pcf
    out = pcf_r(ppp, xrange, kernel, divisor, correction)
    pcf_values = create_dict(out)["iso"]
    if ci:
        # calculate confidence intervals
        ci_values = pcf_calc_loh_ci(ppp, cutoff, len(xrange))
        ci_values = create_dict(ci_values)
    else: 
        ci_values = None    
    return xrange, pcf_values, ci_values

# ---------------------------------------------------------------------
# visualization
# ---------------------------------------------------------------------
import matplotlib.pyplot as plt

# plot pair correlation function
def plot_pcr_with_ci(radius, pcf_values, ci_values):
    plt.fill_between(ci_values["r"], ci_values["lo"], ci_values["hi"], 
                     alpha=0.2, label="95% CI (Loh)")
    plt.plot(radius, pcf_values, label="pcf")
    plt.xlabel("r")
    plt.ylabel("g(r)")    
    plt.legend()
