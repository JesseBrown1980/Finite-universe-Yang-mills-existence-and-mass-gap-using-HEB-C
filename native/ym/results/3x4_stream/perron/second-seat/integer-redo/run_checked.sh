#!/bin/bash
# The four integer copies again, with every true division checked, at below normal priority. Compares each output with the plain run's. json=0.
export MSYS_NO_PATHCONV=1
export PYTHONDONTWRITEBYTECODE=1
cd C:/tmp/ym-float-redo || exit 9
C=C:/Users/acer/ym-vector-wt/native/ym/results/3x4_stream/perron/second-seat/integer-redo/checked_division.py
L=CHECKED-DIVISIONS.hbp
mask() { tr -d '\r' < "$1" | sed -E 's/ secs=[0-9]+//; s/\|secs_wall=[0-9]+//; /^CHECKED_DIVISION\|/d'; }
run() { local tag=$1; shift; local t0=$(date +%s); python3 -X utf8 "$C" "second-seat-integer/$tag.py" "$@" > "checked-$tag.out" 2> "checked-$tag.err"; local c=$?; local same=0; cmp -s <(mask "$tag.out") <(mask "checked-$tag.out") && same=1; printf 'CHECKED_DIVISION_RUN|script=%s|exit=%d|wall_secs=%d|rows_same_as_plain_run=%d|at=%s|%s\n' "$tag" "$c" "$(( $(date +%s) - t0 ))" "$same" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(grep -a '^CHECKED_DIVISION|' "checked-$tag.out" | tr -d '\r' | cut -d'|' -f3-)" >> "$L"; }
run c2_acc
run c2_fuzz 27 300
run c4b_open
run c3_random 27 3000
printf 'CHECKED_DIVISION_DONE|at=%s|json=0\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$L"
