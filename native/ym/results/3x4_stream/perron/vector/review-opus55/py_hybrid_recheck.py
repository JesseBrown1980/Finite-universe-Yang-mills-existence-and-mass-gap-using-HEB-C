# Independent recheck of a hybrid certificate written by ritz: recomputes its value with a separately written representation, from the definition of H.
# d = the vector on orbits with 0 < M <= CUT (given per lattice-symmetry class), d = one value per lump above the cut, d = 0 on flats.
# Rows at M <= CUT: every move recomputed, exact ratio. Rows above: my own enumeration of the table's integer points, with a move into a lump at M <= CUT taken at the largest d in that lump.
# usage: py_hybrid_recheck.py LX LY R CUT HYBRID_FILE EXPECT_MICRO [--sabotage]   Python integers, json=0. The sabotage lowers one value and must change the result.
import sys
from math import isqrt
from itertools import permutations, product
LX, LY, R, CUT = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
PATH, EXPECT = sys.argv[5], int(sys.argv[6])
SAB = '--sabotage' in sys.argv
PERMS = list(permutations(range(3)))
IDX = {p: i for i, p in enumerate(PERMS)}
MUL = [[IDX[tuple(p[q[i]] for i in range(3))] for q in PERMS] for p in PERMS]
E = IDX[(0, 1, 2)]
INV = [next(j for j in range(6) if MUL[i][j] == E) for i in range(6)]
COST = [2 - (sum(1 for i in range(3) if p[i] == i) - 1) for p in PERMS]
TR = [i for i in range(6) if COST[i] == 2]
CONJ = [[MUL[MUL[c][u]][INV[c]] for u in range(6)] for c in range(6)]
def rust_el(e):
    k, f = e % 3, e // 3
    return IDX[tuple((k + (x if f == 0 else -x)) % 3 for x in range(3))]
RUST = [rust_el(e) for e in range(6)]
P, NL = LX * LY, 2 * LX * LY
def L(x, y, d):
    return 2 * ((x % LX) + LX * (y % LY)) + d
def site(x, y):
    return (x % LX) + LX * (y % LY)
PL = [(L(x, y, 0), L(x + 1, y, 1), L(x, y + 1, 0), L(x, y, 1)) for y in range(LY) for x in range(LX)]
def lump(u):
    a = b = 0
    for q0, q1, q2, q3 in PL:
        c = COST[MUL[MUL[MUL[u[q0]][u[q1]]][INV[u[q2]]]][INV[u[q3]]]]
        if c == 2:
            a += 1
        elif c == 3:
            b += 1
    return a, b
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
TREE, ORDER = set(), []
for x in range(1, LX):
    TREE.add(L(x - 1, 0, 0))
    ORDER.append((L(x - 1, 0, 0), site(x - 1, 0), site(x, 0)))
for x in range(LX):
    for y in range(1, LY):
        TREE.add(L(x, y - 1, 1))
        ORDER.append((L(x, y - 1, 1), site(x, y - 1), site(x, y)))
FREE = [l for l in range(NL) if l not in TREE]
SRC, DST = [0] * NL, [0] * NL
for y in range(LY):
    for x in range(LX):
        SRC[L(x, y, 0)], DST[L(x, y, 0)] = site(x, y), site(x + 1, y)
        SRC[L(x, y, 1)], DST[L(x, y, 1)] = site(x, y), site(x, y + 1)
def orbit_key(u):
    p = [E] * P
    for l, a, b in ORDER:
        p[b] = MUL[p[a]][u[l]]
    v = [MUL[MUL[p[SRC[l]]][u[l]]][INV[p[DST[l]]]] for l in FREE]
    return min(tuple(CONJ[c][e] for e in v) for c in range(6))
def automorphisms():
    out = []
    swaps = [False, True] if LX == LY else [False]
    for sw, sx, sy, tx, ty in product(swaps, [1, -1], [1, -1], range(LX), range(LY)):
        table = [None] * NL
        def phi(x, y):
            a, b = sx * x, sy * y
            if sw:
                a, b = b, a
            return (a + tx) % LX, (b + ty) % LY
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
                    else:
                        table[L(x, y, d)] = (L(q[0], q[1], 1), True)
        out.append(table)
    return out
