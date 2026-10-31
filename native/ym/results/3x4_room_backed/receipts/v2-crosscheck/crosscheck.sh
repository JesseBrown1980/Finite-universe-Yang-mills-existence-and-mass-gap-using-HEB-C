#!/bin/bash
# Read-only cross-check: streaming comparator v2 (b028a03) on the LOCAL 3x3 60M and 72M outputs.
# Operator direction 2026-10-29. Not a merge of evidence lanes. Inputs are never modified.
# Runs only after: RUNALL.hbp has its final PILOT| row, no chain process, and the clean rebuild
# wrote REBUILD_VERDICT or REBUILD_ABORT (so it never contends with chain, pilot or rebuild).
set -u
X=/d/ym-3x4-room-run/v2-crosscheck; L=$X/CROSSCHECK.hbp; G=/d/ym-3x4-room-run/gate3x3-seg
RUNALL=$G/RUNALL.hbp; RB=/d/ym-3x4-room-run/rebuild-2e4846e/REBUILD.hbp
until grep -q '^PILOT|' "$RUNALL" && grep -qE '^REBUILD_(VERDICT|ABORT)\|' "$RB" 2>/dev/null \
      && ! tasklist.exe | grep -qiE 'shellschur|roomschur|ymroom|cargo|rustc'; do sleep 60; done
echo "XCHECK_START|t=$(date -Iseconds)|comparator=schur_record_compare_stream.py@b028a03|stream_sha256=$(sha256sum $X/code/schur_record_compare_stream.py | cut -c1-64)|v2_module_sha256=$(sha256sum $X/code/schur_record_compare.py | cut -c1-64)|python=$(python --version 2>&1 | tr ' ' '_')|json=0" >> $L
# CI forms each side's evidence as concatenated chunk outputs + merge output; the shell side here is
# the same shape: cols chunk 0:1000000000 output, then merge output. The room side is the local
# non-split roomschur output, used as is. Concatenation is the only input preparation.
for t in 60000000 72000000; do
  A1=$G/shellschur-cols-t$t.out; A2=$G/shellschur-merge-t$t.out; RM=$G/roomschur-seg-t$t.out; SH=$X/shell-t$t.hbp
  for f in $A1 $A2 $RM; do echo "XCHECK_INPUT|t=$t|file=$(basename $f)|bytes=$(stat -c%s $f)|sha256=$(sha256sum $f | cut -c1-64)|json=0" >> $L; done
  cat $A1 $A2 > $SH
  echo "XCHECK_PREP|t=$t|shell_file=$(basename $SH)|op=cat(cols,merge)|bytes=$(stat -c%s $SH)|sha256=$(sha256sum $SH | cut -c1-64)|json=0" >> $L
  for mode in v2 v1; do
    fl=""; [ $mode = v1 ] && fl="--v1"
    python -I $X/code/schur_record_compare_stream.py $fl $SH $RM > $X/stdout-$mode-t$t.txt 2> $X/stderr-$mode-t$t.txt; e=$?
    echo "XCHECK_RUN|t=$t|mode=$mode|exit=$e|stdout_sha256=$(sha256sum $X/stdout-$mode-t$t.txt | cut -c1-64)|stderr_bytes=$(stat -c%s $X/stderr-$mode-t$t.txt)|json=0" >> $L
    sed "s/^/XCHECK_STDOUT|t=$t|mode=$mode|/" $X/stdout-$mode-t$t.txt >> $L
  done
  for f in $A1 $A2 $RM; do echo "XCHECK_INPUT_AFTER|t=$t|file=$(basename $f)|sha256=$(sha256sum $f | cut -c1-64)|json=0" >> $L; done
done
echo "XCHECK_END|t=$(date -Iseconds)|local_comparator_verdicts_beside=t60_AGREE,t72_AGREE(compare.py_57b4c811_scope)|json=0" >> $L
cat $L
