# -*- coding: utf-8 -*-

"""
Script to produce numpy arrays of triplet parameters.
"""

import numpy as np
from MTopCorrelations.samples.nanoTuples_UL_RunII_nanoAOD import UL2018
from MTopCorrelations.Tools.python.triplet_maker import Triplets
from MTopCorrelations.Tools.python.jet_constituents import JetConstituents
from ROOT import TLorentzVector, TNtuple, TFile
import argparse


def find_hadronic_jet(event):
    top_vec, anti_top_vec = TLorentzVector(), TLorentzVector()
    for i in range(event.nGenPart):
        if event.GenPart_pdgId[i] == 6:
            top_vec.SetPtEtaPhiM(event.GenPart_pt[i], event.GenPart_eta[i], event.GenPart_phi[i], event.GenPart_m[i])
        elif event.GenPart_pdgId[i] == -6:
            anti_top_vec.SetPtEtaPhiM(event.GenPart_pt[i], event.GenPart_eta[i], event.GenPart_phi[i],
                                      event.GenPart_m[i])

    top_lep, top_had = TLorentzVector(), TLorentzVector()
    for i in range(event.nGenPart):
        if abs(event.GenPart_pdgId[i]) in [11, 13, 15]:
            if event.GenPart_grmompdgId[i] == 6:
                # top_lep = top_vec
                top_had = anti_top_vec
            elif event.GenPart_grmompdgId[i] == -6:
                # top_lep = anti_top_vec
                top_had = top_vec

    jets = []
    for i in range(event.nGenJetAK8):
        jets.append(TLorentzVector())
        jets[-1].SetPtEtaPhiM(event.GenJetAK8_pt[i], event.GenJetAK8_eta[i],
                              event.GenJetAK8_phi[i], event.GenJetAK8_mass[i])
    deltas = [jets[j].DeltaR(top_had) for j in range(event.nGenJetAK8)]
    nearest_jet_idx = np.argmin(deltas)
    nearest_jet_pt = jets[nearest_jet_idx].Pt()

    return nearest_jet_idx, nearest_jet_pt


def calc_triplet_data(sample):
    read_variables = [
        "nGenPart/I",
        "GenPart[pt/F,eta/F,phi/F,m/F,pdgId/I,mompdgId/I,grmompdgId/I]",
        "nGenJetAK8/I",
        "GenJetAK8[pt/F,eta/F,phi/F,mass/F]",
        "nGenJetAK8_cons/I",
        VectorTreeVariable.fromString("GenJetAK8_cons[pt/F,eta/F,phi/F,mass/F,pdgId/I,jetIndex/I]", nMax=1000),
    ]

    triplets = []

    r = sample.treeReader(variables=read_variables, selectionString="GenJetAK8_pt>400")

    r.start()
    while r.run():                                                              # Event-Loop
        nearest_jet_idx, nearest_jet_pt = find_hadronic_jet(r.event)

        jet_constituents = JetConstituents.get(event=r.event, index=nearest_jet_idx)

        triplets.append(Triplets.make(jet_pt=nearest_jet_pt, particle_vectors=jet_constituents))

    return np.concatenate(triplets, axis=0)


def save_triplets_to_hdf5_file(triplets_data, filename):
    # type: (np.ndarray, str) -> None

    import h5py

    with h5py.File(filename, 'a') as f:
        ds = f.create_dataset(name='triplet-parameters', dtype='float32', data=triplets_data)
        description = 'Rows are triplets and Columns are [3*Zeta, Weight (w), maximum of delta_zeta, the delta_zeta between the legs of an isosceles triangle, the length of the shortest triangle side, the pt of the surrounding jet]'
        ds.attrs.create(name='description', data=description)


def save_triplets_to_root_file(triplets_data, filename):
    # type: (np.ndarray, str) -> None

    outfile = TFile(filename, 'RECREATE')
    outfile.cd()

    ds = TNtuple('triplet-parameters', 'triplet-parameters',
                 'three_zeta:w:max_delta_zeta:delta_legs:shortest_side:jet_pt')
    for row in triplets_data:
        ds.Fill(row)

    outfile.Close()


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(description='Argument parser')    # So #SPLIT100 can be used in the bash script.
    argParser.add_argument('--nJobs', action='store', nargs='?', type=int, default=1)
    argParser.add_argument('--job', action='store', type=int, default=0)
    args = argParser.parse_args()

    mc_ = [UL2018.TTbar_1]            # + [UL2018.TTbar_2, UL2018.TTbar_3]
    samples = [sample.split(n=args.nJobs, nSub=args.job) for sample in mc_]

    for sample in samples:
        all_triplets = calc_triplet_data(sample=sample)
        save_triplets_to_hdf5_file(triplets_data=all_triplets,
                                   filename='EWC_triplets_{:}_{:02}.h5'.format(sample.name[:11], args.job))