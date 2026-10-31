#!/bin/bash
# Rebuild attempt 2 of commit 2e4846e at the IDENTICAL absolute path (operator-approved Option A, 2026-10-30).
# Pre-registered in PREREG.hbp / PREREG.hbi / SHA256SUMS before any compilation.
# Never deletes anything. Every failure path writes a named row and leaves directories intact.
set -u
O=/d/ym-3x4-room-run/rebuild2-2e4846e; L=$O/REBUILD2.hbp
R=/c/Users/acer/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C
H=$R.hold; A=$R.rebuild2clone
COMMIT=2e4846e7440000b2b0ee6b0fabbea65afbfbe17c
declare -A ORIG=([shellschur]=29b6b55078796ad223b31373f063196a7b3a24a5f2396496b129b96c36542dd3 [roomschur]=a8007c1545a2d8827964fad71a761c1a38744671173bf393f0517e1297434eff [ymroom]=a0bc359d88aca652e5b4ec9e192741d8a1c8c501658e7fd0e33055b410c12cc8 [ymsec]=9fa8232d917892df9c0b071903f258849d40dcd477f984a438fab6a561168607)
declare -A SRC=([crates/torusl/src/segio.rs]=e9253ea2697cf6d5ff98af65ab0d7c0791c57f5492a336099680b806ea331cb5 [crates/torusl/src/bin/ymroom.rs]=2a8409b1f3e110299688900f59bbb3dcc74687b23dc02b3b42f6179568dbcf9e [crates/sturmrs/src/bin/roomschur.rs]=f213b009921ade113325dcbca33b686c6b3f7162b108236eddddffee8447cfec [crates/sturmrs/src/bin/shellschur.rs]=9bd8d245046850b254dd1481fc21722b406b74f74a7051607e523272c05c3783)
row() { echo "$1|t=$(date -Iseconds)|json=0" >> $L; }
state() { # $1 = BEFORE|AFTER ; snapshot of the operator's checkout at path $R
  local p=$1
  for b in shellschur roomschur ymroom ymsec; do echo "${p}_EXE|bin=$b|sha256=$(sha256sum $R/native/ym/target/release/$b.exe | cut -c1-64)|json=0" >> $L; done
  echo "${p}_REPO|head=$(git -C $R rev-parse HEAD)|branch=$(git -C $R branch --show-current)|status_sha256=$(git -C $R status --porcelain=v1 | sha256sum | cut -c1-64)|main_rs_sha256=$(sha256sum $R/native/ym/backend/src/main.rs | cut -c1-64)|runlog_sha256=$(sha256sum $R/native/ym/results/3x4_room_backed/HEBC-YM-3X4-ROOM-RUN.hbp | cut -c1-64)|tracked_raw_sha256=$(cut -f2 $O/tree.tsv | (cd $R && git hash-object --no-filters --stdin-paths) | sha256sum | cut -c1-64)|json=0" >> $L
}
cd $O || exit 9
sleep 30   # let the launching shell exit so no process holds the checkout as its cwd
row "REBUILD2_START|commit=$COMMIT|path=$R|prereg_seal=$(cat $O/PREREG.seal)"
# --- step 0: preconditions
[ -e "$H" ] && { row "REBUILD2_ABORT|reason=hold_path_exists|verdict=INCONCLUSIVE"; exit 3; }
[ -e "$A" ] && { row "REBUILD2_ABORT|reason=aside_path_exists|verdict=INCONCLUSIVE"; exit 3; }
[ "$(git -C $R worktree list | wc -l)" = 1 ] || { row "REBUILD2_ABORT|reason=linked_worktree_present|verdict=INCONCLUSIVE"; exit 3; }
tasklist.exe | grep -qiE 'shellschur|roomschur|ymroom|ymsec|cargo|rustc' && { row "REBUILD2_ABORT|reason=chain_or_build_process_running|verdict=INCONCLUSIVE"; exit 3; }
state BEFORE
for b in shellschur roomschur ymroom ymsec; do grep -q "^BEFORE_EXE|bin=$b|sha256=${ORIG[$b]}|" $L || { row "REBUILD2_ABORT|reason=original_exe_not_recorded_hash|bin=$b|verdict=INCONCLUSIVE"; exit 3; }; done
# --- step 1: rename the operator's checkout to .hold
mv "$R" "$H" 2>>$O/mv.err || { row "REBUILD2_ABORT|reason=rename_to_hold_failed(nothing_moved)|verdict=INCONCLUSIVE"; exit 4; }
[ -d "$H/.git" ] && [ ! -e "$R" ] || { row "REBUILD2_ABORT|reason=post_rename_state_unexpected(left_as_is)|verdict=INCONCLUSIVE"; exit 4; }
row "RENAMED|from=$R|to=$H"
restore() { # move clone aside, put the operator's checkout back; retry, never delete
  local i
  if [ -e "$R" ]; then
    for i in $(seq 1 20); do mv "$R" "$A" 2>>$O/mv.err && break; sleep 30; done
    [ -e "$R" ] && { row "RESTORE_FAILED|reason=clone_could_not_be_moved_aside|hold_left_intact=$H|verdict=INCONCLUSIVE"; return 1; }
    row "CLONE_ASIDE|path=$A"
  fi
  for i in $(seq 1 20); do mv "$H" "$R" 2>>$O/mv.err && break; sleep 30; done
  [ -d "$R/.git" ] && [ ! -e "$H" ] || { row "RESTORE_FAILED|reason=hold_could_not_be_renamed_back|hold_left_intact=$H|verdict=INCONCLUSIVE"; return 1; }
  row "RESTORED|path=$R"; return 0
}
# --- step 2: fresh clone at the identical path, LF exact
git clone -q --no-local --no-hardlinks -c core.autocrlf=false "$H" "$R" 2>>$O/clone.err && git -C "$R" -c advice.detachedHead=false checkout -q $COMMIT 2>>$O/clone.err
ok=1
[ "$(git -C $R rev-parse HEAD 2>/dev/null)" = $COMMIT ] || ok=0
[ "$(git -C $R config core.autocrlf)" = false ] || ok=0
for f in "${!SRC[@]}"; do h=$(sha256sum $R/native/ym/$f | cut -c1-64); e=0; [ "$h" = "${SRC[$f]}" ] && e=1 || ok=0; echo "CLONE_SOURCE|file=$f|sha256=$h|expected=${SRC[$f]}|equal=$e|json=0" >> $L; done
nd=$(cut -f2 $O/tree.tsv | (cd $R && git hash-object --no-filters --stdin-paths) | paste $O/tree.tsv - | awk -F'\t' '$1!=$3' | wc -l); [ "$nd" = 0 ] || ok=0
echo "CLONE_CHECK|head=$(git -C $R rev-parse HEAD 2>/dev/null)|autocrlf=$(git -C $R config core.autocrlf)|tracked_native_ym_files=$(wc -l < $O/tree.tsv)|raw_differs_from_blob=$nd|vendor_multiplication_CR=$(tr -cd '\r' < $R/native/ym/vendor/num-bigint/src/biguint/multiplication.rs | wc -c)|ok=$ok|json=0" >> $L
if [ $ok = 1 ]; then
  # --- step 3: build (identical commands to the originals)
  echo "TOOLCHAIN|cargo=$(cargo +1.81 --version | tr ' ' '_')|rustc=$(rustc +1.81 --version | tr ' ' '_')|host=$(rustc +1.81 -vV | sed -n 's/^host: //p')|llvm=$(rustc +1.81 -vV | sed -n 's/^LLVM version: //p')|env_RUST_CARGO=$(env | grep -E '^(RUST|CARGO)' | tr '\n' ';')|json=0" >> $L
  C1="cargo +1.81 build --release --offline --locked -p sturmrs --bin roomschur --bin shellschur"
  C2="cargo +1.81 build --release --offline --locked -p torusl --bin ymroom --bin ymsec"
  s=$(date +%s); (cd $R/native/ym && $C1) > $O/build1.log 2>&1; e1=$?; (cd $R/native/ym && $C2) > $O/build2.log 2>&1; e2=$?
  echo "BUILD|cmd1=$C1|exit1=$e1|cmd2=$C2|exit2=$e2|wall_s=$(( $(date +%s)-s ))|cwd=$R/native/ym|json=0" >> $L
  # --- step 4: secure rebuilt binaries outside both checkouts
  mkdir -p $O/rebuilt
  for b in shellschur roomschur ymroom ymsec; do cp $R/native/ym/target/release/$b.exe $O/rebuilt/ 2>/dev/null; echo "REBUILT|bin=$b|sha256=$(sha256sum $O/rebuilt/$b.exe 2>/dev/null | cut -c1-64)|json=0" >> $L; done
