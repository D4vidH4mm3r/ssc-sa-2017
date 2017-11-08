#! /bin/bash

# This script will start program (arg 1) on all files in dir (arg 2)
# This is done using job arrays (starts aux-runner-dir.sh repeatedly)

# arg 1 should be program
# arg 2 should be dir with many things in it
# arg 3 should be chunk size
shopt -s nullglob # so empty dirs count as 0
maxarray=1000 # depends on slurm config; 1000 for Abacus

program=$1
dir=$2
chunksize=$3
permaxarray=$((maxarray*chunksize))

numfiles=($dir/*)
numfiles=${#numfiles[@]}
numarrays=$((numfiles/permaxarray))

remaining=$numfiles
numstarted=0
echo "Will run $1 on $numfiles different inputs"
for (( i=0; i<= $numarrays; i++ )); do
    dostart=$((remaining>permaxarray?permaxarray:remaining)) # how many to start now; take min
    arraylen=$(((dostart+chunksize-1)/chunksize))
    echo "Starting array number $i with $dostart files (will have array indices 1-$arraylen) and offset $numstarted"
    sbatch --array=1-$arraylen aux-runner-dir.job $program $dir $chunksize $numstarted
    remaining=$((remaining-dostart))
    numstarted=$((numstarted+dostart))
done

