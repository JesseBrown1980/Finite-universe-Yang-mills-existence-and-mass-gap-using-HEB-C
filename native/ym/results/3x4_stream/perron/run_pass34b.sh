#!/bin/bash
# After the certifying checks on x3-c.bin: one read-only pass for the final bracket, both sides, every coupling in the list, final tool.
# Operator's word: "go higher obviously ... we need the full run", "resume the finite yang mills work".
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
R=D:/ym-3x4-room-run/p0-ball
W=/d/ym-3x4-room-run/p0-ball/jump34
J=$W/JUMP.hbp
until grep -q 'CERTIFY3_DONE' $J; do sleep 30; done
"$R/perronritz-final.exe" pass "seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-" 0 1000 9000,8000,7000,6000,5000,27000,81000,243000 $R/p34/d93700000.bin $R/jump34/d93950000-conv.bin $R/jump34/d94058000-hosted.bin $R/jump34/x3-c.bin > $W/pass2.out 2> $W/pass2.err
echo "PASS2_DONE|exit=$?|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> $J
