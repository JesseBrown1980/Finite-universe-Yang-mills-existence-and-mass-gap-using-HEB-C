cd /root/floor-v6-verify/repoE
F=independent/y131-floor-cert-freeze-v2-20261110
git diff HEAD^ HEAD -- $F/final/tools/run_floor.sh $F/final/tools/recheck_floor.py
sed -n '1,40p' $F/final/tools/freeze_args_controls.sh | grep -nE 'usage|\$1|\$2|\$3|\$4|^#' | head -20
sha256sum $F/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
