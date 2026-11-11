export PATH="$HOME/.cargo/bin:$PATH"
D=/root/floor-v2-final/head/independent/y131-floor-cert-freeze-v2-20261110
cd $D/work/design/rs
rustc +1.81 --version; cargo +1.81 --version
env -u FLOORCERT_FREEZE_COMMIT -u FLOORCERT_PREDICTION_SHA256 cargo +1.81 clippy --release --locked -- -D warnings > /root/floor-v2-final/clippy.txt 2>&1; echo "CLIPPY_EXIT=$?"
env -u FLOORCERT_FREEZE_COMMIT -u FLOORCERT_PREDICTION_SHA256 cargo +1.81 build --release --locked -j1 > /root/floor-v2-final/build.txt 2>&1; echo "BUILD_EXIT=$?"
sha256sum target/release/floorcert src/main.rs
grep -E '^PIN\|id=(013|016)\|' $D/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp | sed 's/|value=\([0-9a-f]*\)|.*/ VALUE=\1/' | cut -c1-200
tail -3 /root/floor-v2-final/clippy.txt
which inotifywait; python3 --version; ls -la ~/.cargo/bin | head
