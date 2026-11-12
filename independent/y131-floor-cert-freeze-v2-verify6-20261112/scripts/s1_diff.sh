cd /root/floor-v6-verify/repoE
git diff --stat=200 HEAD^ HEAD | grep -v review-v6 | head -60
git log -3 --format='%H %s'
F=independent/y131-floor-cert-freeze-v2-20261110
ls $F $F/final $F/final/tools
grep -nE 'id=14[0-9]\|' $F/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp | cut -c1-600
