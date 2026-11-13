#!/bin/bash
# run_m13.sh - WSNEXT of PROTOCOL-WORD-SEARCH.hbp: the ONE cutoff-13 certificate of the word search, for the word
# sealed in PREDICT-WORD-SEARCH-M13.hbp, written with the frozen binary and passed through the pinned verifier.
# usage: bash run_m13.sh        (inside WSL; runs once; refuses a second start)
set -u
W=81,54,36,24,16
B=/root/floor-r9; C=c8dbcdbf990114292313cbc410a745a14ba0b778
P=9f1076dd756d5b3ff3cb7c18974f52ce1c088f23e06ca3077ac05ab66f44f99c
ROOT=$B/repo/independent/y131-floor-cert-freeze-v2-20261110
CHK=$B/chk/independent/y131-floor-cert-freeze-v2-20261110
FB=$ROOT/work/run9/target/release/floorcert
S=/root/floor-word-search; D=$S/run_m13
[ -e $S/M13.started ] && { echo "M13|already started once, refusing"; exit 9; }
[ -e $S/CONFIRM.done ] || { echo "M13|confirmation not finished"; exit 8; }
[ "$(sha256sum $FB | cut -d' ' -f1)" = 027b05152ac9f5fa79b3824e47956af3220faee53ccb5d34433d179873f8ba85 ] || { echo "M13|binary hash differs"; exit 8; }
[ "$(sha256sum $ROOT/work/run9/RUN13/core_keys_m13.bin | cut -d' ' -f1)" = b67d54ab32d0c33ac8b1cbd783fa6579c0f7423a342c169a58e4b7c8e86bbc94 ] || { echo "M13|key file hash differs"; exit 8; }
[ "$(git -C $B/chk rev-parse HEAD)" = $C ] || { echo "M13|clone head differs"; exit 8; }
[ -z "$(git -C $B/chk status --short)" ] || { echo "M13|clone not clean"; exit 8; }
date -u +%FT%TZ > $S/M13.started
mkdir -p $D && cp $ROOT/work/run9/RUN13/core_keys_m13.bin $D/
T0=$(date +%s)
( cd $ROOT && ulimit -v 4194304 && timeout 3600 env -i PATH=/usr/bin:/bin LANG=C $FB cert --m0 13 --r 9 --f "$W" --write-cert --threads 2 --dir $D --freeze-commit $C --prediction final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp --prediction-sha256 $P ) > $S/log/run_m13.txt 2>&1 < /dev/null
e=$?
rm -f $D/core_keys_m13.bin
cert=$(ls $D/cert_*.txt 2>/dev/null | head -1)
echo "M13WRITE|f=$W|exit=$e|seconds=$(( $(date +%s) - T0 ))|$(grep '^CERT|' $S/log/run_m13.txt | head -1 | tr '|' '\n' | grep -E '^(gamma|row_check|ritz_upper|tail_cap)=' | tr '\n' '|')certificate=$(basename "$cert")|sha256=$(sha256sum "$cert" | cut -d' ' -f1)|bytes=$(stat -c %s "$cert")|json=0" | tee -a $S/M13.hbp
[ -n "$cert" ] || { echo "M13GATE|no certificate file|json=0" | tee -a $S/M13.hbp; date -u +%FT%TZ > $S/M13.done; exit 1; }
cd $CHK || exit 7
env -i PATH=/usr/bin:/bin LANG=C bash --noprofile --norc work/design/gate_required.sh "$cert" --freeze-commit $C --prediction final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp --prediction-sha256 $P > $S/log/run_m13_gate.txt 2>&1
g=$?
echo "M13GATE|gate_exit=$g|$(tail -1 $S/log/run_m13_gate.txt | cut -c1-40)|$(grep '^VERDICT' $S/log/run_m13_gate.txt | cut -c1-160)|json=0" | tee -a $S/M13.hbp
date -u +%FT%TZ > $S/M13.done
