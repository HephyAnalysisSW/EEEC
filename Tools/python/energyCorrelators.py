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


def getTriplets_pp(scale, constituents, n=2, max_zeta=None, max_delta_zeta=None, delta_legs=None, shortest_side=None, log=False):
    # in pp, zeta = (Delta R)^2 and weight = (pT1*pT2+pT3 / pTjet^3)^n


    # transform coordinates to np.array
    constituents         = np.array( [[np.sqrt(c.px()*c.px()+c.py()*c.py()), c.eta(), c.phi(), c.m()]  for c in constituents])

    # keep track of indices
    pt   = 0
    eta  = 1
    phi  = 2
    mass = 3

    # make triplet combinations
    if log:
        # if we make a log plot, we cannot have dR=0, so we use the variant without repeting elements
        triplet_combinations = np.array(list(itertools.combinations( range(len(constituents)), 3))) # this gives all combinations WITHOUT repeating particles
    else:
        triplet_combinations = np.array(list(itertools.combinations_with_replacement( range(len(constituents)), 3))) # this gives all combinations WITH repeating particles
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
    zeta_values[:,0] = (c[:,0,eta]-c[:,1,eta])*(c[:,0,eta]-c[:,1,eta]) + dPhiValues[:,0]*dPhiValues[:,0]
    zeta_values[:,1] = (c[:,0,eta]-c[:,2,eta])*(c[:,0,eta]-c[:,2,eta]) + dPhiValues[:,1]*dPhiValues[:,1]
    zeta_values[:,2] = (c[:,1,eta]-c[:,2,eta])*(c[:,1,eta]-c[:,2,eta]) + dPhiValues[:,2]*dPhiValues[:,2]

    zeta_values = np.sort( zeta_values, axis=1)

    if log:
        zeta_values = np.log10( np.sqrt(zeta_values) ) # this returns log(dR) instead of dR^2


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

    # Also create a transformed version:
    # X = (zeta_medium+zeta_large)/2
    # Y = zeta_large-zeta_medium
    # Z = zeta_short
    # 1. Make an array with same dimensions and fill it with zeros
    # 2. Transform into new values
    transformed_values = np.full_like(zeta_values, 0)

    if log:
        transformed_values[:,0] = ( pow(10, zeta_values[:,0])+pow(10, zeta_values[:,1]) )/2
        transformed_values[:,1] = pow(10, zeta_values[:,0]) - pow(10, zeta_values[:,1])
        transformed_values[:,2] = pow(10, zeta_values[:,2])
    else:
        transformed_values[:,0] = (zeta_values[:,0]+zeta_values[:,1])/2
        transformed_values[:,1] = zeta_values[:,0]-zeta_values[:,1]
        transformed_values[:,2] = zeta_values[:,2]

    return zeta_values, transformed_values, weight

def getTriplets_pp_pteta(scale, constituents, n=2, max_zeta=None, max_delta_zeta=None, delta_legs=None, shortest_side=None, log=False):
    # in pp, zeta = (Delta R)^2 and weight = (pT1*pT2+pT3 / pTjet^3)^n


    # transform coordinates to np.array
    constituents         = np.array( [[np.sqrt(c.px()*c.px()+c.py()*c.py()), c.eta(), c.phi(), c.m()]  for c in constituents])

    # keep track of indices
    pt   = 0
    eta  = 1
    phi  = 2
    mass = 3

    # make triplet combinations
    if log:
        # if we make a log plot, we cannot have dR=0, so we use the variant without repeting elements
        triplet_combinations = np.array(list(itertools.combinations( range(len(constituents)), 3))) # this gives all combinations WITHOUT repeating particles
    else:
        triplet_combinations = np.array(list(itertools.combinations_with_replacement( range(len(constituents)), 3))) # this gives all combinations WITH repeating particles
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
    zeta_values[:,0] = (c[:,0,eta]-c[:,1,eta])*(c[:,0,eta]-c[:,1,eta]) + dPhiValues[:,0]*dPhiValues[:,0]
    zeta_values[:,1] = (c[:,0,eta]-c[:,2,eta])*(c[:,0,eta]-c[:,2,eta]) + dPhiValues[:,1]*dPhiValues[:,1]
    zeta_values[:,2] = (c[:,1,eta]-c[:,2,eta])*(c[:,1,eta]-c[:,2,eta]) + dPhiValues[:,2]*dPhiValues[:,2]

    if log:
        zeta_values = np.log10( np.sqrt(zeta_values) ) # this returns log(dR) instead of dR^2

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

    return zeta_values, weight, c[:,0,pt], c[:,1,pt], c[:,2,pt], c[:,0,eta], c[:,1,eta], c[:,2,eta]
