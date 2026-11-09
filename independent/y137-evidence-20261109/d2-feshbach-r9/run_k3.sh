#!/usr/bin/env bash
# K3 runs (after the K3 cache exists): amplitude estimate (12 Jacobi steps, check 20) and the
# K3 sandwich point test at the K2 unconditional E2_even upper bound 699567503/10^7 plus bisection.
cd /mnt/c/tmp/opus55/ym137-fable5-20261109/d2-feshbach-r9 || exit 1
ulimit -v 2400000
mode=$1
if [ "$mode" = amp ]; then
  /usr/bin/time -f 'rss_kb=%M wall=%e' timeout 2400 python3 -I -B fe_k3.py run 12 20 12 9 k3-amp.rows > k3-amp.log 2>&1
  echo "k3 amp rc=$?"
else
  /usr/bin/time -f 'rss_kb=%M wall=%e' timeout 2400 python3 -I -B fe_k3lower.py 12 12 7 699567503/10000000 k3-lower.rows 7 > k3-lower.log 2>&1
  echo "k3 lower rc=$?"
fi
