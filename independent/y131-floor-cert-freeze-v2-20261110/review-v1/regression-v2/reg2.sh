#!/bin/bash
# v2 regression, part 2 (heavy): m0 = 11 rowhash in an absent dir, then cert at the excluded r = 21/2 reusing that dir,
# then the required gate. Excluded r only.
set -u
P=/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110
FB=$P/work/design/rs/target/release/floorcert
PK="python3 -I -B $P/work/design/peak_rss.py"
O=/root/floor-v2/reg
rm -rf $O/RUN11 $O/part2.log $O/rh11.txt $O/honest11_writer.txt $O/honest11_gate.txt
mkdir -p $O
L=$O/part2.log
echo "START $(date -u +%FT%TZ) binary=$(sha256sum $FB | cut -d' ' -f1)" > $L
echo "RUN11_exists_before=$([ -e $O/RUN11 ] && echo 1 || echo 0)" >> $L
$PK $FB rowhash --m0 11 --threads 2 --dir $O/RUN11 > $O/rh11.txt 2>&1; echo "rowhash11_rc=$? dir_exists=$([ -d $O/RUN11 ] && echo 1 || echo 0)" >> $L
grep -E 'ROWHASH_ONLY|PEAK_RSS|ENUM|KEYS' $O/rh11.txt | cut -c1-300 >> $L
sha256sum $O/RUN11/core_keys_m11.bin >> $L
ls $O/RUN11 | tr '\n' ' ' >> $L; echo >> $L
$PK $FB cert --m0 11 --r 21/2 --f '8,7,6,5,4' --write-cert --threads 2 --dir $O/RUN11 > $O/honest11_writer.txt 2>&1; echo "cert11_rc=$?" >> $L
grep -E '^(KEYS|ENUM|CERT|PEAK_RSS|WROTE)' $O/honest11_writer.txt | cut -c1-500 >> $L
sha256sum $O/RUN11/cert_m11_r21_2_f8-7-6-5-4.txt >> $L
echo "MID $(date -u +%FT%TZ)" >> $L
( cd $O/RUN11 && bash $P/work/design/gate_required.sh cert_m11_r21_2_f8-7-6-5-4.txt ) > $O/honest11_gate.txt 2>&1; echo "gate11_rc=$?" >> $L
sha256sum $O/honest11_gate.txt >> $L
diff $O/honest11_gate.txt $P/work/design/out/fix1/honest_m11/cert_m11_r21_2_f8-7-6-5-4.txt.gate.txt >> $L 2>&1; echo "gate_receipt_diff_rc=$?" >> $L
echo "END $(date -u +%FT%TZ)" >> $L
