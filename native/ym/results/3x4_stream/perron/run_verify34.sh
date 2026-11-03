#!/bin/bash
# Rebuilds sampled rows of the 3x4 store from the definition of H. Read-only on the store and the key table.
# Operator's word, 2026-11-02: "run verify_sample_rows on the 3x4 store".
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
RD=/d/ym-3x4-room-run/p0-ball
W=$RD/rev1
L=$W/VERIFY34.hbp
PY="$1"
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
echo "VERIFY34_START|at=$(stamp)|tool_sha256=$(sha256sum $RD/verify_sample_rows.py | cut -c1-64)|passa_sha256=$(sha256sum /d/ym-3x4-room-run/passA.bin | cut -c1-64)|json=0" >> $L
t0=$(date +%s)
"$PY" -I D:/ym-3x4-room-run/p0-ball/verify_sample_rows.py 3 4 "341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-" D:/ym-3x4-room-run/passA.bin --per-M 50 --per-sector 50 --uniform 1000 --seed 27 --rows 44742735 > "$W/verify34.out" 2> "$W/verify34.err"
rc=$?
echo "VERIFY34_END|exit=$rc|secs=$(( $(date +%s)-t0 ))|at=$(stamp)|json=0" >> $L
tr -d '\r' < "$W/verify34.out" >> $L
echo "DONE|exit=$rc|at=$(stamp)|json=0" >> $L
