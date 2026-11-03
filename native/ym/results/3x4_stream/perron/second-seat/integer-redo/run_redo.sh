#!/bin/bash
# The second seat's four fuzzers again, integer only, at below normal priority. Results go to REDO-RUNS.hbp, each with its exit and its last line.
export MSYS_NO_PATHCONV=1
export PYTHONDONTWRITEBYTECODE=1
cd C:/tmp/ym-float-redo || exit 9
L=REDO-RUNS.hbp
run() { local tag=$1; shift; local t0=$(date +%s); python3 -X utf8 "$@" > "$tag.out" 2> "$tag.err"; local c=$?; printf 'REDO|file=%s|exit=%d|wall_secs=%d|at=%s|last=%s|json=0\n' "$tag" "$c" "$(( $(date +%s) - t0 ))" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(tail -1 "$tag.out" | tr -d '\r' | cut -c1-300)" >> "$L"; }
run c3_random second-seat-integer/c3_random.py 27 3000
run c2_acc second-seat-integer/c2_acc.py
run c2_fuzz second-seat-integer/c2_fuzz.py 27 300
run c4b_open second-seat-integer/c4b_open.py
printf 'REDO_DONE|at=%s|json=0\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$L"
