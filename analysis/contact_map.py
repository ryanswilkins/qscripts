import sys
import os
import mdtraj as md
import numpy as np 

pdbfile=sys.argv[1]

traj = md.load('total_traj.dcd',top=pdbfile)

contact_scheme=['ca', 'closest', 'closest-heavy', 'sidechain-heavy']

for contact_type in contact_scheme:
    print(contact_type)
    contacts = md.compute_contacts(traj, contacts='all', scheme=contact_type, ignore_nonprotein=True, periodic=False, soft_min=False)
    contact_map = md.geometry.squareform(contacts[0],contacts[1])

    avg_contact = np.mean(contact_map,axis=0,dtype=np.float64)
    std_contact = np.std(contact_map,axis=0,dtype=np.float64)

    np.savetxt("contact_mean"+contact_type+".dat",avg_contact)
    np.savetxt("contact_std"+contact_type+".dat",std_contact)
