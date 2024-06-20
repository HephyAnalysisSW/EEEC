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

################################################################################
def drawEEEC(hists, path, mode="top"):

    canvas = ROOT.TCanvas("c", "c", 600, 600)
    ROOT.gPad.SetLeftMargin(.2)
    ROOT.gPad.SetRightMargin(.1)
    ROOT.gPad.SetTopMargin(.06)
    ROOT.gPad.SetBottomMargin(.15)


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
            h.GetYaxis().SetTitle("#zeta_{avg}^{-0.3} EEEC/EEC")
            h.GetXaxis().SetRangeUser(0.02, 0.4)
            h.GetYaxis().SetRangeUser(0.5, 1.5)
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
        # h.SetLineWidth(2)
        if firsthist:
            drawoption = "E1"
            firsthist = False
        else:
            drawoption = "E1 SAME"
        h.Draw(drawoption)

        fit.SetLineColor(color)
        fit.SetLineWidth(2)
        fit.Draw("SAME")
        leg.AddEntry(fit, legname, "l")
        h.SetStats(False)

    # for W draw hists in different order for visibility but not change ordering in legend
    if mode == "W":
        for (h, fit, legname, color) in reversed(hists):
            h.Draw("E1 SAME")
            fit.Draw("SAME")


    leg.Draw()
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


def getPeakRatio(x, y, ex, ey):
    ratio = 0
    error = 0
    prefactor = 88.
    if x > 0 and y > 0:
        ratio = prefactor*sqrt(x/y)
        deriv_x = prefactor*sqrt(x/y)/(2*x)
        deriv_y = prefactor* (-0.5) * sqrt(x/pow(y,3))
        error = sqrt(pow(deriv_x,2)*pow(ex,2) + pow(deriv_y,2)*pow(ey,2) )
    return ratio, error

def drawPeakPosition(graph, path, mode):
    c = ROOT.TCanvas("c", "c", 600, 600)
    graph.SetMarkerStyle(8)
    graph.Draw("AP")
    graph.GetXaxis().SetTitle("Jet p_{T}")
    if mode == "top":
        graph.GetYaxis().SetRangeUser(0., 0.8)
        graph.GetYaxis().SetTitle("#zeta_{peak}^{top}")
    else:
        graph.GetYaxis().SetRangeUser(0., 0.2)
        graph.GetYaxis().SetTitle("#zeta_{peak}^{W}")
    c.Print(path+".pdf")

def drawPeakPositionCompare(graph1, graph2, path, mode):
    c = ROOT.TCanvas("c", "c", 600, 600)
    graph1.SetMarkerStyle(8)
    graph1.Draw("AP")
    graph1.GetXaxis().SetTitle("Jet p_{T}")
    if mode == "top":
        graph1.GetYaxis().SetRangeUser(0., 0.8)
        graph1.GetYaxis().SetTitle("#zeta_{peak}^{top}")
    else:
        graph1.GetYaxis().SetTitle("#zeta_{peak}^{W}")
        graph1.GetYaxis().SetRangeUser(0., 0.2)
    graph2.SetMarkerStyle(8)
    graph2.SetMarkerColor(ROOT.kRed)
    graph2.SetLineColor(ROOT.kRed)
    graph2.Draw("P SAME")
    leg = ROOT.TLegend(.6, .7, .85, .85)
    leg.AddEntry(graph1, "All particles", "pe")
    leg.AddEntry(graph2, "Only charged", "pe")
    leg.Draw("SAME")
    c.Print(path+".pdf")

