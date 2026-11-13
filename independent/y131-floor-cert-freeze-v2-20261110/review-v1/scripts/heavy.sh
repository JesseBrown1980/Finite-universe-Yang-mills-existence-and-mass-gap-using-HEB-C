#!/bin/bash
set -u
R=/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor
FB=$R/work/design/rs/target/release/floorcert
PK="python3 -I -B $R/work/design/peak_rss.py"
O=$R/work/verify_opus55/heavy
mkdir -p $O
cd $R/work/design
L=$O/log.txt
echo "START $(date -u +%FT%TZ)" > $L
$PK $FB rowhash --m0 11 --threads 2 --dir $O/rh11 > $O/rh11.txt 2>&1 || true
mkdir -p $O/rh11 2>/dev/null
grep -E 'ROWHASH_ONLY|PEAK_RSS' $O/rh11.txt >> $L; sha256sum $O/rh11/core_keys_m11.bin >> $L 2>&1
H=$R/work/design/out/fix1/honest_m11
$PK $FB cert --m0 11 --r 21/2 --f '8,7,6,5,4' --write-cert --threads 2 --dir $H > $O/honest11_writer.txt 2>&1
grep -E '^(CERT|PEAK_RSS|WROTE)' $O/honest11_writer.txt | cut -c1-400 >> $L
sha256sum $H/cert_m11_r21_2_f8-7-6-5-4.txt >> $L
/usr/bin/time -v bash $R/work/design/gate_required.sh $H/cert_m11_r21_2_f8-7-6-5-4.txt > $O/honest11_gate.txt 2> $O/honest11_gate.time
echo "gate_rc=$?" >> $L
sha256sum $O/honest11_gate.txt >> $L
grep -E 'Elapsed|Maximum resident' $O/honest11_gate.time >> $L
echo "MID $(date -u +%FT%TZ)" >> $L
$PK $FB rowhash --m0 12 --threads 2 --dir $O/rh12 > $O/rh12.txt 2>&1
grep -E 'ROWHASH_ONLY|PEAK_RSS' $O/rh12.txt >> $L; sha256sum $O/rh12/core_keys_m12.bin >> $L 2>&1
$PK $FB rowhash --m0 13 --threads 2 --dir $O/rh13 > $O/rh13.txt 2>&1
grep -E 'ROWHASH_ONLY|PEAK_RSS' $O/rh13.txt >> $L; sha256sum $O/rh13/core_keys_m13.bin >> $L 2>&1
echo "END $(date -u +%FT%TZ)" >> $L
