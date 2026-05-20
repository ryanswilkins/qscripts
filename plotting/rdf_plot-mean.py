import os
import sys
import numpy as np 
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from cycler import cycler
from scipy.signal import savgol_filter

# to run: plots.py n_plots plot_type  
# n_plots - int, number of systems/enzymes to add to plot
# plot_type - arr for Arrhenius plot, rep for reaction energy profile

n_plots = int(sys.argv[1])

# prompt data files and corresponding system names (for labelling purposes)
# assumes data files are all .dat files, so adds extensions automatically
plt_files = []
sys_names = []
for i in range(n_plots):
    plt_file, sys_name = input("Enter file path and system: ").split()
    if len(plt_file) > 0:
        plt_files.append(plt_file)
        sys_names.append(sys_name)


# loads all data files and stores them in a dict with key corresponding to system name
# dict values are a list of 2 lists, one for T/rxn coord data, one for free energy data
plots = {}
for i, name in enumerate(sys_names):
    x_data = []
    y_data = []
    with open(plt_files[i]+'.dat','r') as f:
        for line in f:
            xy = line.split()
            x_data.append(float(xy[0]))
            y_data.append(float(xy[1]))
    xy = [x_data,y_data]
    plots[name] = xy


fig, ax = plt.subplots()
matplotlib.rcParams['text.usetex'] = True
plt.xlabel('r (Å)',fontsize=14)
plt.ylabel('g(r)',fontsize=14)
# Set appropriate label properties for reaction energy profile
plt.minorticks_off()
plt.xlim(0,10)
# necessary for arrhenius plot labels
def create_dummy_line(**kwds):
    return Line2D([], [], **kwds)

for name in sys_names:

    col, ls = input(f'Enter colour and line style of {name}: ').split()
    
    # main plot
    ax.plot(plots[name][0],plots[name][1],label=name,color=col,linestyle=ls,linewidth=3.5)

plt.legend()


plt.show()
