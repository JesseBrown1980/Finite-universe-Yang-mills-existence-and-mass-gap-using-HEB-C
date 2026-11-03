#!/bin/bash
# Warm start of the 3x4 Perron solve at a higher threshold. Read-only on the store. Operator's word, 2026-11-02:
# "run the warm start at a higher threshold after the check". Start it only if the check of d93000000.bin agreed.
# The starting d is kept. The new d goes to its own file.
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
RD=/d/ym-3x4-room-run/p0-ball
W=$RD/p34; cd $W
DEV="seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-"
L=$W/WARM34.hbp
T=${1:-93700000}
PASSES=${2:-8}
INNER=${3:-16:500}
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
echo "WARM34_START|at=$(stamp)|solve_t_milli=$T|full_passes=$PASSES|inner=$INNER|start_d_sha256=$(sha256sum $W/d93000000.bin | cut -c1-64)|perroncert_sha256=$(sha256sum $RD/perroncert.exe | cut -c1-64)|json=0" >> $L
t0=$(date +%s)
PERRONCERT_START=D:/ym-3x4-room-run/p0-ball/p34/d93000000.bin PERRONCERT_INNER=$INNER PERRONCERT_CHECK_EVERY=4 $RD/perroncert.exe solve "$DEV" 0 1000 9000 "$T" "$PASSES" "D:/ym-3x4-room-run/p0-ball/p34/d$T.bin" > "$W/warm-$T.out" 2> "$W/warm-$T.err"
rc=$?
echo "WARM34_SOLVE|exit=$rc|secs=$(( $(date +%s)-t0 ))|at=$(stamp)|json=0" >> $L
grep -E '^PERRONCERT(_PROGRESS|_ERROR)?\|' "$W/warm-$T.out" | tr -d '\r' >> $L
[ -f "$W/d$T.bin" ] && echo "WARM34_D|file=d$T.bin|bytes=$(stat -c %s "$W/d$T.bin")|sha256=$(sha256sum "$W/d$T.bin" | cut -c1-64)|json=0" >> $L
echo "DONE|exit=$rc|at=$(stamp)|json=0" >> $L
