import os
import sys
import numpy as np 
import matplotlib
import matplotlib.pyplot as plt
import glob
from matplotlib.lines import Line2D
from cycler import cycler
from scipy.signal import savgol_filter

# to run: plots.py n_plots plot_type  
# n_plots - int, number of systems/enzymes to add to plot
# plot_type - arr for Arrhenius plot, rep for reaction energy profile

n_plots = 1

# prompt data files and corresponding system names (for labelling purposes)
# assumes data files are all .dat files, so adds extensions automatically
rdf_files = glob.glob('*.dat')

r = []         
all_gr = [] 

for filename in rdf_files:
    data = np.loadtxt(filename,delimiter=None)
    if len(r) == 0:
        r = data[:,0]
    all_gr.append(data[:,1])
gr = np.mean(all_gr, axis=0)

with open("rdf_O3.dat","w") as f:
    for i in range(len(r)):
        f.write(f'{10*r[i]} {gr[i]}\n')


# with open()

# plt_files = []
# sys_names = []
# for i in range(n_plots):
#     plt_file, sys_name = input("Enter file path and system: ").split()
#     if len(plt_file) > 0:
#         plt_files.append(plt_file)
#         sys_names.append(sys_name)



# fig, ax = plt.subplots()
# matplotlib.rcParams['text.usetex'] = True
# plt.xlabel('r (Å)',fontsize=14)
# plt.ylabel('g(r)',fontsize=14)
# # Set appropriate label properties for reaction energy profile
# plt.minorticks_off()
# plt.xlim(0,)
# # necessary for arrhenius plot labels
# col = 'r'
# ls = '-'

# # main plot
# ax.plot(r,gr,label='BpCM',color=col,linestyle=ls,linewidth=3.5)


# plt.legend()


# plt.show()
