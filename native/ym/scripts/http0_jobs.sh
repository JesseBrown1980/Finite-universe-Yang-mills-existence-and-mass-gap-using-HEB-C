#!/bin/bash
# Run jobs through the HEB-C HTTP-0 server: start `hebc_ym_http0 serve`, POST /job/<spec>
# and GET /verify/<spec> for each spec in order, require PASS for both, then stop.
# usage: scripts/http0_jobs.sh BIN ROOT PORT SPEC [SPEC ...]      json=0
set -euo pipefail
B=$1; R=$2; P=$3; shift 3
mkdir -p "$R"
n=$(( 2 * $# + 1 ))
"$B" serve "$R" "$P" "$n" > "$R.serve.log" 2>&1 &
pid=$!
for _ in $(seq 200); do grep -q READY "$R.serve.log" 2>/dev/null && break; sleep 0.1; done
grep -q READY "$R.serve.log" || { echo "HTTP0_JOBS|error=server_not_ready|json=0"; cat "$R.serve.log"; exit 2; }
curl -s "http://127.0.0.1:$P/health" > /dev/null
for s in "$@"; do
  out=$(curl -s --max-time 21000 -X POST "http://127.0.0.1:$P/job/$s")
  case "$out" in HEBC_YM\|result=PASS*) ;; *) echo "HTTP0_JOBS|error=job|spec=$s|$out"; kill $pid; exit 1 ;; esac
  out=$(curl -s --max-time 21000 "http://127.0.0.1:$P/verify/$s")
  case "$out" in *result=PASS*) ;; *) echo "HTTP0_JOBS|error=verify|spec=$s|$out"; kill $pid; exit 1 ;; esac
  echo "HTTP0_JOBS|spec=$s|job=PASS|verify=PASS|json=0"
done
wait $pid
