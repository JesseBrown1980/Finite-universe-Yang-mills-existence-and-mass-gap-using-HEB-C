for i in $(seq 1 130); do
  if pgrep -x floorcert >/dev/null || pgrep -f 'py/cert_gate.py' >/dev/null || pgrep -f 'run_floor.sh' >/dev/null; then sleep 3; else break; fi
done
echo "idle_after_loops=$i"
