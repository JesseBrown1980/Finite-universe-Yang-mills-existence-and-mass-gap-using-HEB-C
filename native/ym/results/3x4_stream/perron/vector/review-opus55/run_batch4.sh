#!/usr/bin/bash
# Fourth batch, after the third has finished. Final build, remaining controls, low-M audits, the E8 test space, the table-file comparison, and the refit.
cd /c/tmp/opus55/vector-review-20261103
export TMP=C:/tmp/opus55/vector-review-20261103/tmp TEMP=C:/tmp/opus55/vector-review-20261103/tmp
low() { cmd //c "start /belownormal /b /wait $*"; }
F='review\target-final\release'
DIRECT=review/target-final/release
# Controls, each direct so the exit code is seen.
$DIRECT/census.exe 3 3 9 1 given/g-local-3x3-lump.hbp 3 conj planar > out/ctl_census_planar.out 2>&1; echo "EXIT=$?" >> out/ctl_census_planar.out
$DIRECT/classes.exe 4 4 9 1 given/g-local-4x4-lump.hbp 112252744 planar > out/ctl_classes_planar.out 2>&1; echo "EXIT=$?" >> out/ctl_classes_planar.out
$DIRECT/classes.exe 4 4 9 1 given/g-local-4x4-lump.hbp 112252745 > out/ctl_classes_plus1.out 2>&1; echo "EXIT=$?" >> out/ctl_classes_plus1.out
$DIRECT/hunt.exe 4 4 9 1 given/g-local-4x4-lump.hbp 112252745 31 5 3 > out/ctl_hunt_direct.out 2>&1; echo "EXIT=$?" >> out/ctl_hunt_direct.out
$DIRECT/subsets.exe 5 5 planar > out/ctl_subsets_planar_5x5.out 2>&1; echo "EXIT=$?" >> out/ctl_subsets_planar_5x5.out
python -I py_moves.py --sabotage > out/ctl_moves.out 2>&1; echo "EXIT=$?" >> out/ctl_moves.out
sed -E '0,/^LOW\|([^|]*)\|([^|]*)\|micro=[0-9]+/s//LOW|\1|\2|micro=999/' out/hunt_4x4_r9.out > tmp/hunt_altered.out
python -I py_verify_low.py tmp/hunt_altered.out 4 4 9 given/g-local-4x4-lump.hbp 112252744 > out/ctl_verify_low.out 2>&1; echo "EXIT=$?" >> out/ctl_verify_low.out
# The E8 test space.
for spec in "4 4 9" "4 4 6" "4 5 9" "5 5 9" "3 4 9" "3 3 9"; do
  low python -I py_e8_dressed.py $spec > "out/e8_${spec// /_}.out" 2>&1
done
low python -I py_e8_dressed.py 4 4 9 --sabotage > out/e8_sabotage.out 2>&1
# Low-M exhaustive audits, on real orbits, by the definition.
low $F\\ritz.exe 4 4 9 14 1 3 tmp/audit44 none audit=given/g-local-4x4-lump.hbp > out/lowm_4x4_r9.out 2>&1
low $F\\ritz.exe 4 4 6 14 1 3 tmp/audit44r6 none audit=given/g-local-4x4-lump-r6.hbp > out/lowm_4x4_r6.out 2>&1
low $F\\ritz.exe 4 5 9 12 1 3 tmp/audit45 none audit=given/g-local-4x5-lump.hbp > out/lowm_4x5_r9.out 2>&1
low $F\\ritz.exe 5 5 9 11 1 3 tmp/audit55 none audit=given/g-local-5x5-product.hbp > out/lowm_5x5_r9.out 2>&1
rm -f tmp/audit*.psi
# The author's table files against my signature sets.
for spec in "3 3" "3 4" "4 4" "4 5" "5 5"; do
  low python -I py_compare_table_file.py "D:/ym-3x4-room-run/p0-ball/vector/local-${spec// /x}.hbp" $spec > "out/tablefile_${spec// /x}.out" 2>&1
done
# Refit on the class walk.
low $F\\classes.exe 4 4 9 1 given/g-local-4x4-lump.hbp 112252744 dump > tmp/classes_dump_4x4.out 2>&1
low python -I py_refit_classes.py tmp/classes_dump_4x4.out 4 4 9 112000000 118000000 out/g-refit-4x4-r9.hbp > out/refit_4x4_r9.out 2>&1
# A higher-cut recheck of the Ritz engine, which brings in (0,3) and (2,2) rows.
low python -I py_ritz_recheck.py 4 4 9 10 out/ritz_4x4_r9_m10.psi out/ritz_4x4_r9_m10.out > out/recheck_4x4_m10.out 2>&1
echo "BATCH4_DONE|json=0" > out/batch4.done
