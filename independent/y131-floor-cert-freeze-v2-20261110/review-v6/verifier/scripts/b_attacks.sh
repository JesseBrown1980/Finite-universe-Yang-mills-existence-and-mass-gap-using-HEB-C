# b_attacks.sh -- verifier seat (opus55), verification 5, gate B: launcher re-attacks. r = 12 only. Own clones only.
set -u
V=/root/floor-v5-verify; O=$V/out/B; mkdir -p $O
TC=/root/.rustup/toolchains/1.81-x86_64-unknown-linux-gnu/bin
NEW=3c41ea2d9dd01de0ffcd547a7e7d417baa2ca6c0
A="--test-r 12 --test-m0 7 --test-f 1 --test-g0 100/1"
row() { echo "$1" | tee -a $O/B.hbp; }
last() { tail -1 "$1" | cut -d'|' -f2-3,5-7 | cut -c1-230; }
mk() { # fresh local clone NAME at NEW with the pin-free binary prebuilt (copied from repoC)
  rm -rf $V/$1; git clone -q $V/repoC $V/$1; git -C $V/$1 checkout -q $NEW
  mkdir -p $V/$1/independent/y131-floor-cert-freeze-v2-20261110/work/design/rs/target/release
  cp $V/repoC/independent/y131-floor-cert-freeze-v2-20261110/work/design/rs/target/release/floorcert $V/$1/independent/y131-floor-cert-freeze-v2-20261110/work/design/rs/target/release/floorcert
}
mk repoD; FD=$V/repoD/independent/y131-floor-cert-freeze-v2-20261110
SRC=$(cat $FD/final/tools/run_floor.sh)

# B0 baseline frozen-build rehearsal (clean clone): its binary is the comparison for the build attacks and the FZA input
( cd $FD && env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-frozen-build --test-out $O/B0 > $O/B0.out 2>&1; echo $? > $O/B0.rc )
row "CASE|id=B0_frozen_build_clean|exit=$(cat $O/B0.rc)|frozen_binary=$(sha256sum $O/B0/target/release/floorcert 2>/dev/null | cut -d' ' -f1)|$(last $O/B0.out)|json=0"

# B1 = C4 rebuilt: a holder process sits in a private namespace; direct stage-2 entry by nsenter -t HOLDER
unshare -m --propagation private sleep 300 & HP=$!; sleep 1
H=$(pgrep -P $HP sleep || echo $HP); [ "$(readlink /proc/$H/ns/mnt)" != "$(readlink /proc/1/ns/mnt)" ] || H=$HP
env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$FD /usr/bin/nsenter -t $H -m /usr/bin/bash --noprofile --norc -c "$SRC" run_floor.sh $A --test-out $O/B1 > $O/B1.out 2>&1; e=$?
row "CASE|id=B1_C4_nsenter_into_process_held_ns|exit=$e|run_dir=$([ -e $O/B1 ] && echo 1 || echo 0)|$(last $O/B1.out)|json=0"
kill $H $HP 2>/dev/null; wait $HP 2>/dev/null

# B2 = C4 variant NEW: the namespace is held by a bind mount of its nsfs file, no process in it
mkdir -p $V/nsd; mount --bind $V/nsd $V/nsd; mount --make-private $V/nsd; touch $V/nsd/mnt
unshare --mount=$V/nsd/mnt --propagation private /usr/bin/true; echo "nsfile_bound=$(grep -c ' /root/floor-v5-verify/nsd/mnt ' /proc/self/mountinfo)" > $O/B2.ns
env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$FD /usr/bin/nsenter --mount=$V/nsd/mnt /usr/bin/bash --noprofile --norc -c "$SRC" run_floor.sh $A --test-out $O/B2 > $O/B2.out 2>&1; e=$?
after=$(nsenter --mount=$V/nsd/mnt grep -c floor-run /proc/self/mountinfo)
tools=$(nsenter --mount=$V/nsd/mnt ls $O/B2/tmp/tools 2>&1 | tr '\n' ',')
row "CASE|id=B2_nsenter_into_ns_held_by_a_bind_mount_no_process|$(cat $O/B2.ns)|exit=$e|run_dir=$([ -e $O/B2 ] && echo 1 || echo 0)|ns_note=$(grep -o 'other_processes_in_this_namespace=[0-9]*' $O/B2.out | head -1)|floor_run_mounts_left_in_held_ns_after_run=$after|private_tools_listed_after_run_by_reentering=$tools|host_floor_run=$(grep -c floor-run /proc/1/mountinfo)|$(last $O/B2.out)|json=0"
nsenter --mount=$V/nsd/mnt sha256sum $O/B2/tmp/tools/gate_required.sh > $O/B2.toolsha 2>&1
umount $V/nsd/mnt; umount $V/nsd

