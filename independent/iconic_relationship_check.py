# The relationship between this repository's finite S3 theory and Iconic 3-space, checked exactly. json=0.
# The local Opus 5.5 seat, pid 8467a937cba309f7, November 9, 2026. Integer only; writes ICONIC-RELATIONSHIP-20261109.hbp
# and its .sha256 beside this file. Every check can fail, and two deliberately broken controls must fail.
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ICONIC-RELATIONSHIP-20261109.hbp")
ROWS = []
FAILED = []


def row(tag, *kv):
    ROWS.append(tag + "".join("|%s=%s" % (k, v) for k, v in kv) + "|json=0")


def check(name, ok, *kv):
    row("CHECK", ("name", name), ("status", "PASS" if ok else "FAIL"), *kv)
    if not ok:
        FAILED.append(name)


def control(name, broke):
    row("CONTROL", ("name", name), ("expected", "FAIL"), ("observed", "FAIL" if broke else "PASS"),
        ("status", "PASS" if broke else "FAIL"))
    if not broke:
        FAILED.append(name)


# ---- finite groups as permutation tuples -------------------------------------------------------------------------
def compose(p, q):
    return tuple(p[q[i]] for i in range(len(q)))


def inverse(p):
    r = [0] * len(p)
    for i, x in enumerate(p):
        r[x] = i
    return tuple(r)


def perms(n):
    if n == 1:
        return [(0,)]
    out = []
    for p in perms(n - 1):
        for pos in range(n):
            q = list(p)
            q.insert(pos, n - 1)
            out.append(tuple(q))
    return out


def conj_classes(G):
    seen, classes = set(), []
    for g in G:
        if g in seen:
            continue
        c = {compose(compose(h, g), inverse(h)) for h in G}
        seen |= c
        classes.append(sorted(c))
    return classes


def centralizer(G, g):
    return [h for h in G if compose(h, g) == compose(g, h)]


def commuting_pair_orbits(G, conj):
    pairs = [(a, b) for a in G for b in G if compose(a, b) == compose(b, a)]
    seen, orbits = set(), []
    for pr in pairs:
        if pr in seen:
            continue
        orb = {conj(h, pr) for h in G}
        seen |= orb
        orbits.append(orb)
    return pairs, orbits


def simultaneous(h, pr):
    a, b = pr
    hi = inverse(h)
    return (compose(compose(h, a), hi), compose(compose(h, b), hi))


def cycle_type(p):
    seen, lens = set(), []
    for i in range(len(p)):
        if i in seen:
            continue
        n, j = 0, i
        while j not in seen:
            seen.add(j)
            j = p[j]
            n += 1
        lens.append(n)
    return tuple(sorted(lens, reverse=True))


S3 = perms(3)
S4 = perms(4)
LABEL = {(1, 1, 1): "e", (2, 1): "t", (3,): "c"}

# 1. The eight flat sectors: commuting pairs (a, b) modulo simultaneous conjugation
pairs, orbits = commuting_pair_orbits(S3, simultaneous)
k_S3 = len(conj_classes(S3))
check("S3_commuting_pairs_equal_order_times_classes", len(pairs) == len(S3) * k_S3 == 18,
      ("commuting_pairs", len(pairs)), ("order", len(S3)), ("classes", k_S3))
check("S3_flat_sectors_are_8", len(orbits) == 8, ("orbits", len(orbits)))
labelled = []
for orb in orbits:
    a, b = min(orb)
    la, lb = LABEL[cycle_type(a)], LABEL[cycle_type(b)]
    if la == "c" and lb == "c":
        lb = "c" if b == a else "c^-1"
    labelled.append((la, lb, len(orb)))
labelled.sort()
row("FLAT_SECTORS", ("group", "S3"), ("sectors", ";".join("(%s,%s):w%d" % x for x in labelled)),
    ("weight_sum", sum(x[2] for x in labelled)))
want = sorted([("e", "e", 1), ("e", "t", 3), ("e", "c", 2), ("t", "e", 3), ("t", "t", 3), ("c", "e", 2), ("c", "c", 2), ("c", "c^-1", 2)])
check("S3_flat_sector_weights_match_this_repo", labelled == want,
      ("this_repo", "(e,e)w1,(e,t)w3,(e,c)w2,(t,e)w3,(t,t)w3,(c,e)w2,(c,c)w2,(c,c^-1)w2"))

# 2. The irreducible representations of the quantum double D(S3): one per (class, irrep of its centralizer)
dd_count, dd_dims = 0, []
irrep_dims = {6: [1, 1, 2], 2: [1, 1], 3: [1, 1, 1]}
for cl in conj_classes(S3):
    Z = centralizer(S3, cl[0])
    kz = len(conj_classes(Z))
    dims = irrep_dims[len(Z)]
    check("centralizer_irreps_consistent", len(dims) == kz and sum(d * d for d in dims) == len(Z),
          ("class", LABEL[cycle_type(cl[0])]), ("centralizer_order", len(Z)), ("centralizer_classes", kz))
    dd_count += kz
    dd_dims += [len(cl) * d for d in dims]
