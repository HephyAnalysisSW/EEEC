import os

path = "/groups/hephy/cms/dennis.schwarz/EEEC/output/PAPER/"

dirs = {
    "EEEC_PP_13000_1700_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2": (1000),
    "EEEC_PP_13000_1725_794_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2": (1000),
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIoff_HADoff_R12_HERWIG_NEWHISTv2": (1000),
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIoff_HADoff_R12_NEWHISTv2": (1000),
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIoff_HADon_R12_HERWIG_NEWHISTv2": (1000),
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIoff_HADon_R12_NEWHISTv2": (1000),
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_HERWIG_NEWHISTv2": (1000),
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2": (1000),
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_HLLHC": (100),
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_Run2": (10),
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_Run3": (10),
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R15_NEWHISTv2": (1000),
    "EEEC_PP_13000_1725_814_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2": (1000),
    "EEEC_PP_13000_1750_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2": (1000),
}

Nfiles_tot = 0
Ndone_tot = 0

for dir in dirs.keys():
    (Nfiles) = dirs[dir]
    Nfiles_tot += Nfiles
    Ndone = len(os.listdir(path+dir))
    Ndone_tot += Ndone
    Nmissing = Nfiles-Ndone
    percent = 100.*Ndone/Nfiles
    missingstring = ""
    if percent < 100.:
        missingstring = " - %i missing"%(Nmissing)
    else:
        missingstring = " - Done."
    print dir, Ndone, "/", Nfiles, missingstring
percent_tot = 100.*Ndone_tot/Nfiles_tot
print "--------------------------"
print "Total:", Ndone_tot, "/", Nfiles_tot, "(%.2f percent done)"%percent_tot
