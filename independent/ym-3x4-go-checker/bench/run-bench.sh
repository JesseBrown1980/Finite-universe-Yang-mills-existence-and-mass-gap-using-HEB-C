#!/usr/bin/env bash
# run-bench.sh MODE : streams a 2^22-row, 73-entry-per-row store into the checker, reports secs and peak RSS.
mode=$1
mkfifo pipe.$mode 2>/dev/null
../checker -progress a.bin b.bin < pipe.$mode > out-$mode.txt 2> err-$mode.txt &
pid=$!
start=$(date +%s)
../ymgen bench -inmem -logn 22 -k 72 -mode $mode -d1 a.bin -d2 b.bin > pipe.$mode 2>gen-$mode.txt &
gpid=$!
hwm=0
while kill -0 $pid 2>/dev/null; do
  v=$(awk '/VmHWM/ {print $2}' /proc/$pid/status 2>/dev/null)
  [ -n "$v" ] && hwm=$v
  sleep 0.5
done
wait $pid; rc=$?
wait $gpid
echo "mode=$mode rc=$rc wall=$(( $(date +%s) - start ))s peak_rss_kb=$hwm"
rm -f pipe.$mode
