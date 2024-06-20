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

def extractUncertainty(nominal, variation):
    absdiff = []
    for i in range(nominal.GetN()):
        absdiff.append(abs(nominal.GetY()[i]-variation.GetY()[i]))
    return absdiff

def addUncert(graph, uncerts):
    for i in range(graph.GetN()):
        xerr = graph.GetErrorX(i)
        newerr = sqrt( pow(graph.GetErrorY(i),2)+pow(uncerts[i],2) )
        graph.SetPointError(i, xerr, newerr)
    return graph

def getRatio(g1, g2):
    ratio = g1.Clone()
    prefactor = 88.
    for i in range(g1.GetN()):
        r = 0
        error = 0
        xval = g1.GetX()[i]
        xerr = g1.GetErrorX(i)
        if g1.GetY()[i] != 0 and g2.GetY()[i] != 0:
            r = prefactor*sqrt(g1.GetY()[i]/g2.GetY()[i])
            deriv_g1 = prefactor*sqrt(g1.GetY()[i]/g2.GetY()[i])/(2*g1.GetY()[i])
            deriv_g2 = prefactor* (-0.5) * sqrt(g1.GetY()[i]/pow(g2.GetY()[i],3))
            error = sqrt(pow(deriv_g1,2)*pow(g1.GetErrorY(i),2) + pow(deriv_g2,2)*pow(g2.GetErrorY(i),2) )
        ratio.SetPoint(i, xval, r)
        ratio.SetPointError(i, xerr, error)
    return ratio

def drawPeakPositionCompare(graphs, path, mode):
    c = ROOT.TCanvas("c", "c", 600, 600)
    leg = ROOT.TLegend(.6, .7, .85, .85)
    first = True
    for (g, col, name) in graphs:
        g.SetMarkerStyle(8)
        g.SetMarkerColor(col)
        g.SetLineColor(col)
        if first:
            g.Draw("AP")
            first = False
        else:
            g.Draw("P SAME")
        g.GetXaxis().SetTitle("Jet p_{T}")
        if mode == "top":
            g.GetYaxis().SetRangeUser(0., 0.8)
            g.GetYaxis().SetTitle("#zeta_{peak}^{top}")
        else:
            g.GetYaxis().SetTitle("#zeta_{peak}^{W}")
            g.GetYaxis().SetRangeUser(0., 0.2)

        leg.AddEntry(g, name, "pe")
    leg.Draw("SAME")
    c.Print(path+".pdf")

def drawRatio(graph_stat, graph_tot, path):
    color_stat = ROOT.TColor.GetColor("#2b2b2b")
    color_tot = ROOT.TColor.GetColor("#2b2b2b")
    c = ROOT.TCanvas("c", "c", 600, 600)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gPad.SetLeftMargin(.2)
    graph_tot.SetLineWidth(1)
    graph_tot.SetMarkerStyle(8)
    graph_tot.SetMarkerColor(color_tot)
    graph_tot.SetLineColor(color_tot)
    graph_tot.Draw("AP")
    graph_tot.GetXaxis().SetNdivisions(505)
    graph_tot.GetXaxis().SetTitle("Jet p_{T}")
    graph_tot.GetYaxis().SetTitle("88 (#zeta_{peak}^{top}/#zeta_{peak}^{W})^{0.5}")
    graph_tot.GetXaxis().SetRangeUser(400, 800)
    graph_tot.GetYaxis().SetRangeUser(160, 180)
    graph_tot.GetYaxis().SetTitleOffset(1.6)

    graph_stat.SetLineWidth(3)
    graph_stat.SetMarkerStyle(8)
    graph_stat.SetMarkerColor(color_stat)
    graph_stat.SetLineColor(color_stat)
    graph_stat.Draw("P SAME")

    fitgraph_stat, fitline_stat = fitRatio(graph_stat)
    fitgraph_stat.SetLineColor(ROOT.TColor.GetColor("#b5bff7"))
    fitgraph_stat.SetFillColor(ROOT.TColor.GetColor("#b5bff7"))
    fitline_stat.SetLineColor(ROOT.TColor.GetColor("#1935d1"))

    fitgraph_tot, fitline_tot = fitRatio(graph_tot)
    fitgraph_tot.SetLineColor(ROOT.TColor.GetColor("#d66f6f"))
    fitgraph_tot.SetFillColor(ROOT.TColor.GetColor("#d66f6f"))
    fitline_tot.SetLineColor(ROOT.TColor.GetColor("#8f2727"))

    fitgraph_tot.Draw("E2 SAME")
    fitline_tot.Draw("SAME")

    fitgraph_stat.Draw("E2 SAME")
    fitline_stat.Draw("SAME")

    graph_tot.Draw("P SAME")
    graph_stat.Draw("P SAME")

    leg = ROOT.TLegend(.3, .2, .8, .5)
    leg.AddEntry(fitgraph_tot, "Total uncertainty", "f")
    leg.AddEntry(fitgraph_stat, "Stat. uncertainty", "f")
    leg.Draw()

    ROOT.gPad.RedrawAxis()
    c.Print(path+".pdf")

