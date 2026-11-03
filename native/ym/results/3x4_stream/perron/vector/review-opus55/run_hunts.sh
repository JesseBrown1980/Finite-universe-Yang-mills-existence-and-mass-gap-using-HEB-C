#!/usr/bin/bash
# The hunt runs and their controls. Below-normal priority, 3 threads. Writes only under out/.
cd /c/tmp/opus55/vector-review-20261103
export TMP=C:/tmp/opus55/vector-review-20261103/tmp TEMP=C:/tmp/opus55/vector-review-20261103/tmp
H='review\target\release\hunt.exe'
run() { # name args...
  name=$1; shift
  cmd //c "start /belownormal /b /wait $H $*" > out/$name.out 2>&1
  echo "RUN|name=$name|exit=$?|json=0" >> out/hunts.index
  grep -E 'HUNT_RESULT|HUNT_VERDICT|FIRST_' out/$name.out | cut -c1-260 >> out/hunts.index
}
: > out/hunts.index
# Controls first, 15 seconds each. Each must print verdict=RED, exit 2.
run ctl_swap_rule 4 4 9 1 given/g-local-4x4-lump.hbp 112252744 21 15 3 swap_rule
run ctl_planar 4 4 9 1 given/g-local-4x4-lump.hbp 112252744 22 15 3 planar_adj
run ctl_dent 4 4 9 1 given/g-local-4x4-lump.hbp 112252744 23 15 3 dent
run ctl_wrong_m 4 4 9 1 given/g-local-4x4-lump.hbp 112252744 24 15 3 wrong_m
run ctl_nonzero_flat 4 4 9 1 given/g-local-4x4-lump.hbp 112252744 25 15 3 nonzero_flat
run ctl_claim_plus1_4x4 4 4 9 1 given/g-local-4x4-lump.hbp 112252745 26 15 3
run ctl_claim_plus1_4x4_r6 4 4 6 1 given/g-local-4x4-lump-r6.hbp 96472614 27 15 3
run ctl_claim_plus1_4x5 4 5 9 1 given/g-local-4x5-lump.hbp 134017196 28 15 3
run ctl_claim_plus1_5x5 5 5 9 1 given/g-local-5x5-product.hbp 154016735 29 15 3
# The hunts. Exit 0 and verdict=CLEAN unless something breaks.
run hunt_4x4_r9 4 4 9 1 given/g-local-4x4-lump.hbp 112252744 101 150 3
run hunt_4x4_r6 4 4 6 1 given/g-local-4x4-lump-r6.hbp 96472613 102 150 3
run hunt_4x5_r9 4 5 9 1 given/g-local-4x5-lump.hbp 134017195 103 200 3
run hunt_5x5_r9 5 5 9 1 given/g-local-5x5-product.hbp 154016734 104 240 3
echo "ALLDONE|json=0" >> out/hunts.index
