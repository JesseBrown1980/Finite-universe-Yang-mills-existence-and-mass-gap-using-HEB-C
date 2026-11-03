# Independent recheck of a Rust ritz run: reads its psi file and recomputes A, B, C from the definition of H with a separately written representation:
# S3 as permutation tuples, lattice symmetries built from endpoints, a different gauge tree, and a whole-space dictionary of gauge orbits instead of a lattice-canonical key.
# Python integers only, json=0.
# usage: py_ritz_recheck.py LX LY R CUT PSIFILE RITZ_OUT [--sabotage]
# With --sabotage one psi value is changed after reading, and the comparison must go red. Exit 1 on any mismatch.
import sys
from itertools import permutations, product
LX, LY, R, CUT = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
PSI, OUT = sys.argv[5], sys.argv[6]
SAB = '--sabotage' in sys.argv
PERMS = list(permutations(range(3)))
IDX = {p: i for i, p in enumerate(PERMS)}
MUL = [[IDX[tuple(p[q[i]] for i in range(3))] for q in PERMS] for p in PERMS]
INV = [next(j for j in range(6) if MUL[i][j] == IDX[(0, 1, 2)]) for i in range(6)]
E = IDX[(0, 1, 2)]
COST = [2 - (sum(1 for i in range(3) if p[i] == i) - 1) for p in PERMS]
TR = [i for i in range(6) if COST[i] == 2]
assert sorted(COST) == [0, 2, 2, 2, 3, 3] and len(TR) == 3
CONJ = [[MUL[MUL[c][u]][INV[c]] for u in range(6)] for c in range(6)]
def rust_el(e):
    k, f = e % 3, e // 3
    return IDX[tuple((k + (x if f == 0 else -x)) % 3 for x in range(3))]
RUST = [rust_el(e) for e in range(6)]
NL = 2 * LX * LY
def L(x, y, d):
    return 2 * ((x % LX) + LX * (y % LY)) + d
def site(x, y):
    return (x % LX) + LX * (y % LY)
PL = [(L(x, y, 0), L(x + 1, y, 1), L(x, y + 1, 0), L(x, y, 1)) for y in range(LY) for x in range(LX)]
LINK_PLAQ = [[] for _ in range(NL)]
for i, q in enumerate(PL):
    for l in q:
        LINK_PLAQ[l].append(i)
def hol(u, i):
    a, b, c, d = PL[i]
    return MUL[MUL[MUL[u[a]][u[b]]][INV[u[c]]]][INV[u[d]]]
def total_m(u):
    return sum(COST[hol(u, i)] for i in range(LX * LY))
# Rust's tree, only to decode its keys.
RTREE = set()
for y in range(LY):
    for x in range(LX - 1):
        RTREE.add(L(x, y, 0))
for y in range(LY - 1):
    RTREE.add(L(0, y, 1))
RFREE = [l for l in range(NL) if l not in RTREE]
def decode(key):
    u = [E] * NL
    for l in reversed(RFREE):
        u[l] = RUST[key % 6]
        key //= 6
    return u
# My tree here: y-links in every column but the top, x-links on row 0 but the last.
EDGES = []
TREE = set()
for x in range(LX):
    for y in range(1, LY):
        l = L(x, y - 1, 1)
        TREE.add(l)
for x in range(1, LX):
    TREE.add(L(x - 1, 0, 0))
FREE = [l for l in range(NL) if l not in TREE]
ORDER = []
for x in range(1, LX):
    ORDER.append((L(x - 1, 0, 0), site(x - 1, 0), site(x, 0)))
for x in range(LX):
    for y in range(1, LY):
        ORDER.append((L(x, y - 1, 1), site(x, y - 1), site(x, y)))
assert len(ORDER) == LX * LY - 1
SRC = [0] * NL
DST = [0] * NL
for y in range(LY):
    for x in range(LX):
        SRC[L(x, y, 0)] = site(x, y)
        DST[L(x, y, 0)] = site(x + 1, y)
        SRC[L(x, y, 1)] = site(x, y)
        DST[L(x, y, 1)] = site(x, y + 1)
def orbit_key(u):
    """Gauge-orbit key and its conjugation stabilizer size."""
    p = [E] * (LX * LY)
    for l, a, b in ORDER:
        p[b] = MUL[p[a]][u[l]]
    v = [MUL[MUL[p[SRC[l]]][u[l]]][INV[p[DST[l]]]] for l in FREE]
    imgs = [tuple(CONJ[c][e] for e in v) for c in range(6)]
    m = min(imgs)
    return m, imgs.count(m)