def fitRatio(graph):
    RatioFitFunction = ROOT.TF1("RatioFitFunction", "[0]")
    graph.Fit(RatioFitFunction, "Q0")
    fit = graph.GetFunction("RatioFitFunction")
    mtop = fit.GetParameter(0)
    uncert = fit.GetParError(0)
    fitgraph = ROOT.TGraphErrors(1)
    fitgraph.SetPoint(0, 600, mtop)
    fitgraph.SetPointError(0, 300, uncert)
    fitline = ROOT.TLine(400, mtop, 800, mtop)
    fitline.SetLineWidth(2)
    return fitgraph, fitline

################################################################################

directory = "/groups/hephy/cms/dennis.schwarz/www/MTopCorrelations/plots/EEEC_plots/"

files = [
    ("Nominal", 1, directory+"central/Results.root"),
    ("70% efficiency", ROOT.kRed-4, directory+"EFFIFLAT/Results.root"),
    ("35% efficiency", ROOT.kRed+3, directory+"EFFIFLATSCALE/Results.root"),
    ("Efficiency model", ROOT.kAzure+7, directory+"EFFIREALISTIC/Results.root"),
    ("Half-efficiency model", ROOT.kBlue-2, directory+"EFFIREALISTICSCALE/Results.root"),
]


plotdir = plot_directory+"/EEEC_uncerts/"
if not os.path.exists( plotdir ): os.makedirs( plotdir )

TopPeaks = []
TopPeaks_charged = []
WPeaks = []
WPeaks_charged = []
Ratios = []
Ratios_charged = []

for (name, color, filename) in files:
    print "Running file '%s': %s"%(name, filename)
    peakPositionTop = getObjFromFile(filename, "TopPosition")
    peakPositionTop_charged = getObjFromFile(filename, "TopPosition_charged")
    peakPositionW = getObjFromFile(filename, "WPosition")
    peakPositionW_charged = getObjFromFile(filename, "WPosition_charged")
    peakRatio = getObjFromFile(filename, "Ratio")
    peakRatio_charged = getObjFromFile(filename, "Ratio_charged")

    TopPeaks.append( (peakPositionTop, color, name) )
    TopPeaks_charged.append( (peakPositionTop_charged, color, name) )
    WPeaks.append( (peakPositionW, color, name) )
    WPeaks_charged.append( (peakPositionW_charged, color, name) )
    Ratios.append( (peakRatio, color, name) )
    Ratios_charged.append( (Ratios_charged, color, name) )

drawPeakPositionCompare(TopPeaks, plotdir+"TopPeaks", "top")
drawPeakPositionCompare(TopPeaks_charged, plotdir+"TopPeaks_charged", "top")
drawPeakPositionCompare(WPeaks, plotdir+"WPeaks", "W")
drawPeakPositionCompare(WPeaks_charged, plotdir+"WPeaks_charged", "W")


models = [
    (directory+"central/Results.root", directory+"EFFIREALISTIC/Results.root", "TopPosition", "WPosition", "Ratio_EffiRealistic"),
    (directory+"central/Results.root", directory+"EFFIREALISTIC/Results.root", "TopPosition_charged", "WPosition_charged", "Ratio_EffiRealistic_charged"),
    (directory+"central/Results.root", directory+"EFFIFLAT/Results.root", "TopPosition", "WPosition", "Ratio_EffiFlat"),
    (directory+"central/Results.root", directory+"EFFIFLAT/Results.root", "TopPosition_charged", "WPosition_charged", "Ratio_EffiFlat_charged"),
    (directory+"central/Results.root", directory+"EFFIREALISTICSCALE/Results.root", "TopPosition", "WPosition", "Ratio_EffiRealisticScale"),
    (directory+"central/Results.root", directory+"EFFIREALISTICSCALE/Results.root", "TopPosition_charged", "WPosition_charged", "Ratio_EffiRealisticScale_charged"),
    (directory+"central/Results.root", directory+"EFFIFLATSCALE/Results.root", "TopPosition", "WPosition", "Ratio_EffiFlatScale"),
    (directory+"central/Results.root", directory+"EFFIFLATSCALE/Results.root", "TopPosition_charged", "WPosition_charged", "Ratio_EffiFlatScale_charged"),

]

for (f_nominal, f_variation, topname, Wname, plotname) in models:
    peakPositionTop_nominal = getObjFromFile(f_nominal, topname)
    peakPositionW_nominal = getObjFromFile(f_nominal, Wname)
    peakPositionTop_var = getObjFromFile(f_variation, topname)
    peakPositionW_var = getObjFromFile(f_variation, Wname)
    uncert_top = extractUncertainty(peakPositionTop_nominal, peakPositionTop_var)
    uncert_W = extractUncertainty(peakPositionW_nominal, peakPositionW_var)
    peakPositionTop_nominal_tot = peakPositionTop_nominal.Clone()
    peakPositionW_nominal_tot = peakPositionW_nominal.Clone()
    peakPositionTop_nominal_tot = addUncert(peakPositionTop_nominal_tot, uncert_top)
    peakPositionW_nominal_tot = addUncert(peakPositionW_nominal_tot, uncert_W)
    ratio_stat = getRatio(peakPositionTop_nominal, peakPositionW_nominal)
    ratio_tot = getRatio(peakPositionTop_nominal_tot, peakPositionW_nominal_tot)
    drawRatio(ratio_stat, ratio_tot, plotdir+plotname)
