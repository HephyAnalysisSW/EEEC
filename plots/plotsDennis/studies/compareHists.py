#!/usr/bin/env python
import ROOT, os
import csv
import array as arr

ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetOptStat(0)

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--file',           action='store',      default='output.root')

args = argParser.parse_args()

# This function is a copy from the HEPHY framework
def getObjFromFile(fname, hname):
    f = ROOT.TFile(fname)
    assert not f.IsZombie()
    f.cd()
    htmp = f.Get(hname)
    if not htmp:  return htmp
    ROOT.gDirectory.cd('PyROOT:/')
    res = htmp.Clone()
    f.Close()
    return res

def project3Dto1D(h3D, axis):
    NbinsX = h3D.GetXaxis().GetNbins()
    NbinsY = h3D.GetYaxis().GetNbins()
    NbinsZ = h3D.GetZaxis().GetNbins()
    if axis == "x":
        bins = []
        bins.append(h3D.GetXaxis().GetBinLowEdge(1))
        for i in range(NbinsX):
            bins.append(h3D.GetXaxis().GetBinUpEdge(i+1))
        print "New hist has", NbinsX, "bins"
        array_bins = arr.array('d', bins)
        h1D = ROOT.TH1D("hist", "hist", NbinsX, array_bins)
        for i in range(NbinsX):
            binX = i+1
            content = 0
            for j in range(NbinsY):
                binY = j+1
                for k in range(NbinsZ):
                    binZ = k+1
                    content += h3D.GetBinContent(binX, binY, binZ)
            binwidth = h3D.GetXaxis().GetBinWidth(binX)
            h1D.SetBinContent(binX, content/binwidth)
    elif axis == "y":
        bins = []
        bins.append(h3D.GetYaxis().GetBinLowEdge(1))
        for i in range(NbinsY):
            bins.append(h3D.GetYaxis().GetBinUpEdge(i+1))
        array_bins = arr.array('d', bins)
        print "New hist has", NbinsY, "bins"
        h1D = ROOT.TH1D("hist", "hist", NbinsY, array_bins)
        for j in range(NbinsY):
            binY = j+1
            content = 0
            for i in range(NbinsX):
                binX = i+1
                for k in range(NbinsZ):
                    binZ = k+1
                    content += h3D.GetBinContent(binX, binY, binZ)
            binwidth = h3D.GetYaxis().GetBinWidth(binY)
            h1D.SetBinContent(binY, content/binwidth)
    elif axis == "z":
        bins = []
        bins.append(h3D.GetZaxis().GetBinLowEdge(1))
        for i in range(NbinsZ):
            bins.append(h3D.GetZaxis().GetBinUpEdge(i+1))
        array_bins = arr.array('d', bins)
        print "New hist has", NbinsZ, "bins"
        h1D = ROOT.TH1D("hist", "hist", NbinsZ, array_bins)
        for k in range(NbinsZ):
            binZ = k+1
            content = 0
            for i in range(NbinsX):
                binX = i+1
                for j in range(NbinsY):
                    binY = j+1
                    content += h3D.GetBinContent(binX, binY, binZ)
            binwidth = h3D.GetZaxis().GetBinWidth(binZ)
            h1D.SetBinContent(binZ, content/binwidth)
    else:
        print "AXIS", axis, "NOT DEFINED"
    return h1D


f1 = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/EEEC_PP_13000_1725_804_HARDPT300to900_MPIon_HADon_NEWHIST.root"
f2 = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/EEEC_PP_13000_1725_804_HARDPT300to900_MPIon_HADon_TESTRUN.root"


h_old_3D = getObjFromFile(f1, "EEEC1_jetpt500to525")
h_new_3D = getObjFromFile(f2, "EEEC1_jetpt500to525")

h_old = project3Dto1D(h_old_3D, "x")
h_new = project3Dto1D(h_new_3D, "x")


c = ROOT.TCanvas("c", "c", 600, 600)
ROOT.gPad.SetRightMargin(0.2)
h_old.GetYaxis().SetRangeUser(0, 300000)
h_old.SetLineColor(ROOT.kGreen)
h_new.SetLineColor(ROOT.kBlue)
h_old.Draw("HIST")
# h_new.Draw("HIST SAME")

c.Print("/groups/hephy/cms/dennis.schwarz/EEEC1_compare.pdf")
