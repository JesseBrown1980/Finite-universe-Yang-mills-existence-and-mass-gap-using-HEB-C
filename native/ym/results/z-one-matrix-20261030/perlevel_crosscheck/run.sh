#!/bin/sh
set -eu
cd "$(dirname "$0")"
sha256sum -c SHA256SUMS
sha256sum -c PREREG.hbp.sha256
actual=$(cat SHA256SUMS PERLEVEL.hbi | sha256sum | cut -c1-64)
expected=$(cat PERLEVEL.seal)
test "$actual" = "$expected"
tmp=$(mktemp -d)
cp probe.py PREREG.hbp PREREG.hbp.sha256 "$tmp/"
python3 "$tmp/probe.py" >/dev/null
cmp -s "$tmp/RESULT.hbp" RESULT.hbp
python3 pair_check.py > "$tmp/PAIR-CHECK.hbp"
cmp -s "$tmp/PAIR-CHECK.hbp" PAIR-CHECK.hbp
rm "$tmp/probe.py" "$tmp/PREREG.hbp" "$tmp/PREREG.hbp.sha256" "$tmp/RESULT.hbp" "$tmp/PAIR-CHECK.hbp"
rmdir "$tmp"
echo 'RJ_VERIFY|prereg=PASS|replay=PASS|pair_posthoc=PASS|manifest=PASS|seal=PASS|json=0'
