#!/bin/bash
# leaves from the m0 = 8 and m0 = 9 rehearsal certificates of run A1 (r = 12), with the same scratch verifier copy
cd /root/ymleaf
for m in 8 9; do for f in f1 f4-3-2-1; do
  c=/root/floor-v6/rehf/A1/RUN$m/cert_m${m}_r12_1_$f.txt; b=cert_m${m}_r12_1_$f
  [ -f "$c" ] || { echo "$b certificate absent"; continue; }
  s=$(date +%s); timeout 1500 python3 -I -B cert_gate_leaf.py $c > $b.out 2>&1; rc=$?
  grep '^LEAF|' $b.out > $b.leaf.hbp
  echo "$b rc=$rc leaves=$(grep -c . $b.leaf.hbp) secs=$(( $(date +%s)-s )) $(tail -1 $b.out | cut -c1-80)"
  cp $b.leaf.hbp /mnt/c/tmp/opus55/ym-residual-rooms/data/
done; done
