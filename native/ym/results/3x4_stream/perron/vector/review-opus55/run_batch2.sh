#!/usr/bin/bash
# Second batch, in order. Below-normal priority. At most 3 threads at a time, since the steps run one after another.
cd /c/tmp/opus55/vector-review-20261103
export TMP=C:/tmp/opus55/vector-review-20261103/tmp TEMP=C:/tmp/opus55/vector-review-20261103/tmp
B='review\target-b\release'
low() { cmd //c "start /belownormal /b /wait $*"; }
# Ritz machinery anchored on the small lattices.
low $B\\ritz.exe 2 2 9 999 800 3 out/ritz_2x2_r9 > out/ritz_2x2_r9.out 2>&1
low $B\\census.exe 3 3 9 1 given/g-local-3x3-lump.hbp 3 > out/census_3x3.out 2>&1
low $B\\ritz.exe 3 3 9 999 400 3 out/ritz_3x3_r9 > out/ritz_3x3_r9.out 2>&1
# Author's points() against my brute force, with its sabotage, then the second path on the hunts' lowest rows.
low python -I py_points_compare.py native/ym/results/3x4_stream/perron/vector/local_table.py 4 4 > out/points_4x4.out 2>&1
low python -I py_points_compare.py native/ym/results/3x4_stream/perron/vector/local_table.py 4 4 --sabotage > out/points_4x4_sabotage.out 2>&1
low python -I py_points_compare.py native/ym/results/3x4_stream/perron/vector/local_table.py 4 5 > out/points_4x5.out 2>&1
low python -I py_points_compare.py native/ym/results/3x4_stream/perron/vector/local_table.py 5 5 > out/points_5x5.out 2>&1
low python -I py_verify_low.py out/hunt_4x4_r9.out 4 4 9 given/g-local-4x4-lump.hbp 112252744 > out/verify_low_4x4_r9.out 2>&1
low python -I py_verify_low.py out/hunt_4x4_r6.out 4 4 6 given/g-local-4x4-lump-r6.hbp 96472613 > out/verify_low_4x4_r6.out 2>&1
low python -I py_verify_low.py out/hunt_4x5_r9.out 4 5 9 given/g-local-4x5-lump.hbp 134017195 > out/verify_low_4x5_r9.out 2>&1
low python -I py_verify_low.py out/hunt_5x5_r9.out 5 5 9 given/g-local-5x5-product.hbp 154016734 > out/verify_low_5x5_r9.out 2>&1
low python -I py_two_numbers.py given/g-local-5x5-product.hbp > out/two_numbers.out 2>&1
# Per-lump table minima for the comparison with the hunts, and the exact-value sabotages.
for spec in "4 4 9 1 given/g-local-4x4-lump.hbp 112252744|4x4_r9" "4 4 6 1 given/g-local-4x4-lump-r6.hbp 96472613|4x4_r6" "4 5 9 1 given/g-local-4x5-lump.hbp 134017195|4x5_r9" "5 5 9 1 given/g-local-5x5-product.hbp 154016734|5x5_r9"; do
  low python -I py_exact_t.py ${spec%|*} > out/exact_${spec#*|}.out 2>&1
done
for sab in swap_rule planar_adj dent wrong_M nonzero_flat; do
  low python -I py_exact_t.py 4 4 9 1 given/g-local-4x4-lump.hbp 112252744 --sabotage=$sab > out/exactsab_r9_$sab.out 2>&1
  low python -I py_exact_t.py 4 4 6 1 given/g-local-4x4-lump-r6.hbp 96472613 --sabotage=$sab > out/exactsab_r6_$sab.out 2>&1
done
low python -I py_exact_t.py 4 4 12 1 given/g-local-4x4-lump.hbp > out/exact_4x4_r12_with_r9_vector.out 2>&1
# Class-pattern walks.
low $B\\classes.exe 4 4 9 1 given/g-local-4x4-lump.hbp 112252744 > out/classes_4x4_r9.out 2>&1
low $B\\classes.exe 4 4 6 1 given/g-local-4x4-lump-r6.hbp 96472613 > out/classes_4x4_r6.out 2>&1
low $B\\classes.exe 4 5 9 1 given/g-local-4x5-lump.hbp 134017195 > out/classes_4x5_r9.out 2>&1
# Extra tori for the adjacency inequality.
for spec in "3 5" "3 6" "3 7" "4 6" "5 6"; do
  low $B\\subsets.exe $spec > out/adj_${spec// /x}.out 2>&1
done
# The flat block.
for spec in "3 3" "3 4" "4 4" "4 5" "5 5"; do
  low python -I py_flats.py $spec > out/flats_${spec// /x}.out 2>&1
done
low python -I py_flats.py 4 4 --sabotage > out/flats_sabotage.out 2>&1
# The rerun of the wrong_m control with the audit no longer compensated.
low $B\\hunt.exe 4 4 9 1 given/g-local-4x4-lump.hbp 112252744 24 15 3 wrong_m > out/ctl_wrong_m_rerun.out 2>&1
echo "BATCH2_DONE|json=0" > out/batch2.done
