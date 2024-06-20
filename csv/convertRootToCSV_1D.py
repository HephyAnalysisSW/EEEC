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

histnames_1D = [
    "EEEC1top", "EEEC1avg", "EEEC1long", "EEEC1medium", "EEC1", "EEC1mod",
    "EEEC1top_charged", "EEEC1avg_charged", "EEEC1long_charged", "EEEC1medium_charged", "EEC1_charged", "EEC1mod_charged",
    "pTjet",
]

for histname in histnames_1D:
    if args.ptmin is not None and args.ptmax is not None:
        if histname == "pTjet":
            histname = histname+"_ptjet"+args.ptmin+"to"+args.ptmax
        else:
            histname = histname+"_jetpt"+args.ptmin+"to"+args.ptmax
    print "Converting histogram", histname, "..."
    f_csv = open(args.file.replace(".root", "")+"_"+histname+'_bin'+args.mode+'.csv', 'w')
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
f_csv = open(args.file.replace(".root", "")+"_"+histname+'_bin'+args.mode+'.csv', 'w')
h_jetpT = getObjFromFile(filename, "pTjet_ptjet"+args.ptmin+"to"+args.ptmax)
writer = csv.writer(f_csv)
Nevents = h_jetpT.Integral()
row = [Nevents]
writer.writerow(row)
f_csv.close()
