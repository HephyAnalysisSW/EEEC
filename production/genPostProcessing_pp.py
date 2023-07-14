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
argParser.add_argument('--jetR',               action='store',      type=float, default=1.0)
argParser.add_argument('--jetAlgorithm',       action='store',      default="AK")
argParser.add_argument('--log',                action='store_true', default = False)
argParser.add_argument('--newHist',            action='store_true', default = False)

args = argParser.parse_args()

# Logging
import EEEC.Tools.logger as _logger
logger  = _logger.get_logger(args.logLevel, logFile = None)
import RootTools.core.logger as _logger_rt
logger_rt = _logger_rt.get_logger(args.logLevel, logFile = None )

logger.info("Starting genPostProcessing_pp.py")

logger.info("Jet algorithm: %s", args.jetAlgorithm)
logger.info("Jet R = %s", args.jetR)


clusteringAlgorithm = fastjet.antikt_algorithm

if args.jetAlgorithm == "CA":
    clusteringAlgorithm = fastjet.cambridge_algorithm

jetDef  = fastjet.JetDefinition(clusteringAlgorithm, args.jetR, fastjet.E_scheme)
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

# Make binning finer for larger COM energy
binfactor = {
    "13000": 1.0,
}
comstring = args.output.split("_")[1]
if comstring not in binfactor.keys():
    logger.info( "No binning scheme defined for COM energy = %s. Quit.", comstring )
    sys.exit(0)


Nbins = 100
min_zeta = 0.0
max_zeta_500 = 0.15*(1000./500.)**2
max_zeta_600 = 0.15*(1000./600.)**2

if args.log:
    Nbins = 200
    min_zeta = -2.5
    max_zeta_500 = 0.0
    max_zeta_600 = 0.0

binning500 = np.array([ np.linspace(min_zeta, max_zeta_500, Nbins+1) for i in range(3)], dtype='d')
binning600 = np.array([ np.linspace(min_zeta, max_zeta_600, Nbins+1) for i in range(3)], dtype='d')

# New 3D histogram has the axes:
# X = (zeta_medium+zeta_large)/2 with 100 bins from 0 to 0.15 and 100 bins from 0.15 to 0.6
# Y = zeta_large-zeta_medium with 20 bins between 0 and 0.06
# Z = zeta_short with 90 bins between 0 and 0.45

binsX_A = np.linspace(0, 0.15, 100+1)
binsX_B = np.linspace(0.15, 0.6, 100+1)
binsX_B = np.delete(binsX_B, 0) # remove first number because it is already part of "binsA"
binningX = np.append(binsX_A, binsX_B)
binningY = np.linspace(0, 0.06, 20+1)
binningZ = np.linspace(0, 0.45, 90+1)

binning_new =  [binningX, binningY, binningZ]

if args.newHist:
    binning500 = binning_new
    binning600 = binning_new

_mindR_top_jet = ROOT.TH1D("mindR_top_jet", "min[#Delta R(top, jet)]", 10, 0, 3)
_mjet = ROOT.TH1F("mjet", "m_{jet}", 30, 0, 300)
_ptjet = ROOT.TH1F("pTjet", "Jet p_{T}", 600, 400, 1000)
_pttop = ROOT.TH1F("pTtop", "Top quark p_{T}", 200, 0, 1000)
_ptW = ROOT.TH1F("pTW", "W boson p_{T}", 200, 0, 1000)
_dPhi = ROOT.TH1F("dPhi", "#Delta #Phi (jet1, jet2)", 35, 0, 7.0)
_Nconstituents = ROOT.TH1D("Nconstituents", "Nconstituents", 20, 0, 200)

ptbins = {}
ptbins["500to525"] = (500, 525, binning500)
ptbins["525to550"] = (525, 550, binning500)
ptbins["550to575"] = (550, 575, binning500)
ptbins["575to600"] = (575, 600, binning500)
ptbins["600to625"] = (600, 625, binning600)
ptbins["625to650"] = (625, 650, binning600)
ptbins["650to675"] = (650, 675, binning600)
ptbins["675to700"] = (675, 700, binning600)

h_mindR_top_jet = {}
h_mjet = {}
h_ptjet = {}
h_pttop = {}
h_ptW = {}
h_Nconstituents = {}
h_correlator1 = {}
h_correlator2 = {}
sawEvents = {}

