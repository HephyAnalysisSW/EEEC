#!/usr/bin/env python

import os
import ROOT
import array as arr
import numpy as np
from math                                         import sqrt, exp
from EEEC.Tools.helpers                           import getObjFromFile
from EEEC.Tools.user                              import plot_directory

from MyRootTools.plotter.Plotter                  import Plotter
import Analysis.Tools.syncer

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetOptStat(0)

plotdir = plot_directory+"/LastTop/"
if not os.path.exists( plotdir ): os.makedirs( plotdir )

dir = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/"

filename = "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_RADIUS_NEWHISTv2_1D.root"

radii = ["R10", "R12", "R15"]

hists = [
    "EEEC1top",
    "EEEC1avg",
    "EEC1",
    "pTjet",
]

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

for radius in radii:
    f_lasttop = dir+filename.replace("RADIUS", radius).replace("NEWHISTv2", "LASTTOP_NEWHISTv2")
    f_firsttop = dir+filename.replace("RADIUS", radius)
    for histname in hists:
        for ptbin in ptbins:
            hname = histname+"_ptjet"+ptbin if histname == "pTjet" else histname+"_jetpt"+ptbin
            h_lasttop = getObjFromFile(f_lasttop, hname)
            h_firsttop = getObjFromFile(f_firsttop, hname)
            if histname == "EEEC1avg" or histname == "EEC1":
                h_lasttop.GetXaxis().SetRangeUser(0.07, 0.25)
                h_firsttop.GetXaxis().SetRangeUser(0.07, 0.25)

            p = Plotter(hname+"_"+radius)
            p.plot_dir = plotdir
            p.drawRatio = True
            p.ratiotitle = "#frac{Last}{First}"
            p.addBackground(h_firsttop, "First top", 13)
            p.addSignal(h_lasttop, "Last top", ROOT.kRed)
            p.draw()
