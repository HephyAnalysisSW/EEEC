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
from EEEC.Tools.helpers import make_TH3D, make_TH2D, make_TH1D

# Track efficiency
from EEEC.Tools.trackEfficiency import applyEfficiency

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
argParser.add_argument('--isHERWIG',           action='store_true', default = False)
argParser.add_argument('--doTwoPoint',         action='store_true', default = False)
argParser.add_argument('--applyEfficiency',    action='store_true', default = False)
argParser.add_argument('--effiMode',           action='store',      default="realistic")
argParser.add_argument('--lastTop',            action='store_true', default = False)

args = argParser.parse_args()

# Logging
import EEEC.Tools.logger as _logger
logger  = _logger.get_logger(args.logLevel, logFile = None)
import RootTools.core.logger as _logger_rt
logger_rt = _logger_rt.get_logger(args.logLevel, logFile = None )

logger.info("Starting genPostProcessing_pp.py")

logger.info("Jet algorithm: %s", args.jetAlgorithm)
logger.info("Jet R = %s", args.jetR)
if args.applyEfficiency:
    logger.info("Modelling track efficiency with model %s", args.effiMode)

if args.lastTop:
    logger.info("Use last top before decay for matching")


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
    pseudojet = fastjet.PseudoJet( obj.px(), obj.py(), obj.pz(), obj.energy() )
    # print obj.charge(), obj.threeCharge(), obj.pdgId()
    if obj.charge() == 0 and obj.threeCharge() == 0:
        pseudojet.set_user_index(0)
    else:
        pseudojet.set_user_index(1)
    return pseudojet

def removeNeutrinos(particles):
    # Nbefore = len(particles)
    neutrino_IDs = [12, 14, 16]
    new_particles = [p for p in particles if abs(p.pdgId()) not in neutrino_IDs]
    # Nafter = len(new_particles)
    # print Nbefore, Nafter
    # if Nbefore != Nafter:
    #     print "!!!"
    return new_particles

countWnotfound = 0
countWfound = 0

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

# New 3D histogram has the axes:
# X = (zeta_medium+zeta_large)/2 with 100 bins from 0 to 0.15 and 100 bins from 0.15 to 0.6
# Y = zeta_large-zeta_medium with 20 bins between 0 and 0.2 and one overflow
# Z = zeta_short with 90 bins between 0 and 0.45 + divide first bin into 50 bins

binsX_A = np.linspace(0, 0.2, 200+1)
binsX_B = np.linspace(0.2, 0.8, 120+1)
binsX_B = np.delete(binsX_B, 0) # remove first number because it is already part of "binsA"
binningX = np.append(binsX_A, binsX_B)

binsY_A = np.linspace(0, 0.2, 20+1)
binsY_B = np.linspace(0.2, 0.65, 1+1) # one overflow
binsY_B = np.delete(binsY_B, 0) # remove first number because it is already part of "binsA"
binningY = np.append(binsY_A, binsY_B)

binsZ_A = np.linspace(0, 0.005, 50+1)
binsZ_B = np.linspace(0.005, 0.45, 89+1)
binsZ_B = np.delete(binsZ_B, 0) # remove first number because it is already part of "binsA"
binningZ = np.append(binsZ_A, binsZ_B)

# print "-------------------------------"
# print "Binning X:"
# print binningX
# print "-------------------------------"
# print "Binning Y:"
# print binningY
# print "-------------------------------"
# print "Binning Z:"
# print binningZ


binning_new =  [binningX, binningY, binningZ]

binning500 = [binningX, binningX, binningX]
binning600 = [binningX, binningX, binningX]

binning500_twoPoint = [binningX]
binning600_twoPoint = [binningX]

binning_long_medium = [binningX]

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
_Nconstituents_charged = ROOT.TH1D("Nconstituents_charged", "Nconstituents_charged", 20, 0, 200)

