#!/bin/bash
cd /tmp/opus55ffv/pkg/work/design/rs
CARGO_TARGET_DIR=/tmp/opus55ffv/tgt1 cargo +1.81 clippy --release --locked -- -D warnings > /tmp/opus55ffv/clippy.log 2>&1
echo "clippy_rc=$?"
CARGO_TARGET_DIR=/tmp/opus55ffv/tgt1 cargo +1.81 build --release --locked -j1 > /tmp/opus55ffv/build3.log 2>&1
echo "build_rc=$?"
grep -c '^warning' /tmp/opus55ffv/build3.log
