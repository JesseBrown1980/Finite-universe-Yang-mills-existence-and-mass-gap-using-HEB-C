set -u
V=/root/floor-v4-verify
[ -e $V/out/F13.exit ] || { echo F13_not_finished; exit 3; }
rm -rf $V/second/F13; cp -a $V/out/F13 $V/second/F13; rm -rf $V/second/F13/tmp $V/second/F13/target
cd $V/exp0/independent/y131-floor-cert-freeze-v2-20261110
python3 -I -B final/tools/recheck_floor.py receipt=$V/second/F13/FLOOR-RUN-RECEIPT.hbp out=$V/out/F13.recheck.out > $V/out/F13.recheck.txt 2>&1; echo $? > $V/out/F13.recheck.txt.exit
tail -2 $V/out/F13.recheck.txt | cut -c1-500
