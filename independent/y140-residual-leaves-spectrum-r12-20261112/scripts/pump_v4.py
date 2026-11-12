#!/usr/bin/env python3
"""pump_v4.py -- does the row's structure class carry the three-way agreement? See SPEC-PUMP-V4.hbp.
Exact integers. HBP rows on stdout.
  python pump_v4.py <m0> <leaf_f1> <leaf_f8-7-6-5-4> <leaf_f6-5-4-3>
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
            cls = tuple(int(f[k]) for k in ("M", "nflat", "ncore", "ndistinct_core", "ntail", "nback"))
            d[int(f["key"])] = (cls, int(f["slack"]) * 10**9 // max(int(f["lhs"]), 1))
    return d


def trits(view, keys):
    order = sorted(keys, key=lambda k: (view[k][1], k))
    n = len(order)
    return {k: (-1 if i < n // 3 else (0 if i < n - n // 3 else 1)) for i, k in enumerate(order)}


def shuffle(a, r):
    a = list(a)
    for i in range(len(a) - 1, 0, -1):
        k = r() % (i + 1)
        a[i], a[k] = a[k], a[i]
    return a


m0 = sys.argv[1]
V = [load(p) for p in sys.argv[2:5]]
keys = sorted(V[0])
assert all(V[0][k][0] == V[1][k][0] == V[2][k][0] for k in keys), "structure class differs between certificates"
cols = [[trits(v, keys)[k] for k in keys] for v in V]
cls = [V[0][k][0] for k in keys]
n = len(keys)
groups = {}
for i, c in enumerate(cls):
    groups.setdefault(c, []).append(i)
single = sum(1 for g in groups.values() if len(g) == 1)
multi = [i for g in groups.values() if len(g) > 1 for i in g]
white = [cols[0][i] == cols[1][i] == cols[2][i] for i in range(n)]
print("STRUCT|m0=%s|rows=%d|structure_classes=%d|rows_alone_in_their_class=%d|rows_in_classes_of_two_or_more=%d|largest_class=%d|json=0"
      % (m0, n, len(groups), single, len(multi), max(len(g) for g in groups.values())))
real_all = sum(white)
real_multi = sum(1 for i in multi if white[i])
runs = []
for k in range(27):
    r = mixer(9000 + k)
    c2 = [list(cols[0]), list(cols[1]), list(cols[2])]
    for v in (1, 2):
        for g in groups.values():
            if len(g) > 1:
                vals = [cols[v][q] for q in shuffle(g, r)]
                for dst, val in zip(g, vals):
                    c2[v][dst] = val
    runs.append(sum(1 for i in multi if c2[0][i] == c2[1][i] == c2[2][i]))
lo, hi = min(runs), max(runs)
print("WHITE|all_rows=%d|rows_in_classes_of_two_or_more=%d|of=%d|within_structure_class_null_min=%d|max=%d|mean=%d|real_per_1000_of_null_max=%d|json=0"
      % (real_all, real_multi, len(multi), lo, hi, sum(runs) // len(runs), real_multi * 1000 // max(hi, 1)))
# how pure are the classes: in view 1, the share of rows whose trit equals their class's majority trit
pure = 0
for g in groups.values():
    cnt = {}
    for i in g:
        cnt[cols[1][i]] = cnt.get(cols[1][i], 0) + 1
    pure += max(cnt.values())
print("PURITY|view=f8-7-6-5-4|rows_whose_trit_is_their_class_majority=%d|of=%d|json=0" % (pure, n))
v = "HELD" if real_multi * 100 <= 115 * hi else "FALSIFIED"
print("VERDICT|m0=%s|rule=real_WHITE_at_most_1.15_times_the_null_maximum_on_rows_in_classes_of_two_or_more|result=%s|json=0" % (m0, v))
