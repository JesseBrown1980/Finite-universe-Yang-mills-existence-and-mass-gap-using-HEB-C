#!/bin/bash
# Every 3x4 row recomputed from the definition of H by the second seat's fullrebuild.rs, built with Rust 1.81, compared with the store.
# Read-only. Operator's word: "The full rebuild should recompute the matrix rows from their defining rules".
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
R=D:/ym-3x4-room-run/p0-ball
W=/d/ym-3x4-room-run/p0-ball/fullrebuild
S0=$(date +%s)
echo "FULLREBUILD_START|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|threads=6|json=0" >> $W/RUN.hbp
"$R/fullrebuild/fullrebuild.exe" 341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector- D:/ym-3x4-room-run/passA.bin 3 4 6 > $W/fullrebuild-3x4.out 2> $W/fullrebuild-3x4.err
echo "FULLREBUILD_DONE|exit=$?|secs=$(( $(date +%s) - S0 ))|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $W/RUN.hbp
