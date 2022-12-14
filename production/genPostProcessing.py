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

#RootTools
from RootTools.core.standard             import *

import fastjet
ak18 = fastjet.JetDefinition(fastjet.antikt_algorithm, 1.0, fastjet.E_scheme)

# Helpers
from EEEC.Tools.helpers import checkRootFile

# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',              action='store_true', help='Run only on a small subset of the data?')#, default = True)
argParser.add_argument('--input',              action='store',      help='input file')
argParser.add_argument('--overwrite',          action='store',      nargs='?', choices = ['none', 'all', 'target'], default = 'none', help='Overwrite?')#, default = True)
argParser.add_argument('--output',             action='store',      default='output')
args = argParser.parse_args()

# Logging
import EEEC.Tools.logger as _logger
logger  = _logger.get_logger(args.logLevel, logFile = None)

import RootTools.core.logger as _logger_rt
logger_rt = _logger_rt.get_logger(args.logLevel, logFile = None )


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

extra_variables = []

products = {
#    'lhe':{'type':'LHEEventProduct', 'label':("externalLHEProducer")},
#    'gen':{'type':'GenEventInfoProduct', 'label':'generator'},
    'gp':{'type':'vector<reco::GenParticle>', 'label':("genParticles")},
#    'genJets':{'type':'vector<reco::GenJet>', 'label':("ak4GenJets")},
#    'genMET':{'type':'vector<reco::GenMET>',  'label':("genMetTrue")},
}

#def varnames( vec_vars ):
#    return [v.split('/')[0] for v in vec_vars.split(',')]
#
#def vecSumPt(*args):
#    return sqrt( sum([o['pt']*cos(o['phi']) for o in args],0.)**2 + sum([o['pt']*sin(o['phi']) for o in args],0.)**2 )
#
#def addIndex( collection ):
#    for i  in range(len(collection)):
#        collection[i]['index'] = i

# variables
variables = ["test/F"]

# jet vector

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
maker = TreeMaker(
    #sequence  = [ filler ],
    variables = [ TreeVariable.fromString(x) for x in variables ] + extra_variables,
    treeName = "Events"
    )

tmp_dir.cd()

def make_pseudoJet( obj ):
    return fastjet.PseudoJet( obj.px(), obj.py(), obj.pz(), obj.energy() )

gRandom = ROOT.TRandom3()
def filler( event ):

    if reader.position % 100==0: logger.info("At event %i/%i", reader.position, reader.nEvents)

    # All gen particles
    gp        = reader.products['gp']

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

    maker.fill()
    maker.event.init()

counter = 0
reader.start()
maker.start()

while reader.run( ):

    filler( maker.event )
    counter += 1
    if counter == maxEvents:  break

    #showered   = [p for p in reader.products['gp'] if abs(p.status())>=51 and abs(p.status())<80]
    particles = [p for p in reader.products['gp'] if p.numberOfDaughters()==0]

    clustSeq      = fastjet.ClusterSequence( map( make_pseudoJet, particles ), ak18 )
    sortedJets    = fastjet.sorted_by_pt(clustSeq.inclusive_jets())

    for jet in sortedJets:
        print "AK18 jet: pt %3.2f constituents %i"% (jet.pt(), len(jet.constituents()) )

logger.info( "Done with running over %i events.", reader.nEvents )

output_file.cd()
maker.tree.Write()
output_file.Close()

logger.info( "Written output file %s", output_filename )
