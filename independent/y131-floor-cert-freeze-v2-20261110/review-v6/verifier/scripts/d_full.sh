set -u
V=/root/floor-v5-verify; F=$V/repoC/independent/y131-floor-cert-freeze-v2-20261110
mkdir -p $V/out; O=$V/out/D13
[ -e $O ] && { echo "D13 exists, refusing to rerun" > $V/out/D13.refused; exit 9; }
rm -rf $V/exp0; mkdir -p $V/exp0; git -C $V/repoC archive 3c41ea2d9dd01de0ffcd547a7e7d417baa2ca6c0 | tar -x -C $V/exp0
( n=0; mx=0; while [ ! -e $V/out/D13.exit ]; do c=$(grep -c floor-run /proc/1/mountinfo); n=$((n+1)); [ $c -gt $mx ] && mx=$c; echo "$n $mx" > $V/out/D13.sampler; sleep 1; done; echo "$n $mx after=$(grep -c floor-run /proc/1/mountinfo)" > $V/out/D13.sampler ) &
cd $F
date -u +%FT%TZ > $V/out/D13.start
env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh --test-r 21/2 --test-m0 11,12,13 --test-f '1;8,7,6,5,4;6,5,4,3' --test-census --test-hang 1:cert,2:cert --test-g0 99372/1000 --test-out $O > $V/out/D13.stdout.txt 2>&1
echo $? > $V/out/D13.exit.tmp; date -u +%FT%TZ >> $V/out/D13.exit.tmp; mv $V/out/D13.exit.tmp $V/out/D13.exit
wait
PUB=$(grep -o '^PUBLISH|receipt_sha256=[0-9a-f]*' $V/out/D13.stdout.txt | cut -d= -f2)
mkdir -p $V/second; rm -rf $V/second/D13; cp -a $O $V/second/D13; rm -rf $V/second/D13/tmp $V/second/D13/target
cd $V/exp0/independent/y131-floor-cert-freeze-v2-20261110
date -u +%FT%TZ > $V/out/D13.check.start
python3 -I -B final/tools/recheck_floor.py receipt=$V/second/D13/FLOOR-RUN-RECEIPT.hbp receipt_sha256=$PUB out=$V/out/D13.recheck.out > $V/out/D13.recheck.txt 2>&1; echo $? > $V/out/D13.recheck.exit
date -u +%FT%TZ >> $V/out/D13.recheck.exit
touch $V/out/D13.done
