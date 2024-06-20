#!/usr/bin/env python

import os
import ROOT
from EEEC.Tools.user                              import plot_directory
from MyRootTools.plotter.Plotter                  import Plotter
import Analysis.Tools.syncer

ROOT.gROOT.SetBatch(ROOT.kTRUE)
plotdir = plot_directory+"/FitTest/"
if not os.path.exists( plotdir ): os.makedirs( plotdir )

parameters = [
    (440.81791, 8.78017),
    (-5695.129, 83.1038),
    (29076.374, 270.4464),
    (-73260.44, 289.3496),
    (91212.08, 144.6902),
    (-4496.172, 332.5908),
]

correlations = [1, -1, 1, -1, -1, 1]


function = ROOT.TF1("function", "[0]+[1]*x+[2]*x*x+[3]*x*x*x+[4]*x*x*x*x+[5]*x*x*x*x*x")
function2 = ROOT.TF1("function2", "[0]+[1]*x+[2]*x*x+[3]*x*x*x+[4]*x*x*x*x+[5]*x*x*x*x*x")

for i, (value, error) in enumerate(parameters):
    function.SetParameter( i, value)
    function2.SetParameter( i, value+correlations[i]*error)

c = ROOT.TCanvas("c", "c", 600, 600)
function.GetXaxis().SetRangeUser(0, 0.7)
function.Draw()
function2.SetLineColor(20)
function2.Draw("SAME")

c.Print(plotdir+"Fit.pdf")
