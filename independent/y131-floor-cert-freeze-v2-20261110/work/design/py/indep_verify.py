#!/usr/bin/env python3
# Floor lane DESIGN: independent verifier of a floorcert certificate at a small core (m0 <= 7), excluded r only.
# Independent of the Rust code except for the key format (the engine's tree-gauge letter encoding), which is used only
# to read the certificate's class keys. Own S3, own link conventions, own spanning tree, own 48-symmetry action, own
# canonical form (24-letter tuple), full recomputation of M for every move, own colouring bound for the tail.
# Integers only. Usage: python3 -I -B indep_verify.py CERT_FILE [--plant none|vzero|tup|fneg]
# FIX-1: the 'capup' plant (a refusal triggered by the flag itself) is deleted; a claimed cap in the header is compared
# with the recomputed cap instead. r is whitelisted (21/2, 12, 14, r >= 20); r = 9 only against a frozen certificate.
# The REQUIRED gate for any quoted gamma is py/cert_gate.py (via gate_required.sh); this script is a second opinion.
import sys
import hashlib
from itertools import permutations, product

cert_path = sys.argv[1]
plant = sys.argv[sys.argv.index("--plant") + 1] if "--plant" in sys.argv else "none"

# ---------------------------------------------------------------- S3
EL = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]  # engine numbering, used to decode keys
def mul(a, b):
    return tuple(a[b[i]] for i in range(3))
def inv(a):
    r = [0, 0, 0]
    for i in range(3):
        r[a[i]] = i
    return tuple(r)
E_ = (0, 1, 2)
G = sorted(set(permutations(range(3))))
TR = [g for g in G if g != E_ and mul(g, g) == E_]
assert len(TR) == 3
def cost(g):
    return 2 - (sum(1 for i in range(3) if g[i] == i) - 1)
assert sorted(cost(g) for g in G) == [0, 2, 2, 2, 3, 3]

LX, LY = 3, 4
def H(x, y):
    return ("h", x % LX, y % LY)
def Vl(x, y):
    return ("v", x % LX, y % LY)
LINKS = [H(x, y) for x in range(LX) for y in range(LY)] + [Vl(x, y) for x in range(LX) for y in range(LY)]
def ends(l):
    t, x, y = l
    return ((x, y), ((x + 1) % LX, y)) if t == "h" else ((x, y), (x, (y + 1) % LY))
PLAQ = [((x, y), [(H(x, y), 1), (Vl(x + 1, y), 1), (H(x, y + 1), -1), (Vl(x, y), -1)]) for x in range(LX) for y in range(LY)]
def hol(U, links):
    g = E_
    for l, s in links:
        g = mul(g, U[l] if s == 1 else inv(U[l]))
    return g
def magnetic(U):
    return sum(cost(hol(U, ls)) for _, ls in PLAQ)

# ---------------------------------------------------------------- own tree (vertical links y=0..2 in every column, two horizontal at y=0)
TREE = [Vl(x, y) for x in range(LX) for y in range(LY - 1)] + [H(0, 0), H(1, 0)]
assert len(TREE) == 11
def gauge_fix(U):
    # want g_s U_l g_t^-1 = e on tree links, so g_t = g_s U_l
    g = {(0, 0): E_}
    changed = True
    while changed:
        changed = False
        for l in TREE:
            s, t = ends(l)
            if s in g and t not in g:
                g[t] = mul(g[s], U[l])
                changed = True
            elif t in g and s not in g:
                g[s] = mul(g[t], inv(U[l]))
                changed = True
    assert len(g) == LX * LY
    out = {}
    for l in LINKS:
        s, t = ends(l)
        out[l] = mul(mul(g[s], U[l]), inv(g[t]))
    for l in TREE:
        assert out[l] == E_
    return out
def orbit_key(U):
    F = gauge_fix(U)
    best = None
    for c in G:
        ci = inv(c)
        k = tuple(EL.index(mul(mul(c, F[l]), ci)) for l in LINKS)
        if best is None or k < best:
            best = k
    return best
def orbit_weight(U):
    F = gauge_fix(U)
    return len({tuple(mul(mul(c, F[l]), inv(c)) for l in LINKS) for c in G})

# ---------------------------------------------------------------- own 48 symmetries: translations x {1, Rx, Ry, RxRy}
def transform(U, a, b, rx, ry):
    out = {}
    for (t, x, y), g in U.items():
        if t == "h":
            if rx:
                l2 = H(-x - 1 + a, (-y if ry else y) + b)
                g2 = inv(g)
            else:
                l2 = H(x + a, (-y if ry else y) + b)
                g2 = g
        else:
            if ry:
                l2 = Vl((-x if rx else x) + a, -y - 1 + b)
                g2 = inv(g)
            else:
                l2 = Vl((-x if rx else x) + a, y + b)
                g2 = g
        out[l2] = g2
    assert len(out) == 24
    return out
