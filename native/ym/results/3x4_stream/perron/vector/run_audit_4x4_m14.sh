#!/bin/bash
# The exhaustive audit of the store-free table on 4x4, up to M = 14, from the definition of H. Below normal priority, 3 threads.
export MSYS_NO_PATHCONV=1
V=/d/ym-3x4-room-run/p0-ball/vector
cd "$V" || exit 9
T=C:/tmp/ym-vector-target/release
t0=$(date +%s)
"$T/localaudit.exe" enumerate 4 4 local-4x4.hbp g-local-4x4-lump.hbp 1000 9000 112252744 14 3 > audit-4x4-m14.out 2> audit-4x4-m14.err
c=$?
echo "AUDIT_4x4_M14|exit=$c|secs=$(( $(date +%s) - t0 ))|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|$(tail -1 audit-4x4-m14.out | cut -c1-300)" >> VECTOR-RUN.hbp
