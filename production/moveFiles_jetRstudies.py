import os
import glob
import datetime



def files_before(files, min):
    lower_time_bound = datetime.datetime.now() - datetime.timedelta(minutes=min)
    return filter(lambda f: datetime.datetime.fromtimestamp(os.path.getmtime(f)) < lower_time_bound, files)

path = "/groups/hephy/cms/dennis.schwarz/EEEC/output/"


####
# create dir list
dirs = {}
prefix_dir = "EEEC_PP_13000_1725_804_HARDPT200to1000_"
suffix_dir = "_NEWHISTv2"

prefix_file = "output_13000_172.5_80.4_HARDPT200to1000_"
suffix_file = "_NEWHIST_"

hadmodes = ["MPIon_HADon", "MPIoff_HADon", "MPIoff_HADoff"]
jetRadii = ["R10", "R12", "R15"]
generators = ["_HERWIG", "_LASTTOP", ""]

for gen in generators:
    for had in hadmodes:
        for jetR in jetRadii:
            dirname = prefix_dir+had+"_"+jetR+gen+suffix_dir
            filename = prefix_file+had+"_"+jetR+gen+suffix_file
            dirs[dirname] = filename
####

# print dirs


placeholder ="*.root"




for dir in dirs.keys():
    filename = dirs[dir]
    list_of_files = glob.glob(path+filename+placeholder)
    Nfiles_before = len(list_of_files)
    filtered_list = files_before(list_of_files, 10.0)
    Nfiles = len(filtered_list)
    print dir, ", moving", Nfiles, "files..."
    for f in filtered_list:
        f_newpath = f.replace(path, path+"JETRSTUDIES/"+dir+"/")
        # print f, f_newpath
        os.rename(f, f_newpath)
