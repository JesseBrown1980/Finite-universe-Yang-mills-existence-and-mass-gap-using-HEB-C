#!/usr/bin/env python3
"""pascal_v17.py -- the composition of n leaves per row, laid on layer n of Pascal's pyramid.

For n frozen leaves (each a trit per row, by its own terciles of the exact local ratio slack/v), every row has a
composition (a, b, c) = how many leaves read -, 0, +, with a + b + c = n. If the leaves were independent the rows
would spread over the compositions as the trinomial numbers n!/(a! b! c!) / 3^n: layer n of Pascal's pyramid.
This prints where the rows actually sit. Exact integers only (expected counts are printed as integer fractions
of 3^n).   python pascal_v17.py <leaf_file> <leaf_file> ...   (any number of leaves)
"""
import sys
from fractions import Fraction as Fr
from math import factorial


def load(path):
    d = {}
    for line in open(path):
        if line.startswith("LEAF|"):
            x = dict(w.split("=", 1) for w in line.strip().split("|")[1:] if "=" in w)
            d[int(x["key"])] = Fr(int(x["slack"]), int(x["v"]))
    return d


L = [load(p) for p in sys.argv[1:]]
keys = sorted(set.intersection(*[set(x) for x in L]))
rows = len(keys); n = len(L)
cols = []
for x in L:
    order = sorted(range(rows), key=lambda i: (x[keys[i]], keys[i]))
    t = [0] * rows
    for rnk, i in enumerate(order):
        t[i] = 0 if rnk < rows // 3 else (1 if rnk < rows - rows // 3 else 2)
    cols.append(t)
comp = {}
for i in range(rows):
    a = sum(1 for c in cols if c[i] == 0); b = sum(1 for c in cols if c[i] == 1)
    comp[(a, b, n - a - b)] = comp.get((a, b, n - a - b), 0) + 1
tri = lambda a, b, c: factorial(n) // (factorial(a) * factorial(b) * factorial(c))
print("PASCALHDR|leaves=%d|rows=%d|compositions_possible=%d|compositions_occupied=%d|layer_sum=3^%d|json=0" % (n, rows, (n + 1) * (n + 2) // 2, len(comp), n))
corners = comp.get((n, 0, 0), 0) + comp.get((0, n, 0), 0) + comp.get((0, 0, n), 0)
edges = sum(c for (a, b, cc), c in comp.items() if (a == 0) + (b == 0) + (cc == 0) == 1)
inside = sum(c for (a, b, cc), c in comp.items() if a and b and cc)
exp_corner = Fr(3 * rows, 3 ** n); exp_inside = Fr(rows * sum(tri(a, b, n - a - b) for a in range(1, n) for b in range(1, n - a)), 3 ** n)
print("PASCAL|rows_at_the_three_corners=%d|independent_expectation=%d/%d|rows_on_the_edges=%d|rows_in_the_interior=%d|independent_expectation_interior=%d_of_%d|json=0"
      % (corners, exp_corner.numerator, exp_corner.denominator, edges, inside, exp_inside.numerator // exp_inside.denominator, rows))
# radial profile: distance from the centre measured by the largest of (a, b, c)
prof = {}; eprof = {}
for a in range(n + 1):
    for b in range(n + 1 - a):
        c = n - a - b; m = max(a, b, c)
        prof[m] = prof.get(m, 0) + comp.get((a, b, c), 0)
        eprof[m] = eprof.get(m, 0) + tri(a, b, c)
print("PROFILE|by_largest_count|" + "|".join("max=%d:rows_%d_expected_%d" % (m, prof[m], eprof[m] * rows // 3 ** n) for m in sorted(prof)) + "|json=0")
if n <= 9:
    for a in range(n, -1, -1):
        print("LAYER|minus=%d|" % a + " ".join("%4d" % comp.get((a, b, n - a - b), 0) for b in range(n + 1 - a)) + "|json=0")