# B3 mid-run entry by the launcher's own pid (after the start and after-mount checks), leaving before the close
( cd $FD && env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-out $O/B3 > $O/B3.out 2>&1; echo $? > $O/B3.rc ) &
BP=$!; LP=""; for i in $(seq 1 300); do LP=$(pgrep -f 'bash --noprofile --norc -c .*[r]un_floor.sh --test-r 12 --test-m0 7 --test-f 1 --test-g0 100/1 --test-out /root/floor-v5-verify/out/B/B3' | head -1); [ -n "$LP" ] && grep -q '^NOTE|before_m0' $O/B3.out 2>/dev/null && break; sleep 0.2; done
seen=$(nsenter -t $LP -m sh -c "ls $O/B3/tmp/tools | tr '\n' ,; sleep 2")
wait $BP
row "CASE|id=B3_nsenter_by_launcher_pid_midrun_leave_before_close|exit=$(cat $O/B3.rc)|entered_pid=$LP|tools_seen_from_inside=$seen|$(last $O/B3.out)|json=0"

# B3b same entry, staying until after the close
( cd $FD && env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-out $O/B3b > $O/B3b.out 2>&1; echo $? > $O/B3b.rc ) &
BP=$!; LP=""; for i in $(seq 1 300); do LP=$(pgrep -f 'bash --noprofile --norc -c .*[r]un_floor.sh --test-r 12 --test-m0 7 --test-f 1 --test-g0 100/1 --test-out /root/floor-v5-verify/out/B/B3b' | head -1); [ -n "$LP" ] && grep -q '^NOTE|before_m0' $O/B3b.out 2>/dev/null && break; sleep 0.2; done
nsenter -t $LP -m sleep 240 & SP=$!
wait $BP; kill $SP 2>/dev/null
row "CASE|id=B3b_nsenter_by_launcher_pid_staying_past_close|exit=$(cat $O/B3b.rc)|close_note=$(grep -o 'close=another_process[^|]*' $O/B3b.out | head -1)|$(last $O/B3b.out)|json=0"

# B4 = E4 rebuilt: untracked work/design/rs/.cargo/config.toml, frozen build
mkdir -p $FD/work/design/rs/.cargo; printf '[profile.release]\nopt-level = 2\n' > $FD/work/design/rs/.cargo/config.toml
( cd $FD && env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-frozen-build --test-out $O/B4 > $O/B4.out 2>&1; echo $? > $O/B4.rc )
row "CASE|id=B4_E4_untracked_rs_cargo_config|exit=$(cat $O/B4.rc)|$(last $O/B4.out)|json=0"
rm -rf $FD/work/design/rs/.cargo
# B4b config in the repository root .cargo
mkdir -p $V/repoD/.cargo; printf '[profile.release]\nopt-level = 2\n' > $V/repoD/.cargo/config.toml
( cd $FD && env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-frozen-build --test-out $O/B4b > $O/B4b.out 2>&1; echo $? > $O/B4b.rc )
row "CASE|id=B4b_untracked_cargo_config_at_repo_root|exit=$(cat $O/B4b.rc)|$(last $O/B4b.out)|json=0"
rm -rf $V/repoD/.cargo

# B5 NEW: untracked workspace root above the crate: work/design/Cargo.toml [workspace] members=[rs] with a release profile
printf '[workspace]\nmembers = ["rs"]\nresolver = "2"\n\n[profile.release]\nopt-level = 2\noverflow-checks = false\n' > $FD/work/design/Cargo.toml
cp $FD/work/design/rs/Cargo.lock $FD/work/design/Cargo.lock
echo "status_tracked=$(git -C $V/repoD status --porcelain --untracked-files=no | wc -l) untracked=$(git -C $V/repoD status --porcelain | tr '\n' ' ')" > $O/B5.status
( cd $FD && env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-frozen-build --test-out $O/B5 > $O/B5.out 2>&1; echo $? > $O/B5.rc )
row "CASE|id=B5_untracked_workspace_Cargo.toml_above_the_crate|$(cat $O/B5.status)|exit=$(cat $O/B5.rc)|frozen_binary=$(sha256sum $O/B5/target/release/floorcert 2>/dev/null | cut -d' ' -f1)|differs_from_B0=$([ "$(sha256sum $O/B5/target/release/floorcert 2>/dev/null | cut -d' ' -f1)" != "$(sha256sum $O/B0/target/release/floorcert | cut -d' ' -f1)" ] && echo 1 || echo 0)|build_log_warning=$(grep -c 'profiles for the non root package will be ignored' $O/B5/log/build_frozen.txt 2>/dev/null)|$(last $O/B5.out)|json=0"
rm -f $FD/work/design/Cargo.toml $FD/work/design/Cargo.lock

