set -u
P=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110
V1=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-20261110
FB=/root/floor-v2-verify/build/rs/target/release/floorcert
PK="python3 -I -B $P/work/design/peak_rss.py"
LED=$V1/work/design/out/fix1/LEDGER.txt
O=/root/floor-v2-verify/reg
rm -rf $O; mkdir -p $O/smoke $O/plants
pgrep -a -x floorcert; pgrep -af cert_gate.py | grep -v pgrep
echo "binary=$(sha256sum $FB | cut -c1-16)"
$FB selftest > $O/smoke/selftest.txt 2>&1; echo "selftest_rc=$? $(sha256sum $O/smoke/selftest.txt | cut -c1-16) ledger=$(grep -F 'smoke/selftest.txt |' $LED | sed 's/.*| //')"
[ -e $O/e1 ] && echo PRE_FAIL
$PK $FB rowhash --m0 7 --threads 2 --dir $O/e1 > $O/e1.txt 2>&1; echo "rowhash_absent_rc=$? dir=$([ -d $O/e1 ] && echo created) keys=$(sha256sum $O/e1/core_keys_m7.bin | cut -c1-16) ledger=$(grep -F 'smoke/core_keys_m7.bin |' $LED | sed 's/.*| //')"
$FB cert --m0 7 --r 12 --f '4,3,2,1' --write-cert --threads 2 --dir $O/smoke > $O/smoke/writer.txt 2>&1; echo "smoke_rc=$?"
echo "writer $(sha256sum $O/smoke/writer.txt | cut -c1-16) ledger=$(grep -F 'smoke/writer.txt |' $LED | sed 's/.*| //')"
echo "cert $(sha256sum $O/smoke/cert_m7_r12_1_f4-3-2-1.txt | cut -c1-16) ledger=$(grep -F 'smoke/cert_m7_r12_1_f4-3-2-1.txt |' $LED | sed 's/.*| //')"
echo "keys $(sha256sum $O/smoke/core_keys_m7.bin | cut -c1-16)"
bash $P/work/design/gate_required.sh $O/smoke/cert_m7_r12_1_f4-3-2-1.txt > $O/smoke/gate.txt 2>&1; echo "gate_rc=$? $(tail -1 $O/smoke/gate.txt | cut -c1-60)"
$FB cert --m0 7 --r 12 --f '4,3,2,1' --write-cert --threads 2 --dir $O/e1 > $O/e1_cert.txt 2>&1; echo "cert_reuse_rc=$? $(grep -E '^KEYS' $O/e1_cert.txt) $(grep -c '^ENUM' $O/e1_cert.txt) cert=$(sha256sum $O/e1/cert_m7_r12_1_f4-3-2-1.txt | cut -c1-16)"
$FB cert --m0 7 --r 12 --f '4,3,2,1' --write-cert --threads 2 --dir $O/absent > $O/absent.txt 2>&1; echo "cert_absent_rc=$? dir=$([ -d $O/absent ] && echo 1 || echo 0)"
$FB cert --m0 6 --r 21/2 --f '4,3,2,1' --write-cert --plant all --ub 993765/10000 --threads 2 --dir $O/plants > $O/plants/writer.txt 2>&1; echo "plants_rc=$?"
echo "plant_writer $(sha256sum $O/plants/writer.txt | cut -c1-16) ledger=$(grep -F 'plants_m6_f4321/writer.txt |' $LED | sed 's/.*| //')"
n=0; ok=0
for f in $(cd $O/plants && ls cert_*.txt); do
  n=$((n+1)); h=$(sha256sum $O/plants/$f | cut -c1-16); l=$(grep -F "plants_m6_f4321/$f |" $LED | head -1 | sed 's/.*| //')
  [ "$h" = "$l" ] && ok=$((ok+1)) || echo "DIFF $f $h $l"
  bash $P/work/design/gate_required.sh $O/plants/$f > $O/plants/$f.gate 2>&1; echo "  $f gate_rc=$? $(grep -oE '^GATE_REQUIRED\|[A-Z]+' $O/plants/$f.gate)"
done
echo "plants=$n match=$ok"
