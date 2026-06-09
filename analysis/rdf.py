import sys
import os
import mdtraj as md
import numpy as np 

dcd_file = sys.argv[1]
pdb_file = sys.argv[2]
rdf_file = sys.argv[3]
pdb = md.load_pdb(pdb_file)
print(pdb)
traj = md.load(dcd_file,top=pdb_file)
print(traj)

bins = 1000
r_max = 10
r_min = 0.1
print(f'ucv {traj.unitcell_volumes}')
o_pairs = traj.topology.select_pairs("resi >= 346 and name O","name O2")
print(f'o_pairs {o_pairs}')
r,gr = md.compute_rdf(traj,o_pairs,(r_min,r_max),n_bins=bins,periodic=False)


with open(rdf_file, 'w') as f:
    for i in range(len(r)):
        line = f'{r[i]} {gr[i]}\n'
        f.write(line)
    f.close()



