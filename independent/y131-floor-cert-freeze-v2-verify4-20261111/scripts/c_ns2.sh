set -u
V=/root/floor-v4-verify; F=$V/repoB/independent/y131-floor-cert-freeze-v2-20261110; O=$V/out/C; mkdir -p $O
cd $F
SRC=$(cat final/tools/run_floor.sh)
A="--test-r 12 --test-m0 7 --test-f 1 --test-g0 100/1 --test-out"
# C0 normal documented call, host mount table sampled every 0.1 s
( n=0; mx=0; while [ ! -e $O/C0.done ]; do c=$(grep -c floor-run /proc/1/mountinfo); n=$((n+1)); [ $c -gt $mx ] && mx=$c; sleep 0.1; done; echo "samples=$n max=$mx after=$(grep -c floor-run /proc/1/mountinfo)" > $O/C0.sampler ) &
env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A $O/C0 > $O/C0.out 2>&1; e=$?; touch $O/C0.done; wait
echo "CASE|id=C0|exit=$e|$(cat $O/C0.sampler)|ns_note=$(grep -o 'mount_namespace=private_CHECKED[^|]*|namespace_of_this_process=[^|]*|namespace_of_the_parent_process=[^|]*|namespace_of_process_1=[^|]*' $O/C0.out | head -1)|last=$(tail -1 $O/C0.out | cut -c1-200)|json=0"
# C4 direct entry by nsenter into a private namespace held by another process
unshare -m --propagation private sleep 900 & HOLD=$!
sleep 1
H=$(pgrep -P $HOLD sleep || echo $HOLD); [ "$(readlink /proc/$H/ns/mnt)" != "$(readlink /proc/1/ns/mnt)" ] || H=$HOLD
echo "holder_pid=$H holder_ns=$(readlink /proc/$H/ns/mnt) init_ns=$(readlink /proc/1/ns/mnt) holder_shared=$(grep -cE ' (shared|master):' /proc/$H/mountinfo)"
env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$F /usr/bin/nsenter -t $H -m /usr/bin/bash --noprofile --norc -c "$SRC" run_floor.sh $A $O/C4 > $O/C4.out 2>&1 &
RP=$!
seen=0; for i in $(seq 1 600); do if [ -e /proc/$H/root$O/C4/tmp/tools/floorcert ]; then seen=1; break; fi; kill -0 $RP 2>/dev/null || break; sleep 0.2; done
echo "C4_outside_view|tools_visible_via_/proc/HOLDER/root=$seen|listing=$(ls /proc/$H/root$O/C4/tmp/tools 2>&1 | tr '\n' ',')|holder_mountinfo_floor_run=$(grep -c floor-run /proc/$H/mountinfo)|host_floor_run=$(grep -c floor-run /proc/1/mountinfo)|nsenter_view=$(nsenter -t $H -m grep -c floor-run /proc/self/mountinfo)"
wait $RP; e=$?
echo "CASE|id=C4|exit=$e|run_dir_exists=$([ -e $O/C4 ] && echo 1 || echo 0)|host_floor_run_mounts=$(grep -c floor-run /proc/1/mountinfo)|holder_floor_run_mounts_after=$(grep -c floor-run /proc/$H/mountinfo)|ns_note=$(grep -o 'mount_namespace=private_CHECKED' $O/C4.out | head -1)|last=$(tail -1 $O/C4.out | cut -c1-220)|json=0"
kill $HOLD 2>/dev/null; kill $H 2>/dev/null
# C5 parent in another (private) namespace, stage 2 in a nested private namespace, no stage 1
export SRC F O A
unshare -m --propagation private /usr/bin/bash --noprofile --norc -c 'env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$F /usr/bin/unshare -m --propagation private /usr/bin/bash --noprofile --norc -c "$SRC" run_floor.sh $A $O/C5; echo "inner_exit=$?"' > $O/C5.out 2>&1
echo "CASE|id=C5|exit=$(grep -o 'inner_exit=[0-9]*' $O/C5.out)|run_dir_exists=$([ -e $O/C5 ] && echo 1 || echo 0)|host_floor_run_mounts=$(grep -c floor-run /proc/1/mountinfo)|ns_note=$(grep -o 'mount_namespace=private_CHECKED' $O/C5.out | head -1)|last=$(grep FLOOR_RUN $O/C5.out | tail -1 | cut -c1-220)|json=0"
