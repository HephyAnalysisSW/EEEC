#!/usr/bin/env python

import ROOT
import os, sys
ROOT.gROOT.SetBatch(True)
import numpy as np

#RootTools
from RootTools.core.standard             import *



# Helpers
from EEEC.Tools.helpers import make_TH3D



NbinsA = 100
NbinsB = 100
min_zeta = 0.0
interm_zeta = 0.15
max_zeta = 1.0

binsA = np.linspace(min_zeta, interm_zeta, NbinsA+1)
binsB = np.linspace(interm_zeta, max_zeta, NbinsB+1)
binsB = np.delete(binsB, 0) # remove first number because it is already part of "binsA"
binning = np.array([ np.append(binsA, binsB) for i in range(3)], dtype='d')

triplets_top = [(0.2, 0.1, 0.05)]
triplets_antitop = [(0.25, 0.15, 0.1)]
weights_top = [1]
weights_antitop = [1]

h_correlator1, (xedges, yedges, zedges) = np.histogramdd( np.concatenate((triplets_top, triplets_antitop)), binning, weights=np.concatenate((weights_top, weights_antitop)))

thrs1, thrs2, thrs3 = binning
print len(thrs1)-1
print thrs1


th3d_h_correlator1 = make_TH3D(h_correlator1, (xedges, yedges, zedges), sumw2=None)
for i in range(len(thrs1)-1):
    print th3d_h_correlator1.GetXaxis().GetBinWidth(i+1)
    print th3d_h_correlator1.GetYaxis().GetBinWidth(i+1)
    print th3d_h_correlator1.GetZaxis().GetBinWidth(i+1)

print "--------"

h_test = ROOT.TH1F("1", "1", 1, thrs1[0], 0.0015)
