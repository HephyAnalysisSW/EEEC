#!/usr/bin/env python
''' EEEC histograms 
'''
#
# Standard imports and batch mode
#
import ROOT
import os, sys
ROOT.gROOT.SetBatch(True)
import imp
import time
import numpy as np

#RootTools
from RootTools.core.standard             import *

# Fastjet
import fastjet

# Helpers
from EEEC.Tools.helpers import checkRootFile, deltaRGenparts
from EEEC.Tools.helpers import make_TH3D

# Energy Correlators
import EEEC.Tools.energyCorrelators as ec

# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',              action='store_true', help='Run only on a small subset of the data?')#, default = True)
argParser.add_argument('--input',              action='store',      help='input file')
argParser.add_argument('--overwrite',          action='store',      nargs='?', choices = ['none', 'all', 'target'], default = 'none', help='Overwrite?')#, default = True)
argParser.add_argument('--output',             action='store',      default='output')
argParser.add_argument('--jetR',               action='store',      default=1.5)

args = argParser.parse_args()

# Logging
import EEEC.Tools.logger as _logger
logger  = _logger.get_logger(args.logLevel, logFile = None)
import RootTools.core.logger as _logger_rt
logger_rt = _logger_rt.get_logger(args.logLevel, logFile = None )

akjet   = fastjet.JetDefinition(fastjet.antikt_algorithm, args.jetR, fastjet.E_scheme)
sample  = FWLiteSample( "output", args.input)

maxEvents = -1
if args.small: 
    args.output    += "_small"
    maxEvents       = 500 

# event content
products = {
    'gp':{'type':'vector<reco::GenParticle>', 'label':("genParticles")},
}

# FWLite reader if this is an EDM file
reader = sample.fwliteReader( products = products )


def make_pseudoJet( obj ):
    return fastjet.PseudoJet( obj.px(), obj.py(), obj.pz(), obj.energy() )

gRandom = ROOT.TRandom3()

counter = 0
reader.start()

Nbins = 150
min_zeta = 0
max_zeta = 2*args.jetR+0.2
binning = np.array([ np.linspace(min_zeta,max_zeta,Nbins+1) for i in range(3)], dtype='f')

h_mindR_top_jet = ROOT.TH1D("mindR_top_jet", "min[#Delta R(top, jet)]", 10, 0, 3)
h_mjet = ROOT.TH1F("m_jet", "m_{jet}", 30, 0, 300)
h_Nconstituents = ROOT.TH1D("Nconstituents", "Nconstituents", 20, 0, 200)

timediffs = []

