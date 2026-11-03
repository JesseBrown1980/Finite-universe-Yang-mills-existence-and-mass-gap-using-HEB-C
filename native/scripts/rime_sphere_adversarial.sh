#!/usr/bin/env bash
# Stage 2J adversarial carrier regression (review 5643283114).
#
# Runs every fixture in tests/fixtures/rime_sphere through a decoder as a
# BOUNDED SUBPROCESS: virtual memory capped by ulimit, wall time by timeout.
# An oversized header therefore cannot exhaust CI memory; it can only fail.
#
#   valid.rime  -> exit 0 and bytes identical to input.bin
#   every other -> exit exactly 1 with a "FAIL|reason=" line
#
# Anything else is a regression: 101 (panic), 134 (abort), 124 (timeout),
# 137 (killed), or 0 (silently accepted).
#
# usage: rime_sphere_adversarial.sh DECODER...
#   DECODER is a command prefix taking "CARRIER OUT", e.g.
#     target/release/hebc rime-sphere-decode
#     python3 scripts/rime_sphere_carrier.py --decode
set -u
here="$(cd "$(dirname "$0")/.." && pwd)"
fx="$here/tests/fixtures/rime_sphere"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
fail=0
total=0
for f in "$fx"/*.rime; do
  name="$(basename "$f")"
  out="$work/out.bin"; rm -f "$out"
  err="$( (ulimit -v 2097152; timeout 30 "$@" "$f" "$out") 2>&1 >/dev/null )"
  rc=$?
  total=$((total + 1))
  if [ "$name" = valid.rime ]; then
    if [ $rc -eq 0 ] && cmp -s "$out" "$fx/input.bin"; then verdict=ok; else verdict=REGRESSION; fi
  else
    if [ $rc -eq 1 ] && printf '%s' "$err" | grep -q 'FAIL|reason='; then verdict=ok; else verdict=REGRESSION; fi
  fi
  [ $verdict = ok ] || fail=$((fail + 1))
  printf '%-34s rc=%-4s %-10s %s\n' "$name" "$rc" "$verdict" "$(printf '%s' "$err" | tail -1 | cut -c1-90)"
done
echo "ADVERSARIAL|decoder=$*|fixtures=$total|regressions=$fail|json=0"
[ $fail -eq 0 ]
