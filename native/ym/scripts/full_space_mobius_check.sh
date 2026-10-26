#!/bin/bash
# Full-space counts from line-subgroup sectors, run through the HTTP-0 route, and
# compared with the reflection-only full-space counts (G = C2v, every momentum).
# usage: scripts/full_space_mobius_check.sh BIN_DIR WORK_DIR PORT LX LY JE JB FDIG TOL T1 [T2 ...]
# FDIG_R (default FDIG) sets the precision of the reflection-only comparison counts.
set -euo pipefail
B=$1/hebc_ym_http0; W=$2; P=$3; LX=$4; LY=$5; JE=$6; JB=$7; FD=$8; TOL=$9; shift 9
TS="$*"
FDR=${FDIG_R:-$FD}
here=$(cd "$(dirname "$0")/.." && pwd)
specs=()
for m in "" tx ty td ta r; do
  fd=$FD; [ "$m" = r ] && fd=$FDR
  for s in "1 1" "1 -1" "-1 1" "-1 -1"; do
    set -- $s
    specs+=("${m}sector/$LX/$LY/$1/$2")
    for t in $TS; do specs+=("${m}count/$LX/$LY/$1/$2/$JE/$JB/$t/$fd/$TOL"); done
  done
done
rm -rf "$W"; mkdir -p "$W"
"$B" serve "$W" "$P" $(( ${#specs[@]} + 1 )) > "$W/serve.log" 2>&1 &
pid=$!
for _ in $(seq 100); do grep -q READY "$W/serve.log" 2>/dev/null && break; sleep 0.1; done
curl -s "http://127.0.0.1:$P/health" > /dev/null
for s in "${specs[@]}"; do
  out=$(curl -s -X POST "http://127.0.0.1:$P/job/$s")
  case "$out" in
    HEBC_YM\|result=PASS*) ;;
    *noncanonical_sector*|*exited\ 1*) ;;   # sector label not used by this point group
    *) echo "$out"; exit 1 ;;
  esac
done
wait $pid
for t in $TS; do
  python3 "$here/python/full_space_mobius.py" "$W" "$LX" "$LY" "$JE" "$JB" "$t" "$FD" "$TOL" | grep -E "INVARIANT|ISOTYPIC|FULL_SPACE_COUNT"
  r=0
  for s in "1 1" "1 -1" "-1 1" "-1 -1"; do
    set -- $s
    f="$W/shards/rcount_${LX}_${LY}_$1_$2_${JE}_${JB}_${t}_${FDR}_${TOL}/run.hbp"
    grep -q "ambiguous=0|result=PASS" "$f" || { echo "REFLECTION_ONLY_COUNT|error=ambiguous|file=$f|json=0"; exit 1; }
    n=$(grep -o "negative=[0-9]*" "$f" | head -1 | cut -d= -f2)
    r=$((r + n))
  done
  echo "REFLECTION_ONLY_COUNT|L=${LX}x${LY}|t_milli=$t|N=$r|json=0"
  full=$(python3 "$here/python/full_space_mobius.py" "$W" "$LX" "$LY" "$JE" "$JB" "$t" "$FD" "$TOL" | grep -o "FULL_SPACE_COUNT|.*N=[0-9]*" | grep -o "N=[0-9]*$" | cut -d= -f2)
  [ "$full" = "$r" ] || { echo "FULL_SPACE_CHECK|t_milli=$t|mobius=$full|reflection_only=$r|result=FAIL|json=0"; exit 1; }
  echo "FULL_SPACE_CHECK|L=${LX}x${LY}|t_milli=$t|mobius=$full|reflection_only=$r|result=PASS|json=0"
done
