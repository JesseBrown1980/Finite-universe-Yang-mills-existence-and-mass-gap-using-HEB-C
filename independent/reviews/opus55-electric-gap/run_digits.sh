#!/bin/bash
# The engine at thresholds that stopped closed at 40 digits, with more guard digits. Low priority, two at a time.
export MSYS_NO_PATHCONV=1 PYTHONDONTWRITEBYTECODE=1
A=C:/tmp/opus55/attack-electric-20261103
OUT=$A/engine_digits
mkdir -p "$OUT"
one() {
  T=$1
  D=$2
  S=$(date +%s)
  nice -n 10 python3 -I -X utf8 "$A/mine/engine_digits.py" "$A/wt/independent/gpt6_sturm_interval.py" "$A/sector" "$T" "$D" > "$OUT/t_${T}_d_$D.out" 2> "$OUT/t_${T}_d_$D.err"
  rc=$?
  echo "ATTACK_DIGITS|T=$T|digits=$D|exit=$rc|seconds=$(( $(date +%s)-S ))|row=$(grep GPT6_STURM "$OUT/t_${T}_d_$D.out" | tr -d '\r\n')|sectors_done=$(grep -c GPT6_SECTOR "$OUT/t_${T}_d_$D.err")|last_err=$(tail -1 "$OUT/t_${T}_d_$D.err" | tr -d '\r' | cut -c1-90)|json=0" >> "$OUT/runs.log"
}
export -f one
export A OUT
printf '%s\n' "$@" | xargs -P 2 -L 1 bash -c 'one $0 $1'
echo "ATTACK_DIGITS_DONE|json=0" >> "$OUT/runs.log"
