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
argParser.add_argument('--jetR',               action='store',      default=1.0)
argParser.add_argument('--jetAlgorithm',       action='store',      default="CA")
argParser.add_argument('--log',                action='store_true', default = False)

args = argParser.parse_args()

# Logging
import EEEC.Tools.logger as _logger
logger  = _logger.get_logger(args.logLevel, logFile = None)
import RootTools.core.logger as _logger_rt
logger_rt = _logger_rt.get_logger(args.logLevel, logFile = None )

logger.info("Starting genPostProcessing_pp.py")

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


_mindR_top_jet = ROOT.TH1D("mindR_top_jet", "min[#Delta R(top, jet)]", 10, 0, 3)
_mjet = ROOT.TH1F("mjet", "m_{jet}", 30, 0, 300)
_ptjet = ROOT.TH1F("pTjet", "Jet p_{T}", 600, 400, 1000)
_pttop = ROOT.TH1F("pTtop", "Top quark p_{T}", 200, 0, 1000)
_ptW = ROOT.TH1F("pTW", "W boson p_{T}", 200, 0, 1000)
_dPhi = ROOT.TH1F("dPhi", "#Delta #Phi (jet1, jet2)", 35, 0, 7.0)
_Nconstituents = ROOT.TH1D("Nconstituents", "Nconstituents", 20, 0, 200)
_ptetaconstituents_unweighted = ROOT.TH2D("ptetaconstituents_unweighted", "ptetaconstituents_unweighted", 40, 0, 200, 50, -2.5, 2.5)
_ptetaconstituents_all = ROOT.TH2D("ptetaconstituents_all", "ptetaconstituents_all", 40, 0, 200, 50, -2.5, 2.5)
_ptetaconstituents_W = ROOT.TH2D("ptetaconstituents_W", "ptetaconstituents_W", 40, 0, 200, 50, -2.5, 2.5)
_ptetaconstituents_top = ROOT.TH2D("ptetaconstituents_top", "ptetaconstituents_top", 40, 0, 200, 50, -2.5, 2.5)
_correlator_all = ROOT.TH1D("correlator_all", "correlator_all", 120, 0, 0.6)
_correlator_top = ROOT.TH1D("correlator_top", "correlator_top", 120, 0, 0.6)
_correlator_W = ROOT.TH1D("correlator_W", "correlator_W", 120, 0, 0.6)

ptbins = {}
ptbins["500to525"] = (500, 525)
ptbins["525to550"] = (525, 550)
ptbins["550to575"] = (550, 575)
ptbins["575to600"] = (575, 600)
ptbins["600to625"] = (600, 625)
ptbins["625to650"] = (625, 650)
ptbins["650to675"] = (650, 675)
ptbins["675to700"] = (675, 700)

h_mindR_top_jet = {}
h_mjet = {}
h_ptjet = {}
h_pttop = {}
h_ptW = {}
h_Nconstituents = {}
h_ptetaconstituents_top = {}
h_ptetaconstituents_all = {}
h_ptetaconstituents_W = {}
h_ptetaconstituents_unweighted = {}
h_correlator_all = {}
h_correlator_W = {}
h_correlator_top = {}


