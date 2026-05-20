import os
import sys
import numpy as np 
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from cycler import cycler

# to run: plots.py n_plots plot_type  
# n_plots - int, number of systems/enzymes to add to plot
# plot_type - arr for Arrhenius plot, rep for reaction energy profile

n_plots = int(sys.argv[1])
plot_type = sys.argv[2]


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

if plot_type=='arr':
	# Set appropriate label properties for Arrhenius plot

	# custom temperature labels
	x_ticks = [0.003003003,0.00304878,0.003095975,0.003144654,0.003194888,0.003246753,0.00330033,0.003355705,0.003412969,0.003472222,0.003533569]
	x_labels = ['$333^{-1}$','$328^{-1}$','$323^{-1}$','$318^{-1}$','$313^{-1}$','$308^{-1}$','$303^{-1}$','$298^{-1}$','$293^{-1}$','$288^{-1}$','$283^{-1}$']
	plt.xticks(ticks = x_ticks,labels=x_labels,rotation=45)
	
	# axes labels and limits
	plt.xlabel('$T^{-1}$  (K$^{-1}$)',fontsize=14)
	plt.ylabel('$\Delta G/T$ (kcal mol$^{-1}$ K$^{-1})$',fontsize=14)
	plt.minorticks_off()

	max_dGT = max((max(plots[name][1]) for name in plots))
	min_dGT = min((min(plots[name][1]) for name in plots))

	plt.xlim(0.003003003*.99,0.003533569*1.01)
	plt.ylim(0.925*min_dGT,1.075*max_dGT)
elif plot_type=='rep':

	# usetex = true looks nicer for labels, but doesn't work with arrhenius plots
	matplotlib.rcParams['text.usetex'] = True
	plt.xlabel('$\epsilon$  (Å)',fontsize=14)
	plt.ylabel('$\Delta G$ (kcal mol$^{-1})$',fontsize=14)
	# Set appropriate label properties for reaction energy profile
	plt.minorticks_off()
	plt.grid(which='major',axis='y',color='gray')

elif plot_type=='rmsf':
	matplotlib.rcParams['text.usetex'] = True
	plt.xlabel('Residue',fontsize=14)
	plt.ylabel('RMSF (Å)',fontsize=14)
	# Set appropriate label properties for reaction energy profile
	plt.minorticks_off()
	plt.xlim(1,116)
# necessary for arrhenius plot labels
def create_dummy_line(**kwds):
    return Line2D([], [], **kwds)

if plot_type=='arr':

	# empty vector for line of best fit
	x_fit = np.linspace(0, 0.003533569*1.1)

	# empty list for legend purposes
	labels = []

	# plot and fit each system
	for name in sys_names:

		a,b = np.polyfit(plots[name][0],plots[name][1],1)
		col, ls, mrk = input(f'Enter colour, line style, and marker of {name}: ').split()
		p1, =ax.plot(plots[name][0],plots[name][1],linestyle='None',marker=mrk,color=col,label=name)
		p2, =ax.plot(x_fit,a*x_fit+b,color=col,linestyle=ls,label=name)
		labels.append((name, {'color': col, 'linestyle': ls, 'marker': mrk}))
	ax.legend(
	    # Line handles
    	[create_dummy_line(**l[1]) for l in labels],
    	# Line titles
    	[l[0] for l in labels]    
		)



elif plot_type=='rep':
	for name in sys_names:
		col = input(f'Enter colour of {name}:')
		ax.plot(plots[name][0],plots[name][1],label=name,color=col)
	plt.legend()


elif plot_type=='rmsf':
	for name in sys_names:
		col, ls = input(f'Enter colour and line style of {name}: ').split()
		ax.plot(plots[name][0],plots[name][1],label=name,color=col,linestyle=ls,linewidth=3.5)
	plt.legend()


plt.show()


