#!/bin/bash
# SH layer of the dictionary-tests chain (HBI -> HBP -> SHA -> SH -> HASH, json=0).
# Order: predictions sealed first, then build, clippy, run B and A, run C, seal.
set -u
cd "$(dirname "$0")"
sha256sum -c PREREG.hbp.sha256 || { echo "DICT_ABORT|reason=prereg_seal_fails|json=0"; exit 2; }
cargo +1.81 build --release --offline || exit 3
cargo +1.81 clippy --release --offline -- -D warnings || exit 4
{ echo "DICT_BUILD|rustc=$(rustc +1.81 --version | tr ' ' '_')|clippy_D_warnings=exit0|exe_sha256=$(sha256sum target/release/dicttests.exe | cut -c1-64)|src_sha256=$(sha256sum src/main.rs | cut -c1-64)|c_script_sha256=$(sha256sum c_provenance.sh | cut -c1-64)|tribit_sha256=$(sha256sum C:/asolaria-acer/asolaria-os/kernel/core/src/tribit/mod.rs | cut -c1-64)|prereg_sha256=$(cut -c1-64 PREREG.hbp.sha256)|json=0"
  ./target/release/dicttests.exe; echo "DICT_EXIT_BA|code=$?|json=0"
  bash c_provenance.sh; echo "DICT_EXIT_C|code=$?|json=0"; } | tr -d '\r' > RESULT.hbp
sha256sum RESULT.hbp | sed 's/  / */' > RESULT.hbp.sha256
sha256sum -c RESULT.hbp.sha256
