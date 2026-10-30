#!/bin/bash
# SH layer of the zlight chain (HBI -> HBP -> SHA -> SH -> HASH, json=0).
# The procedure that produced RESULT.hbp on 2026-10-30, written down as run.
# Order: predictions sealed first (PREREG.hbp.sha256), then build, clippy, run, seal.
set -u
cd "$(dirname "$0")"
sha256sum -c PREREG.hbp.sha256 || { echo "ZLIGHT_ABORT|reason=prereg_seal_fails|json=0"; exit 2; }
cargo +1.81 build --release --offline || exit 3
cargo +1.81 clippy --release --offline -- -D warnings || exit 4
{ echo "ZLIGHT_BUILD|rustc=$(rustc +1.81 --version | tr ' ' '_')|clippy_D_warnings=exit0|exe_sha256=$(sha256sum target/release/zlight.exe | cut -c1-64)|src_sha256=$(sha256sum src/main.rs | cut -c1-64)|prereg_sha256=$(cut -c1-64 PREREG.hbp.sha256)|json=0"
  ./target/release/zlight.exe
  echo "ZLIGHT_EXIT|code=$?|json=0"; } | tr -d '\r' > RESULT.hbp
sha256sum RESULT.hbp | sed 's/  / */' > RESULT.hbp.sha256
sha256sum -c RESULT.hbp.sha256
