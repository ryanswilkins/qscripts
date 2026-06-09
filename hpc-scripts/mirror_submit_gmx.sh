#! /bin/bash

###################USER_VARIABLES###################################



#ZIP WHEN DONE?
zip_after=true

#SET TEMPERATURES TO SIMULATE:
        #temperatures=(278)
        temperatures=298
        #temperatures=(283 288 293 303 308 313)
        #temperatures=(283 288 293 303 308 313 318 323 328)
        #temperatures=(288 323 333)
        #temperatures=(343 348 353 358 363 368 373)
        #temperatures=(293 303 308 313 318 323 328)
        #temperatures=(318 323 328 333)

#SET NUMBER OF RUNS:
        runs=10

        #START SUBMITTING JOBS FROM:
start_from=1

#NAME OF CLUSTER SPECIFIC SUBMISSION SCRIPT (STORED IN $inputfiles)
submit_script="run.sh"

#CLUSTER SPECIFIC SUBMIT COMMAND
submit_command="sbatch"

#YOU ARE WORKING HERE:
home_path=$(pwd)

#INPUTFILES ARE EXISTING IN $home_path/$inputfiles WITH THIS NAME:
inputfiles="inputfiles"

#MIRROR JOBS FROM ../$mirror_from/../$home_path/  (--> /inputfiles)
mirror_from="SimFiles"

#JOBS WILL BE MIRRORED TO work_path/../$home_path/ (--> /inputfiles)
work_path="/cluster/work/users/$USER/nodelete"

#JOB LOG FILE WITH TIMESTAMP
job_info="job_"`date +%Y-%m-%d_%H-%M`".txt"
###########################END######################################
####################################################################

##########################SCRIPT####################################

#CHECK IF /inputfiles EXISTS
if [ -d "$home_path/$inputfiles" ];
then
    printf "\nFound $inputfiles directory\n"
else
    printf "\nCould not find $inputfiles directory. ABORTING!\n"
    exit 1
fi

#CHECK IF $qdyn MATCHES THE ONE GIVE IN $submit_script
#FILE IN $home_path/$inputfiles/$submit_script
#if [[ $(echo $(cat $inputfiles/$submit_script | grep -o -m 1 "$qdyn")) = $(echo "$qdyn") ]];
#then
#       printf "\nQ version matches submission script\n"
#else
#       printf "\nQ version does not match submission script - aborting!\n"
#       exit 1
#fi

#GET PATH TO CREATE FROM  home_path + mirror_from:
IFS='/' read -ra path_array <<< "$home_path"

found_mirror=false
for i in "${path_array[@]}"
do
    if $found_mirror;
    then
        work_path="$work_path/$i"
    
    fi

    if [ "$i" = "$mirror_from" ];
    then
        found_mirror=true 
    fi
done

printf  "\nJobs from:\n $home_path \nwill be submitted from:\n $work_path \n\n"

#CREATE $work_path if it does not exist
mkdir -p $work_path

#COPY $home_path/$inputfiles to $work_path
cp -r "$home_path/$inputfiles/" "$work_path"

#Move to $work_path
cd $work_path

#BEFORE SUBMITTING - WRITE TO job_info.txt Qdyn version


IFS='
'



#Iterate over temperatures
for temp in ${temperatures[*]}
do

    #Create temperature directory if it does not exist
    if [ ! -d "$temp" ]; then
        mkdir -p $temp
    fi

    cd $temp

    #iterate over runs
    for i in $(seq $start_from $runs)
    do

        #Create run directory if it does not exist
        if [ ! -d "$i" ]; then
            mkdir -p $i
        fi

        cd $i
         
	pdb_file=$(ls *.pdb)

        #copy inpufiles to run directory:
        cp ../../inputfiles/* .
         
        #Set temperature in mdp inputfiles:
        sed -i s/T_VAR/"$temp"/ *.mdp

        #Submit job (f.ex: sbatch run.sh):
        $submit_command $submit_script $pdb_file 1234

        cd ../
    done
    cd ../
done

#ZIP $home_path/$inputfiles WHEN DONE? 
if $zip_after;
then
        printf "\nZipping input files\n"
        cd $home_path
        zip -rq ${inputfiles}"_"`date +%Y-%m-%d_%H-%M`.zip $inputfiles
        #rm -r $inputfiles
else
        printf "\nNot zipping input files\n"
fi
exit 1
