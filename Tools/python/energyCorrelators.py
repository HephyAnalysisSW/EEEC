from EEEC.Tools.helpers import deltaRGenparts
from ROOT import TLorentzVector
import numpy as np
import itertools

def getTriplets(scale, constituents, n=2, max_zeta=None, max_delta_zeta=None, delta_legs=None, shortest_side=None):

    # transform coordinates to np.array
    constituents         = np.array( [[c.E(), c.px(), c.py(), c.pz()]  for c in constituents])
    
    # keep track of indices
    E  = 0
    px = 1
    py = 2
    pz = 3
    
    # make triplet combinations
    triplet_combinations = np.array(list(itertools.combinations( range(len(constituents)), 3)))
    try:
        c = constituents[triplet_combinations]
    except IndexError:
        return np.empty((0,3)), np.empty((0)) 

    zeta_values = np.zeros( ( len(c), 3), dtype='f' )

    zeta_values[:,0] = (c[:,0,px]*c[:,1,px]+c[:,0,py]*c[:,1,py]+c[:,0,pz]*c[:,1,pz])/np.sqrt( (c[:,0,px]**2+c[:,0,py]**2+c[:,0,pz]**2)*(c[:,1,px]**2+c[:,1,py]**2+c[:,1,pz]**2) ) 
    zeta_values[:,1] = (c[:,0,px]*c[:,2,px]+c[:,0,py]*c[:,2,py]+c[:,0,pz]*c[:,2,pz])/np.sqrt( (c[:,0,px]**2+c[:,0,py]**2+c[:,0,pz]**2)*(c[:,2,px]**2+c[:,2,py]**2+c[:,2,pz]**2) ) 
    zeta_values[:,2] = (c[:,1,px]*c[:,2,px]+c[:,1,py]*c[:,2,py]+c[:,1,pz]*c[:,2,pz])/np.sqrt( (c[:,1,px]**2+c[:,1,py]**2+c[:,1,pz]**2)*(c[:,2,px]**2+c[:,2,py]**2+c[:,2,pz]**2) ) 
    zeta_values = (1-zeta_values)/2.

    zeta_values = np.sort( zeta_values, axis=1)

    # Check if smallest dR is small enough
    mask = np.ones( len(zeta_values), dtype=bool)
    if max_zeta is not None:
        mask &= (zeta_values[:,0]<=max_zeta)

    # Check if the dRs form an equilateral triangle (for top)
    if max_delta_zeta is not None:
        mask &= (zeta_values[:,2]-zeta_values[:,0]<=max_delta_zeta)

    # Check if the dRs form a 2-point correlator (for W)
    if delta_legs is not None and shortest_side is not None:
        mask &= (~( (zeta_values[:,2]-zeta_values[:,1] > delta_legs) & (zeta_values[:,0] > shortest_side)))

    zeta_values = zeta_values[mask]
    c           = c[mask]
    del mask

    # pT weight
    # weight = ( np.sqrt( (c[:,0,px]**2+c[:,0,py]**2)*(c[:,1,px]**2+c[:,1,py]**2)*(c[:,2,px]**2+c[:,2,py]**2)) / scale**3 )**n
    
    # energy weight 
    weight = ( c[:,0,E]*c[:,1,E]*c[:,2,E] / scale**3 )**n
    

    return zeta_values, weight

    
