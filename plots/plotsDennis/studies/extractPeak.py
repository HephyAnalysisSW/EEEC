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

logger.info( "Extract peaks of EEEC")

filedir = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/"
filename = "EEEC_PP_13000_MTOP_MW_HARDPT300to900_MPIon_HADon.root"
# ptbins = ["500to525", "525to550", "550to575", "575to600", "600to625", "625to650", "650to675", "675to700"]
ptbins = ["500to525"]

masses = ["1695", "1715", "1725", "1735", "1755", "1825"]
colors = {
    "1695": 99,
    "1715": 93,
    "1725": 1,
    "1735": 69,
    "1755": 64,
    "1825": 60,
}

for ptbin in ptbins:
    logger.info( "Jet pt bin = %s", ptbin)

    hists = {}
    hists_stat = {}

    for mtop in masses:
        hist3D = getObjFromFile(filedir+filename.replace("MTOP", mtop).replace("MW", "804"), "EEEC1_jetpt"+ptbin)
        logger.info( "Make 3D -> 1D projection for mtop = %s", mtop)
        hists[mtop] = project3Dto1D(hist3D, 0.003, 0.01, mtop+"_"+ptbin, mtop+"_"+ptbin)
        hists_stat[mtop] = hists[mtop].Clone(hists[mtop].GetName()+"_stat")

    logger.info( "Make plot" )

    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    ROOT.gStyle.SetLegendBorderSize(0)
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetOptStat(0)
    c = ROOT.TCanvas("eeec", "eeec", 600, 600)
    hists["1725"].SetTitle("")
    hists["1725"].GetXaxis().SetTitle("(#zeta_{max}+#zeta_{med})/2")
    hists["1725"].GetYaxis().SetTitle("Weighted triplets")
    hists["1725"].Draw("HIST")
    leg = ROOT.TLegend(.6, .6, .85, .85)

    for mtop in masses:
        hists[mtop].SetLineWidth(2)
        hists[mtop].SetLineColor(colors[mtop])
        hists_stat[mtop].SetFillColorAlpha(colors[mtop], 0.3)
        hists_stat[mtop].SetMarkerSize(0.0)
        # hists_stat[mtop].Draw("E3 SAME")
        hists[mtop].Draw("HIST SAME")
        leg.AddEntry(hists[mtop], "m_{t} = "+mtop[:-1]+".5 GeV", "l")
    leg.Draw()

    c.Print(plot_directory+"/EEEC_masses/EEEC_masses_jetpt"+ptbin+".pdf")
