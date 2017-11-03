#!/bin/bash
for f in "$@"; do
  grep "error\|CANCELLED" $f -q
  if [[ $? -eq 0 ]]; then
    echo "$f was apparently cancelled"
    s=$(head -n 1 $f)
    fn=${s##* }
    echo "Was working on $fn"
    echo "$fn" >> remaining.csv
  else
    mv $f oldslurm/
  fi
done
