# The flat block from the definition: on each torus, all 18 commuting holonomy pairs, their gauge classes, and every single-link move out of each.
# Checks: M = 0 on all 18; 8 classes by gauge-fixed conjugation minimum; each of the 3 nl moves lands at M = 4 exactly, so never on a flat state, so the 8 x 8 block of H is 3 nl times the identity.
# Also checks the classes by an invariant that uses no gauge fixing: the class of the two holonomies and of their product and whether they are equal, under random gauge transformations.
# Python integers, json=0. usage: py_flats.py LX LY [--sabotage]; the sabotage lets 19 pairs through (one non-commuting) and must go red.
import sys, random
from itertools import permutations, product
LX, LY = int(sys.argv[1]), int(sys.argv[2])
SAB = '--sabotage' in sys.argv
PERMS = list(permutations(range(3)))
IDX = {p: i for i, p in enumerate(PERMS)}
MUL = [[IDX[tuple(p[q[i]] for i in range(3))] for q in PERMS] for p in PERMS]
E = IDX[(0, 1, 2)]
INV = [next(j for j in range(6) if MUL[i][j] == E) for i in range(6)]
COST = [2 - (sum(1 for i in range(3) if p[i] == i) - 1) for p in PERMS]
TR = [i for i in range(6) if COST[i] == 2]
NL = 2 * LX * LY
def L(x, y, d):
    return 2 * ((x % LX) + LX * (y % LY)) + d
PL = [(L(x, y, 0), L(x + 1, y, 1), L(x, y + 1, 0), L(x, y, 1)) for y in range(LY) for x in range(LX)]
def total_m(u):
    s = 0
    for a, b, c, d in PL:
        s += COST[MUL[MUL[MUL[u[a]][u[b]]][INV[u[c]]]][INV[u[d]]]]
    return s
def loops(u):
    # Wilson lines around the two cycles from site (0,0), read from the links directly, so gauge invariance is tested and not assumed.
    hx = E
    for x in range(LX):
        hx = MUL[hx][u[L(x, 0, 0)]]
    hy = E
    for y in range(LY):
        hy = MUL[hy][u[L(0, y, 1)]]
    return hx, hy
def inv_class(hx, hy):
    # A complete invariant of a commuting pair up to conjugation: minimum over conjugates.
    return min((MUL[MUL[c][hx]][INV[c]], MUL[MUL[c][hy]][INV[c]]) for c in range(6))
rng = random.Random(9)
pairs = [(x, y) for x, y in product(range(6), range(6)) if MUL[x][y] == MUL[y][x]]
if SAB:
    pairs.append(next((x, y) for x, y in product(range(6), range(6)) if MUL[x][y] != MUL[y][x]))
classes = set()
flat_bad = move_bad = gauge_bad = 0
moves = 0
for hx, hy in pairs:
    u = [E] * NL
    for y in range(LY):
        u[L(LX - 1, y, 0)] = hx
    for x in range(LX):
        u[L(x, LY - 1, 1)] = hy
    if total_m(u) != 0:
        flat_bad += 1
    base = inv_class(*loops(u))
    classes.add(base)
    # A random gauge transformation keeps M and the class.
    for _ in range(4):
        h = [rng.randrange(6) for _ in range(LX * LY)]
        v = list(u)
        for y in range(LY):
            for x in range(LX):
                s = x % LX + LX * (y % LY)
                v[L(x, y, 0)] = MUL[MUL[h[s]][u[L(x, y, 0)]]][INV[h[(x + 1) % LX + LX * (y % LY)]]]
                v[L(x, y, 1)] = MUL[MUL[h[s]][u[L(x, y, 1)]]][INV[h[x % LX + LX * ((y + 1) % LY)]]]
        if total_m(v) != 0 and not SAB:
            gauge_bad += 1
        if inv_class(*loops(v)) != base:
            gauge_bad += 1
    for l in range(NL):
        keep = u[l]
        for s in TR:
            u[l] = MUL[s][keep]
            moves += 1
            if total_m(u) != 4:
                move_bad += 1
        u[l] = keep
ok = flat_bad == 0 and move_bad == 0 and gauge_bad == 0 and len(classes) == 8
print("FLATS|Lx=%d|Ly=%d|pairs=%d|classes=%d|moves=%d|moves_not_to_M4=%d|flat_bad=%d|gauge_bad=%d|sabotage=%d|verdict=%s|json=0" % (LX, LY, len(pairs), len(classes), moves, move_bad, flat_bad, gauge_bad, 1 if SAB else 0, 'PASS' if ok else 'FAIL'))
sys.exit(0 if ok else 1)
