#!/bin/bash
set -u
R=/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor
FB=$R/work/design/rs/target/release/floorcert
O=$R/work/verify_opus55
mkdir -p $O/smoke $O/plants_m6 $O/refuse
cd $R/work/design
$FB selftest > $O/smoke/selftest.txt 2>&1; echo selftest_rc=$?
sha256sum $O/smoke/selftest.txt
/usr/bin/time -v $FB cert --m0 7 --r 12 --f '4,3,2,1' --write-cert --threads 2 --dir $O/smoke > $O/smoke/writer.txt 2>$O/smoke/writer.time; echo smoke_rc=$?
sha256sum $O/smoke/cert_* $O/smoke/core_keys_m7.bin 2>/dev/null
bash $R/work/design/gate_required.sh $O/smoke/cert_m7_r12_1_f4-3-2-1.txt > $O/smoke/gate.txt 2>&1; echo gate_rc=$?
tail -2 $O/smoke/gate.txt | cut -c1-200
grep -E '^(CERT|TAIL)' $O/smoke/writer.txt | cut -c1-300
# refusal tests for r near 9 (no computation expected)
for r in 9 10 19/2 90000001/10000000 8 18/2 '21/2,9'; do $FB cert --m0 4 --r "$r" --dir $O/refuse > $O/refuse/out.txt 2>&1; echo "r=$r rc=$? $(head -c 160 $O/refuse/out.txt)"; done
ls $O/refuse
