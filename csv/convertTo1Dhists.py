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
argParser.add_argument('--divideWidth',    action='store_true',      default=False)
args = argParser.parse_args()


if args.file is None:
    raise RuntimeError( "You have to specify a file with --file=FILENAME")

normToWidth = True if args.divideWidth else False
if normToWidth:
    print "Will divide by bin width"
else:
    print "Will NOT divide by bin width"

path = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/"
infilename = path+args.file+".root"
print "Reading from file", infilename

outfilename = args.file+"_1D.root"
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
name_long = "EEEC1Long"
name_medium = "EEEC1Medium"
name_twopoint = "EEC1"


name_3D_charged = "EEEC1charged"
name_long_charged = "EEEC1Longcharged"
name_medium_charged = "EEEC1Mediumcharged"
name_twopoint_charged = "EEC1charged"

for i, ptbin in enumerate(ptbins):
    print "pT bin", ptbin

    ptjetname = "pTjet_ptjet"+ptbin
    h_ptjet = getObjFromFile(infilename,ptjetname)

    h_3D = getObjFromFile(infilename, name_3D+"_jetpt"+ptbin)
    h_long = getObjFromFile(infilename, name_long+"_jetpt"+ptbin)
    h_medium = getObjFromFile(infilename, name_medium+"_jetpt"+ptbin)
    h_twopoint = getObjFromFile(infilename, name_twopoint+"_jetpt"+ptbin)
    h_twopoint_mod = getObjFromFile(infilename, name_twopoint.replace("EEC1", "EEC1Mod")+"_jetpt"+ptbin)

    h_3D_charged = getObjFromFile(infilename, name_3D_charged+"_jetpt"+ptbin)
    h_long_charged = getObjFromFile(infilename, name_long_charged+"_jetpt"+ptbin)
    h_medium_charged = getObjFromFile(infilename, name_medium_charged+"_jetpt"+ptbin)
    h_twopoint_charged = getObjFromFile(infilename, name_twopoint_charged+"_jetpt"+ptbin)
    h_twopoint_mod_charged = getObjFromFile(infilename, name_twopoint_charged.replace("EEC1", "EEC1Mod")+"_jetpt"+ptbin)

    mt = 172.5
    pt = float(ptbin.split("to")[0])
    asymm_max = pow(mt,2)/pow(pt,2)
    short_min = 0.8 * pow(mt,2)/pow(pt,2)
    print "  - get top peak"
    h_top = getTopPeak(h_3D, asymm_max, short_min, normToWidth)
    h_top_charged = getTopPeak(h_3D_charged, asymm_max, short_min, normToWidth)

    # Get W
    print "  - get W peak"
    h_W_avg = getWPeak(h_3D, None, False, normToWidth)
    h_W_avg_charged = getWPeak(h_3D_charged, None, False, normToWidth)

    outfile.cd()
    h_ptjet.Write(ptjetname)

    h_top.Write("EEEC1top"+"_jetpt"+ptbin)
    h_W_avg.Write("EEEC1avg"+"_jetpt"+ptbin)
    h_long.Write("EEEC1long"+"_jetpt"+ptbin)
    h_medium.Write("EEEC1medium"+"_jetpt"+ptbin)
    h_twopoint.Write("EEC1"+"_jetpt"+ptbin)
    h_twopoint_mod.Write("EEC1mod"+"_jetpt"+ptbin)

    h_top_charged.Write("EEEC1top_charged"+"_jetpt"+ptbin)
    h_W_avg_charged.Write("EEEC1avg_charged"+"_jetpt"+ptbin)
    h_long_charged.Write("EEEC1long_charged"+"_jetpt"+ptbin)
    h_medium_charged.Write("EEEC1medium_charged"+"_jetpt"+ptbin)
    h_twopoint_charged.Write("EEC1_charged"+"_jetpt"+ptbin)
    h_twopoint_mod_charged.Write("EEC1mod_charged"+"_jetpt"+ptbin)

outfile.cd()
outfile.Close()

print "Wrote output in", outfilename
