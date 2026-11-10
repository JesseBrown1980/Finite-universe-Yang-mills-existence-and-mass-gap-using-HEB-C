#!/usr/bin/env python3
# FLOOR lane FIX-1: the REQUIRED independent gate on a written floorcert certificate file.
# Adopted from the critic's critic/class_verify.py (sha256 756b3a2590293c1a). Kept from it: own S3 law (a;b = "a then b"),
# right moves U_e -> U_e;tau, own BFS spanning tree rooted at (1,2), own canonical forms, own 48 lattice maps built from
# site maps, own per-link table (exhaustive over the 7 links of two plaquettes) and own colouring cap. Changed: every
# check is a GATE line and the run ends in one VERDICT|PASS or VERDICT|REFUSE|reasons=... line; the claimed cap and the
# row hash in the header are compared with this program's own recomputation; r is whitelisted; no plant flags; orbit
# keys are base-6 integers (same order as the critic's tuples) to fit m0 = 12 in memory.
# Integers only: no float, fractions, decimal, math module, true division or negative powers.
# Usage: python3 -I -B cert_gate.py CERT [--freeze-commit C --prediction FILE --prediction-sha256 H]   (r = 9: frozen only)
#        python3 -I -B cert_gate.py --rows-only KEYS_FILE M0       (r-independent row hash of a core_keys file)
import sys
import hashlib
from itertools import permutations, product

argv = sys.argv[1:]
def opt(name, default=None):
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default

REASONS = []
def gate(name, ok, detail=""):
    print("GATE|%s|%s|%s" % (name, "PASS" if ok else "FAIL", detail), flush=True)
    if not ok:
        REASONS.append("%s(%s)" % (name, detail))
    return ok
def refuse_now(name, detail):
    gate(name, False, detail)
    print("VERDICT|REFUSE|reasons=" + ";".join(REASONS), flush=True)
    sys.exit(1)

# ---------------------------------------------------------------- S3 and the lattice (critic conventions)
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
CONJ = [[MUL[MUL[INV[c]][a]][c] for a in range(6)] for c in range(6)]

LX, LY = 3, 4
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

def pcost(U, p):
    g = E
    for l, rev in PLAQ[p]:
        g = MUL[g][INV[U[l]] if rev else U[l]]
    return COST[g]
def magnetic(U):
    return sum(pcost(U, p) for p in range(12))

# own spanning tree: BFS from (1,2), neighbour order +y, -x, -y, +x
root = (1, 2)
tree = []
seen = {root}
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
    g = {root: E}
    for s, t in tree:
        l, rev = link_between(s, t)
        u = INV[U[l]] if rev else U[l]
        g[t] = MUL[INV[u]][g[s]]
    out = [0] * NL
    for l, (s, t) in enumerate(LINKS):
        out[l] = MUL[MUL[INV[g[s]]][U[l]]][g[t]]
    for l in TREE_L:
        assert out[l] == E
    return out
def code13(vals):  # base-6 code of 13 letters; the same order as the tuples
    k = 0
    for a in vals:
        k = k * 6 + a
    return k
def keys_of_tree_gauge(vals):
    return set(code13([CJ[a] for a in vals]) for CJ in CONJ)
def orbit_key_w(U):
    F = gauge_fix(U)
    ks = keys_of_tree_gauge([F[l] for l in FREE])
    return min(ks), len(ks)
def orbit_key(U):
    return orbit_key_w(U)[0]
def from_free(k):
    U = [E] * NL
    for i in range(12, -1, -1):
        U[FREE[i]] = k % 6
        k //= 6
    return U

SYMS = [(a, b, sx, sy) for a in range(LX) for b in range(LY) for sx in (1, -1) for sy in (1, -1)]
def transform(U, s):
    a, b, sx, sy = s
    out = [None] * NL
    for l, (p, q2) in enumerate(LINKS):
        l2, rev = link_between(((sx * p[0] + a) % LX, (sy * p[1] + b) % LY), ((sx * q2[0] + a) % LX, (sy * q2[1] + b) % LY))
        assert out[l2] is None
        out[l2] = INV[U[l]] if rev else U[l]
    return out

