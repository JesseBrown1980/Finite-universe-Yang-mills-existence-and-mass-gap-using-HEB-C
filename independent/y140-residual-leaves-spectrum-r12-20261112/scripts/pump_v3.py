#!/usr/bin/env python3
"""pump_v3.py -- the pump test on three certificates of one matrix. See SPEC-PUMP-V3.hbp (sealed before the
certificates were made). Exact integers. HBP rows on stdout.
  python pump_v3.py <m0> <leaf_f1> <leaf_f8-7-6-5-4> <leaf_f6-5-4-3>
"""
import sys


def mixer(seed):
    st = [seed & 0xFFFFFFFFFFFFFFFF]
    def nxt():
        st[0] = (st[0] + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = st[0]
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        return z ^ (z >> 31)
    return nxt


def load(path):
    d = {}
    for line in open(path):
        if line.startswith("LEAF|"):
            f = dict(w.split("=", 1) for w in line.strip().split("|")[1:] if "=" in w)
            d[int(f["key"])] = (int(f["M"]), int(f["slack"]) * 10**9 // max(int(f["lhs"]), 1))
    return d


def trits(view, keys):
    """equal-population terciles of the relative slack: -1, 0, +1 (ties broken by key order)."""
    order = sorted(keys, key=lambda k: (view[k][1], k))
    n = len(order)
    t = {}
    for i, k in enumerate(order):
        t[k] = -1 if i < n // 3 else (0 if i < n - n // 3 else 1)
    return t


def census(cols):
    w = s = j = 0
    for a, b, c in zip(*cols):
        if a == b == c:
            w += 1
        elif a != b and b != c and a != c:
            j += 1
        else:
            s += 1
    return w, s, j


def shuffle(a, r):
    a = list(a)
    for i in range(len(a) - 1, 0, -1):
        k = r() % (i + 1)
        a[i], a[k] = a[k], a[i]
    return a


m0 = sys.argv[1]
V = [load(p) for p in sys.argv[2:5]]
keys = sorted(V[0])
assert all(sorted(v) == keys for v in V), "the three certificates do not carry the same rows"
M = [V[0][k][0] for k in keys]
T = [trits(v, keys) for v in V]
cols = [[t[k] for k in keys] for t in T]
n = len(keys)
print("PUMPHDR|m0=%s|rows=%d|views=f1,f8-7-6-5-4,f6-5-4-3|trit=own_terciles_of_relative_slack|integer_only=1|json=0" % (m0, n))
for (a, b, nm) in ((0, 1, "f1~f87654"), (0, 2, "f1~f6543"), (1, 2, "f87654~f6543")):
    tie = sum(1 for x, y in zip(cols[a], cols[b]) if x == y)
    print("LEVEL2|pair=%s|rows_that_tie=%d|of=%d|independent_expectation=%d|json=0" % (nm, tie, n, n // 3))
w, s, j = census(cols)
print("LEVEL3|WHITE_all_equal=%d|SECONDARY_two_equal=%d|TRIJECTION_all_different=%d|of=%d|independent_expectation=%d_%d_%d|json=0"
      % (w, s, j, n, n // 9, 6 * n // 9, 2 * n // 9))
byM = {}
for i, m in enumerate(M):
    byM.setdefault(m, []).append(i)
res = {"global_shuffle": [], "within_M_shuffle": []}
for k in range(27):
    r = mixer(7000 + k)
    res["global_shuffle"].append(census([cols[0], shuffle(cols[1], r), shuffle(cols[2], r)]))
    r = mixer(8000 + k)
    c2 = [list(cols[0]), list(cols[1]), list(cols[2])]
    for v in (1, 2):
        for m, idx in byM.items():
            p = shuffle(idx, r)
            vals = [cols[v][q] for q in p]
            for dst, val in zip(idx, vals):
                c2[v][dst] = val
    res["within_M_shuffle"].append(census(c2))
for name, runs in res.items():
    for pos, lab, real in ((0, "WHITE", w), (1, "SECONDARY", s), (2, "TRIJECTION", j)):
        xs = [u[pos] for u in runs]
        v = "OUTSIDE_ABOVE" if real > max(xs) else ("OUTSIDE_BELOW" if real < min(xs) else "INSIDE")
        print("CONTROL|null=%s|class=%s|real=%d|null_min=%d|null_max=%d|result=%s|json=0" % (name, lab, real, min(xs), max(xs), v))
print("WHITE_BY_M|" + "|".join("M%d=%d_of_%d" % (m, sum(1 for i in idx if cols[0][i] == cols[1][i] == cols[2][i]), len(idx)) for m, idx in sorted(byM.items())) + "|json=0")
print("SHELL|m0=%s|white_per_million=%d|json=0" % (m0, w * 10**6 // n))
