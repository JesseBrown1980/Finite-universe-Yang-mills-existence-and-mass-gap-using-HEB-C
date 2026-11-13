#!/bin/bash
# confirm_m11.sh - WSCONFIRM of PROTOCOL-WORD-SEARCH.hbp: the screening winner is written as a certificate at cutoff 11
# with the frozen binary and passed through the pinned verifier (same gate command as the recheck of the protected run).
# usage: bash confirm_m11.sh        (inside WSL; runs once)
set -u
W=81,54,36,24,16
B=/root/floor-r9; C=c8dbcdbf990114292313cbc410a745a14ba0b778
P=9f1076dd756d5b3ff3cb7c18974f52ce1c088f23e06ca3077ac05ab66f44f99c
ROOT=$B/repo/independent/y131-floor-cert-freeze-v2-20261110
CHK=$B/chk/independent/y131-floor-cert-freeze-v2-20261110
FB=$ROOT/work/run9/target/release/floorcert
S=/root/floor-word-search; D=$S/confirm_m11
[ -e $S/CONFIRM.started ] && { echo "CONFIRM|already started once, refusing"; exit 9; }
[ -e $S/SCREEN.done ] || { echo "CONFIRM|screening not finished"; exit 8; }
[ "$(sha256sum $FB | cut -d' ' -f1)" = 027b05152ac9f5fa79b3824e47956af3220faee53ccb5d34433d179873f8ba85 ] || { echo "CONFIRM|binary hash differs"; exit 8; }
[ "$(git -C $B/chk rev-parse HEAD)" = $C ] || { echo "CONFIRM|clone head differs"; exit 8; }
[ -z "$(git -C $B/chk status --short)" ] || { echo "CONFIRM|clone not clean"; exit 8; }
date -u +%FT%TZ > $S/CONFIRM.started
mkdir -p $D && cp $ROOT/work/run9/RUN11/core_keys_m11.bin $D/
( cd $ROOT && ulimit -v 2097152 && timeout 1800 env -i PATH=/usr/bin:/bin LANG=C $FB cert --m0 11 --r 9 --f "$W" --write-cert --threads 2 --dir $D --freeze-commit $C --prediction final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp --prediction-sha256 $P ) > $S/log/confirm_m11.txt 2>&1 < /dev/null
e=$?
rm -f $D/core_keys_m11.bin
cert=$(ls $D/cert_*.txt 2>/dev/null | head -1)
echo "CONFIRMWRITE|f=$W|exit=$e|$(grep '^CERT|' $S/log/confirm_m11.txt | head -1 | tr '|' '\n' | grep -E '^(gamma|row_check)=' | tr '\n' '|')certificate=$(basename "$cert")|sha256=$(sha256sum "$cert" | cut -d' ' -f1)|bytes=$(stat -c %s "$cert")|json=0" | tee -a $S/CONFIRM.hbp
[ -n "$cert" ] || { echo "CONFIRMGATE|no certificate file|json=0" | tee -a $S/CONFIRM.hbp; exit 1; }
cd $CHK || exit 7
env -i PATH=/usr/bin:/bin LANG=C bash --noprofile --norc work/design/gate_required.sh "$cert" --freeze-commit $C --prediction final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp --prediction-sha256 $P > $S/log/confirm_m11_gate.txt 2>&1
g=$?
echo "CONFIRMGATE|gate_exit=$g|$(tail -1 $S/log/confirm_m11_gate.txt | cut -c1-40)|$(grep '^VERDICT' $S/log/confirm_m11_gate.txt | cut -c1-160)|json=0" | tee -a $S/CONFIRM.hbp
date -u +%FT%TZ > $S/CONFIRM.done
