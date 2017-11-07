#!/bin/bash
echo "Redoing preprocessing!"
jid=$(sbatch py-run.sh 2-preprocessing.py)
jid=${jid##* }
echo $jid
echo "Redoing splitting afterwards"
sbatch --dependency=afterok:$jid py-run.sh 3-split.py 
