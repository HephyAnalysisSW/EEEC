import ROOT
import os
from EEEC.Tools.user            import plot_directory
from EEEC.Tools.trackEfficiency import getEfficiency, applyEfficiency
from RootTools.core.standard             import *
import Analysis.Tools.syncer
import random
import array as arr
import numpy as np

################################################################################
# Helper class to have a similar input
class GenPart:
    def __init__(self, pt, eta):
        self.pt_ = pt
        self.eta_ = eta

    def pt(self):
        return self.pt_

    def eta(self):
        return self.eta_
################################################################################

def setStyle(g):
    g.SetTitle(" ;p_{T} [GeV];Efficiency")
    g.GetXaxis().SetTitleOffset(1.2)

def getGrid(xmin, xmax, ymin, ymax):
    horizontal_lines = []
    vertical_lines = []
    for y in [0.2, 0.4, 0.6, 0.8, 1.0]:
        horizontal_lines.append(ROOT.TLine(xmin, y, xmax, y))
    for f in [0.1, 1, 10, 100]:
        for x_tmp in range(1, 10):
            x = f*x_tmp
            if x > xmin and x < xmax:
                vertical_lines.append(ROOT.TLine(x, ymin, x, ymax))

    lines = horizontal_lines+vertical_lines
    for l in lines:
        l.SetLineStyle(3)
    return lines


def generateParticles(Nparts):
    print "Generating %i particles" %(Nparts)
    particles = []
    for i in range(Nparts):
        r1 = random.uniform(0, 1)
        if r1 < 0.333:
            pt = random.uniform(0.1, 1.)
        elif r1 > 0.333 and r1 < 0.666:
            pt = random.uniform(1., 10.)
        else:
            pt = random.uniform(10., 100.)
        eta = random.uniform(-2.4, 2.4)
        p = GenPart(pt, eta)
        particles.append(p)
    return particles

def draw2D(hist, path, effi=False):
    c = ROOT.TCanvas("c", "c", 600, 600)
    ROOT.gPad.SetRightMargin(.2)
    ROOT.gPad.SetLeftMargin(.15)
    hist.SetTitle("")
    hist.GetXaxis().SetTitle("p_{T} [GeV]")
    hist.GetYaxis().SetTitle("#eta")
    hist.GetZaxis().SetTitle("Number of particles")
    if effi:
        hist.GetZaxis().SetTitle("Efficiency")
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetZaxis().SetTitleOffset(1.6)

    hist.Draw("COLZ")
    ROOT.gPad.SetLogx()
    c.Print(path)

################################################################################

ROOT.gROOT.SetBatch(ROOT.kTRUE)

plotdir = plot_directory+"/TrackEfficiencyModel/"
if not os.path.exists( plotdir ): os.makedirs( plotdir )

Npoints = 1000
ptmin = 0.1
ptmax = 100
step = (ptmax-ptmin)/Npoints
effi_barrel = ROOT.TGraph(Npoints)
effi_inter = ROOT.TGraph(Npoints)
effi_endcap = ROOT.TGraph(Npoints)
for i in range(Npoints):
    pt = ptmin+i*step
    effi_barrel.SetPoint(i, pt, getEfficiency(pt, 0.0))
    effi_inter.SetPoint(i, pt, getEfficiency(pt, 1.0))
    effi_endcap.SetPoint(i, pt, getEfficiency(pt, 2.0))


effi_barrel.SetMarkerStyle(20)
effi_inter.SetMarkerStyle(22)
effi_endcap.SetMarkerStyle(21)

effi_barrel.SetLineColor(ROOT.kBlack)
effi_inter.SetLineColor(ROOT.kBlue)
effi_endcap.SetLineColor(ROOT.kRed)

effi_barrel.SetLineWidth(2)
effi_inter.SetLineWidth(2)
effi_endcap.SetLineWidth(2)

dummy = ROOT.TGraph(2)
dummy.SetPoint(0, 0.1, 0.0)
dummy.SetPoint(1, 105, 1.01)
# dummy.SetMarkerColor(ROOT.kWhite)
dummy.SetMarkerSize(0.)

setStyle(dummy)
setStyle(effi_barrel)
setStyle(effi_inter)
setStyle(effi_endcap)

c = ROOT.TCanvas("c", "c", 600, 600)
ROOT.gPad.SetTopMargin(.02)
ROOT.gPad.SetBottomMargin(.1)

ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gStyle.SetOptStat(0)
dummy.Draw("AP")
effi_barrel.Draw("C SAME")
effi_inter.Draw("C SAME")
effi_endcap.Draw("C SAME")
ROOT.gPad.SetLogx()
ROOT.gPad.SetTicks(1, 1)

lines = getGrid(0.1, 105, 0, 1.1)
for l in lines:
    l.Draw("SAME")

leg = ROOT.TLegend(.4, .2, .8, .4)
leg.AddEntry(effi_barrel, "Barrel region (|#eta| < 0.9)", "l")
leg.AddEntry(effi_inter, "Transition region (0.9 < |#eta| < 1.4)", "l")
leg.AddEntry(effi_endcap, "Endcap region (|#eta| > 1.4)", "l")
leg.Draw()

c.Print(plotdir+"EfficiencyModel.pdf")


array_pt = arr.array('d',[0.1, 0.4, 0.7, 1.0, 10, 40, 100])
array_eta = arr.array('d', [-2.4, -1.4, -0.9, 0.9, 1.4, 2.3])
h_2D_before = ROOT.TH2F("h_2D_before", "h_2D_before", len(array_pt)-1, array_pt, len(array_eta)-1, array_eta)




particles = generateParticles(10000)
blist = []

for i,p in enumerate(particles):
    h_2D_before.Fill(p.pt(), p.eta())
    if p.pt() > 1 and p.pt() < 10 and abs(p.eta()) < 0.9:
        blist.append(i)

draw2D(h_2D_before, plotdir+"Before_2D.pdf")

modes = ["realistic", "realisticScale", "flat", "flatScale", "Bfrag", "BfragScale"]
for mode in modes:
    particles_before = list(particles)
    print "Running mode", mode
    h_2D_after = ROOT.TH2F("h_2D_after_"+mode, "h_2D_after_"+mode, len(array_pt)-1, array_pt, len(array_eta)-1, array_eta)
    particles_after = applyEfficiency(particles_before, mode, blist)

    for p in particles_after:
        h_2D_after.Fill(p.pt(), p.eta())


    h_2D_effi = h_2D_after.Clone("h_2D_effi_"+mode)
    h_2D_effi.Divide(h_2D_before)

    draw2D(h_2D_after, plotdir+"After_2D_"+mode+".pdf")
    draw2D(h_2D_effi, plotdir+"Efficiency_2D_"+mode+".pdf", effi=True)
