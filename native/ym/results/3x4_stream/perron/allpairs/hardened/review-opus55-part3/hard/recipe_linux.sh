#!/bin/bash
# Fresh public clone on the Linux lane. The recipe with an empty sectors folder never reads the 3x4 store and stops before the build, so the build and the failing-judge path
# run from a patched copy of the recipe, on the 2x2 store and with the sector check replaced. Rows only, json=0.
R=/mnt/c/tmp/opus55/allpairs-review-20261103/hard
C=$R/clones
export TMPDIR=$R/tmp CARGO_HOME=$R/tmp/cargo-home
export PATH=/root/.cargo/bin:/usr/bin:/bin
U=https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C.git
PIN=9c2c7e67e29e0b2450010bd43c3391638e6670eb
A=native/ym/results/3x4_stream/perron/allpairs
H=$A/hardened/reproduce_hardened_run.sh
E=$R/tmp/empty-sectors
O=$R/out/recipes-linux
mkdir -p "$C" "$E" "$O" "$TMPDIR"
emit() { printf 'RECIPE_LINUX|%s|json=0\n' "$*"; }
tailrow() { tail -1 "$1" | tr -d '\r' | cut -c1-120 | tr '|' '~'; }
cd "$C" || exit 9
git clone --quiet --branch ym-3x4-allpairs-hardened --single-branch "$U" linux
cd linux || exit 9
git -c advice.detachedHead=false checkout --quiet --detach "$PIN"
emit "head=$(git rev-parse HEAD)|manifest_sha256=$(sha256sum native/ym/results/3x4_room_backed/receipts/hf-store/SECTORS-341-374.sha256 | cut -c1-64)|uname=$(uname -s)|rustc=$(rustc +1.81.0 -V | cut -d' ' -f2)"
bash "$H" "$PIN" "$E" "$O/plain" > "$O/plain.log" 2>&1; c=$?
emit "recipe=hardened|sectors=empty|exit=$c|sectors_failed_rows=$(grep -c FAILED "$O/plain/sectors-check.txt" 2>/dev/null)|last=$(tailrow "$O/plain.log")"
# The patched copy: the store is the 2x2 file, the sector check is gone, nothing else changes. The judge must fail, and the recipe must exit nonzero with no REPRODUCE_DONE row.
S2=/mnt/d/ym-3x4-room-run/p0-ball/small/2x2/dev.bin
sed -e "s#^( cd \"\$SECTORS\" && sha256sum -c.*#echo sector_check_replaced#" -e "s#\"seg:341:34:800000000:\$SECTORS/sector-\" 0 470000000#\"$S2\" 0 470000000#" "$H" > "$R/tmp/recipe-small.sh"
grep -c "sector_check_replaced\|$S2" "$R/tmp/recipe-small.sh"
bash "$R/tmp/recipe-small.sh" "$PIN" "$E" "$O/small" > "$O/small.log" 2>&1; c=$?
emit "recipe=patched_on_the_2x2_store|exit=$c|reproduce_done_rows=$(grep -c REPRODUCE_DONE "$O/small.log")|judge_failed=$(grep -a HARDENED_COMPARE_DONE "$O/small/HARDENED-COMPARE.hbp" | sed -e 's/.*failed=\([0-9]*\).*/\1/')|exit_txt=$(tr -d '\n' < "$O/small/exit.txt")|last=$(tailrow "$O/small.log")"
X=native/ym/target/release/allpairs
emit "build=plain|file_sha256=$(sha256sum "$X" | cut -c1-64)|hosted_tools_txt=0f3fbbfda2b46928abd9e80d726b71052788a7f516d4e780b30e7edbedea8cc9|equal=$([ "$(sha256sum "$X" | cut -c1-64)" = 0f3fbbfda2b46928abd9e80d726b71052788a7f516d4e780b30e7edbedea8cc9 ] && echo 1 || echo 0)|build_txt=$(head -1 "$O/small/build.txt" | cut -c1-16)"
# A config one directory above the pathspec, with the same recipe checks.
mkdir -p native/.cargo
printf '[build]\nrustflags = ["-C", "opt-level=1"]\n' > native/.cargo/config.toml
git diff --quiet "$PIN" -- native/ym/crates native/ym/backend native/ym/Cargo.toml native/ym/Cargo.lock native/ym/.cargo native/ym/vendor native/ym/rust-toolchain.toml native/Cargo.toml; d=$?
bash "$R/tmp/recipe-small.sh" "$PIN" "$E" "$O/small-config" > "$O/small-config.log" 2>&1; c=$?
emit "build=with_native_dot_cargo_config|git_diff_exit=$d|recipe_exit=$c|file_sha256=$(sha256sum "$X" | cut -c1-64)|differs_from_plain=$([ "$(sha256sum "$X" | cut -c1-64)" = 0f3fbbfda2b46928abd9e80d726b71052788a7f516d4e780b30e7edbedea8cc9 ] && echo 0 || echo 1)|build_txt_same_row_printed=$(head -1 "$O/small-config/build.txt" | cut -c1-16)"
rm -rf native/.cargo
rm -f "$R/tmp/recipe-small.sh"
emit "done=1"
