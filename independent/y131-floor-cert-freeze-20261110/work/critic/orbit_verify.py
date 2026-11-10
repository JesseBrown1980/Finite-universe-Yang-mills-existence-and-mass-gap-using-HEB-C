#!/usr/bin/env python3
# CRITIC lane (floor workflow): orbit-level independent check of a floorcert certificate (excluded r only).
# Own S3 law (a;b = "a then b"), right moves U_e -> U_e;tau, own BFS tree rooted at (1,2), own canonical forms, own
# 48 maps via site maps, own per-link table and colouring cap. Rows are checked at EVERY gauge orbit of the core, not
# only at class representatives. Integers only. Usage: python3 -I -B orbit_verify.py CERT [--t-override N] [--plant P]
import sys
from itertools import permutations, product

cert = sys.argv[1]
args = sys.argv[2:]
def opt(name, default=None):
    return args[args.index(name) + 1] if name in args else default

PERMS = sorted(permutations(range(3)))
IDX = {p: i for i, p in enumerate(PERMS)}
def seq(a, b):  # a then b: i -> b[a[i]]
    pa, pb = PERMS[a], PERMS[b]
    return IDX[tuple(pb[pa[i]] for i in range(3))]
MUL = [[seq(a, b) for b in range(6)] for a in range(6)]
E = IDX[(0, 1, 2)]
INV = [next(b for b in range(6) if MUL[a][b] == E) for a in range(6)]
TAU = [a for a in range(6) if a != E and MUL[a][a] == E]
assert len(TAU) == 3
COST = [3 - sum(1 for i in range(3) if PERMS[a][i] == i) for a in range(6)]  # e 0, t 2, c 3
assert sorted(COST) == [0, 2, 2, 2, 3, 3]

LX, LY = 3, 4
SITES = [(x, y) for x in range(LX) for y in range(LY)]
LINKS = []
for x in range(LX):
    for y in range(LY):
        LINKS.append(((x, y), ((x + 1) % LX, y)))
        LINKS.append(((x, y), (x, (y + 1) % LY)))
LID = {l: i for i, l in enumerate(LINKS)}
NL = len(LINKS)
def link_between(s, t):
    if (s, t) in LID:
        return LID[(s, t)], False
    return LID[(t, s)], True
PLAQ = []
for x in range(LX):
    for y in range(LY):
        a, b, c, d = (x, y), ((x + 1) % LX, y), ((x + 1) % LX, (y + 1) % LY), (x, (y + 1) % LY)
        PLAQ.append([link_between(a, b), link_between(b, c), link_between(c, d), link_between(d, a)])
LP = [[] for _ in range(NL)]
for p, ls in enumerate(PLAQ):
    for l, _ in ls:
        LP[l].append(p)
assert all(len(set(x)) == 2 and len(x) == 2 for x in LP)

def hol(U, p):
    g = E
    for l, rev in PLAQ[p]:
        g = MUL[g][INV[U[l]] if rev else U[l]]
    return g
def pcost(U, p):
    return COST[hol(U, p)]
def magnetic(U):
    return sum(pcost(U, p) for p in range(12))

# own spanning tree: BFS from (1,2), neighbour order +y, -x, -y, +x
root = (1, 2)
tree = []
seen = {root}
order = [root]
q = [root]
while q:
    s = q.pop(0)
    x, y = s
    for t in [(x, (y + 1) % LY), ((x - 1) % LX, y), (x, (y - 1) % LY), ((x + 1) % LX, y)]:
        if t not in seen:
            seen.add(t)
            q.append(t)
            tree.append((s, t))
assert len(tree) == 11
TREE_L = set(link_between(s, t)[0] for s, t in tree)
FREE = [l for l in range(NL) if l not in TREE_L]
assert len(FREE) == 13

def gauge_fix(U):
    # g_s^-1 ; U_l ; g_t = e on tree links (path products transform by conjugation)
    g = {root: E}
    for s, t in tree:
        l, rev = link_between(s, t)
        # value along s -> t
        u = INV[U[l]] if rev else U[l]
        g[t] = MUL[INV[u]][g[s]]
    out = [0] * NL
    for l, (s, t) in enumerate(LINKS):
        out[l] = MUL[MUL[INV[g[s]]][U[l]]][g[t]]
    for l in TREE_L:
        assert out[l] == E
    return out
def orbit_key_w(U):
    F = gauge_fix(U)
    keys = set()
    for c in range(6):
        ci = INV[c]
        keys.add(tuple(MUL[MUL[ci][F[l]]][c] for l in FREE))
    return min(keys), len(keys)
def orbit_key(U):
    return orbit_key_w(U)[0]

SYMS = [(a, b, sx, sy) for a in range(LX) for b in range(LY) for sx in (1, -1) for sy in (1, -1)]
def transform(U, s):
    a, b, sx, sy = s
    smap = lambda p: ((sx * p[0] + a) % LX, (sy * p[1] + b) % LY)
    out = [None] * NL
    for l, (p, q2) in enumerate(LINKS):
        l2, rev = link_between(smap(p), smap(q2))
        assert out[l2] is None
        out[l2] = INV[U[l]] if rev else U[l]
    return out

