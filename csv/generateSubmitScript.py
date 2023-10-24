files = [
    "EEEC_PP_13000_1700_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2",
    "EEEC_PP_13000_1725_794_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIoff_HADoff_R12_HERWIG_NEWHISTv2",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIoff_HADoff_R12_NEWHISTv2",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIoff_HADon_R12_HERWIG_NEWHISTv2",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIoff_HADon_R12_NEWHISTv2",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_HERWIG_NEWHISTv2",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_HLLHC",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_Run2",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_Run3",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R15_NEWHISTv2",
    "EEEC_PP_13000_1725_814_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2",
    "EEEC_PP_13000_1750_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2",
]

ptbins = [
    ("400","425"),
    ("425","450"),
    ("450","475"),
    ("475","500"),
    ("500","525"),
    ("525","550"),
    ("550","575"),
    ("575","600"),
    ("600","650"),
    ("650","700"),
    ("700","750"),
    ("750","800"),
]


f = open("convertRootToCSV_PAPER.sh", "w")

for file in files:
    for (ptmin, ptmax) in ptbins:
        line =  "python convertRootToCSV.py "
        line += "--file="+file+".root "
        line += "--ptmin="+ptmin+" "
        line += "--ptmax="+ptmax+" "
        line += "--mode=centers --round --doTwoPoint"
        line += "\n"
        f.write(line)
    f.write("\n")
f.close()
