#!/bin/bash
# Record of the warm-start calibration on the 3x3 store, run on 2026-11-02 to choose the 3x4 threshold.
# Group A is a slip kept on purpose: the variable holding the inner limit was empty, so PERRONCERT_INNER=":200"
# failed to parse and those runs are plain sweeps. They show that t_cert can fall below its starting value (75.156799)
# until d settles, which is why a warm start writes to its own file.
export MSYS_NO_PATHCONV=1
RD=D:/ym-3x4-room-run/p0-ball
EXE=/d/ym-3x4-room-run/p0-ball/perroncert.exe
O=$RD/warmcal
OL=/d/ym-3x4-room-run/p0-ball/warmcal
START=$RD/pc33-final/d75000000.bin

for T in 76200000 76300000 76400000; do
  PERRONCERT_START=$START PERRONCERT_INNER=:200 PERRONCERT_CHECK_EVERY=2 $EXE solve $RD/c33/dev33.bin 0 1000 9000 $T 10 $O/w33-$T.bin > $OL/w33-$T.out 2>&1
done

for spec in "12:200 76200000" "12:200 76300000" "12:200 76400000" "12:1000 76400000"; do
  set -- $spec; I=$1; T=$2; tag=$T-${I/:/_}
  PERRONCERT_START=$START PERRONCERT_INNER=$I PERRONCERT_CHECK_EVERY=2 $EXE solve $RD/c33/dev33.bin 0 1000 9000 $T 10 $O/w33-$tag.bin > $OL/w33-$tag.out 2>&1
done

for spec in "12:200 76430000" "12:200 76500000" "12:200 76700000" "12:200 77000000"; do
  set -- $spec; I=$1; T=$2; tag=$T-${I/:/_}
  PERRONCERT_START=$START PERRONCERT_INNER=$I PERRONCERT_CHECK_EVERY=1 $EXE solve $RD/c33/dev33.bin 0 1000 9000 $T 8 $O/w33-$tag.bin > $OL/w33-$tag.out 2>&1
done
