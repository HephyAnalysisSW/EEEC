#!/usr/bin/env python

import os
import ROOT
import array as arr
from math                                         import sqrt
from EEEC.Tools.helpers                           import getObjFromFile
from EEEC.Tools.user                              import plot_directory
from MyRootTools.plotter.Plotter                  import Plotter
import Analysis.Tools.syncer

def project3Dto1D(hist3D, delta, cut, name, title):
    # z axis is largest zeta, y medium and x shortest
    Nbins_x = hist3D.GetXaxis().GetNbins()
    Nbins_y = hist3D.GetYaxis().GetNbins()
    Nbins_z = hist3D.GetZaxis().GetNbins()
    binning = []
    for i in range(Nbins_x):
        binning.append( round(hist3D.GetXaxis().GetBinLowEdge(i+1),5) )
    binning.append( round(hist3D.GetXaxis().GetBinUpEdge(Nbins_x),5) )
    # print binning
    hist1D = ROOT.TH1F(name, title, Nbins_x, arr.array('d',binning))
    entries = []
    for i in range(Nbins_x):
        bin_x = i+1
        for j in range(Nbins_y):
            bin_y = j+1
            for k in range(Nbins_z):
                bin_z = k+1
                zeta_short = round(hist3D.GetXaxis().GetBinCenter( bin_x ), 5)
                zeta_medium = round(hist3D.GetYaxis().GetBinCenter( bin_y ), 5)
                zeta_large = round(hist3D.GetZaxis().GetBinCenter( bin_z ), 5)
                if (zeta_large-zeta_medium <= delta) and (zeta_short >= cut):
                    zeta = (zeta_medium+zeta_large)/2
                    value = hist3D.GetBinContent(bin_x, bin_y, bin_z)
                    error = hist3D.GetBinError(bin_x, bin_y, bin_z)
                    entries.append( (zeta, value, error) )
    for i, low in enumerate(binning):
        if i == len(binning)-1:
            break
        high = binning[i+1]
        value_tot = 0
        error2_tot = 0
        for (zeta, value, error) in entries:
            if zeta >= low and zeta < high:
                value_tot += value
                error2_tot += error*error
        hist1D.SetBinContent(i+1, value_tot)
        hist1D.SetBinError(i+1, sqrt(error2_tot) )
    return hist1D


#-------------------------------------------------------------------------------
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--file',  action='store', type=str)
argParser.add_argument('--cut',   action='store', type=float)
argParser.add_argument('--delta', action='store', type=float)
args = argParser.parse_args()

if not os.path.exists(args.file):
    raise Exception("File %s does not exist"%args.file)

ROOT.gROOT.SetBatch(ROOT.kTRUE)
plotdir = plot_directory+"/EEEC_projections/"+args.file.replace(".root", "")+"/"
if not os.path.exists( plotdir ): os.makedirs( plotdir )
plotdirkin = plot_directory+"/Kinematics/"+args.file.replace(".root", "")+"/"
if not os.path.exists( plotdirkin ): os.makedirs( plotdirkin )


ptbins = ["500to525", "525to550", "550to575", "575to600", "600to625", "625to650", "650to675", "675to700"]

h_3d_EEEC1 = {}
h_1d_EEEC1 = {}

# h_3d_EEEC2 = {}

for ptbin in ptbins:
    h_3d_EEEC1[ptbin] = getObjFromFile(args.file, "EEEC1_jetpt"+ptbin)

kinplots = [
    ("mindR_top_jet", "min #Delta R(top, jet)"),
    ("mjet", "m_{jet} [GeV]"),
    ("pTjet", "Jet p_{T} [GeV]"),
    ("pTtop", "Top p_{T} [GeV]"),
    ("pTW", "W p_{T} [GeV]"),
    ("Nconstituents", "Number of jet constituents"),
]

for ptbin in ptbins:
    h_1d_EEEC1[ptbin] = project3Dto1D(h_3d_EEEC1[ptbin], args.delta, args.cut, "EEEC1_"+ptbin, "EEEC1_"+ptbin)
    p = Plotter("EEEC1_"+ptbin)
    p.plot_dir = plotdir
    # p.rebin = 4
    p.xtitle = "(#zeta_{max}+#zeta_{med})/2"
    p.ytitle = "Weighted triplets"
    p.drawLogo = False
    p.addBackground(h_1d_EEEC1[ptbin], "t#bar{t}", 15)

    p.addText(0.24, 0.7, "#zeta_{min} > %.3f"%(args.cut), size=14)
    p.addText(0.24, 0.65, "#zeta_{max}-#zeta_{med} < %.3f"%(args.delta), size=14)

    p.draw()

    for (histname, xtitle) in kinplots:
        hist = getObjFromFile(args.file, histname+"_ptjet"+ptbin)
        pkin = Plotter(histname+"_"+ptbin)
        pkin.plot_dir = plotdirkin
        pkin.xtitle = xtitle
        pkin.ytitle = "Events"
        pkin.addBackground(hist, "t#bar{t}", 15)
        pkin.draw()
