#!/usr/bin/bash
# Last batch. The Python recheck of a good hybrid vector, and the hybrid with no table rows at all on the whole 3x3 space. Then the default build for the reproducers.
cd /c/tmp/opus55/vector-review-20261103
export TMP=C:/tmp/opus55/vector-review-20261103/tmp TEMP=C:/tmp/opus55/vector-review-20261103/tmp
F='review\target-final\release'
low() { cmd //c "start /belownormal /b /wait $*"; }
low python -I py_hybrid_recheck.py 4 4 9 10 tmp/hyb_4x4_r9_m10.hybrid 115534179 > out/hybrid_recheck_m10.out 2>&1
low $F\\ritz.exe 3 3 9 999 150 2 tmp/hyb_3x3_full none hybrid=76000000,76400000,76440000 hsweeps=300 > out/hyb_3x3_full.out 2>&1
low python -I py_lump_counts.py 3 3 ritz out/hyb_3x3_full.out > out/hyb_3x3_full.count 2>&1
rm -f tmp/hyb_3x3_full.psi
( cd review; unset CARGO_TARGET_DIR; cargo +1.81 clippy -j 3 --release --all-targets -- -D warnings > ../out/default_clippy.out 2>&1; echo "CLIPPY_EXIT=$?" >> ../out/default_clippy.out; cargo +1.81 build -j 3 --release > ../out/default_build.out 2>&1; echo "BUILD_EXIT=$?" >> ../out/default_build.out )
echo "BATCH7_DONE|json=0" > out/batch7.done
