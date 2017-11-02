# This script will start program (arg 1) on all files from csv file (arg 2)

# arg 1 should be program, arg 2 should be file with many things in it

maxarray=1000 # depends on slurm config; 1000 for Abacus

readarray -t files < $2
numfiles=${#files[@]}
echo "Will run $1 on $numfiles different inputs"

remaining=$numfiles
numstarted=0
while [ $remaining -gt 0 ]; do
  dostart=$((remaining>maxarray?maxarray:remaining)) # how many to start now; take min
  echo "started: $numstarted, remaining: $remaining, now starting: $dostart"
  # running batch script thing takes dir, offset and goal script
  sbatch --array=1-$((dostart)) csvrunner.sh $2 $numstarted $1
  remaining=$((remaining-dostart))
  numstarted=$((numstarted+dostart))
done

