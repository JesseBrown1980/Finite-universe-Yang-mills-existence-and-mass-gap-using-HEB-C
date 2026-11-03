#!/bin/bash
# Final receipts for the frozen tools. Every row below comes from the binaries hashed in FINAL.hbp.
export MSYS_NO_PATHCONV=1
RD=/d/ym-3x4-room-run/p0-ball
W=$RD/final; mkdir -p $W; cd $W
L=$W/FINAL.hbp; : > $L
echo "FINAL_EXE|perroncert=$(sha256sum $RD/perroncert.exe | cut -c1-64)|flatcomp=$(sha256sum $RD/flatcomp.exe | cut -c1-64)|roomball=$(sha256sum $RD/roomball.exe | cut -c1-64)|ball=$(sha256sum $RD/ball.exe | cut -c1-64)|cluster=$(sha256sum $RD/cluster.exe | cut -c1-64)|shellschur=$(sha256sum $RD/shellschur.exe | cut -c1-64)|ymroom=$(sha256sum $RD/ymroom.exe | cut -c1-64)|json=0" >> $L

# flatcomp: text and store must print the same row, and a changed byte must print none.
C=$RD/c33
$RD/flatcomp.exe D:/ym-3x4-room-run/p0-ball/c33/t33.txt > flat-text.out
$RD/flatcomp.exe --room D:/ym-3x4-room-run/p0-ball/c33/dev33.bin 0 > flat-room.out; echo "FINAL_FLAT_ROOM|exit=$?|json=0" >> $L
cat flat-text.out flat-room.out >> $L
A=$(sed 's/|matrix=[^|]*|/|/' flat-text.out); B=$(grep '^FLATCOMP|' flat-room.out | sed 's/|matrix=[^|]*|/|/')
[ "$A" = "$B" ] && echo "FINAL_FLAT_SAME|1|json=0" >> $L || echo "FINAL_FLAT_SAME|0|json=0" >> $L
cp $C/dev33.bin dev33-bad.bin
python -I -c "
import sys
p=sys.argv[1]; f=open(p,'r+b'); f.seek(4096+123456); b=f.read(1); f.seek(4096+123456); f.write(bytes([b[0]^1])); f.close()" D:/ym-3x4-room-run/p0-ball/final/dev33-bad.bin
$RD/flatcomp.exe --room D:/ym-3x4-room-run/p0-ball/final/dev33-bad.bin 0 > flat-bad.out; echo "FINAL_FLAT_BAD|exit=$?|flatcomp_rows=$(grep -c '^FLATCOMP|' flat-bad.out)|json=0" >> $L
$RD/perroncert.exe check D:/ym-3x4-room-run/p0-ball/final/dev33-bad.bin 0 1000 9000 D:/ym-3x4-room-run/p0-ball/pc33/d74.bin > perron-bad.out; echo "FINAL_PERRON_BAD|exit=$?|certified_rows=$(grep -c '^PERRONCERT|' perron-bad.out)|json=0" >> $L
rm -f dev33-bad.bin

# 3x3 table, plain sweeps.
DEV=D:/ym-3x4-room-run/p0-ball/c33/dev33.bin
for spec in 60000000:60 70000000:60 72000000:80 74000000:80 75000000:80 76000000:80 76400000:80; do
  T=${spec%%:*}; S=${spec##*:}
  $RD/perroncert.exe solve $DEV 0 1000 9000 $T $S D:/ym-3x4-room-run/p0-ball/final/d$T.bin > s$T.out 2>&1
  echo "PERRON33_RUN|solve_t_milli=$T|sweeps=$S|exit=$?|$(tail -1 s$T.out | sed -E 's/^PERRONCERT\|//')" >> $L
done
PERRONCERT_START=D:/ym-3x4-room-run/p0-ball/final/d76400000.bin $RD/perroncert.exe solve $DEV 0 1000 9000 76400000 200 D:/ym-3x4-room-run/p0-ball/final/d76400000b.bin > w764.out 2>&1
echo "PERRON33_RUN|solve_t_milli=76400000|sweeps=80+200|exit=$?|$(tail -1 w764.out | sed -E 's/^PERRONCERT\|//')" >> $L
# Past the level the solve must stop by itself and certify nothing.
$RD/perroncert.exe solve $DEV 0 1000 9000 78000000 400 > over.out 2>&1
echo "PERRON33_OVER|solve_t_milli=78000000|exit=$?|last=$(tail -1 over.out | cut -c1-120)|json=0" >> $L
# Inner sweeps: fewer disk passes, same exact check.
for spec in "74000000 13 100 8" "76000000 13 200 12"; do set -- $spec
  PERRONCERT_INNER=$2:$3 $RD/perroncert.exe solve $DEV 0 1000 9000 $1 $4 > inner$1.out 2>&1
  echo "PERRON33_INNER|solve_t_milli=$1|keep_mag=$2|inner_limit=$3|full_passes=$4|exit=$?|$(tail -1 inner$1.out | sed -E 's/^PERRONCERT\|//')" >> $L
  grep PERRONCERT_INNER inner$1.out | tail -1 >> $L
done
# Separately written checkers, on one saved vector, must agree exactly.
python -I D:/ym-3x4-room-run/p0-ball/check_d.py $DEV D:/ym-3x4-room-run/p0-ball/final/d74000000.bin 1000 9000 >> $L 2>&1
python -I D:/ym-3x4-room-run/p0-ball/check_d_stream.py $DEV D:/ym-3x4-room-run/p0-ball/final/d74000000.bin 1000 9000 >> $L 2>&1
$RD/perroncert.exe check $DEV 0 1000 9000 D:/ym-3x4-room-run/p0-ball/final/d74000000.bin >> $L 2>&1
echo "PERRON33_WARNINGS|checkpoint_warn_rows=$(cat s*.out w764.out over.out inner*.out | grep -c PERRONCERT_WARN)|json=0" >> $L

# Small lattices: the certified value never above the level.
for spec in "2x2 46466796 46468750" "2x3 58441406 58443359"; do set -- $spec
  for dist in 5000000 2000000 500000; do
    t0=$(( $2 - dist ))
    row=$($RD/perroncert.exe solve D:/ym-3x4-room-run/p0-ball/small/$1/dev.bin 0 1000 9000 $t0 200 | tail -1)
    tc=$(echo "$row" | sed -E 's/.*t_cert_milli=([0-9]+).*/\1/')
    echo "SMALL_S3|L=$1|lambda1_in=[$2,$3]|solve_t_milli=$t0|t_cert_milli=$tc|below_lambda1=$([ "$tc" -le "$3" ] && echo 1 || echo 0)|shortfall_to_hi=$(( $3 - tc ))|json=0" >> $L
  done
done
rm -f d*.bin
echo DONE >> $L
