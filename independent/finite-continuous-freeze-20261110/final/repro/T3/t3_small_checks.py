# T3 pre-freeze small checks. Integer arithmetic only (no float, fractions, decimal, math).
# The only SU(2)_k fusion enumeration here is at k = 1 and k = 2 (allowed smallest cases).
# Everything else is SU(2) Catalan data or arithmetic on the closed forms derived in NOTE.md.
import sys

NMAX = 30
SER = 16  # beta-series order kept


def gcd(a, b):
    a = -a if a < 0 else a
    b = -b if b < 0 else b
    while b:
        a, b = b, a % b
    return a


def R(n, d=1):
    if d == 0:
        raise ZeroDivisionError("zero denominator")
    if d < 0:
        n, d = -n, -d
    g = gcd(n, d)
    return (n // g, d // g)


def radd(x, y):
    return R(x[0] * y[1] + y[0] * x[1], x[1] * y[1])


def rsub(x, y):
    return R(x[0] * y[1] - y[0] * x[1], x[1] * y[1])


def rmul(x, y):
    return R(x[0] * y[0], x[1] * y[1])


def rdiv(x, y):
    return R(x[0] * y[1], x[1] * y[0])


ZERO = (0, 1)
ONE = (1, 1)


def rs(x):
    return "%d:%d" % x


def binom(n, r):
    if r < 0 or r > n:
        return 0
    num, den = 1, 1
    for i in range(r):
        num *= n - i
        den *= i + 1
    return num // den


def fact(n):
    out = 1
    for i in range(2, n + 1):
        out *= i
    return out


def catalan(m):
    return binom(2 * m, m) // (m + 1)


def fusion_counts(k, nmax):
    # out[n][a] = multiplicity of spin a/2 in V_{1/2}^{(x)n}; k=None means untruncated SU(2).
    top = nmax if k is None else k
    vec = [0] * (top + 1)
    vec[0] = 1
    out = []
    for _ in range(nmax + 1):
        out.append(list(vec))
        new = [0] * (top + 1)
        for a in range(top + 1):
            c = vec[a]
            if c:
                if a - 1 >= 0:
                    new[a - 1] += c
                if a + 1 <= top:
                    new[a + 1] += c
        vec = new
    return out


def reflection(n, k):
    if n % 2:
        return 0
    K = k + 2
    h = n // 2
    total = 0
    t = -(n // K) - 2
    while t <= n // K + 2:
        total += binom(n, h + t * K) - binom(n, h + t * K + 1)
        t += 1
    return total


def ser_mul(a, b):
    out = [ZERO] * (SER + 1)
    for i in range(SER + 1):
        if a[i] == ZERO:
            continue
        for j in range(SER + 1 - i):
            if b[j] != ZERO:
                out[i + j] = radd(out[i + j], rmul(a[i], b[j]))
    return out


def ser_log(a):
    assert a[0] == ONE
    L = [ZERO] * (SER + 1)
    for n in range(1, SER + 1):
        acc = R(n * a[n][0], a[n][1])
        for i in range(1, n):
            acc = rsub(acc, rmul(R(i * L[i][0], L[i][1]), a[n - i]))
        L[n] = R(acc[0], acc[1] * n)
    return L


def ser_scale(a, c):
    return [rmul(x, c) for x in a]


def ser_add(a, b):
    return [radd(x, y) for x, y in zip(a, b)]


def ser_sub(a, b):
    return [rsub(x, y) for x, y in zip(a, b)]


def ser_div(a, b):
    assert b[0] == ONE
    out = [ZERO] * (SER + 1)
    for n in range(SER + 1):
        acc = a[n]
        for i in range(1, n + 1):
            acc = rsub(acc, rmul(b[i], out[n - i]))
        out[n] = acc
    return out


def ser_pow(a, e):
    out = [ONE] + [ZERO] * SER
    for _ in range(e):
        out = ser_mul(out, a)
    return out


def a_series(counts, two_j):
    # a_j(beta) = sum_n (beta/2)^n N_n(0 -> 2j) / n!
    out = [ZERO] * (SER + 1)
    for n in range(SER + 1):
        row = counts[n]
        c = row[two_j] if two_j < len(row) else 0
        out[n] = R(c, (1 << n) * fact(n))
    return out


def first_nonzero(s):
    for i, x in enumerate(s):
        if x != ZERO:
            return i, x
    return None, ZERO


rows = []
fails = 0


def check(name, ok, detail=""):
    global fails
    if not ok:
        fails += 1
    rows.append("CHECK|name=%s|result=%s|%s|json=0" % (name, "PASS" if ok else "FAIL", detail))


su2 = fusion_counts(None, NMAX)
cat_ok = all(su2[n][0] == (catalan(n // 2) if n % 2 == 0 else 0) for n in range(NMAX + 1))
check("su2_spin0_eq_catalan_n0_30", cat_ok, "C=" + ",".join(str(catalan(m)) for m in range(16)))

counts = {1: fusion_counts(1, NMAX), 2: fusion_counts(2, NMAX)}
for k in (1, 2):
    M = [counts[k][n][0] for n in range(NMAX + 1)]
    check("k%d_enum_eq_reflection" % k, all(M[n] == reflection(n, k) for n in range(NMAX + 1)),
          "M=" + ",".join(str(x) for x in M))
    check("k%d_odd_zero" % k, all(M[n] == 0 for n in range(1, NMAX + 1, 2)))
    check("k%d_catalan_prefix_m_le_k" % k, all(M[2 * m] == catalan(m) for m in range(k + 1)))
    check("k%d_break_2k+2_eq_C-1" % k, M[2 * k + 2] == catalan(k + 1) - 1,
          "M=%d|C=%d" % (M[2 * k + 2], catalan(k + 1)))
    if k == 1:
        cf = all(M[2 * m] == 1 for m in range(16))
    else:
        cf = M[0] == 1 and all(M[2 * m] == (1 << (m - 1)) for m in range(1, 16))
    check("k%d_closed_form" % k, cf)
    # Cayley-Hamilton recurrence from U_{k+1}(x/2) = sum_j (-1)^j binom(k+1-j,j) x^{k+1-2j}
    rec_ok = True
    for n in range(k + 1, NMAX + 1):
        s = 0
        j = 1
        while 2 * j <= k + 1:
            s += (-1) ** (j + 1) * binom(k + 1 - j, j) * M[n - 2 * j]
            j += 1
        rec_ok = rec_ok and (s == M[n])
    check("k%d_chebyshev_recurrence" % k, rec_ok)
    # generating function P_k/P_{k+1}, P_h = sum_j (-1)^j binom(h-j,j) x^j
    def P(h):
        return [(-1) ** j * binom(h - j, j) for j in range(16)]
    num, den = P(k), P(k + 1)
    q = [0] * 16
    for i in range(16):
        acc = num[i]
        for t in range(1, i + 1):
            acc -= den[t] * q[i - t]
        q[i] = acc
    check("k%d_gf_Pk_over_Pk+1" % k, all(q[m] == M[2 * m] for m in range(16)))
    # deficit polynomials, valid for r <= k+1
    D = [catalan(m) - M[2 * m] for m in range(16)]
    poly = {0: 1, 1: 2 * k + 2, 2: 2 * k * k + 7 * k + 4}
    if k >= 2:
        poly[3] = 2 * (k + 3) * (k + 4) * (2 * k + 1) // 3
    ok = all(D[m] == 0 for m in range(k + 1))
    for r, v in poly.items():
        if r <= k + 1 and k + 1 + r < 16:
            ok = ok and D[k + 1 + r] == v
    for r in range(0, k + 2):
        m = k + 1 + r
        if m < 16:
            N2 = 2 * m
            ok = ok and D[m] == binom(N2, r) - 2 * binom(N2, r - 1) + binom(N2, r - 2)
    check("k%d_deficit_three_term_and_polys" % k, ok, "D=" + ",".join(str(x) for x in D))
    # other spins: first difference at n = 2k+2-2j with deficit 1
    ok = True
    for tj in range(0, k + 1):
        nb = 2 * k + 2 - tj
        for n in range(0, nb):
            ok = ok and counts[k][n][tj] == su2[n][tj]
        ok = ok and counts[k][nb][tj] == su2[nb][tj] - 1
    check("k%d_spin_j_break_at_2k+2-2j_deficit_1" % k, ok)

# 2D free-boundary model: f = log z, z = sum_n beta^n M_n/(2^n n!)
f = {}
for key, cnt in (("su2", su2), (1, counts[1]), (2, counts[2])):
    z = a_series(cnt, 0)
    f[key] = ser_log(z)
for k in (1, 2):
    d = ser_sub(f[k], f["su2"])
    p, v = first_nonzero(d)
    pred1 = R(-1, (4 ** (k + 1)) * fact(2 * k + 2))
    pred2 = R(2 * k * k + 5 * k + 4, (4 ** (k + 2)) * fact(2 * k + 4))
    ok = p == 2 * k + 2 and v == pred1 and d[2 * k + 4] == pred2
    check("k%d_2D_free_first_break" % k, ok,
          "power=%d|value=%s|next=%s|pred=%s,%s" % (p, rs(v), rs(d[2 * k + 4]), rs(pred1), rs(pred2)))
    check("k%d_2D_free_diff_even" % k, all(d[i] == ZERO for i in range(1, SER + 1, 2)))

# a_j series and exact quantum-dimension powers for k <= 2
A = {}
for key, cnt, js in (("su2", su2, (0, 1, 2, 3, 4)), (1, counts[1], (0, 1)), (2, counts[2], (0, 1, 2))):
    A[key] = {tj: a_series(cnt, tj) for tj in js}


def dpow(key, tj, e):
    # d_j^e as a rational, e even when irrational; key su2: d=2j+1; k=1: all 1; k=2: d_{1/2}^2=2, d_1=1
    if key == "su2":
        base = tj + 1
        return R(base ** e, 1) if e >= 0 else R(1, base ** (-e))
    if key == 1:
        return ONE
    if tj == 1:
        assert e % 2 == 0
        h = e // 2
        return R(2 ** h, 1) if h >= 0 else R(1, 2 ** (-h))
    return ONE


def closed_surface_logZ(key, chi, P):
    a0 = A[key][0]
    tot = [ONE] + [ZERO] * SER
    for tj in A[key]:
        if tj == 0:
            continue
        ratio = ser_div(A[key][tj], a0)
        term = ser_scale(ser_pow(ratio, P), dpow(key, tj, chi - P))
        tot = ser_add(tot, term)
    la0 = ser_log(a0)
    return ser_add(ser_scale(la0, R(P, 1)), ser_log(tot))


for label, chi, P in (("cube_surface_S2_P6", 2, 6), ("torus_1x2_P2", 0, 2), ("torus_2x2_P4", 0, 4)):
    base = closed_surface_logZ("su2", chi, P)
    for k in (1, 2):
        d = ser_sub(closed_surface_logZ(k, chi, P), base)
        p, v = first_nonzero(d)
        rows.append("VALUE|name=%s_k%d_first_diff|power=%d|value=%s|json=0" % (label, k, p, rs(v)))
        expect = {("cube_surface_S2_P6", 1): (4, R(-1, 64)), ("cube_surface_S2_P6", 2): (6, R(43, 15360)),
                  ("torus_1x2_P2", 1): (2, R(3, 16)), ("torus_1x2_P2", 2): (2, R(1, 16)),
                  ("torus_2x2_P4", 1): (4, R(37, 768)), ("torus_2x2_P4", 2): (4, R(3, 256))}[(label, k)]
        check("%s_k%d" % (label, k), (p, v) == expect, "expect=%d,%s" % (expect[0], rs(expect[1])))

# 3D thermodynamic through beta^8: f = log a0 + (1/3) d^-4 (a_half/a0)^6
def f3d(key):
    a0 = A[key][0]
    cube = ser_scale(ser_pow(ser_div(A[key][1], a0), 6), rmul(R(1, 3), dpow(key, 1, -4)))
    return ser_add(ser_log(a0), cube)


b3 = f3d("su2")
for k in (1, 2):
    d = ser_sub(f3d(k), b3)
    p, v = first_nonzero(d)
    rows.append("VALUE|name=f3D_k%d|first_power=%d|value=%s|c4=%s|c6=%s|json=0" % (k, p, rs(v), rs(d[4]), rs(d[6])))
    exp = {1: (4, R(-1, 384), R(59, 11520)), 2: (6, R(11, 11520), R(11, 11520))}[k]
    check("f3D_k%d" % k, p == exp[0] and v == exp[1] and d[6] == exp[2])
check("su2_f3D_beta6_cube_coeff", rsub(b3[6], ser_log(A["su2"][0])[6]) == R(1, 3072))

# Hamiltonian RS 4th-order arithmetic (conjectural construction), as a function of d^2
def ham_c4(d2, has_spin1):
    single_chain = R(2, 9) if has_spin1 else ZERO
    single = rsub(single_chain, R(16, 27))
    a0sq = R(1, d2[0]) if d2[1] == 1 else R(d2[1], d2[0])
    pair = rsub(rmul(R(64, 9), radd(rmul(a0sq, R(2, 9)), rmul(rsub(ONE, a0sq), R(2, 13)))), R(32, 27))
    return rmul(R(-1, 1), radd(single, rmul(R(2, 1), pair)))


c4su2 = ham_c4((4, 1), True)
c4k2 = ham_c4((2, 1), True)
c4k1 = ham_c4((1, 1), False)
rows.append("VALUE|name=ham_c4|su2=%s|k2=%s|k1=%s|json=0" % (rs(c4su2), rs(c4k2), rs(c4k1)))
check("ham_c4_values", c4su2 == R(326, 1053) and c4k2 == R(70, 1053) and c4k1 == R(-16, 81))

# pillow (two plaquettes on one boundary, a sphere): Z = sum_j a_j^2 must equal a_0(2 beta)
for key, cnt in (("su2", su2), (1, counts[1]), (2, counts[2])):
    tot = [ZERO] * (SER + 1)
    tjs = range(0, SER // 2 + 1) if key == "su2" else A[key]
    for tj in tjs:
        aj = a_series(cnt, tj)
        tot = ser_add(tot, ser_mul(aj, aj))
    a0_2b = [rmul(x, R(1 << n, 1)) for n, x in enumerate(A[key][0])]
    check("pillow_eq_a0_of_2beta_%s" % key, tot == a0_2b)
for k in (1, 2):
    d = ser_sub(ser_log([rmul(x, R(1 << n, 1)) for n, x in enumerate(A[k][0])]),
                ser_log([rmul(x, R(1 << n, 1)) for n, x in enumerate(A["su2"][0])]))
    p, v = first_nonzero(d)
    check("pillow_k%d_first_diff" % k, p == 2 * k + 2 and v == R(-1, fact(2 * k + 2)), "power=%d|value=%s" % (p, rs(v)))

# weight-independent ratio: [logZ_cube - 6 log b0]_6 / [logZ_2x3torus - 6 log b0]_6 = d_half^2
r_test = [ZERO, R(3, 7), R(5, 11)] + [ZERO] * (SER - 2)
for key, d2 in (("su2", R(4, 1)), (1, ONE), (2, R(2, 1))):
    r6 = ser_pow(r_test, 6)
    dm4 = rmul(rdiv(ONE, d2), rdiv(ONE, d2))
    dm6 = rmul(dm4, rdiv(ONE, d2))
    cube6 = ser_log([radd(ONE, rmul(dm4, r6[0]))] + [rmul(dm4, x) for x in r6[1:]])[6]
    tor6 = ser_log([radd(ONE, rmul(dm6, r6[0]))] + [rmul(dm6, x) for x in r6[1:]])[6]
    check("psi6_ratio_%s" % key, rdiv(cube6, tor6) == d2, "ratio=%s" % rs(rdiv(cube6, tor6)))

for r in rows:
    print(r)
print("END|checks=%d|failed=%d|json=0" % (sum(1 for r in rows if r.startswith("CHECK")), fails))
sys.exit(1 if fails else 0)
