# EEEC 

```
export SCRAM_ARCH=slc6_amd64_gcc700
cmsrel CMSSW_10_2_15_patch2
cd CMSSW_10_2_15_patch2/src
cmsenv
git cms-init
git clone git@github.com:HephyAnalysisSW/RootTools.git
git clone git@github.com:HephyAnalysisSW/EEEC.git
scram setup fastjet
scram setup fastjet-contrib
scram b -j40
```

# How to run production on CLIP-CBE
Produce 27 events at COM=1000 GeV with mT=172.5, mW=80.4 and hadronization turned on:
```
cd $CMSSW_BASE/src/EEEC/production
singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production.sh 27 1000 172.5 80.4 on)

```

Produce 27 pp events at COM=13 TeV  with mT=172.5, mW=80.4, MPI turned off and hadronization turned off:
```
cd $CMSSW_BASE/src/EEEC/production
singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 27 13000 172.5 80.4 off off)
```


# How to run production on lxplus
Produce 27 events at COM=1000 GeV with mT=172.5, mW=80.4 and hadronization turned on:
```
cd $CMSSW_BASE/src/EEEC/production
singularity run -B /afs -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:amd64 $(echo $(pwd)/production.sh test 100 1000 172.5 80.4 on)

```
