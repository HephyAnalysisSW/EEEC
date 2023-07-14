# Make 100000000 events = 500*200000 / 50*2000000 / 100*1000000 / 200*500000

singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_newHist.sh 100 13000 172.5 80.4 300 900 on on)



# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_herwig.sh 100 13000 172.5 80.4 300 900 on on)


# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_log.sh 200000 13000 172.5 80.4 300 900 on on)


# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_PFstudies.sh 100000 13000 172.5 80.4 300 900 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_R08.sh 1000000 13000 172.5 80.4 300 900 off off)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_R12.sh 1000000 13000 172.5 80.4 300 900 off off)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_R08.sh 100000 13000 172.5 80.4 300 900 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp_R12.sh 100000 13000 172.5 80.4 300 900 on on)


# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 1000000 13000 172.5 80.4 300 900 off off)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 1000000 13000 169.5 80.4 300 900 off off)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 1000000 13000 171.5 80.4 300 900 off off)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 1000000 13000 173.5 80.4 300 900 off off)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 1000000 13000 175.5 80.4 300 900 off off)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 1000000 13000 182.5 80.4 300 900 off off)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 1000000 13000 172.5 77.4 300 900 off off)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 1000000 13000 172.5 79.4 300 900 off off)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 1000000 13000 172.5 81.4 300 900 off off)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 1000000 13000 172.5 83.4 300 900 off off)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 1000000 13000 172.5 85.4 300 900 off off)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 100000 13000 172.5 80.4 300 900 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 100000 13000 169.5 80.4 300 900 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 100000 13000 171.5 80.4 300 900 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 100000 13000 173.5 80.4 300 900 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 100000 13000 175.5 80.4 300 900 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 100000 13000 182.5 80.4 300 900 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 100000 13000 172.5 77.4 300 900 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 100000 13000 172.5 79.4 300 900 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 100000 13000 172.5 81.4 300 900 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 100000 13000 172.5 83.4 300 900 on on)
# singularity run -B /eos -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:x86_64 $(echo $(pwd)/production_pp.sh 100000 13000 172.5 85.4 300 900 on on)