for bin in ptbins:
    h_mindR_top_jet[bin] = _mindR_top_jet.Clone(_mindR_top_jet.GetName()+"_ptjet"+bin)
    h_mjet[bin] = _mjet.Clone(_mjet.GetName()+"_ptjet"+bin)
    h_ptjet[bin] = _ptjet.Clone(_ptjet.GetName()+"_ptjet"+bin)
    h_pttop[bin] = _pttop.Clone(_pttop.GetName()+"_ptjet"+bin)
    h_ptW[bin] = _ptW.Clone(_ptW.GetName()+"_ptjet"+bin)
    h_Nconstituents[bin] = _Nconstituents.Clone(_Nconstituents.GetName()+"_ptjet"+bin)
    sawEvents[bin] = False

timediffs = []

first = True
while reader.run( ):

    t_start = time.time()

    if reader.position % 100==0: logger.info("At event %i/%i", reader.position, reader.nEvents)

    counter +=1
    if counter == maxEvents:  break

    hard_scatter_quarks = []
    for i, p in enumerate(reader.products['gp']):
        if p.status() in [22,23] and abs(p.pdgId()) != 6 and abs(p.pdgId()) != 24:
            hard_scatter_quarks.append(p)

    # print '------------------------------------'
    # for i,p in enumerate(hard_scatter_quarks):
    #         print i, p.pdgId(), p.status()

    # Find incoming particles and top quarks
    top = None
    antitop = None
    wplus = None
    wminus = None
    initial1 = None
    initial2 = None
    hard_scatter = [p for p in reader.products['gp'] if p.status() in [21,22] ]
    for i, p in enumerate(hard_scatter):
        if p.pdgId() == 6:
            top = p
        elif p.pdgId() == -6:
            antitop = p
        elif p.pdgId() == 24:
            wplus = p
        elif p.pdgId() == -24:
            wminus = p
        # print i, "pdgId = %i, status = %i" %(p.pdgId(), p.status())

    if top is None or antitop is None:
        logger.info("Did not find 2 top quarks, skip this event...")
        continue

    if wplus is None or wminus is None:
        logger.info("Did not find 2 W bosons, skip this event...")
        continue


    # Get parton level/particle level/hadron level particles

    #showered   = [p for p in reader.products['gp'] if abs(p.status())>=51 and abs(p.status())<80]
    particles = [p for p in reader.products['gp'] if p.numberOfDaughters()==0]

    if "HardProcess" in args.output:
        particles = hard_scatter_quarks
        if len(particles) != 6:
            logger.info("Did not find 6 quarks of hard process, skip this event...")

    clustSeq      = fastjet.ClusterSequence( map( make_pseudoJet, particles ), jetDef )
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

    if jet_top is not None and jet_antitop is not None and jet_antitop==jet_top: continue

    # top quark
    triplets_top = np.empty((0,3))
    weights_top  = np.empty((0))
    if jet_top is not None:
        if jet_top.pt() > 500 and abs(jet_top.eta()) < 4.0:
            # Get triplets
            if jet_top.constituents() < 3:
                continue
            scale = jet_top.pt()
            triplets_top, new_triplets_top, weights_top = ec.getTriplets_pp(scale, jet_top.constituents(), n=1, max_zeta=1.0, max_delta_zeta=None, delta_legs=None, shortest_side=None, log=args.log)
            # Fill jet hists
            for bin in ptbins:
                minpt, maxpt, binning = ptbins[bin]
                if jet_top.pt() > minpt and jet_top.pt() < maxpt:
                    h_mindR_top_jet[bin].Fill(dRmin_top)
                    h_mjet[bin].Fill(jet_top.m())
                    h_ptjet[bin].Fill(jet_top.pt())
                    h_Nconstituents[bin].Fill(len(jet_top.constituents()))
                    h_pttop[bin].Fill(top.pt())
                    h_ptW[bin].Fill(wplus.pt())
                    if args.newHist:
                        if not sawEvents[bin]:
                            h_correlator1[bin],       (xedges, yedges, zedges) = np.histogramdd( new_triplets_top, binning, weights=weights_top )
                            h_correlator2[bin],       (xedges, yedges, zedges) = np.histogramdd( new_triplets_top, binning, weights=weights_top**2 )
                            sawEvents[bin] = True
                        else:
                            h_correlator1[bin]       += np.histogramdd( new_triplets_top, binning, weights=weights_top )   [0]
                            h_correlator2[bin]       += np.histogramdd( new_triplets_top, binning, weights=weights_top**2 )[0]
                    else:
                        if not sawEvents[bin]:
                            h_correlator1[bin],       (xedges, yedges, zedges) = np.histogramdd( triplets_top, binning, weights=weights_top )
                            h_correlator2[bin],       (xedges, yedges, zedges) = np.histogramdd( triplets_top, binning, weights=weights_top**2 )
                            sawEvents[bin] = True
                        else:
                            h_correlator1[bin]       += np.histogramdd( triplets_top, binning, weights=weights_top )   [0]
                            h_correlator2[bin]       += np.histogramdd( triplets_top, binning, weights=weights_top**2 )[0]

    # anti top quark
    triplets_antitop = np.empty((0,3))
    weights_antitop  = np.empty((0))
    if jet_antitop is not None:
        if jet_antitop.pt() > 500 and abs(jet_antitop.eta()) < 4.0:
            # Get triplets
            if jet_antitop.constituents() < 3:
                continue
            scale = jet_antitop.pt()
            triplets_antitop, new_triplets_antitop, weights_antitop = ec.getTriplets_pp(scale, jet_antitop.constituents(), n=1, max_zeta=1.0, max_delta_zeta=None, delta_legs=None, shortest_side=None, log=args.log)
            # Fill jet hists
            for bin in ptbins:
                minpt, maxpt, binning = ptbins[bin]
                if jet_antitop.pt() > minpt and jet_antitop.pt() < maxpt:
                    h_mindR_top_jet[bin].Fill(dRmin_antitop)
                    h_mjet[bin].Fill(jet_antitop.m())
                    h_ptjet[bin].Fill(jet_antitop.pt())
                    h_Nconstituents[bin].Fill(len(jet_antitop.constituents()))
                    h_pttop[bin].Fill(antitop.pt())
                    h_ptW[bin].Fill(wminus.pt())
                    if args.newHist:
                        if not sawEvents[bin]:
                            h_correlator1[bin],       (xedges, yedges, zedges) = np.histogramdd( new_triplets_antitop, binning, weights=weights_antitop )
                            h_correlator2[bin],       (xedges, yedges, zedges) = np.histogramdd( new_triplets_antitop, binning, weights=weights_antitop**2 )
                            sawEvents[bin] = True
                        else:
                            h_correlator1[bin]       += np.histogramdd( new_triplets_antitop, binning, weights=weights_antitop )   [0]
                            h_correlator2[bin]       += np.histogramdd( new_triplets_antitop, binning, weights=weights_antitop**2 )[0]
                    else:
                        if not sawEvents[bin]:
                            h_correlator1[bin],       (xedges, yedges, zedges) = np.histogramdd( triplets_antitop, binning, weights=weights_antitop )
                            h_correlator2[bin],       (xedges, yedges, zedges) = np.histogramdd( triplets_antitop, binning, weights=weights_antitop**2 )
                            sawEvents[bin] = True
                        else:
                            h_correlator1[bin]       += np.histogramdd( triplets_antitop, binning, weights=weights_antitop )   [0]
                            h_correlator2[bin]       += np.histogramdd( triplets_antitop, binning, weights=weights_antitop**2 )[0]

    timediffs.append(time.time() - t_start)

