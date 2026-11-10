A=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110
python3 -I /mnt/c/tmp/opus55/floor-v2-verify/scripts/rows.py $A/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp 116 | cut -c2400-6000
echo ====
grep -n -i 'ritz' $A/work/design/py/cert_gate.py | head -30
echo ====
grep -n -i -E 'ritz_upper|fn ritz|RITZ' $A/work/design/rs/src/main.rs | head -20
echo ====
cat $A/work/design/peak_rss.py
