#!/bin/bash
# Clean-rebuild provenance check of commit 2e4846e (operator direction 2026-10-29).
# Runs ONLY after the 3x3 chain and any auto-triggered 3x4 pilot have finished:
# waits for the final PILOT| row of RUNALL.hbp and for no shellschur/roomschur/ymroom process.
# Never touches native/ym/target of the working repo (the four hashed chain executables).
set -u
O=/d/ym-3x4-room-run/rebuild-2e4846e; L=$O/REBUILD.hbp
RUNALL=/d/ym-3x4-room-run/gate3x3-seg/RUNALL.hbp
SRC=/c/Users/acer/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C
# same path length as SRC (C->X in the last letter) so embedded PDB paths keep the same length
W=/c/Users/acer/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-X
B=$SRC/native/ym/target/release
COMMIT=2e4846e7440000b2b0ee6b0fabbea65afbfbe17c
declare -A REC=([shellschur]=29b6b55078796ad223b31373f063196a7b3a24a5f2396496b129b96c36542dd3 [roomschur]=a8007c1545a2d8827964fad71a761c1a38744671173bf393f0517e1297434eff [ymroom]=a0bc359d88aca652e5b4ec9e192741d8a1c8c501658e7fd0e33055b410c12cc8 [ymsec]=9fa8232d917892df9c0b071903f258849d40dcd477f984a438fab6a561168607)

until grep -q '^PILOT|' "$RUNALL" && ! tasklist.exe | grep -qiE 'shellschur|roomschur|ymroom'; do sleep 60; done
echo "REBUILD_START|t=$(date -Iseconds)|waited_for=RUNALL_PILOT_row+no_chain_process|pilot_row=$(grep '^PILOT|' $RUNALL | tail -1 | tr '|' ';')|json=0" >> $L

# chain executables must be untouched before and after
for b in shellschur roomschur ymroom ymsec; do echo "CHAIN_EXE_BEFORE|bin=$b|sha256=$(sha256sum $B/$b.exe | cut -c1-64)|recorded=${REC[$b]}|json=0" >> $L; done

[ -e "$W" ] && { echo "REBUILD_ABORT|reason=checkout_path_exists|path=$W|json=0" >> $L; exit 3; }
git clone -q --no-local --no-hardlinks "$SRC" "$W" && git -C "$W" -c advice.detachedHead=false checkout -q $COMMIT
echo "CHECKOUT|path=$W|head=$(git -C $W rev-parse HEAD)|status_lines=$(git -C $W status --porcelain | wc -l)|clone=--no-local_--no-hardlinks|json=0" >> $L
echo "TOOLCHAIN|cargo=$(cargo +1.81 --version | tr ' ' '_')|rustc=$(rustc +1.81 --version | tr ' ' '_')|host=$(rustc +1.81 -vV | sed -n 's/^host: //p')|profile=release|features=default|deps=vendored_offline_locked|cargo_config_sha256=$(sha256sum $W/native/ym/.cargo/config.toml | cut -c1-64)|cargo_lock_sha256=$(sha256sum $W/native/ym/Cargo.lock | cut -c1-64)|env_RUST_CARGO=$(env | grep -E '^(RUST|CARGO)' | tr '\n' ';')|json=0" >> $L

cd "$W/native/ym" || exit 4
C1="cargo +1.81 build --release --offline --locked -p sturmrs --bin roomschur --bin shellschur"
C2="cargo +1.81 build --release --offline --locked -p torusl --bin ymroom --bin ymsec"
s=$(date +%s); $C1 > $O/build1.log 2>&1; e1=$?; $C2 > $O/build2.log 2>&1; e2=$?
echo "BUILD|cmd1=$C1|exit1=$e1|cmd2=$C2|exit2=$e2|wall_s=$(( $(date +%s)-s ))|cwd=$W/native/ym|json=0" >> $L

all=1
for b in shellschur roomschur ymroom ymsec; do
  h=$(sha256sum target/release/$b.exe 2>/dev/null | cut -c1-64); eq=0; [ "$h" = "${REC[$b]}" ] && eq=1 || all=0
  echo "REBUILT|bin=$b|sha256=$h|recorded=${REC[$b]}|byte_equal=$eq|json=0" >> $L
done
for b in shellschur roomschur ymroom ymsec; do echo "CHAIN_EXE_AFTER|bin=$b|sha256=$(sha256sum $B/$b.exe | cut -c1-64)|json=0" >> $L; done
R=$W/native/ym/results/3x4_room_backed/receipts/gate3x3-seg
echo "SCRIPTS|compare_py_committed=$(sha256sum $R/compare.py | cut -c1-64)|compare_py_runall_recorded=57b4c811ad501340032b08997c1da9e7d05cca80423f3e87adcd143391f6506a|compare_py_executed=$(sha256sum /d/ym-3x4-room-run/gate3x3-seg/compare.py | cut -c1-64)|run_all_committed=$(sha256sum $R/run-all.sh | cut -c1-64)|run_all_executed=$(sha256sum /d/ym-3x4-room-run/gate3x3-seg/run-all.sh | cut -c1-64)|json=0" >> $L
if [ $all = 1 ]; then v=scoped_binary_provenance_PASS; else v="provenance_INCONCLUSIVE_investigate(not_a_mathematical_MISMATCH)"; fi
echo "REBUILD_VERDICT|all_four_byte_equal=$all|verdict=$v|t=$(date -Iseconds)|json=0" >> $L
cat $L
