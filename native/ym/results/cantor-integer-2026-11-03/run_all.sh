#!/bin/bash
# Reproduces this folder's rows, from the repository root, with cantorint and ymsec built on Rust 1.81. Integer only, json=0.
set -euo pipefail
F=native/ym/results/cantor-integer-2026-11-03
X=native/ym/target/release
"$X/ymsec" 2 2 1 1 s22.matrix > /dev/null
"$X/cantorint" run s22.matrix 9 4 > RESULT-r9.hbp
"$X/cantorint" run s22.matrix 243 4 > RESULT-r243.hbp
"$X/cantorint" run s22.matrix 9 4 P=300 > RESULT-r9-P300.hbp
for c in cantor zero inverted rotated_one; do python3 -I -X utf8 "$F/verify_cantorint.py" s22.matrix 9 "$c" > "second-$c.out" & done; wait
cat second-cantor.out second-zero.out second-inverted.out second-rotated_one.out > SECOND-PATH.hbp
