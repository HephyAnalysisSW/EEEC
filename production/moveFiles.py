import os
import glob
import datetime



def files_before(files, min):
    lower_time_bound = datetime.datetime.now() - datetime.timedelta(minutes=min)
    return filter(lambda f: datetime.datetime.fromtimestamp(os.path.getmtime(f)) < lower_time_bound, files)



jpgFilenamesList = glob.glob('145592*.jpg')
path = "/groups/hephy/cms/dennis.schwarz/EEEC/output/"

dirs = {
    "EEEC_PP_13000_1700_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2":          "output_13000_170.0_80.4_HARDPT200to1000_MPIon_HADon_R12_NEWHIST_",
    "EEEC_PP_13000_1725_794_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2":          "output_13000_172.5_79.4_HARDPT200to1000_MPIon_HADon_R12_NEWHIST_",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIoff_HADoff_R12_HERWIG_NEWHISTv2": "output_13000_172.5_80.4_HARDPT200to1000_MPIoff_HADoff_R12_HERWIG_NEWHIST_",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIoff_HADoff_R12_NEWHISTv2":        "output_13000_172.5_80.4_HARDPT200to1000_MPIoff_HADoff_R12_NEWHIST_",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIoff_HADon_R12_HERWIG_NEWHISTv2":  "output_13000_172.5_80.4_HARDPT200to1000_MPIoff_HADon_R12_HERWIG_NEWHIST_",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIoff_HADon_R12_NEWHISTv2":         "output_13000_172.5_80.4_HARDPT200to1000_MPIoff_HADon_R12_NEWHIST_",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_HERWIG_NEWHISTv2":   "output_13000_172.5_80.4_HARDPT200to1000_MPIon_HADon_R12_HERWIG_NEWHIST_",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2":          "output_13000_172.5_80.4_HARDPT200to1000_MPIon_HADon_R12_NEWHIST_" ,
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_HLLHC":    "output_13000_172.5_80.4_HARDPT200to1000_MPIon_HADon_R12_NEWHIST_HLLHC_",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_Run2":     "output_13000_172.5_80.4_HARDPT200to1000_MPIon_HADon_R12_NEWHIST_Run2_",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2_Run3":     "output_13000_172.5_80.4_HARDPT200to1000_MPIon_HADon_R12_NEWHIST_Run3_",
    "EEEC_PP_13000_1725_804_HARDPT200to1000_MPIon_HADon_R15_NEWHISTv2":          "output_13000_172.5_80.4_HARDPT200to1000_MPIon_HADon_R15_NEWHIST_",
    "EEEC_PP_13000_1725_814_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2":          "output_13000_172.5_81.4_HARDPT200to1000_MPIon_HADon_R12_NEWHIST_",
    "EEEC_PP_13000_1750_804_HARDPT200to1000_MPIon_HADon_R12_NEWHISTv2":          "output_13000_175.0_80.4_HARDPT200to1000_MPIon_HADon_R12_NEWHIST_",
}

suffix ="*.root"

for dir in dirs.keys():
    filename = dirs[dir]
    list_of_files = glob.glob(path+filename+suffix)
    Nfiles_before = len(list_of_files)
    filtered_list = files_before(list_of_files, 10.0)
    Nfiles = len(filtered_list)
    print dir, ", moving", Nfiles, "files..."
    for f in filtered_list:
        f_newpath = f.replace(path, path+"PAPER/"+dir+"/")
        # print f, f_newpath
        os.rename(f, f_newpath)
