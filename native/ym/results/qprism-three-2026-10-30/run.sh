#!/bin/sh
set -eu
cd "$(dirname "$0")"
sha256sum -c SHA256SUMS
actual=$(cat SHA256SUMS Q3.hbi | sha256sum | cut -c1-64)
test "$actual" = "$(cat Q3.seal)"
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT HUP INT TERM
cp PREREG.hbp q3_test.py "$T/"
(cd "$T" && python3 q3_test.py)
(cd "$T" && printf '%s  %s\n' 5875929926f4fdfdb1b8577839e675a87aed51cf157bb82851dbe816ffd7dc5c RESULT.hbp | sha256sum -c)
echo 'Q3_REPLAY|prisms=3|cases=54|source_hash=PASS|result_hash=PASS|seal=PASS|json=0'
