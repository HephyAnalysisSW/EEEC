#!/usr/bin/env python

import os
import ROOT
import array as arr
from math                                         import sqrt
from EEEC.Tools.helpers                           import getObjFromFile
from EEEC.Tools.user                              import plot_directory
from MyRootTools.plotter.Plotter                  import Plotter
import Analysis.Tools.syncer



path = "/users/dennis.schwarz/CMSSW_10_2_15_patch2/src/EEEC/csv/"
prefix = "EEEC_PP_13000_1725_804_HARDPT200to1000_"

modes = ["MPIoff_HADoff", "MPIoff_HADon", "MPIon_HADon"]

plotdir = plot_directory+"/HERWIGvsPYTHIA/"
if not os.path.exists( plotdir ): os.makedirs( plotdir )


for mode in modes:
    histname = "Nconstituents_ptjet500to525"

    fname_pythia = path+prefix+mode+"_R12_NEWHISTv2.root"
    fname_herwig = path+prefix+mode+"_R12_HERWIG_NEWHISTv2.root"

    h_pythia = getObjFromFile(fname_pythia, histname)
    h_herwig = getObjFromFile(fname_herwig, histname)

    p = Plotter(histname+"_"+mode)
    p.plot_dir = plotdir
    p.xtitle = "Number of jet constituents"
    p.drawRatio = True
    p.ratiotitle = "#frac{HERWIG}{PYTHIA}"
    p.addBackground(h_pythia, "PYTHIA", 13)
    p.addSignal(h_herwig, "HERWIG", ROOT.kRed)
    p.draw()