SYMS = [(a, b, rx, ry) for a in range(LX) for b in range(LY) for rx in (0, 1) for ry in (0, 1)]
def class_key(U):
    return min(orbit_key(transform(U, *s)) for s in SYMS)
def class_size(U):
    return len({orbit_key(transform(U, *s)) for s in SYMS})

# ---------------------------------------------------------------- certificate
hdr = open(cert_path).readline().split()
meta = dict(x.split("=", 1) for x in hdr[3:])
m0 = int(meta["m0"]); rn, rd = map(int, meta["r"].split("/")); tn, td = map(int, meta["t"].split("/"))
fvals = [int(x) for x in meta["f"].split(",")]
assert rd > 0 and td > 0
if not (2 * rn == 21 * rd or rn == 12 * rd or rn == 14 * rd or rn >= 20 * rd):
    # prediction first: nothing within 1 of r = 9; r = 9 itself only against the frozen binary's certificate
    _a = sys.argv
    _o = lambda n: _a[_a.index(n) + 1] if n in _a and _a.index(n) + 1 < len(_a) else ""
    _fc, _pf, _ph = _o("--freeze-commit"), _o("--prediction"), _o("--prediction-sha256")
    _ok = rn == 9 * rd and len(_fc) == 40 and len(_ph) == 64 and meta.get("freeze") == _fc and meta.get("pred") == _ph
    if _ok:
        try:
            _ok = hashlib.sha256(open(_pf, "rb").read()).hexdigest() == _ph
        except OSError:
            _ok = False
    if not _ok:
        print("REFUSE|gate=r_policy|r=%d/%d|allowed: 21/2, 12, 14, r >= 20; r = 9 only with the freeze commit and prediction sha256" % (rn, rd))
        sys.exit(1)
assert m0 <= 7, "the independent verifier is for small cores"
rows_in = [tuple(map(int, l.split())) for l in open(cert_path) if not l.startswith("#")]
def f_of(M):
    a = M - m0
    assert a >= 1
    return fvals[min(a, len(fvals)) - 1]
if plant == "fneg":
    fvals[1 % len(fvals)] = -fvals[1 % len(fvals)]
if plant == "tup":
    tn += td
print("CERT|m0=%d|r=%d/%d|t=%d/%d|f=%s|classes=%d|plant=%s" % (m0, rn, rd, tn, td, fvals, len(rows_in), plant))

