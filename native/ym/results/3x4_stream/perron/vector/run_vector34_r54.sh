#!/bin/bash
# The pinned check of the 49-number vector fitted at r = 5.4 on the 3x4 store. Read-only on the store. Below normal priority.
export MSYS_NO_PATHCONV=1
V=/d/ym-3x4-room-run/p0-ball/vector
cd "$V" || exit 9
T=C:/tmp/ym-vector-target/release
DEV=seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-
PASSA=D:/ym-3x4-room-run/passA.bin
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
"$T/prodvec.exe" write "$PASSA" 3 4 scan/g-store34-5400.hbp d-3x4-r54.bin > write-3x4-r54.out 2>&1
echo "VECTOR_3x4_R54_WRITE|at=$(now)|exit=$?|$(cut -c1-200 write-3x4-r54.out)" >> VECTOR-RUN.hbp
"$T/perroncert.exe" check "$DEV" 0 1000 5400 d-3x4-r54.bin > check-3x4-r54.out 2> check-3x4-r54.err
echo "VECTOR_3x4_R54_CHECK|at=$(now)|exit=$?|$(cut -c1-420 check-3x4-r54.out)" >> VECTOR-RUN.hbp
