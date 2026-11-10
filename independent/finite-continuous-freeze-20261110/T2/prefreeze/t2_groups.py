# t2_groups.py -- pre-freeze derivation check for T2 part (a). Integers only.
# Builds the ten finite subgroups of SU(2) by exact quaternion closure over Z[alpha]
# (alpha^2 = p*alpha + q), and derives: design strength t, iota = M_(t+1)^G - M_(t+1)^Haar,
# the Transfer coefficients, the class data used by the large-beta analysis, and the integer
# strong-coupling (Wronskian) series used by the small-beta analysis.
# Two independent routes for the invariant dimensions d_n: (1) group sum of Chebyshev
# characters, (2) Klein's invariant degrees (closed Molien formulas, NAMED). They must agree.
# No plaquette curve is evaluated here. Run: python3 -I -B t2_groups.py OUTDIR
import hashlib
import sys

N_MAX = 40          # d_n and M_n range
W_MAX = 30          # Wronskian series range


def igcd(a, b):
    a = -a if a < 0 else a
    b = -b if b < 0 else b
    while b:
        a, b = b, a % b
    return a


def rat(n, d):
    assert d != 0
    if d < 0:
        n, d = -n, -d
    g = igcd(n, d)
    return (n // g, d // g)


def rs(x):
    return str(x[0]) + ":" + str(x[1])


# ---------------------------------------------------------------- ring Z[alpha]
class Ring:
    def __init__(self, p, q, name):
        self.p, self.q, self.name = p, q, name

    def mul(self, x, y):
        a, b = x
        c, d = y
        bd = b * d
        return (a * c + bd * self.q, a * d + b * c + bd * self.p)

    def add(self, x, y):
        return (x[0] + y[0], x[1] + y[1])

    def sub(self, x, y):
        return (x[0] - y[0], x[1] - y[1])

    def half(self, x):
        assert x[0] % 2 == 0 and x[1] % 2 == 0, "not divisible by 2 in Z[alpha]"
        return (x[0] // 2, x[1] // 2)


Z0 = (0, 0)


def qmul(R, X, Y):
    # X, Y are 2*quaternion with coordinates in R; returns 2*(x*y) = X*Y/2
    a1, b1, c1, d1 = X
    a2, b2, c2, d2 = Y
    m = R.mul
    s = R.sub
    ad = R.add
    a = s(s(s(m(a1, a2), m(b1, b2)), m(c1, c2)), m(d1, d2))
    b = s(ad(ad(m(a1, b2), m(b1, a2)), m(c1, d2)), m(d1, c2))
    c = ad(ad(s(m(a1, c2), m(b1, d2)), m(c1, a2)), m(d1, b2))
    d = ad(s(ad(m(a1, d2), m(b1, c2)), m(c1, b2)), m(d1, a2))
    return (R.half(a), R.half(b), R.half(c), R.half(d))


def closure(R, gens):
    one = ((2, 0), Z0, Z0, Z0)
    seen = {one}
    frontier = [one]
    while frontier:
        nxt = []
        for x in frontier:
            for g in gens:
                y = qmul(R, x, g)
                if y not in seen:
                    seen.add(y)
                    nxt.append(y)
        frontier = nxt
        assert len(seen) <= 200
    return seen


def norm4(R, X):
    acc = Z0
    for c in X:
        acc = R.add(acc, R.mul(c, c))
    return acc


def order_of(R, X):
    one = ((2, 0), Z0, Z0, Z0)
    k = 1
    Y = X
    while Y != one:
        Y = qmul(R, Y, X)
        k += 1
        assert k <= 200
    return k


# ---------------------------------------------------------------- the ten groups
RZ = Ring(0, 2, "Z[sqrt2]")      # also used for integer-coordinate groups
R2 = Ring(0, 2, "Z[sqrt2]")
R3 = Ring(0, 3, "Z[sqrt3]")
RF = Ring(1, 1, "Z[phi]")

I_ = (Z0, (2, 0), Z0, Z0)
J_ = (Z0, Z0, (2, 0), Z0)
W_ = ((1, 0), (1, 0), (1, 0), (1, 0))

GROUPS = [
    # name, ring, generators, order, family, Klein degrees (q, r, p) of Molien (1+t^p)/((1-t^q)(1-t^r))
    ("Z3", R3, [((-1, 0), (0, 1), Z0, Z0)], 3, "cyclic", (2, 3, 3)),
    ("Z4", RZ, [(Z0, (2, 0), Z0, Z0)], 4, "cyclic", (2, 4, 4)),
    ("Z6", R3, [((1, 0), (0, 1), Z0, Z0)], 6, "cyclic", (2, 6, 6)),
    ("Dic2=Q8", RZ, [I_, J_], 8, "binary_dihedral", (4, 4, 6)),
    ("Dic3", R3, [((1, 0), (0, 1), Z0, Z0), J_], 12, "binary_dihedral", (4, 6, 8)),
    ("Dic4", R2, [((0, 1), (0, 1), Z0, Z0), J_], 16, "binary_dihedral", (4, 8, 10)),
    ("Dic6", R3, [((0, 1), (1, 0), Z0, Z0), J_], 24, "binary_dihedral", (4, 12, 14)),
    ("2T", RZ, [I_, W_], 24, "binary_tetrahedral", (6, 8, 12)),
    ("2O", R2, [I_, W_, ((0, 1), (0, 1), Z0, Z0)], 48, "binary_octahedral", (8, 12, 18)),
    ("2I", RF, [I_, W_, ((0, 1), (-1, 1), (1, 0), Z0)], 120, "binary_icosahedral", (12, 20, 30)),
]


def binom_table(n):
    C = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        C[i][0] = 1
        for j in range(1, i + 1):
            C[i][j] = C[i - 1][j - 1] + C[i - 1][j]
    return C


def series_mul(a, b, n):
    out = [0] * (n + 1)
    for i in range(n + 1):
        if a[i]:
            for j in range(n + 1 - i):
                out[i + j] += a[i] * b[j]
    return out


def molien_klein(q, r, p, n):
    num = [0] * (n + 1)
    num[0] = 1
    if p <= n:
        num[p] += 1
    gq = [1 if k % q == 0 else 0 for k in range(n + 1)]
    gr = [1 if k % r == 0 else 0 for k in range(n + 1)]
    return series_mul(series_mul(num, gq, n), gr, n)


def cg_mult(n_max):
    # m[n][k] = multiplicity of spin k/2 in (spin 1/2)^n
    m = [[0] * (n_max + 2) for _ in range(n_max + 1)]
    m[0][0] = 1
    for n in range(n_max):
        for k in range(n_max + 1):
            if m[n][k]:
                m[n + 1][k + 1] += m[n][k]
                if k > 0:
                    m[n + 1][k - 1] += m[n][k]
    return m


def catalan_moments(n_max):
    M = [0] * (n_max + 1)
    for n in range(0, n_max + 1, 2):
        k = n // 2
        c = 1
        for i in range(k):
            c = c * 2 * (2 * i + 1) // (i + 2)
        M[n] = c
    return M


def fact(n):
    f = 1
    for i in range(2, n + 1):
        f *= i
    return f


def main():
    outdir = sys.argv[1]
    rows = []
    checks = []
    MH = catalan_moments(N_MAX + 2)
    CG = cg_mult(N_MAX)
    # Haar moments by the CG route agree with Catalan
    for n in range(N_MAX + 1):
        checks.append(("haar_catalan_eq_cg_n%d" % n, MH[n] == CG[n][0]))
    rows.append("HAAR|M_0..%d=%s|rule=Catalan(n:2)_even_n|json=0" % (N_MAX, ",".join(str(x) for x in MH[:N_MAX + 1])))
    for (name, R, gens, order, fam, kd) in GROUPS:
        G = closure(R, gens)
        checks.append((name + "_order", len(G) == order))
        checks.append((name + "_unit_norm", all(norm4(R, X) == (4, 0) for X in G)))
        # trace tr g = X[0] (scaled real part), as an element of Z[alpha]
        tr = [X[0] for X in G]
        # moments
        M = []
        for n in range(N_MAX + 3):
            acc = Z0
            for x in tr:
                pw = (1, 0)
                for _ in range(n):
                    pw = R.mul(pw, x)
                acc = R.add(acc, pw)
            assert acc[1] == 0 and acc[0] % order == 0, (name, n, acc)
            M.append(acc[0] // order)
        # d_n by group sum of characters chi_(n/2) via Chebyshev recursion
        d_grp = [0] * (N_MAX + 1)
        alpha_parts = [0] * (N_MAX + 1)
        for x in tr:
            prev, cur = Z0, (1, 0)
            seq = [cur]
            for n in range(1, N_MAX + 1):
                nxt = R.sub(R.mul(x, cur), prev)
                prev, cur = cur, nxt
                seq.append(cur)
            for n in range(N_MAX + 1):
                d_grp[n] += seq[n][0]
                alpha_parts[n] += seq[n][1]
        checks.append((name + "_char_sums_rational", all(a == 0 for a in alpha_parts)))
        checks.append((name + "_char_sums_divisible", all(v % order == 0 for v in d_grp)))
        d_grp = [v // order for v in d_grp]
        q_, r_, p_ = kd
        d_kl = molien_klein(q_, r_, p_, N_MAX)
        checks.append((name + "_molien_group_eq_klein_d0..%d" % N_MAX, d_grp == d_kl))
        # moments from d_n via Clebsch-Gordan agree with the direct group moments
        M_cg = [sum(CG[n][k] * d_grp[k] for k in range(n + 1)) for n in range(N_MAX + 1)]
        checks.append((name + "_moments_eq_cg_of_d", M_cg == M[:N_MAX + 1]))
        # design strength
        t = None
        for n in range(1, N_MAX + 1):
            if d_grp[n] > 0:
                t = n - 1
                break
        iota = d_grp[t + 1]
        checks.append((name + "_moments_eq_haar_through_t", all(M[n] == MH[n] for n in range(t + 1))))
        checks.append((name + "_moment_defect_eq_iota", M[t + 1] - MH[t + 1] == iota))
        cz = rat(iota, pow(2, t + 1) * fact(t + 1))
        cp = rat(iota, pow(2, t + 1) * fact(t))
        # element orders and trace classes
        orders = {}
        for X in G:
            o = order_of(R, X)
            orders[o] = orders.get(o, 0) + 1
        classes = {}
        for x in tr:
            classes[x] = classes.get(x, 0) + 1
        defects = [str(n) + ":" + str(d_grp[n]) for n in range(1, N_MAX + 1) if d_grp[n] > 0]
        # class list: trace element (a,b) meaning a + b*alpha, multiplicity
        cl = sorted(classes.items())
        cls = ";".join("tr=(%d,%d)x%d" % (k[0], k[1], v) for k, v in cl)
        rows.append("GROUP|name=%s|family=%s|order=%d|ring=%s|alpha2=%d*alpha+%d|klein_degrees=%d,%d,%d|"
                    "t=%d|iota=%d|M_t+1_G=%d|M_t+1_Haar=%d|coef_logZ_per_plaquette=%s|coef_plaquette=%s|"
                    "orders=%s|trace_classes=%s|defect_degrees_n:d_n=%s|json=0" % (
                        name, fam, order, R.name, R.p, R.q, q_, r_, p_, t, iota, M[t + 1], MH[t + 1], rs(cz), rs(cp),
                        ",".join("%d:%d" % (k, orders[k]) for k in sorted(orders)), cls, ",".join(defects)))
        rows.append("MOMENTS|name=%s|M_0..%d=%s|json=0" % (name, N_MAX + 2, ",".join(str(x) for x in M)))
        rows.append("MOLIEN|name=%s|d_0..%d=%s|json=0" % (name, N_MAX, ",".join(str(x) for x in d_grp)))
        # integer EGF Wronskian series: delta = W(x)/D(x), x = beta/2,
        # W_n = sum_k C(n,k) (M^G_(k+1) M^H_(n-k) - M^G_k M^H_(n-k+1)), D_n = sum_k C(n,k) M^G_k M^H_(n-k+1)
        Cb = binom_table(W_MAX)
        Wn, Dn = [], []
        for n in range(W_MAX + 1):
            w = 0
            dd = 0
            for k in range(n + 1):
                w += Cb[n][k] * (M[k + 1] * MH[n - k] - M[k] * MH[n - k + 1])
                dd += Cb[n][k] * M[k] * MH[n - k + 1]
            Wn.append(w)
            Dn.append(dd)
        checks.append((name + "_W_zero_below_t", all(Wn[n] == 0 for n in range(t))))
        checks.append((name + "_W_t_eq_iota", Wn[t] == iota))
        checks.append((name + "_D0_0_D1_1", Dn[0] == 0 and Dn[1] == 1))
        rows.append("WRONSKIAN|name=%s|x=beta:2|delta=sum_n(W_n*x^n:n!):sum_n(D_n*x^n:n!)|W_0..%d=%s|D_0..%d=%s|json=0" % (
            name, W_MAX, ",".join(str(x) for x in Wn), W_MAX, ",".join(str(x) for x in Dn)))
    bad = [c for c, ok in checks if not ok]
    rows.append("CHECKS|n=%d|failed=%d|bad=%s|json=0" % (len(checks), len(bad), ",".join(bad) if bad else "none"))
    src = open(__file__, "rb").read()
    head = "T2_GROUPS_HEAD|script=t2_groups.py|script_sha256=%s|integer_only=1|plaquette_curves_evaluated=0|json=0" % hashlib.sha256(src).hexdigest()
    text = "\n".join([head] + rows) + "\n"
    with open(outdir + "/GROUPS.hbp", "w") as f:
        f.write(text)
    print("checks", len(checks), "failed", len(bad), bad)
    for r in rows:
        if r.startswith("GROUP|"):
            print(r[:400])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
