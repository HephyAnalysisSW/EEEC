#!/usr/bin/env python

import os
import ROOT
import array as arr
from math                                         import sqrt
from EEEC.Tools.helpers                           import getObjFromFile
from EEEC.Tools.user                              import plot_directory
from MyRootTools.plotter.Plotter                  import Plotter
import Analysis.Tools.syncer

ROOT.gROOT.SetBatch(ROOT.kTRUE)

def convertMjetHist(h_mjet, h_eeec):
    newhist = h_eeec.Clone()
    newhist.Reset()
    for i in range(h_eeec.GetXaxis().GetNbins()):
        bin = i+1
        bin_mjet = bin+100
        content_mjet = h_mjet.GetBinContent(bin_mjet)
        newhist.SetBinContent(bin, content_mjet)
    return newhist

f1 = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/EEEC_PP_13000_1725_804_HARDPT150to1000_MPIon_HADon_R12_NEWHISTv2.root"
f2 = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2.root"
f3 = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/EEEC_PP_13000_1725_804_HARDPT250to1000_MPIon_HADon_R12_NEWHISTv2.root"
f4 = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/EEEC_PP_13000_1725_804_HARDPT300to900_MPIon_HADon_R12_NEWHISTv2.root"
f_mjet = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/plots/plotsDennis/studies/Mjet_ptSpectrum.root"
plotdir = plot_directory+"/PTspectrum/"
if not os.path.exists( plotdir ): os.makedirs( plotdir )

histname = "pTjet"
ptbins = [
    "400to425",
    "425to450",
    "450to475",
    "475to500",
    "500to525",
    "525to550",
    "550to575",
    "575to600",
    "600to650",
    "650to700",
    "700to750",
    "750to800",
]




h1_all = ROOT.TH1F()
h2_all = ROOT.TH1F()
h3_all = ROOT.TH1F()
h4_all = ROOT.TH1F()

first = True

rebin = 10
Nevents = {}
for ptbin in ptbins:
    p = Plotter(histname+"_ptjet"+ptbin)
    p.plot_dir = plotdir
    p.xtitle = "Jet p_{T} [GeV]"
    p.xtitle = "Jet p_{T} [GeV]"
    p.drawRatio = True
    p.rebin = rebin
    fullname = histname+"_ptjet"+ptbin
    h1 = getObjFromFile(f1, fullname)
    h2 = getObjFromFile(f2, fullname)
    h3 = getObjFromFile(f3, fullname)
    h4 = getObjFromFile(f4, fullname)
    p.addBackground(h4, "300 < hard p_{T} < 900", 13)
    p.addSignal(h1, "150 < hard p_{T} < 1000", ROOT.kRed)
    p.addSignal(h2, "200 < hard p_{T} < 1000", ROOT.kBlue)
    p.addSignal(h3, "250 < hard p_{T} < 1000", ROOT.kGreen)
    p.draw()
    Nevents[ptbin] = h2.Integral()
    if first:
        first = False
        h1_all = h1.Clone()
        h2_all = h2.Clone()
        h3_all = h3.Clone()
        h4_all = h4.Clone()
    else:
        h1_all.Add(h1)
        h2_all.Add(h2)
        h3_all.Add(h3)
        h4_all.Add(h4)

    p_norm = Plotter(histname+"_ptjet"+ptbin+"_NORM")
    p_norm.plot_dir = plotdir
    p_norm.xtitle = "Jet p_{T} [GeV]"
    p_norm.drawRatio = True
    p_norm.rebin = rebin
    h1_norm = h1.Clone()
    h2_norm = h2.Clone()
    h3_norm = h3.Clone()
    h4_norm = h4.Clone()
    h1_norm.Scale(1/h1.Integral())
    h2_norm.Scale(1/h2.Integral())
    h3_norm.Scale(1/h3.Integral())
    h4_norm.Scale(1/h4.Integral())
    p_norm.addBackground(h4_norm, "300 < hard p_{T} < 900", 13)
    p_norm.addSignal(h1_norm, "150 < hard p_{T} < 1000", ROOT.kRed)
    p_norm.addSignal(h2_norm, "200 < hard p_{T} < 1000", ROOT.kBlue)
    p_norm.addSignal(h3_norm, "250 < hard p_{T} < 1000", ROOT.kGreen)
    p_norm.draw()

