#!/usr/bin/env python
''' Make flat ntuple from GEN data tier 
'''
#
# Standard imports and batch mode
#
import ROOT
import os, sys
ROOT.gROOT.SetBatch(True)
import imp
import time

#RootTools
from RootTools.core.standard             import *

# Fastjet
import fastjet


# Helpers
from EEEC.Tools.helpers import checkRootFile, deltaRGenparts

# Energy Correlators
from EEEC.Tools.energyCorrelators import getTriplets

# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',              action='store_true', help='Run only on a small subset of the data?')#, default = True)
argParser.add_argument('--input',              action='store',      help='input file')
argParser.add_argument('--overwrite',          action='store',      nargs='?', choices = ['none', 'all', 'target'], default = 'none', help='Overwrite?')#, default = True)
argParser.add_argument('--output',             action='store',      default='output')
argParser.add_argument('--jetR',               action='store',      default=1.5)

args = argParser.parse_args()

# Logging
import EEEC.Tools.logger as _logger
logger  = _logger.get_logger(args.logLevel, logFile = None)

import RootTools.core.logger as _logger_rt
logger_rt = _logger_rt.get_logger(args.logLevel, logFile = None )

akjet = fastjet.JetDefinition(fastjet.antikt_algorithm, args.jetR, fastjet.E_scheme)

sample = FWLiteSample( "output", args.input)

maxEvents = -1
if args.small: 
    args.output    += "_small"
    maxEvents       = 500 

# output directory
output_directory = os.path.join(".") 

if not os.path.exists( output_directory ): 
    try:
        os.makedirs( output_directory )
    except OSError:
        pass
    logger.info( "Created output directory %s", output_directory )

products = {
#    'lhe':{'type':'LHEEventProduct', 'label':("externalLHEProducer")},
#    'gen':{'type':'GenEventInfoProduct', 'label':'generator'},
    'gp':{'type':'vector<reco::GenParticle>', 'label':("genParticles")},
#    'genJets':{'type':'vector<reco::GenJet>', 'label':("ak4GenJets")},
#    'genMET':{'type':'vector<reco::GenMET>',  'label':("genMetTrue")},
}

def fill_vector_collection( event, collection_name, collection_varnames, objects):
    setattr( event, "n"+collection_name, len(objects) )
    for i_obj, obj in enumerate(objects):
        for var in collection_varnames:
            getattr(event, collection_name+"_"+var)[i_obj] = obj[var]
def fill_vector( event, collection_name, collection_varnames, obj):
    for var in collection_varnames:
        try:
            setattr(event, collection_name+"_"+var, obj[var] )
        except TypeError as e:
            logger.error( "collection_name %s var %s obj[var] %r", collection_name, var,  obj[var] )
            raise e
        except KeyError as e:
            logger.error( "collection_name %s var %s obj[var] %r", collection_name, var,  obj[var] )
            raise e

# FWLite reader if this is an EDM file
reader = sample.fwliteReader( products = products )

#def addTLorentzVector( p_dict ):
#    ''' add a TLorentz 4D Vector for further calculations
#    '''
#    p_dict['vecP4'] = ROOT.TLorentzVector( p_dict['pt']*cos(p_dict['phi']), p_dict['pt']*sin(p_dict['phi']),  p_dict['pt']*sinh(p_dict['eta']), p_dict['pt']*cosh(p_dict['eta']) )

tmp_dir     = ROOT.gDirectory
output_filename =  os.path.join(output_directory, sample.name + '.root')

if os.path.exists( output_filename ) and checkRootFile( output_filename, checkForObjects=["Events"]) and args.overwrite =='none' :
    logger.info( "File %s found. Quit.", output_filename )
    sys.exit(0)

output_file = ROOT.TFile( output_filename, 'recreate')
output_file.cd()

tmp_dir.cd()

def make_pseudoJet( obj ):
    return fastjet.PseudoJet( obj.px(), obj.py(), obj.pz(), obj.energy() )

gRandom = ROOT.TRandom3()

counter = 0
reader.start()

Nbins = 20
min_zeta = 0
max_zeta = 2*args.jetR+0.2

h_correlator1 = ROOT.TH3F("EEEC1", "EEEC1", Nbins, min_zeta, max_zeta, Nbins, min_zeta, max_zeta, Nbins, min_zeta, max_zeta)
h_correlator2 = ROOT.TH3F("EEEC2", "EEEC2", Nbins, min_zeta, max_zeta, Nbins, min_zeta, max_zeta, Nbins, min_zeta, max_zeta)
h_mindR_top_jet = ROOT.TH1F("mindR_top_jet", "min[#Delta R(top, jet)]", 10, 0, 5)
h_mjet = ROOT.TH1F("m_jet", "m_{jet}", 30, 0, 300)
h_Nconstituents = ROOT.TH1F("Nconstituents", "Nconstituents", 20, 0, 100)

timediffs = []

