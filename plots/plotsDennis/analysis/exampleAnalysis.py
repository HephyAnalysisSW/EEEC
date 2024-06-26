#!/usr/bin/env python
''' Analysis script for standard plots
'''
#
# Standard imports and batch mode
#
import ROOT, os
ROOT.gROOT.SetBatch(True)
c1 = ROOT.TCanvas() # do this to avoid version conflict in png.h with keras import ...
c1.Draw()
c1.Print('delete.png')
import itertools
import copy
import array
import operator
from math                                import sqrt, cos, sin, pi, atan2, cosh, exp

# RootTools
from RootTools.core.standard             import *

# EEEC
from EEEC.Tools.user                      import plot_directory
from EEEC.Tools.cutInterpreter            import cutInterpreter
from EEEC.Tools.objectSelection           import cbEleIdFlagGetter, vidNestedWPBitMapNamingList
from EEEC.Tools.objectSelection           import lepString
from EEEC.Tools.helpers                   import getCollection
from EEEC.Tools.energyCorrelators         import getTriplets_pp_TLorentz

# Analysis
from Analysis.Tools.helpers              import deltaPhi, deltaR
from Analysis.Tools.puProfileCache       import *
from Analysis.Tools.puReweighting        import getReweightingFunction
from Analysis.Tools.leptonJetArbitration     import cleanJetsAndLeptons

import Analysis.Tools.syncer
import numpy as np

################################################################################
# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--plot_directory', action='store', default='EEEC_v1')
argParser.add_argument('--selection',      action='store', default='nAK82p-AK8pt')
argParser.add_argument('--era',            action='store', type=str, default="UL2018")
args = argParser.parse_args()

################################################################################
# Logger
import EEEC.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

################################################################################
# Define the MC samples
# from EEEC.samples.nanoTuples_UL_RunII_nanoAOD import *
from EEEC.samples.nanoTuples_UL_RunII_nanoAOD_onesample import *

mc = [UL2018.TTbar]
# mc = [UL2018.TTbar_3]

lumi_scale = 60

################################################################################
# Correlator Hist
# hist = ROOT.TH1F("Correlator", "dR", 10, 0, 3)

################################################################################
# Text on the plots
tex = ROOT.TLatex()
tex.SetNDC()
tex.SetTextSize(0.04)
tex.SetTextAlign(11) # align right

################################################################################
# Functions needed specifically for this analysis routine

def drawObjects( plotData, lumi_scale ):
    lines = [
      (0.15, 0.95, 'CMS Preliminary' if plotData else 'CMS Simulation'),
      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) '% ( lumi_scale ) ) if plotData else (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    ]
    return [tex.DrawLatex(*l) for l in lines]

def drawPlots(plots):
    for log in [False, True]:
        plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.era, args.selection, ("log" if log else "lin"), )
        for plot in plots:
            if not max(l.GetMaximum() for l in sum(plot.histos,[])): continue # Empty plot

            _drawObjects = []
            n_stacks=len(plot.histos)
            plotData=False
            if isinstance( plot, Plot):
                plotting.draw(plot,
                  plot_directory = plot_directory_,
                  ratio =  None,
                  logX = False, logY = log, sorting = True,
                  yRange = (0.03, "auto") if log else (0.001, "auto"),
                  scaling = {},
                  legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
                  drawObjects = drawObjects( plotData , lumi_scale ) + _drawObjects,
                  copyIndexPHP = True, extensions = ["png", "pdf", "root"],
                )


def getHadronicTop(event):
    # First find the two tops
    foundTop = False
    foundATop = False
    for i in range(event.nGenPart):
        if foundTop and foundATop:
            break
        if event.GenPart_pdgId[i] == 6:
            top = ROOT.TLorentzVector()
            top.SetPtEtaPhiM(event.GenPart_pt[i],event.GenPart_eta[i],event.GenPart_phi[i],event.GenPart_m[i])
            foundTop = True
        elif event.GenPart_pdgId[i] == -6:
            atop = ROOT.TLorentzVector()
            atop.SetPtEtaPhiM(event.GenPart_pt[i],event.GenPart_eta[i],event.GenPart_phi[i],event.GenPart_m[i])
            foundATop = True
    # Now search for leptons
    # if grandmother is the top, the atop is hadronice and vice versa
    for i in range(event.nGenPart):
        if abs(event.GenPart_pdgId[i]) in [11, 13, 15]:
            if event.GenPart_grmompdgId[i] == 6:
                return atop
            elif event.GenPart_grmompdgId[i] == -6:
                return top
    return None

