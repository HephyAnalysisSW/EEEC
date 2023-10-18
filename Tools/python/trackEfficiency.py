from ROOT import TLorentzVector
from copy import copy
import numpy as np
import random

def getEfficiency(pt, eta, type=None):
    # Model efficiency curves from center right plot of Figure 8 in
    # https://arxiv.org/pdf/1405.6569.pdf
    # Model with two straight lines (as function of log(pT))
    # One from pt=0.1 to pt=1, another from pt=1 to pt=100
    eff0p1, eff1p0, eff100 = 0., 0., 0.
    if abs(eta) < 0.9:
        eff0p1, eff1p0, eff100 = 0.43, 0.96, 0.93
    elif abs(eta) > 0.9 and abs(eta) < 1.4:
        eff0p1, eff1p0, eff100 = 0.38, 0.94, 0.87
    elif abs(eta) > 1.4:
        eff0p1, eff1p0, eff100 = 0.33, 0.87, 0.81

    a = 0.0
    b = 1.0
    if pt < 1.0:
        a = eff1p0 - eff0p1
        b = eff1p0
    elif pt > 1.0:
        a = (eff100 - eff1p0)/2
        b = eff1p0

    return a*np.log10(pt)+b

def applyEfficiency(particles, mode, blist = None):
    if mode not in ["realistic", "realisticScale", "flat", "flatScale", "Bfrag", "BfragScale"]:
        raise RuntimeError( "Efficiency mode %s is not knwon:"%(mode) )
    if mode in ["Bfrag", "BfragScale"] and blist is None:
        raise RuntimeError( "For efficiency mode Bfrag you need to provide a list")
    SF = 0.5
    particles_copy = list(particles) # Copy list to not loop over the list from which we remove entries
    for i,p in enumerate(particles_copy):
        efficiency = 1.0
        if mode == "realistic":
            efficiency = getEfficiency(p.pt(), p.eta())
        elif mode == "realisticScale":
            efficiency = getEfficiency(p.pt(), p.eta()) * SF
        elif mode == "flat":
            efficiency = 0.7
        elif mode == "flatScale":
            efficiency = 0.7 * SF
        elif mode == "Bfrag":
            if i in blist:
                efficiency = 0.7
            else:
                efficiency = 1.0
        elif mode == "BfragScale":
            if i in blist:
                efficiency = 0.7 * SF
            else:
                efficiency = 1.0
        r = random.uniform(0, 1)
        if r < (1.0-efficiency):
            particles.remove(p)
    return particles
