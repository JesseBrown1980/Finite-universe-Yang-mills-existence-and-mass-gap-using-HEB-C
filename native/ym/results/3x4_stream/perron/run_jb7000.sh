#!/bin/bash
# After the certifying checks: one read-only pass of the pinned perroncert at JB=7000 on d93, against the coupling table of pass 1.
# Predicted before the run, by the table and by the second seat's store-free pass: 79745170, row 44743136, M=8.
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
R=D:/ym-3x4-room-run/p0-ball
W=/d/ym-3x4-room-run/p0-ball/jump34
J=$W/JUMP.hbp
until grep -q 'CERTIFY_DONE' $J; do sleep 30; done
S0=$(date +%s)
"$R/perroncert.exe" check "seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-" 0 1000 7000 $R/p34/d93000000.bin > $W/check-jb7000.out 2> $W/check-jb7000.err
echo "JB7000_CHECK|exit=$?|secs=$(( $(date +%s) - S0 ))|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $J
