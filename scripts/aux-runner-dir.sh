#! /bin/bash
#
#SBATCH --account sdusscsa2_slim
#SBATCH --nodes 1
#SBATCH --time 24:00:00

# Batch file run from rundirarray.sh mostly
# arg 1 should be dir with many files and stuff
# arg 2 should be offset (stuff handled by other jobs)
# arg 3 should be chunk size

#module load python/3.6.0
program=$1
dir=$2
chunksize=$3
offset=$4

files=($dir/*)
startindex=$((offset+(SLURM_ARRAY_TASK_ID-1)*chunksize))
subset=${files[@]:startindex:chunksize} # TODO: take min so no array OOB
echo "Have: chunk size $chunksize"
echo "$HOSTNAME runs from $startindex, that is $subset"
$program $subset
