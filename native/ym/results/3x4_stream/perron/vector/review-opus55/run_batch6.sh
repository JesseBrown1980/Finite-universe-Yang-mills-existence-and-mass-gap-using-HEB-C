#!/usr/bin/bash
# Sixth batch, outside the claim: finer targets for the hybrid at complete cuts. Below-normal priority, 3 threads, sequential.
cd /c/tmp/opus55/vector-review-20261103
export TMP=C:/tmp/opus55/vector-review-20261103/tmp TEMP=C:/tmp/opus55/vector-review-20261103/tmp
T=3
F='review\target-final\release'
PY=python
low() { cmd //c "start /belownormal /b /wait $*"; }
hyb() { # name lx ly r cut targets
  low $F\\ritz.exe $2 $3 $4 $5 150 $T tmp/$1 none hybrid=$6 hsweeps=300 > out/$1.out 2>&1
  low $PY -I py_lump_counts.py $2 $3 ritz out/$1.out > out/$1.count 2>&1
  grep -hE '^HYBRID_BEST' out/$1.out >> out/hybrid.index
  tail -1 out/$1.count >> out/hybrid.index
  rm -f tmp/$1.psi
}
# A good vector at a small cut, for the Python recheck.
hyb hyb_4x4_r9_m10 4 4 9 10 115000000,116500000,116800000
hyb hyb_4x4_r9_m14 4 4 9 14 117300000,117450000,117500000
hyb hyb_4x4_r6_m14 4 4 6 14 103000000,103500000,104000000
hyb hyb_5x5_r9_m11b 5 5 9 11 168000000,168300000,168600000,168900000
hyb hyb_4x5_r9_m13 4 5 9 13 139000000,140200000,140500000
echo "BATCH6_DONE|json=0" > out/batch6.done
