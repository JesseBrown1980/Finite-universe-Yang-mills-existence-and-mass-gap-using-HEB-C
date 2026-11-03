#!/bin/bash
# Perron bound on the 3x4 store. Read-only on the store. Needs the operator's word: do not start without it.
# Solve threshold and predictions are in PERRON-RULE-DRAFT.md, written before this ran.
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
RD=/d/ym-3x4-room-run/p0-ball
W=$RD/p34; mkdir -p $W; cd $W
DEV="seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-"
L=$W/P34.hbp
T=${1:-93000000}
PASSES=${2:-12}
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
echo "P34_START|at=$(stamp)|solve_t_milli=$T|full_passes=$PASSES|inner=16:200|perroncert_sha256=$(sha256sum $RD/perroncert.exe | cut -c1-64)|json=0" >> $L
t0=$(date +%s)
PERRONCERT_INNER=16:200 PERRONCERT_CHECK_EVERY=6 $RD/perroncert.exe solve "$DEV" 0 1000 9000 "$T" "$PASSES" "D:/ym-3x4-room-run/p0-ball/p34/d$T.bin" > "$W/solve-$T.out" 2> "$W/solve-$T.err"
rc=$?
echo "P34_SOLVE|exit=$rc|secs=$(( $(date +%s)-t0 ))|at=$(stamp)|json=0" >> $L
grep -E '^PERRONCERT(_PROGRESS)?\|' "$W/solve-$T.out" >> $L
[ -f "$W/d$T.bin" ] && echo "P34_D|file=d$T.bin|bytes=$(stat -c %s "$W/d$T.bin")|sha256=$(sha256sum "$W/d$T.bin" | cut -c1-64)|json=0" >> $L
echo "DONE|exit=$rc|at=$(stamp)|json=0" >> $L
