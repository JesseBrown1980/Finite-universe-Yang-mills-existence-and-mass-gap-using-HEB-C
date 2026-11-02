#!/bin/bash
# W2: exact leading minors on the 3x3 90M midpoint matrix. Started detached on operator direction,
# "go on all three, I agree, yes" (2026-11-01). The verifier is native/ym/independent/minors,
# written separately from roomschur, shellschur and schurcert. It uses no intervals.
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
RD=/d/ym-3x4-room-run/schurcert-w2
IN=/d/ym-3x4-room-run/gate3x3-seg/roomschur-seg-t90000000.out
PY="$1"
L=$RD/W2.log
export WORKERS=6
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }

echo "W2_START|at=$(stamp)|workers=$WORKERS|pid=$$|json=0" >> "$L"
echo "W2_SHA|exe=$(sha256sum "$RD/indep-minors.exe" | cut -c1-64)|input=$(sha256sum "$IN" | cut -c1-64)|dump_mid=$(sha256sum "$RD/dump_mid.py" | cut -c1-64)|count_signs=$(sha256sum "$RD/count_signs.py" | cut -c1-64)|json=0" >> "$L"

t0=$(date +%s)
"$PY" -I "$(cygpath -w "$RD/dump_mid.py")" "$(cygpath -w "$RD/mid-c3x3-90M.txt")" 27 "$(cygpath -w "$IN")" >> "$L" 2>> "$RD/W2.err"
rc=$?
echo "W2_DUMP|exit=$rc|secs=$(( $(date +%s)-t0 ))|mid_sha256=$(sha256sum "$RD/mid-c3x3-90M.txt" | cut -c1-64)|at=$(stamp)|json=0" >> "$L"
if [ "$rc" -ne 0 ]; then echo "DONE|exit=dump_failed|at=$(stamp)|json=0" >> "$L"; exit 1; fi

t0=$(date +%s)
"$RD/indep-minors.exe" < "$RD/mid-c3x3-90M.txt" > "$RD/minors-c3x3-90M.out" 2>> "$RD/W2.err"
rc=$?
echo "W2_MINORS|exit=$rc|secs=$(( $(date +%s)-t0 ))|out_sha256=$(sha256sum "$RD/minors-c3x3-90M.out" | cut -c1-64)|at=$(stamp)|json=0" >> "$L"
"$PY" -I "$(cygpath -w "$RD/count_signs.py")" "$(cygpath -w "$RD/minors-c3x3-90M.out")" >> "$L" 2>> "$RD/W2.err"
echo "DONE|exit=$rc|at=$(stamp)|json=0" >> "$L"
