import ROOT
import numpy as np
import copy

location = "/groups/hephy/cms/dennis.schwarz/www/EEEC/DataGenerator/"

f_gen_sim = location+"GenParticles_SIM.npz"
f_gen_dat = location+"GenParticles_DAT.npz"
f_rec_sim = location+"RecParticles_SIM.npz"
f_rec_dat = location+"RecParticles_DAT.npz"




histograms = {
    "pt": ROOT.TH1F("pt", "pt", 100, 0, 200),
    "Nparts": ROOT.TH1F("Nparts", "Nparts", 101, -0.5, 100.5),
}

outname = location+"Histograms.root"
f_histograms = ROOT.TFile(outname, "RECREATE")
for file in [f_gen_sim,f_gen_dat,f_rec_sim,f_rec_dat]:
    hist = copy.deepcopy(histograms)
    npfile = np.load(file)
    npdata = npfile['array1']
    Nevent = len(npdata)
    print "Reading", file, "(",Nevent, "events)"
    for i_evt in range(Nevent):
        Nparticles = len(npdata[i_evt])
        hist["Nparts"].Fill(Nparticles)
        for i_part in range(Nparticles):
            px = npdata[i_evt][i_part][0]
            py = npdata[i_evt][i_part][1]
            pz = npdata[i_evt][i_part][2]
            mass = npdata[i_evt][i_part][3]
            hist["pt"].Fill(np.sqrt(px*px+py*py))
    npfile.close()
    for histname in hist.keys():
        f_histograms.cd()
        writename = histname+"_"+file.replace(location,"").replace(".npz","")
        hist[histname].Write(writename)
        print "  - Wrote histogram", writename

f_histograms.Close()
print "Stored histograms in", outname