AUT = automorphisms()
reps, G = [], {}
for line in open(PATH, encoding='utf-8'):
    f = line.strip().split('|')
    if f[0] == 'P':
        reps.append((int(f[1]), int(f[2])))
    elif f[0] == 'G':
        G[(int(f[1]), int(f[2]))] = int(f[3])
if SAB:
    k, v = reps[0]
    reps[0] = (k, v // 2)
psi_of, dmax = {}, {}
for k, v in reps:
    u = decode(k)
    a, b = lump(u)
    assert 2 * a + 3 * b <= CUT
    dmax[(a, b)] = max(dmax.get((a, b), 0), v)
    for t in AUT:
        w = [E] * NL
        for l, (to, inv) in enumerate(t):
            w[to] = INV[u[l]] if inv else u[l]
        psi_of[orbit_key(w)] = v
U = 10 ** 6
min_a = None
missing = 0
for k, v in reps:
    u = decode(k)
    a, b = lump(u)
    s = 0
    for l in range(NL):
        keep = u[l]
        for e in TR:
            u[l] = MUL[e][keep]
            t = lump(u)
            m = 2 * t[0] + 3 * t[1]
            if m == 0:
                pass
            elif m <= CUT:
                d = psi_of.get(orbit_key(u))
                if d is None:
                    missing += 1
                else:
                    s += d
            else:
                s += G[t]
        u[l] = keep
    r = (R * (2 * a + 3 * b) + 3 * NL) * U - (s * U + v - 1) // v
    min_a = r if min_a is None or r < min_a else min_a
def c2s(n):
    return 0 if n == 0 else isqrt(4 * n - 1) + 1
def adj(s):
    if s == 0:
        return 0
    if s == P:
        return 2 * s
    return 2 * s - min(c2s(s), min(LX, LY), c2s(P - s))
RULE = ((2, 0, 3),), ((0, 0, 1), (0, 1, 2)), ((2, -1, 3),), ((-2, 0, 1), (-2, 2, 2)), ((-2, 1, 2), (-2, 2, 1)), ((0, -1, 1), (0, 0, 2)), ((2, -2, 3),)
def dbar(t):
    if t == (0, 0):
        return 0
    return dmax.get(t, 0) if 2 * t[0] + 3 * t[1] <= CUT else G[t]
min_b = None
for a in range(0, P + 1, 2):
    for b in range(0, P - a + 1):
        if 2 * a + 3 * b <= CUT:
            continue
        A, B, I = adj(a), adj(b), adj(a + b)
        g0 = G[(a, b)]
        for tt in range(0, A + 1):
            for tc in range(0, min(4 * a - 2 * tt, 4 * b) + 1):
                for cc in range(0, min(B, (4 * b - tc) // 2, I - tt - tc) + 1):
                    et, ec = 4 * a - 2 * tt - tc, 4 * b - tc - 2 * cc
                    ee = NL - et - ec - tt - tc - cc
                    if ee < 0:
                        continue
                    for tts in range(0, tt + 1):
                        n = (ee, et, ec, tts, tt - tts, tc, cc)
                        s, own = 0, 0
                        for pat, c in enumerate(n):
                            if c:
                                for da, db, m in RULE[pat]:
                                    t = (a + da, b + db)
                                    if t == (a, b):
                                        own += m * c
                                    else:
                                        s += m * c * dbar(t)
                        r = (R * (2 * a + 3 * b) + 3 * NL - own) * U - (s * U + g0 - 1) // g0
                        min_b = r if min_b is None or r < min_b else min_b
cert = min(min_a, min_b)
same = cert == EXPECT and missing == 0
print("HYBRID_RECHECK|Lx=%d|Ly=%d|r=%d|mcut=%d|reps=%d|gauge_orbits=%d|missing=%d|min_exact_rows=%d|min_table_rows=%d|cert_micro=%d|expect_micro=%d|sabotage=%d|verdict=%s|json=0" % (LX, LY, R, CUT, len(reps), len(psi_of), missing, min_a, min_b, cert, EXPECT, 1 if SAB else 0, 'SAME' if same else 'DIFFER'))
sys.exit(0 if same else 1)
