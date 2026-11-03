#!/bin/sh
set -eu
cd "$(dirname "$0")"
sha256sum -c SHA256SUMS
sha256sum -c PREREG.hbp.sha256 PREREG-v2.hbp.sha256 RESULT-v2.hbp.sha256
python3 - <<'PY'
import hashlib, pathlib
root=pathlib.Path('.')
manifest=(root/'SHA256SUMS').read_bytes()
hbi=(root/'ZDEST.hbi').read_bytes()
assert hashlib.sha256(manifest+hbi).hexdigest()==(root/'ZDEST.seal').read_text().strip()
prev='0'*64
lines=hbi.decode().splitlines()
for i,line in enumerate(lines):
    k={a:b for a,b in (x.split('=',1) for x in line.split('|')[1:])}
    assert line.startswith('EMIT|') and int(k['index'])==i and k['prev']==prev and k['json']=='0'
    path=k['name']; actual=hashlib.sha256((root/path).read_bytes()).hexdigest()
    assert actual==k['sha256']
    prev=hashlib.sha256((prev+'|'+path+'|'+actual).encode()).hexdigest()
    assert k['chain']==prev
print('ZDEST_CHAIN|hbi=PASS|seal=PASS|json=0')
PY
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
python3 test.py > "$TMP/result"
cmp "$TMP/result" RESULT-v2.hbp
if python3 test_v1.py > "$TMP/v1_stdout" 2> "$TMP/v1_stderr"; then
  echo 'ZDEST_ABORT|reason=original_v1_unexpected_pass|json=0'; exit 1
fi
grep -q 'AssertionError: P3 nonselected' "$TMP/v1_stderr"
test ! -s "$TMP/v1_stdout"
grep -q '^1$' RUN1.exit
grep -q 'AssertionError: P3 nonselected' RUN1.stderr
printf 'ZDEST_REPLAY|revision_1=EXPECTED_FAIL|revision_2=BYTE_EQUAL|integrity=PASS|json=0\n'