for bin in ptbins:
    h_mindR_top_jet[bin] = _mindR_top_jet.Clone(_mindR_top_jet.GetName()+"_ptjet"+bin)
    h_mjet[bin] = _mjet.Clone(_mjet.GetName()+"_ptjet"+bin)
    h_ptjet[bin] = _ptjet.Clone(_ptjet.GetName()+"_ptjet"+bin)
    h_pttop[bin] = _pttop.Clone(_pttop.GetName()+"_ptjet"+bin)
    h_ptW[bin] = _ptW.Clone(_ptW.GetName()+"_ptjet"+bin)
    h_Nconstituents[bin] = _Nconstituents.Clone(_Nconstituents.GetName()+"_ptjet"+bin)
    h_ptetaconstituents_unweighted[bin] = _ptetaconstituents_unweighted.Clone(_ptetaconstituents_unweighted.GetName()+"_ptjet"+bin)
    h_ptetaconstituents_top[bin] = _ptetaconstituents_all.Clone(_ptetaconstituents_all.GetName()+"_ptjet"+bin)
    h_ptetaconstituents_all[bin] = _ptetaconstituents_top.Clone(_ptetaconstituents_top.GetName()+"_ptjet"+bin)
    h_ptetaconstituents_W[bin] = _ptetaconstituents_W.Clone(_ptetaconstituents_W.GetName()+"_ptjet"+bin)
    h_correlator_all[bin] = _correlator_all.Clone(_correlator_all.GetName()+"_ptjet"+bin)
    h_correlator_top[bin] = _correlator_top.Clone(_correlator_top.GetName()+"_ptjet"+bin)
    h_correlator_W[bin] = _correlator_W.Clone(_correlator_W.GetName()+"_ptjet"+bin)
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
            triplets_top, weights_top, pts1, pts2, pts3, etas1, etas2, etas3 = ec.getTriplets_pp_pteta(scale, jet_top.constituents(), n=1, max_zeta=1.0, max_delta_zeta=None, delta_legs=None, shortest_side=None, log=args.log)
            # Fill jet hists
            for bin in ptbins:
                minpt, maxpt = ptbins[bin]
                if jet_top.pt() > minpt and jet_top.pt() < maxpt:
                    h_mindR_top_jet[bin].Fill(dRmin_top)
                    h_mjet[bin].Fill(jet_top.m())
                    h_ptjet[bin].Fill(jet_top.pt())
                    h_Nconstituents[bin].Fill(len(jet_top.constituents()))
                    h_pttop[bin].Fill(top.pt())
                    h_ptW[bin].Fill(wplus.pt())
                    for c in jet_top.constituents():
                        h_ptetaconstituents_unweighted[bin].Fill(c.pt(), c.eta())

                    for i, weight in enumerate(weights_top):
                        zeta_small = triplets_top[i][0]
                        zeta_medium = triplets_top[i][1]
                        zeta_large = triplets_top[i][2]
                        if zeta_small > 0.01 and abs(zeta_large-zeta_medium)<0.003:
                            h_ptetaconstituents_all[bin].Fill(pts1[i], etas1[i], weight)
                            h_ptetaconstituents_all[bin].Fill(pts2[i], etas2[i], weight)
                            h_ptetaconstituents_all[bin].Fill(pts3[i], etas3[i], weight)
                            h_correlator_all[bin].Fill( (zeta_large+zeta_medium)/2, weight)
                            if (zeta_large+zeta_medium)/2 > 0.075 and (zeta_large+zeta_medium)/2 < 0.14:
                                h_ptetaconstituents_W[bin].Fill(pts1[i], etas1[i], weight)
                                h_ptetaconstituents_W[bin].Fill(pts2[i], etas2[i], weight)
                                h_ptetaconstituents_W[bin].Fill(pts3[i], etas3[i], weight)
                                h_correlator_W[bin].Fill( (zeta_large+zeta_medium)/2, weight)

                            elif (zeta_large+zeta_medium)/2 > 0.375 and (zeta_large+zeta_medium)/2 < 0.425:
                                h_ptetaconstituents_top[bin].Fill(pts1[i], etas1[i], weight)
                                h_ptetaconstituents_top[bin].Fill(pts2[i], etas2[i], weight)
                                h_ptetaconstituents_top[bin].Fill(pts3[i], etas3[i], weight)
                                h_correlator_top[bin].Fill( (zeta_large+zeta_medium)/2, weight)

    # anti top quark
    triplets_antitop = np.empty((0,3))
    weights_antitop  = np.empty((0))
    if jet_antitop is not None:
        if jet_antitop.pt() > 500 and abs(jet_antitop.eta()) < 4.0:
            # Get triplets
            if jet_antitop.constituents() < 3:
                continue
            scale = jet_antitop.pt()
            triplets_antitop, weights_antitop, pts1, pts2, pts3, etas1, etas2, etas3 = ec.getTriplets_pp_pteta(scale, jet_antitop.constituents(), n=1, max_zeta=1.0, max_delta_zeta=None, delta_legs=None, shortest_side=None, log=args.log)
            # Fill jet hists
            for bin in ptbins:
                minpt, maxpt = ptbins[bin]
                if jet_antitop.pt() > minpt and jet_antitop.pt() < maxpt:
                    h_mindR_top_jet[bin].Fill(dRmin_antitop)
                    h_mjet[bin].Fill(jet_antitop.m())
                    h_ptjet[bin].Fill(jet_antitop.pt())
                    h_Nconstituents[bin].Fill(len(jet_antitop.constituents()))
                    h_pttop[bin].Fill(antitop.pt())
                    h_ptW[bin].Fill(wminus.pt())
                    for c in jet_antitop.constituents():
                        h_ptetaconstituents_unweighted[bin].Fill(c.pt(), c.eta())

                    for i, weight in enumerate(weights_antitop):
                        zeta_small = triplets_antitop[i][0]
                        zeta_medium = triplets_antitop[i][1]
                        zeta_large = triplets_antitop[i][2]
                        if zeta_small > 0.01 and abs(zeta_large-zeta_medium)<0.003:
                            h_ptetaconstituents_all[bin].Fill(pts1[i], etas1[i], weight)
                            h_ptetaconstituents_all[bin].Fill(pts2[i], etas2[i], weight)
                            h_ptetaconstituents_all[bin].Fill(pts3[i], etas3[i], weight)
                            h_correlator_all[bin].Fill( (zeta_large+zeta_medium)/2, weight)
                            if (zeta_large+zeta_medium)/2 > 0.075 and (zeta_large+zeta_medium)/2 < 0.14:
                                h_ptetaconstituents_W[bin].Fill(pts1[i], etas1[i], weight)
                                h_ptetaconstituents_W[bin].Fill(pts2[i], etas2[i], weight)
                                h_ptetaconstituents_W[bin].Fill(pts3[i], etas3[i], weight)
                                h_correlator_W[bin].Fill( (zeta_large+zeta_medium)/2, weight)

                            elif (zeta_large+zeta_medium)/2 > 0.375 and (zeta_large+zeta_medium)/2 < 0.425:
                                h_ptetaconstituents_top[bin].Fill(pts1[i], etas1[i], weight)
                                h_ptetaconstituents_top[bin].Fill(pts2[i], etas2[i], weight)
                                h_ptetaconstituents_top[bin].Fill(pts3[i], etas3[i], weight)
                                h_correlator_top[bin].Fill( (zeta_large+zeta_medium)/2, weight)

    timediffs.append(time.time() - t_start)

