#!/usr/bin/env python

import os
import ROOT
import array as arr
import numpy as np
from math                                         import sqrt, exp
from EEEC.Tools.helpers                           import getObjFromFile
from EEEC.Tools.user                              import plot_directory
from EEEC.Tools.getPeaksFrom3D                    import getTopPeak, getWPeak
from EEEC.Tools.crystalBall                       import OneSidedCB, DoubleSidedCB

from MyRootTools.plotter.Plotter                  import Plotter
import Analysis.Tools.syncer

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetEndErrorSize(0)

################################################################################
def drawEEEC(hists, path, mode="top", hadComparePlots=None):

    canvas = ROOT.TCanvas("c", "c", 600, 600)
    pad1 = ROOT.TPad("pad1", "pad1", 0., 0., 1., 1.)
    pad1.SetLeftMargin(.2)
    pad1.SetRightMargin(.1)
    pad1.SetTopMargin(.06)
    pad1.SetBottomMargin(.17)
    pad1.Draw()

    if hadComparePlots is not None:
        pad2 = ROOT.TPad("pad2", "pad2", 0.24, 0.6, 0.59, 0.92)
        pad2.SetLeftMargin(0.1)
        pad2.SetRightMargin(0.05)
        pad2.SetTopMargin(0.05)
        pad2.SetBottomMargin(0.1)
        pad2.Draw()

    pad1.cd()
    leg_height=0.4
    leg_width=0.25
    if mode == "W":
        xleg, yleg = 0.6, 0.5
    elif mode=="top":
        xleg, yleg = 0.25, 0.5
    leg = ROOT.TLegend(xleg, yleg, xleg+leg_width, yleg+leg_height )

    firsthist = True
    for (h, fit, legname, color) in hists:
        h.SetTitle("")
        h.GetXaxis().SetTitle("#zeta_{avg}")
        if mode == "W":
            h.GetYaxis().SetTitle("#zeta_{avg}^{-0.25} EEEC/EEC")
            h.GetXaxis().SetRangeUser(0.02, 0.2)
            h.GetYaxis().SetRangeUser(0.6, 1.35)
        elif mode == "top":
            h.GetYaxis().SetTitle("EEEC")
        h.GetYaxis().SetTitleOffset(1.5)
        h.GetYaxis().SetTitleSize(0.06)
        h.GetXaxis().SetNdivisions(505)
        h.GetXaxis().SetTitleOffset(1.2)
        h.SetLineColor(1)
        h.SetMarkerColor(1)
        h.SetMarkerSize(.2)
        h.SetMarkerStyle(8)
        if firsthist:
            drawoption = "E1"
            firsthist = False
        else:
            drawoption = "E1 SAME"
        h.Draw(drawoption)

        fit.SetLineColor(color)
        fit.SetLineWidth(3)
        fit.Draw("SAME")
        leg.AddEntry(fit, legname, "l")
        h.SetStats(False)

    # for W draw hists in different order for visibility but not change ordering in legend
    if mode == "W":
        for (h, fit, legname, color) in reversed(hists):
            h.Draw("E1 SAME")
            fit.Draw("SAME")


    leg.Draw()

    if hadComparePlots is not None:
        pad2.cd()
        (h_Had, h_noHad, f_Had, f_noHad) = hadComparePlots

        h_noHad.GetYaxis().SetTitle("")
        h_noHad.GetXaxis().SetRangeUser(0.055, 0.095)
        h_noHad.GetYaxis().SetRangeUser(0.81, 0.94)
        h_noHad.GetYaxis().SetTitleOffset(1.5)
        h_noHad.GetYaxis().SetTitleSize(0.06)
        h_noHad.GetXaxis().SetNdivisions(505)
        h_noHad.GetXaxis().SetTitleOffset(1.2)
        h_noHad.SetStats(False)

        h_noHad.SetLineColor(15)
        h_noHad.SetMarkerColor(15)
        h_noHad.SetMarkerSize(.2)
        h_noHad.SetMarkerStyle(8)
        h_Had.SetLineColor(1)
        h_Had.SetMarkerColor(1)
        h_Had.SetMarkerSize(.2)
        h_Had.SetMarkerStyle(8)
        f_noHad.SetLineColor(ROOT.kRed)
        f_noHad.SetLineWidth(2)
        f_Had.SetLineColor(ROOT.kBlue)
        f_Had.SetLineWidth(2)
        h_noHad.Draw("E1")
        h_Had.Draw("E1 SAME")
        f_noHad.Draw("SAME")
        f_Had.Draw("SAME")

        leg2 = ROOT.TLegend(.13, .65, .8, .9)
        leg2.AddEntry(f_Had, "Hadron level (600 < p_{T} < 650 GeV)", "l")
        leg2.AddEntry(f_noHad, "Particle level (600 < p_{T} < 650 GeV)", "l")
        leg2.AddEntry(None, "(Scaled by 0.73 for comparison)", "")
        leg2.SetTextSize(.047)
        leg2.Draw()

    canvas.Print(path+".pdf")


