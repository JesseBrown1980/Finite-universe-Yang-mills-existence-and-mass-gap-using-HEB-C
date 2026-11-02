#!/bin/bash
# Regenerates every small-lattice number of PERRON-TWO-SIDED.md, in one file of rows, json=0. Read-only on the stores.
# usage: run_two_sided_small.sh PYTHON
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
PY="$1"
R=D:/ym-3x4-room-run/p0-ball
P=$R/perroncert.exe
X=$R/perronritz-grid.exe
O=$R/jump34/small
OL=/d/ym-3x4-room-run/p0-ball/jump34/small
mkdir -p $OL
OUT=$OL/TWO-SIDED-SMALL.hbp
: > $OUT
row() { tr -d '\r' | grep -E "$1" >> $OUT; }
echo "TWO_SIDED_SMALL|perroncert_sha16=$(sha256sum $P | cut -c1-16)|perronritz_sha16=$(sha256sum $X | cut -c1-16)|json=0" >> $OUT

small() {
  local L=$1 T1=$2 T2=$3 T3=$4 BLO=$5 BHI=$6 DEV=$R/small/$1/dev.bin
  echo "BRACKET|L=$L|tool=shellschur|lo=$BLO|hi=$BHI|json=0" >> $OUT
  for T in $T1 $T2 $T3; do
    PERRONCERT_INNER=16:2000 "$P" solve $DEV 0 1000 9000 $T 40 $O/$L-$T.bin | row '^PERRONCERT\|'
  done
  "$X" pass $DEV 0 1000 9000 $O/$L-$T1.bin $O/$L-$T2.bin $O/$L-$T3.bin | row 'LOWER|UPPER|^PERRONRITZ\|'
  "$X" grid $DEV 0 1000 9000 $O/$L-g.bin $T1 $O/$L-$T1.bin $T2 $O/$L-$T2.bin $T3 $O/$L-$T3.bin | row 'PERRONRITZ_BEST'
  "$P" check $DEV 0 1000 9000 $O/$L-g.bin | row '^PERRONCERT\|'
}
small 2x2 45000000 46000000 46400000 46466796 46468750
small 2x3 57000000 58000000 58400000 58441406 58443359

# 3x3, on the vectors of warmcal33.sh and run_perron33.sh.
D33=$R/c33/dev33.bin
W=$R/warmcal
F=$R/pc33-final
"$X" pass $D33 0 1000 9000,6000,4000 $W/w33-76200000-12_200.bin $W/w33-76400000-12_200.bin $W/w33-76430000-12_200.bin | row 'LOWER|UPPER|^PERRONRITZ\|'
for jb in 9000 6000 4000; do
  "$P" check $D33 0 1000 $jb $W/w33-76430000-12_200.bin | row '^PERRONCERT\|'
done
g33() {
  local n=$1; shift
  "$X" grid $D33 0 1000 9000 $O/33-$n.bin "$@" | row 'PERRONRITZ_BEST'
  "$P" check $D33 0 1000 9000 $O/33-$n.bin | row '^PERRONCERT\|'
}
g33 x3a 76200000 $W/w33-76200000-12_200.bin 76300000 $W/w33-76300000-12_200.bin 76400000 $W/w33-76400000-12_200.bin
g33 x3c 75000000 $F/d75000000.bin 76200000 $W/w33-76200000-12_200.bin 76400000 $W/w33-76400000-12_200.bin
g33 x2 76200000 $W/w33-76200000-12_200.bin 76400000 $W/w33-76400000-12_200.bin
"$PY" -I $R/check_d_strict.py $D33 $O/33-x3a.bin 1000 9000 --self-adjoint 27 | row 'CHECK_D_STRICT'

# 3x3 solved at lower couplings, each from d = 0.
low() {
  local JB=$1 T=$2
  PERRONCERT_INNER=14:400 "$P" solve $D33 0 1000 $JB $T 16 $O/33-r$JB.bin | row '^PERRONCERT\|'
}
low 6000 64500000
low 5000 59000000
low 4000 53500000
echo "TWO_SIDED_SMALL_DONE|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $OUT
