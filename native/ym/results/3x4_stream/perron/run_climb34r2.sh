#!/bin/bash
# The 3x4 climb, local copy, restart after the power-off at 2026-11-02T14:20:24Z took segment 2 of T=93.95 (no checkpoint from it).
# Operator's word: "resume last claude and resume the finite yang mills work", on top of "go higher obviously ... we need the full run".
# Read-only on the store. Starts from climb34/best.bin (sha 635e7273), the vector of segment 1, so segment 1 here is the lost segment 2.
# climb34/ stays as it is. New files go to climb34r2/.
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
PY="$1"
R=D:/ym-3x4-room-run/p0-ball
W=/d/ym-3x4-room-run/p0-ball/climb34r2
mkdir -p $W
"$PY" -I $R/perron_climb.py $R/perroncert.exe "seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-" $R/climb34/best.bin $R/climb34r2 93950000 72000 16:500 3 93000000:61051 93700000:18416 > $W/climb.out 2> $W/climb.err
echo "DONE|exit=$?|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $W/CLIMB.hbp
