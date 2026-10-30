#!/bin/bash
# SH layer of the zgap2 cloud-seat chain (HBI -> HBP -> SHA -> SH -> HASH, json=0). Checks the
# prediction and addendum seals, builds with Rust 1.81 (std only), runs clippy -D warnings, and checks
# that the run reproduces RESULT.hbp byte for byte. Never overwrites a record.
set -u
cd "$(dirname "$0")"
sha256sum -c --quiet PREREG.md.sha256 ADDENDUM.md.sha256 || { echo "REPLAY|test=zgap2|result=INCONCLUSIVE|reason=seal|json=0"; exit 2; }
export CARGO_TARGET_DIR=$(mktemp -d)
cargo +1.81.0 build -q --release --locked --manifest-path zgap2/Cargo.toml || { echo "REPLAY|test=zgap2|result=INCONCLUSIVE|reason=build_failed|json=0"; exit 3; }
cargo +1.81.0 clippy -q --release --locked --manifest-path zgap2/Cargo.toml -- -D warnings || { echo "REPLAY|test=zgap2|result=FAIL|reason=clippy|json=0"; exit 4; }
same=0; "$CARGO_TARGET_DIR/release/zgap2" | cmp -s - RESULT.hbp && same=1
echo "REPLAY|test=zgap2|rustc=$(rustc +1.81.0 --version | tr ' ' '_')|src_sha256=$(cat zgap2/src/*.rs | sha256sum | cut -c1-64)|byte_identical=$same|json=0"
rm -rf "$CARGO_TARGET_DIR"
[ $same = 1 ]
