#!/usr/bin/bash
# Fifth batch, outside the claim: the hybrid lower bound, at cuts where the model is complete by the character count. Below-normal priority.
# usage: run_batch5.sh THREADS
cd /c/tmp/opus55/vector-review-20261103
export TMP=C:/tmp/opus55/vector-review-20261103/tmp TEMP=C:/tmp/opus55/vector-review-20261103/tmp
T=$1
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
: > out/hybrid.index
# Small, for the Python recheck.
hyb hyb_4x4_r9_m8 4 4 9 8 8 110000000,114000000,115000000,115500000
# Controls against known upper bounds.
hyb hyb_3x3_r9_m13 3 3 9 13 74000000,76000000,76300000
hyb hyb_3x4_r9_m14 3 4 9 14 92000000,93500000,93900000,94000000
# The claim's tori.
hyb hyb_4x4_r9_m13 4 4 9 13 115000000,117000000,117300000,117400000
hyb hyb_4x4_r6_m13 4 4 6 13 100000000,103000000,104500000,104900000
hyb hyb_5x5_r9_m11 5 5 9 11 165000000,168000000,169500000,169900000
hyb hyb_4x5_r9_m11 4 5 9 11 135000000,139000000,140500000,140800000
echo "BATCH5_DONE|json=0" > out/batch5.done
