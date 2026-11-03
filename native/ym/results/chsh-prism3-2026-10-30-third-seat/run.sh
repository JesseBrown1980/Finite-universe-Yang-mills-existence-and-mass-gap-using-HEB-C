#!/bin/sh
set -eu
cd "$(dirname "$0")"
sha256sum -c SHA256SUMS
out=$(mktemp)
trap 'rm -f "$out"' EXIT HUP INT TERM
python3 -B test_chsh.py > "$out"
cmp -s RESULT.hbp "$out"
echo 'CHSH_REPLAY|prereg=PASS|source_hash=PASS|result_hash=PASS|byte_identical=1|json=0'
