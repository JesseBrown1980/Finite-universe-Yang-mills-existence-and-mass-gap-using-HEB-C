#!/bin/bash
# second scratch copy of the pinned verifier: the LEAF line also carries the row's structure counts it already computes
# (flat moves, core moves, tail moves, back moves). Pinned file and certificates untouched.
set -u
V=/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/work/design/py/cert_gate.py
W=/root/ymleaf
python3 -I - "$V" "$W/cert_gate_leaf2.py" <<'EOF'
import sys
s = open(sys.argv[1]).read()
a = "        slack = lhs - rhs\n"
assert s.count(a) == 1
s = s.replace(a, a + "        print('LEAF|key=%d|M=%d|v=%d|slack=%d|lhs=%d|rhs=%d|w=%d|nflat=%d|ncore=%d|ndistinct_core=%d|ntail=%d|nback=%d' % (cls2cert[ci], M, vi, slack, lhs, rhs, cls_W[ci], nflat, sum(core.values()), len(core), len(tails), sum(len(tl) - 10 for tl in tails)))\n")
open(sys.argv[2], "w").write(s)
EOF
sha256sum $W/cert_gate_leaf2.py | cut -c1-64
for m in 7 8 9; do for c in $W/T$m/RUN$m/cert_*.txt; do
  b=S_$(basename $c .txt)
  python3 -I -B $W/cert_gate_leaf2.py $c > $W/$b.out 2>&1
  grep '^LEAF|' $W/$b.out > $W/$b.leaf.hbp
  echo "$b leaves=$(grep -c . $W/$b.leaf.hbp) $(tail -1 $W/$b.out | cut -c1-60)"
  cp $W/$b.leaf.hbp /mnt/c/tmp/opus55/ym-residual-rooms/data/
done; done
echo ALLDONE
