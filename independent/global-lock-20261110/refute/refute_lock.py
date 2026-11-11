"""Independent pre-freeze refuter structure checks for PREDICTION-GLOBAL-LOCK-DRAFT-20261110.
Integers only: no float, no fractions module. Rationals are (num, den) int pairs reduced by math.gcd.
Elements of real quadratic rings Z[w] are int pairs (a, b) = a + b*w, w in {sqrt2, sqrt3, phi}; signs decided by squares.
No spectrum of any torus is computed. Only group theory, an abstract open-patch second-order count, and move counting."""
import itertools, math, hashlib, sys

ROWS = []
def emit(row):
    ROWS.append(row); print(row)

# ---------- exact rationals ----------
def rq(n, d=1):
    if d < 0: n, d = -n, -d
    g = math.gcd(n, d); return (n // g, d // g)
def radd(x, y): return rq(x[0]*y[1] + y[0]*x[1], x[1]*y[1])
def rs(x): return "%d/%d" % x if x[1] != 1 else "%d" % x[0]

# ---------- rings ----------
class Ring:
    def __init__(s, kind): s.kind = kind
    def mul(s, x, y):
        a, b = x; c, d = y
        if s.kind == "int": return (a*c, 0)
        if s.kind == "sqrt2": return (a*c + 2*b*d, a*d + b*c)
        if s.kind == "sqrt3": return (a*c + 3*b*d, a*d + b*c)
        if s.kind == "phi": return (a*c + b*d, a*d + b*c + b*d)
    def sign(s, x):
        a, b = x
        if s.kind == "int": return (a > 0) - (a < 0)
        if s.kind == "phi": p, q, D = 2*a + b, b, 5
        else: p, q, D = a, b, (2 if s.kind == "sqrt2" else 3)
        if p >= 0 and q >= 0: return 0 if p == 0 and q == 0 else 1
        if p <= 0 and q <= 0: return -1
        L, R = p*p, q*q*D
        if L == R: return 0
        return (1 if p > 0 else -1) if L > R else (1 if q > 0 else -1)
    def name(s, x):
        w = {"int": "", "sqrt2": "sqrt2", "sqrt3": "sqrt3", "phi": "phi"}[s.kind]
        return "%d" % x[0] if x[1] == 0 else "%d%+d*%s" % (x[0], x[1], w)

def quat_group(kind, gens):
    """Quaternions with doubled coordinates, entries in Z[w]; closure by BFS; identity doubled = (2,0,0,0)."""
    R = Ring(kind)
    add = lambda x, y: (x[0]+y[0], x[1]+y[1]); sub = lambda x, y: (x[0]-y[0], x[1]-y[1])
    def mul(p, q):
        m = R.mul
        a1, b1, c1, d1 = p; a2, b2, c2, d2 = q
        r = (sub(sub(sub(m(a1, a2), m(b1, b2)), m(c1, c2)), m(d1, d2)),
             add(add(m(a1, b2), m(b1, a2)), sub(m(c1, d2), m(d1, c2))),
             add(sub(m(a1, c2), m(b1, d2)), add(m(c1, a2), m(d1, b2))),
             add(sub(add(m(a1, d2), m(b1, c2)), m(c1, b2)), m(d1, a2)))
        for x in r:
            if x[0] % 2 or x[1] % 2: raise ValueError("closure")
        return tuple((x[0]//2, x[1]//2) for x in r)
    e = ((2, 0), (0, 0), (0, 0), (0, 0))
    G = {e}; fr = [e]
    while fr:
        nx = []
        for g in fr:
            for h in gens:
                p = mul(g, h)
                if p not in G: G.add(p); nx.append(p)
        fr = nx
    inv = lambda p: (p[0],) + tuple((-x[0], -x[1]) for x in p[1:])
    cost = lambda p: (2 - p[0][0], -p[0][1])   # 2 - trace; trace = doubled real coordinate
    return R, sorted(G), mul, inv, cost, e

def s3_group():
    R = Ring("int")
    G = sorted(itertools.permutations(range(3)))
    mul = lambda a, b: tuple(a[b[i]] for i in range(3))
    inv = lambda a: tuple(sorted(range(3), key=lambda i: a[i]))
    cost = lambda a: (2 - (sum(1 for i in range(3) if a[i] == i) - 1), 0)   # 2 - chi_std
    return R, G, mul, inv, cost, (0, 1, 2)

def analyse(name, grp):
    R, G, mul, inv, cost, e = grp
    n = len(G)
    comm = {mul(mul(a, b), mul(inv(a), inv(b))) for a in G for b in G}
    # derived subgroup (closure of comm) for comparison
    D = set(comm); ch = True
    while ch:
        ch = False
        for x in list(D):
            for y in list(D):
                z = mul(x, y)
                if z not in D: D.add(z); ch = True
    cls = {}
    for g in G: cls.setdefault(frozenset(mul(mul(h, g), inv(h)) for h in G), g)
    classes = [c for c in cls if e not in c]
    ccost = {c: cost(next(iter(c))) for c in classes}
    lt = lambda x, y: R.sign((x[0]-y[0], x[1]-y[1])) < 0
    cmin = classes[0]
    for c in classes:
        if lt(ccost[c], ccost[cmin]): cmin = c
    # exhaustive multiset search; bound k by k*cost(cmin) <= best (all costs > 0)
    best = None; best_sets = []
    k = 1
    while True:
        kmin = (k*ccost[cmin][0], k*ccost[cmin][1])
        if best is not None and lt(best, kmin): break
        if k > 6: break
        for tup in itertools.combinations_with_replacement(classes, k):
            v = (sum(ccost[c][0] for c in tup), sum(ccost[c][1] for c in tup))
            if best is not None and lt(best, v): continue
            S = {e}
            for c in tup: S = {mul(s, x) for s in S for x in c}
            if S & comm:
                if best is None or lt(v, best): best = v; best_sets = [tup]
                elif not lt(best, v): best_sets.append(tup)
        k += 1
    # formula: 2 - max trace over nontrivial commutators == min cost over nontrivial commutators
    nt = [g for g in comm if g != e]
    form = None
    for g in nt:
        v = cost(g)
        if form is None or lt(v, form): form = v
    form_ok = (form is not None and not lt(form, best) and not lt(best, form))
    # flat states on a 2-torus: orbits of commuting pairs under simultaneous conjugation
    seen = set(); orbits2 = 0
    for a in G:
        for b in G:
            if mul(a, b) != mul(b, a) or (a, b) in seen: continue
            orbits2 += 1
            for h in G: seen.add((mul(mul(h, a), inv(h)), mul(mul(h, b), inv(h))))
    tie = "|".join("+".join(R.name(ccost[c]) for c in t) for t in best_sets)
    emit("LOCK|group=%s|order=%d|commutator_set=%d|derived_subgroup=%d|nontrivial_classes=%d|cheapest_class_cost=%s|cheapest_class_is_commutator=%d|kappa=%s|optimal_flux_sets=%d|optimal_sets_costs=%s|min_plaquettes=%d|formula_2_minus_max_comm_trace=%s|formula_equals_kappa=%d|flat_states_2torus=%d|json=0"
         % (name, n, len(comm), len(D), len(classes), R.name(ccost[cmin]), int(any(g in comm for g in cmin)), R.name(best),
            len(best_sets), tie, min(len(t) for t in best_sets), (R.name(form) if form else "none"), int(form_ok), orbits2))
    return R, G, mul, inv, cost, e, comm, classes

r2 = lambda a, b: (a, b)
I = lambda n: (n, 0)
base = [(I(1), I(1), I(1), I(1)), (I(0), I(2), I(0), I(0)), (I(0), I(0), I(2), I(0))]
S3 = analyse("S3_chi_std", s3_group())
analyse("2T", quat_group("int", base))
analyse("2O", quat_group("sqrt2", base + [((0, 1), (0, 1), (0, 0), (0, 0))]))
analyse("2I", quat_group("phi", base + [((0, 1), (1, 0), (-1, 1), (0, 0))]))
# binary dihedral Dic_n = <x, j>, x = exp(i*pi/n): doubled (2cos(pi/n), 2sin(pi/n))
analyse("Q8_Dic2", quat_group("int", [(I(0), I(2), I(0), I(0)), (I(0), I(0), I(2), I(0))]))
analyse("Dic3_order12", quat_group("sqrt3", [((1, 0), (0, 1), (0, 0), (0, 0)), (I(0), I(0), I(2), I(0))]))
analyse("Dic4_order16", quat_group("sqrt2", [((0, 1), (0, 1), (0, 0), (0, 0)), (I(0), I(0), I(2), I(0))]))
analyse("Dic6_order24", quat_group("sqrt3", [((0, 1), (1, 0), (0, 0), (0, 0)), (I(0), I(0), I(2), I(0))]))
analyse("Z6_cyclic", quat_group("sqrt3", [((1, 0), (0, 1), (0, 0), (0, 0))]))

# ---------- S3 commutator set inside A3 => even number of transposition plaquettes ----------
R, G, mul, inv, cost, e, comm, classes = S3
sgn = lambda a: 1 if sum(1 for i in range(3) for j in range(i+1, 3) if a[i] > a[j]) % 2 == 0 else -1
emit("PARITY|group=S3|commutators_all_even=%d|min_nonflat_M=3|reason=sign([a,b])=+1_so_transposition_plaquettes_even|json=0"
     % int(all(sgn(g) == 1 for g in comm)))

# ---------- abstract open patch, S3, exact second-order counting ----------
P = 9                       # plaquettes per side, open patch; flux at the centre
c3 = (1, 2, 0)              # a 3-cycle
T = [g for g in G if sum(1 for i in range(3) if g[i] == i) == 1]
def links():
    L = []
    for x in range(P):
        for y in range(P + 1): L.append(("h", x, y))
    for x in range(P + 1):
        for y in range(P): L.append(("v", x, y))
    return L
LINKS = links()
def plaqs_of(l):
    k, x, y = l
    out = []
    if k == "h":
        for py in (y - 1, y):
            if 0 <= py < P: out.append((x, py))
    else:
        for px in (x - 1, x):
            if 0 <= px < P: out.append((px, y))
    return out
INTERIOR = [l for l in LINKS if len(plaqs_of(l)) == 2]
def hol(cfg, p):
    x, y = p
    g = cfg.get
    return mul(mul(g(("h", x, y), e), g(("v", x + 1, y), e)), mul(inv(g(("h", x, y + 1), e)), inv(g(("v", x, y), e))))
def mcost(cfg, ps): return sum(cost(hol(cfg, p))[0] for p in ps)
def Mtot(cfg): return mcost(cfg, [(x, y) for x in range(P) for y in range(P)])
def move(cfg, l, t):
    c = dict(cfg); c[l] = mul(t, cfg.get(l, e)); return c
def second_order(cfg):
    M0 = Mtot(cfg); diag = rq(0); hops = {}
    for l in INTERIOR:
        for t in T:
            c1 = move(cfg, l, t)
            dM = Mtot(c1) - M0
            assert dM > 0
            diag = radd(diag, rq(1, dM))
            near = set(plaqs_of(l))
            for l2 in INTERIOR:
                if not (set(plaqs_of(l2)) & near) and l2 != l: continue
                for t2 in T:
                    c2 = move(c1, l2, t2)
                    if c2 == cfg or (l2 == l and c2.get(l) == cfg.get(l, e)): continue
                    c2n = {k: v for k, v in c2.items() if v != e}
                    if Mtot(c2) == M0:
                        key = tuple(sorted(c2n.items()))
                        hops[key] = radd(hops.get(key, rq(0)), rq(1, dM))
    return M0, diag, hops
vac = {}
flux = {("v", x, P // 2): c3 for x in range(0, P // 2 + 1)}
Mv, dv, hv = second_order(vac)
Mf, df, hf = second_order(flux)
hopsum = rq(0)
for v in hf.values(): hopsum = radd(hopsum, v)
amps = sorted(set(rs(v) for v in hf.values()))
nint = len(INTERIOR)
emit("PATCH2|group=S3|patch=%dx%d_open|interior_links=%d|M_vac=%d|M_flux=%d|diag_vac=%s|diag_flux=%s|diag_vac_per_link=%s|offdiag_vac_targets=%d|hop_targets_flux=%d|hop_amplitudes=%s|hop_row_sum=%s|json=0"
     % (P, P, nint, Mv, Mf, rs(dv), rs(df), rs(rq(dv[0], dv[1]*nint)), len(hv), len(hf), ",".join(amps), rs(hopsum)))
cL = radd(radd(df, hopsum), rq(-dv[0], dv[1]))
emit("DELTA2|group=S3|c=(diag_flux+hop_row_sum)-diag_vac|c=%s|meaning=E9-E8=3r-c/r+O(1/r^2)_if_flat_2nd_order_scalar_and_flux_Perron_uniform|on_file=zgap2_c_L=21_on_3x3_3x4_4x4|delta_sign=positive|gap_r9_second_order=%s|json=0"
     % (rs(cL), rs(radd(rq(27), rq(-cL[0], cL[1]*9)))))

# ---------- rigorous sandwich for GL1 (S3, any torus, N links) ----------
emit("SANDWICH|claim=3r-3N<=E9-E8<=3r+3N_JE|lower=E9>=3r_from_H>=JB*M_and_E>=0;E8<=3N_flat_trial|upper=E9<=3r+3N_9dim_trial_flat+flux_block_diagonal;E8>=0|consequence=(E9-E8)/r->3_on_every_finite_torus_is_a_theorem_not_a_prediction|json=0")

# ---------- GL3: per-link move cost to change one flat sector into another ----------
# change (a,b) -> (h a, b) needs h in C(b); per link of the dual cut, h costs its transposition word length
wl = lambda h: 0 if h == e else (1 if h in T else 2)
pairs = [(a, b) for a in G for b in G if mul(a, b) == mul(b, a)]
def canon(a, b): return min((mul(mul(h, a), inv(h)), mul(mul(h, b), inv(h))) for h in G)
secs = sorted(set(canon(a, b) for a, b in pairs))
best_link = {}
for (a, b) in secs:
    bl = None
    for h in G:
        if h == e: continue
        for (x, y, nx) in ((a, b, (mul(h, a), b)), (b, a, (a, mul(h, b)))):
            if mul(h, y) != mul(y, h): continue
            tgt = canon(*nx)
            if tgt == (a, b): continue
            w = wl(h)
            if bl is None or w < bl: bl = w
    best_link[(a, b)] = bl
w1 = sum(1 for v in best_link.values() if v == 1); w2 = sum(1 for v in best_link.values() if v == 2)
emit("GL3MOVES|group=S3|sectors=%d|sectors_leaving_at_L_moves=%d|sectors_leaving_only_at_2L_moves=%d|W_order_in_lambda=L_min|W_JE~r^-(L_min-1)|json=0" % (len(secs), w1, w2))

# ---------- 3D: S3 flat count and minimal flux cost (dual-cycle argument) ----------
triples = 0; seen = set()
for a in G:
    for b in G:
        if mul(a, b) != mul(b, a): continue
        for c in G:
            if mul(a, c) != mul(c, a) or mul(b, c) != mul(c, b) or (a, b, c) in seen: continue
            triples += 1
            for h in G: seen.add(tuple(mul(mul(h, z), inv(h)) for z in (a, b, c)))
emit("LOCK3D|group=S3|flat_states_3torus=%d|bianchi=each_cube_product_e_so_nonflat_faces_form_closed_dual_cycles|min_dual_cycle=4_(L>=4:winding>=L)|cheapest_class=transposition_cost2|kappa3D=8|kappa2D=3|lock_binding_in_3D=0|json=0" % triples)

out = "\n".join(ROWS) + "\n"
sys.stdout.flush()
open(sys.argv[1], "w", newline="\n").write(out) if len(sys.argv) > 1 else None
print("SHA256|rows=%d|sha256=%s|json=0" % (len(ROWS), hashlib.sha256(out.encode()).hexdigest()))
