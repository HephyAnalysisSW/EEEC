from RootTools.core.standard import *

# from EEEC.samples.nanoTuples_Run2016_nanoAODv6_private_postProcessed import Run2016
# from EEEC.samples.nanoTuples_Run2017_nanoAODv6_private_postProcessed import Run2017
# from EEEC.samples.nanoTuples_Run2018_nanoAODv6_private_postProcessed import Run2018
#
#
# RunII      = Sample.combine( "RunII", [Run2016, Run2017, Run2018] )
# RunII.lumi = Run2016.lumi + Run2017.lumi + Run2018.lumi
#
# lumi_year  = {2016:Run2016.lumi, 2017:Run2017.lumi, 2018:Run2018.lumi}

import EEEC.samples.nanoTuples_UL2018_nanoAOD as UL2018


TTbar_1 = Sample.combine( "TTbar", [UL2018.TTbar_1],texName = "t#bar{t}")
TTbar_2 = Sample.combine( "TTbar", [UL2018.TTbar_2],texName = "t#bar{t}")
TTbar_3 = Sample.combine( "TTbar", [UL2018.TTbar_3],texName = "t#bar{t}")
