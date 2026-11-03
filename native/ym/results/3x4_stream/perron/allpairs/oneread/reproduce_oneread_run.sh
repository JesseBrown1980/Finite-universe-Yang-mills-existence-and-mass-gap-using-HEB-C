#!/bin/bash
# Repeats the 3x4 run of allpairs with one read of its header block from its pinned source, on any machine, and judges it. Exits nonzero if any step or requirement fails.
# From hardened/reproduce_hardened_run.sh, with R9, R10 and R11 of the second seat's review closed.
#
# usage, from the repo root: reproduce_hardened_run.sh PIN SECTORS_DIR OUT_DIR
#   PIN          the commit named in oneread/run34/ONEREAD-RUN.hbp, row ONEREAD_3x4_PREDICTION
#   SECTORS_DIR  holds sector-341.rooms .. sector-374.rooms from https://huggingface.co/datasets/Jessedbrown/ym-3x4-room-store
#   OUT_DIR      takes the output, the standard error, the build's hash and the judged rows
#
# It reads the store and writes nothing to it. It needs Rust 1.81.0, Python 3, GNU coreutils and about 4 GiB of memory, and hashes 27.2 GB, then reads 26.85 GB four times.
# Clone with `git clone -c core.autocrlf=false`, which keeps that setting in the clone, so the working copy holds the committed bytes.
# Build hash: on Linux compare the file hash. On Windows the linker stamps each build, so compare pe_normal_hash.py, where a difference means another toolset or source.
set -euo pipefail
PIN=$1
SECTORS=$2
OUT=$3
A=native/ym/results/3x4_stream/perron/allpairs
O=$A/oneread
R=native/ym/crates/torusl/src/roomscan.rs
S=native/ym/crates/evolvers/src/bin/allpairs.rs
MANIFEST=native/ym/results/3x4_room_backed/receipts/hf-store/SECTORS-341-374.sha256
MANIFEST_SHA=9213927b3b60cfbeae8efef10730e8c7df2ad52f56159017b048539377886ce3
SOURCE_SHA=adcacfc5427666a02ca5dcc1a984d56b4e73bf9f95142e3f532d1c023cf2bb25
ROOMSCAN_SHA=b8880f4b3e04f307b21e2da2d2491e95ef8bd3721a9717bc4d4a2ad2daaed795
ORIGINAL_OUT_SHA=b0b172204fb1cbadeacec6dc58576f6436179225d5f0ea03163ba16227c3f271
mkdir -p "$OUT"
OUT_ABS=$(cd "$OUT" && pwd)
ROOT=$(pwd)
# The cheap checks first, so a clone holding other bytes stops here.
[ "$(sha256sum "$A/ALLPAIRS-3x4.out" | cut -d' ' -f1)" = "$ORIGINAL_OUT_SHA" ] || { echo "the original output differs: clone with git clone -c core.autocrlf=false"; exit 2; }
[ "$(sha256sum "$S" | cut -d' ' -f1)" = "$SOURCE_SHA" ] || { echo "allpairs.rs differs from this recipe"; exit 2; }
[ "$(sha256sum "$R" | cut -d' ' -f1)" = "$ROOMSCAN_SHA" ] || { echo "roomscan.rs differs from this recipe"; exit 2; }
[ "$(git show "$PIN:$S" | sha256sum | cut -d' ' -f1)" = "$SOURCE_SHA" ] || { echo "the pin holds another allpairs.rs"; exit 2; }
# Everything Cargo reads for this build must match the pin, with no untracked file among it. Receipts added after the pin do not touch these paths.
BUILD_INPUTS="native/ym/crates native/ym/backend native/ym/Cargo.toml native/ym/Cargo.lock native/ym/.cargo native/ym/vendor native/ym/rust-toolchain.toml native/Cargo.toml native/.cargo .cargo"
git diff --quiet "$PIN" -- $BUILD_INPUTS || { echo "the build inputs differ from $PIN"; exit 2; }
[ -z "$(git status --porcelain --ignored --untracked-files=all -- $BUILD_INPUTS)" ] || { echo "the build inputs hold uncommitted, untracked or ignored files"; exit 2; }
git show "$PIN:$S" | sha256sum | tee "$OUT_ABS/source-at-pin.sha256"
# The original run's source, at its own commit.
[ "$(git show 8faadb07748417e713e95723f01d83e0ad80b93f:"$S" | sha256sum | cut -d' ' -f1)" = "f4ea7e856728fde8a5fe56b0e9fe85a0770d930ea566c25b490f697760e55754" ] || { echo "the original source differs"; exit 2; }
# The store: the public manifest in this repo, then every sector against it.
[ "$(sha256sum "$MANIFEST" | cut -d' ' -f1)" = "$MANIFEST_SHA" ] || { echo "the manifest differs"; exit 2; }
( cd "$SECTORS" && sha256sum -c "$ROOT/$MANIFEST" ) | tee "$OUT_ABS/sectors-check.txt"
( cd native/ym && cargo +1.81.0 build --locked --release -p evolvers --bin allpairs )
X=native/ym/target/release/allpairs
# Git Bash finds allpairs when allpairs.exe exists, and native Python needs the full name.
[ -e "$X.exe" ] && X=$X.exe
{ sha256sum "$X"; rustc +1.81.0 -V; cargo +1.81.0 -V; } | tee "$OUT_ABS/build.txt"
c=0
"$X" "seg:341:34:800000000:$SECTORS/sector-" 0 470000000 > "$OUT_ABS/allpairs-3x4.out" 2> "$OUT_ABS/allpairs-3x4.err" || c=$?
echo "exit=$c" | tee "$OUT_ABS/exit.txt"
python3 -I -X utf8 "$O/compare_oneread_run.py" "$A/ALLPAIRS-3x4.out" "$OUT_ABS/allpairs-3x4.out" "$c" "$OUT_ABS/allpairs-3x4.err" --exe "$X" | tee "$OUT_ABS/ONEREAD-COMPARE.hbp"
echo "REPRODUCE_DONE|exit=0|json=0"
