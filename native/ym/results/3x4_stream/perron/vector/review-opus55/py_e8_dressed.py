# Outside the claim, on "what would change the numbers": a tighter rigorous upper bound on E_8 than 3 nl, with no store.
# For each flat orbit f: A = indicator of f, B = (number of moves into f), both functions on gauge orbits. Test space of dimension 16.
# Exact integer matrix elements, by the definition, in the weighted inner product. If the 16 x 16 problem is block diagonal over f with every block
# [[3nl, -sqrt(3nl)], [-sqrt(3nl), 3nl + 4 r]] then E_8 <= the lower root, 3nl + 2r - sqrt(4r^2 + 3nl), since the 8 lower Ritz vectors span an 8-dimensional space with all values at that root.
# usage: py_e8_dressed.py LX LY R [--sabotage]    Python integers, json=0. The sabotage uses 2 r in place of 4 r in the check and must go red.
import sys
from math import isqrt
from itertools import permutations, product
LX, LY, R = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
SAB = '--sabotage' in sys.argv
PERMS = list(permutations(range(3)))
IDX = {p: i for i, p in enumerate(PERMS)}
MUL = [[IDX[tuple(p[q[i]] for i in range(3))] for q in PERMS] for p in PERMS]
E = IDX[(0, 1, 2)]
INV = [next(j for j in range(6) if MUL[i][j] == E) for i in range(6)]
COST = [2 - (sum(1 for i in range(3) if p[i] == i) - 1) for p in PERMS]
TR = [i for i in range(6) if COST[i] == 2]
CONJ = [[MUL[MUL[c][u]][INV[c]] for u in range(6)] for c in range(6)]
NL = 2 * LX * LY
def L(x, y, d):
    return 2 * ((x % LX) + LX * (y % LY)) + d
def site(x, y):
    return (x % LX) + LX * (y % LY)
PL = [(L(x, y, 0), L(x + 1, y, 1), L(x, y + 1, 0), L(x, y, 1)) for y in range(LY) for x in range(LX)]
SRC, DST = [0] * NL, [0] * NL
for y in range(LY):
    for x in range(LX):
        SRC[L(x, y, 0)], DST[L(x, y, 0)] = site(x, y), site(x + 1, y)
        SRC[L(x, y, 1)], DST[L(x, y, 1)] = site(x, y), site(x, y + 1)
TREE = set()
ORDER = []
for x in range(1, LX):
    TREE.add(L(x - 1, 0, 0))
    ORDER.append((L(x - 1, 0, 0), site(x - 1, 0), site(x, 0)))
for x in range(LX):
    for y in range(1, LY):
        TREE.add(L(x, y - 1, 1))
        ORDER.append((L(x, y - 1, 1), site(x, y - 1), site(x, y)))
FREE = [l for l in range(NL) if l not in TREE]
def key_of(u):
    p = [E] * (LX * LY)
    for l, a, b in ORDER:
        p[b] = MUL[p[a]][u[l]]
    v = [MUL[MUL[p[SRC[l]]][u[l]]][INV[p[DST[l]]]] for l in FREE]
    imgs = [tuple(CONJ[c][e] for e in v) for c in range(6)]
    m = min(imgs)
    return m, 6 // imgs.count(m)
def decode(k):
    u = [E] * NL
    for l, e in zip(FREE, k):
        u[l] = e
    return u
def total_m(u):
    return sum(COST[MUL[MUL[MUL[u[a]][u[b]]][INV[u[c]]]][INV[u[d]]]] for a, b, c, d in PL)
def moves(k):
    """Keys of the 3 nl moves out of a gauge orbit, from its representative."""
    u = decode(k)
    out = []
    for l in range(NL):
        keep = u[l]
        for s in TR:
            u[l] = MUL[s][keep]
            out.append(key_of(u)[0])
        u[l] = keep
    return out
