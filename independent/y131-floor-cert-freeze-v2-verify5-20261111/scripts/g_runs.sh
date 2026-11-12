# genuine small rehearsal receipts from the new launcher (fresh clone repoC), r = 14 only
set -u
V=/root/floor-v5-verify; F=$V/repoC/independent/y131-floor-cert-freeze-v2-20261110; O=$V/out/G; mkdir -p $O
run() { # name args...
  local n=$1; shift
  [ -e $O/$n ] && { echo "RUN|id=$n|skipped_exists|json=0" >> $O/runs.hbp; return; }
  local t0=$(date +%s)
  ( cd $F && env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh "$@" --test-out $O/$n > $O/$n.out 2>&1 ); local e=$?
  echo "RUN|id=$n|exit=$e|secs=$(( $(date +%s) - t0 ))|final=$(tail -1 $O/$n.out | cut -d'|' -f2-7)|publish=$(grep -o '^PUBLISH|receipt_sha256=[0-9a-f]*' $O/$n.out | cut -d= -f2)|json=0" >> $O/runs.hbp
}
run D1 --test-r 14 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 1/1
run D2 --test-r 14 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 1112/10
run D3 --test-r 14 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 112/1
run D4 --test-r 14 --test-m0 7 --test-f 1 --test-g0 1109058/10000
run U2 --test-r 14 --test-m0 7,8 --test-f '1;4,3,2,1' --test-g0 111/1
run L1 --test-r 14 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 1/1 --test-limit-kb 5000
run H1 --test-r 14 --test-m0 7,8 --test-f '1;4,3,2,1' --test-g0 1112/10 --test-hang 1:cert
touch $O/runs.done
