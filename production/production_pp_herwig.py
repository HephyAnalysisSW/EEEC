# Auto generated configuration file
# using:
# Revision: 1.19
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v
# with command line options: Configuration/GenProduction/python/EXO-RunIIFall18GS-02638-fragment.py --python_filename EXO-RunIIFall18GS-02638_1_cfg.py --eventcontent RECOSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN --fileout file:EXO-RunIIFall18GS-02638.root --conditions 102X_upgrade2018_realistic_v11 --beamspot Realistic25ns13TeVEarly2018Collision --customise_commands process.source.numberEventsInLuminosityBlock=cms.untracked.uint32(100) --step GEN --geometry DB:Extended --era Run2_2018 --no_exec --mc -n 219
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

from Configuration.Generator.Herwig7Settings.Herwig7CH3TuneSettings_cfi import herwig7CH3SettingsBlock
from Configuration.Generator.Herwig7Settings.Herwig7StableParticlesForDetector_cfi import *
# from Configuration.Generator.Herwig7Settings.Herwig7_7p1SettingsFor7p2_cfi import *

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
MPISWITCH = str(os.environ["MPISWITCH"])
PTMIN = float(os.environ["PTMIN"])
PTMAX = float(os.environ["PTMAX"])
POSTFIX = str(os.environ["POSTFIX"])

had_string = '' if 'on' in HADSWITCH else 'set EventHandler:HadronizationHandler NULL'
mpi_string = '' if 'on' in MPISWITCH else 'set EventHandler:CascadeHandler:MPIHandler NULL'

if os.environ.has_key('PRODUCTION_TMP_FILE'):
    PRODUCTION_TMP_FILE = os.environ['PRODUCTION_TMP_FILE']
else:
    PRODUCTION_TMP_FILE = "PRODUCTION_TMP_FILE.root"

print("Will process %i pp events for c.o.m %3.2f, mT = %3.2f, mW=%3.2f, %3.2f < pT < %3.2f, MPI: %s, Hadronization: %s"%(maxEvents, COM, MT, MW, PTMIN, PTMAX, MPISWITCH, HADSWITCH))
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

#############################################
process.generator = cms.EDFilter("Herwig7GeneratorFilter",
    herwig7CH3SettingsBlock,
    herwig7StableParticlesForDetectorBlock,
    # herwig7p1SettingsFor7p2Block,
    productionParameters = cms.vstring(
        'read snippets/PPCollider.in',
        'cd /Herwig/MatrixElements/',
        'insert SubProcess:MatrixElements[0] MEHeavyQuark',
        'do /Herwig/Particles/t:SelectDecayModes t->b,bbar,c; t->b,u,dbar; t->b,c,dbar; t->b,sbar,u; t->b,c,sbar;',
        'cd /',
        'insert /Herwig/Cuts/Cuts:OneCuts 0 /Herwig/Cuts/TopQuarkCut',
        'set /Herwig/Cuts/TopQuarkCut:PtMin %s*GeV'%PTMIN,
        'set /Herwig/Cuts/TopQuarkCut:PtMax %s*GeV'%PTMAX,
        'set /Herwig/EventHandlers/Luminosity:Energy %s'%COM,
        'set /Herwig/Particles/t:NominalMass %s*GeV'%MT,
        'set /Herwig/Particles/t:HardProcessMass %s*GeV'%MT,
        'set /Herwig/Particles/tbar:NominalMass %s*GeV'%MT,
        'set /Herwig/Particles/tbar:HardProcessMass %s*GeV'%MT,
        'set /Herwig/Particles/W+:NominalMass %s*GeV'%MW,
        'set /Herwig/Particles/W+:HardProcessMass %s*GeV'%MW,
        'set /Herwig/Particles/W-:NominalMass %s*GeV'%MW,
        'set /Herwig/Particles/W-:HardProcessMass %s*GeV'%MW,
        'do /Herwig/Particles/t:PrintDecayModes',
        'do /Herwig/Particles/tbar:PrintDecayModes',
        'cd /Herwig/EventHandlers',
        had_string,
        mpi_string,
        'cd /',

    ),
    parameterSets = cms.vstring('productionParameters',
                                'herwig7CH3PDF',
                                'herwig7CH3AlphaS',
                                'herwig7CH3MPISettings',
                                'herwig7StableParticlesForDetector'),
                                # 'hw_7p1SettingsFor7p2'),
    configFiles = cms.vstring(),
    crossSection = cms.untracked.double(1363000000),
    dataLocation = cms.string('${HERWIGPATH:-6}'),
    eventHandlers = cms.string('/Herwig/EventHandlers'),
    filterEfficiency = cms.untracked.double(1.0),
    generatorModule = cms.string('/Herwig/Generators/EventGenerator'),
    repository = cms.string('${HERWIGPATH}/HerwigDefaults.rpo'),
    run = cms.string('InterfaceMatchboxTest_'+POSTFIX),
    runModeList = cms.untracked.string("read,run"),
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