flats = {}
for hx, hy in product(range(6), range(6)):
    if MUL[hx][hy] != MUL[hy][hx]:
        continue
    u = [E] * NL
    for y in range(LY):
        u[L(LX - 1, y, 0)] = hx
    for x in range(LX):
        u[L(x, LY - 1, 1)] = hy
    k, w = key_of(u)
    flats[k] = w
assert len(flats) == 8 and sum(flats.values()) == 18
W = {}
def weight(k):
    if k not in W:
        W[k] = key_of(decode(k))[1]
    return W[k]
# B_f as a dictionary orbit -> number of moves from that orbit into f.
B = {}
for f in flats:
    d = {}
    for y in set(moves(f)):
        c = sum(1 for z in moves(y) if z == f)
        d[y] = c
    B[f] = d
assert all(k not in B[f] for f in flats for k in flats)
cache = {}
def H_on(vec):
    """(H v) on orbits as a dictionary, for v a dictionary. Only orbits that can be reached are kept; the diagonal is exact."""
    out = {}
    for x, val in vec.items():
        m = total_m(decode(x))
        out[x] = out.get(x, 0) + (R * m + 3 * NL) * val
    # -sum_moves v(m x) at x: by detailed balance it is simplest to walk the support: for each y in support and each move y -> x, x gets a term weighted by w_y / w_x.
    return out
def inner(u, v):
    if len(u) > len(v):
        u, v = v, u
    return sum(weight(k) * val * v[k] for k, val in u.items() if k in v)
def quad(u, v):
    """<u, H v> with u and v dictionaries: sum_x w_x u_x ((r M + 3 nl) v_x - sum_moves v(m x))."""
    s = 0
    for x, ux in u.items():
        m = total_m(decode(x))
        t = (R * m + 3 * NL) * v.get(x, 0)
        for z in moves(x):
            t -= v.get(z, 0)
        s += weight(x) * ux * t
    return s
A = {f: {f: 1} for f in flats}
blocks = []
cross_bad = 0
fl = list(flats)
for i, f in enumerate(fl):
    aa = inner(A[f], A[f])
    bb = inner(B[f], B[f])
    ab = inner(A[f], B[f])
    haa = quad(A[f], A[f])
    hab = quad(A[f], B[f])
    hbb = quad(B[f], B[f])
    blocks.append((aa, bb, ab, haa, hab, hbb))
    for g in fl[i + 1:]:
        for u, v in ((A[f], A[g]), (A[f], B[g]), (B[f], A[g]), (B[f], B[g])):
            if inner(u, v) != 0 or quad(u, v) != 0:
                cross_bad += 1
ok = cross_bad == 0
r_in_block = 2 * R if SAB else 4 * R
for aa, bb, ab, haa, hab, hbb in blocks:
    # Normalized: <A,HA>/aa = 3nl; <A,HB>^2/(aa bb) = 3nl; <B,HB>/bb = 3nl + 4r; ab = 0.
    if ab != 0 or haa != 3 * NL * aa or hab * hab != 3 * NL * aa * bb or hbb != (3 * NL + r_in_block) * bb or hab >= 0:
        ok = False
# Lower root: 3nl + 2r - sqrt(4r^2 + 3nl). The smallest micro value at or above it.
d = 4 * R * R + 3 * NL
root_floor = isqrt(d * 10**12)  # floor of 10^6 sqrt(d)
u8 = (3 * NL + 2 * R) * 10**6 - root_floor
print("E8_DRESSED|Lx=%d|Ly=%d|r=%d|flats=%d|cross_elements_nonzero=%d|blocks_as_predicted=%d|flat_bound_micro=%d|E8_upper_micro=%d|improvement_micro=%d|sabotage=%d|verdict=%s|json=0" % (LX, LY, R, len(fl), cross_bad, 1 if ok else 0, 3 * NL * 10**6, u8, 3 * NL * 10**6 - u8, 1 if SAB else 0, 'PASS' if ok else 'FAIL'))
sys.exit(0 if ok else 1)
