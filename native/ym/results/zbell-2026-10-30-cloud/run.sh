#!/bin/bash
# SH layer of the zbell cloud-seat chain (HBI -> HBP -> SHA -> SH -> HASH, json=0).
# Checks the prediction and addendum seals, copies the sources to a scratch directory outside the
# repo (the repo's .cargo/config.toml routes crates.io to native/ym/vendor, which has no sha2),
# builds with Rust 1.81 against the locked sha2 =0.10.8, runs clippy -D warnings and checks that
# the run reproduces RESULT.hbp byte for byte. Never overwrites a record.
set -u
cd "$(dirname "$0")"
sha256sum -c --quiet PREREG.md.sha256 ADDENDUM.md.sha256 || { echo "REPLAY|test=zbell|result=INCONCLUSIVE|reason=prereg_seal_fails|json=0"; exit 2; }
W=$(mktemp -d)
cp Cargo.toml Cargo.lock "$W"/ && mkdir -p "$W/src" && cp src/main.rs "$W/src/"
(cd "$W" && cargo +1.81.0 build -q --release --locked) || { echo "REPLAY|test=zbell|result=INCONCLUSIVE|reason=build_failed|json=0"; rm -rf "$W"; exit 3; }
(cd "$W" && cargo +1.81.0 clippy -q --release --locked -- -D warnings) || { echo "REPLAY|test=zbell|result=FAIL|reason=clippy|json=0"; rm -rf "$W"; exit 4; }
same=0; "$W/target/release/zbell" | cmp -s - RESULT.hbp && same=1
echo "REPLAY|test=zbell|rustc=$(rustc +1.81.0 --version | tr ' ' '_')|src_sha256=$(sha256sum src/main.rs | cut -c1-64)|byte_identical=$same|json=0"
rm -rf "$W"
[ $same = 1 ]
