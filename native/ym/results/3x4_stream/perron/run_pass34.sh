#!/bin/bash
# One read-only pass over the 3x4 store. Side from below on the jump vector, side from above on the span of the stored vectors,
# at the couplings in the list. Operator's word: "go higher obviously ... we need the full run", "resume the finite yang mills work".
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
R=D:/ym-3x4-room-run/p0-ball
W=/d/ym-3x4-room-run/p0-ball/jump34
"$R/perronritz.exe" pass "seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-" 0 1000 9000,8000,7000,6000,5000,27000,81000,243000 $R/p34/d93000000.bin $R/p34/d93700000.bin $R/climb34/best.bin $R/jump34/x-93-937.bin > $W/pass1.out 2> $W/pass1.err
echo "PASS1_DONE|exit=$?|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $W/JUMP.hbp