ptbins = {}
ptbins["400to425"] = (400, 425, binning500, binning500_twoPoint, binning_long_medium)
ptbins["425to450"] = (425, 450, binning500, binning500_twoPoint, binning_long_medium)
ptbins["450to475"] = (450, 475, binning500, binning500_twoPoint, binning_long_medium)
ptbins["475to500"] = (475, 500, binning500, binning500_twoPoint, binning_long_medium)
ptbins["500to525"] = (500, 525, binning500, binning500_twoPoint, binning_long_medium)
ptbins["525to550"] = (525, 550, binning500, binning500_twoPoint, binning_long_medium)
ptbins["550to575"] = (550, 575, binning500, binning500_twoPoint, binning_long_medium)
ptbins["575to600"] = (575, 600, binning500, binning500_twoPoint, binning_long_medium)
ptbins["600to650"] = (600, 650, binning600, binning600_twoPoint, binning_long_medium)
ptbins["650to700"] = (650, 700, binning600, binning600_twoPoint, binning_long_medium)
ptbins["700to750"] = (700, 750, binning600, binning600_twoPoint, binning_long_medium)
ptbins["750to800"] = (750, 800, binning600, binning600_twoPoint, binning_long_medium)

h_mindR_top_jet = {}
h_mjet = {}
h_ptjet = {}
h_pttop = {}
h_ptW = {}
h_Nconstituents = {}
h_Nconstituents_charged = {}
h_correlator1 = {}
h_correlator2 = {}
h_correlator1_charged = {}
h_correlator2_charged = {}
h_correlator1_long = {}
h_correlator2_long = {}
h_correlator1_long_charged = {}
h_correlator2_long_charged = {}
h_correlator1_medium = {}
h_correlator2_medium = {}
h_correlator1_medium_charged = {}
h_correlator2_medium_charged = {}
h_correlator1_twoPoint = {}
h_correlator2_twoPoint = {}
h_correlator1_twoPoint_charged = {}
h_correlator2_twoPoint_charged = {}
h_correlator1_twoPointModified = {}
h_correlator2_twoPointModified = {}
h_correlator1_twoPointModified_charged = {}
h_correlator2_twoPointModified_charged = {}
sawEvents = {}

