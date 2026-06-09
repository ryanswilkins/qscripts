#! /usr/bin/env python

# Script to caclulate torsion of four specified atoms
#  at the reactant, transition, and product states
# Torsions are calculated from the highest-weighted bin
#  corresponding to each specified state
# 
# Directions for use:
#  - place torsion_calc_states.py in your work path/scripts folder
#  - copy .top file from $inputfiles to $results
#  - run "torsion_calc_states.py $topfile $atom1 $atom2 $atom3 $atom4"
#     from $results, where $atom1-$atom4 are the positions of atoms 1-4
#     in the pdb file


#import matplotlib.pyplot as plt
import os
import sys
import numpy as np
import subprocess
import shlex



nruns = 100 #change this if doing 100 runs/T
alpha = -94.7

def get_qfep_part3(qfep_file):
    part3 = list()
    found_part3 = False
    
    with open(qfep_file, 'r') as qfepout:
        for line in qfepout:
            if found_part3:
                if not line.startswith('#') and len(line.split()) > 4:
                    part3.append(line)
                if len(line.split()) < 4:
                    break
            if '# Part 3:' in line:
                found_part3 = True

    return part3

def find_bins(part3 = []):

    bin_rs, bin_ts, bin_ps = None, None, None
    found_TS = False
 
    rsE = float(part3[0].split()[3])
    tsE = None
    psE = None
    
    for i in range(1, len(part3) - 1):
        prev = float(part3[i - 1].split()[3])
        mid = float(part3[i].split()[3])
        nxt = float(part3[i + 1].split()[3])
        if mid <= prev and mid <= nxt:
            if not found_TS:
                if not rsE:
                    rsE = mid
                    bin_rs = part3[i].split()[0]
                elif mid < rsE:
                    rsE = mid
                    bin_rs = part3[i].split()[0]
            else:
                if not psE:
                    psE = mid
                    bin_ps = part3[i].split()[0]
                elif mid < psE:
                    psE = mid
                    bin_ps = part3[i].split()[0]
        elif mid >= prev and mid >= nxt:
            if not found_TS:
                if abs(mid) > 0:
                    tsE = mid
                    bin_ts = part3[i].split()[0]
                    found_TS = True
            elif found_TS:
                if mid > tsE:
                    tsE = mid
                    bin_ts = part3[i].split()[0]
    if not bin_rs or not bin_ts:
        print('Problems locatin states... Aborting')
        return
    else:
        return bin_rs, bin_ts, bin_ps

def find_lambdas(qfepout = 'qfep.out', bins = dict()):
    found_part2 = False
    
    state_lamdas = dict()
   
    with open(qfepout,'r') as qfepout:
        for line in qfepout:
            if found_part2:
                if not line.startswith('#') and len(line.split()) > 7:
                    bin = line.split()[1]
                    lamda = line.split()[0]
                    pts = float(line.split()[6])
                    if bin in list(bins.keys()):
                        if bins[bin] not in list(state_lamdas.keys()):
                            state_lamdas[bins[bin]] = dict()
                        state_lamdas[bins[bin]][lamda] = pts
                if len(line.split()) < 6 or '# Part 3:' in line:
                        break
            if '# Part 2' in line:
                found_part2 = True
    
    return state_lamdas



