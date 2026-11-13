#!/bin/bash
# floor lane: text scan (no computation) of every .txt and .log in a FIXED list of work/ directories for r values, in
# two forms: r=<int>/<int> fields and --r <token> arguments. Usage: r_scan.sh OUT.
# File-type limit: ONLY *.txt and *.log are read. .out, .err, .sh, .py, .rs, .md, .json, .bin and binaries are not
# scanned (record row 096 says how those were checked). target/ dirs are excluded.
# OUT must lie outside work/, or end in .out (a type this scan never reads), so that a seat confined to its own
# work/<seat>/ folder can reproduce the receipt with this exact script.
# Listed dirs that do not exist yet (a pre-listed verifier folder) are skipped. Directories of work/ not in the list
# are named on stderr only; each needs its own DISCLOSE row and a place in the list.
# V2 (2026-11-10): F is the package root, two levels above this script (final/tools/), at any absolute location.
set -u
F=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)
W=$F/work
DIRS="map design critic critic2 review verify1_0 verify1_1 refix2 verify2_0 verify2_1 verify3_0"
OUT=${1:?usage: r_scan.sh OUT}
OUT=$(realpath -m "$OUT")
case "$OUT" in "$W"|"$W"/*) case "$OUT" in *.out) ;; *) echo "R_SCAN|REFUSE|output under work/ must end in .out" >&2; exit 2 ;; esac ;; esac
for d in $(ls "$W"); do
  case " $DIRS " in *" $d "*) ;; *) echo "R_SCAN_UNLISTED|dir=work/$d" >&2 ;; esac
done
EX=""
for d in $DIRS; do [ -d "$W/$d" ] && EX="$EX $d"; done
near9() { # integer test |a/b - 9| <= 1 on each comma-separated a/b or a token
  local t a b hit=""
  for t in $(echo "$1" | tr ',' ' '); do
    case "$t" in */*) a=${t%/*}; b=${t#*/} ;; *) a=$t; b=1 ;; esac
    [ -n "$a" ] && [ -n "$b" ] && [ "$b" -gt 0 ] && [ $((8 * b)) -le "$a" ] && [ "$a" -le $((10 * b)) ] && hit=1
  done
  [ -n "$hit" ]
}
cd "$W"
{
  echo "R_SCAN|dirs=$DIRS|exclude=target|files=*.txt,*.log|forms=(start_or_|_or_#_or_space)r=<int>/<int>_and_--r_<token>"
  grep -rhoE '(^|[|# ])r=[0-9]+/[0-9]+' --exclude-dir=target --include='*.txt' --include='*.log' $EX \
    | sed 's/^[|# ]//' | sort | uniq -c | sort -k1,1rn -k2 | awk '{print "R_VALUE|"$2"|occurrences="$1}'
  for v in 10/1 19/2 90000001/10000000 8/1 9/1; do
    echo "R_NEAR9|r=$v|files=$(grep -rlE "r=$v([^0-9]|$)" --exclude-dir=target --include='*.txt' --include='*.log' $EX | sort | tr '\n' ',')"
  done
  grep -rhoE -e '--r[ =][0-9]([0-9,/]*[0-9])?' --exclude-dir=target --include='*.txt' --include='*.log' $EX \
    | sed 's/^--r[ =]//' | sort | uniq -c | sort -k1,1rn -k2 | while read -r n v; do
      if near9 "$v"; then echo "R_ARG|--r=$v|occurrences=$n|near9=yes|files=$(grep -rlE -e "--r[ =]$v([^0-9,/]|$)" --exclude-dir=target --include='*.txt' --include='*.log' $EX | sort | tr '\n' ',')"
      else echo "R_ARG|--r=$v|occurrences=$n|near9=no"; fi
    done
} > "$OUT"
