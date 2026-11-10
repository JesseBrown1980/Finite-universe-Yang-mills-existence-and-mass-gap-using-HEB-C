set -u
export PATH="$HOME/.cargo/bin:$PATH"
A=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110
B=/root/floor-v2-verify/build
rm -rf $B; mkdir -p $B
cp -r $A/work/design/rs $B/rs
cd $B/rs
rustc +1.81 --version; cargo +1.81 --version
env -u FLOORCERT_FREEZE_COMMIT -u FLOORCERT_PREDICTION_SHA256 cargo +1.81 build --release --locked -j1 > $B/build.txt 2>&1; echo "build_rc=$?"
grep -c '^warning' $B/build.txt; tail -3 $B/build.txt
sha256sum target/release/floorcert
env -u FLOORCERT_FREEZE_COMMIT -u FLOORCERT_PREDICTION_SHA256 cargo +1.81 clippy --release --locked -- -D warnings > $B/clippy.txt 2>&1; echo "clippy_rc=$?"; tail -3 $B/clippy.txt
grep -cE '\bf32\b|\bf64\b' src/main.rs; grep -cE '\bunsafe\b' src/main.rs; grep -cE '#!?\[allow' src/main.rs
grep -nE '[0-9]\.[0-9]+(e[0-9]+)?_?f?(32|64)?\b' src/main.rs | grep -v '//' | head
sha256sum src/main.rs Cargo.toml Cargo.lock
cat Cargo.toml
