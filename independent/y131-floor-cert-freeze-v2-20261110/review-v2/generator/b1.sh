#!/bin/bash
# correction round, stage 1: F8 note, verifier v2 material, generator, stage-1 record.
set -u
T=/mnt/c/tmp/opus55/floor-v2; W=/root/floor-v2; R=$W/repo
P=$R/independent/y131-floor-cert-freeze-v2-20261110
VS=/mnt/c/tmp/opus55/floor-v2-verify
REC=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
E=$P/review-v1/E3-PROVENANCE.hbp
if ! grep -q '^E3_NOTE|' $E; then
  python3 -I -B $T/e3note.py $E || exit 1
fi
grep -c '^E3_NOTE|' $E; tail -1 $E | cut -c1-60; grep -c $'\r' $E
mkdir -p $P/review-v2/verifier-out $P/review-v2/scripts $P/review-v2/generator
cp $VS/VERIFY-FLOOR-FREEZE-V2.hbp $VS/VERIFY-FLOOR-FREEZE-V2.hbp.sha256 $VS/VERIFY-FLOOR-FREEZE-V2.md $VS/VERIFY-FLOOR-FREEZE-V2.md.sha256 $P/review-v2/
for f in f13.out l5.out live.out r1.out reg2.out; do cp $VS/$f $P/review-v2/verifier-out/; done
tr -d '\r' < $VS/nofloat_win.out > $P/review-v2/verifier-out/nofloat_win.out
sha256sum $VS/nofloat_win.out | cut -c1-64
cp $VS/scripts/* $P/review-v2/scripts/
chmod 644 $P/review-v2/scripts/* $P/review-v2/verifier-out/* $P/review-v2/VERIFY*
( cd $P/review-v2 && sha256sum -c VERIFY-FLOOR-FREEZE-V2.hbp.sha256 VERIFY-FLOOR-FREEZE-V2.md.sha256 )
python3 -I -B $T/gen_b.py || exit 1
cp $T/revise_record2.py $T/gen_b.py $T/tail_b.py $P/review-v2/generator/ 2>/dev/null
STAGE=1 python3 $T/revise_record2.py | cut -c1-400 || exit 1
cd $P
mkdir -p $W/rehb
cp $REC $W/record_stage1b.hbp
sha256sum $REC | tee $W/rehb/STAGE1.sha256
grep -c . $REC; tail -1 $REC | cut -c1-300
grep -E '^PIN\|id=11[45]\|' $REC | cut -c1-140; sha256sum final/tools/run_floor.sh final/tools/floor_eval.py
python3 -I -B final/tools/lint_hbp.py $REC . > $W/lint_stage1b.txt 2>&1; echo lint_rc=$?; tail -2 $W/lint_stage1b.txt | cut -c1-300
cd $R && python3 -I -X utf8 native/scripts/no_float_gate.py . > $W/nofloat_b1.txt 2>&1; echo nofloat_rc=$?; tail -4 $W/nofloat_b1.txt | cut -c1-300
