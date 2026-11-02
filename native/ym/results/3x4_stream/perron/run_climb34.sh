#!/bin/bash
# The 3x4 climb, local copy. Operator's word, 2026-11-02: "go higher obviously ... we need the full run". Read-only on the store.
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
PY="$1"
R=D:/ym-3x4-room-run/p0-ball
W=/d/ym-3x4-room-run/p0-ball/climb34
mkdir -p $W
"$PY" -I $R/perron_climb.py $R/perroncert.exe "seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-" $R/p34/d93700000.bin $R/climb34 93950000 72000 16:500 3 93000000:61051 93700000:18416 > $W/climb.out 2> $W/climb.err
echo "DONE|exit=$?|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $W/CLIMB.hbp
