#!/usr/bin/env python

import ROOT
import Analysis.Tools.syncer

from EEEC.Tools.helpers                           import getObjFromFile, writeObjToFile
from EEEC.Tools.user                              import plot_directory
from MyRootTools.plotter.Plotter                  import Plotter
ROOT.gROOT.SetBatch(ROOT.kTRUE)

import EEEC.Tools.logger as logger
logger    = logger.get_logger(   "INFO", logFile = None)

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--year',             action='store', type=str, default="UL2018")
args = argParser.parse_args()

def drawMatrix(hist, xtitle, ytitle, savepath):
        ROOT.gStyle.SetLegendBorderSize(0)
        ROOT.gStyle.SetPadTickX(1)
        ROOT.gStyle.SetPadTickY(1)
        ROOT.gStyle.SetOptStat(0)
        # ROOT.gStyle.SetPalette(ROOT.kSunset)
        c = ROOT.TCanvas("c", "c", 600, 600)
        ROOT.gPad.SetRightMargin(0.23)
        ROOT.gPad.SetLeftMargin(0.19)
        ROOT.gPad.SetBottomMargin(0.12)
        hist.SetTitle(" ")
        hist.GetXaxis().SetTitle(xtitle)
        hist.GetYaxis().SetTitle(ytitle)
        hist.GetZaxis().SetTitle("Triplets")
        hist.GetZaxis().SetTitleOffset(1.3)
        hist.Draw("COLZ")
        c.Print(savepath)



file = "/groups/hephy/cms/dennis.schwarz/www/EEEC/results/TTbar.root"

histograms = {
    "Weight": ("Triplet weight", "Triplets", True),
    "WeightZoom": ("Triplet weight", "Triplets", True),
    "Zeta": ("#zeta", "Weighted triplets", False),
    "ZetaNoWeight": ("#zeta", "Triplets", False),
    "MatchingEfficiency": ("Matching efficiency", "Events", False),
}

histograms_2D = {
    "Weight_matrix": ("Triplet weight (gen)", "Triplet weight (rec)"),
    "ZetaNoWeight_matrix": ("#zeta (gen)", "#zeta (rec)"),
}

for histname in histograms.keys():
    (xtitle, ytitle, drawlog) = histograms[histname]
    p = Plotter(histname)
    p.plot_dir = plot_directory+"/TripletMatching/"
    p.xtitle = xtitle
    p.ytitle = ytitle
    p.drawRatio = True
    if drawlog:
        p.log = True
    if histname == "MatchingEfficiency":
        hist = getObjFromFile(file, histname)
        p.addBackground(hist, "TTbar", 633)
    else:
        h_rec = getObjFromFile(file, histname+"_rec")
        h_gen = getObjFromFile(file, histname+"_gen")
        p.addBackground(h_rec, "Detector level", 633)
        p.addSignal(h_gen, "Particle level", ROOT.kAzure+7)
    p.draw()

for histname in histograms_2D.keys():
    (xtitle, ytitle) = histograms_2D[histname]
    hist = getObjFromFile(file, histname)
    drawMatrix(hist, xtitle, ytitle, plot_directory+"/TripletMatching/"+histname+".pdf")