def getTriplets_pp(scale, constituents, n=2, max_zeta=None, max_delta_zeta=None, delta_legs=None, shortest_side=None):

    # transform coordinates to np.array
    constituents         = np.array( [[np.sqrt(c.px()*c.px()+c.py()*c.py()), c.eta(), c.phi(), c.m()]  for c in constituents])
    
    # keep track of indices
    pt   = 0
    eta  = 1
    phi  = 2
    mass = 3
    
    # make triplet combinations
    triplet_combinations = np.array(list(itertools.combinations( range(len(constituents)), 3)))
    try:
        c = constituents[triplet_combinations]
    except IndexError:
        return np.empty((0,3)), np.empty((0)) 

    # first create an array of the dPhi since this has to be adjusted to by inside [-pi, pi]
    dPhiValues = np.zeros( ( len(c), 3), dtype='f' )
    dPhiValues[:,0] = c[:,0,phi] - c[:,1,phi]
    dPhiValues[:,1] = c[:,0,phi] - c[:,2,phi]
    dPhiValues[:,2] = c[:,1,phi] - c[:,2,phi]
    
    dPhiValues[dPhiValues  >  np.pi] += -2*np.pi
    dPhiValues[dPhiValues <= -np.pi] += 2*np.pi
    
    zeta_values = np.zeros( ( len(c), 3), dtype='f' )
    zeta_values[:,0] = np.sqrt( (c[:,0,eta]-c[:,1,eta])*(c[:,0,eta]-c[:,1,eta]) + dPhiValues[:,0]*dPhiValues[:,0]) 
    zeta_values[:,1] = np.sqrt( (c[:,0,eta]-c[:,2,eta])*(c[:,0,eta]-c[:,2,eta]) + dPhiValues[:,1]*dPhiValues[:,1])
    zeta_values[:,2] = np.sqrt( (c[:,1,eta]-c[:,2,eta])*(c[:,1,eta]-c[:,2,eta]) + dPhiValues[:,2]*dPhiValues[:,2])

    zeta_values = np.sort( zeta_values, axis=1)

    # Check if smallest dR is small enough
    mask = np.ones( len(zeta_values), dtype=bool)
    if max_zeta is not None:
        mask &= (zeta_values[:,0]<=max_zeta)

    # Check if the dRs form an equilateral triangle (for top)
    if max_delta_zeta is not None:
        mask &= (zeta_values[:,2]-zeta_values[:,0]<=max_delta_zeta)

    # Check if the dRs form a 2-point correlator (for W)
    if delta_legs is not None and shortest_side is not None:
        mask &= (~( (zeta_values[:,2]-zeta_values[:,1] > delta_legs) & (zeta_values[:,0] > shortest_side)))

    zeta_values = zeta_values[mask]
    c           = c[mask]
    del mask

    # pT weight
    weight = ( c[:,0,pt]*c[:,1,pt]*c[:,2,pt] / scale**3 )**n    
    
    # energy weight 
    # weight = ( c[:,0,E]*c[:,1,E]*c[:,2,E] / scale**3 )**n
    

    return zeta_values, weight




# def getZeta(p1, p2, pp = False):
#     if pp:
#         return p1.delta_R(p2)
#     else:
#         product = p1.px()*p2.px() + p1.py()*p2.py() + p1.pz()*p2.pz() 
#         mag1 = np.sqrt(p1.px()**2 + p1.py()**2 + p1.pz()**2)
#         mag2 = np.sqrt(p2.px()**2 + p2.py()**2 + p2.pz()**2)
#         costheta = product / (mag1*mag2)
#         return (1-costheta)/2

# def _getTriplets(scale, constituents, n=2, max_zeta=None, max_delta_zeta=None, delta_legs=None, shortest_side=None):
#     triplets = []
#     for i in range(len(constituents)):
#         for j in range(i+1, len(constituents)):
#             for k in range(j+1, len(constituents)):
# 
#                 zeta_values = [
#                     getZeta(constituents[i], constituents[j], pp = False),
#                     getZeta(constituents[i], constituents[k], pp = False),
#                     getZeta(constituents[j], constituents[k], pp = False),
#                     ]
#                 zeta_values.sort()
# 
# 
#                 # Check if smallest dR is small enough
#                 if max_zeta is not None:
#                     if zeta_values[0] > max_zeta:
#                         continue
#                 # Check if the dRs form an equilateral triangle (for top)
#                 if max_delta_zeta is not None:
#                     if (zeta_values[2]-zeta_values[0]) > max_delta_zeta:
#                         continue
#                 # Check if the dRs form a 2-point correlator (for W)
#                 if delta_legs is not None and shortest_side is not None:
#                     if (zeta_values[2]-zeta_values[1]) > delta_legs and zeta_values[0] > shortest_side:
#                         continue
# 
#                 weight = (constituents[i].pt() * constituents[j].pt() * constituents[k].pt())**n / ((scale**3)**n)
#                 triplets.append( (zeta_values[0], zeta_values[1], zeta_values[2], weight) )
# 
#     return triplets

        
