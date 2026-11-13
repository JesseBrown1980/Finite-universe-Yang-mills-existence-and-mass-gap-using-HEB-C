#!/bin/bash
# correction round, stage 2: rehearsal summary, final record, comparisons, notes, lint result, pins, checks.
set -u
T=/mnt/c/tmp/opus55/floor-v2; W=/root/floor-v2; R=$W/repo
V1=$R/independent/y131-floor-cert-freeze-20261110
V=independent/y131-floor-cert-freeze-v2-20261110; P=$R/$V
REC=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
NAMES="A1 A2 A3 B1 B2 C1 C2 C3 C4 C5 V1 V2 V3 N9 N13 BA BAm BU BUp E0 E1 E2 E3 E4 E5 E6 E7 E8 E9 E10 E11 LK1 LK2 MG G1 G2 G3 G4 G5 G6 G7 G8 EV0 EV1 EV2 EV3 EV4 EV5 X0 X1 X1b Y1 Y1b P1 R1 R2 R3 D1 DX D3"
ST1=$(cut -d' ' -f1 $W/rehb/STAGE1.sha256)
[ "$(sha256sum $W/record_stage1b.hbp | cut -d' ' -f1)" = "$ST1" ] || { echo "stage1 record copy differs"; exit 1; }
# every receipt names the stage-1 record
for n in $NAMES; do case $n in X*) continue;; esac; f=$W/rehb/$n/FLOOR-RUN-RECEIPT.hbp; [ -f $f ] && ! grep -q "$ST1" $f && echo "!! receipt $n lacks the stage-1 record hash"; done
rm -rf $P/review-v2/rehearsal-v2b; mkdir -p $P/review-v2/rehearsal-v2b
cp $W/record_stage1b.hbp $P/review-v2/rehearsal-v2b/RECORD-AT-REHEARSAL.hbp
python3 -I -B $T/reh_sum_b.py $NAMES > $W/rehb/summary_print.txt || { tail -3 $W/rehb/summary_print.txt; exit 1; }
grep -c . $W/rehb/SUMMARY.txt
cp $V1/final/CHANGES.txt $P/final/CHANGES.txt; cp $V1/final/NOTE-S3-3X4-R9-FLOOR-CERT-20261109.md $P/final/
python3 -I -B $T/gen_b.py || exit 1
python3 -I -B $T/gen_notes.py || exit 1
cp $T/revise_record2.py $T/gen_b.py $T/tail_b.py $T/e3note.py $T/compare2.py $T/gen_notes.py $T/notes2.py $T/lintres2.py $T/pins2.sh $T/b1.sh $T/final_b.sh $T/patch_eval.py $T/upd_tail.py $T/upd_reh.py $T/upd_sum.py $T/upd_notes.py $P/review-v2/generator/
for f in $P/review-v2/generator/*; do tr -d '\r' < $f > $f.lf && mv $f.lf $f; done
STAGE=2 python3 $T/revise_record2.py | tail -1 | cut -c1-200 || exit 1
echo "rows that differ from the rehearsal state:"; diff $W/record_stage1b.hbp $P/$REC | grep '^>' | cut -c1-16
python3 -I -B $T/compare.py | head -1 | cut -c1-400 || exit 1
python3 -I -B $T/compare2.py | cut -c1-400 || exit 1
python3 -I -B $T/notes2.py | head -1 || exit 1
cd $R; git add -A -- $V ':!'$V/work/design/rs/target
rm -rf $W/exportb; mkdir -p $W/exportb; git checkout-index -a --prefix=$W/exportb/
( cd $W/exportb/$V && python3 -I -B final/tools/lint_hbp.py $REC . ) > $W/lint_export.txt 2>&1; echo "lint_export_rc=$?"
( cd $P && python3 -I -B final/tools/lint_hbp.py $REC . ) > $W/lint_tree.txt 2>&1; echo "lint_tree_rc=$?"
python3 -I -B $T/lintres2.py | grep 'LINT_RESULT\|LINT_CLASS\|other' | cut -c1-200
bash $T/pins2.sh 2>&1 | cut -c1-300
echo "status other than A/M/??:"; git status --short | grep -v '^A  \|^M  \|^?? ' | head
echo "staged vs cfc57bef:"; git diff --cached --stat HEAD | tail -1
git diff --cached --name-status HEAD | cut -f1 | sort | uniq -c
echo "fixed files vs cfc57bef (expect 0 lines):"; git diff --cached HEAD --stat -- $V/work | tail -2
sha256sum $P/work/design/rs/src/main.rs $P/work/design/rs/target/release/floorcert | cut -c1-64
grep -E '^PIN\|id=01[36]\|' $P/$REC | cut -c1-150
