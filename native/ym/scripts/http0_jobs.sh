#!/bin/bash
# Run jobs through the HEB-C HTTP-0 server: start `hebc_ym_http0 serve`, POST /job/<spec>
# and GET /verify/<spec> for each spec in order, require PASS for both, then stop.
# Fails closed: the request plan must fit the server cap, the server must start, every
# request must complete, and the server must exit after exactly the planned requests.
# Writes $OUT_ID (default out/HTTP0.hbp) with the identity and the request accounting.
# usage: scripts/http0_jobs.sh BIN ROOT PORT SPEC [SPEC ...]      json=0
set -euo pipefail
B=$1; R=$2; P=$3; shift 3
CAP=10000
ID=${OUT_ID:-out/HTTP0.hbp}; mkdir -p "$(dirname "$ID")" "$R"
planned=$(( 2 * $# + 1 ))
bsha=$(sha256sum "$B" | cut -c1-64)
[ "$planned" -le "$CAP" ] || { echo "HTTP0_JOBS|error=plan_exceeds_cap|planned=$planned|cap=$CAP|json=0" | tee -a "$ID"; exit 2; }
"$B" serve "$R" "$P" "$planned" > "$R.serve.log" 2>&1 &
pid=$!
for _ in $(seq 200); do grep -q READY "$R.serve.log" 2>/dev/null && break; kill -0 $pid 2>/dev/null || break; sleep 0.1; done
grep -q READY "$R.serve.log" || { echo "HTTP0_JOBS|error=server_not_ready|json=0" | tee -a "$ID"; cat "$R.serve.log"; exit 2; }
done_=0
curl -sf "http://127.0.0.1:$P/health" > /dev/null && done_=$((done_ + 1))
for s in "$@"; do
  out=$(curl -s --max-time 21000 -X POST "http://127.0.0.1:$P/job/$s") || true
  case "$out" in HEBC_YM\|result=PASS*) done_=$((done_ + 1)) ;; *) echo "HTTP0_JOBS|error=job|spec=$s|$out" | tee -a "$ID"; kill $pid 2>/dev/null; exit 1 ;; esac
  out=$(curl -s --max-time 21000 "http://127.0.0.1:$P/verify/$s") || true
  case "$out" in *result=PASS*) done_=$((done_ + 1)) ;; *) echo "HTTP0_JOBS|error=verify|spec=$s|$out" | tee -a "$ID"; kill $pid 2>/dev/null; exit 1 ;; esac
  echo "HTTP0_JOBS|seq=$(( done_ / 2 ))|spec=$s|job=PASS|verify=PASS|json=0" | tee -a "$ID"
done
rc=0; wait $pid || rc=$?
echo "HTTP0_IDENTITY|binary_sha256=$bsha|cap=$CAP|planned=$planned|completed=$done_|server_exit=$rc|json=0" | tee -a "$ID"
[ "$done_" -eq "$planned" ] && [ "$rc" -eq 0 ] || { echo "HTTP0_JOBS|error=request_accounting|json=0"; exit 2; }
