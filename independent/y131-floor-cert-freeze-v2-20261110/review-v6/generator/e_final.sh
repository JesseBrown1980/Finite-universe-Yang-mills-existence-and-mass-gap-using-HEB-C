#!/bin/bash
# fifth correction round, stage 2: rehearsal summary, final record, comparison, notes, lint result, pins, checks.
set -u
T=/root/floor-v6/gen; W=/root/floor-v6; R=/root/floor-v2/repo
V=independent/y131-floor-cert-freeze-v2-20261110; P=$R/$V
REC=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
C4=3c41ea2d9dd01de0ffcd547a7e7d417baa2ca6c0
ST1=$(cut -d' ' -f1 $W/rehf/STAGE1.sha256)
[ "$(sha256sum $W/record_stage1f.hbp | cut -d' ' -f1)" = "$ST1" ] || { echo "stage1 record copy differs"; exit 1; }
[ "$(git -C $R rev-parse HEAD)" = $C4 ] || { echo "HEAD is not 3c41ea2d"; exit 1; }
rm -rf $P/review-v6/rehearsal-v2f; mkdir -p $P/review-v6/rehearsal-v2f
cp $W/record_stage1f.hbp $P/review-v6/rehearsal-v2f/RECORD-AT-REHEARSAL.hbp
python3 -I -B $T/e_sum.py > $W/rehf/summary_print.txt; echo "summary_rc=$?"; tail -1 $W/rehf/summary_print.txt | cut -c1-400
for f in patch_f.py revise_record6.py compare6.py notes6.py lintres6.py e_install.sh e_reh.sh e_sum.py e_pins.sh e_final.sh e_commit.sh; do cp $T/$f $P/review-v6/generator/$f; done
grep -rlI $'\r' $P/review-v6 | head -3
STAGE=2 python3 -I -B $T/revise_record6.py | tail -1 | cut -c1-200 || exit 1
echo "rows that differ from the rehearsal state:"; diff $W/record_stage1f.hbp $P/$REC | grep '^>' | cut -c1-16
python3 -I -B $T/compare6.py | cut -c1-400 || exit 1
python3 -I -B $T/notes6.py | head -1 || exit 1
cd $R; git add -A -- $V ':!'$V/work/design/rs/target
rm -rf $W/exportb; mkdir -p $W/exportb; git checkout-index -a --prefix=$W/exportb/
( cd $W/exportb/$V && python3 -I -B final/tools/lint_hbp.py $REC . ) > $W/lint_export.txt 2>&1; echo "lint_export_rc=$?"
( cd $P && python3 -I -B final/tools/lint_hbp.py $REC . ) > $W/lint_tree.txt 2>&1; echo "lint_tree_rc=$?"
python3 -I -B $T/lintres6.py | grep 'LINT_RESULT\|LINT_CLASS\|other' | cut -c1-200
bash $T/e_pins.sh 2>&1 | cut -c1-300
echo "status other than A/M/??:"; git status --short | grep -v '^A  \|^M  \|^?? ' | head
echo "staged vs 3c41ea2d:"; git diff --cached --stat HEAD | tail -1
git diff --cached --name-status HEAD | cut -f1 | sort | uniq -c
echo "modified files:"; git diff --cached --name-status HEAD | grep -v '^A' | cut -c1-160
echo "work/ review-v1..v5 vs 3c41ea2d (expect empty):"; git diff --cached HEAD --stat -- $V/work $V/review-v1 $V/review-v2 $V/review-v3 $V/review-v4 $V/review-v5 | tail -2
sha256sum $P/work/design/rs/src/main.rs $P/work/design/rs/target/release/floorcert | cut -c1-64
git show HEAD:$V/$REC | grep '^PREDICT|' | sha256sum | cut -c1-64; grep '^PREDICT|' $P/$REC | sha256sum | cut -c1-64; grep -c '^PREDICT|' $P/$REC
