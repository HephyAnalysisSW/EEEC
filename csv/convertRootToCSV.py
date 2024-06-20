#!/usr/bin/env python
import ROOT, os
import csv


import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--file',           action='store',      default='output.root')
argParser.add_argument('--ptmin',          action='store',      default=None)
argParser.add_argument('--ptmax',          action='store',      default=None)
argParser.add_argument('--mode',           action='store',      default='edges')
argParser.add_argument('--round',          action='store_true', default=False)
argParser.add_argument('--reduce',         action='store_true', default=False)
argParser.add_argument('--doTwoPoint',     action='store_true', default=False)
argParser.add_argument('--do2DEEEC',       action='store_true', default=False)

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

if args.mode not in ["edges", "centers", "numbers"]:
    raise RuntimeError( "mode %s not known", args.mode)

filename = args.file
# histnames = ["EEEC1", "EEEC2", "EEEC1charged", "EEEC2charged"]
histnames = ["EEEC1", "EEEC1charged"]

suffix = ""
if args.reduce:
    suffix = "_reduced"

# 3D Histograms
for histname in histnames:
    if args.ptmin is not None and args.ptmax is not None:
        histname = histname+"_jetpt"+args.ptmin+"to"+args.ptmax
    print "Converting histogram", histname, "..."
    f_csv = open(args.file.replace(".root", "")+"_"+histname+'_bin'+args.mode+suffix+'.csv', 'w')
    writer = csv.writer(f_csv)
    hist = getObjFromFile(filename, histname)
    NbinsX = hist.GetXaxis().GetNbins()
    NbinsY = hist.GetYaxis().GetNbins()
    NbinsZ = hist.GetZaxis().GetNbins()
    n_tenth = 1
    min_binX = 1
    for binX in range(min_binX, NbinsX+1):
        min_binY = binX if args.reduce else 1
        for binY in range(min_binY, NbinsY+1):
            min_binZ = binY if args.reduce else 1
            for binZ in range(min_binZ, NbinsZ+1):
                if args.reduce and binZ < binY: continue
                centerX = hist.GetXaxis().GetBinCenter(binX)
                centerY = hist.GetYaxis().GetBinCenter(binY)
                centerZ = hist.GetZaxis().GetBinCenter(binZ)
                widthX = hist.GetXaxis().GetBinWidth(binX)
                widthY = hist.GetYaxis().GetBinWidth(binY)
                widthZ = hist.GetZaxis().GetBinWidth(binZ)
                lowX = hist.GetXaxis().GetBinLowEdge(binX)
                lowY = hist.GetYaxis().GetBinLowEdge(binY)
                lowZ = hist.GetZaxis().GetBinLowEdge(binZ)
                upX = hist.GetXaxis().GetBinUpEdge(binX)
                upY = hist.GetYaxis().GetBinUpEdge(binY)
                upZ = hist.GetZaxis().GetBinUpEdge(binZ)
                content = hist.GetBinContent(binX, binY, binZ)
                error   = hist.GetBinError(binX, binY, binZ)
                if args.round:
                    centerX = round(centerX, 7)
                    centerY = round(centerY, 7)
                    centerZ = round(centerZ, 7)
                    widthX = round(widthX, 7)
                    widthY = round(widthY, 7)
                    widthZ = round(widthZ, 7)
                    lowX = round(lowX, 7)
                    lowY = round(lowY, 7)
                    lowZ = round(lowZ, 7)
                    upX = round(upX, 7)
                    upY = round(upY, 7)
                    upZ = round(upZ, 7)
                row = []
                if args.mode == "numbers":
                    row = [binX, binY, binZ, content, error]
                elif args.mode == "centers":
                    row = [centerX, centerY, centerZ, widthX, widthY, widthZ, content, error]
                elif args.mode == "edges":
                    row = [lowX, upX, lowY, upY, lowZ, upZ, content, error]
                else:
                    raise RuntimeError( "mode %s not known", args.mode)
                writer.writerow(row)
        if binX > n_tenth*NbinsX/10:
            print "%i percent of the bins converted"%(n_tenth*10)
            n_tenth+=1

    f_csv.close()
    print "Converting histogram", histname, "done."

