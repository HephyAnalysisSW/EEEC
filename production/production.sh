#!/bin/bash

export SCRAM_ARCH=slc6_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scram runtime -sh`

# unique ID
export uuid=$(uuidgen)

export POSTFIX=$uuid
export MAXEVENTS=$1
export COM=$2
export MT=$3
export MW=$4


# Run the cmsRun
cmsRun -e $PWD/production.py || exit $? ;
python genPostProcessing.py --input production_$POSTFIX.root --output output_$POSTFIX 