def getClosestJetIdx(object, event, maxDR, genpf_switch):
    Njets = event.nGenJetAK8 if genpf_switch == "gen" else event.nPFJetAK8
    minDR = maxDR
    idx_match = None
    for i in range(Njets):
        jet = ROOT.TLorentzVector()
        if genpf_switch == "gen":
            jet.SetPtEtaPhiM(event.GenJetAK8_pt[i],event.GenJetAK8_eta[i],event.GenJetAK8_phi[i],event.GenJetAK8_mass[i])
        else:
            jet.SetPtEtaPhiM(event.PFJetAK8_pt[i],event.PFJetAK8_eta[i],event.PFJetAK8_phi[i],event.PFJetAK8_mass[i])
        if jet.DeltaR(object) < minDR:
            idx_match = i
            minDR = jet.DeltaR(object)
    return idx_match




################################################################################
# Define sequences
sequence       = []


def getConstituents( event, sample ):
    genParts = []
    pfParts = []
    hadTop = getHadronicTop(event)
    scale_gen = None
    scale_rec = None
    if hadTop is not None:
        idx_genJet = getClosestJetIdx(hadTop, event, 0.8, "gen")
        if idx_genJet is not None:
            genJet = ROOT.TLorentzVector()
            genJet.SetPtEtaPhiM(event.GenJetAK8_pt[idx_genJet],event.GenJetAK8_eta[idx_genJet],event.GenJetAK8_phi[idx_genJet],event.GenJetAK8_mass[idx_genJet])
            if genJet.Pt() > 400:
                scale_gen = genJet.Pt()
                idx_pfJet = getClosestJetIdx(genJet, event, 0.8, "pf")
                if idx_pfJet is not None:
                    pfJet = ROOT.TLorentzVector()
                    pfJet.SetPtEtaPhiM(event.PFJetAK8_pt[idx_pfJet],event.PFJetAK8_eta[idx_pfJet],event.PFJetAK8_phi[idx_pfJet],event.PFJetAK8_mass[idx_pfJet])
                    if pfJet.Pt() > 400:
                        scale_pf = pfJet.Pt()
                        for iGen in range(event.nGenJetAK8_cons):
                            if event.GenJetAK8_cons_jetIndex[iGen] != idx_genJet:
                                continue
                            if abs(event.GenJetAK8_cons_pdgId[iGen]) not in [211, 13, 11, 1, 321, 2212, 3222, 3112, 3312, 3334]:
                                continue
                            genPart = ROOT.TLorentzVector()
                            genPart.SetPtEtaPhiM(event.GenJetAK8_cons_pt[iGen],event.GenJetAK8_cons_eta[iGen],event.GenJetAK8_cons_phi[iGen],event.GenJetAK8_cons_mass[iGen])
                            genPartCharge = 1 if event.GenJetAK8_cons_pdgId[iGen]>0 else -1
                            genParts.append( (genPart, genPartCharge) )
                        for iRec in range(event.nPFJetAK8_cons):
                            if event.PFJetAK8_cons_jetIndex[iRec] != idx_pfJet:
                                continue
                            if abs(event.PFJetAK8_cons_pdgId[iRec]) not in [211, 13, 11, 1, 321, 2212, 3222, 3112, 3312, 3334]:
                                continue
                            pfPart = ROOT.TLorentzVector()
                            pfPart.SetPtEtaPhiM(event.PFJetAK8_cons_pt[iRec],event.PFJetAK8_cons_eta[iRec],event.PFJetAK8_cons_phi[iRec],event.PFJetAK8_cons_mass[iRec])
                            pfPartCharge = 1 if event.PFJetAK8_cons_pdgId[iRec]>0 else -1
                            pfParts.append( (pfPart, pfPartCharge) )
    event.nGenParts = len(genParts)
    event.nPFParts = len(pfParts)
    maxDR_part = 0.05
    genMatches = {}
    alreadyMatched = []
    for i, (genPart, genCharge) in enumerate(genParts):
        matches = []
        for j, (pfPart, pfCharge) in enumerate(pfParts):
            if j in alreadyMatched:
                continue
            if genCharge == pfCharge and genPart.DeltaR(pfPart) < maxDR_part:
                matches.append(j)
        matchIDX = None
        if len(matches) == 0:
            matchIDX = None
        elif len(matches) == 1:
            matchIDX = matches[0]
        else:
            minPtDiff = 1000
            for idx in matches:
                PtDiff = abs(genPart.Pt() - pfParts[idx][0].Pt())
                if PtDiff < minPtDiff:
                    minPtDiff = PtDiff
                    gmatchIDX = idx
        genMatches[i] = matchIDX
        alreadyMatched.append(matchIDX)

    Nall = 0
    Nmatched = 0
    genParts_matched = []
    pfParts_matched = []
    for i, (genPart, genCharge) in enumerate(genParts):
        if genMatches[i] is not None:
            genParts_matched.append(genParts[i][0])
            pfParts_matched.append(pfParts[genMatches[i]][0])

    event.nGenAll = len(genParts) if len(genParts) > 0 else float('nan')
    event.nGenMatched = len(genParts_matched) if len(genParts) > 0 else float('nan')
    event.matchingEffi = float(len(genParts_matched))/float(len(genParts)) if Nall > 0 else float('nan')

    if len(genParts_matched) > 0:
        zeta_gen, transformed_values_gen, long_gen, medium_gen, weight_gen = getTriplets_pp_TLorentz(scale_gen, genParts_matched, n=2, max_zeta=None, max_delta_zeta=None, delta_legs=None, shortest_side=None, log=False)
        zeta_pf,  transformed_values_pf,  long_pf,  medium_pf,  weight_pf  = getTriplets_pp_TLorentz(scale_pf, pfParts_matched, n=2, max_zeta=None, max_delta_zeta=None, delta_legs=None, shortest_side=None, log=False)






