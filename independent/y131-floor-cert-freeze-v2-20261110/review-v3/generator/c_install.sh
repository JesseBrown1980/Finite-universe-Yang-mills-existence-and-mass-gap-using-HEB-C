#!/bin/bash
# second correction round, stage 1: launcher and evaluator installed, verifier final material copied, stage-1 record.
set -u
T=/mnt/c/tmp/opus55/floor-v2; W=/root/floor-v2; R=$W/repo
P=$R/independent/y131-floor-cert-freeze-v2-20261110
VS=/mnt/c/tmp/opus55/floor-v2-final
REC=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
cd $R
[ "$(git rev-parse HEAD)" = 3b91d1a047d7485693c754ece8c7c18f43fbf326 ] || { echo "HEAD is not 3b91d1a0"; exit 1; }
rm -rf $R/rehE14
tr -d '\r' < $T/run_floor_c.sh > $P/final/tools/run_floor.sh
tr -d '\r' < $T/floor_eval_c.py > $P/final/tools/floor_eval.py
bash -n $P/final/tools/run_floor.sh || exit 1
python3 -I -B -c "import ast,sys;ast.parse(open(sys.argv[1]).read())" $P/final/tools/floor_eval.py || exit 1
git ls-files -s -- independent/y131-floor-cert-freeze-v2-20261110/final/tools/run_floor.sh independent/y131-floor-cert-freeze-v2-20261110/final/tools/floor_eval.py | cut -c1-7; stat -c '%a %n' $P/final/tools/run_floor.sh $P/final/tools/floor_eval.py
rm -rf $P/review-v3; mkdir -p $P/review-v3/verifier-out $P/review-v3/scripts $P/review-v3/generator
for f in VERIFY-FLOOR-FREEZE-V2-FINAL.hbp VERIFY-FLOOR-FREEZE-V2-FINAL.hbp.sha256 VERIFY-FLOOR-FREEZE-V2-FINAL.md VERIFY-FLOOR-FREEZE-V2-FINAL.md.sha256; do cp $VS/$f $P/review-v3/; done
for f in attacks.out b1.out tools.diff; do cp $VS/$f $P/review-v3/verifier-out/; done
cp $VS/scripts/* $P/review-v3/scripts/
chmod 644 $P/review-v3/scripts/* $P/review-v3/verifier-out/* $P/review-v3/VERIFY*
( cd $P/review-v3 && sha256sum -c VERIFY-FLOOR-FREEZE-V2-FINAL.hbp.sha256 VERIFY-FLOOR-FREEZE-V2-FINAL.md.sha256 2>&1 | cut -c1-200 )
grep -rlI $'\r' $P/review-v3 | head -3
STAGE=1 python3 -I -B $T/revise_record3.py | cut -c1-400 || exit 1
cd $P
mkdir -p $W/rehc
cp $REC $W/record_stage1c.hbp
sha256sum $REC | tee $W/rehc/STAGE1.sha256
grep -c . $REC; tail -1 $REC | cut -c1-300
grep -E '^PIN\|id=11[45]\|' $REC | cut -c1-140; sha256sum final/tools/run_floor.sh final/tools/floor_eval.py
python3 -I -B final/tools/lint_hbp.py $REC . > $W/lint_stage1c.txt 2>&1; echo lint_rc=$?; tail -2 $W/lint_stage1c.txt | cut -c1-300
grep '^ERROR' $W/lint_stage1c.txt | grep -E 'id=1(1[45]|2[3-9]|30)|row 1(1[45]|2[3-9]|30)' | head -10 | cut -c1-300
cd $R && python3 -I -X utf8 native/scripts/no_float_gate.py . > $W/nofloat_c1.txt 2>&1; echo nofloat_rc=$?; tail -4 $W/nofloat_c1.txt | cut -c1-300
git status --short | grep -v '^ M \|^?? ' | head
