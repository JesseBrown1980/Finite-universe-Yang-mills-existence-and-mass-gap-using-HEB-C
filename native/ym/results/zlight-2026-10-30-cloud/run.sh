#!/bin/bash
# SH layer of the zlight cloud-seat chain (HBI -> HBP -> SHA -> SH -> HASH, json=0).
# Rebuilds both source versions in a scratch copy (this directory is not a workspace member,
# so the copy gets its own empty [workspace] table) and checks that each reproduces its recorded
# HBP byte for byte. It never overwrites a record. Writes its own lines to stdout.
set -u
cd "$(dirname "$0")"
here=$(pwd)
sha256sum -c PREREG.md.sha256 || { echo "ZLIGHT_ABORT|reason=prereg_seal_fails|json=0"; exit 2; }
W=$(mktemp -d)
rc=0
fresh() { rm -rf "$W/src"; mkdir -p "$W/src"; cp "$here/Cargo.toml" "$here/Cargo.lock" "$W/"; printf '\n[workspace]\n' >> "$W/Cargo.toml"; cp "$1" "$W/src/main.rs"; }
for v in final run1; do
  if [ $v = final ]; then src=src/main.rs; rec=RESULT.hbp; else src=run1/main.rs; rec=RESULT.run1.hbp; fi
  fresh "$here/$src"
  if ! (cd "$W" && cargo +1.81.0 build -q --release); then
    echo "ZLIGHT_REPRO|version=$v|result=INCONCLUSIVE|reason=build_failed|json=0"; rc=3; continue
  fi
  same=0; "$W/target/release/zlight" | cmp -s - "$rec" && same=1
  [ $same = 1 ] || rc=1
  echo "ZLIGHT_REPRO|version=$v|src_sha256=$(sha256sum "$src" | cut -c1-64)|record=$rec|byte_identical=$same|json=0"
done
fresh "$here/src/main.rs"
if (cd "$W" && cargo +1.81.0 clippy -q --release -- -D warnings); then echo "ZLIGHT_CLIPPY|version=final|D_warnings=exit0|json=0"
else echo "ZLIGHT_CLIPPY|version=final|D_warnings=FAIL|json=0"; rc=4; fi
echo "ZLIGHT_TOOLCHAIN|rustc=$(rustc +1.81.0 --version | tr ' ' '_')|json=0"
rm -rf "$W"
echo "ZLIGHT_REPRO_EXIT|code=$rc|json=0"
exit $rc
