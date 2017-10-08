#! /bin/bash
#
#SBATCH --account sdusscsa2_slim
#SBATCH --nodes 1
#SBATCH --time 10:00:00

echo Loading module
module add python/3.6.0

echo Will run $@
python $@
