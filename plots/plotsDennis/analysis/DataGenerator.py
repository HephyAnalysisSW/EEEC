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
argParser.add_argument('--plot_directory', action='store', default='DataGenerator_v1')
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
# Functions needed specifically for this analysis routine
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

def getChargedParticlesFromJet(event, jetidx, genrec):
    chargedIds = [211, 13, 11, 1, 321, 2212, 3222, 3112, 3312, 3334]
    particles = []
    if genrec == "gen":
        for iPart in range(event.nGenJetAK8_cons):
            if event.GenJetAK8_cons_jetIndex[iPart] != jetidx:
                continue
            if abs(event.GenJetAK8_cons_pdgId[iPart]) not in chargedIds:
                continue
            particle = ROOT.TLorentzVector()
            particle.SetPtEtaPhiM(event.GenJetAK8_cons_pt[iPart],event.GenJetAK8_cons_eta[iPart],event.GenJetAK8_cons_phi[iPart],event.GenJetAK8_cons_mass[iPart])
            charge = 1 if event.GenJetAK8_cons_pdgId[iPart]>0 else -1
            particles.append( (particle, charge) )
    elif genrec == "rec":
        for iPart in range(event.nPFJetAK8_cons):
            if event.PFJetAK8_cons_jetIndex[iPart] != jetidx:
                continue
            if abs(event.PFJetAK8_cons_pdgId[iPart]) not in chargedIds:
                continue
            particle = ROOT.TLorentzVector()
            particle.SetPtEtaPhiM(event.PFJetAK8_cons_pt[iPart],event.PFJetAK8_cons_eta[iPart],event.PFJetAK8_cons_phi[iPart],event.PFJetAK8_cons_mass[iPart])
            charge = 1 if event.PFJetAK8_cons_pdgId[iPart]>0 else -1
            particles.append( (particle, charge) )
    return particles

################################################################################
# Define sequences
sequence       = []


def getConstituents( event, sample ):
    passSel = False
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
                        passSel = True
                        genParts = getChargedParticlesFromJet(event, idx_genJet, "gen")
                        pfParts = getChargedParticlesFromJet(event, idx_pfJet, "rec")
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
                PtDiff = abs(genPart.Pt()-pfParts[idx][0].Pt())
                if PtDiff < minPtDiff:
                    minPtDiff = PtDiff
                    gmatchIDX = idx
        genMatches[i] = matchIDX
        alreadyMatched.append(matchIDX)

    genParts_matched = []
    pfParts_matched = []
    for i, (genPart, genCharge) in enumerate(genParts):
        if genMatches[i] is not None:
            genParts_matched.append(genParts[i][0])
            pfParts_matched.append(pfParts[genMatches[i]][0])

    event.nGenAll = len(genParts) if len(genParts) > 0 else float('nan')
    event.nGenMatched = len(genParts_matched) if len(genParts) > 0 else float('nan')
    event.matchingEffi = float(len(genParts_matched))/float(len(genParts)) if len(genParts) > 0 else float('nan')
    event.passSel = passSel

    event.genParts_matched = genParts_matched


    # event.zeta_gen = np.zeros( ( len([]), 3), dtype='f' )
    # event.weight_gen = np.zeros( ( len([]), 1), dtype='f' )
    # event.zeta_rec = np.zeros( ( len([]), 3), dtype='f' )
    # event.weight_rec = np.zeros( ( len([]), 1), dtype='f' )
    # if len(genParts_matched) > 0:
    #     _, event.zeta_gen, _, _, event.weight_gen = getTriplets_pp_TLorentz(scale_gen, genParts_matched, n=1, max_zeta=None, max_delta_zeta=None, delta_legs=None, shortest_side=None, log=False)
    #     _, event.zeta_rec, _, _, event.weight_rec = getTriplets_pp_TLorentz(scale_pf, pfParts_matched, n=1, max_zeta=None, max_delta_zeta=None, delta_legs=None, shortest_side=None, log=False)

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
# Histograms
histograms = {
    "pt_gen": ROOT.TH1F("pt_gen", "pt_gen", 100, 0, 0.04),
}


################################################################################
# Detector smear function
def applyDetector(p_gen):
    p_rec = ROOT.TLorentzVector()
    p_rec.SetPtEtaPhiM(p_gen.Pt(), p_gen.Eta(), p_gen.Phi(), p_gen.M())
    return p_rec
# Data function
def getData(p_gen):
    p_rec = ROOT.TLorentzVector()
    p_rec.SetPtEtaPhiM(p_gen.Pt(), p_gen.Eta(), p_gen.Phi(), p_gen.M())
    p_rec *= 1.1
    return p_rec

outdir = "/groups/hephy/cms/dennis.schwarz/www/EEEC/DataGenerator/"
NeventsMax = 10000
for sample in mc:
    hist = histograms.copy()
    r = sample.treeReader( variables = read_variables, sequence = sequence, selectionString = cutInterpreter.cutString(args.selection))
    r.start()
    counter = 0
    genParticles = np.empty(NeventsMax, dtype=object)
    recParticles = np.empty(NeventsMax, dtype=object)
    genParticles_data = np.empty(NeventsMax, dtype=object)
    recParticles_data = np.empty(NeventsMax, dtype=object)
    while r.run():
        event = r.event
        if event.passSel and event.nGenMatched > 0:
            genParts = event.genParts_matched
            genPerEvent = np.empty(len(genParts), dtype=object)
            recPerEvent = np.empty(len(genParts), dtype=object)
            genPerEvent_data = np.empty(len(genParts), dtype=object)
            recPerEvent_data = np.empty(len(genParts), dtype=object)
            for i,p in enumerate(genParts):
                p_array = np.array([p.Px(), p.Py(), p.Pz(), p.M()])
                genPerEvent[i] = p_array
                # generate data
                p_data = getData(p)
                p_data_array = np.array([p_data.Px(), p_data.Py(), p_data.Pz(), p_data.M()])
                genPerEvent_data[i] = p_data_array
                # simulate detector
                p_rec = applyDetector(p)
                p_rec_array = np.array([p_rec.Px(), p_rec.Py(), p_rec.Pz(), p_rec.M()])
                recPerEvent[i] = p_rec_array
                # simulate detector for data
                p_data_rec = applyDetector(p_data)
                p_data_rec_array = np.array([p_data_rec.Px(), p_data_rec.Py(), p_data_rec.Pz(), p_data_rec.M()])
                recPerEvent_data[i] = p_data_rec_array


            genParticles[counter] = genPerEvent
            recParticles[counter] = recPerEvent
            genParticles_data[counter] = genPerEvent_data
            recParticles_data[counter] = recPerEvent_data
            counter += 1

        if counter >= NeventsMax:
            break

    np.savez(outdir+'GenParticles_SIM.npz',      array1=genParticles)
    np.savez(outdir+'GenParticles_DAT.npz', array1=genParticles_data)
    np.savez(outdir+'RecParticles_SIM.npz',      array1=recParticles)
    np.savez(outdir+'RecParticles_DAT.npz', array1=recParticles_data)
    print "Saved np arrays in", outdir

    logger.info( "Done with sample "+sample.name+" and selectionString "+cutInterpreter.cutString(args.selection) )
