#!/bin/bash
# Repeats the 3x4 run of the corrected allpairs from the source pinned at 0fd24d3, then judges it against the original run at 8faadb0.
#
# usage, from the repo root: reproduce_pin_run.sh SECTORS_DIR OUT_DIR
#   SECTORS_DIR holds sector-341.rooms .. sector-374.rooms from https://huggingface.co/datasets/Jessedbrown/ym-3x4-room-store
#   OUT_DIR     takes the output, the standard error and the judged rows
#
# It reads the store and writes nothing to it. It needs Rust 1.81, Python 3, about 4 GiB of memory, and 2,704 s on the machine that ran it first.
# Build hash: on Linux compare the file hash, 389881ac... on hosted Linux. On Windows the linker stamps each build, so compare pe_normal_hash.py.
# Corrected after a second seat found that the first version exited 0 on a failed judgement and hashed no sector: review-opus55 part two, R1, R2, R3, R5.
set -euo pipefail
ROOT=$(pwd)
MANIFEST=native/ym/results/3x4_room_backed/receipts/hf-store/SECTORS-341-374.sha256
PIN=0fd24d31e3abad7c2745a2c3ffa917663418621a
SRC=f4ea7e856728fde8a5fe56b0e9fe85a0770d930ea566c25b490f697760e55754
FIXED=5ab04b184a4395a779ec6b2189352ea54533f7d1c49b32275d0f30d15d83f4ef
A=native/ym/results/3x4_stream/perron/allpairs
S=native/ym/crates/evolvers/src/bin/allpairs.rs
SECTORS=$1
OUT=$2
mkdir -p "$OUT"
# Everything the build reads must match the pin. Receipts added to the branch after the pin do not touch it.
git diff --quiet "$PIN" -- native/ym/crates/evolvers/src/bin/allpairs.rs native/ym/crates/torusl/src/roomio.rs native/ym/crates/torusl/src/segio.rs native/ym/crates/torusl/src/sha.rs native/ym/backend/Cargo.toml native/ym/Cargo.toml native/ym/Cargo.lock native/ym/.cargo native/ym/vendor native/ym/rust-toolchain.toml native/Cargo.toml || echo "this tree holds later sources. To build the pinned executable: git checkout --detach $PIN"
[ "$(git show "$PIN:$S" | sha256sum | cut -d' ' -f1)" = "$FIXED" ] || { echo "the source at $PIN differs"; exit 2; }
[ "$(sha256sum "$A/ALLPAIRS-3x4.out" | cut -d' ' -f1)" = "b0b172204fb1cbadeacec6dc58576f6436179225d5f0ea03163ba16227c3f271" ] || { echo "the original output differs"; exit 2; }
[ "$(sha256sum "$MANIFEST" | cut -d' ' -f1)" = "9213927b3b60cfbeae8efef10730e8c7df2ad52f56159017b048539377886ce3" ] || { echo "the manifest differs"; exit 2; }
( cd "$SECTORS" && sha256sum -c "$ROOT/$MANIFEST" ) | tee "$OUT/sectors-check.txt"
echo "$SRC  -" > "$OUT/original-source.expect"
git show 8faadb07748417e713e95723f01d83e0ad80b93f:"$S" | sha256sum -c "$OUT/original-source.expect"
( cd native/ym && cargo +1.81.0 build --locked --release -p evolvers --bin allpairs )
X=native/ym/target/release/allpairs
[ -e "$X" ] || X=$X.exe
{ sha256sum "$X"; rustc +1.81.0 -V; } | tee "$OUT/build.txt"
c=0
"$X" "seg:341:34:800000000:$SECTORS/sector-" 0 470000000 > "$OUT/allpairs-3x4.out" 2> "$OUT/allpairs-3x4.err" || c=$?
python3 -I -X utf8 "$A/failclosed/compare_pin_run.py" "$A/ALLPAIRS-3x4.out" "$OUT/allpairs-3x4.out" "$c" "$OUT/allpairs-3x4.err" | tee "$OUT/PIN-COMPARE.hbp"
