#!/bin/bash
# Idempotent close-out for the d300 pass B run. Safe to run after success, failure, or if run.sh died.
R=/d/ym-3x4-room-run/d300; S=/d/ASOLARIA-HOST8-ROOMS-300G; C=$R/CLOSEOUT.hbp
SEAL0=$(grep -o "seal_sha256=[0-9a-f]*" $R/LEDGER.hbp | head -1 | cut -d= -f2)
bad=0
for k in $(seq 341 374); do
  attrib.exe +R "D:\ASOLARIA-HOST8-ROOMS-300G\sector-$k.rooms" >/dev/null 2>&1
  attrib.exe "D:\ASOLARIA-HOST8-ROOMS-300G\sector-$k.rooms" | cut -c1-12 | grep -q R || { bad=$((bad+1)); echo "CLOSEOUT_FLAG_FAIL|sector=$k|json=0" >> $C; }
done
SEAL1=$(sha256sum $S/ROOMS-MAKE.hbp 2>/dev/null | cut -c1-64)
echo "CLOSEOUT|t=$(date -Iseconds)|readonly_restored=$((34-bad))/34|seal_before=$SEAL0|seal_after=${SEAL1:-UNREADABLE}|seal_unchanged=$([ -n "$SEAL1" ] && [ "$SEAL0" = "$SEAL1" ] && echo 1 || echo 0)|ymroom_running=$(tasklist.exe | grep -ci ymroom)|json=0" >> $C
tail -1 $C
