#!/bin/bash
# third correction round, stage 2: rehearsal summary, final record, comparison, notes, lint result, pins, checks.
set -u
T=/root/floor-v3/gen; W=/root/floor-v3; R=/root/floor-v2/repo
V=independent/y131-floor-cert-freeze-v2-20261110; P=$R/$V
REC=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
C3=78c89c312a265fe4090071fc1abdc7d6eb102e7e
ST1=$(cut -d' ' -f1 $W/rehd/STAGE1.sha256)
[ "$(sha256sum $W/record_stage1d.hbp | cut -d' ' -f1)" = "$ST1" ] || { echo "stage1 record copy differs"; exit 1; }
[ "$(git -C $R rev-parse HEAD)" = $C3 ] || { echo "HEAD is not 78c89c31"; exit 1; }
rm -rf $P/review-v4/rehearsal-v2d; mkdir -p $P/review-v4/rehearsal-v2d
cp $W/record_stage1d.hbp $P/review-v4/rehearsal-v2d/RECORD-AT-REHEARSAL.hbp
python3 -I -B $T/d_sum.py > $W/rehd/summary_print.txt; echo "summary_rc=$?"; tail -1 $W/rehd/summary_print.txt | cut -c1-400
for f in patch_d.py revise_record4.py compare4.py notes4.py lintres4.py d_install.sh d_reh.sh d_sum.py d_pins.sh d_final.sh; do cp $T/$f $P/review-v4/generator/$f; done
grep -rlI $'\r' $P/review-v4 | head -3
STAGE=2 python3 -I -B $T/revise_record4.py | tail -1 | cut -c1-200 || exit 1
echo "rows that differ from the rehearsal state:"; diff $W/record_stage1d.hbp $P/$REC | grep '^>' | cut -c1-16
python3 -I -B $T/compare4.py | cut -c1-400 || exit 1
python3 -I -B $T/notes4.py | head -1 || exit 1
cd $R; git add -A -- $V ':!'$V/work/design/rs/target
rm -rf $W/exportb; mkdir -p $W/exportb; git checkout-index -a --prefix=$W/exportb/
( cd $W/exportb/$V && python3 -I -B final/tools/lint_hbp.py $REC . ) > $W/lint_export.txt 2>&1; echo "lint_export_rc=$?"
( cd $P && python3 -I -B final/tools/lint_hbp.py $REC . ) > $W/lint_tree.txt 2>&1; echo "lint_tree_rc=$?"
python3 -I -B $T/lintres4.py | grep 'LINT_RESULT\|LINT_CLASS\|other' | cut -c1-200
bash $T/d_pins.sh 2>&1 | cut -c1-300
echo "status other than A/M/??:"; git status --short | grep -v '^A  \|^M  \|^?? ' | head
echo "staged vs 78c89c31:"; git diff --cached --stat HEAD | tail -1
git diff --cached --name-status HEAD | cut -f1 | sort | uniq -c
echo "modified files:"; git diff --cached --name-status HEAD | grep -v '^A' | cut -c1-160
echo "work/ review-v1 review-v2 review-v3 vs 78c89c31 (expect empty):"; git diff --cached HEAD --stat -- $V/work $V/review-v1 $V/review-v2 $V/review-v3 | tail -2
sha256sum $P/work/design/rs/src/main.rs $P/work/design/rs/target/release/floorcert | cut -c1-64
grep -E '^PIN\|id=01[36]\|' $P/$REC | cut -c1-150
git show HEAD:$V/$REC | grep '^PREDICT|' | sha256sum | cut -c1-64; grep '^PREDICT|' $P/$REC | sha256sum | cut -c1-64; grep -c '^PREDICT|' $P/$REC