# engine (writer) key decoding: engine element p acts with product a.b = a o b; this law is a;b = b o a, so phi(p) = p^-1
ENG_P = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
def pinv(p):
    r = [0, 0, 0]
    for i in range(3):
        r[p[i]] = i
    return tuple(r)
ENG2MY = [IDX[pinv(p)] for p in ENG_P]
ENG_TREE = {12, 13, 14} | set(range(8))
ENG_KEPT = [k for k in range(24) if k not in ENG_TREE]
SIX13 = 6 ** 13
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

# ---------------------------------------------------------------- input: certificate or (rows-only) a core_keys file
rows_only = argv[:1] == ["--rows-only"]
if rows_only:
    keys_path, m0 = argv[1], int(argv[2])
    blob = open(keys_path, "rb").read()
    if len(blob) % 8:
        refuse_now("keys_file", "length not a multiple of 8")
    cert_rows = [(int.from_bytes(blob[i:i + 8], "little"), None, None) for i in range(0, len(blob), 8)]
    meta = {}
    print("ROWS_ONLY|keys=%s|m0=%d|classes=%d" % (keys_path, m0, len(cert_rows)), flush=True)
else:
    cert_path = argv[0]
    lines = open(cert_path).read().split("\n")
    hdr = lines[0]
    if not hdr.startswith("# floorcert certificate:"):
        refuse_now("header", "first line is not a floorcert certificate header")
    meta = dict(x.split("=", 1) for x in hdr.split() if "=" in x)
    for need in ("m0", "r", "t", "f", "cap", "rowhash"):
        if need not in meta:
            refuse_now("header", "missing field %s" % need)
    try:
        m0 = int(meta["m0"])
        rn, rd = map(int, meta["r"].split("/"))
        tn, td = map(int, meta["t"].split("/"))
        fvals = [int(x) for x in meta["f"].split(",")]
        capn_claim, capd_claim = map(int, meta["cap"].split("/"))
        cert_rows = [tuple(map(int, l.split())) for l in lines[1:] if l.strip() and not l.startswith("#")]
    except ValueError:
        refuse_now("header", "unparsable field or row")
    if not (rd > 0 and td > 0 and capd_claim > 0 and m0 >= 4 and fvals):
        refuse_now("header", "need r, t and cap denominators > 0, m0 >= 4 and a nonempty f")
    if any(len(x) != 3 for x in cert_rows):
        refuse_now("header", "a row is not 'key M v'")
    # prediction first: r in {21/2, 12, 14} or r >= 20; r = 9 only against the frozen binary's certificate
    excluded = 2 * rn == 21 * rd or rn == 12 * rd or rn == 14 * rd or rn >= 20 * rd
    if not excluded:
        if rn != 9 * rd:
            refuse_now("r_policy", "r=%d/%d not allowed: 21/2, 12, 14 and r >= 20 only (nothing within 1 of r = 9)" % (rn, rd))
        fc, pf, ph = opt("--freeze-commit", ""), opt("--prediction", ""), opt("--prediction-sha256", "")
        hexd = set("0123456789abcdef")
        if not (len(fc) == 40 and set(fc) <= hexd and len(ph) == 64 and set(ph) <= hexd):
            refuse_now("r9_frozen_mode", "r = 9 needs --freeze-commit (40 hex), --prediction FILE and --prediction-sha256 (64 hex)")
        try:
            got = hashlib.sha256(open(pf, "rb").read()).hexdigest()
        except OSError:
            refuse_now("r9_frozen_mode", "prediction file unreadable")
        if got != ph or meta.get("freeze") != fc or meta.get("pred") != ph:
            refuse_now("r9_frozen_mode", "prediction sha256, freeze commit and certificate header must agree")
        print("FREEZE|r=9|commit=%s|prediction_sha256=%s|verifier_sha256=%s" % (fc, ph, hashlib.sha256(open(__file__, "rb").read()).hexdigest()))
    gate("r_policy", True, "r=%d/%d%s" % (rn, rd, "" if excluded else " (frozen r = 9 mode)"))
    print("CERT|m0=%d|r=%d/%d|t=%d/%d|f=%s|claimed_cap=%d/%d|classes=%d" % (m0, rn, rd, tn, td, ",".join(map(str, fvals)), capn_claim, capd_claim, len(cert_rows)), flush=True)
