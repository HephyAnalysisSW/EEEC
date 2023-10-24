# Make 100000000 events = 500*200000 / 50*2000000 / 100*1000000 / 200*500000


# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist_lastTop.sh 100000 13000 172.5 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist_R10_lastTop.sh 100000 13000 172.5 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist_R15_lastTop.sh 100000 13000 172.5 80.4 200 1000 on on)


# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_herwig.sh 100000 13000 172.5 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_herwig.sh 100000 13000 172.5 80.4 200 1000 off on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_herwig.sh 1000000 13000 172.5 80.4 200 1000 off off)
#
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_herwig_R10.sh 100000 13000 172.5 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_herwig_R10.sh 100000 13000 172.5 80.4 200 1000 off on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_herwig_R10.sh 1000000 13000 172.5 80.4 200 1000 off off)
#
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_herwig_R15.sh 100000 13000 172.5 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_herwig_R15.sh 100000 13000 172.5 80.4 200 1000 off on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_herwig_R15.sh 1000000 13000 172.5 80.4 200 1000 off off)
#
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist.sh 100000 13000 172.5 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist.sh 100000 13000 172.5 80.4 200 1000 off on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist.sh 1000000 13000 172.5 80.4 200 1000 off off)
#
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist_R10.sh 100000 13000 172.5 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist_R10.sh 100000 13000 172.5 80.4 200 1000 off on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist_R10.sh 1000000 13000 172.5 80.4 200 1000 off off)
#
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist_R15.sh 100000 13000 172.5 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist_R15.sh 100000 13000 172.5 80.4 200 1000 off on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist_R15.sh 1000000 13000 172.5 80.4 200 1000 off off)

# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist_seed.sh 10000 13000 172.5 80.4 200 1000 on on)


###############################
# PAPER
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist.sh 100000 13000 172.5 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist.sh 100000 13000 170.0 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist.sh 100000 13000 175.0 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist.sh 100000 13000 172.5 79.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist.sh 100000 13000 172.5 81.4 200 1000 on on)
#
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist_R15.sh 100000 13000 172.5 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist.sh 100000 13000 172.5 80.4 200 1000 off on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist.sh 1000000 13000 172.5 80.4 200 1000 off off)

# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_herwig.sh 100000 13000 172.5 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_herwig.sh 100000 13000 172.5 80.4 200 1000 off on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_herwig.sh 1000000 13000 172.5 80.4 200 1000 off off)

# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_HLLHC.sh 54000 13000 172.5 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_Run3.sh 54000 13000 172.5 80.4 200 1000 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_Run2.sh 24850 13000 172.5 80.4 200 1000 on on)
