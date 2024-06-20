#!/bin/bash

export SCRAM_ARCH=slc6_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scram runtime -sh`

uuid=$(uuidgen)

export WORKDIR=/scratch-cbe/users/$USER/tmp/
mkdir -p $WORKDIR
export OUTPUTDIR=/groups/hephy/cms/$USER/EEEC/output/
mkdir -p $OUTPUTDIR

export PRODUCTION_TMP_FILE=$WORKDIR/$uuid.root

export POSTFIX=$uuid
export MAXEVENTS=$1
export COM=$2
export MT=$3
export MW=$4
export PTMIN=$5
export PTMAX=$6



# Run the cmsRun
#ipython -i $PWD/production.py || exit $? ;
cmsRun -e $PWD/production_pp_hardprocess.py || exit $? ;
python genPostProcessing_pp.py --input $PRODUCTION_TMP_FILE --output $OUTPUTDIR/output_${COM}_${MT}_${MW}_HARDPT${PTMIN}to${PTMAX}_HardProcess_$POSTFIX

rm $PRODUCTION_TMP_FILE
