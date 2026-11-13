#!/bin/bash
R=/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor
O=$R/work/verify_opus55/heavy
diff $O/honest11_gate.txt $R/work/design/out/fix1/honest_m11/cert_m11_r21_2_f8-7-6-5-4.txt.gate.txt
FB=$R/work/design/rs/target/release/floorcert
cd $R/work/design
for m in 11 12 13; do
  rm -rf $O/rhm$m; mkdir $O/rhm$m
  python3 -I -B $R/work/design/peak_rss.py $FB rowhash --m0 $m --threads 2 --dir $O/rhm$m > $O/rhm$m.txt 2>&1
  grep -E 'ROWHASH_ONLY|PEAK_RSS|GATE.*FAIL|ENUM' $O/rhm$m.txt | cut -c1-220; sha256sum $O/rhm$m/core_keys_m$m.bin
done