def drawPeakRatio(graph, path):
    c = ROOT.TCanvas("c", "c", 600, 600)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gPad.SetLeftMargin(.2)
    graph.SetMarkerStyle(8)
    graph.Draw("AP")
    graph.GetXaxis().SetNdivisions(505)
    graph.GetXaxis().SetTitle("Jet p_{T}")
    graph.GetYaxis().SetTitle("88 (#zeta_{peak}^{top}/#zeta_{peak}^{W})^{0.5}")
    graph.GetXaxis().SetRangeUser(400, 800)
    graph.GetYaxis().SetRangeUser(160, 180)
    graph.GetYaxis().SetTitleOffset(1.6)
    RatioFitFunction = ROOT.TF1("RatioFitFunction", "[0]")
    graph.Fit(RatioFitFunction, "Q0")
    fit = graph.GetFunction("RatioFitFunction")
    graph.GetHistogram().SetStats(False)
    graph.Draw("AP")
    mtop = fit.GetParameter(0)
    uncert = fit.GetParError(0)
    fitgraph = ROOT.TGraphErrors(1)
    fitgraph.SetPoint(0, 600, mtop)
    fitgraph.SetPointError(0, 300, uncert)
    fillcol = ROOT.TColor.GetColor("#b5bff7")
    linecol = ROOT.TColor.GetColor("#1935d1")
    fitgraph.SetLineColor(fillcol)
    fitgraph.SetFillColor(fillcol)
    fitgraph.Draw("E2 SAME")
    fitline = ROOT.TLine(400, mtop, 800, mtop)
    fitline.SetLineColor(linecol)
    fitline.SetLineWidth(2)
    fitline.Draw("SAME")
    graph.Draw("P SAME")
    ROOT.gPad.RedrawAxis()
    c.Print(path+".pdf")
################################################################################