def get_Eqs(state,temp,run, qfep,lams):
    max_weight = max(state.values())
    max_lambda = str([k for k,v in state.items() if v==max_weight])
    lambda_int1 = float([k for k,v in state.items() if v==max_weight][0])
    lambda_int2 = 1.0000-lambda_int1

    if (len(max_lambda)>13):
        max_lambda=max_lambda[2:-12]
    if os.path.isfile("files.txt"):
        os.remove("files.txt")
    
    lambda_1 = str(max_lambda)[2:-5]   
    lambda_2 = str(round(1.0000-float(max_lambda[2:-5]),3))[0:5]

    current_dir = os.getcwd()
    grep_call_1 = "tail -v -n 5 %s/inputfiles/md_* | grep -EB 6  \"%s[[:space:]]{1,}%s\" > \'files.txt\'" % (current_dir,lambda_1,lambda_2)
    os.system(grep_call_1)
    grep_call_2 = "grep -v \"%s[[:space:]]{1,}%s\" \'files.txt\' > \'tmp.txt\'" % (lambda_1,lambda_2)
    os.system(grep_call_2)
    os.system("cp \'tmp.txt\' \'files.txt\'")
    os.system("sed -i \"s|%s||g\" \'files.txt\'" % current_dir)
    os.system("sed -i \"s|inputfiles\\/||g\" \'files.txt\'")
    os.system("sed -i \"s|/md|md|g\" \'files.txt\'")
    os.system("sed -i \"s/==>//g\" \'files.txt\'")
    os.system("sed -i \"s/<==//g\" \'files.txt\'")

    with open("files.txt",'r') as files: 
         for line in files:
            if "md" in str(line):
                md_file = line.split('.')
    energy_file=md_file[0][1:15]+'.en'
    found_part0 = False
    with open(qfep,'r') as qf:
        for line in qf:
            if found_part0:
                if len(line.split()) < 6 or '# Part 1' in line:
                    break
                if line.split()[0]==energy_file and int(line.split()[1])==1:
                    E_b1 = float(line.split()[5])
                    E_a1 = float(line.split()[6])
                    E_t1 = float(line.split()[7])
                    E_i1 = float(line.split()[8])
                    E_el1 = float(line.split()[9])
                    E_vdw1 = float(line.split()[10])
                    E_nb1 = E_el1+E_vdw1
                elif line.split()[0]==energy_file and int(line.split()[1])==2:
                    E_b2 = float(line.split()[5])
                    E_a2 = float(line.split()[6])
                    E_t2 = float(line.split()[7])
                    E_i2 = float(line.split()[8])
                    E_el2 = float(line.split()[9])
                    E_vdw2 = float(line.split()[10])
                    E_nb2 = E_el2+E_vdw2
            if '# Part 0' in line:
                found_part0 = True
    os.system("rm files.txt")
    os.system("rm tmp.txt")
    

    return lambda_int1*E_b1+lambda_int2*E_b2, lambda_int1*E_a1+lambda_int2*E_a2, lambda_int1*E_t1+lambda_int2*E_t2, lambda_int1*E_i1+lambda_int2*E_i2, lambda_int1*E_nb1+lambda_int2*E_nb2, lambda_int1*E_el1+lambda_int2*E_el2, lambda_int1*E_vdw1+lambda_int2*E_vdw2



#temperatures = (283,288,293,298,303,308,313)
temperatures = (298,300)
data_files = ["torsion_avgs_rs.dat","torsion_avgs_ts.dat","torsion_avgs_ps.dat"]