first = True
while reader.run( ):

    t_start = time.time()

    if reader.position % 100==0: logger.info("At event %i/%i", reader.position, reader.nEvents)

    counter +=1
    if counter == maxEvents:  break

    # Find incoming particles and top quarks
    top = None
    antitop = None
    initial1 = None
    initial2 = None
    hard_scatter = [p for p in reader.products['gp'] if p.status() in [21,22] ] 
    for i, p in enumerate(hard_scatter):
        if p.pdgId() == 6:
            top = p 
        elif p.pdgId() == -6:
            antitop = p
        elif p.pdgId() == 11:
            initial1 = p
        elif p.pdgId() == -11:
            initial2 = p
        # print i, "pdgId = %i, status = %i" %(p.pdgId(), p.status())

    if top is None or antitop is None:
        print "Did not find 2 top quarks, skip this event..."
        continue

    if initial1 is None or initial2 is None:
        print "Did not find 2 incoming partons, skip this event..."
        continue
    
    # Get parton level/particle level/hadron level particles 
    
    #showered   = [p for p in reader.products['gp'] if abs(p.status())>=51 and abs(p.status())<80]
    particles = [p for p in reader.products['gp'] if p.numberOfDaughters()==0]

    clustSeq      = fastjet.ClusterSequence( map( make_pseudoJet, particles ), akjet )
    sortedJets    = fastjet.sorted_by_pt(clustSeq.inclusive_jets())

    # Find the jets that overlap with the tops
    jet_top         = None
    jet_antitop     = None
    dRmin_top       = args.jetR
    dRmin_antitop   = args.jetR
    
    for jet in sortedJets:
        if deltaRGenparts(jet, top) < dRmin_top:
            dRmin_top   = deltaRGenparts(jet, top)
            jet_top     = jet
        if deltaRGenparts(jet, antitop) < dRmin_antitop:
            dRmin_antitop = deltaRGenparts(jet, antitop)
            jet_antitop   = jet
    
    minpT = 300 # Set some minimal jet pT to ensure boosted tops that are within a single jet
    
    scale = (initial1.p4()+initial2.p4()).M()

    # top quark
    triplets_top = np.empty((0,3))
    weights_top  = np.empty((0))
    if jet_top is not None:
        if jet_top.pt() > minpT:
            # Get triplets
            triplets_top, weights_top = ec.getTriplets(scale, jet_top.constituents(), n=1, max_zeta=max_zeta, max_delta_zeta=None, delta_legs=None, shortest_side=None)
            # Fill jet hists
            h_mindR_top_jet.Fill(dRmin_top)
            h_mjet.Fill(jet_top.m())
            h_Nconstituents.Fill(len(jet_top.constituents()))

    # anti top quark
    triplets_antitop = np.empty((0,3)) 
    weights_antitop  = np.empty((0))
    if jet_antitop is not None:
        if jet_antitop.pt() > minpT:
            # Get triplets
            triplets_antitop, weights_antitop = ec.getTriplets(scale, jet_antitop.constituents(), n=1, max_zeta=max_zeta, max_delta_zeta=None, delta_legs=None, shortest_side=None)
            # Fill jet hists
            h_mindR_top_jet.Fill(dRmin_antitop)
            h_mjet.Fill(jet_antitop.m())
            h_Nconstituents.Fill(len(jet_antitop.constituents()))            

    if len(triplets_top)+len(triplets_antitop)>0:
        if first:
            h_correlator1, (xedges, yedges, zedges) = np.histogramdd( np.concatenate((triplets_top, triplets_antitop)), binning, weights=np.concatenate((weights_top, weights_antitop)))
            h_correlator2, (xedges, yedges, zedges) = np.histogramdd( np.concatenate((triplets_top, triplets_antitop)), binning, weights=np.concatenate((weights_top, weights_antitop))**2)
            first = False
        else:
            h_correlator1 += np.histogramdd( np.concatenate((triplets_top, triplets_antitop)), binning, weights=np.concatenate((weights_top, weights_antitop)))   [0]
            h_correlator2 += np.histogramdd( np.concatenate((triplets_top, triplets_antitop)), binning, weights=np.concatenate((weights_top, weights_antitop))**2)[0]
 
    timediffs.append(time.time() - t_start)

logger.info( "Done with running over %i events.", reader.nEvents )
logger.info( "Took %3.2f seconds per event (average)", sum(timediffs)/len(timediffs) )

th3d_h_correlator1 = make_TH3D((h_correlator1, (xedges, yedges, zedges)))
th3d_h_correlator1.SetName("EEEC1")
th3d_h_correlator1.SetTitle("EEEC1")
th3d_h_correlator2 = make_TH3D((h_correlator2, (xedges, yedges, zedges)))
th3d_h_correlator2.SetName("EEEC2")
th3d_h_correlator2.SetTitle("EEEC2")

output_filename =  args.output + '.root'
if os.path.exists( output_filename ) and checkRootFile( output_filename, checkForObjects=["Events"]) and args.overwrite =='none' :
    logger.info( "File %s found. Quit.", output_filename )
    sys.exit(0)

output_file = ROOT.TFile( output_filename, 'recreate')
output_file.cd()

output_file.cd()
th3d_h_correlator1.Write()
th3d_h_correlator2.Write()
h_mindR_top_jet.Write()
h_mjet.Write()
h_Nconstituents.Write()
output_file.Close()

logger.info( "Written output file %s", output_filename )
import pickle
pickle.dump(  (h_correlator1, h_correlator2, binning), file(output_filename.replace('.root', '.pkl'), 'w') )
