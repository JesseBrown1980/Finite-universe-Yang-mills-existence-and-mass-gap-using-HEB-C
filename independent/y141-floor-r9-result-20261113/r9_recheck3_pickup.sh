set -u
# Pick-up of the recheck (operator, 2026-11-13: "pick up on it from where it dropped off, because you already have the
# certificates"). Attempt 2 rechecked the six certificates of cutoffs 11 and 12 (all PASS) and was stopped by the host
# for low memory before cutoff 13. This runs the SAME pinned gate command the checker runs (recheck_floor.py line 424),
# in the same clean clone and environment, on the three cutoff-13 certificates only. One at a time.
B=/root/floor-r9; C=c8dbcdbf990114292313cbc410a745a14ba0b778
P=9f1076dd756d5b3ff3cb7c18974f52ce1c088f23e06ca3077ac05ab66f44f99c
ROOT=$B/chk/independent/y131-floor-cert-freeze-v2-20261110
[ -e $B/recheck3.done ] && { echo "RECHECK3|already ran, refusing"; exit 9; }
[ "$(git -C $B/chk rev-parse HEAD)" = $C ] || { echo "RECHECK3|clone head differs"; exit 8; }
[ -z "$(git -C $B/chk status --short)" ] || { echo "RECHECK3|clone not clean"; exit 8; }
cd $ROOT || exit 7
date -u +%FT%TZ > $B/recheck3.start
n=6
for f in cert_m13_r9_1_f1.txt cert_m13_r9_1_f8-7-6-5-4.txt cert_m13_r9_1_f6-5-4-3.txt; do
  n=$((n+1)); full=$B/second/run9/RUN13/$f
  env -i PATH=/usr/bin:/bin LANG=C bash --noprofile --norc work/design/gate_required.sh "$full" --freeze-commit $C --prediction final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp --prediction-sha256 $P > $B/recheck3.gate_${n}_$f.txt 2>&1
  e=$?
  echo "PICKUP|n=$n|certificate=RUN13/$f|sha256=$(sha256sum "$full" | cut -d' ' -f1)|gate_exit=$e|$(tail -1 $B/recheck3.gate_${n}_$f.txt | cut -c1-40)|$(grep '^VERDICT' $B/recheck3.gate_${n}_$f.txt | cut -c1-110)|ended=$(date -u +%T)" | tee -a $B/recheck3.txt
done
date -u +%FT%TZ > $B/recheck3.done
