A=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110
python3 -I /mnt/c/tmp/opus55/floor-v2-verify/scripts/rows.py $A/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp 064,072 | cut -c1-1500
cd /root/floor-v2/repo; echo "--- refs containing 5e70e9dc"; git branch -a --contains 5e70e9dc02d6ed32fe9a94d03a2c3a77587ff9af 2>&1 | head -5
git for-each-ref --contains 5e70e9dc02d6ed32fe9a94d03a2c3a77587ff9af --format='%(refname)' | head
