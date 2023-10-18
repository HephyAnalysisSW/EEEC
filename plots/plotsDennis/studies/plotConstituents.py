#!/usr/bin/env python

import os
import ROOT
import array as arr
from math                                         import sqrt
from EEEC.Tools.helpers                           import getObjFromFile
from EEEC.Tools.user                              import plot_directory
from MyRootTools.plotter.Plotter                  import Plotter
import Analysis.Tools.syncer
import EEEC.Tools.logger as logger
logger    = logger.get_logger(   "INFO", logFile = None)

ROOT.gROOT.SetBatch(ROOT.kTRUE)

def drawMap(hist_2d, savepath, weighted=False):
    hist_2d.SetTitle("")
    hist_2d.GetXaxis().SetTitle("p_{T} [GeV]")
    hist_2d.GetYaxis().SetTitle("#eta")
    hist_2d.GetZaxis().SetTitle("Constituents")
    if weighted:
        hist_2d.GetZaxis().SetTitle("Weighted constituents")
    hist_2d.GetXaxis().SetNdivisions(505)
    hist_2d.GetYaxis().SetNdivisions(505)
    hist_2d.GetZaxis().SetTitleOffset(1.2)
    c = ROOT.TCanvas(hist_2d.GetName()+"_canv", "", 800, 600)
    ROOT.gPad.SetRightMargin(.2)
    hist_2d.Draw("COLZ")
    c.Print(savepath)
    draw1D(hist_2d, savepath, weighted)

def draw1D(hist_2d, savepath, weighted=False):
    # hist X
    hist_X = hist_2d.ProjectionX()
    hist_X.SetTitle("")
    hist_X.GetXaxis().SetTitle("p_{T} [GeV]")
    hist_X.GetYaxis().SetTitle("Constituents")
    if weighted:
        hist_X.GetYaxis().SetTitle("Weighted constituents")
    hist_X.GetXaxis().SetNdivisions(505)
    hist_X.GetYaxis().SetNdivisions(505)
    cX = ROOT.TCanvas(hist_X.GetName()+"_canv", "", 800, 600)
    hist_X.Draw("HIST")
    cX.Print(savepath.replace(".pdf", "__ptProjection.pdf"))
    # hist Y
    hist_Y = hist_2d.ProjectionY()
    hist_Y.SetTitle("")
    hist_Y.GetXaxis().SetTitle("#eta")
    hist_Y.GetYaxis().SetTitle("Constituents")
    if weighted:
        hist_Y.GetYaxis().SetTitle("Weighted constituents")
    hist_Y.GetXaxis().SetNdivisions(505)
    hist_Y.GetYaxis().SetNdivisions(505)
    cY = ROOT.TCanvas(hist_Y.GetName()+"_canv", "", 800, 600)
    hist_Y.Draw("HIST")
    cY.Print(savepath.replace(".pdf", "__etaProjection.pdf"))

plotdir = plot_directory+"/EEEC_constituents/"
if not os.path.exists( plotdir ): os.makedirs( plotdir )

filedir = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/"
filename = "EEEC_PP_13000_1725_804_HARDPT300to900_MPIon_HADon_PFSTUDIES.root"
ptbins = ["500to525", "525to550", "550to575", "575to600", "600to625", "625to650", "650to675", "675to700"]

for ptbin in ptbins:
    hist2D_unweighted = getObjFromFile(filedir+filename, "ptetaconstituents_unweighted_ptjet"+ptbin)
    hist2D_W = getObjFromFile(filedir+filename, "ptetaconstituents_W_ptjet"+ptbin)
    hist2D_top = getObjFromFile(filedir+filename, "ptetaconstituents_top_ptjet"+ptbin)
    hist2D_all = getObjFromFile(filedir+filename, "ptetaconstituents_all_ptjet"+ptbin)
    drawMap(hist2D_unweighted, plotdir+"PtEta_unweighted__"+ptbin+".pdf", False)
    drawMap(hist2D_all, plotdir+"PtEta_all__"+ptbin+".pdf", True)
    drawMap(hist2D_W, plotdir+"PtEta_W__"+ptbin+".pdf", True)
    drawMap(hist2D_top, plotdir+"PtEta_top__"+ptbin+".pdf", True)
