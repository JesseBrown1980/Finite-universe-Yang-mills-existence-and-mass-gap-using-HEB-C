#!/bin/bash
# Operator direction 2026-10-29 "run it all": 3x3 shellschur full records (COLS+MERGE, correct args),
# record comparison vs segmented roomschur at 60/72/90e6; only if all three AGREE, 3x4 pilot on D: 300G.
O=/d/ym-3x4-room-run/gate3x3-seg; P=/d/ym-3x4-room-run/pilot3x4; B=/c/Users/acer/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/native/ym/target/release
MAT=C:/Users/acer/AppData/Local/Temp/claude/C--Users-acer/6853eb37-154a-4f43-bb7d-93cda2fc8b63/scratchpad/gate/ymsec-3x3.txt
L=$O/RUNALL.hbp
while tasklist.exe | grep -qi shellschur; do sleep 30; done
cat "C:/Users/acer/AppData/Local/Temp/claude/C--Users-acer/6853eb37-154a-4f43-bb7d-93cda2fc8b63/tasks/biwrcepk0.output" | grep ^CTL >> $L
echo "RUNALL|start=$(date -Iseconds)|shellschur_sha256=$(sha256sum $B/shellschur.exe | cut -c1-64)|roomschur_sha256=$(sha256sum $B/roomschur.exe | cut -c1-64)|compare_sha256=$(sha256sum $O/compare.py | cut -c1-64)|matrix_sha256=$(sha256sum $MAT | cut -c1-64)|args=JE1000_JB9000_SHELLMAX-1_FDIG12|json=0" >> $L
all=1
for t in 60000000 72000000 90000000; do
  s=$(date +%s)
  SHELLSCHUR_COLS=0:1000000000 $B/shellschur.exe $MAT 1000 9000 $t -1 12 > $O/shellschur-cols-t$t.out 2> $O/shellschur-cols-t$t.err; e1=$?
  SHELLSCHUR_MERGE=D:/ym-3x4-room-run/gate3x3-seg/shellschur-cols-t$t.out $B/shellschur.exe $MAT 1000 9000 $t -1 12 > $O/shellschur-merge-t$t.out 2> $O/shellschur-merge-t$t.err; e2=$?
  echo "SHELLRUN|t=$t|cols_exit=$e1|merge_exit=$e2|wall_s=$(( $(date +%s)-s ))|scol=$(grep -c ^SCOL $O/shellschur-cols-t$t.out)|cols_sha256=$(sha256sum $O/shellschur-cols-t$t.out | cut -c1-64)|merge_sha256=$(sha256sum $O/shellschur-merge-t$t.out | cut -c1-64)|json=0" >> $L
  python D:/ym-3x4-room-run/gate3x3-seg/compare.py "D:/ym-3x4-room-run/gate3x3-seg/shellschur-cols-t$t.out,D:/ym-3x4-room-run/gate3x3-seg/shellschur-merge-t$t.out" D:/ym-3x4-room-run/gate3x3-seg/roomschur-seg-t$t.out $t > $O/COMPARE-t$t.hbp 2>&1
  r=$(grep ^COMPARE\| $O/COMPARE-t$t.hbp | tail -1); echo "$r" >> $L
  echo "$r" | grep -q "outcome=AGREE" || all=0
done
echo "GATE|all_three_AGREE=$all|t=$(date -Iseconds)|json=0" >> $L
if [ $all = 1 ]; then
  s=$(date +%s)
  ROOMSCHUR_COLS=0:4 ROOMSCHUR_K=4 ROOMSCHUR_BUDGET=9000000000 WORKERS=8 MSYS_NO_PATHCONV=1 $B/roomschur.exe "seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-" 0 1000 9000 60000000 12 > $P/pilot.out 2> $P/pilot.err &
  RP=$!; sleep 20; powershell.exe -NoProfile -File 'D:\ym-3x4-room-run\pilot3x4\peakmem.ps1' &
  wait $RP; e=$?; wait
  echo "PILOT|cols=0:4|K=4|budget=9000000000|t=60000000|exit=$e|wall_s=$(( $(date +%s)-s ))|out_sha256=$(sha256sum $P/pilot.out | cut -c1-64)|json=0" >> $L
else
  echo "PILOT|skipped=1|reason=comparison_not_all_AGREE|json=0" >> $L
fi
tail -12 $L
