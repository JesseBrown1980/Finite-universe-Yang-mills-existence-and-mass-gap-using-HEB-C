#!/bin/bash
# SH layer of the per-level chain (HBI -> HBP -> SHA -> SH -> HASH, json=0).
# Order: predictions sealed first (PREREG.hbp.sha256), then build, clippy, run, seal.
set -u
cd "$(dirname "$0")"
sha256sum -c PREREG.hbp.sha256 || { echo "PERLEVEL_ABORT|reason=prereg_seal_fails|json=0"; exit 2; }
cargo +1.81 build --release --offline || exit 3
cargo +1.81 clippy --release --offline -- -D warnings || exit 4
{ echo "PERLEVEL_BUILD|rustc=$(rustc +1.81 --version | tr ' ' '_')|clippy_D_warnings=exit0|exe_sha256=$(sha256sum target/release/perlevel.exe | cut -c1-64)|src_sha256=$(sha256sum src/main.rs | cut -c1-64)|tribit_sha256=$(sha256sum C:/asolaria-acer/asolaria-os/kernel/core/src/tribit/mod.rs | cut -c1-64)|prereg_sha256=$(cut -c1-64 PREREG.hbp.sha256)|json=0"
  ./target/release/perlevel.exe
  echo "PERLEVEL_EXIT|code=$?|json=0"; } | tr -d '\r' > RESULT.hbp
sha256sum RESULT.hbp | sed 's/  / */' > RESULT.hbp.sha256
sha256sum -c RESULT.hbp.sha256
