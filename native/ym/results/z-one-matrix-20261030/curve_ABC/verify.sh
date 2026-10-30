#!/bin/sh
set -eu
cd "$(dirname "$0")"
sha256sum -c PREREG.hbp.sha256
python3 replay.py
sha256sum -c SHA256SUMS
actual=$(cat SHA256SUMS DICTIONARY.hbi | sha256sum | cut -d ' ' -f 1)
expected=$(cat DICTIONARY.seal)
[ "$actual" = "$expected" ]
printf 'DICTIONARY_PROVENANCE|manifest=PASS|replay=PASS|seal=PASS|json=0\n'
