#! /bin/bash

# This script will start program (arg 1) on all files in dir (arg 2)
# This is done using job arrays (starts dirrunner.sh repeatedly)

# arg 1 should be program, arg 2 should be dir with many things in it

shopt -s nullglob # so empty dirs count as 0
maxarray=1000 # depends on slurm config; 1000 for Abacus

numfiles=($2/*)
numfiles=${#numfiles[@]}
remaining=$numfiles
numstarted=0

echo "Will run $1 on $numfiles different inputs"
while [ $remaining -gt 0 ]; do
  dostart=$((remaining>maxarray?maxarray:remaining)) # how many to start now; take min
  echo "started: $numstarted, remaining: $remaining, now starting: $dostart"
  # running batch script thing takes dir, offset and goal script
  sbatch --array=1-$((dostart)) dirrunner.sh $2 $numstarted $1
  remaining=$((remaining-dostart))
  numstarted=$((numstarted+dostart))
done

