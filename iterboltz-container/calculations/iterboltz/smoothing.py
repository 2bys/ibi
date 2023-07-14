# smoothing operations
import numpy as np
# ----------------- strong enforcer ----------------- #

def strong_enforcer(V):
    V = V.copy()

    # set all nan to np.inf
    V[np.isnan(V)] = np.inf

    # set first value to np.inf 
    V[0] = np.inf

    # set last value two values to 0.
    V[-2:] = 0.

    return V

# ----------------- head correction ----------------- #

# ----------------- tail correction ----------------- #

def find_nearest(array, target):
    """Find array component whose numeric 
    value is closest to 'target'. """
    idx = np.abs(array - target).argmin()
    return idx, array[idx]

def tail_correction(r, V, r_switch=2.0, runparams=None):
    if runparams:
        r_switch = runparams.r_switch
    r_cut = r[-1]
    idx_r_switch, r_switch = find_nearest(r, r_switch)

    S_r = np.ones_like(r)
    r = r[idx_r_switch:]
    S_r[idx_r_switch:] = ((r_cut ** 2 - r ** 2) ** 2 *
            (r_cut ** 2 + 2 * r ** 2 - 3 * r_switch ** 2) /
            (r_cut ** 2 - r_switch ** 2) ** 3)
    return V * S_r

# ----------------- pressure correction ----------------- #
def pressure_correction(r, r_cut, a):
    return a * (1 - r / r_cut)

def apply_pressure_correction(r, V, runparams):
    a = runparams.a
    r_cut = runparams.r_cut
    return V + pressure_correction(r, r_cut, a)

# ----------------- smoothing class ----------------- #

smoothing_options = {
    "tail_correction": tail_correction,
    "pressure_correction": apply_pressure_correction,
}

class PotentialSmoother():
    def __init__(self, runparams=None):
        if runparams:
            self.list_of_methods = runparams.list_of_smoother
            self.runparams = runparams

    def smooth(self, r, V):
        for method in self.list_of_methods:
            V = smoothing_options[method](r, V, runparams=self.runparams)
        return V
