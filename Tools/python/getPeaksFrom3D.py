import ROOT
import array as arr
import numpy as np
import random
import string


def extractBinning(hist, axis):
    bins = []
    if axis == "X":
        Nbins = hist.GetXaxis().GetNbins()
        for i in range(Nbins):
            bin = i+1
            if i==0:
                bins.append(hist.GetXaxis().GetBinLowEdge(bin))
            bins.append(hist.GetXaxis().GetBinUpEdge(bin))
    elif axis == "Y":
        Nbins = hist.GetYaxis().GetNbins()
        for i in range(Nbins):
            bin = i+1
            if i==0:
                bins.append(hist.GetYaxis().GetBinLowEdge(bin))
            bins.append(hist.GetYaxis().GetBinUpEdge(bin))
    elif axis == "Z":
        Nbins = hist.GetZaxis().GetNbins()
        for i in range(Nbins):
            bin = i+1
            if i==0:
                bins.append(hist.GetZaxis().GetBinLowEdge(bin))
            bins.append(hist.GetZaxis().GetBinUpEdge(bin))
    return bins

def rescaleWplot(hist):
    hist_scale = hist.Clone(hist.GetName()+"_rescale")
    for i in range(hist.GetXaxis().GetNbins()):
        binX = i+1
        content = hist.GetBinContent(binX)
        error = hist.GetBinError(binX)
        center = hist.GetXaxis().GetBinCenter(binX)
        sf = pow(center, -0.25)
        hist_scale.SetBinContent(binX, content*sf)
        hist_scale.SetBinError(binX, error*sf)
    return hist_scale

def getTopPeak(h_3D, asymm_max, short_min):
    random_str = ''.join(random.choice(string.ascii_letters) for i in range(10))
    bins_1D = extractBinning(h_3D, "X")
    h_1D = ROOT.TH1D("h_top_"+random_str, "h_top", len(bins_1D)-1, arr.array('d', bins_1D))

    for i in range(h_3D.GetXaxis().GetNbins()):
        binX = i+1
        widthX = h_3D.GetXaxis().GetBinWidth(binX)
        content = 0
        error2 = 0
        for j in range(h_3D.GetYaxis().GetNbins()):
            binY = j+1
            for k in range(h_3D.GetZaxis().GetNbins()):
                binZ = k+1
                if h_3D.GetYaxis().GetBinUpEdge(binY) < asymm_max:
                    if h_3D.GetZaxis().GetBinLowEdge(binZ) > short_min:
                        content += h_3D.GetBinContent(binX, binY, binZ)
                        error2  += pow(h_3D.GetBinError(binX, binY, binZ), 2)
        h_1D.SetBinContent(binX, content/widthX)
        h_1D.SetBinError(binX, np.sqrt(error2)/widthX)
    return h_1D


def getWPeak(h_3D, h_twopoint, scale=True):
    bins_1D = extractBinning(h_3D, "X")
    h_1D = ROOT.TH1D("h_W", "h_W", len(bins_1D)-1, arr.array('d', bins_1D))

    for i in range(h_3D.GetXaxis().GetNbins()):
        binX = i+1
        widthX = h_3D.GetXaxis().GetBinWidth(binX)
        content = 0
        error2 = 0
        for j in range(h_3D.GetYaxis().GetNbins()):
            binY = j+1
            for k in range(h_3D.GetZaxis().GetNbins()):
                binZ = k+1
                content += h_3D.GetBinContent(binX, binY, binZ)
                error2  += pow(h_3D.GetBinError(binX, binY, binZ), 2)
        h_1D.SetBinContent(binX, content/widthX)
        h_1D.SetBinError(binX, np.sqrt(error2)/widthX)
        h_twopoint.SetBinContent(binX, h_twopoint.GetBinContent(binX)/widthX)
        h_twopoint.SetBinError(binX, h_twopoint.GetBinError(binX)/widthX)
    h_1D.Divide(h_twopoint)
    if scale:
        h_1D = rescaleWplot(h_1D)
    return h_1D
