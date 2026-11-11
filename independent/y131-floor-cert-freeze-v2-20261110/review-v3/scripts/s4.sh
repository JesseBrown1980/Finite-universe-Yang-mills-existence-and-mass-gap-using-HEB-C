D=/root/floor-v2-final/head/independent/y131-floor-cert-freeze-v2-20261110
cat $D/work/design/gate_required.sh; echo =====; cat $D/work/design/peak_rss.py; echo ====
grep -nE '^[A-Z_]+\|id=(00[0-9]|01[0-2]|119|12[0-2])\|' $D/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
