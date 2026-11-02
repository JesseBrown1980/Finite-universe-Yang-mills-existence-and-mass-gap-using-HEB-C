#!/bin/bash
# Grid on the converged T=93.95 vector, then both certifying checks on whichever vector scored highest. Read-only on the store.
# Operator's word: "go higher obviously ... we need the full run", "resume the finite yang mills work".
# usage: run_grid34b.sh PYTHON
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
PY="$1"
R=D:/ym-3x4-room-run/p0-ball
W=/d/ym-3x4-room-run/p0-ball/jump34
STORE="seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-"
J=$W/JUMP.hbp
"$R/perronritz-grid.exe" grid "$STORE" 0 1000 9000 $R/jump34/x3-b.bin 93000000 $R/p34/d93000000.bin 93700000 $R/p34/d93700000.bin 93950000 $R/jump34/d93950000-conv.bin > $W/grid2.out 2> $W/grid2.err
echo "GRID2_DONE|exit=$?|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $J
val() { tr -d '\r' < "$1" | grep PERRONRITZ_BEST | sed -E 's/.*\|t_cert_milli=([-0-9]+)\|.*/\1/'; }
A=$(val $W/grid1.out)
B=$(val $W/grid2.out)
if [ -n "$B" ] && [ "$B" -gt "$A" ]; then WIN=x3-b.bin; else WIN=x3-a.bin; fi
SHA=$(sha256sum $W/$WIN | cut -c1-64)
echo "CERTIFY_START|file=$WIN|grid_a=$A|grid_b=$B|sha256=$SHA|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $J
S0=$(date +%s)
"$R/perroncert.exe" check "$STORE" 0 1000 9000 $R/jump34/$WIN > $W/certify-perroncert.out 2> $W/certify-perroncert.err
echo "CERTIFY_PERRONCERT|exit=$?|secs=$(( $(date +%s) - S0 ))|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $J
S0=$(date +%s)
"$PY" -I $R/check_d_strict.py "341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-" $R/jump34/$WIN 1000 9000 --passa D:/ym-3x4-room-run/passA.bin --self-adjoint 27 --expect-d-sha256 $SHA > $W/certify-strict.out 2> $W/certify-strict.err
echo "CERTIFY_STRICT|exit=$?|secs=$(( $(date +%s) - S0 ))|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $J
echo "CERTIFY_DONE|file=$WIN|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $J
