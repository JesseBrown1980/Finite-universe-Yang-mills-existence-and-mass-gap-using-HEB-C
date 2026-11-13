#!/usr/bin/env python3
"""nine_v15.py -- relationships among NINE frozen leaves. See SPEC-NINE-V15.hbp (sealed before the run).

Nine views of the same rows: the three weight words at each of the cutoffs 7, 8, 9 (coupling 12). The rows are
the 682 classes present at all three cutoffs. Each view turns a row's exact local ratio q = slack/v into a trit by
its own terciles among those rows. Question: is there structure among the nine that NO PAIR explains?
Control: surrogate data sets that keep every single view's counts and every one of the 36 pairwise tables EXACTLY,
found by swapping values inside one view between two rows until all pair tables match (deterministic seeds).
Integers and exact comparisons only.   python nine_v15.py <data_dir> <surrogates>
"""
import random, sys
from fractions import Fraction as Fr
from itertools import combinations

D = sys.argv[1]; NS = int(sys.argv[2])
VIEWS = [(m, f) for m in (7, 8, 9) for f in ("f1", "f8-7-6-5-4", "f6-5-4-3")]


def load(m, f):
    d = {}
    for line in open("%s/T_cert_m%d_r12_1_%s.leaf.hbp" % (D, m, f)):
        if line.startswith("LEAF|"):
            x = dict(w.split("=", 1) for w in line.strip().split("|")[1:] if "=" in w)
            d[int(x["key"])] = Fr(int(x["slack"]), int(x["v"]))
    return d


L = [load(m, f) for m, f in VIEWS]
keys = sorted(set.intersection(*[set(x) for x in L]))
n = len(keys); V = len(VIEWS)
X = []
for x in L:
    order = sorted(range(n), key=lambda i: (x[keys[i]], keys[i]))
    t = [0] * n
    for rnk, i in enumerate(order):
        t[i] = 0 if rnk < n // 3 else (1 if rnk < n - n // 3 else 2)
    X.append(t)
PAIRS = list(combinations(range(V), 2)); TRIPLES = list(combinations(range(V), 3))


def tables(Y):
    return {(a, b): [[sum(1 for i in range(n) if Y[a][i] == s and Y[b][i] == u) for u in range(3)] for s in range(3)] for a, b in PAIRS}


def stats(Y):
    rows = [tuple(Y[v][i] for v in range(V)) for i in range(n)]
    cnt = {}
    for r_ in rows:
        cnt[r_] = cnt.get(r_, 0) + 1
    s9 = sum(1 for r_ in rows if len(set(r_)) == 1)
    t3 = sum(1 for r_ in rows for a, b, c in TRIPLES if r_[a] == r_[b] == r_[c])
    maj = sum(max(r_.count(0), r_.count(1), r_.count(2)) for r_ in rows)
    return s9, t3, len(cnt), max(cnt.values()), maj


T0 = tables(X)
real = stats(X)
print("NINEHDR|views=%s|rows_common_to_all_nine=%d|trit=own_terciles_of_slack/v|pairs=%d|triples=%d|json=0" % ("+".join("m%d:%s" % v for v in VIEWS), n, len(PAIRS), len(TRIPLES)))
print("PAIRWISE|rows_that_tie_per_pair_min=%d|max=%d|chance=%d|json=0" % (min(sum(T0[p][s][s] for s in range(3)) for p in PAIRS), max(sum(T0[p][s][s] for s in range(3)) for p in PAIRS), n // 3))
print("REAL|all_nine_equal=%d|triple_agreements_summed_over_84_triples=%d|distinct_nine_patterns=%d|largest_pattern_multiplicity=%d|majority_size_summed=%d|json=0" % real)


def surrogate(seed, maxit=8000000):
    rnd = random.Random(seed)
    Y = [list(col) for col in X]
    for v in range(V):
        rnd.shuffle(Y[v])                                   # singles kept, everything else destroyed
    cur = tables(Y)
    cost = sum(abs(cur[p][s][u] - T0[p][s][u]) for p in PAIRS for s in range(3) for u in range(3))
    it = 0
    while cost > 0 and it < maxit:
        it += 1
        v = rnd.randrange(V); i = rnd.randrange(n); j = rnd.randrange(n)
        a, b = Y[v][i], Y[v][j]
        if a == b:
            continue
        delta = 0; ch = []
        for w in range(V):
            if w == v:
                continue
            ci, cj = Y[w][i], Y[w][j]
            if ci == cj:
                continue
            p = (v, w) if v < w else (w, v)
            cells = ((a, ci, -1), (b, ci, 1), (b, cj, -1), (a, cj, 1)) if v < w else ((ci, a, -1), (ci, b, 1), (cj, b, -1), (cj, a, 1))
            for s, u, dd in cells:
                old = cur[p][s][u] - T0[p][s][u]
                delta += abs(old + dd) - abs(old)
                ch.append((p, s, u, dd))
        T = 0.6 * (1 - it / maxit) ** 2 + 0.02
        if delta <= 0 or (it < (maxit * 3) // 4 and rnd.random() < 2.718281828 ** (-delta / T)):   # last quarter: downhill and neutral moves only
            # note: a cell may appear twice in ch only across different w, never within one w
            for p, s, u, dd in ch:
                cur[p][s][u] += dd
            Y[v][i], Y[v][j] = b, a
            cost += delta
    return Y, cost, it


out = []
for k in range(NS):
    k = k + (int(sys.argv[3]) if len(sys.argv) > 3 else 0)
    Y, cost, it = surrogate(15000 + k)
    exact = cost == 0 and tables(Y) == T0
    s = stats(Y)
    print("SURROGATE|seed=%d|pair_tables_all_exact=%d|residual_cost=%d|swaps_tried=%d|all_nine_equal=%d|triple_agreements=%d|distinct_patterns=%d|largest_multiplicity=%d|majority_size_summed=%d|json=0" % ((15000 + k, int(exact), cost, it) + s))
    if cost <= 48:
        out.append(s)
names = ("all_nine_equal", "triple_agreements", "distinct_patterns", "largest_multiplicity", "majority_size_summed")
for q in range(5):
    xs = [s[q] for s in out]
    if xs:
        v = "OUTSIDE_ABOVE" if real[q] > max(xs) else ("OUTSIDE_BELOW" if real[q] < min(xs) else "INSIDE")
        print("VERDICT|statistic=%s|real=%d|surrogates_within_48_counts_of_all_36_pair_tables=%d|min=%d|max=%d|result=%s|json=0" % (names[q], real[q], len(xs), min(xs), max(xs), v))
