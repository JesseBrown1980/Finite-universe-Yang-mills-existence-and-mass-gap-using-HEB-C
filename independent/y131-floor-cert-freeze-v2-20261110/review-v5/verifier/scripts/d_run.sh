# usage: d_run.sh NAME R M0LIST FSPEC G0
set -u
V=/root/floor-v4-verify; F=$V/repoB/independent/y131-floor-cert-freeze-v2-20261110; O=$V/out/D; mkdir -p $O $V/second
N=$1; cd $F
env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh --test-r "$2" --test-m0 "$3" --test-f "$4" --test-g0 "$5" --test-out $O/$N > $O/$N.out 2>&1; e=$?
echo "RUN|id=$N|exit=$e|$(tail -1 $O/$N.out | cut -d'|' -f2-6)|steps=$(tail -1 $O/$N.out | grep -o 'steps_run=[^|]*')|acc=$(tail -1 $O/$N.out | grep -o 'accepted_certificates=[^|]*')|json=0"
grep '^DECISION|' $O/$N.out | cut -c1-250
grep '^STEP|' $O/$N/FLOOR-RUN-RECEIPT.hbp 2>/dev/null | cut -d'|' -f2-9
rm -rf $V/second/$N; cp -a $O/$N $V/second/$N 2>/dev/null; rm -rf $V/second/$N/tmp $V/second/$N/target
cd $V/exp0/independent/y131-floor-cert-freeze-v2-20261110
python3 -I -B final/tools/recheck_floor.py receipt=$V/second/$N/FLOOR-RUN-RECEIPT.hbp > $O/$N.recheck.txt 2>&1; c=$?
echo "CHECK|id=$N|exit=$c|$(grep '^DECISION_HERE' $O/$N.recheck.txt | cut -d'|' -f2-6)|json=0"
tail -1 $O/$N.recheck.txt | cut -c1-400
