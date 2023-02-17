# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: Configuration/GenProduction/python/EXO-RunIIFall18GS-02638-fragment.py --python_filename EXO-RunIIFall18GS-02638_1_cfg.py --eventcontent RECOSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN --fileout file:EXO-RunIIFall18GS-02638.root --conditions 102X_upgrade2018_realistic_v11 --beamspot Realistic25ns13TeVEarly2018Collision --customise_commands process.source.numberEventsInLuminosityBlock=cms.untracked.uint32(100) --step GEN --geometry DB:Extended --era Run2_2018 --no_exec --mc -n 219
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

process = cms.Process('GEN',eras.Run2_2018)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic25ns13TeVEarly2018Collision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

import os
maxEvents = int(os.environ["MAXEVENTS"])
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(maxEvents)
)

MT  = float(os.environ["MT"])
MW  = float(os.environ["MW"])
COM = float(os.environ["COM"])
HADSWITCH = str(os.environ["HADSWITCH"])
if os.environ.has_key('PRODUCTION_TMP_FILE'):
    PRODUCTION_TMP_FILE = os.environ['PRODUCTION_TMP_FILE']
else:
    PRODUCTION_TMP_FILE = "PRODUCTION_TMP_FILE.root"

print("Will process %i events for c.o.m %3.2f, mT = %3.2f, mW=%3.2f, Hadronization: %s"%(maxEvents, COM, MT, MW, HADSWITCH))
# Input source
process.source = cms.Source("EmptySource")

process.options = cms.untracked.PSet(

)

## Production Info
#process.configurationMetadata = cms.untracked.PSet(
#    annotation = cms.untracked.string('Configuration/GenProduction/python/EXO-RunIIFall18GS-02638-fragment.py nevts:219'),
#    name = cms.untracked.string('Applications'),
#    version = cms.untracked.string('$Revision: 1.19 $')
#)

# Output definition

process.RECOSIMoutput = cms.OutputModule("PoolOutputModule",
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('generation_step')
    ),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('file:'+PRODUCTION_TMP_FILE),
    outputCommands = process.RECOSIMEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

# Additional output definition

# Other statements
process.genstepfilter.triggerConditions=cms.vstring("generation_step")
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '102X_upgrade2018_realistic_v11', '')

process.load("Configuration.StandardSequences.SimulationRandomNumberGeneratorSeeds_cff")
process.RandomNumberGeneratorService.generator = process.RandomNumberGeneratorService.generator.clone()

import random
process.RandomNumberGeneratorService.generator.initialSeed = cms.untracked.uint32(random.randint(0,10**9))

process.generator = cms.EDFilter("Pythia8GeneratorFilter",
#process.generator = cms.EDFilter("Pythia8HadronizerFilter",
    PythiaParameters = cms.PSet(
        parameterSets = cms.vstring(
            'processParameters'
        ),
        processParameters = cms.vstring(
            #'Random:setSeed = on',
            #'Random:seed = on',
            'Beams:idA = 11',
            'Beams:idB = -11',
            'PDF:lepton = off',
            'Top:ffbar2ttbar(s:gmZ) = on',

            ### only hard process
            #'ProcessLevel:all = on',# parton level
            #'PartonLevel:all = off',#parton level

            ### hadronization 
            'HadronLevel:Hadronize = %s'%HADSWITCH,

            '6:m0 = %f'%MT,
            '6:mWidth = 1.43',
            '24:m0 = %f'%MW,
            '24:onMode = off',
            '24:onIfAny = 1 2 3 4 5',
        ),
    ),
    comEnergy = cms.double(COM),
    ElectronPositronInitialState = cms.untracked.bool(True),
    filterEfficiency = cms.untracked.double(1.0),
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    pythiaPylistVerbosity = cms.untracked.int32(1)
)


# Path and EndPath definitions
process.generation_step = cms.Path(process.pgen)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RECOSIMoutput_step = cms.EndPath(process.RECOSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.generation_step,process.genfiltersummary_step,process.endjob_step,process.RECOSIMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)
# filter all path with the production filter sequence
for path in process.paths:
	getattr(process,path)._seq = process.generator * getattr(process,path)._seq 

# customisation of the process.

# Automatic addition of the customisation function from Configuration.DataProcessing.Utils
from Configuration.DataProcessing.Utils import addMonitoring 

#call to customisation function addMonitoring imported from Configuration.DataProcessing.Utils
process = addMonitoring(process)

# End of customisation functions

# Customisation from command line

process.source.numberEventsInLuminosityBlock=cms.untracked.uint32(100)
# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
