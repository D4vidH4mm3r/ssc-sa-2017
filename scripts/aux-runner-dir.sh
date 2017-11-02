#! /bin/bash
#
#SBATCH --account sdusscsa2_slim
#SBATCH --nodes 1
#SBATCH --time 24:00:00

# Batch file run from rundirarray.sh mostly
# arg 1 should be dir with many files and stuff
# arg 2 should be offset (stuff handled by other jobs)

files=($1/*)
index=$(($2+SLURM_ARRAY_TASK_ID-1))
file=${files[$index]}
echo "$HOSTNAME runs $index, that is $file"
$3 $file