for bin in ptbins:
    h_mindR_top_jet[bin] = _mindR_top_jet.Clone(_mindR_top_jet.GetName()+"_ptjet"+bin)
    h_mjet[bin] = _mjet.Clone(_mjet.GetName()+"_ptjet"+bin)
    h_ptjet[bin] = _ptjet.Clone(_ptjet.GetName()+"_ptjet"+bin)
    h_pttop[bin] = _pttop.Clone(_pttop.GetName()+"_ptjet"+bin)
    h_ptW[bin] = _ptW.Clone(_ptW.GetName()+"_ptjet"+bin)
    h_Nconstituents[bin] = _Nconstituents.Clone(_Nconstituents.GetName()+"_ptjet"+bin)
    h_Nconstituents_charged[bin] = _Nconstituents_charged.Clone(_Nconstituents_charged.GetName()+"_ptjet"+bin)
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

    # Find incoming particles and top quarks
    top = None
    antitop = None
    bottom = None
    antibottom = None
    wplus = None
    wminus = None
    initial1 = None
    initial2 = None
    hard_scatter = []
    if args.isHERWIG:
        hard_scatter = [p for p in reader.products['gp'] if p.status() in [11] and abs(p.pdgId()) in [1, 2, 3, 4, 5, 6, 24] ]
    else:
        hard_scatter = [p for p in reader.products['gp'] if p.status() in [21,22,23] ]
    foundTop = False
    foundATop = False
    foundBottom = False
    foundABottom = False
    foundWplus = False
    foundWminus = False
    # print "---------------------------"
    for i, p in enumerate(hard_scatter):
        # print i, "pdgId = %i, status = %i, pt = %.3f" %(p.pdgId(), p.status(), p.pt())
        if p.pdgId() == 6 and not foundTop:
            # print "found top:", i, "pdgId = %i, status = %i, pt = %.3f" %(p.pdgId(), p.status(), p.pt())
            top = p
            foundTop = True
            # print "   - this is top"
        elif p.pdgId() == -6 and not foundATop:
            antitop = p
            foundATop = True
            # print "   - this is antitop"
        elif p.pdgId() == 24 and not foundWplus:
            wplus = p
            foundWplus = True
            # print "   - this is Wplus"
        elif p.pdgId() == -24 and not foundWminus:
            wminus = p
            foundWminus = True
            # print "   - this is Wminus"
        elif p.pdgId() == 5 and not foundBottom:
            bottom = p
            foundBottom = True
        elif p.pdgId() == -5 and not foundABottom:
            antibottom = p
            foundABottom = True

    if args.lastTop:
        # print "------------------------------------------------"
        tops = [p for p in reader.products['gp'] if abs(p.pdgId()) in [6] ]
        for i,p in enumerate(tops):
            if p.pdgId() == 6:
                top = p
            elif p.pdgId() == -6:
                antitop = p

    # print top.pt(), antitop.pt()
    if top is None or antitop is None:
        logger.info("Did not find 2 top quarks, skip this event...")
        continue

    if wplus is None or wminus is None:
        logger.info("Did not find 2 W bosons, skip this event...")
        countWnotfound += 1
        continue
    else:
        countWfound += 1

    if args.applyEfficiency and args.effiMode in ["Bfrag", "BfragScale"]:
        if bottom is None or antibottom is None:
            logger.info("Did not find 2 bottom quarks")
            continue


    # Get parton level/particle level/hadron level particles

    #showered   = [p for p in reader.products['gp'] if abs(p.status())>=51 and abs(p.status())<80]
    particles = [p for p in reader.products['gp'] if p.numberOfDaughters()==0]


    # Nall = len(particles)
    # Ncharged = 0
    # Nphotons = 0
    # Nneutral = 0
    # print "--------------------------------------------------------------------"
    # for p in particles:
    #     print p.pdgId()
    #     if p.charge() == 0:
    #         if p.pdgId() == 22:
    #             Nphotons = Nphotons+1
    #         else:
    #             Nneutral = Nneutral+1
    #     else:
    #         Ncharged = Ncharged+1
    # print "Nall     = %i (%.2f)"%(Nall, float(Nall)/float(Nall))
    # print "Ncharged = %i (%.2f)"%(Ncharged, float(Ncharged)/float(Nall))
    # print "Nphotons = %i (%.2f)"%(Nphotons, float(Nphotons)/float(Nall))
    # print "Nneutral = %i (%.2f)"%(Nneutral, float(Nneutral)/float(Nall))


    if "HardProcess" in args.output:
        particles = hard_scatter_quarks
        if len(particles) != 6:
            logger.info("Did not find 6 quarks of hard process, skip this event...")

    particles = removeNeutrinos(particles)

    clustSeq      = fastjet.ClusterSequence( map( make_pseudoJet, particles ), jetDef )
    sortedJets    = fastjet.sorted_by_pt(clustSeq.inclusive_jets())

    # Find the jets that overlap with the tops
    # jet_top         = None
    # jet_antitop     = None
    # dRmin_top       = args.jetR
    # dRmin_antitop   = args.jetR
    #
    # for jet in sortedJets:
    #     if deltaRGenparts(jet, top) < dRmin_top:
    #         dRmin_top   = deltaRGenparts(jet, top)
    #         jet_top     = jet
    #     if deltaRGenparts(jet, antitop) < dRmin_antitop:
    #         dRmin_antitop = deltaRGenparts(jet, antitop)
    #         jet_antitop   = jet
    jet_top         = sortedJets[0]
    jet_antitop     = sortedJets[1]
    dRmin_top = deltaRGenparts(sortedJets[0], top)
    dRmin_antitop = deltaRGenparts(sortedJets[1], antitop)

    if deltaRGenparts(jet_antitop, top) > deltaRGenparts(jet_top, top):
        jet_top         = sortedJets[1]
        jet_antitop     = sortedJets[0]
        dRmin_top = deltaRGenparts(sortedJets[1], top)
        dRmin_antitop = deltaRGenparts(sortedJets[2], antitop)

    # if jet_top is not None and jet_antitop is not None and jet_antitop==jet_top: continue

    tops = [
        (top, jet_top, dRmin_top, wplus),
        (antitop, jet_antitop, dRmin_antitop, wminus),
    ]

    for (topParticle, topJet, dRmin, wParticle) in tops:
        if topJet is not None:
            if topJet.pt() > 400 and abs(topJet.eta()) < 4.0:
                constituents = list(topJet.constituents())
                constituents_charged = [c for c in constituents if c.user_index() == 1]
                # print "---------------"
                # print len(constituents), len(constituents_charged)
                if len(constituents) < 3 or len(constituents_charged) < 3:
                    continue
                scale = topJet.pt()


                # Apply efficiency model
                if args.applyEfficiency:
                    list_bfrag = None
                    list_bfrag_charged = None
                    if args.effiMode in ["Bfrag", "BfragScale"]:
                        list_bfrag = []
                        list_bfrag_charged = []
                        dR_bottom = 0.4
                        for i, p in enumerate(constituents):
                            if deltaRGenparts(bottom, p) < dR_bottom or deltaRGenparts(antibottom, p) < dR_bottom:
                                list_bfrag.append(i)
                        for i, p in enumerate(constituents_charged):
                            if deltaRGenparts(bottom, p) < dR_bottom or deltaRGenparts(antibottom, p) < dR_bottom:
                                list_bfrag_charged.append(i)
                    constituents = applyEfficiency(constituents, args.effiMode, list_bfrag)
                    constituents_charged = applyEfficiency(constituents_charged, args.effiMode, list_bfrag_charged)

                # Make Triplets
                triplets, transformed_triplets, long, medium, weights = ec.getTriplets_pp(scale, constituents, n=1, max_zeta=1.0, max_delta_zeta=None, delta_legs=None, shortest_side=None, log=args.log)
                triplets_charged, transformed_triplets_charged, long_charged, medium_charged, weights_charged = ec.getTriplets_pp(scale, constituents_charged, n=1, max_zeta=1.0, max_delta_zeta=None, delta_legs=None, shortest_side=None, log=args.log)

                if args.newHist:
                    values = transformed_triplets
                    values_charged = transformed_triplets_charged
                else:
                    values = triplets
                    values_charged = triplets_charged

                # Make douplets
                doublets, weights_doublets, weights_doublets_modified = ec.getDoublets_pp(scale, constituents, n=1)
                doublets_charged, weights_doublets_charged, weights_doublets_charged_modified = ec.getDoublets_pp(scale, constituents_charged, n=1)


                # Fill Hists
                for bin in ptbins:
                    minpt, maxpt, binning, binningTwoPoint, binning_long_medium = ptbins[bin]
                    if topJet.pt() > minpt and topJet.pt() < maxpt:
                        h_mindR_top_jet[bin].Fill(dRmin)
                        h_mjet[bin].Fill(topJet.m())
                        h_ptjet[bin].Fill(topJet.pt())
                        h_Nconstituents[bin].Fill(len(constituents))
                        h_Nconstituents_charged[bin].Fill(len(constituents_charged))
                        h_pttop[bin].Fill(topParticle.pt())
                        h_ptW[bin].Fill(wParticle.pt())
                        if not sawEvents[bin]:
                            # New hist
                            h_correlator1[bin],       (xedges, yedges, zedges) = np.histogramdd( values, binning, weights=weights )
                            h_correlator2[bin],       (xedges, yedges, zedges) = np.histogramdd( values, binning, weights=weights**2 )

                            h_correlator1_charged[bin],       (xedges, yedges, zedges) = np.histogramdd( values_charged, binning, weights=weights_charged )
                            h_correlator2_charged[bin],       (xedges, yedges, zedges) = np.histogramdd( values_charged, binning, weights=weights_charged**2 )

                            # zeta_long
                            h_correlator1_long[bin],       (xedges) = np.histogramdd( long, binning_long_medium, weights=weights )
                            h_correlator2_long[bin],       (xedges) = np.histogramdd( long, binning_long_medium, weights=weights**2 )

                            h_correlator1_long_charged[bin],       (xedges) = np.histogramdd( long_charged, binning_long_medium, weights=weights_charged )
                            h_correlator2_long_charged[bin],       (xedges) = np.histogramdd( long_charged, binning_long_medium, weights=weights_charged**2 )

                            # zeta_medium
                            h_correlator1_medium[bin],       (xedges) = np.histogramdd( medium, binning_long_medium, weights=weights )
                            h_correlator2_medium[bin],       (xedges) = np.histogramdd( medium, binning_long_medium, weights=weights**2 )

                            h_correlator1_medium_charged[bin],       (xedges) = np.histogramdd( medium_charged, binning_long_medium, weights=weights_charged )
                            h_correlator2_medium_charged[bin],       (xedges) = np.histogramdd( medium_charged, binning_long_medium, weights=weights_charged**2 )

                            # two point
                            h_correlator1_twoPoint[bin],       (xedges) = np.histogramdd( doublets, binningTwoPoint, weights=weights_doublets )
                            h_correlator2_twoPoint[bin],       (xedges) = np.histogramdd( doublets, binningTwoPoint, weights=weights_doublets**2 )

                            h_correlator1_twoPoint_charged[bin],       (xedges) = np.histogramdd( doublets_charged, binningTwoPoint, weights=weights_doublets_charged )
                            h_correlator2_twoPoint_charged[bin],       (xedges) = np.histogramdd( doublets_charged, binningTwoPoint, weights=weights_doublets_charged**2 )

                            # two point modified weight
                            h_correlator1_twoPointModified[bin],       (xedges) = np.histogramdd( doublets, binningTwoPoint, weights=weights_doublets_modified )
                            h_correlator2_twoPointModified[bin],       (xedges) = np.histogramdd( doublets, binningTwoPoint, weights=weights_doublets_modified**2 )

                            h_correlator1_twoPointModified_charged[bin],       (xedges) = np.histogramdd( doublets_charged, binningTwoPoint, weights=weights_doublets_charged_modified )
                            h_correlator2_twoPointModified_charged[bin],       (xedges) = np.histogramdd( doublets_charged, binningTwoPoint, weights=weights_doublets_charged_modified**2 )

                            sawEvents[bin] = True

                        else:
                            # New hist
                            h_correlator1[bin] += np.histogramdd( values, binning, weights=weights )   [0]
                            h_correlator2[bin] += np.histogramdd( values, binning, weights=weights**2 )[0]

                            h_correlator1_charged[bin] += np.histogramdd( values_charged, binning, weights=weights_charged )   [0]
                            h_correlator2_charged[bin] += np.histogramdd( values_charged, binning, weights=weights_charged**2 )[0]

                            # zeta_long
                            h_correlator1_long[bin] += np.histogramdd( long, binning_long_medium, weights=weights )   [0]
                            h_correlator2_long[bin] += np.histogramdd( long, binning_long_medium, weights=weights**2 )[0]

                            h_correlator1_long_charged[bin] += np.histogramdd( long_charged, binning_long_medium, weights=weights_charged )   [0]
                            h_correlator2_long_charged[bin] += np.histogramdd( long_charged, binning_long_medium, weights=weights_charged**2 )[0]

                            # zeta_medium
                            h_correlator1_medium[bin] += np.histogramdd( medium, binning_long_medium, weights=weights )   [0]
                            h_correlator2_medium[bin] += np.histogramdd( medium, binning_long_medium, weights=weights**2 )[0]

                            h_correlator1_medium_charged[bin] += np.histogramdd( medium_charged, binning_long_medium, weights=weights_charged )   [0]
                            h_correlator2_medium_charged[bin] += np.histogramdd( medium_charged, binning_long_medium, weights=weights_charged**2 )[0]

                            # two-point
                            h_correlator1_twoPoint[bin] += np.histogramdd( doublets, binningTwoPoint, weights=weights_doublets )   [0]
                            h_correlator2_twoPoint[bin] += np.histogramdd( doublets, binningTwoPoint, weights=weights_doublets**2 )[0]

                            h_correlator1_twoPoint_charged[bin] += np.histogramdd( doublets_charged, binningTwoPoint, weights=weights_doublets_charged )   [0]
                            h_correlator2_twoPoint_charged[bin] += np.histogramdd( doublets_charged, binningTwoPoint, weights=weights_doublets_charged**2 )[0]

                            # two point modified weight
                            h_correlator1_twoPointModified[bin] += np.histogramdd( doublets, binningTwoPoint, weights=weights_doublets_modified )   [0]
                            h_correlator2_twoPointModified[bin] += np.histogramdd( doublets, binningTwoPoint, weights=weights_doublets_modified**2 )[0]

                            h_correlator1_twoPointModified_charged[bin] += np.histogramdd( doublets_charged, binningTwoPoint, weights=weights_doublets_charged_modified )   [0]
                            h_correlator2_twoPointModified_charged[bin] += np.histogramdd( doublets_charged, binningTwoPoint, weights=weights_doublets_charged_modified**2 )[0]


    timediffs.append(time.time() - t_start)
    # End event loop

