cd /root/floor-v2/repo
git log -1 --format=%B cfc57befadcb61fb36b992af841941adaecd3fd0 | grep -inE 'co-authored|signed-off|claude-session|generated' ; echo "trailer_grep_rc=$?"
git log -1 --format=%B cfc57befadcb61fb36b992af841941adaecd3fd0 | git interpret-trailers --parse; echo "parsed_done"
A=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110
wc -l $A/final/tools/run_floor.sh $A/final/tools/floor_eval.py $A/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp $A/work/design/rs/src/main.rs $A/work/design/gate_required.sh
mkdir -p /mnt/c/tmp/opus55/floor-v2-verify/view
cp $A/final/tools/run_floor.sh $A/final/tools/floor_eval.py $A/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp $A/work/design/gate_required.sh /mnt/c/tmp/opus55/floor-v2-verify/view/
cd /root/floor-v2-verify/arch/independent
diff y131-floor-cert-freeze-20261110/work/design/rs/src/main.rs y131-floor-cert-freeze-v2-20261110/work/design/rs/src/main.rs > /mnt/c/tmp/opus55/floor-v2-verify/view/main.diff; wc -l /mnt/c/tmp/opus55/floor-v2-verify/view/main.diff
cp y131-floor-cert-freeze-20261110/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp /mnt/c/tmp/opus55/floor-v2-verify/view/PREDICT-v1.hbp
ls y131-floor-cert-freeze-20261110/ y131-floor-cert-freeze-20261110/work/design y131-floor-cert-freeze-v2-20261110/work/design
