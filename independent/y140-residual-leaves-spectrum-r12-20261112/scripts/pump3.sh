#!/bin/bash
# Pump test inputs: three certificates (the three frozen f words) of the same matrix at m0 = 7, 8, 9, coupling r = 12
# (an excluded rehearsal coupling; nothing at r = 9 or within 1 of it; --launch-r9 never passed).
# Uses the pinned launcher in test mode and the scratch verifier copy that prints the per-row slack.
P=/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110
W=/root/ymleaf
cd /
for m in 7 8 9; do
  rm -rf $W/T$m
  bash $P/final/tools/run_floor.sh --test-r 12 --test-m0 $m --test-f '1;8,7,6,5,4;6,5,4,3' --test-g0 100/1 --test-out $W/T$m > $W/T$m.stdout 2>&1
  echo "T$m exit=$? $(tail -1 $W/T$m.stdout | cut -d'|' -f1-6 | cut -c1-200)"
  for c in $W/T$m/RUN$m/cert_*.txt; do
    b=T_$(basename $c .txt)
    python3 -I -B $W/cert_gate_leaf.py $c > $W/$b.out 2>&1
    grep '^LEAF|' $W/$b.out > $W/$b.leaf.hbp
    echo "  $b leaves=$(grep -c . $W/$b.leaf.hbp) $(tail -1 $W/$b.out | cut -c1-75)"
    cp $W/$b.leaf.hbp /mnt/c/tmp/opus55/ym-residual-rooms/data/
  done
done
