#!/usr/bin/env python3
"""powers_v18.py -- Pascal-pyramid layer of n = 9, 27, 81, 243 leaves (SPEC-POWERS-V18.hbp). Exact integers only."""
import sys, os
from fractions import Fraction as Fr
D = sys.argv[1]
W3 = ["1", "8-7-6-5-4", "6-5-4-3"]
W9 = W3 + ["4-3-2-1", "8-7-6-5", "10-9-8-7", "6-5-4-3-2", "10-9-8-7-6", "12-11-10-9-8"]
allw = sorted({f.split("_f")[1].replace(".leaf.hbp", "") for f in os.listdir(D) if f.endswith(".leaf.hbp")})
assert len(allw) == 27 and all(w in allw for w in W9)
RS = ["21_2", "12_1", "14_1"]
cache = {}
def load(m, r, w):
    k = (m, r, w)
    if k not in cache:
        d = {}
        for line in open("%s/X_cert_m%d_r%s_f%s.leaf.hbp" % (D, m, r, w)):
            if line.startswith("LEAF|"):
                x = dict(q.split("=", 1) for q in line.strip().split("|")[1:] if "=" in q)
                d[int(x["key"])] = Fr(int(x["slack"]), int(x["v"]))
        cache[k] = d
    return cache[k]
def layer(name, sel):
    L = [load(*s) for s in sel]; n = len(L)
    keys = sorted(set.intersection(*[set(x) for x in L])); N = len(keys); comp = [[0, 0, 0] for _ in keys]
    for x in L:
        o = sorted(range(N), key=lambda i: (x[keys[i]], keys[i]))
        for rk, i in enumerate(o):
            comp[i][0 if rk < N // 3 else (1 if rk < N - N // 3 else 2)] += 1
    corner = sum(1 for c in comp if max(c) == n); interior = sum(1 for c in comp if min(c) > 0); edge = N - corner - interior
    deep = sum(1 for c in comp if 10 * min(c) >= n); big = sum(1 for c in comp if 3 * max(c) >= 2 * n)
    print("POWERS|leaves=%d|set=%s|rows=%d|corner=%d|edge=%d|interior=%d|rows_with_every_value_at_least_a_tenth=%d|quarter_of_rows=%d|rows_with_largest_count_at_least_two_thirds=%d|half_of_rows=%d|occupied_compositions=%d_of_%d|distinct_patterns_not_computed=1|statement=%s|also=%s|json=0" % (
        n, name, N, corner, edge, interior, deep, N // 4, big, N // 2, len({tuple(c) for c in comp}), (n + 1) * (n + 2) // 2,
        "HELD" if 4 * deep < N else "FALSIFIED", "HELD" if 2 * big > N else "FALSIFIED"), flush=True)
layer("3_words_x_3_cutoffs_r12", [(m, "12_1", w) for m in (7, 8, 9) for w in W3])
layer("3_words_x_3_cutoffs_x_3_couplings", [(m, r, w) for m in (7, 8, 9) for r in RS for w in W3])
layer("9_words_x_3_cutoffs_x_3_couplings", [(m, r, w) for m in (7, 8, 9) for r in RS for w in W9])
layer("27_words_x_3_cutoffs_x_3_couplings", [(m, r, w) for m in (7, 8, 9) for r in RS for w in allw])
