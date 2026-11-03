#!/bin/bash
# All-pairs check on the 3x4 store with the hardened executable, built from the source pinned at 9c2c7e6. Read-only, below normal priority.
# The prediction reached GitHub before this started. Rows go to allpairs-3x4.out, start and end to RUN.hbp.
export MSYS_NO_PATHCONV=1
R=/d/ym-3x4-room-run/p0-ball/allpairs-hardened
cd "$R" || exit 9
echo "HARDENED_3x4_START|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|cap_entries=470000000|json=0" >> RUN.hbp
t0=$(date +%s)
./allpairs.exe seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector- 0 470000000 > allpairs-3x4.out 2> allpairs-3x4.err
c=$?
echo "HARDENED_3x4_DONE|exit=$c|secs=$(( $(date +%s) - t0 ))|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> RUN.hbp
