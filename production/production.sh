#!/bin/bash

export SCRAM_ARCH=slc6_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scram runtime -sh`

export POSTFIX=$1
export MAXEVENTS=$2
export COM=$3
export MT=$4
export MW=$5

# Run the cmsRun
cmsRun -e $PWD/production.py || exit $? ;
python genPostProcessing.py --input production_$POSTFIX.root 
