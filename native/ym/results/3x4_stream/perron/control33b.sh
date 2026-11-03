#!/bin/bash
# Final-binary control. Predictions written first:
#   one roomball run writes files byte-identical to the separate single-radius runs (K=1..5);
#   N_ball(t) <= N_sector(t): at most 7 at 60M, 7 at 72M, 44 at 90M; counts never fall as K grows.
RD=/d/ym-3x4-room-run/p0-ball; C=$RD/c33; L=$C/C33B.log; : > $L; cd $C
export MSYS_NO_PATHCONV=1
$RD/roomball.exe dev33.bin 0 5 mm >> $L
for K in 1 2 3 4 5; do cmp mm.K$K m$K.txt && echo "C33B_SAME|K=$K|identical=1|json=0" >> $L || echo "C33B_SAME|K=$K|identical=0|json=0" >> $L; done
for K in 2 3 4 5; do for T in 60000000 72000000 90000000; do
  t0=$(date +%s); $RD/shellschur.exe mm.K$K 1000 9000 $T > s$K-$T.out 2> s$K-$T.err; rc=$?
  echo "C33B_COUNT|K=$K|t_milli=$T|exit=$rc|secs=$(( $(date +%s)-t0 ))|$(grep -h '^SHELL_SCHUR|' s$K-$T.out | cut -c1-170)" >> $L
done; done
echo DONE >> $L