sequence.append( getConstituents )


################################################################################
# Read variables

read_variables = [
    "nGenPart/I",
    "GenPart[pt/F,eta/F,phi/F,m/F,pdgId/I,mompdgId/I,grmompdgId/I]",
    "nGenJetAK8/I",
    "GenJetAK8[pt/F,eta/F,phi/F,mass/F]",
    "nGenJetAK8_cons/I",
    VectorTreeVariable.fromString( "GenJetAK8_cons[pt/F,eta/F,phi/F,mass/F,pdgId/I,jetIndex/I]", nMax=1000),
    "nPFJetAK8/I",
    "PFJetAK8[pt/F,eta/F,phi/F,mass/F]",
    "nPFJetAK8_cons/I",
    VectorTreeVariable.fromString( "PFJetAK8_cons[pt/F,eta/F,phi/F,mass/F,pdgId/I,jetIndex/I]", nMax=1000),

]

################################################################################
# Set up plotting
# weight_ = lambda event, sample: event.weight if sample.isData else event.weight*lumi_scale/1000.
# weight_ = lambda event, sample: 1. if sample.isData else lumi_scale/1000.
weight_ = lambda event, sample: 1.

for sample in mc:
    sample.style = styles.fillStyle(sample.color)

for sample in mc:
    sample.weight = lambda event, sample: 1.

stack = Stack(mc)

# Use some defaults
Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection))

################################################################################
# Now define the plots

plots = []

plots.append(Plot(
    name = "nAK8",
    texX = 'Number of AK8 jets', texY = 'Number of Events',
    attribute = lambda event, sample: event.nPFJetAK8,
    binning=[11, -0.5, 10.5],
))

plots.append(Plot(
    name = "nGen",
    texX = 'Number of gen constituents', texY = 'Number of Events',
    attribute = lambda event, sample: event.nGenParts,
    binning=[61, -0.5, 60.5],
))

plots.append(Plot(
    name = "nRec",
    texX = 'Number of PF constituents', texY = 'Number of Events',
    attribute = lambda event, sample: event.nPFParts,
    binning=[61, -0.5, 60.5],
))

plots.append(Plot(
    name = "nGenAll",
    texX = 'Number of gen constituents after selection', texY = 'Number of Events',
    attribute = lambda event, sample: event.nGenAll,
    binning=[61, -0.5, 60.5],
))

plots.append(Plot(
    name = "nGenMatched",
    texX = 'Number of matched gen constituents after selection', texY = 'Number of Events',
    attribute = lambda event, sample: event.nGenMatched,
    binning=[61, -0.5, 60.5],
))

plots.append(Plot(
    name = "MatchnigEfficiency",
    texX = 'Matching efficiency', texY = 'Number of Events',
    attribute = lambda event, sample: event.matchingEffi,
    binning=[20, 0.0, 1.0],
))


plotting.fill(plots, read_variables = read_variables, sequence = sequence)

drawPlots(plots)


logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )
