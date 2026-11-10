#!/bin/bash
# v2 regression, part 1 (light): selftest, smoke r=12 m0=7, plants m0=6 r=21/2, E1 at m0=7. Excluded r only.
set -u
P=/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110
FB=$P/work/design/rs/target/release/floorcert
PK="python3 -I -B $P/work/design/peak_rss.py"
O=/root/floor-v2/reg
rm -rf $O/smoke $O/plants_m6 $O/e1_m7 $O/part1.log
mkdir -p $O/smoke $O/plants_m6
L=$O/part1.log
echo "START $(date -u +%FT%TZ) binary=$(sha256sum $FB | cut -d' ' -f1)" > $L
$FB selftest > $O/smoke/selftest.txt 2>&1; echo "selftest_rc=$? sha16=$(sha256sum $O/smoke/selftest.txt | cut -c1-16)" >> $L
# E1: absent --dir, m0 = 7 (r-independent)
[ -e $O/e1_m7 ] && echo "E1_m7 PRECONDITION FAIL" >> $L
$PK $FB rowhash --m0 7 --threads 2 --dir $O/e1_m7 > $O/e1_m7.txt 2>&1; echo "e1_m7_rowhash_rc=$? dir_exists=$([ -d $O/e1_m7 ] && echo 1 || echo 0) keys_sha16=$(sha256sum $O/e1_m7/core_keys_m7.bin | cut -c1-16)" >> $L
grep -E 'ROWHASH_ONLY|PEAK_RSS|ENUM|KEYS' $O/e1_m7.txt >> $L
# smoke: cert reuses an existing directory (made by mkdir above), enumerates and writes keys
$FB cert --m0 7 --r 12 --f '4,3,2,1' --write-cert --threads 2 --dir $O/smoke > $O/smoke/writer.txt 2>&1; echo "smoke_rc=$?" >> $L
for f in $O/smoke/cert_m7_r12_1_f4-3-2-1.txt $O/smoke/core_keys_m7.bin; do echo "smoke $(basename $f) sha16=$(sha256sum $f | cut -c1-16)" >> $L; done
grep -E '^(CERT|TAIL|WROTE)' $O/smoke/writer.txt | cut -c1-400 >> $L
bash $P/work/design/gate_required.sh $O/smoke/cert_m7_r12_1_f4-3-2-1.txt > $O/smoke/gate.txt 2>&1; echo "smoke_gate_rc=$? $(tail -1 $O/smoke/gate.txt | cut -c1-260)" >> $L
# cert in the directory rowhash made: KEYS loaded expected
$FB cert --m0 7 --r 12 --f '4,3,2,1' --write-cert --threads 2 --dir $O/e1_m7 > $O/e1_m7_cert.txt 2>&1; echo "e1_m7_cert_rc=$? $(grep -E '^KEYS' $O/e1_m7_cert.txt) cert_sha16=$(sha256sum $O/e1_m7/cert_m7_r12_1_f4-3-2-1.txt | cut -c1-16)" >> $L
# cert with an absent dir keeps the v1 behaviour (no directory is created)
$FB cert --m0 7 --r 12 --f '4,3,2,1' --write-cert --threads 2 --dir $O/absent_for_cert > $O/absent_cert.txt 2>&1; echo "cert_absent_dir_rc=$? dir_exists=$([ -d $O/absent_for_cert ] && echo 1 || echo 0)" >> $L
# plants
$FB cert --m0 6 --r 21/2 --f '4,3,2,1' --write-cert --plant all --ub 993765/10000 --threads 2 --dir $O/plants_m6 > $O/plants_m6/writer.txt 2>&1; echo "plants_rc=$?" >> $L
cd $O/plants_m6
n=0; ok=0
for f in cert_*.txt; do
  h=$(sha256sum $f | cut -c1-16); n=$((n+1))
  led=$(grep -F "plants_m6_f4321/$f |" $P/work/design/out/fix1/LEDGER.txt | head -1 | sed 's/.*| //')
  if [ "$h" = "$led" ]; then ok=$((ok+1)); m=MATCH; else m=DIFF; fi
  bash $P/work/design/gate_required.sh $O/plants_m6/$f > $O/plants_m6/$f.gate.txt 2>&1; rc=$?
  echo "plant $f v2=$h ledger=$led $m gate_rc=$rc $(grep '^VERDICT' $O/plants_m6/$f.gate.txt | cut -c1-90)" >> $L
done
echo "plants_files=$n ledger_match=$ok" >> $L
echo "END $(date -u +%FT%TZ)" >> $L
cat $L