# engine key -> configuration (engine layout: link id 4x+y horizontal, 12+4x+y vertical; kept = non-tree of the engine tree)
ENG_TREE = {12 + 0, 12 + 1, 12 + 2} | {4 * x + y for x in range(2) for y in range(4)}
ENG_KEPT = [k for k in range(24) if k not in ENG_TREE]
def from_engine_key(key):
    z = []
    for _ in range(13):
        z.append(key % 6)
        key //= 6
    z.reverse()
    U = {l: E_ for l in LINKS}
    for k, a in zip(ENG_KEPT, z):
        l = H(k // 4, k % 4) if k < 12 else Vl((k - 12) // 4, (k - 12) % 4)
        U[l] = EL[a]
    return U

# ---------------------------------------------------------------- independent enumeration of every nonflat orbit with M <= m0
FREE = [l for l in LINKS if l not in TREE]
DONE_AT = []
_assigned = set(TREE)
_done = set()
for i, l in enumerate(FREE):
    _assigned.add(l)
    lev = []
    for pi, (_, ls) in enumerate(PLAQ):
        if pi not in _done and all(x in _assigned for x, _ in ls):
            _done.add(pi)
            lev.append(ls)
    DONE_AT.append(lev)
assert len(_done) == 12
orbits = {}
def dfs(i, U, part):
    if i == len(FREE):
        if part >= 1:
            k = orbit_key(U)
            if k not in orbits:
                orbits[k] = dict(U)
        return
    for g in G:
        U[FREE[i]] = g
        p = part + sum(cost(hol(U, ls)) for ls in DONE_AT[i])
        if p <= m0:
            dfs(i + 1, U, p)
    del U[FREE[i]]
dfs(0, {l: E_ for l in TREE}, 0)
for k, U in orbits.items():
    assert magnetic(U) <= m0
# classes, and a cache orbit key -> class key for every core orbit
classes = {}
orb2cls = {}
for k, U in orbits.items():
    if k in orb2cls:
        continue
    imgs = [orbit_key(transform(U, *s)) for s in SYMS]
    ck = min(imgs)
    for x in imgs:
        assert x in orbits, "a symmetry image left the core"
        orb2cls[x] = ck
    classes[ck] = U
assert set(orb2cls) == set(orbits)
def core_class(U):
    return orb2cls[orbit_key(U)]
print("ENUM|orbits=%d|classes=%d" % (len(orbits), len(classes)))
assert len(classes) == len(rows_in), "class count differs from the certificate"

# map certificate rows to independent classes, check M and the bijection
v = {}
for key, M, val in rows_in:
    U = from_engine_key(key)
    assert magnetic(U) == M
    ck = core_class(U)
    assert ck in classes, "certificate class not in the independent enumeration"
    assert ck not in v, "two certificate rows map to one class"
    v[ck] = val
assert set(v) == set(classes)
if plant == "vzero":
    v[min(v, key=lambda k: v[k])] = 0
print("GATE|class_bijection|PASS")

# ---------------------------------------------------------------- independent per-link move table and colouring bound
def link_deltas(X, Y):
    return sorted(cost(mul(t, X)) + cost(mul(t, Y)) - cost(X) - cost(Y) for t in TR)
CLS = {0: "e", 2: "t", 3: "c"}
table = {}
for X in G:
    for Y in G:
        key = tuple(sorted((CLS[cost(X)], CLS[cost(Y)])))
        table.setdefault(key, set()).add(tuple(link_deltas(X, Y)))
# dual adjacency: the two plaquettes of each link
plaq_of_link = {l: [] for l in LINKS}
for p, ls in PLAQ:
    for l, _ in ls:
        plaq_of_link[l].append(p)
assert all(len(set(x)) == 2 for x in plaq_of_link.values())
PIDX = {p: i for i, (p, _) in enumerate(PLAQ)}
EDGES = [tuple(PIDX[p] for p in plaq_of_link[l]) for l in LINKS]
def fsum_link(M, cls_pair):
    best = None
    for ds in table[cls_pair]:
        s = sum(f_of(M + d) for d in ds if M + d > m0)
        best = s if best is None or s > best else best
    return best
Gmax = {}
CC = {"e": 0, "t": 2, "c": 3}
for col in product("etc", repeat=12):
    M = sum(CC[c] for c in col)
    if M <= m0:
        continue
    s = sum(fsum_link(M, tuple(sorted((col[a], col[b])))) for a, b in EDGES)
    if s > Gmax.get(M, -1):
        Gmax[M] = s
# tail layer cap: min_M (72 + r M - G(M)/f(M)) as a fraction; require t below it
cap = None
for M, g in sorted(Gmax.items()):
    num, den = (72 * rd + rn * M) * f_of(M) - rd * g, rd * f_of(M)
    if cap is None or num * cap[1] < cap[0] * den:
        cap = (num, den)
print("TAILCAP|%d/%d" % cap)

# ---------------------------------------------------------------- rows from scratch and the exact check
def refuse(msg):
    print("REFUSE|" + msg)
    sys.exit(1)
for x in fvals:
    if x < 1:
        refuse("gate=positivity_f")
for ck, x in v.items():
    if x < 1:
        refuse("gate=positivity_v")
if not tn * cap[1] < cap[0] * td:
    refuse("gate=tail_layer_cap")
# a cap claimed in the header must equal the cap recomputed here from the colourings
if "cap" in meta:
    _cn, _cd = map(int, meta["cap"].split("/"))
    if _cn * cap[1] != cap[0] * _cd:
        refuse("gate=tail_cap_claim|claimed=%d/%d|recomputed=%d/%d" % (_cn, _cd, cap[0], cap[1]))
rdtd = rd * td
worst = None
ntails = 0
for ck, U in classes.items():
    M = magnetic(U)
    lhs = (rdtd * 72 + td * rn * M - rd * tn) * v[ck]
    rhs = 0
    nmoves = 0
    for l in LINKS:
        old = U[l]
        for t in TR:
            U[l] = mul(t, old)
            m1 = magnetic(U)
            nmoves += 1
            if m1 == 0:
                pass
            elif m1 <= m0:
                lhs -= rdtd * v[core_class(U)]
            else:
                # tail orbit: its floor delta_k = 72 + r m1 - sum_{tail moves} f/f_k, and its moves back into the core
                ntails += 1
                sf = 0
                sk = 0
                n2 = 0
                for l2 in LINKS:
                    o2 = U[l2]
                    for t2 in TR:
                        U[l2] = mul(t2, o2)
                        m2 = magnetic(U)
                        n2 += 1
                        if m2 > m0:
                            sf += f_of(m2)
                        else:
                            assert m2 >= 1
                            sk += v[core_class(U)]
                    U[l2] = o2
                assert n2 == 72
                fk = f_of(m1)
                N = td * rd * (72 * fk - sf) + td * rn * m1 * fk - rd * tn * fk
                if N <= 0:
                    refuse("gate=schur_denominator")
                num = sk * rdtd * rdtd * fk
                rhs += -(-num // N)
        U[l] = old
    assert nmoves == 72
    slack = lhs - rhs
    if slack < 0:
        refuse("gate=row_check|M=%d|slack=%d" % (M, slack))
    worst = slack if worst is None or slack < worst else worst
print("ROWS|classes=%d|tail_targets=%d|min_slack=%d" % (len(classes), ntails, worst))
print("VERDICT|PASS|lambda_min(QHQ) >= %d/%d at r = %d/%d (m0 = %d)" % (tn, td, rn, rd, m0))
