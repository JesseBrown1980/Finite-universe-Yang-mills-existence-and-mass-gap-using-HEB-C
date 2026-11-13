set -u
V=/root/floor-v4-verify; F=$V/repo/independent/y131-floor-cert-freeze-v2-20261110
mkdir -p $V/out; O=$V/out/F13
[ -e $O ] && { echo "F13 exists, refusing to rerun"; exit 9; }
# sampler of the host mount table (process 1) during the whole run
( n=0; mx=0; while [ ! -e $V/out/F13.exit ]; do c=$(grep -c floor-run /proc/1/mountinfo); n=$((n+1)); [ $c -gt $mx ] && mx=$c; echo "$n $mx" > $V/out/F13.sampler; sleep 1; done; c=$(grep -c floor-run /proc/1/mountinfo); echo "$n $mx after=$c" > $V/out/F13.sampler ) &
cd $F
date -u +%FT%TZ > $V/out/F13.start
env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh --test-r 21/2 --test-m0 11,12,13 --test-f '1;8,7,6,5,4;6,5,4,3' --test-census --test-hang 1:cert,2:cert --test-g0 99372/1000 --test-out $O > $V/out/F13.stdout.txt 2>&1
echo $? > $V/out/F13.exit.tmp; date -u +%FT%TZ >> $V/out/F13.exit.tmp; mv $V/out/F13.exit.tmp $V/out/F13.exit
wait
cat $V/out/F13.exit $V/out/F13.sampler; tail -1 $V/out/F13.stdout.txt | cut -c1-400
