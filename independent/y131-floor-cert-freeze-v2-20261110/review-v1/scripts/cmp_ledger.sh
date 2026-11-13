#!/bin/bash
cd /tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor/work
n=0; ok=0
while read h f; do
  n=$((n+1))
  L=$(grep -F "plants_m6_f4321/$f |" design/out/fix1/LEDGER.txt | head -1 | sed 's/.*| //')
  if [ -z "$L" ]; then echo "NOT_IN_LEDGER $f"; continue; fi
  if [ "$L" = "$h" ]; then ok=$((ok+1)); else echo "DIFF $f mine=$h ledger=$L"; fi
done < verify_opus55/plants_m6/hashes.txt
echo "n=$n ok=$ok"
grep -F 'plants_m6_f4321/cert_m6_r21_2_f' design/out/fix1/LEDGER.txt | head -3
grep -F 'P5b' design/out/fix1/LEDGER.txt | grep m6 | head -2
