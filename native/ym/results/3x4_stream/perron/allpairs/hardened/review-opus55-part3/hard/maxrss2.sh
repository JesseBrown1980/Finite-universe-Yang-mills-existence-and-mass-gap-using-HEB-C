#!/bin/bash
# The fix for the reading: a small helper process between the Python parent that holds the store and the tool. Rows only, json=0.
R=/mnt/c/tmp/opus55/allpairs-review-20261103/hard
export TMPDIR=$R/tmp PATH=/usr/bin:/bin
python3 -I -X utf8 - "$R/clones/linux/native/ym/target/release/allpairs" /mnt/d/ym-3x4-room-run/p0-ball/small/2x2/dev.bin <<'PY'
import subprocess, sys
exe, store = sys.argv[1], sys.argv[2]
big = bytearray(700 << 20)
for i in range(0, len(big), 4096):
    big[i] = 1
helper = "import os,subprocess,sys;p=subprocess.Popen(sys.argv[1:],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);_,s,r=os.wait4(p.pid,0);print(r.ru_maxrss*1024,os.waitstatus_to_exitcode(s))"
r = subprocess.run([sys.executable, "-I", "-c", helper, exe, store, "0"], capture_output=True, text=True)
peak, code = r.stdout.split()
print("MAXRSS|parent=python_holding_700_MiB_through_a_small_helper|peak_bytes=%s|exit=%s|json=0" % (peak, code))
PY
