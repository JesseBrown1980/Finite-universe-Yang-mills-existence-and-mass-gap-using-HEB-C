#!/bin/bash
# third correction round, stage 1: launcher, evaluator and checker installed, the reviewer's text copied, stage-1 record.
set -u
T=/root/floor-v3/gen; W=/root/floor-v3; R=/root/floor-v2/repo
P=$R/independent/y131-floor-cert-freeze-v2-20261110
REC=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
C3=78c89c312a265fe4090071fc1abdc7d6eb102e7e
cd $R
[ "$(git rev-parse HEAD)" = $C3 ] || { echo "HEAD is not 78c89c31"; exit 1; }
mkdir -p $W/base
git show $C3:independent/y131-floor-cert-freeze-v2-20261110/final/tools/run_floor.sh > $W/base/run_floor.sh
git show $C3:independent/y131-floor-cert-freeze-v2-20261110/final/tools/floor_eval.py > $W/base/floor_eval.py
python3 -I -B $T/patch_d.py $W $W/base || exit 1
cp $W/run_floor_d.sh $P/final/tools/run_floor.sh
cp $W/floor_eval_d.py $P/final/tools/floor_eval.py
tr -d '\r' < $T/recheck_floor.py > $P/final/tools/recheck_floor.py
tr -d '\r' < $T/freeze_args_controls.sh > $P/final/tools/freeze_args_controls.sh
bash -n $P/final/tools/freeze_args_controls.sh || exit 1
bash -n $P/final/tools/run_floor.sh || exit 1
for f in floor_eval.py recheck_floor.py; do python3 -I -B -c "import ast,sys;ast.parse(open(sys.argv[1]).read())" $P/final/tools/$f || exit 1; done
chmod 644 $P/final/tools/run_floor.sh $P/final/tools/floor_eval.py $P/final/tools/recheck_floor.py $P/final/tools/freeze_args_controls.sh
rm -rf $P/review-v4; mkdir -p $P/review-v4/generator
tr -d '\r' < $T/REVIEW-ACCEPTANCE-20261111.md > $P/review-v4/REVIEW-ACCEPTANCE-20261111.md
STAGE=1 python3 -I -B $T/revise_record4.py | cut -c1-400 || exit 1
cd $P
mkdir -p $W/rehd
cp $REC $W/record_stage1d.hbp
sha256sum $REC | tee $W/rehd/STAGE1.sha256
grep -c . $REC; tail -1 $REC | cut -c1-300
grep -E '^PIN\|id=(11[45]|131)\|' $REC | cut -c1-140; sha256sum final/tools/run_floor.sh final/tools/floor_eval.py final/tools/recheck_floor.py
python3 -I -B final/tools/lint_hbp.py $REC . > $W/lint_stage1d.txt 2>&1; echo lint_rc=$?; tail -1 $W/lint_stage1d.txt | cut -c1-300
grep '^ERROR' $W/lint_stage1d.txt | awk -F: '{print $1}' | sort | uniq -c | awk '$2 ~ /line/ {print}' | tail -12
cd $R && python3 -I -X utf8 native/scripts/no_float_gate.py . > $W/nofloat_d1.txt 2>&1; echo nofloat_rc=$?; tail -4 $W/nofloat_d1.txt | cut -c1-300
git status --short | grep -v '^?? .*target/' | head -20
