#!/bin/bash
# Headless command vs HTTP-0 route: identical canonical bytes from identical inputs.
# usage: scripts/route_identity.sh BIN_DIR WORK_DIR PORT SPEC...
set -euo pipefail
B=$1/hebc_ym_http0; W=$2; P=$3; shift 3
rm -rf "$W/cli" "$W/http"; mkdir -p "$W"
for s in "$@"; do "$B" job "$W/cli" "$s" > /dev/null; done
n=$(( $# + 2 ))
"$B" serve "$W/http" "$P" "$n" > "$W/serve.log" 2>&1 &
pid=$!
for _ in $(seq 50); do grep -q READY "$W/serve.log" 2>/dev/null && break; sleep 0.1; done
curl -s "http://127.0.0.1:$P/health" > /dev/null
for s in "$@"; do curl -s -X POST "http://127.0.0.1:$P/job/$s" | grep -q '^HEBC_YM|result=PASS|'; done
curl -s "http://127.0.0.1:$P/verify/$1" | grep -q '^HEBC_YM|result=PASS|action=verify|'
wait $pid
same=0; total=0
for d in "$W"/cli/shards/*/; do
  id=$(basename "$d"); total=$((total+1))
  for f in run.hbp index.hbi run.anchor; do cmp -s "$d/$f" "$W/http/shards/$id/$f" || { echo "ROUTE_IDENTITY|shard=$id|file=$f|identical=0|json=0"; exit 1; }; done
  same=$((same+1))
done
echo "ROUTE_IDENTITY|shards=$total|identical=$same|compared=run.hbp,index.hbi,run.anchor|runtime_metadata_excluded=run.measure|result=PASS|json=0"