# B6 = E3b rebuilt: a tracked file outside the freeze folder modified
F1=$(git -C $V/repoD ls-files | grep -v '^independent/y131-floor-cert-freeze-v2-20261110/' | grep -E '\.md$' | head -1)
echo "x" >> "$V/repoD/$F1"
( cd $FD && env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-frozen-build --test-out $O/B6 > $O/B6.out 2>&1; echo $? > $O/B6.rc )
row "CASE|id=B6_E3b_tracked_file_outside_folder_modified|file=$F1|exit=$(cat $O/B6.rc)|$(last $O/B6.out)|json=0"
# B6b NEW: same modification hidden from git status by update-index --assume-unchanged
git -C $V/repoD update-index --assume-unchanged "$F1"
( cd $FD && env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-frozen-build --test-out $O/B6b > $O/B6b.out 2>&1; echo $? > $O/B6b.rc )
row "CASE|id=B6b_tracked_change_hidden_by_assume_unchanged|status_lines=$(git -C $V/repoD status --porcelain --untracked-files=no | wc -l)|exit=$(cat $O/B6b.rc)|$(last $O/B6b.out)|json=0"
git -C $V/repoD update-index --no-assume-unchanged "$F1"; git -C $V/repoD checkout -q -- "$F1"

# B7 NEW: HEAD is a local commit on top of the freeze commit that adds a (tracked) workspace root above the crate
printf '[workspace]\nmembers = ["rs"]\nresolver = "2"\n\n[profile.release]\nopt-level = 2\noverflow-checks = false\n' > $FD/work/design/Cargo.toml
cp $FD/work/design/rs/Cargo.lock $FD/work/design/Cargo.lock
git -C $V/repoD -c user.name=x -c user.email=x@x add independent/y131-floor-cert-freeze-v2-20261110/work/design/Cargo.toml independent/y131-floor-cert-freeze-v2-20261110/work/design/Cargo.lock
git -C $V/repoD -c user.name=x -c user.email=x@x commit -q -m "local test commit, never pushed"
( cd $FD && env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-frozen-build --test-out $O/B7 > $O/B7.out 2>&1; echo $? > $O/B7.rc )
row "CASE|id=B7_descendant_commit_adds_workspace_root|HEAD=$(git -C $V/repoD rev-parse --short HEAD)|freeze_commit_used=$(grep -o 'NOTE|freeze_commit=[0-9a-f]*' $O/B7.out | cut -d= -f2 | cut -c1-12)|exit=$(cat $O/B7.rc)|frozen_binary=$(sha256sum $O/B7/target/release/floorcert 2>/dev/null | cut -d' ' -f1)|$(last $O/B7.out)|json=0"
git -C $V/repoD reset -q --hard $NEW

# B8 FZA: the eleven freeze-argument refusal controls on the B0 frozen binary (script as written; its only r = 9 contact)
( cd $FD && bash final/tools/freeze_args_controls.sh $O/B0/target/release/floorcert $FD/work/design/rs/target/release/floorcert $NEW 561e36b40630485c9f27ee981bb1c03280c63296153fca21c3123703308cc96e > $O/FZA.out 2>&1; echo $? > $O/FZA.rc )
row "CASE|id=B8_FZA|exit=$(cat $O/FZA.rc)|$(grep -c '^CONTROL|.*refused_as_expected=1' $O/FZA.out)_of_$(grep -c '^CONTROL|' $O/FZA.out)_refused|$(tail -1 $O/FZA.out | cut -d'|' -f2-9)|json=0"
grep '^CONTROL|' $O/FZA.out >> $O/B.hbp
touch $O/B.done
