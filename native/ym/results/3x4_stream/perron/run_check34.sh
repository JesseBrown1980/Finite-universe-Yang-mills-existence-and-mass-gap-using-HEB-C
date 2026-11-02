#!/bin/bash
# Checks the final d of the 3x4 Perron run. Read-only on the store. The operator was told this step follows the solve.
# perroncert check first (PERRON-RULE-DRAFT names its value), then the separately written check_d_stream.py.
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
RD=/d/ym-3x4-room-run/p0-ball
W=$RD/p34
L=$W/CHECK34.hbp
PY="$1"
T=93000000
DEV_RS="seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-"
DEV_PY="341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-"
DF="D:/ym-3x4-room-run/p0-ball/p34/d$T.bin"
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }

echo "CHECK34_START|at=$(stamp)|d_sha256=$(sha256sum $W/d$T.bin | cut -c1-64)|perroncert_sha256=$(sha256sum $RD/perroncert.exe | cut -c1-64)|check_d_stream_sha256=$(sha256sum $RD/check_d_stream.py | cut -c1-64)|json=0" >> $L

t0=$(date +%s)
$RD/perroncert.exe check "$DEV_RS" 0 1000 9000 "$DF" > "$W/check-perroncert.out" 2> "$W/check-perroncert.err"
rc1=$?
echo "CHECK34_PERRONCERT|exit=$rc1|secs=$(( $(date +%s)-t0 ))|at=$(stamp)|json=0" >> $L
grep -E '^PERRONCERT\|' "$W/check-perroncert.out" | tr -d '\r' >> $L

t0=$(date +%s)
"$PY" -I D:/ym-3x4-room-run/p0-ball/check_d_stream.py "$DEV_PY" "$DF" 1000 9000 > "$W/check-stream.out" 2> "$W/check-stream.err"
rc2=$?
echo "CHECK34_STREAM|exit=$rc2|secs=$(( $(date +%s)-t0 ))|at=$(stamp)|json=0" >> $L
grep -E '^CHECK_D\|' "$W/check-stream.out" | tr -d '\r' >> $L

echo "DONE|perroncert_exit=$rc1|stream_exit=$rc2|at=$(stamp)|json=0" >> $L
