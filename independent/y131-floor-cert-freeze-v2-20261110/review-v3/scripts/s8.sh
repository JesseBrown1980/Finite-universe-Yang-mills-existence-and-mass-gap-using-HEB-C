D=/root/floor-v2-final/head/independent/y131-floor-cert-freeze-v2-20261110
grep -n 'current_exe\|/proc/self\|run9\|FLOORCERT_' $D/work/design/rs/src/main.rs | head -20
grep -n '^import\|^from\|__file__\|sys.path\|open(' $D/work/design/py/cert_gate.py | head -20
grep -c . $D/work/design/py/cert_gate.py
mount | grep -E ' /tmp | / ' ; df -h /tmp /root | tail -2
