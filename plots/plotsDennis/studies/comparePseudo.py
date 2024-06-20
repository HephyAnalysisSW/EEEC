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

f_eeec_hllhc = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_HLLHC.root"
f_eeec_run2 = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_Run2.root"
f_eeec_run3 = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_Run3.root"
f_mjet = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/plots/plotsDennis/studies/Mjet_ptSpectrum.root"
plotdir = plot_directory+"/HLLHC_pseudo/"
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

# Combine pT bins
h_eeec_hllhc = ROOT.TH1F()
h_eeec_run2 = ROOT.TH1F()
h_eeec_run3 = ROOT.TH1F()
first = True
Nevents = {}
for ptbin in ptbins:
    fullname = histname+"_ptjet"+ptbin
    h_tmp_hllhc = getObjFromFile(f_eeec_hllhc, fullname)
    h_tmp_run2  = getObjFromFile(f_eeec_run2, fullname)
    h_tmp_run3  = getObjFromFile(f_eeec_run3, fullname)
    if first:
        first = False
        h_eeec_hllhc = h_tmp_hllhc.Clone()
        h_eeec_run2  = h_tmp_run2.Clone()
        h_eeec_run3  = h_tmp_run3.Clone()
    else:
        h_eeec_hllhc.Add(h_tmp_hllhc)
        h_eeec_run2.Add(h_tmp_run2)
        h_eeec_run3.Add(h_tmp_run3)

# Compare with mjet spectrum
h_mjet = getObjFromFile(f_mjet, "data_fine")
h_mjet_conv = convertMjetHist(h_mjet, h_eeec_hllhc)

h_mjet_run2 = h_mjet_conv.Clone("mjet_run2")
h_mjet_run3 = h_mjet_conv.Clone("mjet_run3")
h_mjet_hllhc = h_mjet_conv.Clone("mjet_hllhc")

h_mjet_run3.Scale(300./138.)
h_mjet_hllhc.Scale(3000./138.)

rebin = 10
p_hllhc = Plotter("HLLHC_projection")
p_hllhc.plot_dir = plotdir
p_hllhc.xtitle = "Jet p_{T} [GeV]"
p_hllhc.drawRatio = True
p_hllhc.rebin = rebin
p_hllhc.ratiotitle = "#frac{MJET}{EEEC}"
p_hllhc.addBackground(h_eeec_hllhc, "EEEC HL-LHC", 13)
p_hllhc.addSignal(h_mjet_hllhc, "m_{jet} measurement at 3000 fb^{-1}", ROOT.kRed)
p_hllhc.draw()

p_run2 = Plotter("Run2_projection")
p_run2.plot_dir = plotdir
p_run2.xtitle = "Jet p_{T} [GeV]"
p_run2.drawRatio = True
p_run2.rebin = rebin
p_run2.ratiotitle = "#frac{MJET}{EEEC}"
p_run2.addBackground(h_eeec_run2, "EEEC Run 2", 13)
p_run2.addSignal(h_mjet_run2, "m_{jet} measurement at 138 fb^{-1}", ROOT.kRed)
p_run2.draw()

p_run3 = Plotter("Run3_projection")
p_run3.plot_dir = plotdir
p_run3.xtitle = "Jet p_{T} [GeV]"
p_run3.drawRatio = True
p_run3.rebin = rebin
p_run3.ratiotitle = "#frac{MJET}{EEEC}"
p_run3.addBackground(h_eeec_run3, "EEEC Run 3", 13)
p_run3.addSignal(h_mjet_run3, "m_{jet} measurement at 300 fb^{-1}", ROOT.kRed)
p_run3.draw()