average = sum(timediffs)/len(timediffs) if len(timediffs) > 0 else 0
logger.info( "Done with running over %i events.", reader.nEvents )
logger.info( "Took %3.2f seconds per event (average)", average )

logger.info( "Found both Ws = %i", countWfound )
logger.info( "Not found both Ws = %i", countWnotfound )

th3d_h_correlator1 = {}
th3d_h_correlator1_charged = {}
th3d_h_correlator1_long = {}
th3d_h_correlator1_long_charged = {}
th3d_h_correlator1_medium = {}
th3d_h_correlator1_medium_charged = {}
th3d_h_correlator1_twoPoint = {}
th3d_h_correlator1_twoPoint_charged = {}
th3d_h_correlator1_twoPointModified = {}
th3d_h_correlator1_twoPointModified_charged = {}
for bin in ptbins:
    if sawEvents[bin]:
        minpt, maxpt, binning, binningTwoPoint, binningLM = ptbins[bin]
        dummy, (xedges, yedges, zedges) = np.histogramdd( [[0.1],[0.1],[0.1]], binning )
        dummy_twoPoint, (xedges_twoPoint) = np.histogramdd( [0.1], binningTwoPoint )
        dummyLM, (xedges_LM) = np.histogramdd( [0.1], binningLM )

        # New hist
        logger.info( "Converting EEEC1_jetpt"+bin+" to ROOT" )
        th3d_h_correlator1[bin] = make_TH3D(h_correlator1[bin], (xedges, yedges, zedges), sumw2=h_correlator2[bin])
        th3d_h_correlator1[bin].SetName("EEEC1_jetpt"+bin)
        th3d_h_correlator1[bin].SetTitle("EEEC1_jetpt"+bin)

        logger.info( "Converting EEEC1charged_jetpt"+bin+" to ROOT" )
        th3d_h_correlator1_charged[bin] = make_TH3D(h_correlator1_charged[bin], (xedges, yedges, zedges), sumw2=h_correlator2_charged[bin])
        th3d_h_correlator1_charged[bin].SetName("EEEC1charged_jetpt"+bin)
        th3d_h_correlator1_charged[bin].SetTitle("EEEC1charged_jetpt"+bin)

        # zeta_long
        logger.info( "Converting EEEC1Long_jetpt"+bin+" to ROOT" )
        th3d_h_correlator1_long[bin] = make_TH1D(h_correlator1_long[bin], (xedges_LM), sumw2=h_correlator2_long[bin])
        th3d_h_correlator1_long[bin].SetName("EEEC1Long_jetpt"+bin)
        th3d_h_correlator1_long[bin].SetTitle("EEEC1Long_jetpt"+bin)

        logger.info( "Converting EEEC1Longcharged_jetpt"+bin+" to ROOT" )
        th3d_h_correlator1_long_charged[bin] = make_TH1D(h_correlator1_long_charged[bin], (xedges_LM), sumw2=h_correlator2_long_charged[bin])
        th3d_h_correlator1_long_charged[bin].SetName("EEEC1Longcharged_jetpt"+bin)
        th3d_h_correlator1_long_charged[bin].SetTitle("EEEC1Longcharged_jetpt"+bin)

        # zeta_medium
        logger.info( "Converting EEEC1Medium_jetpt"+bin+" to ROOT" )
        th3d_h_correlator1_medium[bin] = make_TH1D(h_correlator1_medium[bin], (xedges_LM), sumw2=h_correlator2_medium[bin])
        th3d_h_correlator1_medium[bin].SetName("EEEC1Medium_jetpt"+bin)
        th3d_h_correlator1_medium[bin].SetTitle("EEEC1Medium_jetpt"+bin)

        logger.info( "Converting EEEC1Mediumcharged_jetpt"+bin+" to ROOT" )
        th3d_h_correlator1_medium_charged[bin] = make_TH1D(h_correlator1_medium_charged[bin], (xedges_LM), sumw2=h_correlator2_medium_charged[bin])
        th3d_h_correlator1_medium_charged[bin].SetName("EEEC1Mediumcharged_jetpt"+bin)
        th3d_h_correlator1_medium_charged[bin].SetTitle("EEEC1Mediumcharged_jetpt"+bin)

        # two point
        logger.info( "Converting EEC1_jetpt"+bin+" to ROOT" )
        th3d_h_correlator1_twoPoint[bin] = make_TH1D(h_correlator1_twoPoint[bin], xedges_twoPoint, sumw2=h_correlator2_twoPoint[bin])
        th3d_h_correlator1_twoPoint[bin].SetName("EEC1_jetpt"+bin)
        th3d_h_correlator1_twoPoint[bin].SetTitle("EEC1_jetpt"+bin)

        logger.info( "Converting EEC1charged_jetpt"+bin+" to ROOT" )
        th3d_h_correlator1_twoPoint_charged[bin] = make_TH1D(h_correlator1_twoPoint_charged[bin], xedges_twoPoint, sumw2=h_correlator2_twoPoint_charged[bin])
        th3d_h_correlator1_twoPoint_charged[bin].SetName("EEC1charged_jetpt"+bin)
        th3d_h_correlator1_twoPoint_charged[bin].SetTitle("EEC1charged_jetpt"+bin)

        # two point modified
        logger.info( "Converting EEC1Mod_jetpt"+bin+" to ROOT" )
        th3d_h_correlator1_twoPointModified[bin] = make_TH1D(h_correlator1_twoPointModified[bin], xedges_twoPoint, sumw2=h_correlator2_twoPointModified[bin])
        th3d_h_correlator1_twoPointModified[bin].SetName("EEC1Mod_jetpt"+bin)
        th3d_h_correlator1_twoPointModified[bin].SetTitle("EEC1Mod_jetpt"+bin)

        logger.info( "Converting EEC1Modcharged_jetpt"+bin+" to ROOT" )
        th3d_h_correlator1_twoPointModified_charged[bin] = make_TH1D(h_correlator1_twoPointModified_charged[bin], xedges_twoPoint, sumw2=h_correlator2_twoPointModified_charged[bin])
        th3d_h_correlator1_twoPointModified_charged[bin].SetName("EEC1Modcharged_jetpt"+bin)
        th3d_h_correlator1_twoPointModified_charged[bin].SetTitle("EEC1Modcharged_jetpt"+bin)

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
        th3d_h_correlator1_charged[bin].Write()
        th3d_h_correlator1_long[bin].Write()
        th3d_h_correlator1_long_charged[bin].Write()
        th3d_h_correlator1_medium[bin].Write()
        th3d_h_correlator1_medium_charged[bin].Write()
        th3d_h_correlator1_twoPoint[bin].Write()
        th3d_h_correlator1_twoPoint_charged[bin].Write()
        th3d_h_correlator1_twoPointModified[bin].Write()
        th3d_h_correlator1_twoPointModified_charged[bin].Write()
    h_mindR_top_jet[bin].Write()
    h_mjet[bin].Write()
    h_ptjet[bin].Write()
    h_pttop[bin].Write()
    h_ptW[bin].Write()
    h_Nconstituents[bin].Write()
    h_Nconstituents_charged[bin].Write()
output_file.Close()

logger.info( "Written output file %s", output_filename )
# import pickle
# pickle.dump(  (h_correlator1, h_correlator2, binning), file(output_filename.replace('.root', '.pkl'), 'w') )