files = [
    ("central", "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_CONVERTED.root"),
    ("HERWIG", "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_HERWIG_NEWHISTv2_CONVERTED.root"),
    # ("HLLHC", "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_HLLHC_CONVERTED.root"),
    # ("Run3", "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_Run3_CONVERTED.root"),
    # ("Run2", "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_Run2_CONVERTED.root"),
    # ("EFFIFLAT", "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_EFFIFLAT_CONVERTED.root"),
    # ("EFFIFLATSCALE", "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_EFFIFLATSCALE_CONVERTED.root"),
    # ("EFFIREALISTIC", "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_EFFIREALISTIC_CONVERTED.root"),
    # ("EFFIREALISTICSCALE", "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_EFFIREALISTICSCALE_CONVERTED.root"),
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

name_top = "top"
name_top_charged = "top_charged"
name_W = "W"
name_W_charged = "W_charged"

for (name, filename) in files:
    print "Running file '%s': %s"%(name, filename)
    h_ptavg = getObjFromFile(filename, "ptjet_avg")
    hists_top = []
    hists_W = []
    hists_top_charged = []
    hists_W_charged = []

    peakPositionTop = ROOT.TGraphErrors(len(ptbins))
    peakPositionTop_charged = ROOT.TGraphErrors(len(ptbins))
    peakPositionW = ROOT.TGraphErrors(len(ptbins))
    peakPositionW_charged = ROOT.TGraphErrors(len(ptbins))
    peakRatio = ROOT.TGraphErrors(len(ptbins))
    peakRatio_charged = ROOT.TGraphErrors(len(ptbins))

    plotdir = plot_directory+"/EEEC_plots/"+name+"/"
    if not os.path.exists( plotdir ): os.makedirs( plotdir )

    colors1 = [69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58]
    colors2 = [90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 2, 2]
    icol = 0
    for i, ptbin in enumerate(ptbins):
        print "Ptbin", ptbin
        print "  - get histogram"
        h_top = getObjFromFile(filename, name_top+"_"+ptbin)
        h_top_charged = getObjFromFile(filename, name_top_charged+"_"+ptbin)
        h_W   = getObjFromFile(filename, name_W+"_"+ptbin)
        h_W_charged   = getObjFromFile(filename, name_W_charged+"_"+ptbin)

        print "  - perform fit"
        wmin = 0.0
        if ptbin in ["600to650","650to700","700to750","750to800"]:
            wmin = 0.025
        elif ptbin in ["500to525","525to550","550to575","575to600"]:
            wmin = 0.05
        else:
            wmin = 0.075

        fit_top         = fitPeak(h_top,         0.10, 0.70, "top")
        fit_top_charged = fitPeak(h_top_charged, 0.10, 0.70, "top")
        fit_W           = fitPeak(h_W,           wmin, 0.25, "W")
        fit_W_charged   = fitPeak(h_W_charged  , wmin, 0.25, "W")

        legname = ptbin.split("to")[0]+" < jet p_{T} < "+ptbin.split("to")[1]
        hists_top.append( (h_top, fit_top, legname, colors1[icol]) )
        hists_top_charged.append( (h_top_charged, fit_top_charged, legname, colors1[icol]) )
        hists_W.append( (h_W, fit_W, legname, colors1[icol]) )
        hists_W_charged.append( (h_W_charged, fit_W_charged, legname, colors1[icol]) )
        icol += 1

        ptcenter = h_ptavg.GetBinContent(i+1)
        ptwidth = h_ptavg.GetBinError(i+1)
        p_top = fit_top.GetParameter(1)
        e_top = fit_top.GetParError(1)
        p_W   = fit_W.GetParameter(1)
        e_W   = fit_W.GetParError(1)
        ratio, r_error = getPeakRatio(p_top, p_W, e_top, e_W)
        peakPositionTop.SetPoint(i, ptcenter, p_top )
        peakPositionTop.SetPointError(i, ptwidth, e_top )
        peakPositionW.SetPoint(i, ptcenter, p_W )
        peakPositionW.SetPointError(i, ptwidth, e_W )
        peakRatio.SetPoint(i, ptcenter, ratio )
        peakRatio.SetPointError(i, ptwidth, r_error )
        p_top_charged = fit_top_charged.GetParameter(1)
        e_top_charged = fit_top_charged.GetParError(1)
        p_W_charged   = fit_W_charged.GetParameter(1)
        e_W_charged   = fit_W_charged.GetParError(1)
        ratio_charged, r_error_charged = getPeakRatio(p_top_charged, p_W_charged, e_top_charged, e_W_charged)
        peakPositionTop_charged.SetPoint(i, ptcenter, p_top_charged )
        peakPositionTop_charged.SetPointError(i, ptwidth, e_top_charged )
        peakPositionW_charged.SetPoint(i, ptcenter, p_W_charged )
        peakPositionW_charged.SetPointError(i, ptwidth, e_W_charged )
        peakRatio_charged.SetPoint(i, ptcenter, ratio_charged )
        peakRatio_charged.SetPointError(i, ptwidth, r_error_charged )

    drawEEEC(hists_top, plotdir+"topPeak", "top")
    drawEEEC(hists_top_charged, plotdir+"topPeak_charged", "top")
    drawEEEC(hists_W, plotdir+"WPeak", "W")
    drawEEEC(hists_W_charged, plotdir+"WPeak_charged", "W")

    drawPeakPosition(peakPositionTop, plotdir+"TopPosition", "top")
    drawPeakPosition(peakPositionTop_charged, plotdir+"TopPosition_charged", "top")
    drawPeakPositionCompare(peakPositionTop, peakPositionTop_charged, plotdir+"TopPosition_compare", "top")
    drawPeakPosition(peakPositionW, plotdir+"WPosition", "W")
    drawPeakPosition(peakPositionW_charged, plotdir+"WPosition_charged", "W")
    drawPeakPositionCompare(peakPositionW, peakPositionW_charged, plotdir+"WPosition_compare", "W")
    drawPeakRatio(peakRatio, plotdir+"PeakRatio")
    drawPeakRatio(peakRatio_charged, plotdir+"PeakRatio_charged")

    outfile = ROOT.TFile(plotdir+"Results.root", "RECREATE")
    outfile.cd()
    peakPositionTop.Write("TopPosition")
    peakPositionTop_charged.Write("TopPosition_charged")
    peakPositionW.Write("WPosition")
    peakPositionW_charged.Write("WPosition_charged")
    peakRatio.Write("Ratio")
    peakRatio_charged.Write("Ratio_charged")
    outfile.Close()
