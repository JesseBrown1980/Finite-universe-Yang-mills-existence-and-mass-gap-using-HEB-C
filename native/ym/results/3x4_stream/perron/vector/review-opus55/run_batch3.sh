#!/usr/bin/bash
# Third batch: the attack from above and the 3x4 census. Sequential, below-normal priority, 3 threads.
cd /c/tmp/opus55/vector-review-20261103
export TMP=C:/tmp/opus55/vector-review-20261103/tmp TEMP=C:/tmp/opus55/vector-review-20261103/tmp
B='review\target-c\release'
low() { cmd //c "start /belownormal /b /wait $*"; }
ritz() { # name lx ly r cut sweeps claim
  low $B\\ritz.exe $2 $3 $4 $5 $6 3 out/$1 > out/$1.out 2>&1
  low python -I py_ritz_bound.py out/$1.out $7 > out/$1.bound 2>&1
  sha256sum out/$1.psi | cut -c1-64 > out/$1.psi.sha256
  if [ $(stat -c %s out/$1.psi) -gt 20000000 ]; then rm -f out/$1.psi; fi
  cat out/$1.bound >> out/ritz.index
}
: > out/ritz.index
# Rechecks and controls.
low python -I py_ritz_recheck.py 4 4 9 8 out/ritz_4x4_r9_m8.psi out/ritz_4x4_r9_m8.out > out/recheck_4x4_m8.out 2>&1
low python -I py_ritz_recheck.py 4 4 9 8 out/ritz_4x4_r9_m8.psi out/ritz_4x4_r9_m8.out --sabotage > out/recheck_4x4_m8_sabotage.out 2>&1
ritz ritz_5x5_r9_m7 5 5 9 7 200 154016734
low python -I py_ritz_recheck.py 5 5 9 7 out/ritz_5x5_r9_m7.psi out/ritz_5x5_r9_m7.out > out/recheck_5x5_m7.out 2>&1
ritz ritz_4x5_r9_m7 4 5 9 7 200 134017195
low python -I py_ritz_recheck.py 4 5 9 7 out/ritz_4x5_r9_m7.psi out/ritz_4x5_r9_m7.out > out/recheck_4x5_m7.out 2>&1
low $B\\ritz.exe 4 4 9 7 10 3 out/ritz_sab_unit unit_weight > out/ritz_sab_unit.out 2>&1
low $B\\ritz.exe 4 4 9 7 200 3 out/ritz_sab_m wrong_m > out/ritz_sab_m.out 2>&1
low python -I py_ritz_bound.py out/ritz_sab_m.out 112252744 > out/ritz_sab_m.bound 2>&1
# 3x4, against the store's 94.0707.
ritz ritz_3x4_r9_m12 3 4 9 12 300 94070673
ritz ritz_3x4_r9_m14 3 4 9 14 300 94070673
ritz ritz_3x4_r9_m16 3 4 9 16 300 94070673
# 4x4 r=9, escalating.
ritz ritz_4x4_r9_m13 4 4 9 13 300 112252744
ritz ritz_4x4_r9_m14 4 4 9 14 300 112252744
ritz ritz_4x4_r9_m15 4 4 9 15 300 112252744
ritz ritz_4x4_r9_m16 4 4 9 16 300 112252744
# 4x4 r=6.
ritz ritz_4x4_r6_m10 4 4 6 10 400 96472613
ritz ritz_4x4_r6_m13 4 4 6 13 400 96472613
ritz ritz_4x4_r6_m16 4 4 6 16 400 96472613
# 4x5 and 5x5.
ritz ritz_4x5_r9_m10 4 5 9 10 300 134017195
ritz ritz_4x5_r9_m12 4 5 9 12 300 134017195
ritz ritz_5x5_r9_m10 5 5 9 10 300 154016734
ritz ritz_5x5_r9_m11 5 5 9 11 300 154016734
# The 3x4 census, with the first link on class representatives.
low $B\\census.exe 3 4 9 1 given/g-local-3x4-lump.hbp 3 conj > out/census_3x4.out 2>&1
echo "BATCH3_DONE|json=0" > out/batch3.done