for temp in temperatures:
    print(f"T={temp}")
    E_RS = []
    E_TS = []
    for run in range(1,nruns):  
        qfep = str(temp)+'/'+str(run)+'/qfep.out'
        # try:
        #     part3 = get_qfep_part3(qfep)
        #     if isinstance(find_bins(part3),tuple): 
        #         rs, ts, ps = find_bins(part3)
        #     state_lamdas = find_lambdas(qfep, {rs: '1-RS',ts: '2-TS', ps: '3-PS'})            

        #     for state in sorted(state_lamdas.keys()):
        #         if state=="1-RS":
        #             qfep = str(temp)+'/'+str(run)+'/qfep.out'
        #             #E_RS = get_Eqs(state_lamdas[state],temp,run,topfile)
        #             print("i'm here")
        #         elif state=="2-TS":
        #             qfep = str(temp)+'/'+str(run)+'/qfep.out'
        #             #E_RS = get_Eqs(state_lamdas[state],temp,run,topfile)
        # except:
        #     print('\nqfep.out not found. Moving to next folder.\n\n')
        #     pass

        try:
            part3 = get_qfep_part3(qfep)
            if isinstance(find_bins(part3),tuple): 
                rs, ts, ps = find_bins(part3)
            state_lamdas = find_lambdas(qfep, {rs: '1-RS',ts: '2-TS', ps: '3-PS'})            

            for state in sorted(state_lamdas.keys()):
                if state=="1-RS":
                    lam = (1.0,0.0)
                    qfep = str(temp)+'/'+str(run)+'/qfep.out'
                    E_RS.append(get_Eqs(state_lamdas[state],temp,run,qfep,lam))
                elif state=="2-TS":
                    lam = (0.6,0.4)
                    qfep = str(temp)+'/'+str(run)+'/qfep.out'
                    E_TS.append(get_Eqs(state_lamdas[state],temp,run,qfep,lam))
                else:
                    break
        except:
            print(" ")
            pass


        # part3 = get_qfep_part3(qfep)
        # if isinstance(find_bins(part3),tuple): 
        #     rs, ts, ps = find_bins(part3)
        # state_lamdas = find_lambdas(qfep, {rs: '1-RS',ts: '2-TS', ps: '3-PS'})            

        # for state in sorted(state_lamdas.keys()):
        #     if state=="1-RS":
        #         lam = (1.0,0.0)
        #         qfep = str(temp)+'/'+str(run)+'/qfep.out'
        #         E_RS.append(get_Eqs(state_lamdas[state],temp,run,qfep,lam))
        #     elif state=="2-TS":
        #         lam = (0.6,0.4)
        #         qfep = str(temp)+'/'+str(run)+'/qfep.out'
        #         E_TS.append(get_Eqs(state_lamdas[state],temp,run,qfep,lam))
        #     else:
        #         break

    E_bond_RS = []
    E_ang_RS = []
    E_tor_RS = []
    E_imp_RS = []
    E_nb_RS = []
    E_el_RS = []
    E_vdW_RS = []
    E_bond_TS = []
    E_ang_TS = []
    E_tor_TS = []
    E_imp_TS = []
    E_nb_TS = []
    E_el_TS = []
    E_vdW_TS = []
    for i in E_RS:
            E_bond_RS.append(i[0])
            E_ang_RS.append(i[1])
            E_tor_RS.append(i[2])
            E_imp_RS.append(i[3])
            E_nb_RS.append(i[4])
            E_el_RS.append(i[5])
            E_vdW_RS.append(i[6])

    for i in E_TS:
            E_bond_TS.append(i[0])
            E_ang_TS.append(i[1])
            E_tor_TS.append(i[2])
            E_imp_TS.append(i[3])
            E_nb_TS.append(i[4])
            E_el_TS.append(i[5])
            E_vdW_TS.append(i[6])
    print(f"bonded RS = {np.mean(E_bond_RS)}\nnb RS = {np.mean(E_ang_RS)}\nnb RS = {np.mean(E_tor_RS)} +- {np.std(E_tor_RS)}\nnb RS = {np.mean(E_imp_RS)}\nel RS = {np.mean(E_el_RS)} \nvdW RS = {np.mean(E_vdW_RS)}")
    print(f"bonded TS = {np.mean(E_bond_TS)}\nnb TS = {np.mean(E_ang_TS)}\nnb TS = {np.mean(E_tor_TS)} +- {np.std(E_tor_TS)}\nnb TS = {np.mean(E_imp_TS)}\nel TS = {np.mean(E_el_TS)} \nvdW TS = {np.mean(E_vdW_TS)}")


                #E_RS = get_Eqs(state_lamdas[state],temp,run,topfile)
    # for c, state in enumerate(sorted(state_lamdas.keys())):
    #     df = open(data_files[c],"a")
    #     torsions_temp = collect_data(temp,nruns)
    #     print(data_files[c])
    #     print(torsions_temp[c])
    #     print(data_files[c],torsions_temp[c])
    #     df.write("%f %f\n" % (temp,torsions_temp[c]))
