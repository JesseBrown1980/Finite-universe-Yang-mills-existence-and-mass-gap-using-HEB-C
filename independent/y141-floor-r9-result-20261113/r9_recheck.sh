set -u
# The recheck of the r = 9 receipt from a clean export of the freeze commit (row 131). Runs once.
B=/root/floor-r9; F=$B/repo/independent/y131-floor-cert-freeze-v2-20261110
PUB=79e6c40a20b7972c70e68f69cb580d261e540f29336464cd54836ac06961daa1
[ -e $B/recheck.exit ] && { echo "RECHECK|already ran, refusing"; exit 9; }
[ -e $B/exp0 ] || { mkdir -p $B/exp0 && git -C $B/repo archive c8dbcdbf990114292313cbc410a745a14ba0b778 | tar -x -C $B/exp0; }
[ -e $B/second/run9 ] || { mkdir -p $B/second && cp -a $F/work/run9 $B/second/run9 && rm -rf $B/second/run9/tmp $B/second/run9/target; }
echo "$PUB  $B/second/run9/FLOOR-RUN-RECEIPT.hbp" | sha256sum -c - || exit 8
cd $B/exp0/independent/y131-floor-cert-freeze-v2-20261110 || exit 7
date -u +%FT%TZ > $B/recheck.start
python3 -I -B final/tools/recheck_floor.py receipt=$B/second/run9/FLOOR-RUN-RECEIPT.hbp receipt_sha256=$PUB out=$B/recheck.out > $B/recheck.txt 2>&1
e=$?
echo $e > $B/recheck.exit; date -u +%FT%TZ >> $B/recheck.exit
echo "RECHECK|exit=$e"; tail -4 $B/recheck.txt
