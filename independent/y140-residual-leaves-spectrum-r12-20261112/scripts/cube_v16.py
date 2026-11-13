#!/usr/bin/env python3
"""cube_v16.py -- EXACT pairwise-preserving control for the nine leaves, by balanced cube moves from the real table.

A cube move picks three of the nine leaf coordinates, a fixed setting of the other six, and two trit values on
each chosen coordinate; it adds one row to each of the four even-parity corners and removes one from each of the
four odd-parity corners (or the reverse). Summing over any one chosen coordinate cancels, so every one-way and
every two-way table is unchanged exactly. A move that would make a count negative is not available.
Chain: Metropolis-Hastings over tables with target proportional to 1/prod(n_cell!) (the conditional law of the
pairwise model given its pair tables) and uniform choice among the available moves; the acceptance test is an
integer comparison. Integers only.
  python cube_v16.py <data_dir> <steps> <seed> [sample_every]
"""
import random, sys
from fractions import Fraction as Fr
from itertools import combinations

D = sys.argv[1]; STEPS = int(sys.argv[2]); SEED = int(sys.argv[3]); EVERY = int(sys.argv[4]) if len(sys.argv) > 4 else 50
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
n = len(keys); V = 9
cols = []
for x in L:
    order = sorted(range(n), key=lambda i: (x[keys[i]], keys[i]))
    t = [0] * n
    for rnk, i in enumerate(order):
        t[i] = 0 if rnk < n // 3 else (1 if rnk < n - n // 3 else 2)
    cols.append(t)
T0 = {}
for i in range(n):
    p = tuple(cols[v][i] for v in range(V))
    T0[p] = T0.get(p, 0) + 1
TRIPLES = list(combinations(range(V), 3)); PAIRS = list(combinations(range(V), 2))
VP = [(0, 1), (0, 2), (1, 2)]
CUBES = [(xa, xb, xc) for xa in VP for xb in VP for xc in VP]


def pair_tables(T):
    out = {}
    for p, c in T.items():
        for a, b in PAIRS:
            k = (a, b, p[a], p[b]); out[k] = out.get(k, 0) + c
    return out


def moves(T):
    """every available cube move as (minus_cells, plus_cells)."""
    res = []
    for tr in TRIPLES:
        a, b, c = tr
        groups = {}
        for p in T:
            ctx = p[:a] + p[a + 1:b] + p[b + 1:c] + p[c + 1:]
            groups.setdefault(ctx, set()).add((p[a], p[b], p[c]))
        for ctx, subs in groups.items():
            if len(subs) < 4:
                continue
            def full(x, y, w):
                q = list(ctx); q.insert(a, x); q.insert(b, y); q.insert(c, w); return tuple(q)
            for (x0, x1), (y0, y1), (w0, w1) in CUBES:
                even = [(x0, y0, w0), (x1, y1, w0), (x1, y0, w1), (x0, y1, w1)]
                odd = [(x1, y0, w0), (x0, y1, w0), (x0, y0, w1), (x1, y1, w1)]
                if all(s in subs for s in odd):
                    res.append((tuple(full(*s) for s in odd), tuple(full(*s) for s in even)))
                if all(s in subs for s in even):
                    res.append((tuple(full(*s) for s in even), tuple(full(*s) for s in odd)))
    return res


def stats(T):
    return (sum(c for p, c in T.items() if len(set(p)) == 1), len(T), max(T.values()))


P0 = pair_tables(T0)
M = moves(T0)
print("CUBEHDR|rows=%d|distinct_patterns=%d|pair_table_cells=%d|available_cube_moves_at_the_real_table=%d|steps=%d|seed=%d|target=1/prod(n!)|integer_only=1|json=0"
      % (n, len(T0), len(P0), len(M), STEPS, SEED))
print("REAL|all_nine_equal=%d|distinct_patterns=%d|largest_pattern=%d|json=0" % stats(T0))
if not M:
    print("VERDICT|result=TRAPPED_no_cube_move_is_available_from_the_real_table|control=INCONCLUSIVE|json=0"); sys.exit(0)
rnd = random.Random(SEED)
T = dict(T0); acc = 0; samples = []; seen = {tuple(sorted(T.items()))}
for step in range(1, STEPS + 1):
    minus, plus = M[rnd.randrange(len(M))]
    num = 1; den = 1
    for p in minus:
        num *= T[p]
    for p in plus:
        den *= T.get(p, 0) + 1
    T2 = dict(T)
    for p in minus:
        T2[p] -= 1
        if T2[p] == 0:
            del T2[p]
    for p in plus:
        T2[p] = T2.get(p, 0) + 1
    M2 = moves(T2)
    if rnd.randrange(den * len(M2)) < num * len(M):
        T, M = T2, M2; acc += 1
    if step % EVERY == 0:
        s = stats(T); dist = sum(abs(T.get(p, 0) - T0.get(p, 0)) for p in set(T) | set(T0)) // 2
        samples.append(s + (dist, len(M)))
        seen.add(tuple(sorted(T.items())))
exact = pair_tables(T) == P0
print("CHAIN|accepted=%d|of=%d|pair_tables_exact_at_the_end=%d|distinct_tables_among_samples=%d|samples=%d|json=0" % (acc, STEPS, int(exact), len(seen), len(samples)))
half = samples[len(samples) // 2:]
for q, name in ((1, "distinct_patterns"), (2, "largest_pattern"), (0, "all_nine_equal"), (3, "rows_moved_from_the_real_table"), (4, "available_moves")):
    xs = sorted(s[q] for s in half)
    print("SECOND_HALF|statistic=%s|min=%d|median=%d|max=%d|samples=%d|json=0" % (name, xs[0], xs[len(xs) // 2], xs[-1], len(xs)))
r = stats(T0)
dp = [s[1] for s in half]
print("VERDICT|primary=distinct_patterns|real=%d|chain_min=%d|chain_max=%d|samples_at_or_below_real=%d|of=%d|largest_pattern_real=%d|chain_range=%d..%d|all_nine_equal_real=%d|chain_range_9=%d..%d|json=0"
      % (r[1], min(dp), max(dp), sum(1 for x in dp if x <= r[1]), len(dp), r[2], min(s[2] for s in half), max(s[2] for s in half), r[0], min(s[0] for s in half), max(s[0] for s in half)))
