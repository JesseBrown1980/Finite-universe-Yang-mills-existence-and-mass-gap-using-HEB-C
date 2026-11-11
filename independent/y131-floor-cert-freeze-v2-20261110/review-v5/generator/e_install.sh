#!/bin/bash
# fourth correction round, stage 1: launcher, evaluator and checker installed, the verifier's report copied, stage-1 record.
set -u
T=/root/floor-v5/gen; W=/root/floor-v5; R=/root/floor-v2/repo
P=$R/independent/y131-floor-cert-freeze-v2-20261110
VS=/root/floor-v4-verify/repoB/independent/y131-floor-cert-freeze-v2-verify4-20261111
REC=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
C4=5eecb540431a1b5665605f68ed81bc701719dcd1
cd $R
[ "$(git rev-parse HEAD)" = $C4 ] || { echo "HEAD is not 5eecb540"; exit 1; }
[ "$(git -C /root/floor-v4-verify/repoB rev-parse HEAD)" = e925e0bafac0ef0ad6bbf10212ed6faef04b6103 ] || { echo "verifier clone is not at e925e0ba"; exit 1; }
mkdir -p $W/base
git show $C4:independent/y131-floor-cert-freeze-v2-20261110/final/tools/run_floor.sh > $W/base/run_floor.sh
git show $C4:independent/y131-floor-cert-freeze-v2-20261110/final/tools/floor_eval.py > $W/base/floor_eval.py
python3 -I -B $T/patch_e.py $W $W/base || exit 1
cp $W/run_floor_e.sh $P/final/tools/run_floor.sh
cp $W/floor_eval_e.py $P/final/tools/floor_eval.py
cp $T/recheck_floor.py $P/final/tools/recheck_floor.py
bash -n $P/final/tools/run_floor.sh || exit 1
for f in floor_eval.py recheck_floor.py; do python3 -I -B -c "import ast,sys;ast.parse(open(sys.argv[1]).read())" $P/final/tools/$f || exit 1; done
chmod 644 $P/final/tools/run_floor.sh $P/final/tools/floor_eval.py $P/final/tools/recheck_floor.py
rm -rf $P/review-v5; mkdir -p $P/review-v5/generator $P/review-v5/verifier/scripts
cp $VS/VERIFY-FLOOR-FREEZE-V2-FINAL4.* $P/review-v5/verifier/
cp $VS/scripts/* $P/review-v5/verifier/scripts/
chmod 644 $P/review-v5/verifier/* $P/review-v5/verifier/scripts/* 2>/dev/null; chmod 755 $P/review-v5/verifier/scripts
( cd $P/review-v5/verifier && sha256sum -c VERIFY-FLOOR-FREEZE-V2-FINAL4.hbp.sha256 VERIFY-FLOOR-FREEZE-V2-FINAL4.md.sha256 2>&1 | cut -c1-120 )
grep -rlI $'\r' $P/review-v5 | head -3
STAGE=1 python3 -I -B $T/revise_record5.py | cut -c1-400 || exit 1
cd $P
mkdir -p $W/rehe
cp $REC $W/record_stage1e.hbp
sha256sum $REC | tee $W/rehe/STAGE1.sha256
grep -c . $REC; tail -1 $REC | cut -c1-200
grep -E '^PIN\|id=(11[45]|131)\|' $REC | cut -c1-140; sha256sum final/tools/run_floor.sh final/tools/floor_eval.py final/tools/recheck_floor.py
python3 -I -B final/tools/lint_hbp.py $REC . > $W/lint_stage1e.txt 2>&1; echo lint_rc=$?; tail -1 $W/lint_stage1e.txt | cut -c1-300
grep '^ERROR' $W/lint_stage1e.txt | awk -F: '{print $1}' | sort | uniq -c | tail -14
cd $R && python3 -I -X utf8 native/scripts/no_float_gate.py . > $W/nofloat_e1.txt 2>&1; echo nofloat_rc=$?; tail -3 $W/nofloat_e1.txt | cut -c1-300
git status --short | grep -v '^?? .*target/' | head -12