# Lattice symmetries, by endpoints.
def automorphisms():
    out = []
    swaps = [False, True] if LX == LY else [False]
    for sw, sx, sy, tx, ty in product(swaps, [1, -1], [1, -1], range(LX), range(LY)):
        def phi(x, y, sw=sw, sx=sx, sy=sy, tx=tx, ty=ty):
            a, b = sx * x, sy * y
            if sw:
                a, b = b, a
            return (a + tx) % LX, (b + ty) % LY
        table = [None] * NL
        for y in range(LY):
            for x in range(LX):
                for d in (0, 1):
                    x2, y2 = (x + 1, y) if d == 0 else (x, y + 1)
                    p, q = phi(x, y), phi(x2, y2)
                    if ((p[0] + 1) % LX, p[1]) == q:
                        table[L(x, y, d)] = (L(p[0], p[1], 0), False)
                    elif (p[0], (p[1] + 1) % LY) == q:
                        table[L(x, y, d)] = (L(p[0], p[1], 1), False)
                    elif ((q[0] + 1) % LX, q[1]) == p:
                        table[L(x, y, d)] = (L(q[0], q[1], 0), True)
                    elif (q[0], (q[1] + 1) % LY) == p:
                        table[L(x, y, d)] = (L(q[0], q[1], 1), True)
                    else:
                        raise SystemExit("not a lattice map")
        out.append(table)
    return out
AUT = automorphisms()
def image(u, table):
    v = [E] * NL
    for l, (to, inv) in enumerate(table):
        v[to] = INV[u[l]] if inv else u[l]
    return v
rows = []
for line in open(PSI, encoding='utf-8'):
    k, m, w, p = line.strip().split('|')
    rows.append((int(k), int(m), int(w), int(p)))
if SAB:
    k, m, w, p = rows[len(rows) // 2]
    rows[len(rows) // 2] = (k, m, w, p + 1 + p // 7)
psi_of = {}
weight_bad = 0
m_bad = 0
weights = []
for k, m, w, p in rows:
    u = decode(k)
    if total_m(u) != m:
        m_bad += 1
    seen = {}
    for t in AUT:
        key, st = orbit_key(image(u, t))
        seen[key] = st
    w2 = sum(6 // st for st in seen.values())
    if w2 != w:
        weight_bad += 1
    weights.append(w2)
    for key in seen:
        if key in psi_of and psi_of[key] != p:
            raise SystemExit("two sector rows claim one gauge orbit")
        psi_of[key] = p
A = B = 0
for (k, m, w, p), w2 in zip(rows, weights):
    u = decode(k)
    s = (R * m + 3 * NL) * p
    for l in range(NL):
        keep = u[l]
        for e in TR:
            u[l] = MUL[e][keep]
            s -= psi_of.get(orbit_key(u)[0], 0)
        u[l] = keep
    A += w2 * p * s
    B += w2 * p * p
# Flat classes: 18 commuting pairs from cuts.
classes = {}
for hx, hy in product(range(6), range(6)):
    if MUL[hx][hy] != MUL[hy][hx]:
        continue
    u = [E] * NL
    for y in range(LY):
        u[L(LX - 1, y, 0)] = hx
    for x in range(LX):
        u[L(x, LY - 1, 1)] = hy
    assert total_m(u) == 0
    key, st = orbit_key(u)
    classes[key] = (u, 6 // st)
assert len(classes) == 8 and sum(c[1] for c in classes.values()) == 18
C = 0
for key, (u, wf) in classes.items():
    s = 0
    for l in range(NL):
        keep = u[l]
        for e in TR:
            u[l] = MUL[e][keep]
            s += psi_of.get(orbit_key(u)[0], 0)
        u[l] = keep
    C += wf * s * s
d = None
for line in open(OUT, encoding='utf-8'):
    if line.startswith('RITZ|'):
        d = dict(x.split('=', 1) for x in line.strip().split('|')[1:] if '=' in x)
same = d is not None and int(d['A']) == A and int(d['B']) == B and int(d['C']) == C
print("RITZ_RECHECK|Lx=%d|Ly=%d|r=%d|mcut=%d|rows=%d|gauge_orbits=%d|m_bad=%d|weight_bad=%d|A_same=%d|B_same=%d|C_same=%d|sabotage=%d|verdict=%s|json=0" % (LX, LY, R, CUT, len(rows), len(psi_of), m_bad, weight_bad, int(int(d['A']) == A), int(int(d['B']) == B), int(int(d['C']) == C), 1 if SAB else 0, 'SAME' if same and not m_bad and not weight_bad else 'DIFFER'))
sys.exit(0 if same and not m_bad and not weight_bad else 1)