# 2D Histograms
if args.do2DEEEC:
    # histnames_2D = ["2DEEEC1", "2DEEEC2", "2DEEEC1charged", "2DEEEC2charged"]
    histnames_2D = ["2DEEEC1", "2DEEEC1charged"]


    for histname in histnames_2D:
        if args.ptmin is not None and args.ptmax is not None:
            histname = histname+"_jetpt"+args.ptmin+"to"+args.ptmax
        print "Converting histogram", histname, "..."
        f_csv = open(args.file.replace(".root", "")+"_"+histname+'_bin'+args.mode+suffix+'.csv', 'w')
        writer = csv.writer(f_csv)
        hist = getObjFromFile(filename, histname)
        NbinsX = hist.GetXaxis().GetNbins()
        NbinsY = hist.GetYaxis().GetNbins()
        n_tenth = 1
        min_binX = 1
        min_binY = 1
        for binX in range(min_binX, NbinsX+1):
            for binY in range(min_binY, NbinsY+1):
                centerX = hist.GetXaxis().GetBinCenter(binX)
                centerY = hist.GetYaxis().GetBinCenter(binY)
                widthX = hist.GetXaxis().GetBinWidth(binX)
                widthY = hist.GetYaxis().GetBinWidth(binY)
                lowX = hist.GetXaxis().GetBinLowEdge(binX)
                lowY = hist.GetYaxis().GetBinLowEdge(binY)
                upX = hist.GetXaxis().GetBinUpEdge(binX)
                upY = hist.GetYaxis().GetBinUpEdge(binY)
                content = hist.GetBinContent(binX, binY)
                error   = hist.GetBinError(binX, binY)
                if args.round:
                    centerX = round(centerX, 7)
                    centerY = round(centerY, 7)
                    widthX = round(widthX, 7)
                    widthY = round(widthY, 7)
                    lowX = round(lowX, 7)
                    lowY = round(lowY, 7)
                    upX = round(upX, 7)
                    upY = round(upY, 7)
                row = []
                if args.mode == "numbers":
                    row = [binX, binY, content, error]
                elif args.mode == "centers":
                    row = [centerX, centerY, widthX, widthY, content, error]
                elif args.mode == "edges":
                    row = [lowX, upX, lowY, upY, content, error]
                else:
                    raise RuntimeError( "mode %s not known", args.mode)
                writer.writerow(row)
            if binX > n_tenth*NbinsX/10:
                print "%i percent of the bins converted"%(n_tenth*10)
                n_tenth+=1
        f_csv.close()
        print "Converting histogram", histname, "done."

# Two point Histograms
if args.doTwoPoint:
    # histnames_twoPoint = ["EEC1", "EEC2", "EEC1charged", "EEC2charged"]
    histnames_twoPoint = ["EEC1", "EEC1charged"]

    for histname in histnames_twoPoint:
        if args.ptmin is not None and args.ptmax is not None:
            histname = histname+"_jetpt"+args.ptmin+"to"+args.ptmax
        print "Converting histogram", histname, "..."
        f_csv = open(args.file.replace(".root", "")+"_"+histname+'_bin'+args.mode+suffix+'.csv', 'w')
        writer = csv.writer(f_csv)
        hist = getObjFromFile(filename, histname)
        NbinsX = hist.GetXaxis().GetNbins()
        n_tenth = 1
        min_binX = 1
        for binX in range(min_binX, NbinsX+1):
            centerX = hist.GetXaxis().GetBinCenter(binX)
            widthX = hist.GetXaxis().GetBinWidth(binX)
            lowX = hist.GetXaxis().GetBinLowEdge(binX)
            upX = hist.GetXaxis().GetBinUpEdge(binX)
            content = hist.GetBinContent(binX)
            error   = hist.GetBinError(binX)
            if args.round:
                centerX = round(centerX, 7)
                widthX = round(widthX, 7)
                lowX = round(lowX, 7)
                upX = round(upX, 7)
            row = []
            if args.mode == "numbers":
                row = [binX, content, error]
            elif args.mode == "centers":
                row = [centerX, widthX, content, error]
            elif args.mode == "edges":
                row = [lowX, upX, content, error]
            else:
                raise RuntimeError( "mode %s not known", args.mode)
            writer.writerow(row)
            if binX > n_tenth*NbinsX/10:
                print "%i percent of the bins converted"%(n_tenth*10)
                n_tenth+=1
        f_csv.close()
        print "Converting histogram", histname, "done."

# Store Nevents
# use jet pT hist to count events
histname = "Nevents"+"_jetpt"+args.ptmin+"to"+args.ptmax
f_csv = open(args.file.replace(".root", "")+"_"+histname+'_bin'+args.mode+suffix+'.csv', 'w')
h_jetpT = getObjFromFile(filename, "pTjet_ptjet"+args.ptmin+"to"+args.ptmax)
writer = csv.writer(f_csv)
Nevents = h_jetpT.Integral()
row = [Nevents]
writer.writerow(row)
f_csv.close()
