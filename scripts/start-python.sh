program=$1
simple="${program%.*}" # strips extension
simple="${simple#*-}" # strips leading n-
sbatch -o "${simple}.output" -J "$simple" aux-runner-python.job "$program"