check("D_S3_irreps_are_8", dd_count == 8, ("irreps", dd_count), ("dims", ",".join(str(d) for d in sorted(dd_dims))))
check("D_S3_dimension_is_36", sum(d * d for d in dd_dims) == 36, ("sum_dim_squared", sum(d * d for d in dd_dims)))
check("flat_sectors_equal_D_S3_irreps", len(orbits) == dd_count, ("flat_sectors", len(orbits)), ("D_S3_irreps", dd_count))
# the same identity on S4, as a second instance
p4, o4 = commuting_pair_orbits(S4, simultaneous)
dd4 = sum(len(conj_classes(centralizer(S4, cl[0]))) for cl in conj_classes(S4))
check("S4_flat_sectors_equal_D_S4_irreps", len(o4) == dd4 == 21, ("orbits", len(o4)), ("D_S4_irreps", dd4))

# 3. S3 is the Weyl group of SU(3) inside the Weyl group of G2, acting on the Cartan plane by its 2-dim irrep
# G2 roots on the plane x+y+z=0, as coordinates on the lattice basis b1=(1,-1,0), b2=(0,1,-1)
def to3(c):
    return (c[0], c[1] - c[0], -c[1])


def dot3(u, v):
    return sum(u[i] * v[i] for i in range(3))


short = [(1, -1, 0), (1, 0, -1), (0, 1, -1)]
long_ = [(2, -1, -1), (-1, 2, -1), (-1, -1, 2)]
roots = short + [tuple(-x for x in r) for r in short] + long_ + [tuple(-x for x in r) for r in long_]
basis = [(1, 0), (0, 1)]


def reflect_plane(alpha, c):
    v = to3(c)
    num = 2 * dot3(v, alpha)
    den = dot3(alpha, alpha)
    assert num % den == 0
    k = num // den
    w = tuple(v[i] - k * alpha[i] for i in range(3))
    # back to lattice coordinates: w = c0*b1 + c1*b2 = (c0, c1-c0, -c1)
    assert w[0] + w[1] + w[2] == 0
    return (w[0], -w[2])


def mat_of(alpha):
    cols = [reflect_plane(alpha, b) for b in basis]
    return ((cols[0][0], cols[1][0]), (cols[0][1], cols[1][1]))


def mmul(A, B):
    return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(2)) for j in range(2)) for i in range(2))


def gen(gens):
    I = ((1, 0), (0, 1))
    grp, frontier = {I}, [I]
    while frontier:
        nxt = []
        for g in frontier:
            for s in gens:
                h = mmul(g, s)
                if h not in grp:
                    grp.add(h)
                    nxt.append(h)
        frontier = nxt
    return grp


W = gen([mat_of(r) for r in roots])
WL = gen([mat_of(r) for r in long_])
minusI = ((-1, 0), (0, -1))
check("W_G2_order_12", len(W) == 12, ("order", len(W)))
check("long_root_Weyl_group_order_6_nonabelian", len(WL) == 6 and any(mmul(a, b) != mmul(b, a) for a in WL for b in WL),
      ("order", len(WL)))
check("minus_I_in_W_G2_not_in_long_part", minusI in W and minusI not in WL)
check("W_G2_is_long_part_times_plus_minus_I", {mmul(a, s) for a in WL for s in (((1, 0), (0, 1)), minusI)} == W)
traces = sorted(a[0][0] + a[1][1] for a in WL)
check("long_part_acts_by_the_2dim_irrep_of_S3", traces == [-1, -1, 0, 0, 0, 2],
      ("traces_on_the_Cartan_plane", ",".join(str(t) for t in traces)), ("chi_std", "2,0,-1"),
      ("this_repo_magnetic_term", "2-chi_std(U_p)"))

# 4. S3 = D3 lifts to the binary dihedral group Dic_3 of order 12 inside SU(2); its moments against continuous SU(2)
# Z[w] with w = exp(2 pi i/3): pairs (a, b) = a + b w, w^2 = -1 - w; zeta = exp(i pi/3) = 1 + w; conj(zeta) = -w
def zm(x, y):
    a, b = x
    c, d = y
    return (a * c - b * d, a * d + b * c - b * d)


def za(x, y):
    return (x[0] + y[0], x[1] + y[1])


def zconj(x):
    return (x[0] - x[1], -x[1])


Z0, Z1 = (0, 0), (1, 0)
NEG1 = (-1, 0)


def m2(A, B):
    return tuple(tuple(za(zm(A[i][0], B[0][j]), zm(A[i][1], B[1][j])) for j in range(2)) for i in range(2))


