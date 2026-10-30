#!/bin/bash
# SH layer of the zteleport cloud-seat chain (HBI -> HBP -> SHA -> SH -> HASH, json=0). Checks the
# prediction seal, builds with Rust 1.81 (std only), runs clippy -D warnings, and checks that the run
# reproduces RESULT.hbp byte for byte. Never overwrites a record.
set -u
cd "$(dirname "$0")"
sha256sum -c --quiet PREREG.md.sha256 || { echo "REPLAY|test=zteleport|result=INCONCLUSIVE|reason=prereg_seal_fails|json=0"; exit 2; }
export CARGO_TARGET_DIR=$(mktemp -d)
cargo +1.81.0 build -q --release --locked --manifest-path zteleport/Cargo.toml || { echo "REPLAY|test=zteleport|result=INCONCLUSIVE|reason=build_failed|json=0"; exit 3; }
cargo +1.81.0 clippy -q --release --locked --manifest-path zteleport/Cargo.toml -- -D warnings || { echo "REPLAY|test=zteleport|result=FAIL|reason=clippy|json=0"; exit 4; }
same=0; "$CARGO_TARGET_DIR/release/zteleport" | cmp -s - RESULT.hbp && same=1
echo "REPLAY|test=zteleport|rustc=$(rustc +1.81.0 --version | tr ' ' '_')|src_sha256=$(sha256sum zteleport/src/main.rs | cut -c1-64)|byte_identical=$same|json=0"
rm -rf "$CARGO_TARGET_DIR"
[ $same = 1 ]
