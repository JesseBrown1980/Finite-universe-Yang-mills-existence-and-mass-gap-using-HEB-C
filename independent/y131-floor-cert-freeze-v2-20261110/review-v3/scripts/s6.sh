D=/root/floor-v2-final/head/independent/y131-floor-cert-freeze-v2-20261110
for n in DX D3 D1 X0 X1 Y1 P1; do echo "== $n"; grep -E '^INVOKE' $D/review-v2/rehearsal-v2b/$n.FLOOR-RUN-RECEIPT.hbp | sed -E 's/\|log_sha256=[0-9a-f]*//; s/\|argv=(.{0,150}).*/|argv=\1/' ; grep -E '^FLOOR_RUN' $D/review-v2/rehearsal-v2b/$n.stdout.txt | cut -c1-200; done
cat $D/review-v2/rehearsal-v2b/P1.attack.txt $D/review-v2/rehearsal-v2b/Y1.attack.txt
grep -E 'STEP\|m0=12' $D/review-v2/rehearsal-v2b/DX.stdout.txt | grep -o 'rowhash_pin=[^|]*|bad=[^|]*'
grep -E 'STEP\|m0=13' $D/review-v2/rehearsal-v2b/D3.stdout.txt | grep -o 'rowhash_pin=[^|]*|bad=[^|]*'
grep -rniE 'toctou|race|same user|same_user|residual' $D/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp $D/final/NOTE-S3-3X4-R9-FLOOR-CERT-20261109.md $D/final/CHANGES.txt | cut -c1-300 | head