x = (((1, 1), Z0), (Z0, (0, -1)))
y = ((Z0, Z1), (NEG1, Z0))
I2 = ((Z1, Z0), (Z0, Z1))
Dic = {I2}
front = [I2]
while front:
    nxt = []
    for g in front:
        for s in (x, y):
            h = m2(g, s)
            if h not in Dic:
                Dic.add(h)
                nxt.append(h)
    front = nxt


def det2(A):
    p = zm(A[0][0], A[1][1])
    q = zm(A[0][1], A[1][0])
    return (p[0] - q[0], p[1] - q[1])


def dagger(A):
    return tuple(tuple(zconj(A[j][i]) for j in range(2)) for i in range(2))


check("Dic3_order_12", len(Dic) == 12, ("order", len(Dic)))
check("Dic3_in_SU2", all(det2(g) == Z1 and m2(g, dagger(g)) == I2 for g in Dic))
tr = []
for g in Dic:
    t = za(g[0][0], g[1][1])
    check("Dic3_trace_is_an_integer", t[1] == 0, ("trace", "%d+%dw" % t)) if t[1] != 0 else None
    tr.append(t[0])
center = [g for g in Dic if all(m2(g, h) == m2(h, g) for h in Dic)]
check("Dic3_center_is_plus_minus_1", len(center) == 2)
quot_nonabelian = any(m2(m2(a, b), dagger(m2(b, a))) not in center for a in Dic for b in Dic)
check("Dic3_mod_center_is_S3", len(Dic) // len(center) == 6 and quot_nonabelian,
      ("quotient_order", len(Dic) // len(center)), ("nonabelian", int(quot_nonabelian)))


def catalan(m):
    c = 1
    for i in range(m):
        c = c * 2 * (2 * i + 1)
        assert c % (i + 2) == 0
        c = c // (i + 2)
    return c


moments = []
first_break = None
for n in range(0, 13):
    s = 0
    for t in tr:
        p = 1
        for _ in range(n):
            p *= t
        s += p
    assert s % 12 == 0
    M = s // 12
    Mh = catalan(n // 2) if n % 2 == 0 else 0
    moments.append("%d:%d:%d" % (n, M, Mh))
    if first_break is None and M != Mh:
        first_break = (n, M, Mh)
row("DIC3_MOMENTS", ("rows", "n:M_n(Dic3):M_n(SU2_Haar)"), ("values", ",".join(moments)))
check("Dic3_first_break_degree_4_moment_3_against_2", first_break == (4, 3, 2),
      ("first_break_degree", first_break[0]), ("M_Dic3", first_break[1]), ("M_SU2", first_break[2]))
row("ICONIC_FROZEN_PREDICTION", ("repo", "JesseBrown1980/Iconic-3-space"), ("commit", "eb18a5a"),
    ("file", "predictions/su2-ladder/PREDICTION.hbp"),
    ("sha256", "c2601cf08d7c662422e7284cc123250c27cf4943766d4d41baa43b63e3b8c865"),
    ("Dic_3", "t_pred=3,first_break_degree=4,M_4=3,Mh_4=2"),
    ("agree_with_this_measurement", int(first_break == (4, 3, 2))))

# 5. Controls that must fail
bad_pairs, bad_orbits = commuting_pair_orbits(S3, lambda h, pr: (compose(h, pr[0]), compose(h, pr[1])))
control("wrong_conjugation_breaks_the_sector_count", len(bad_orbits) != 8)
bad_y = ((Z0, Z1), (Z1, Z0))
bad = {I2}
front = [I2]
while front and len(bad) < 200:
    nxt = []
    for g in front:
        for s in (x, bad_y):
            h = m2(g, s)
            if h not in bad:
                bad.add(h)
                nxt.append(h)
    front = nxt
control("wrong_dihedral_generator_leaves_SU2_or_changes_the_order", len(bad) != 12 or not all(det2(g) == Z1 for g in bad))

src = open(os.path.abspath(__file__), "rb").read()
head = ("ICONIC_RELATIONSHIP|date=2026-11-09|by=the local Opus 5.5 seat, pid 8467a937cba309f7|script_sha256=%s"
        "|evidence_class=structural_identities_measured|scope=finite_groups_and_their_counts;a_statement_about_a_continuous_gauge_group_needs_a_proven_transfer(status_OPEN)|json=0"
        % hashlib.sha256(src).hexdigest())
ROWS.insert(0, head)
ROWS.append("END|checks_failed=%d|status=%s|json=0" % (len(FAILED), "ALL_PASS" if not FAILED else "FAIL:" + ",".join(FAILED)))
data = ("\n".join(ROWS) + "\n").encode("utf-8")
with open(OUT, "wb") as fh:
    fh.write(data)
with open(OUT + ".sha256", "wb") as fh:
    fh.write(("%s  %s\n" % (hashlib.sha256(data).hexdigest(), os.path.basename(OUT))).encode("utf-8"))
sys.stdout.write(ROWS[-1] + "\n")
sys.exit(1 if FAILED else 0)
