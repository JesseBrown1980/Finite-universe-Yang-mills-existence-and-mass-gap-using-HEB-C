#!/bin/bash
# second correction round, stage 2: rehearsal summary, final record, comparison, notes, lint result, pins, checks.
set -u
T=/mnt/c/tmp/opus55/floor-v2; W=/root/floor-v2; R=$W/repo
V=independent/y131-floor-cert-freeze-v2-20261110; P=$R/$V
REC=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
NAMES="K0 A1 A2 A3 B1 B2 C1 C2 C3 C4 C5 V1 V2 V3 V4 N9 N13 BA BAm BU BUp E0 E1 E2 E3 E4 E5 E6 E7 E8 E9 E10 E11 E12 E13 E14 E15 E16 E17 AB GC1 GC2 GC3 LK1 LK2 MG G1 G2 G3 G4 G5 G6 G7 G8 EV0 EV1 EV2 EV3 EV4 EV5 EV6 EV7 Y1 Y1b XK XT1 XT2 XT3 XT4 T1 T2 T2b T3 T4 T5 T7a T7b T7c T8 N1 N2 R1 R2 R3 PQ PQ0 F3 D1"
ST1=$(cut -d' ' -f1 $W/rehc/STAGE1.sha256)
[ "$(sha256sum $W/record_stage1c.hbp | cut -d' ' -f1)" = "$ST1" ] || { echo "stage1 record copy differs"; exit 1; }
for n in $NAMES; do case $n in X*) continue;; esac; f=$W/rehc/$n/FLOOR-RUN-RECEIPT.hbp; [ -f $f ] && ! grep -q "$ST1" $f && echo "!! receipt $n lacks the stage-1 record hash"; done
rm -rf $P/review-v3/rehearsal-v2c; mkdir -p $P/review-v3/rehearsal-v2c
cp $W/record_stage1c.hbp $P/review-v3/rehearsal-v2c/RECORD-AT-REHEARSAL.hbp
rm -f $P/review-v3/scripts/race.py $P/review-v3/rehearsal-v2c/race_v.py
python3 -I -B $T/reh_sum_c.py $NAMES > $W/rehc/summary_print.txt || { tail -3 $W/rehc/summary_print.txt; exit 1; }
grep -c . $W/rehc/SUMMARY.txt
for f in revise_record3.py compare3.py notes3.py lintres3.py c_install.sh c_final.sh c_pins.sh; do tr -d '\r' < $T/$f > $P/review-v3/generator/$f; done
STAGE=2 python3 -I -B $T/revise_record3.py | tail -1 | cut -c1-200 || exit 1
echo "rows that differ from the rehearsal state:"; diff $W/record_stage1c.hbp $P/$REC | grep '^>' | cut -c1-16
python3 -I -B $T/compare3.py | cut -c1-400 || exit 1
python3 -I -B $T/notes3.py | head -1 || exit 1
cd $R; git add -A -- $V ':!'$V/work/design/rs/target
rm -rf $W/exportb; mkdir -p $W/exportb; git checkout-index -a --prefix=$W/exportb/
( cd $W/exportb/$V && python3 -I -B final/tools/lint_hbp.py $REC . ) > $W/lint_export.txt 2>&1; echo "lint_export_rc=$?"
( cd $P && python3 -I -B final/tools/lint_hbp.py $REC . ) > $W/lint_tree.txt 2>&1; echo "lint_tree_rc=$?"
python3 -I -B $T/lintres3.py | grep 'LINT_RESULT\|LINT_CLASS\|other' | cut -c1-200
bash $T/c_pins.sh 2>&1 | cut -c1-300
echo "status other than A/M/??:"; git status --short | grep -v '^A  \|^M  \|^?? ' | head
echo "staged vs 3b91d1a0:"; git diff --cached --stat HEAD | tail -1
git diff --cached --name-status HEAD | cut -f1 | sort | uniq -c
echo "modified files:"; git diff --cached --name-status HEAD | grep -v '^A' | cut -c1-160
echo "work/ vs 3b91d1a0 (expect empty):"; git diff --cached HEAD --stat -- $V/work | tail -2
echo "review-v1 review-v2 vs 3b91d1a0 (expect empty):"; git diff --cached HEAD --stat -- $V/review-v1 $V/review-v2 | tail -2
sha256sum $P/work/design/rs/src/main.rs $P/work/design/rs/target/release/floorcert | cut -c1-64
grep -E '^PIN\|id=01[36]\|' $P/$REC | cut -c1-150
git show HEAD:$V/$REC | grep '^PREDICT|' | sha256sum | cut -c1-64; grep '^PREDICT|' $P/$REC | sha256sum | cut -c1-64; grep -c '^PREDICT|' $P/$REC
