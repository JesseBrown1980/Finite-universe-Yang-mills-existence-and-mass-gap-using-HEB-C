# Why a cut divisible by 3 is incomplete: tests that the configurations missing at M = cut are exactly the (0, cut/3) ones with no two 3-cycles adjacent.
# usage: py_missing_check.py LX LY CUT RITZ_OUT   Python integers, json=0.
import sys
from itertools import combinations
from math import comb
LX, LY, CUT, OUT = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
P = LX * LY
def n_of(a, b):
    if a % 2:
        return 0
    if a == 0:
        return 12 * 2 ** b + 6 * (-1) ** b
    return 12 * 3 ** a * 2 ** b
want = 0
for a in range(0, P + 1, 2):
    for b in range(0, P - a + 1):
        if 2 * a + 3 * b == CUT:
            want += comb(P, a) * comb(P - a, b) * n_of(a, b)
have = None
for line in open(OUT, encoding='utf-8'):
    if line.startswith('MODEL_M|'):
        d = dict(x.split('=', 1) for x in line.strip().split('|')[1:] if '=' in x)
        if int(d['M']) == CUT:
            have = int(d['gauge_fixed_configs'])
adj = set()
for y in range(LY):
    for x in range(LX):
        p = x + LX * y
        adj.add((p, (x + 1) % LX + LX * y))
        adj.add((p, x + LX * ((y + 1) % LY)))
adj |= {(b, a) for a, b in adj}
b = CUT // 3
isolated = 0
for s in combinations(range(P), b):
    if all((u, v) not in adj for u, v in combinations(s, 2)):
        isolated += 1
pred = isolated * n_of(0, b)
print("MISSING_CHECK|Lx=%d|Ly=%d|cut=%d|formula_configs_at_cut=%d|model_configs_at_cut=%d|missing=%d|isolated_sets=%d|predicted_missing=%d|same=%d|json=0" % (LX, LY, CUT, want, have, want - have, isolated, pred, 1 if want - have == pred else 0))
sys.exit(0 if want - have == pred else 1)
