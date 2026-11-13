set -u
P=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110
FB=/root/floor-v2-verify/build/rs/target/release/floorcert
PK="python3 -I -B $P/work/design/peak_rss.py"
O=/root/floor-v2-verify/reg2
rm -rf $O; mkdir -p $O
python3 -I /mnt/c/tmp/opus55/floor-v2-verify/scripts/rows.py $P/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp 025,028 value
echo "RUN11_before=$([ -e $O/RUN11 ] && echo 1 || echo 0)"
$PK $FB rowhash --m0 11 --threads 2 --dir $O/RUN11 > $O/rh11.txt 2>&1; echo "rowhash_rc=$?"
grep -E '^ROWHASH_ONLY|^PEAK_RSS' $O/rh11.txt
sha256sum $O/RUN11/core_keys_m11.bin
$PK $FB cert --m0 11 --r 21/2 --f '8,7,6,5,4' --write-cert --threads 2 --dir $O/RUN11 > $O/cert11.txt 2>&1; echo "cert_rc=$?"
grep -E '^KEYS|^PEAK_RSS|^CERT' $O/cert11.txt | cut -c1-300
sha256sum $O/RUN11/cert_m11_r21_2_f8-7-6-5-4.txt
