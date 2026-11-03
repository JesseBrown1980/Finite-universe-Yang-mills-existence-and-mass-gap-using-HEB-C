#!/bin/bash
# The instrument in run_hardening_controls.py on Linux: os.wait4's ru_maxrss, read from a Python parent that holds the store. Same tool, same small store, two parents. Rows only, json=0.
R=/mnt/c/tmp/opus55/allpairs-review-20261103/hard
export TMPDIR=$R/tmp CARGO_HOME=$R/tmp/cargo-home PATH=/root/.cargo/bin:/usr/bin:/bin
cd "$R/clones/linux" || exit 9
git status --short | head -3
( cd native/ym && cargo +1.81.0 build --locked --release -p evolvers --bin allpairs ) > "$R/out/maxrss-build.log" 2>&1
X=$R/clones/linux/native/ym/target/release/allpairs
echo "MAXRSS_BUILD|file_sha256=$(sha256sum "$X" | cut -c1-64)|json=0"
python3 -I -X utf8 - "$X" /mnt/d/ym-3x4-room-run/p0-ball/small/2x2/dev.bin <<'PY'
import os, subprocess, sys
exe, store = sys.argv[1], sys.argv[2]
def run():
    p = subprocess.Popen([exe, store, "0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    _, status, ru = os.wait4(p.pid, 0)
    return ru.ru_maxrss * 1024, os.waitstatus_to_exitcode(status)
a = run()
print("MAXRSS|parent=small_python|peak_bytes=%d|exit=%d|json=0" % a)
big = bytearray(700 << 20)
for i in range(0, len(big), 4096):
    big[i] = 1
b = run()
print("MAXRSS|parent=python_holding_700_MiB|peak_bytes=%d|exit=%d|json=0" % b)
del big
c = run()
print("MAXRSS|parent=same_python_after_freeing_it|peak_bytes=%d|exit=%d|json=0" % c)
PY
