# usage: source hbp.sh; row TAG k=v k=v ...  appends TAG|at=<utc>|k=v|...|json=0 to REVIEW.hbp and echoes it.
RV=C:/tmp/opus55/allpairs-review-20261103/REVIEW.hbp
row() {
  local tag="$1"; shift
  local s="$tag|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  for kv in "$@"; do s="$s|$kv"; done
  s="$s|json=0"
  printf '%s\n' "$s" >> "$RV"
  printf '%s\n' "$s"
}