logger.info( "Done with running over %i events.", reader.nEvents )
logger.info( "Took %3.2f seconds per event (average)", sum(timediffs)/len(timediffs) )

output_filename =  args.output + '.root'
if os.path.exists( output_filename ) and checkRootFile( output_filename, checkForObjects=["Events"]) and args.overwrite =='none' :
    logger.info( "File %s found. Quit.", output_filename )
    sys.exit(0)

output_file = ROOT.TFile( output_filename, 'recreate')
output_file.cd()

output_file.cd()
for bin in ptbins:
    h_mindR_top_jet[bin].Write()
    h_mjet[bin].Write()
    h_ptjet[bin].Write()
    h_pttop[bin].Write()
    h_ptW[bin].Write()
    h_Nconstituents[bin].Write()
    h_ptetaconstituents_all[bin].Write()
    h_ptetaconstituents_W[bin].Write()
    h_ptetaconstituents_top[bin].Write()
    h_ptetaconstituents_unweighted[bin].Write()
    h_correlator_all[bin].Write()
    h_correlator_W[bin].Write()
    h_correlator_top[bin].Write()

output_file.Close()

logger.info( "Written output file %s", output_filename )
# import pickle
# pickle.dump(  (h_correlator1, h_correlator2, binning), file(output_filename.replace('.root', '.pkl'), 'w') )