def f_of(M):
    return fvals[min(M - m0, len(fvals)) - 1]

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
orbits = {}  # orbit key -> 8 M + w
U0 = [E] * NL
nleaf = [0]
def dfs(i, part):
    if i == 13:
        if part >= 1:
            vals = [U0[l] for l in FREE]
            ks = keys_of_tree_gauge(vals)
            k = min(ks)
            nleaf[0] += 1
            if nleaf[0] % 65536 == 1:  # U0 is in tree gauge: gauge_fix is the identity on it
                assert orbit_key_w(U0) == (k, len(ks))
            if k not in orbits:
                orbits[k] = 8 * part + len(ks)
        return
    l = FREE[i]
    for a in range(6):
        U0[l] = a
        p = part + sum(pcost(U0, pp) for pp in done_at[i])
        if p <= m0:
            dfs(i + 1, p)
    U0[l] = E
dfs(0, 0)
orb2cls = {}   # orbit key -> class index
cls_rep = []   # class index -> representative orbit key (minimum over the 48 images)
cls_M = []
cls_W = []     # class weight: sum of w over the distinct orbits of the class
for k, mw in orbits.items():
    if k in orb2cls:
        continue
    U = from_free(k)
    imgs = set(orbit_key(transform(U, s)) for s in SYMS)
    ci = len(cls_rep)
    for x in imgs:
        if orbits.get(x) != mw:
            refuse_now("own_enumeration", "a symmetry image leaves the core or changes (M, w)")
        orb2cls[x] = ci
    cls_rep.append(min(imgs))
    cls_M.append(mw // 8)
    cls_W.append((mw % 8) * len(imgs))
ncls = len(cls_rep)
print("ENUM|orbits=%d|classes=%d|weight=%d|tree_gauge_configurations=%d" % (len(orbits), ncls, sum(mw % 8 for mw in orbits.values()), nleaf[0]), flush=True)
del orbits

# ---------------------------------------------------------------- bijection certificate keys <-> own classes
cert_rows.sort()
cls2cert = [None] * ncls
vcls = [None] * ncls
bad = None
for i, (key, M, val) in enumerate(cert_rows):
    if i and cert_rows[i - 1][0] == key:
        bad = "duplicate key %d" % key
        break
    if not 0 <= key < SIX13:
        bad = "key %d out of range" % key
        break
    U = from_engine(key)
    Mown = magnetic(U)
    if M is not None and Mown != M:
        bad = "key %d: stated M=%d, decoded M=%d" % (key, M, Mown)
        break
    ci = orb2cls.get(orbit_key(U))
    if ci is None:
        bad = "key %d (M=%d) is not a nonflat core class of this enumeration" % (key, Mown)
        break
    if cls2cert[ci] is not None:
        bad = "keys %d and %d are the same class" % (cls2cert[ci], key)
        break
    cls2cert[ci] = key
    vcls[ci] = val
if bad is None and len(cert_rows) != ncls:
    bad = "%d certificate rows, %d own classes" % (len(cert_rows), ncls)
if bad is not None:
    refuse_now("class_bijection", bad)
gate("class_bijection", True, "%d classes" % ncls)
kh = hashlib.sha256()
for key, _, _ in cert_rows:
    kh.update(key.to_bytes(8, "little"))
keyshash = kh.hexdigest()
print("KEYSHASH|m0=%d|sha256=%s" % (m0, keyshash), flush=True)
if not rows_only and "keyshash" in meta:
    gate("keys_hash", meta["keyshash"] == keyshash, "header=%s own=%s" % (meta["keyshash"][:16], keyshash[:16]))

# ---------------------------------------------------------------- own per-link table, colouring cap, positivity
check = False
if not rows_only:
    fpos = gate("positivity_f", all(x >= 1 for x in fvals), "f=%s" % ",".join(map(str, fvals)))
    vmin = min(vcls)
    vpos = gate("positivity_v", vmin >= 1, "min v=%d" % vmin)
    check = fpos and vpos
    capok = False
    if fpos:
        def cls_of(c):
            return {0: "e", 2: "t", 3: "c"}[c]
        table = {}
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
                table.setdefault(tuple(sorted((cls_of(c1), cls_of(c2)))), set()).add(tuple(sorted(ds)))
        print("TABLE|" + "|".join("%s:%s" % ("".join(k), sorted(v_)) for k, v_ in sorted(table.items())))
        assert max(abs(d) for s in table.values() for ds in s for d in ds) == 4
        EDGES = [tuple(LP[l]) for l in range(NL)]
        memo = {}
        def gsum(M, pair):
            if (M, pair) not in memo:
                best = None
                for ds in table[pair]:
                    s = sum(f_of(M + d) for d in ds if M + d > m0)
                    best = s if best is None or s > best else best
                memo[(M, pair)] = best
            return memo[(M, pair)]
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
        print("TAILCAP|own=%d/%d" % cap, flush=True)
        gate("tail_cap_claim", capn_claim * cap[1] == cap[0] * capd_claim, "claimed %d/%d, own %d/%d" % (capn_claim, capd_claim, cap[0], cap[1]))
        capok = gate("t_below_tail_cap", tn * cap[1] < cap[0] * td, "t=%d/%d, own cap %d/%d" % (tn, td, cap[0], cap[1]))
    else:
        print("GATE|tail_cap_claim|SKIP|f not positive")
    if not check:
        print("GATE|row_check|SKIP|positivity failed")
    rdtd = rd * td

# ---------------------------------------------------------------- own rows at every class, canonical hash, row check
rh = hashlib.sha256()
nbytes = 0
def feed(s):
    global nbytes
    b = s.encode()
    rh.update(b)
    nbytes += len(b)
feed("floorcert-rows-v1 m0=%d\n" % m0)
order = sorted(range(ncls), key=lambda ci: cls2cert[ci])
ntail = 0
nback = 0
worst = None
nfail = 0
first_fail = None
nden = 0
num_ritz = 0
den_ritz = 0
for ci in order:
    k = cls_rep[ci]
    M = cls_M[ci]
    U = from_free(k)
    core = {}
    nflat = 0
    tails = []
    if check:
        vi = vcls[ci]
        lhs = (rdtd * 72 + td * rn * M - rd * tn) * vi
        rhs = 0
        rz = (72 * rd + rn * M) * vi
        row_den_bad = False
    pc = [pcost(U, p) for p in range(12)]
    for l in range(NL):
        old = U[l]
        p1, p2 = LP[l]
        for t in TAU:
            U[l] = MUL[old][t]
            m1 = M + pcost(U, p1) + pcost(U, p2) - pc[p1] - pc[p2]
            if m1 == 0:
                nflat += 1
            elif m1 <= m0:
                cj = orb2cls.get(orbit_key(U))
                if cj is None:
                    refuse_now("own_rows", "a core target is missing from the own enumeration")
                kk = cls2cert[cj]
                core[kk] = core.get(kk, 0) + 1
                if check:
                    lhs -= rdtd * vcls[cj]
                    rz -= rd * vcls[cj]
            else:
                pc1 = [pcost(U, p) for p in range(12)]
                hist = [0] * 9
                backs = []
                sf = 0
                sk = 0
                for l2 in range(NL):
                    o2 = U[l2]
                    q1, q2 = LP[l2]
                    for t2 in TAU:
                        U[l2] = MUL[o2][t2]
                        m2 = m1 + pcost(U, q1) + pcost(U, q2) - pc1[q1] - pc1[q2]
                        if m2 > m0:
                            hist[m2 - m1 + 4] += 1
                            if check:
                                sf += f_of(m2)
                        else:
                            if m2 < 1:
                                refuse_now("own_rows", "a tail orbit one move from a flat")
                            cj = orb2cls[orbit_key(U)]
                            backs.append(cls2cert[cj])
                            if check:
                                sk += vcls[cj]
                    U[l2] = o2
                backs.sort()
                tails.append(tuple([m1] + hist + backs))
                nback += len(backs)
                if check:
                    fk = f_of(m1)
                    N = td * rd * (72 * fk - sf) + td * rn * m1 * fk - rd * tn * fk
                    if N <= 0:
                        nden += 1
                        row_den_bad = True
                    else:
                        rhs += -(-(sk * rdtd * rdtd * fk) // N)
        U[l] = old
    ntail += len(tails)
    tails.sort()
    feed("C %d %d %d" % (cls2cert[ci], M, nflat) + "".join(" %d:%d" % (kk, c) for kk, c in sorted(core.items())) + "\n")
    for tl in tails:
        feed("T %d %s" % (tl[0], ",".join(str(x) for x in tl[1:10])) + "".join(" %d" % b for b in tl[10:]) + "\n")
    if check:
        slack = lhs - rhs
        if row_den_bad or slack < 0:
            nfail += 1
            if first_fail is None:
                first_fail = "key=%d|M=%d|%s" % (cls2cert[ci], M, "schur_denominator<=0" if row_den_bad else "slack=%d" % slack)
        elif worst is None or slack < worst:
            worst = slack
        num_ritz += cls_W[ci] * vi * rz
        den_ritz += cls_W[ci] * vi * vi * rd
feed("END %d %d %d\n" % (ncls, ntail, nback))
own_hash = rh.hexdigest()
print("ROWHASH|m0=%d|sha256=%s|classes=%d|tail_moves=%d|back_moves=%d|bytes=%d" % (m0, own_hash, ncls, ntail, nback, nbytes), flush=True)
try:
    print("MEM|" + "".join(l.split()[1] + "kB" for l in open("/proc/self/status") if l.startswith("VmHWM:")))
except OSError:
    pass
if rows_only:
    print("VERDICT|ROWS_ONLY|m0=%d|rowhash=%s|keyshash=%s" % (m0, own_hash, keyshash))
    sys.exit(0)
if check:
    if den_ritz:
        qz = num_ritz * 10 ** 6 // den_ritz
        print("RITZ_CLASS_VECTOR|%d.%06d|upper bound on lambda_min(QHQ) from the zero-extended class vector" % (qz // 10 ** 6, qz % 10 ** 6))
    gate("row_check", nfail == 0, ("rows=%d|min_slack=%d" % (ncls, worst)) if nfail == 0 else "failing_rows=%d|nonpositive_schur_denominators=%d|first=%s" % (nfail, nden, first_fail))
gate("row_hash", meta["rowhash"] == own_hash, "header=%s own=%s" % (meta["rowhash"][:16], own_hash[:16]))
if REASONS:
    print("VERDICT|REFUSE|reasons=" + ";".join(REASONS))
    sys.exit(1)
print("VERDICT|PASS|lambda_min(QHQ) >= %d/%d at r = %d/%d (m0 = %d)|rowhash=%s|min_slack=%d" % (tn, td, rn, rd, m0, own_hash, worst))
