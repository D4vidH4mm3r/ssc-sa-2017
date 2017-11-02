#! /bin/bash
#
#SBATCH --account sdusscsa2_gpu
#SBATCH --nodes 1
#SBATCH --time 24:00:00

echo Loading module
module load python/3.6.0
module load cuda/8.0.44
module load cudnn/5.1

echo Will run $@
python $@
