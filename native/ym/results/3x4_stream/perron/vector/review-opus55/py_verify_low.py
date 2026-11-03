# Second path: reads LOW rows of a hunt output, rebuilds each configuration, and recomputes its exact ratio from the definition of H with S3 as permutation tuples
# and a separately written lattice walk. All 3 nl moves, with all plaquettes recomputed. Python integers and fractions, json=0.
# usage: py_verify_low.py HUNT_OUT LX LY R GFILE CLAIM_MICRO
import sys
from fractions import Fraction as Fr
HUNT, LX, LY, R, GF, CLAIM = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], int(sys.argv[6])
def perm_of(e):  # my element id k + 3 f is x -> k + (-1)^f x on Z3
    k, f = e % 3, e // 3
    return tuple((k + (x if f == 0 else -x)) % 3 for x in range(3))
def comp(p, q):
    return tuple(p[q[i]] for i in range(3))
def inv(p):
    r = [0, 0, 0]
    for i in range(3):
        r[p[i]] = i
    return tuple(r)
IDP = (0, 1, 2)
def cost(p):
    fixed = sum(1 for i in range(3) if p[i] == i)
    return 2 - (fixed - 1)
TRANS = [p for p in [perm_of(e) for e in range(6)] if sum(1 for i in range(3) if p[i] == i) == 1]
assert len(TRANS) == 3
g = {}
for line in open(GF, encoding='utf-8'):
    if line.startswith('G|'):
        d = dict(x.split('=', 1) for x in line.strip().split('|')[1:] if '=' in x)
        g[(int(d['a']), int(d['b']))] = int(d['g'])
g[(0, 0)] = 0
def link(x, y, d):
    return 2 * ((x % LX) + LX * (y % LY)) + d
def lump(U):
    a = b = 0
    for y in range(LY):
        for x in range(LX):
            h = comp(comp(comp(U[link(x, y, 0)], U[link(x + 1, y, 1)]), inv(U[link(x, y + 1, 0)])), inv(U[link(x, y, 1)]))
            c = cost(h)
            if c == 2:
                a += 1
            elif c == 3:
                b += 1
    return a, b
n = 0
bad = 0
low = None
for line in open(HUNT, encoding='utf-8'):
    if not line.startswith('LOW|'):
        continue
    d = dict(x.split('=', 1) for x in line.strip().split('|')[1:] if '=' in x)
    U = [perm_of(int(c)) for c in d['config']]
    a, b = lump(U)
    assert (a, b) == (int(d['a']), int(d['b'])), "lump differs from the hunt row"
    base = g[(a, b)]
    s = Fr(0)
    for l in range(2 * LX * LY):
        keep = U[l]
        for t in TRANS:
            U[l] = comp(t, keep)
            s += 1 - Fr(g[lump(U)], base)
        U[l] = keep
    ratio = R * (2 * a + 3 * b) + s
    fl = (ratio * 1000000).__floor__()
    n += 1
    if fl != int(d['micro']):
        bad += 1
    if ratio < Fr(CLAIM, 1000000):
        bad += 1
    if low is None or ratio < low[0]:
        low = (ratio, a, b)
print("VERIFY_LOW|file=%s|configs=%d|bad=%d|lowest_micro=%d|lump=%d,%d|claim_micro=%d|exact_minus_claim=%s|json=0" % (HUNT.split('/')[-1], n, bad, (low[0] * 1000000).__floor__(), low[1], low[2], CLAIM, str(low[0] - Fr(CLAIM, 1000000))[:60]))
sys.exit(1 if bad else 0)
