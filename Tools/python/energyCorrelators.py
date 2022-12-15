from EEEC.Tools.helpers import deltaRGenparts
from math import sqrt
from ROOT import TLorentzVector

def getZeta(p1, p2, pp = False):
    if pp:
        return p1.delta_R(p2)
    else:
        product = p1.px()*p2.px() + p1.py()*p2.py() + p1.pz()*p2.pz() 
        mag1 = sqrt(p1.px()**2 + p1.py()**2 + p1.pz()**2)
        mag2 = sqrt(p2.px()**2 + p2.py()**2 + p2.pz()**2)
        costheta = product / (mag1*mag2)
        return (1-costheta)/2

def getTriplets(scale, constituents, n=2, max_zeta=None, max_delta_zeta=None, delta_legs=None, shortest_side=None):
    triplets = []
    for i in range(len(constituents)):
        for j in range(i+1, len(constituents)):
            for k in range(j+1, len(constituents)):
                zeta_values = [
                    getZeta(constituents[i], constituents[j], pp = True),
                    getZeta(constituents[i], constituents[k], pp = True),
                    getZeta(constituents[j], constituents[k], pp = True),
                    ]
                zeta_values.sort()


                # Check if smallest dR is small enough
                if max_zeta is not None:
                    if zeta_values[0] > max_zeta:
                        continue
                # Check if the dRs form an equilateral triangle (for top)
                if max_delta_zeta is not None:
                    if (zeta_values[2]-zeta_values[0]) > max_delta_zeta:
                        continue
                # Check if the dRs form a 2-point correlator (for W)
                if delta_legs is not None and shortest_side is not None:
                    if (zeta_values[2]-zeta_values[1]) > delta_legs and zeta_values[0] > shortest_side:
                        continue
                    
                weight = (constituents[i].pt() * constituents[j].pt() * constituents[k].pt())**n / ((scale**3)**n)
                triplets.append( (zeta_values[0], zeta_values[1], zeta_values[2], weight) )
                                
    return triplets

        
