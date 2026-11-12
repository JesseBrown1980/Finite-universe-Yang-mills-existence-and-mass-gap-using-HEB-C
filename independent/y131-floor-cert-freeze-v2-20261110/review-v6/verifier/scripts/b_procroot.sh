O=/root/floor-v5-verify/out/D13
for p in $(pgrep -f 'bash --noprofile --norc -c .*[r]un_floor.sh'); do
  echo "pid=$p ns=$(readlink /proc/$p/ns/mnt) init=$(readlink /proc/1/ns/mnt) ppid=$(awk '/^PPid/{print $2}' /proc/$p/status)"
  echo "host_view_tools: $(ls $O/tmp/tools 2>&1 | tr '\n' ,)"
  echo "procroot_view_tools: $(ls /proc/$p/root$O/tmp/tools 2>&1 | tr '\n' ,)"
  echo "procroot_sha_gate: $(sha256sum /proc/$p/root$O/tmp/tools/gate_required.sh 2>&1 | cut -c1-80)"
done | head -12