p = Plotter(histname+"_inclusive")
p.plot_dir = plotdir
p.xtitle = "Jet p_{T} [GeV]"
p.drawRatio = True
p.rebin = rebin
p.addBackground(h4_all, "300 < hard p_{T} < 900", 13)
p.addSignal(h1_all, "150 < hard p_{T} < 1000", ROOT.kRed)
p.addSignal(h2_all, "200 < hard p_{T} < 1000", ROOT.kBlue)
p.addSignal(h3_all, "250 < hard p_{T} < 1000", ROOT.kGreen)
p.draw()

p_norm = Plotter(histname+"_inclusive_NORM")
p_norm.plot_dir = plotdir
p_norm.xtitle = "Jet p_{T} [GeV]"
p_norm.drawRatio = True
p_norm.rebin = rebin
h1_all_norm = h1_all.Clone()
h2_all_norm = h2_all.Clone()
h3_all_norm = h3_all.Clone()
h4_all_norm = h4_all.Clone()
h1_all_norm.Scale(1/h1_all.Integral())
h2_all_norm.Scale(1/h2_all.Integral())
h3_all_norm.Scale(1/h3_all.Integral())
h4_all_norm.Scale(1/h4_all.Integral())
p_norm.addBackground(h4_all_norm, "300 < hard p_{T} < 900", 13)
p_norm.addSignal(h1_all_norm, "150 < hard p_{T} < 1000", ROOT.kRed)
p_norm.addSignal(h2_all_norm, "200 < hard p_{T} < 1000", ROOT.kBlue)
p_norm.addSignal(h3_all_norm, "250 < hard p_{T} < 1000", ROOT.kGreen)
p_norm.draw()


Ntops_mjet = [
    (["400to425"], 10380),
    (["425to450"], 8469),
    (["450to475"], 6585),
    (["475to500"], 5089),
    (["500to525", "525to550", "550to575", "575to600"], 12132),
    (["600to650", "650to700"], 5115),
    (["700to750", "750to800"], 2295),
    (["400to425","425to450","450to475","475to500","500to525","525to550","550to575","575to600","600to650","650to700","700to750","750to800"], 50065),
]

for (ptbins_mjet, Ntops_mjet) in Ntops_mjet:
    Ntops_EEEC = 0
    for ptbin in ptbins:
        if ptbin in ptbins_mjet:
            Ntops_EEEC += Nevents[ptbin]
    print "------------------------------"
    print ptbins_mjet
    print "EEEC =", Ntops_EEEC
    print "MJET =", Ntops_mjet
    print "SF (Run 2)    =", Ntops_mjet/Ntops_EEEC
    print "SF (HL-LHC)   =", 22*Ntops_mjet/Ntops_EEEC


h_mjet = getObjFromFile(f_mjet, "data_fine")
h_mjet_conv = convertMjetHist(h_mjet, h2_all)
h_mjet_conv.Scale(22)
h_eeec_scale = h2_all.Clone()
h_eeec_scale.Scale(2.7)

p_hllhc = Plotter(histname+"_inclusive_HLLHC")
p_hllhc.plot_dir = plotdir
p_hllhc.xtitle = "Jet p_{T} [GeV]"
p_hllhc.drawRatio = True
p_hllhc.rebin = rebin
p_hllhc.addBackground(h_eeec_scale, "EEEC scaled", 13)
p_hllhc.addSignal(h_mjet_conv, "m_{jet} measurement * 22", ROOT.kRed)
p_hllhc.draw()
