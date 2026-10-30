#!/bin/bash
# SH layer of the zwilson cloud-seat chain (HBI -> HBP -> SHA -> SH -> HASH, json=0). Checks the
# prediction seal, builds the native/ym workspace (HTTP-0 backend, ymconf, sturmrs, ymwser)
# and the driver with Rust 1.81, runs clippy -D warnings on both, starts `hebc_ym_http0 serve` on a fresh
# ROOT, runs every count as an HTTP-0 job through the driver, and checks that the driver output reproduces
# RESULT.hbp byte for byte. Never overwrites a record.
set -u
cd "$(dirname "$0")"
sha256sum -c --quiet PREREG.md.sha256 || { echo "REPLAY|test=zwilson|result=INCONCLUSIVE|reason=seal|json=0"; exit 2; }
W=$(cd ../.. && pwd)
(cd "$W" && cargo +1.81.0 build -q --release --offline --locked) || { echo "REPLAY|test=zwilson|result=INCONCLUSIVE|reason=workspace_build|json=0"; exit 3; }
(cd "$W" && cargo +1.81.0 clippy -q --release --offline --locked --workspace -- -D warnings) || { echo "REPLAY|test=zwilson|result=FAIL|reason=workspace_clippy|json=0"; exit 4; }
export CARGO_TARGET_DIR=$(mktemp -d)
cargo +1.81.0 build -q --release --locked --manifest-path zwilson/Cargo.toml || { echo "REPLAY|test=zwilson|result=INCONCLUSIVE|reason=build_failed|json=0"; exit 3; }
cargo +1.81.0 clippy -q --release --locked --manifest-path zwilson/Cargo.toml -- -D warnings || { echo "REPLAY|test=zwilson|result=FAIL|reason=clippy|json=0"; exit 4; }
ROOT=$(mktemp -d); PORT=18744; LOG=$(mktemp)
"$W/target/release/hebc_ym_http0" serve "$ROOT" "$PORT" 10000 > "$LOG" 2>&1 &
SRV=$!
for _ in $(seq 1 100); do grep -q 'server=READY' "$LOG" && break; sleep 0.1; done
OUT=$(mktemp)
"$CARGO_TARGET_DIR/release/zwilson" "$PORT" > "$OUT"
kill "$SRV" 2>/dev/null; wait "$SRV" 2>/dev/null
same=0; cmp -s "$OUT" RESULT.hbp && same=1
echo "REPLAY|test=zwilson|rustc=$(rustc +1.81.0 --version | tr ' ' '_')|src_sha256=$(sha256sum zwilson/src/main.rs | cut -c1-64)|backend_sha256=$(sha256sum "$W/backend/src/main.rs" | cut -c1-64)|ymconf_sha256=$(sha256sum "$W/crates/torusl/src/bin/ymconf.rs" | cut -c1-64)|ymwser_sha256=$(sha256sum "$W/crates/sturmrs/src/bin/ymwser.rs" | cut -c1-64)|byte_identical=$same|json=0"
[ $same = 1 ] || diff "$OUT" RESULT.hbp | head -20
rm -rf "$CARGO_TARGET_DIR" "$ROOT" "$OUT" "$LOG"
[ $same = 1 ]