else
  row "CLONE_NOT_VERIFIED|build=skipped|verdict=INCONCLUSIVE"
fi
# --- step 5: restore the operator's checkout (clone moved aside, never deleted)
cd $O
restore || exit 5
state AFTER
same=1; for k in EXE REPO; do diff <(grep "^BEFORE_$k|" $L | sed "s/^BEFORE_//") <(grep "^AFTER_$k|" $L | sed "s/^AFTER_//") > /dev/null || same=0; done
row "RESTORE_CHECK|before_equals_after=$same"
[ $same = 1 ] || { row "REBUILD2_VERDICT|verdict=INCONCLUSIVE|reason=checkout_state_changed"; exit 6; }
[ $ok = 1 ] && [ "${e1:-1}" = 0 ] && [ "${e2:-1}" = 0 ] || { row "REBUILD2_VERDICT|verdict=INCONCLUSIVE|reason=clone_or_build_failed"; exit 7; }
# --- step 6: direct comparison vs the four original executables
W=C:/Users/acer/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/native/ym/target/release
m=0; i=0
for b in shellschur roomschur ymroom ymsec; do
  python -I $O/pecmp.py $b $W/$b.exe D:/ym-3x4-room-run/rebuild2-2e4846e/rebuilt/$b.exe >> $L; r=$?
  [ $r = 1 ] && m=1; [ $r = 2 ] && i=1
done
if [ $m = 1 ]; then v=PROVENANCE_MISMATCH; elif [ $i = 1 ]; then v=INCONCLUSIVE; else v=PROVENANCE_PASS; fi
row "REBUILD2_VERDICT|verdict=$v|exclusions=coff_timestamp,debugdir_timestamps,rsds_guid_age,pdb_path(only)|shellschur_source_note=executed_CRLF_809d6330_vs_rebuilt_LF_9bd8d245_stays_recorded|not_a_mathematical_result=1"
sha256sum $L | sed 's/  / */' > $L.sha256
