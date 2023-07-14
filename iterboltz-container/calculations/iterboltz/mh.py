# managing mh functionality through r spatstat scripts.
import numpy as np
from rpy2 import robjects
from rpy2.robjects.packages import importr
from rpy2.robjects import numpy2ri
from .pp import PP
import random

numpy2ri.activate()

# import parallel and spatstat
parallel = importr("parallel")
spatstat = importr("spatstat")

# --------------------------------------
# r - scripts
# --------------------------------------

# single
# TODO: remove
robjects.r(
    """
    simulate_single <- function(xrange, val, beta, size, nreps, nstart, nstates) {

        model <- rmhmodel(
            cif="lookup", 
            par=list(beta=beta, r=xrange, h=val), 
            w=square(size)
            )

        # simulate
        simulation <- rmh(model, start=list(n.start=nstart), nrep=nreps, nverb=nverb)
        return(simulation)
    }
    """
)

# -------------------------- PARALLEL -----------------------------

robjects.r(
    """
    library(parallel)
    library(spatstat)

    simulate_parallel <- function(xrange, val, beta, size, nrep, nstart, nstates) {
        numCores <- detectCores() 
        # setup cluster
        cl <- makeCluster(numCores)

        simulate_cluster <- function(c) {

                # rmh model
                model <- rmhmodel(
                    cif="lookup",
                    par=list(beta=beta, r=xrange, h=val),
                    w=square(size)
                )
                # no nstart implmenntation
                pattern <- rmh(model, nrep=nrep, nverb=1000)
                return(pattern)
            }
                
        clusterExport(cl, c("xrange", "val", "beta", "nrep", "nstart", "size"), envir=environment())
        # export cluster to all 
        clusterEvalQ(cl, library(spatstat))
        res <- parLapply(cl, 1:nstates, simulate_cluster)
        stopCluster(cl)
        return(res)
    }
    """
)

# ------------------- PARALLEL WITH INITIAL -----------------------------

robjects.r(
    """
    library(parallel)
    library(spatstat)
    simulate_xstart <- function(xrange, val, beta, size, nrep, xstart, nstates) {
        numCores <- detectCores() 
        # setup cluster
        cl <- makeCluster(numCores)

        simulate_cluster <- function(c) {

                # rmh model
                model <- rmhmodel(
                    cif="lookup",
                    par=list(beta=beta, r=xrange, h=val),
                    w=square(size)
                )
                # no nstart implmenntation
                pattern <- rmh(model, x.start=xstart, nrep=nrep, nverb=nrep)
                return(pattern)
            }
        
        xstart <- as.ppp(xstart, c(0,size,0,size))
        clusterExport(cl, c("xrange", "val", "beta", "nrep", "xstart", "size"), envir=environment())
        
        # export cluster to all 
        clusterEvalQ(cl, library(spatstat))
        res <- parLapply(cl, 1:nstates, simulate_cluster)
        stopCluster(cl)
        return(res)
    }
    """
)

# -------------------------- PARALLEL ONLY SHIFT -----------------------------

robjects.r(
    """
    library(parallel)
    library(spatstat)
    simulate_only_shift <- function(xrange, val, beta, size, nrep, xstart, nstates) {
        numCores <- detectCores() 
        # setup cluster
        cl <- makeCluster(numCores)
        simulate_cluster <- function(c) {

                # rmh model
                model <- rmhmodel(
                    cif="lookup",
                    par=list(beta=beta, r=xrange, h=val),
                    w=owin(c(0, size), c(0, size))
                )

                # no nstart implmentation
                xpattern <- ppp(xstart[,1], xstart[,2], window=owin(c(0, size), c(0, size)) )
                pattern <- rmh(model, start=list(x.start=xpattern), control=list(p=1, nrep=nrep, nverb=nrep))        

                return(pattern)
            }

        clusterExport(cl, c("xrange", "val", "beta", "nrep", "xstart", "size"), envir=environment())
        
        # export cluster to all 
        clusterEvalQ(cl, library(spatstat))
        res <- parLapply(cl, 1:nstates, simulate_cluster)
        stopCluster(cl)
        return(res)
    }
    """
)


simulate_r_method = {
    "single": robjects.globalenv["simulate_single"],
    "parallel": robjects.globalenv["simulate_parallel"],
    "xstart": robjects.globalenv["simulate_xstart"],
    "only_shift": robjects.globalenv["simulate_only_shift"]
}


class SimulationParameters():
    def __init__(
            self,
            method="single",
            runparams=None,

    ):
        self.method = method
        if runparams: self.set_params(runparams)

    def set_params(
            self,
            runparams,
            method=None,
    ):
        self.beta = runparams.beta
        if method is not None:
            self.method = method
        else:
            self.method = runparams.method
        self.hardcore = runparams.hardcore
        self.size = runparams.size
        self.nreps = runparams.nreps
        self.nstates = runparams.nstates
    
        # set start
        if self.method in ["xstart", "only_shift"]:
            self.pattern = random.choice(runparams.patterns)
            self.start = self.pattern
        else:
            self.start = 100 # TODO: set default value outside
            
            
def simulate(
        radius,
        potential,
        simControl
        ):
    
    # setup cif
    cif_lookup = np.exp(-potential)
    cif_lookup[radius < simControl.hardcore] = 0.
    
    # simulate via rmh
    patterns = simulate_r_method[simControl.method](
        radius,
        cif_lookup,
        simControl.beta,
        simControl.size,
        simControl.nreps,
        simControl.start,
        simControl.nstates
    )

    return [PP(ele).get_coords() for ele in patterns]
