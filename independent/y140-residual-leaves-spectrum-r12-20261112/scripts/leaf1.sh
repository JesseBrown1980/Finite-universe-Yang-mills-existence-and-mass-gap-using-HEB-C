#!/bin/bash
# Residual-leaf extraction, read-only on the certificates: a scratch copy of the pinned verifier with ONE added print per
# row (the slack the verifier already computes). The pinned file and the certificates are not touched.
set -eu
V=/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/work/design/py/cert_gate.py
W=/root/ymleaf; mkdir -p $W
python3 -I - "$V" "$W/cert_gate_leaf.py" <<'EOF'
import sys
s = open(sys.argv[1]).read()
a = "        slack = lhs - rhs\n"
assert s.count(a) == 1
s = s.replace(a, a + "        print('LEAF|key=%d|M=%d|v=%d|slack=%d|lhs=%d|rhs=%d|w=%d|den_bad=%d' % (cls2cert[ci], M, vi, slack, lhs, rhs, cls_W[ci], 1 if row_den_bad else 0))\n")
open(sys.argv[2], "w").write(s)
EOF
sha256sum $V $W/cert_gate_leaf.py | cut -c1-90
for c in /root/floor-v6/rehf/K/RUN7/cert_m7_r12_1_f1.txt /root/floor-v6/rehf/K/RUN7/cert_m7_r12_1_f4-3-2-1.txt; do
  b=$(basename $c .txt)
  python3 -I -B $W/cert_gate_leaf.py $c > $W/$b.out 2>&1 || echo "rc=$?"
  grep '^LEAF|' $W/$b.out > $W/$b.leaf.hbp
  sha256sum $c | cut -c1-64 > $W/$b.cert.sha256
  echo "$b leaves=$(grep -c . $W/$b.leaf.hbp) $(tail -1 $W/$b.out | cut -c1-160)"
  python3 -I - $W/$b.leaf.hbp <<'EOF'
import sys
L = [dict(x.split("=") for x in l.strip().split("|")[1:]) for l in open(sys.argv[1])]
sl = [int(r["slack"]) for r in L]
print(" min_slack", min(sl), "max_slack", max(sl), "negatives", sum(1 for x in sl if x < 0), "zeros", sum(1 for x in sl if x == 0))
# relative slack = slack / lhs in parts per million (integer)
rel = sorted((int(r["slack"]) * 10**6 // max(int(r["lhs"]), 1), int(r["M"]), int(r["key"])) for r in L)
print(" smallest relative slack ppm (ppm, M, key):", rel[:5])
byM = {}
for r in L:
    byM.setdefault(int(r["M"]), []).append(int(r["slack"]) * 10**6 // max(int(r["lhs"]), 1))
print(" per M: count, min ppm, median ppm:", {m: (len(v), min(v), sorted(v)[len(v)//2]) for m, v in sorted(byM.items())})
EOF
done
