import sys
import os
import mdtraj as md
import numpy as np 

dcd_file = sys.argv[1]
pdb_file = sys.argv[2]
rmsf_file = sys.argv[3]
pdb = md.load_pdb(pdb_file)
print(pdb)
traj = md.load(dcd_file,top=pdb_file)
print(traj)

n_sel = traj.topology.select('name N')  
ca_sel = traj.topology.select('name CA')
c_sel = traj.topology.select('name C')
o_sel = traj.topology.select('name O')

n_traj = traj.atom_slice(n_sel)
ca_traj = traj.atom_slice(ca_sel)
c_traj = traj.atom_slice(c_sel)
o_traj = traj.atom_slice(o_sel)

n_rmsf = md.rmsf(n_traj, n_traj, 0)
ca_rmsf = md.rmsf(ca_traj, ca_traj, 0)
c_rmsf = md.rmsf(c_traj, c_traj, 0)
o_rmsf = md.rmsf(o_traj, o_traj, 0)
rmsf = []
for i in range(len(n_rmsf)):
    rmsf_res = (n_rmsf[i]+ca_rmsf[i]+c_rmsf[i]+o_rmsf[i])/4
    rmsf.append(rmsf_res)

with open(rmsf_file, 'w') as f:
    for i in range(len(rmsf)):
        line = f'{i+1}    {10*rmsf[i]}\n'
        f.write(line)
    f.close()



