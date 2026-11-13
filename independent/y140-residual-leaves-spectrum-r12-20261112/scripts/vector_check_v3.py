#!/usr/bin/env python3
"""vector_check_v3.py -- GPT-6's check on the pump result: are the three certificate VECTORS the same vector?
Exact integers. For each pair of certificates at one cutoff: scale both vectors to the same sum and report the
per-row ratio spread in parts per million, overall and by magnetic number.
  python vector_check_v3.py <m0> <leaf_f1> <leaf_f8-7-6-5-4> <leaf_f6-5-4-3>
"""
import sys

NAMES = ("f1", "f87654", "f6543")


def load(path):
    d = {}
    for line in open(path):
        if line.startswith("LEAF|"):
            f = dict(w.split("=", 1) for w in line.strip().split("|")[1:] if "=" in w)
            d[int(f["key"])] = (int(f["M"]), int(f["v"]))
    return d


V = [load(p) for p in sys.argv[2:5]]
keys = sorted(V[0])
for a in range(3):
    for b in range(a + 1, 3):
        sa = sum(V[a][k][1] for k in keys)
        sb = sum(V[b][k][1] for k in keys)
        dev = {}
        for k in keys:
            m, va = V[a][k]
            vb = V[b][k][1]
            # ratio (va/sa)/(vb/sb) in ppm deviation from 1
            r = (va * sb * 10**6) // (vb * sa) - 10**6
            dev.setdefault(m, []).append(r)
        allr = [x for v in dev.values() for x in v]
        print("VECTOR|m0=%s|pair=%s~%s|rows=%d|ratio_deviation_ppm_min=%d|max=%d|rows_within_1000_ppm=%d|by_M=%s|json=0"
              % (sys.argv[1], NAMES[a], NAMES[b], len(allr), min(allr), max(allr), sum(1 for x in allr if abs(x) <= 1000),
                 "_".join("M%d:%d..%d" % (m, min(v), max(v)) for m, v in sorted(dev.items()))))
