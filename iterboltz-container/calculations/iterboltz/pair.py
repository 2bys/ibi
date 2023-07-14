# implements the pair potential class and the corresponding hist object
import numpy as np

#TODO: Find best structure for storage
class HistPairPotential():
    def __init__(
            self,
            smoothed_potential,
            potential,
            target_rdf,
            rdfs,
            cis,
            patterns,
            radius,
            true_data=None
    ):
        # store patterns
        self.patterns = patterns

        # store true data
        self.true_data = true_data

        # initialize arrays
        self.potentials_pre_smoothing = [potential]
        self.potentials = [smoothed_potential]
        self.target_rdf = target_rdf
        self.target_rdfs = rdfs
        self.target_cis = cis
        self.radius = radius

        # for the update rounds
        self.iteration = 1
        self.rdfs = []
        self.rounds = []

    def store_update(self,
                current_pot,
                pre_smoothed_pot,
                current_rdf,
                rdfs,
                cis,
                patterns
                ):
        # store current potential
        self.potentials.append(current_pot)
        self.potentials_pre_smoothing.append(pre_smoothed_pot)
        self.rdfs.append(current_rdf)
        self.rounds.append(
            {
                "iteration": self.iteration,
                "rdfs": rdfs,
                "cis": cis,
                "potential": current_pot,
                "rdf": current_rdf,
                "patterns": patterns
            }
        )

        # increment iteration
        self.iteration += 1

from .smoothing import PotentialSmoother

class PairPotential():
    def __init__(self,
                 patterns,
                 params,
                 pcf = None,
                 radius = None
                 ):
        # set parameters
        self.params = params
        self.dr = params.dr
        self.gamma0 = params.gamma0
        self.gamma = params.gamma
        self.alpha = params.alpha
        self.r_switch = params.r_switch
        self.size = params.size
        self.hardcore = params.hardcore

        # get smoothing operations
        self.smoother = PotentialSmoother(params)

        # set rdf method and cutoff
        self.rdf = params.rdf
        self.rdf_cutoff = params.rdf_cutoff

        # initialize potential
        if pcf is not None:
            self.target_rdf = pcf[radius < self.rdf_cutoff]
            self.radius = radius[radius < self.rdf_cutoff]
            self.patterns = patterns
            rdfs = None
            cis = None
            true_data = None
        else:    
            self.patterns = patterns     
            rdfs, cis = self.get_pcf0()
            true_data = params.true_data

        smoothed_potential = self.step0()

        # initialize hist obj
        self.hist = HistPairPotential(
            smoothed_potential,
            self.potential,
            self.target_rdf,
            rdfs,
            cis,
            patterns,
            self.radius,
            true_data
        )
        self.potential = smoothed_potential

    def compute_current_rdf(self, pattern):
        # calculate rdf
        r, g_r, ci = self.rdf(
            pattern, 
            self.size, 
            dr = self.dr, 
            cutoff = self.rdf_cutoff
            )

        return r, g_r, ci
    
    def update_potential(self, patterns):
        # calculate new current rdf
        self.patterns = patterns
        rdfs = []
        cis = []
        for pattern in patterns:
            _, rdf, ci = self.compute_current_rdf(pattern) 
            rdfs.append(rdf)
            cis.append(ci)

        # get mean and so new current
        self.current_rdf = np.mean(rdfs, axis=0)

        # update potential
        log = np.log(self.current_rdf / self.target_rdf)
        self.potential += (self.gamma * log)

        # apply smoothing
        smoothed_potential = self.smoother.smooth(
            self.radius,
            self.potential.copy(), 
            # self.hardcore, 
            # self.r_switch, 
            # self.alpha * self.gamma
            )

        # store all information
        self.hist.store_update(
            smoothed_potential,
            self.potential,
            self.current_rdf,
            rdfs,
            cis,
            patterns,
        )

        self.potential = smoothed_potential

    def get_pcf0(self):
        # compute rdf
        rdfs = []
        cis = []
        for pattern in self.patterns:
            radius, rdf, ci = self.compute_current_rdf(pattern) # why not pass dr?
            rdfs.append(rdf) 
            cis.append(ci)

        # get target by taking the mean
        self.radius = radius
        self.target_rdf = np.mean(rdfs, axis=0)
        
        return rdfs, cis

    def step0(self):

        # get initial potential
        self.potential = -self.gamma0 * np.log(self.target_rdf)

        # apply smoothing
        smoothed_potential = self.smoother.smooth(
            self.radius,
            self.potential.copy(),
            # self.radius,
            # self.hardcore,
            # self.r_switch,
            # self.alpha * self.gamma0
        )
        return smoothed_potential#, rdfs, cis
