#!/bin/bash
# Fail-closed checks of both 3x4 certificate vectors, on the operator's word of 2026-11-02: "run check_d_strict.py on both the
# 93.061 and 93.7 vectors once the warm start finishes". It waits for the warm start's DONE row, then reads the store three
# times, one job after another, at the priority it was started with. Read-only on the store, the key table and both vectors.
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
export MSYS_NO_PATHCONV=1
RD=/d/ym-3x4-room-run/p0-ball
W=$RD/p34
L=$W/STRICT34.hbp
PY="$1"
DEV_RS="seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-"
DEV_PY="341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-"
PA=D:/ym-3x4-room-run/passA.bin
D93=D:/ym-3x4-room-run/p0-ball/p34/d93000000.bin
D937=D:/ym-3x4-room-run/p0-ball/p34/d93700000.bin
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }

echo "STRICT34_WAIT|at=$(stamp)|for=WARM34_DONE|json=0" >> $L
until grep -q '^DONE' $W/WARM34.hbp; do sleep 60; done
done_row=$(grep '^DONE' $W/WARM34.hbp | tail -1)
echo "STRICT34_START|at=$(stamp)|warm_row=$done_row|strict_sha256=$(sha256sum $RD/check_d_strict.py | cut -c1-64)|perroncert_sha256=$(sha256sum $RD/perroncert.exe | cut -c1-64)|d93_sha256=$(sha256sum $W/d93000000.bin | cut -c1-64)|json=0" >> $L

# The vector at 93 J_E: all row checks, the key table, and the self-adjoint test.
echo "STRICT34_PREDICT|written_before_run=1|vector=d93000000.bin|t_cert_milli=93061051|min_row=44742735|min_mag=3|flats=7|min_nonflat_M=3|max_M=36|row_sums_zero=PASS|passa_w_and_M=PASS|W_self_adjoint=PASS|merkle=PASS|json=0" >> $L
t0=$(date +%s)
"$PY" -I D:/ym-3x4-room-run/p0-ball/check_d_strict.py "$DEV_PY" "$D93" 1000 9000 --passa "$PA" --self-adjoint 27 > "$W/strict-d93.out" 2> "$W/strict-d93.err"
rc=$?
echo "STRICT34_RUN|vector=d93000000.bin|exit=$rc|secs=$(( $(date +%s)-t0 ))|at=$(stamp)|json=0" >> $L
tr -d '\r' < "$W/strict-d93.out" >> $L

# The warm-start vector, when the solve finished and saved it.
if echo "$done_row" | grep -q '^DONE|exit=0|' && [ -f "$W/d93700000.bin" ]; then
  row=$(grep -E '^PERRONCERT\|' "$W/warm-93700000.out" | tail -1 | tr -d '\r')
  tc=$(echo "$row" | sed -E 's/.*\|t_cert_milli=([-0-9]+)\|.*/\1/')
  mr=$(echo "$row" | sed -E 's/.*\|min_row=([0-9]+)\|.*/\1/')
  mm=$(echo "$row" | sed -E 's/.*\|min_mag=([0-9]+)\|.*/\1/')
  echo "STRICT34_PREDICT|written_before_run=1|vector=d93700000.bin|source=warm_solve_row|t_cert_milli=$tc|min_row=$mr|min_mag=$mm|d_sha256=$(sha256sum $W/d93700000.bin | cut -c1-64)|merkle=PASS|json=0" >> $L
  t0=$(date +%s)
  $RD/perroncert.exe check "$DEV_RS" 0 1000 9000 "$D937" > "$W/check-perroncert-d937.out" 2> "$W/check-perroncert-d937.err"
  rc2=$?
  echo "STRICT34_RUN|vector=d93700000.bin|tool=perroncert_check|exit=$rc2|secs=$(( $(date +%s)-t0 ))|at=$(stamp)|json=0" >> $L
  grep -E '^PERRONCERT' "$W/check-perroncert-d937.out" | tr -d '\r' >> $L
  t0=$(date +%s)
  "$PY" -I D:/ym-3x4-room-run/p0-ball/check_d_strict.py "$DEV_PY" "$D937" 1000 9000 --passa "$PA" > "$W/strict-d937.out" 2> "$W/strict-d937.err"
  rc3=$?
  echo "STRICT34_RUN|vector=d93700000.bin|tool=check_d_strict|exit=$rc3|secs=$(( $(date +%s)-t0 ))|at=$(stamp)|json=0" >> $L
  tr -d '\r' < "$W/strict-d937.out" >> $L
  echo "DONE|d93_exit=$rc|d937_perroncert_exit=$rc2|d937_strict_exit=$rc3|at=$(stamp)|json=0" >> $L
else
  echo "DONE|d93_exit=$rc|d937=warm_start_gave_no_vector|at=$(stamp)|json=0" >> $L
fi