# ---------------------------------------------------------------- certificate
hdr = open(cert).readline().split()
meta = dict(x.split("=", 1) for x in hdr[3:])
m0 = int(meta["m0"]); rn, rd = map(int, meta["r"].split("/")); tn, td = map(int, meta["t"].split("/"))
fvals = [int(x) for x in meta["f"].split(",")]
if opt("--t-override"):
    tn = int(opt("--t-override"))
assert rn > 9 * rd, "excluded r only"
rows = [tuple(map(int, l.split())) for l in open(cert) if not l.startswith("#")]
def f_of(M):
    return fvals[min(M - m0, len(fvals)) - 1]
print("CERT|m0=%d|r=%d/%d|t=%d/%d|f=%s|classes=%d" % (m0, rn, rd, tn, td, fvals, len(rows)))

# engine key decoding: engine element p acts with product a.b = a o b; my law is a;b = b o a, so phi(p) = p^-1
ENG_P = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
def pinv(p):
    r = [0, 0, 0]
    for i in range(3):
        r[p[i]] = i
    return tuple(r)
ENG2MY = [IDX[pinv(p)] for p in ENG_P]
ENG_TREE = {12, 13, 14} | set(range(8))
ENG_KEPT = [k for k in range(24) if k not in ENG_TREE]
def from_engine(key):
    z = []
    for _ in range(13):
        z.append(key % 6)
        key //= 6
    z.reverse()
    U = [E] * NL
    for k, a in zip(ENG_KEPT, z):
        x, y = (k // 4, k % 4) if k < 12 else ((k - 12) // 4, (k - 12) % 4)
        l = LID[((x, y), ((x + 1) % LX, y))] if k < 12 else LID[((x, y), (x, (y + 1) % LY))]
        U[l] = ENG2MY[a]
    return U

# ---------------------------------------------------------------- own enumeration of every nonflat orbit with M <= m0
done_at = []
assigned = set(TREE_L)
pd = set()
for l in FREE:
    assigned.add(l)
    lev = [p for p in range(12) if p not in pd and all(x in assigned for x, _ in PLAQ[p])]
    pd.update(lev)
    done_at.append(lev)
assert len(pd) == 12
orbits = {}
U0 = [E] * NL
def dfs(i, part):
    if i == 13:
        if part >= 1:
            k, w = orbit_key_w(U0)
            if k not in orbits:
                orbits[k] = (list(U0), w, part)
        return
    l = FREE[i]
    for a in range(6):
        U0[l] = a
        p = part + sum(pcost(U0, pp) for pp in done_at[i])
        if p <= m0:
            dfs(i + 1, p)
    U0[l] = E
dfs(0, 0)
orb2cls = {}
for k, (U, w, M) in orbits.items():
    if k in orb2cls:
        continue
    imgs = [orbit_key(transform(U, s)) for s in SYMS]
    ck = min(imgs)
    for x in imgs:
        assert x in orbits
        assert orbits[x][1] == w and orbits[x][2] == M
        orb2cls[x] = ck
ncls = len(set(orb2cls.values()))
print("ENUM|orbits=%d|classes=%d|weight=%d" % (len(orbits), ncls, sum(w for _, w, _ in orbits.values())))
assert ncls == len(rows), "class count differs"

v = {}
for key, M, val in rows:
    U = from_engine(key)
    assert magnetic(U) == M, "decoded M differs"
    ck = orb2cls[orbit_key(U)]
    assert ck not in v
    v[ck] = val
assert set(v) == set(orb2cls.values())
print("GATE|class_bijection|PASS")
plant = opt("--plant", "none")

# ---------------------------------------------------------------- own per-link table and colouring cap
def cls_of(c):
    return {0: "e", 2: "t", 3: "c"}[c]
table = {}
for X in range(6):
    for Y in range(6):
        ds = []
        for t in TAU:
            # right move on a link that p traverses forwards at its end and q traverses backwards: compute on a real link
            ds.append(None)
        table.setdefault(tuple(sorted((cls_of(COST[X]), cls_of(COST[Y])))), set())
# derive the multiset from real configurations: for each link, each (X,Y) class pair realised, brute force
for l in range(NL):
    p1, p2 = LP[l]
    # random-free exhaustive: vary U_l and the other links of p1, p2 enough to realise every holonomy pair
    pass
# exhaustive per-link table over all values of the 7 links touching p1 and p2 (6^7 = 279936 per link); link 0 suffices
# by translation, and link 1 for the other orientation
for l in (LID[((0, 0), (1, 0))], LID[((0, 0), (0, 1))]):
    p1, p2 = LP[l]
    touch = sorted(set(x for x, _ in PLAQ[p1]) | set(x for x, _ in PLAQ[p2]))
    assert len(touch) == 7
    U = [E] * NL
    for vals in product(range(6), repeat=7):
        for x, a in zip(touch, vals):
            U[x] = a
        c1, c2 = pcost(U, p1), pcost(U, p2)
        old = U[l]
        ds = []
        for t in TAU:
            U[l] = MUL[old][t]
            ds.append(pcost(U, p1) + pcost(U, p2) - c1 - c2)
        U[l] = old
        table[tuple(sorted((cls_of(c1), cls_of(c2))))].add(tuple(sorted(ds)))
print("TABLE|" + "|".join("%s:%s" % ("".join(k), sorted(v_)) for k, v_ in sorted(table.items())))
assert max(abs(d) for s in table.values() for ds in s for d in ds) == 4
EDGES = [tuple(LP[l]) for l in range(NL)]
def gsum(M, pair):
    best = None
    for ds in table[pair]:
        s = sum(f_of(M + d) for d in ds if M + d > m0)
        best = s if best is None or s > best else best
    return best
CC = {"e": 0, "t": 2, "c": 3}
Gmax = {}
for col in product("etc", repeat=12):
    M = sum(CC[c] for c in col)
    if M <= m0:
        continue
    s = sum(gsum(M, tuple(sorted((col[a], col[b])))) for a, b in EDGES)
    if s > Gmax.get(M, -1):
        Gmax[M] = s
cap = None
for M, g in sorted(Gmax.items()):
    num, den = (72 * rd + rn * M) * f_of(M) - rd * g, rd * f_of(M)
    if cap is None or num * cap[1] < cap[0] * den:
        cap = (num, den)
print("TAILCAP|%d/%d" % cap)
if not tn * cap[1] < cap[0] * td:
    print("REFUSE|gate=tail_cap|t=%d/%d" % (tn, td))
    sys.exit(1)

# ---------------------------------------------------------------- rows at every orbit
rdtd = rd * td
worst = None
ntail = 0
num_ritz = 0
den_ritz = 0
db_fail = 0
cnt = {}
for k, (U, w, M) in orbits.items():
    U = list(U)
    vi = v[orb2cls[k]]
    lhs = (rdtd * 72 + td * rn * M - rd * tn) * vi
    rhs = 0
    rz = (72 * rd + rn * M) * vi
    pc = [pcost(U, p) for p in range(12)]
    for l in range(NL):
        old = U[l]
        p1, p2 = LP[l]
        for t in TAU:
            U[l] = MUL[old][t]
            m1 = M + pcost(U, p1) + pcost(U, p2) - pc[p1] - pc[p2]
            if m1 == 0:
                pass
            elif m1 <= m0:
                kj = orbit_key(U)
                vj = v[orb2cls[kj]]
                lhs -= rdtd * vj
                rz -= rd * vj
                cnt[(k, kj)] = cnt.get((k, kj), 0) + 1
            else:
                ntail += 1
                pc1 = [pcost(U, p) for p in range(12)]
                sf = 0
                sk = 0
                for l2 in range(NL):
                    o2 = U[l2]
                    q1, q2 = LP[l2]
                    for t2 in TAU:
                        U[l2] = MUL[o2][t2]
                        m2 = m1 + pcost(U, q1) + pcost(U, q2) - pc1[q1] - pc1[q2]
                        if m2 > m0:
                            sf += f_of(m2)
                        else:
                            assert m2 >= 1
                            sk += v[orb2cls[orbit_key(U)]]
                    U[l2] = o2
                fk = f_of(m1)
                if plant == "flip":
                    fk = fk
                N = td * rd * (72 * fk - sf) + td * rn * m1 * fk - rd * tn * fk
                if N <= 0:
                    print("REFUSE|gate=schur_denominator")
                    sys.exit(1)
                num = sk * rdtd * rdtd * fk
                rhs += -(-num // N)
        U[l] = old
    slack = lhs - rhs
    if slack < 0:
        print("REFUSE|gate=row_check_orbit|M=%d|slack=%d" % (M, slack))
        sys.exit(1)
    worst = slack if worst is None or slack < worst else worst
    num_ritz += w * vi * rz
    den_ritz += w * vi * vi * rd
# detailed balance at the orbit level on the core
for (a, b), c in cnt.items():
    if orbits[a][1] * c != orbits[b][1] * cnt.get((b, a), 0):
        db_fail += 1
print("GATE|orbit_detailed_balance|%s|edges=%d" % ("PASS" if db_fail == 0 else "FAIL(%d)" % db_fail, len(cnt)))
q = num_ritz * 10**6 // den_ritz
print("ROWS|orbits=%d|tail_moves=%d|min_slack=%d" % (len(orbits), ntail, worst))
print("RITZ_ORBIT_LEVEL|%d.%06d" % (q // 10**6, q % 10**6))
print("VERDICT|PASS|every orbit row|lambda_min(QHQ) >= %d/%d at r = %d/%d (m0 = %d)" % (tn, td, rn, rd, m0))
