#!/bin/bash
# SH layer (HBI -> HBP -> SHA -> SH -> HASH, json=0): checks the seals, builds with Rust 1.81 (std only),
# runs clippy -D warnings and checks byte identity with RESULT.hbp, and that the run-1 lines reproduce.
set -u
cd "$(dirname "$0")"
sha256sum -c --quiet PREREG.md.sha256 ADDENDUM.md.sha256 || { echo "REPLAY|test=zcalib|result=INCONCLUSIVE|reason=seal|json=0"; exit 2; }
export CARGO_TARGET_DIR=$(mktemp -d)
cargo +1.81.0 build -q --release --locked --manifest-path zcalib/Cargo.toml || { echo "REPLAY|test=zcalib|result=INCONCLUSIVE|reason=build|json=0"; exit 3; }
cargo +1.81.0 clippy -q --release --locked --manifest-path zcalib/Cargo.toml -- -D warnings || { echo "REPLAY|test=zcalib|result=FAIL|reason=clippy|json=0"; exit 4; }
same=0; "$CARGO_TARGET_DIR/release/zcalib" GATES.lut | cmp -s - RESULT.hbp && same=1
r1=0; grep -vE '^Z(CUT2|CAL2)' RESULT.hbp | cmp -s - RESULT.run1.hbp && r1=1
echo "REPLAY|test=zcalib|rustc=$(rustc +1.81.0 --version | tr ' ' '_')|byte_identical=$same|run1_identical=$r1|json=0"
rm -rf "$CARGO_TARGET_DIR"
[ $same = 1 ] && [ $r1 = 1 ]
