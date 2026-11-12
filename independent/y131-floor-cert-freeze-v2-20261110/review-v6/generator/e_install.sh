#!/bin/bash
# fifth correction round, stage 1: launcher and checker installed, the verifier's report copied, stage-1 record.
set -u
T=/root/floor-v6/gen; W=/root/floor-v6; R=/root/floor-v2/repo
P=$R/independent/y131-floor-cert-freeze-v2-20261110
VR=/mnt/c/tmp/opus55/floor-v2-verify5/pushrepo
VS=$VR/independent/y131-floor-cert-freeze-v2-verify5-20261111
REC=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
C4=3c41ea2d9dd01de0ffcd547a7e7d417baa2ca6c0
cd $R
[ "$(git rev-parse HEAD)" = $C4 ] || { echo "HEAD is not 3c41ea2d"; exit 1; }
[ "$(git -c safe.directory='*' -C $VR rev-parse HEAD)" = c27abc8268eb7b03128c8cde91c0e7f2cfead42b ] || { echo "verifier clone is not at c27abc82"; exit 1; }
[ -z "$(git -c safe.directory='*' -C $VR status --porcelain -- independent/y131-floor-cert-freeze-v2-verify5-20261111 | grep -v '^??')" ] || echo "NOTE verifier folder has tracked changes"
mkdir -p $W/base
git show $C4:independent/y131-floor-cert-freeze-v2-20261110/final/tools/run_floor.sh > $W/base/run_floor.sh
git show $C4:independent/y131-floor-cert-freeze-v2-20261110/final/tools/recheck_floor.py > $W/base/recheck_floor.py
python3 -I -B $T/patch_f.py $W $W/base || exit 1
cp $W/run_floor_f.sh $P/final/tools/run_floor.sh
cp $W/recheck_floor_f.py $P/final/tools/recheck_floor.py
bash -n $P/final/tools/run_floor.sh || exit 1
python3 -I -B -c "import ast,sys;ast.parse(open(sys.argv[1]).read())" $P/final/tools/recheck_floor.py || exit 1
chmod 644 $P/final/tools/run_floor.sh $P/final/tools/recheck_floor.py
rm -rf $P/review-v6; mkdir -p $P/review-v6/generator $P/review-v6/verifier/scripts $P/review-v6/verifier/raw
for f in $(git -c safe.directory='*' -C $VR ls-files -- independent/y131-floor-cert-freeze-v2-verify5-20261111); do
  d=$P/review-v6/verifier/${f#independent/y131-floor-cert-freeze-v2-verify5-20261111/}
  mkdir -p "$(dirname "$d")"; git -c safe.directory='*' -C $VR show HEAD:$f > "$d"
done
find $P/review-v6/verifier -type f | wc -l; du -sh $P/review-v6/verifier | cut -f1
find $P/review-v6 -type f -exec chmod 644 {} +
( cd $P/review-v6/verifier && sha256sum -c VERIFY-FLOOR-FREEZE-V2-FINAL5.hbp.sha256 VERIFY-FLOOR-FREEZE-V2-FINAL5.md.sha256 2>&1 | cut -c1-120 )
grep -rlI $'\r' $P/review-v6 | head -3
STAGE=1 python3 -I -B $T/revise_record6.py | cut -c1-400 || exit 1
cd $P
mkdir -p $W/rehf
cp $REC $W/record_stage1f.hbp
sha256sum $REC | tee $W/rehf/STAGE1.sha256
grep -c . $REC; tail -1 $REC | cut -c1-200
grep -E '^PIN\|id=(11[45]|131)\|' $REC | cut -c1-140; sha256sum final/tools/run_floor.sh final/tools/floor_eval.py final/tools/recheck_floor.py
python3 -I -B final/tools/lint_hbp.py $REC . > $W/lint_stage1f.txt 2>&1; echo lint_rc=$?; tail -1 $W/lint_stage1f.txt | cut -c1-300
grep '^ERROR' $W/lint_stage1f.txt | awk -F: '{print $1}' | sort | uniq -c | tail -14
cd $R && python3 -I -X utf8 native/scripts/no_float_gate.py . > $W/nofloat_f1.txt 2>&1; echo nofloat_rc=$?; tail -3 $W/nofloat_f1.txt | cut -c1-300
git status --short | grep -v '^?? .*target/' | head -12
diff <(git show $C4:independent/y131-floor-cert-freeze-v2-20261110/final/tools/run_floor.sh) $P/final/tools/run_floor.sh | grep -c '^[<>]'
diff <(git show $C4:independent/y131-floor-cert-freeze-v2-20261110/final/tools/recheck_floor.py) $P/final/tools/recheck_floor.py | grep -c '^[<>]'