while reader.run( ):

    t_start = time.time()

    if reader.position % 100==0: logger.info("At event %i/%i", reader.position, reader.nEvents)
    # All gen particles
    #gp        = reader.products['gp']
    # for searching
    #search  = GenSearch( gp )

    # LHE Zs (Suman's example: https://github.com/Sumantifr/XtoYH/blob/master/Analysis/NTuplizer/plugins/NTuplizer_XYH.cc#L1973-L1992 )
    #hepup = reader.products['lhe'].hepeup()
    #lhe_particles = hepup.PUP
    #for i_p, p in enumerate(lhe_particles):
    #    if abs(hepup.IDUP[i_p])!=24: continue
    #    p4 = ROOT.TLorentzVector(lhe_particles[i_p][0], lhe_particles[i_p][1], lhe_particles[i_p][2], lhe_particles[i_p][3])
    #    print "Found!"
    #    #event.LHE_genZ_pt  = p4.Pt()
    #    #event.LHE_genZ_eta = p4.Eta()
    #    #event.LHE_genZ_phi  = p4.Phi()
    #    #event.LHE_genZ_mass = p4.M()
    #    break

    counter +=1
    if counter == maxEvents:  break

    # Find incoming particles and top quarks
    top = None
    antitop = None
    initial1 = None
    initial2 = None
    hard_scatter = [p for p in reader.products['gp'] if p.status() in [21,22] ] 
    for i, p in enumerate(hard_scatter):
        if p.pdgId() == 6:
            top = p 
        elif p.pdgId() == -6:
            antitop = p
        elif p.pdgId() == 11:
            initial1 = p
        elif p.pdgId() == -11:
            initial2 = p
        # print i, "pdgId = %i, status = %i" %(p.pdgId(), p.status())

    if top is None or antitop is None:
        print "Did not find 2 top quarks, skip this event..."
        continue

    if initial1 is None or initial2 is None:
        print "Did not find 2 incoming partons, skip this event..."
        continue
    
    # Get parton level/particle level/hadron level particles 
    
    #showered   = [p for p in reader.products['gp'] if abs(p.status())>=51 and abs(p.status())<80]
    particles = [p for p in reader.products['gp'] if p.numberOfDaughters()==0]

    clustSeq      = fastjet.ClusterSequence( map( make_pseudoJet, particles ), akjet )
    sortedJets    = fastjet.sorted_by_pt(clustSeq.inclusive_jets())

    # Find the jets that overlap with the tops
    jet_top         = None
    jet_antitop     = None
    dRmin_top       = args.jetR
    dRmin_antitop   = args.jetR
    
    for jet in sortedJets:
        if deltaRGenparts(jet, top) < dRmin_top:
            dRmin_top   = deltaRGenparts(jet, top)
            jet_top     = jet
        if deltaRGenparts(jet, antitop) < dRmin_antitop:
            dRmin_antitop = deltaRGenparts(jet, antitop)
            jet_antitop   = jet
    
    minpT = 300 # Set some minimal jet pT to ensure boosted tops that are within a single jet

    # top quark
    triplets_top = []
    scale = (initial1.p4()+initial2.p4()).M()
    if jet_top is not None:
        if jet_top.pt() > minpT:
            # Get triplets
            triplets_top = getTriplets(scale, jet_top.constituents(), n=1, max_zeta=max_zeta, max_delta_zeta=None, delta_legs=None, shortest_side=None)
            # Fill jet hists
            h_mindR_top_jet.Fill(dRmin_top)
            h_mjet.Fill(jet_top.m())
            h_Nconstituents.Fill(len(jet_top.constituents()))

    # anti top quark
    triplets_antitop = []
    if jet_antitop is not None:
        if jet_antitop.pt() > minpT:
            # Get triplets
            triplets_antitop = getTriplets(scale, jet_antitop.constituents(), n=1, max_zeta=max_zeta, max_delta_zeta=None, delta_legs=None, shortest_side=None)
            # Fill jet hists
            h_mindR_top_jet.Fill(dRmin_antitop)
            h_mjet.Fill(jet_antitop.m())
            h_Nconstituents.Fill(len(jet_antitop.constituents()))            

    # Fill correlator histogram    
    for (dR1, dR2, dR3, weight) in triplets_top+triplets_antitop:
        h_correlator1.Fill(dR1, dR2, dR3, weight)     # N=1
        h_correlator2.Fill(dR1, dR2, dR3, weight**2)  # N=2
        
    
    timediffs.append(time.time() - t_start)

logger.info( "Done with running over %i events.", reader.nEvents )
logger.info( "  Took %3.2f seconds per event (average)", sum(timediffs)/len(timediffs) )

output_file.cd()
h_correlator1.Write()
h_correlator2.Write()
h_mindR_top_jet.Write()
h_mjet.Write()
h_Nconstituents.Write()
output_file.Close()

logger.info( "Written output file %s", output_filename )
