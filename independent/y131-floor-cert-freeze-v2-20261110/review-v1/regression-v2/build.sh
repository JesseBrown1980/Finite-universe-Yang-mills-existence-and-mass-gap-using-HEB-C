export PATH=$HOME/.cargo/bin:$PATH
cd /root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/work/design/rs
env -u FLOORCERT_FREEZE_COMMIT -u FLOORCERT_PREDICTION_SHA256 cargo +1.81 clippy --release --locked -- -D warnings > /root/floor-v2/clippy_v2.txt 2>&1; echo "clippy_exit=$?"
grep -E "^(error|warning)" -A7 /root/floor-v2/clippy_v2.txt | head -90
env -u FLOORCERT_FREEZE_COMMIT -u FLOORCERT_PREDICTION_SHA256 cargo +1.81 build --release --locked -j1 > /root/floor-v2/build_v2.txt 2>&1; echo "build_exit=$?"
echo "warnings=$(grep -c warning /root/floor-v2/build_v2.txt)"; tail -3 /root/floor-v2/build_v2.txt
sha256sum src/main.rs target/release/floorcert Cargo.toml Cargo.lock
echo "float/unsafe scan:"; grep -nE "\bf32\b|\bf64\b|unsafe|as f[0-9]" src/main.rs | head
tr -cd '\r' < src/main.rs | wc -c
