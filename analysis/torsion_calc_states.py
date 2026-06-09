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

topfile = sys.argv[1]
atom1 = sys.argv[2]
atom2 = sys.argv[3]
atom3 = sys.argv[4]
atom4 = sys.argv[5]

nruns = 100 #change this if doing 100 runs/T

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



def qcalc(state,lambda_values,temp,run, qcalc_inp,qcalc_out,top):
    max_weight = max(state.values())
    max_lambda = str([k for k,v in state.items() if v==max_weight])

    if (len(max_lambda)>13):
        max_lambda=max_lambda[2:-12]
    if os.path.isfile("files.txt"):
        os.remove("files.txt")
    
    lambda_1 = str(max_lambda)[2:-5]   
    lambda_2 = str(1.00-float(max_lambda[2:-5]))[0:5] 

    current_dir = os.getcwd()
    grep_call_1 = "tail -v -n 5 %s/inputfiles/md_* | grep -EB 1  \"%s[[:space:]]{1,}%s\" > \'files.txt\'" % (current_dir,lambda_1,lambda_2)
    os.system(grep_call_1)
    grep_call_2 = "grep -Ev \"%s[[:space:]]{1,}%s\" \'files.txt\' > \'tmp.txt\'" % (lambda_1,lambda_2)
    os.system(grep_call_2)
    
    os.system("mv \'tmp.txt\' \'files.txt\'")
    os.system("sed -i \"s|%s||g\" \'files.txt\'" % current_dir)
    os.system("sed -i \"s|inputfiles\\/||g\" \'files.txt\'")
    os.system("sed -i \"s|/md|md|g\" \'files.txt\'")
    os.system("sed -i \"s/==>//g\" \'files.txt\'")
    os.system("sed -i \"s/<==//g\" \'files.txt\'")
    
    qc = open(qcalc_inp,'w')
    qc.write("%s \n" % top)
    qc.write(".\n")
    qc.write("5\n")
    qc.write("   %s   %s   %s   %s \n" % (atom1,atom2,atom3,atom4))
    qc.write(".\ngo\n")
    with open("files.txt",'r') as files: 
         for line in files:
             if "md" in str(line):
                md_file = line.split('.')
                qc.write(current_dir+'/'+str(temp)+'/'+str(run)+'/'+md_file[0][1:]+'.dcd\n')
    qc.write(".\n")
    
    qcalc_cmd = "qcalc5 <%s>%s" % (qcalc_inp,qcalc_out)
    # qcalc_cmd = "echo -n <%s >%s" % (qcalc_inp,qcalc_out)
    # print(qcalc_cmd+"| qcalc5")
    subprocess.Popen(qcalc_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)

    return

def collect_data(temp,nruns):
    torsion_state = []
    torsion = []
    qcalc_out = ['qcalc_rs.out','qcalc_ts.out','qcalc_ps.out']
    for state in qcalc_out:
        torsion_sum = 0
        frame_count = 0    
        for run in range(1,nruns):
            state_file = str(temp)+'/'+str(run)+'/'+state
            with open(state_file) as qc:
                found_data = False
                for line in qc:
                        if line.startswith("file"):
                            found_data = True
                        if found_data:
                            try:
                                data_line = line.split()
                                torsion_sum+=float(data_line[2])
                                frame_count+=1
                                print(torsion_sum)
                            except:
                                print("")

            try:
                torsion.append(sum(torsion_state)/frame_count)
            except ZeroDivisionError: 
                print('Divided by zero')

    # data_file.write("%f %f\n" % (temp,torsion_sum/frame_count))
    # print(len(torsion_state))
    return torsion


#temperatures = (283,288,293,298,303,308,313)
temperatures = (298,303)
data_files = ["torsion_avgs_rs.dat","torsion_avgs_ts.dat","torsion_avgs_ps.dat"]

for temp in temperatures:
    print(temp)
    for run in range(1,nruns):  
        print(run) 
        qfep = str(temp)+'/'+str(run)+'/qfep.out'
        
        try:
            part3 = get_qfep_part3(qfep)
            if isinstance(find_bins(part3),tuple): 
                rs, ts, ps = find_bins(part3)
            state_lamdas = find_lambdas(qfep, {rs: '1-RS',ts: '2-TS', ps: '3-PS'})            

            for state in sorted(state_lamdas.keys()):
                if state=="1-RS":
                    qcalc_inp = str(temp)+'/'+str(run)+'/qcalc_rs.inp'
                    qcalc_out = str(temp)+'/'+str(run)+'/qcalc_rs.out'
                elif state=="2-TS":
                    qcalc_inp = str(temp)+'/'+str(run)+'/qcalc_ts.inp'
                    qcalc_out = str(temp)+'/'+str(run)+'/qcalc_ts.out'
                else:
                    qcalc_inp = str(temp)+'/'+str(run)+'/qcalc_ps.inp'
                    qcalc_out = str(temp)+'/'+str(run)+'/qcalc_ps.out'
                print((state_lamdas[state],state_lamdas[state].keys()))
                qcalc(state_lamdas[state],state_lamdas[state].keys(),temp,run,qcalc_inp,qcalc_out,topfile)
        except:
            print('\nqfep.out not found. Moving to next folder.\n\n')
            pass
    
    # for c, state in enumerate(sorted(state_lamdas.keys())):
    #     df = open(data_files[c],"a")
    #     torsions_temp = collect_data(temp,nruns)
    #     print(data_files[c])
    #     print(torsions_temp[c])
    #     print(data_files[c],torsions_temp[c])
    #     df.write("%f %f\n" % (temp,torsions_temp[c]))
