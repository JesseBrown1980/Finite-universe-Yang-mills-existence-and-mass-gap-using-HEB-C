#!/bin/bash
# The hybrid vector at cut 14 over every row of the 3x4 store, read by the pinned perroncert check. Read-only on the store. Below normal priority. The range is predicted at vector/attack/HYBRID-ATTACK-PREDICTION.hbp, row ATTACK_STORE.
export MSYS_NO_PATHCONV=1
cd C:/tmp/ym-hybrid-attack || exit 9
T=C:/tmp/ym-vector-target/release
L=STORE-RUNS.hbp
DEV=seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
echo "STORE34_START|at=$(now)|perroncert_sha256=$(sha256sum "$T/perroncert.exe" | cut -c1-64)|hybridcheck_sha256=$(sha256sum hybridcheck.exe | cut -c1-64)|json=0" >> "$L"
./hybridcheck.exe write D:/ym-3x4-room-run/passA.bin 3 4 14 in/hyb_3x4_r9_m14.hybrid d-3x4-m14.bin > store34-write.out 2> store34-write.err
echo "STORE34_WRITE|at=$(now)|exit=$?|$(cut -c1-260 store34-write.out)" >> "$L"
"$T/perroncert.exe" check "$DEV" 0 1000 9000 d-3x4-m14.bin > store34-check.out 2> store34-check.err
echo "STORE34_CHECK|at=$(now)|exit=$?|$(cut -c1-420 store34-check.out)" >> "$L"
echo "STORE34_DONE|at=$(now)|json=0" >> "$L"
