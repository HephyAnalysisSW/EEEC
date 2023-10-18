#!/usr/bin/env python

import os
import ROOT
from EEEC.Tools.helpers                           import getObjFromFile
from EEEC.Tools.user                              import plot_directory
from MyRootTools.plotter.Plotter                  import Plotter
import Analysis.Tools.syncer


import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--file', action='store')
argParser.add_argument('--ptbins',          action='store_true', default=False)
args = argParser.parse_args()

if not os.path.exists(args.file):
    raise Exception("File %s does not exist"%args.file)

ROOT.gROOT.SetBatch(ROOT.kTRUE)
plotdir = plot_directory+"/Kinematics/"+args.file.replace(".root", "")+"/"
if not os.path.exists( plotdir ): os.makedirs( plotdir )

plots = [
    ("mindR_top_jet", "min #Delta R(top, jet)"),
    ("mjet", "m_{jet} [GeV]"),
    ("pTjet", "Jet p_{T} [GeV]"),
    ("pTtop", "Top p_{T} [GeV]"),
    ("pTW", "W p_{T} [GeV]"),
    ("Nconstituents", "Number of jet constituents"),
]


if args.ptbins:
    newplots = []
    ptbins = ["500to525", "525to550", "550to575", "575to600", "600to625", "625to650", "650to675", "675to700"]
    for (histname, xtitle) in plots:
        for ptbin in ptbins:
            newplots.append( (histname+"_ptjet"+ptbin, xtitle))
    plots = newplots


for (histname, xtitle) in plots:
    hist = getObjFromFile(args.file, histname)
    p = Plotter(histname)
    p.plot_dir = plotdir
    p.xtitle = xtitle
    p.ytitle = "Events"
    p.addBackground(hist, "t#bar{t}", 15)
    p.draw()
