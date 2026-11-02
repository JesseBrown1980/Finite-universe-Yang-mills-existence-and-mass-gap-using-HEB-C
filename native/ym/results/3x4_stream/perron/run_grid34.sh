#!/bin/bash
# One read-only pass over the 3x4 store: the exact certified value of the third divided difference plus gamma d, for a grid of gamma.
# Operator's word: "go higher obviously ... we need the full run", "resume the finite yang mills work".
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
R=D:/ym-3x4-room-run/p0-ball
W=/d/ym-3x4-room-run/p0-ball/jump34
"$R/perronritz-grid.exe" grid "seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-" 0 1000 9000 $R/jump34/x3-a.bin 93000000 $R/p34/d93000000.bin 93700000 $R/p34/d93700000.bin 93950000 $R/climb34/best.bin > $W/grid1.out 2> $W/grid1.err
echo "GRID1_DONE|exit=$?|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $W/JUMP.hbp
