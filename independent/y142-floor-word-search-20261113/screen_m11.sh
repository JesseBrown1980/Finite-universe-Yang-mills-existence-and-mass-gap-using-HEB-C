#!/bin/bash
# screen_m11.sh - the one screening campaign of PROTOCOL-WORD-SEARCH.hbp. Runs inside WSL, one word at a time.
# It calls the frozen binary of the protected r = 9 run (never rebuilt, never the launcher) at cutoff 11 only.
# usage: bash screen_m11.sh /path/to/WORDS.txt
set -u
B=/root/floor-r9; C=c8dbcdbf990114292313cbc410a745a14ba0b778
P=9f1076dd756d5b3ff3cb7c18974f52ce1c088f23e06ca3077ac05ab66f44f99c
ROOT=$B/repo/independent/y131-floor-cert-freeze-v2-20261110
FB=$ROOT/work/run9/target/release/floorcert
S=/root/floor-word-search; WORDS=$1
[ -e $S/SCREEN.started ] && { echo "SCREEN|already started once, refusing"; exit 9; }
[ "$(sha256sum $FB | cut -d' ' -f1)" = 027b05152ac9f5fa79b3824e47956af3220faee53ccb5d34433d179873f8ba85 ] || { echo "SCREEN|binary hash differs"; exit 8; }
[ "$(sha256sum $ROOT/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp | cut -d' ' -f1)" = $P ] || { echo "SCREEN|prediction file hash differs"; exit 8; }
mkdir -p $S/log && date -u +%FT%TZ > $S/SCREEN.started
cp "$WORDS" $S/WORDS.txt; T0=$(date +%s); n=0
while read -r w; do
  w=$(echo "$w" | tr -d '\r ')
  [ -n "$w" ] || continue
  n=$((n+1)); tag=$(echo "$w" | tr ',' '-'); D=$S/m11_$tag
  if [ $(( $(date +%s) - T0 )) -gt 9000 ]; then echo "SCREENED|n=$n|f=$w|status=NOT_RUN_time_limit_150_min|json=0" | tee -a $S/SCREEN.hbp; continue; fi
  mkdir -p $D && cp $ROOT/work/run9/RUN11/core_keys_m11.bin $D/
  ( cd $ROOT && ulimit -v 2097152 && timeout 1200 env -i PATH=/usr/bin:/bin LANG=C $FB cert --m0 11 --r 9 --f "$w" --threads 2 --dir $D --freeze-commit $C --prediction final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp --prediction-sha256 $P ) > $S/log/m11_$tag.txt 2>&1 < /dev/null
  e=$?
  cert=$(grep '^CERT|' $S/log/m11_$tag.txt | head -1)
  if [ -n "$cert" ]; then
    echo "SCREENED|n=$n|f=$w|exit=$e|$(echo "$cert" | tr '|' '\n' | grep -E '^(gamma|row_check|ritz_upper|tail_cap|secs)=' | tr '\n' '|')status=CERT_LINE|json=0" | tee -a $S/SCREEN.hbp
  else
    echo "SCREENED|n=$n|f=$w|exit=$e|status=NO_CERT_LINE|last=$(tail -1 $S/log/m11_$tag.txt | cut -c1-160 | tr '|' '/')|json=0" | tee -a $S/SCREEN.hbp
  fi
  rm -f $D/core_keys_m11.bin
done < $S/WORDS.txt
date -u +%FT%TZ > $S/SCREEN.done
echo "SCREENEND|words=$n|seconds=$(( $(date +%s) - T0 ))|json=0" | tee -a $S/SCREEN.hbp
