#!/bin/bash
cd /Users/lukasguething/Documents/cfm-toolbox/YASA4CFM/cfmtoolbox
OUT=/tmp/yasa_eval
R=5; M=5; CACHE=50
for interval in 1 3 5 10; do
  for depth in 2 3 4 5 6; do
    model="tests/eval/${depth}_${interval}.json"
    for t in 1 2 3; do
      # sample size
      start=$(date +%s)
      poetry run cfmtoolbox --import "$model" evaluate-t-wise-sample-size --t "$t" --m "$M" --cache-size "$CACHE" --r "$R" > "$OUT/size_${depth}_${interval}_t${t}.log" 2>&1
      end=$(date +%s)
      echo "size,${depth},${interval},${t},wall=$((end-start))" >> "$OUT/walltimes.csv"
      # timing
      start=$(date +%s)
      poetry run cfmtoolbox --import "$model" evaluate-t-wise --t "$t" --m "$M" --cache-size "$CACHE" --r "$R" > "$OUT/time_${depth}_${interval}_t${t}.log" 2>&1
      end=$(date +%s)
      echo "time,${depth},${interval},${t},wall=$((end-start))" >> "$OUT/walltimes.csv"
    done
  done
done
echo BATCH_DONE >> "$OUT/walltimes.csv"

