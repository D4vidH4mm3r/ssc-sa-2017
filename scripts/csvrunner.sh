#! /bin/bash
#
#SBATCH --account sdusscsa2_slim
#SBATCH --nodes 1
#SBATCH --time 24:00:00

# Batch file run from rundirarray.sh mostly
# arg 1 should be the csv file with many filenames
# arg 2 should be offset (stuff handled by other jobs)
# arg 3 should be the program to run on the files

readarray -t files < $1
index=$(($2+SLURM_ARRAY_TASK_ID-1))
file=${files[$index]}
echo "csvrunner: $HOSTNAME runs $index, that is $file"
$3 $file
