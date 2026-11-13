#!/bin/bash
# third scratch copy of the pinned verifier: also writes the canonical row text it hashes (the matrix rows) to a file.
set -u
V=/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/work/design/py/cert_gate.py
W=/root/ymleaf
python3 -I - "$V" "$W/cert_gate_rows.py" <<'EOF'
import sys
s = open(sys.argv[1]).read()
a = "    b = s.encode()\n    rh.update(b)\n"
assert s.count(a) == 1
s = s.replace(a, a + "    ROWSOUT.write(s)\n")
b = "rh = hashlib.sha256()\nnbytes = 0\n"
assert s.count(b) == 1
s = s.replace(b, b + "import os as _os\nROWSOUT = open(_os.environ['ROWSOUT'], 'w')\n")
c = "        slack = lhs - rhs\n"
assert s.count(c) == 1
s = s.replace(c, c + "        print('LEAF|key=%d|M=%d|v=%d|slack=%d|lhs=%d|rhs=%d|w=%d' % (cls2cert[ci], M, vi, slack, lhs, rhs, cls_W[ci]))\n")
open(sys.argv[2], "w").write(s)
EOF
m=7
for f in f8-7-6-5-4 f6-5-4-3 f1; do
  c=$W/T$m/RUN$m/cert_m${m}_r12_1_$f.txt; b=R_cert_m${m}_r12_1_$f
  ROWSOUT=$W/$b.rows.txt python3 -I -B $W/cert_gate_rows.py $c > $W/$b.out 2>&1
  grep '^LEAF|' $W/$b.out > $W/$b.leaf.hbp
  head -1 $c > $W/$b.header.txt
  grep -E '^(ROWHASH|VERDICT)' $W/$b.out | cut -c1-150
  echo "$b rows_text_sha256=$(sha256sum $W/$b.rows.txt | cut -d' ' -f1) lines=$(grep -c . $W/$b.rows.txt)"
  cp $W/$b.rows.txt $W/$b.leaf.hbp $W/$b.header.txt /mnt/c/tmp/opus55/ym-residual-rooms/data/
done
