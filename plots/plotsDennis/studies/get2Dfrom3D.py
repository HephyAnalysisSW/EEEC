#!/usr/bin/env python
import ROOT, os
import csv

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

def project3Dto2D(h3D, h2D_dummy):
    NbinsX = h3D.GetXaxis().GetNbins()
    NbinsY = h3D.GetYaxis().GetNbins()
    NbinsZ = h3D.GetZaxis().GetNbins()
    h2D = h2D_dummy.Clone(h3D.GetName()+"_projection")
    h2D.Reset()
    h2D.SetTitle(h3D.GetTitle()+"_projection")
    for i in range(NbinsX):
        binX = i+1
        for k in range(NbinsZ):
            binZ = k+1
            content = 0
            for j in range(NbinsY):
                binY = j+1
                content += h3D.GetBinContent(binX, binY, binZ)
            h2D.SetBinContent(binZ, binX, content)
    return h2D

def draw2D(hist, name):
    c = ROOT.TCanvas("c", "c", 600, 600)
    ROOT.gPad.SetRightMargin(0.2)
    hist.GetXaxis().SetRangeUser(0.1, 0.6)
    hist.GetYaxis().SetRangeUser(0.1, 0.6)

    hist.Draw("COLZ")
    c.Print("/groups/hephy/cms/dennis.schwarz/"+name+".pdf")

def compareBins(h1, h2):
    NbinsX = h1.GetXaxis().GetNbins()
    NbinsY = h1.GetYaxis().GetNbins()
    for i in range(NbinsX):
        binX = i+1
        for j in range(NbinsY):
            binY = j+1
            print h1.GetBinContent(binX, binY), "=", h2.GetBinContent(binX, binY)

histname_2D = "2DEEEC1_jetpt500to525"
histname_3D = "EEEC1_jetpt500to525"

h_2D = getObjFromFile(args.file, histname_2D)
h_3D = getObjFromFile(args.file, histname_3D)

# print h_2D.GetXaxis().GetNbins(), h_3D.GetXaxis().GetNbins()

#
h_2D_from3D = project3Dto2D(h_3D, h_2D)

draw2D(h_2D_from3D, "2Dfrom3D")
draw2D(h_2D, "2D")
# h_2D_diff = h_2D_from3D.Clone()
# h_2D_diff.Add(h_2D, -1)
# draw2D(h_2D_diff, "2D_diff")
# h_2D_ratio = h_2D_from3D.Clone()
# h_2D_ratio.Divide(h_2D)
# draw2D(h_2D_ratio, "2D_ratio")

compareBins(h_2D, h_2D_from3D)
