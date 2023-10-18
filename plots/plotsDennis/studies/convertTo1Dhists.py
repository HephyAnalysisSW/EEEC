#!/usr/bin/env python

import os
import ROOT
import array as arr
import numpy as np
from math                                         import sqrt, exp
from EEEC.Tools.helpers                           import getObjFromFile
from EEEC.Tools.user                              import plot_directory
from EEEC.Tools.getPeaksFrom3D                    import getTopPeak, getWPeak

from MyRootTools.plotter.Plotter                  import Plotter
import Analysis.Tools.syncer

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetOptStat(0)



################################################################################
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--file',           action='store',      default=None)
args = argParser.parse_args()


if args.file is None:
    raise RuntimeError( "You have to specify a file with --file=FILENAME")

path = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/"
infilename = path+args.file+".root"
print "Reading from file", infilename

outfilename = args.file+"_CONVERTED.root"
outfile = ROOT.TFile(outfilename, "RECREATE")

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

name_3D = "EEEC1"
name_twopoint = "EEC1"

name_3D_charged = "EEEC1charged"
name_twopoint_charged = "EEC1charged"

h_pt_avg = ROOT.TH1F("pt_avg", "pt_avg", len(ptbins), 0.5, 0.5+len(ptbins))

for i, ptbin in enumerate(ptbins):
    print "pT bin", ptbin
    h_3D = getObjFromFile(infilename, name_3D+"_jetpt"+ptbin)
    h_3D_charged = getObjFromFile(infilename, name_3D_charged+"_jetpt"+ptbin)
    h_twopoint = getObjFromFile(infilename, name_twopoint+"_jetpt"+ptbin)
    h_twopoint_charged = getObjFromFile(infilename, name_twopoint_charged+"_jetpt"+ptbin)
    h_pt = getObjFromFile(infilename, "pTjet_ptjet"+ptbin)
    h_pt_avg.SetBinContent(i+1, h_pt.GetMean())
    h_pt_avg.SetBinError(i+1, h_pt.GetMeanError())

    mt = 172.5
    pt = float(ptbin.split("to")[0])
    asymm_max = pow(mt,2)/pow(pt,2)
    short_min = 0.8 * pow(mt,2)/pow(pt,2)
    print "  - get top peak"
    h_top = getTopPeak(h_3D, asymm_max, short_min)
    h_top_charged = getTopPeak(h_3D_charged, asymm_max, short_min)

    print "  - get W peak"
    h_W = getWPeak(h_3D, h_twopoint, True)
    h_W_charged = getWPeak(h_3D_charged, h_twopoint_charged, True)
    outfile.cd()
    h_top.Write("top_"+ptbin)
    h_W.Write("W_"+ptbin)
    h_top_charged.Write("top_charged_"+ptbin)
    h_W_charged.Write("W_charged_"+ptbin)

outfile.cd()
h_pt_avg.Write("ptjet_avg")
outfile.Close()

print "Wrote output in", outfilename
