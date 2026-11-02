#!/bin/bash
# Grid on T=93.7, T=93.95 converged and the hosted T=94.058 vector, then both certifying checks on the result. Read-only on the store.
# Operator's word: "go higher obviously ... we need the full run".
# usage: run_grid34c.sh PYTHON
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
PY="$1"
R=D:/ym-3x4-room-run/p0-ball
W=/d/ym-3x4-room-run/p0-ball/jump34
STORE="seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-"
J=$W/JUMP.hbp
"$R/perronritz-final.exe" grid "$STORE" 0 1000 9000 $R/jump34/x3-c.bin 93700000 $R/p34/d93700000.bin 93950000 $R/jump34/d93950000-conv.bin 94058000 $R/jump34/d94058000-hosted.bin > $W/grid3.out 2> $W/grid3.err
echo "GRID3_DONE|exit=$?|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $J
SHA=$(sha256sum $W/x3-c.bin | cut -c1-64)
echo "CERTIFY3_START|file=x3-c.bin|sha256=$SHA|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $J
S0=$(date +%s)
"$R/perroncert.exe" check "$STORE" 0 1000 9000 $R/jump34/x3-c.bin > $W/certify3-perroncert.out 2> $W/certify3-perroncert.err
echo "CERTIFY3_PERRONCERT|exit=$?|secs=$(( $(date +%s) - S0 ))|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $J
S0=$(date +%s)
"$PY" -I $R/check_d_strict.py "341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-" $R/jump34/x3-c.bin 1000 9000 --passa D:/ym-3x4-room-run/passA.bin --self-adjoint 27 --expect-d-sha256 $SHA > $W/certify3-strict.out 2> $W/certify3-strict.err
echo "CERTIFY3_STRICT|exit=$?|secs=$(( $(date +%s) - S0 ))|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $J
echo "CERTIFY3_DONE|file=x3-c.bin|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $J