logger.info( "Done with running over %i events.", reader.nEvents )
logger.info( "Took %3.2f seconds per event (average)", sum(timediffs)/len(timediffs) )

th3d_h_correlator1 = {}
th3d_h_correlator2 = {}
for bin in ptbins:
    if sawEvents[bin]:
        minpt, maxpt, binning = ptbins[bin]
        dummy, (xedges, yedges, zedges) = np.histogramdd( [[0.1],[0.1],[0.1]], binning )
        th3d_h_correlator1[bin] = make_TH3D(h_correlator1[bin], (xedges, yedges, zedges), sumw2=h_correlator2[bin])
        th3d_h_correlator1[bin].SetName("EEEC1_jetpt"+bin)
        th3d_h_correlator1[bin].SetTitle("EEEC1_jetpt"+bin)
        th3d_h_correlator2[bin] = make_TH3D(h_correlator2[bin], (xedges, yedges, zedges), sumw2=None)
        th3d_h_correlator2[bin].SetName("EEEC2_jetpt"+bin)
        th3d_h_correlator2[bin].SetTitle("EEEC2_jetpt"+bin)

output_filename =  args.output + '.root'
if os.path.exists( output_filename ) and checkRootFile( output_filename, checkForObjects=["Events"]) and args.overwrite =='none' :
    logger.info( "File %s found. Quit.", output_filename )
    sys.exit(0)

output_file = ROOT.TFile( output_filename, 'recreate')
output_file.cd()

output_file.cd()
for bin in ptbins:
    if sawEvents[bin]:
        th3d_h_correlator1[bin].Write()
        th3d_h_correlator2[bin].Write()
    h_mindR_top_jet[bin].Write()
    h_mjet[bin].Write()
    h_ptjet[bin].Write()
    h_pttop[bin].Write()
    h_ptW[bin].Write()
    h_Nconstituents[bin].Write()
output_file.Close()

logger.info( "Written output file %s", output_filename )
# import pickle
# pickle.dump(  (h_correlator1, h_correlator2, binning), file(output_filename.replace('.root', '.pkl'), 'w') )