def findPeak(hist, min, max):
    maxbin = -1
    ymax = 0.0
    for i in range(hist.GetXaxis().GetNbins()):
        if hist.GetXaxis().GetBinLowEdge(i+1) > min and hist.GetXaxis().GetBinUpEdge(i+1) < max:
            content = hist.GetBinContent(i+1)
            if content > ymax:
                ymax = content
                maxbin = i+1
    return maxbin

def fitPeak(hist, min, max, mode):
    peakBin = findPeak(hist, min, max)
    if peakBin > 0:
        xvalPeak = hist.GetXaxis().GetBinCenter(peakBin)
    else:
        xvalPeak = 0.5

    # print xvalPeak

    # First perform Gaus fit to get a rough idea of fit parameters
    rangeGaus_lo = xvalPeak-0.15 if mode == "top" else xvalPeak-0.03
    rangeGaus_hi = xvalPeak+0.15 if mode == "top" else xvalPeak+0.03
    gausFitFunktion = ROOT.TF1("gausFitFunktion", "gaus", rangeGaus_lo, rangeGaus_hi)
    hist.Fit(gausFitFunktion, "RQ")
    gausFit = hist.GetFunction("gausFitFunktion")
    normGaus = gausFit.GetParameter(0)
    meanGaus = gausFit.GetParameter(1)
    sigmaGaus = gausFit.GetParameter(2)
    # return gausFit

    # Now fit with double sided crytal ball
    norm_init = normGaus
    mean_init = meanGaus
    sigmaL_init = sigmaGaus
    sigmaR_init = sigmaGaus
    alphaL_init = 2*sigmaGaus
    alphaR_init = 2*sigmaGaus
    nL_init = 2
    nR_init = 2
    rangeGaus_lo = xvalPeak-sigmaGaus if mode == "top" else xvalPeak-0.25*sigmaGaus
    rangeGaus_hi = xvalPeak+1.5*sigmaGaus if mode == "top" else xvalPeak+0.5*sigmaGaus
    CBFunction = ROOT.TF1("CBFunction", DoubleSidedCB, rangeGaus_lo, rangeGaus_hi, 8)
    CBFunction.SetParameters(norm_init, mean_init, sigmaL_init, sigmaR_init, alphaL_init, alphaR_init, nL_init, nR_init)
    # CBFunction.SetParLimits(1, meanGaus-0.5*sigmaGaus, meanGaus+0.5*sigmaGaus)
    # CBFunction.SetParLimits(2, 0.5*sigmaGaus, 2.*sigmaGaus)
    # CBFunction.SetParLimits(3, 0.5*sigmaGaus, 2.*sigmaGaus)
    # CBFunction.SetParLimits(4, meanGaus-1.*sigmaGaus, meanGaus)
    # CBFunction.SetParLimits(5, meanGaus, meanGaus+1.*sigmaGaus)
    CBFunction.SetParLimits(6, -5, 5)
    CBFunction.SetParLimits(7, -5, 5)

    hist.Fit(CBFunction, "RQ")
    CBfit = hist.GetFunction("CBFunction")
    return CBfit



################################################################################
################################################################################
################################################################################

f_central = "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_CONVERTED.root"
f_noHad = "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIoff_HADoff_R12_NEWHISTv2_CONVERTED.root"
# f_noHad = "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_HERWIG_NEWHISTv2_CONVERTED.root"

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

name_W = "W"
name_W_charged = "W_charged"

hists_W = []
hists_W_charged = []
hadComparePlots = []

plotdir = plot_directory+"/EEEC_plots_paper/"
if not os.path.exists( plotdir ): os.makedirs( plotdir )

colors1 = [69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58]
colors2 = [90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 2, 2]
icol = 0
for i, ptbin in enumerate(ptbins):
    print "Ptbin", ptbin
    print "  - get histogram"
    h_W   = getObjFromFile(f_central, name_W+"_"+ptbin)
    h_W_noHad   = getObjFromFile(f_noHad, name_W+"_"+ptbin)
    h_W_noHad.Scale(0.73)
    h_W_charged   = getObjFromFile(f_central, name_W_charged+"_"+ptbin)

    print "  - perform fit"
    wmin = 0.0
    if ptbin in ["600to650","650to700","700to750","750to800"]:
        wmin = 0.025
    elif ptbin in ["500to525","525to550","550to575","575to600"]:
        wmin = 0.05
    else:
        wmin = 0.075

    fit_W           = fitPeak(h_W,           wmin, 0.25, "W")
    fit_W_noHad     = fitPeak(h_W_noHad,     wmin, 0.25, "W")
    fit_W_charged   = fitPeak(h_W_charged  , wmin, 0.25, "W")

    legname = ptbin.split("to")[0]+" < jet p_{T} < "+ptbin.split("to")[1]+" GeV"
    hists_W.append( (h_W, fit_W, legname, colors1[icol]) )
    hists_W_charged.append( (h_W_charged, fit_W_charged, legname, colors1[icol]) )
    icol += 1
    if ptbin == "600to650":
        hadComparePlots = (h_W.Clone(), h_W_noHad.Clone(), fit_W.Clone(), fit_W_noHad.Clone())

drawEEEC(hists_W, plotdir+"WPeak", "W", hadComparePlots)
drawEEEC(hists_W_charged, plotdir+"WPeak_charged", "W")
