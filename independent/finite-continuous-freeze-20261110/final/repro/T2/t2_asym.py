# t2_asym.py -- pre-freeze ASYMPTOTIC evaluation for T2 (b), (c). Integers only (fixed point).
# Reads GROUPS.hbp (from t2_groups.py). Evaluates three truncated asymptotic approximations of the
# relative deviation delta_G(beta) = P_G(beta) / P_SU2(beta) - 1 of the 2D one-plaquette mean:
#   S (strong coupling): integer Wronskian series W/D truncated at relative order r (r = 8, 10, 12);
#   D (character + Debye): R = 1 + sum_{defects n <= t+9} d_n (n+1) I_(n+1)/I_1, Bessel functions by
#      the Debye uniform expansion through U_4/V_4 (SU(2) side by Debye nu = 1, 2 or Hankel);
#   L (gap): two-class model P2 = (1 + N1 c1 e^(-beta D1)) / (1 + N1 e^(-beta D1)) over the
#      Hankel (or Debye) SU(2) mean.
# The exact curves P_G (full class sum) and I_2/I_1 (convergent series) are NOT evaluated.
# Run: python3 -I -B t2_asym.py DIR   (reads DIR/GROUPS.hbp, writes DIR/ASYM.hbp)
import hashlib
import sys

PREC = 50
ONE = pow(10, PREC)


def igcd(a, b):
    a = -a if a < 0 else a
    b = -b if b < 0 else b
    while b:
        a, b = b, a % b
    return a


def isqrt(n):
    assert n >= 0
    if n < 2:
        return n
    x = 1 << ((n.bit_length() + 1) // 2)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


def fx(n, d=1):
    return n * ONE // d


def fmul(a, b):
    return a * b // ONE


def fdiv(a, b):
    return a * ONE // b


def fsqrt(a):
    return isqrt(a * ONE)


def _atanh_series(s):
    s2 = s * s // ONE
    total = s
    term = s
    k = 1
    while True:
        term = term * s2 // ONE
        add = term // (2 * k + 1)
        if add == 0:
            break
        total += add
        k += 1
    return total


LN2 = 2 * _atanh_series(ONE // 3)


def fexp(a):
    m = (a + LN2 // 2) // LN2
    r = a - m * LN2
    s = ONE
    term = ONE
    k = 1
    while True:
        term = term * r // (ONE * k)
        if term == 0:
            break
        s += term
        k += 1
    return s << m if m >= 0 else s >> (-m)


def fln(a):
    assert a > 0
    m = 0
    b = a
    while b >= 2 * ONE:
        b >>= 1
        m += 1
    while b < ONE:
        b <<= 1
        m -= 1
    s = (b - ONE) * ONE // (b + ONE)
    return 2 * _atanh_series(s) + m * LN2


def fstr(a, digits=6):
    neg = a < 0
    a = -a if neg else a
    q = pow(10, PREC - digits)
    v = (a + q // 2) // q
    ip = v // pow(10, digits)
    fp = v % pow(10, digits)
    return ("-" if neg else "") + str(ip) + "." + str(fp).zfill(digits)


def fsci(a):
    # 3 significant digits, integer-only formatting
    if a == 0:
        return "0"
    neg = a < 0
    a = -a if neg else a
    e = 0
    v = a
    lo = pow(10, PREC)
    while v >= 10 * lo:
        v //= 10
        e += 1
    while v < lo:
        v *= 10
        e -= 1
    mant = (v + pow(10, PREC - 3) // 2) // pow(10, PREC - 3)
    if mant >= 10000:
        mant //= 10
        e += 1
    s = str(mant)
    return ("-" if neg else "") + s[0] + "." + s[1:4] + "e" + str(e)


# ---------------------------------------------------------------- rational polynomials (Debye U_k, V_k)
def rp_norm(c):
    out = []
    for (n, d) in c:
        if d < 0:
            n, d = -n, -d
        g = igcd(n, d) if n != 0 else d
        out.append((n // g, d // g))
    while len(out) > 1 and out[-1][0] == 0:
        out.pop()
    return out


def rp_add(a, b):
    n = max(len(a), len(b))
    out = []
    for i in range(n):
        x = a[i] if i < len(a) else (0, 1)
        y = b[i] if i < len(b) else (0, 1)
        out.append((x[0] * y[1] + y[0] * x[1], x[1] * y[1]))
    return rp_norm(out)


def rp_scale(a, n, d):
    return rp_norm([(x[0] * n, x[1] * d) for x in a])


def rp_mulx(a, k):
    # multiply by p^k
    return [(0, 1)] * k + a


def rp_deriv(a):
    return rp_norm([(a[i][0] * i, a[i][1]) for i in range(1, len(a))] or [(0, 1)])


def rp_integ(a):
    return rp_norm([(0, 1)] + [(a[i][0], a[i][1] * (i + 1)) for i in range(len(a))])


def debye_polys(kmax):
    # DLMF 10.41.9: U_(k+1) = (1/2) p^2 (1-p^2) U_k' + (1/8) int_0^p (1-5t^2) U_k dt;
    #               V_(k+1) = U_(k+1) - (1/2) p (1-p^2) U_k - p^2 (1-p^2) U_k'
    U = [[(1, 1)]]
    V = [[(1, 1)]]
    one_m_p2 = [(1, 1), (0, 1), (-1, 1)]
    one_m_5p2 = [(1, 1), (0, 1), (-5, 1)]

    def pmul(a, b):
        out = [(0, 1)] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                z = out[i + j]
                out[i + j] = (z[0] * x[1] * y[1] + x[0] * y[0] * z[1], z[1] * x[1] * y[1])
        return rp_norm(out)

    for k in range(kmax):
        Uk = U[k]
        Ud = rp_deriv(Uk)
        t1 = rp_scale(rp_mulx(pmul(one_m_p2, Ud), 2), 1, 2)
        t2 = rp_scale(rp_integ(pmul(one_m_5p2, Uk)), 1, 8)
        Un = rp_add(t1, t2)
        U.append(Un)
        v = rp_add(Un, rp_scale(rp_mulx(pmul(one_m_p2, Uk), 1), -1, 2))
        v = rp_add(v, rp_scale(rp_mulx(pmul(one_m_p2, Ud), 2), -1, 1))
        V.append(v)
    return U, V


KD = 5
UP, VP = debye_polys(KD)


def peval(poly, p):
    # fixed-point evaluation by Horner
    acc = 0
    for (n, d) in reversed(poly):
        acc = fmul(acc, p) + n * ONE // d
    return acc


# ---------------------------------------------------------------- Bessel asymptotics
def hankel(nu, b):
    # scaled I_nu: Itilde = I_nu(beta) sqrt(2 pi beta) e^-beta ~ sum (-1)^k a_k(nu) / beta^k
    # optimal truncation; returns (value, |first omitted term|)
    xinv = ONE * ONE // b
    total = ONE
    term = ONE
    k = 1
    mu = 4 * nu * nu
    while k <= 40:
        nt = term * (-(mu - (2 * k - 1) * (2 * k - 1))) * xinv // (8 * k * ONE)
        if abs(nt) >= abs(term) and k > 1:
            return total, abs(nt)
        if nt == 0:
            return total, 0
        total += nt
        term = nt
        k += 1
    return total, abs(term)


def debye(nu, b, kuse=4):
    # returns (ln Itilde_nu(beta), L_nu = I_nu'/I_nu, err_rel) by DLMF 10.41.3/10.41.5 through U_kuse, V_kuse;
    # err_rel = |U_(kuse+1)|/nu^(kuse+1) + |V_(kuse+1)|/nu^(kuse+1)
    S = fsqrt(nu * nu * ONE + fmul(b, b))
    p = nu * ONE * ONE // S
    nueta = S + nu * fln(b * ONE // (nu * ONE + S))
    su = ONE
    sv = ONE
    nuk = 1
    for k in range(1, kuse + 1):
        nuk *= nu
        su += peval(UP[k], p) // nuk
        sv += peval(VP[k], p) // nuk
    nuk *= nu
    err = (abs(peval(UP[kuse + 1], p)) + abs(peval(VP[kuse + 1], p))) // nuk
    lnI = nueta - b + fln(b * ONE // S) // 2 + fln(su)
    L = fdiv(fmul(fdiv(S, b), sv), su)
    return lnI, L, err


def su2(b, method):
    # P_SU2 = I_2/I_1, L_1 = I_1'/I_1, err of P (relative), by method 'hankel' or 'debye'
    if method == "hankel":
        h0, e0 = hankel(0, b)
        h1, e1 = hankel(1, b)
        h2, e2 = hankel(2, b)
        P = fdiv(h2, h1)
        L1 = fdiv(h0, h1) - fdiv(ONE, b)
        err = fdiv(e2, h2) + fdiv(e1, h1)
        return P, L1, err, fln(h1)
    l1, L1, er1 = debye(1, b)
    l2, L2, er2 = debye(2, b)
    P = fexp(l2 - l1)
    return P, L1, er1 + er2, l1


# ---------------------------------------------------------------- data
def parse(path):
    groups = []
    haar = None
    cur = None
    for line in open(path):
        line = line.rstrip("\n")
        parts = line.split("|")
        key = parts[0]
        f = {}
        for p in parts[1:]:
            if "=" in p:
                k, v = p.split("=", 1)
                f[k] = v
        if key == "GROUP":
            cur = {"name": f["name"], "order": int(f["order"]), "t": int(f["t"]), "iota": int(f["iota"]),
                   "ring": f["ring"], "alpha2": f["alpha2"], "classes": f["trace_classes"]}
            groups.append(cur)
        elif key == "MOLIEN":
            cur["d"] = [int(x) for x in f["d_0..40"].split(",")]
        elif key == "WRONSKIAN":
            cur["W"] = [int(x) for x in f["W_0..30"].split(",")]
            cur["D"] = [int(x) for x in f["D_0..30"].split(",")]
    return groups


def alpha_value(g):
    if g["ring"] == "Z[phi]":
        return (ONE + fsqrt(5 * ONE)) // 2
    if g["ring"] == "Z[sqrt3]":
        return fsqrt(3 * ONE)
    return fsqrt(2 * ONE)


def class_list(g):
    al = alpha_value(g)
    out = []
    for item in g["classes"].split(";"):
        a = item[len("tr=("):]
        ab, cnt = a.split(")x")
        x, y = ab.split(",")
        x, y, cnt = int(x), int(y), int(cnt)
        c = (x * ONE + y * al) // 2           # c = tr/2, fixed point
        out.append((c, cnt, (x, y)))
    out.sort(key=lambda z: -z[0])
    return out


def fact(n):
    f = 1
    for i in range(2, n + 1):
        f *= i
    return f


# ---------------------------------------------------------------- the three tools
def delta_S(g, b, r):
    x = b // 2
    t = g["t"]
    num = 0
    xp = ONE
    for n in range(0, t + r + 1):
        if n >= t:
            num += g["W"][n] * xp // fact(n)
        xp = fmul(xp, x)
    den = 0
    xp = ONE
    for n in range(0, 2 + r):
        if n >= 1:
            den += g["D"][n] * xp // fact(n)
        xp = fmul(xp, x)
    return fdiv(num, den)


def delta_D(g, b, method, kdef=4):
    # character + Debye with the first kdef nonzero defect degrees n >= 1;
    # returns (delta, next-defect contribution to delta (first omitted), Debye/Hankel relative error)
    P, L1, errP, lnI1 = su2(b, method)
    Rm1 = 0
    Rp = 0
    errdeb = 0
    nxt = 0
    used = 0
    for n in range(1, len(g["d"])):
        dn = g["d"][n]
        if dn == 0:
            continue
        lnI, L, er = debye(n + 1, b)
        F = fexp(lnI - lnI1)
        term = dn * (n + 1) * F
        if used < kdef:
            Rm1 += term
            Rp += fmul(term, L - L1)
            errdeb = er if er > errdeb else errdeb
            used += 1
        else:
            nxt = fdiv(fmul(term, L - L1), ONE + Rm1)
            break
    dP = fdiv(Rp, ONE + Rm1)
    delta = fdiv(dP, P)
    return delta, fdiv(nxt, P), errdeb + errP


def gapdata(g):
    cl = class_list(g)
    assert cl[0][0] == ONE
    c1, N1 = cl[1][0], cl[1][1]
    c2 = cl[2][0] if len(cl) > 2 else None
    nrest = g["order"] - 1 - N1
    return c1, N1, c2, nrest


def delta_L(g, b, method):
    c1, N1, c2, nrest = gapdata(g)
    D1 = ONE - c1
    e1 = fexp(-fmul(b, D1))
    W2 = ONE + N1 * e1
    P2 = fdiv(ONE + N1 * fmul(c1, e1), W2)
    P, L1, errP, _ = su2(b, method)
    delta = fdiv(P2, P) - ONE
    # rigorous bound 0 <= P2 - P_G <= 2 * nrest * e^(-beta D2) / W2
    if c2 is None:
        bnd = 0
    else:
        bnd = fdiv(2 * nrest * fexp(-fmul(b, ONE - c2)), W2)
    return delta, fdiv(bnd, P), errP


def envelope(b, method):
    P, _, errP, _ = su2(b, method)
    return fdiv(ONE, P) - ONE, errP


def bisect(fun, lo, hi, target, it=40):
    flo = fun(lo) - target
    for _ in range(it):
        mid = (lo + hi) // 2
        fm = fun(mid) - target
        if (fm >= 0) == (flo >= 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) // 2


def grid():
    pts = []
    for k in range(1, 50):
        pts.append(fx(k, 10))          # 0.1 .. 4.9
    for k in range(10, 60):
        pts.append(fx(k, 2))           # 5 .. 29.5
    for k in range(30, 80):
        pts.append(fx(k))              # 30 .. 79
    for k in range(80, 301, 5):
        pts.append(fx(k))              # 80 .. 300
    return pts


def find_crossings(fun, pp, vals, th):
    cr = []
    for i in range(len(pp) - 1):
        a, c = vals[i] - th, vals[i + 1] - th
        if (a >= 0) != (c >= 0):
            cr.append((bisect(fun, pp[i], pp[i + 1], th), "up" if c >= 0 else "down"))
    return cr


def refine_max(fun, lo, hi, it=60):
    for _ in range(it):
        m1 = lo + (hi - lo) // 3
        m2 = hi - (hi - lo) // 3
        if fun(m1) < fun(m2):
            lo = m1
        else:
            hi = m2
    m = (lo + hi) // 2
    return m, fun(m)


def hankel_rational(nu, K):
    # exact a_k(nu) with sign: coefficient of beta^-k in Itilde_nu
    out = [(1, 1)]
    num, den = 1, 1
    mu = 4 * nu * nu
    for k in range(1, K + 1):
        num *= -(mu - (2 * k - 1) * (2 * k - 1))
        den *= 8 * k
        g = igcd(num, den)
        out.append((num // g, den // g))
    return out


def rser_div(a, b, K):
    # power series a/b in u = 1/beta, rationals, b[0] = 1
    q = []
    for k in range(K + 1):
        n, d = a[k]
        for j in range(1, k + 1):
            if j < len(b):
                x = (q[k - j][0] * b[j][0], q[k - j][1] * b[j][1])
                n, d = n * x[1] - x[0] * d, d * x[1]
        g = igcd(n, d)
        q.append((n // g, d // g))
    return q


def main():
    d = sys.argv[1]
    groups = parse(d + "/GROUPS.hbp")
    rows = []
    checks = []
    checks.append(("U1", UP[1] == [(0, 1), (1, 8), (0, 1), (-5, 24)]))
    checks.append(("U2_p2", UP[2][2] == (9, 128)))
    checks.append(("U3_p9", UP[3][9] == rp_norm([(-425425, 414720)])[0]))
    checks.append(("V2_p6", VP[2][6] == rp_norm([(-455, 1152)])[0]))
    checks.append(("V3_p9", VP[3][9] == rp_norm([(475475, 414720)])[0]))
    stir = [(1, 1), (-1, 12), (1, 288), (139, 51840), (-571, 2488320)]
    for k in range(5):
        s = (0, 1)
        for (n, dd) in UP[k]:
            s = (s[0] * dd + n * s[1], s[1] * dd)
        g = igcd(s[0], s[1])
        checks.append(("Uk(1)_stirling_k%d" % k, (s[0] // g, s[1] // g) == stir[k]))
    rows.append("DEBYE_POLYS|source=DLMF_10.41.9_recursion_checked_against_10.41.10_10.41.11_and_Stirling|U1=%s|U2=%s|U3=%s|V1=%s|V2=%s|V3=%s|json=0" % tuple(
        ";".join("%d:%d" % c for c in P) for P in (UP[1], UP[2], UP[3], VP[1], VP[2], VP[3])))
    # exact large-beta series of P_SU2 = I_2/I_1 and of the envelope E = I_1/I_2 - 1 (Hankel, DLMF 10.40.1)
    K = 6
    h1 = hankel_rational(1, K)
    h2 = hankel_rational(2, K)
    pser = rser_div(h2, h1, K)
    eser = rser_div(h1, h2, K)
    eser[0] = (0, 1)
    rows.append("SU2_LARGE_BETA|P_SU2=I2:I1=sum_k c_k*beta^-k|c_0..%d=%s|json=0" % (K, ",".join("%d:%d" % c for c in pser)))
    rows.append("SU2_LARGE_BETA|E=I1:I2-1=sum_k e_k*beta^-k|e_0..%d=%s|json=0" % (K, ",".join("%d:%d" % c for c in eser)))
    checks.append(("P_SU2_c1_eq_-3:2", pser[1] == (-3, 2)))
    checks.append(("E_e1_eq_3:2", eser[1] == (3, 2)))
    for (thr_n, thr_d) in ((1, 2), (1, 10), (1, 100)):
        th = fx(thr_n, thr_d)
        out = []
        for meth, lo in (("hankel", fx(3)), ("debye", fx(1))):
            fun = (lambda m: (lambda bb: envelope(bb, m)[0]))(meth)
            pp = [p for p in grid() if p >= lo]
            vals = [fun(p) for p in pp]
            cr = find_crossings(fun, pp, vals, th)
            out.append(meth + "=" + ",".join(fstr(c[0], 7) for c in cr))
        rows.append("ENVELOPE|theta=%d:%d|%s|json=0" % (thr_n, thr_d, "|".join(out)))
    for g in groups:
        name = g["name"]
        t = g["t"]
        iota = g["iota"]
        c1, N1, c2, nrest = gapdata(g)
        D1 = ONE - c1
        rows.append("GAP|name=%s|c1=%s|N1=%d|Delta1=%s|N1*Delta1=%s|c2=%s|Delta2=%s|n_rest=%d|json=0" % (
            name, fstr(c1, 8), N1, fstr(D1, 8), fstr(N1 * D1, 8),
            fstr(c2, 8) if c2 is not None else "none", fstr(ONE - c2, 8) if c2 is not None else "none", nrest))
        # closed-form laws
        if t >= 2:
            bt = 2 * fexp(fln(fx(fact(t), 100 * iota)) // (t - 1))
            twoC = (t + 1) * (t + 3) // 2      # 2 j(j+1) at j = (t+1)/2, times 1 (exponent numerator)
            # heat-kernel law: iota (t+2) (2C/beta^2) e^(-2C/beta) = 0.01 P_SU2(beta)
            def hk(bb):
                lhs = fmul(iota * (t + 2) * fdiv(twoC * ONE, fmul(bb, bb)), fexp(-fdiv(twoC * ONE, bb)))
                return fdiv(lhs, su2(bb, "debye")[0])
            pp = [p for p in grid() if fx(1, 10) <= p <= fx(100)]
            vals = [hk(p) for p in pp]
            cr = find_crossings(hk, pp, vals, fx(1, 100))
            bhk = cr[0][0] if cr else None
            rows.append("LAW|name=%s|t=%d|iota=%d|taylor_beta_x=2*(0.01*t!:iota)^(1:(t-1))=%s|heat_kernel_beta_x=%s|C2_first_missing_spin=(t+1)(t+3):4=%d:4|json=0" % (
                name, t, iota, fstr(bt, 5), fstr(bhk, 5) if bhk else "none", (t + 1) * (t + 3)))
        # freezing (peak) law from the gap form: beta_p D1 = ln(2 N1 D1^2 beta_p^2 / 3), delta_p = (3/(2 beta_p))(1 - 1/(beta_p D1))
        bp = fx(10)
        root = True
        for _ in range(200):
            nb = fdiv(fln(fdiv(2 * N1 * fmul(fmul(D1, D1), fmul(bp, bp)), fx(3))), D1)
            if nb < fx(1, 10):
                root = False
                break
            bp = nb
        if root:
            dp = fmul(fdiv(fx(3), 2 * bp), ONE - fdiv(ONE, fmul(bp, D1)))
            rows.append("LAW_FREEZE|name=%s|beta_peak_gap_law=%s|delta_peak_gap_law=%s|beta_peak*Delta1=%s|json=0" % (
                name, fstr(bp, 4), fstr(dp, 5), fstr(fmul(bp, D1), 4)))
        else:
            rows.append("LAW_FREEZE|name=%s|beta_peak_gap_law=no_root|meaning=peak_not_controlled_by_the_nearest_class|json=0" % name)
        pts = grid()
        ptsS = [p for p in pts if p <= fx(5, 2)]
        ptsD = [p for p in pts if fx(1) <= p <= fx(60)]
        ptsDh = [p for p in pts if fx(3) <= p <= fx(60)]
        ptsL = [p for p in pts if p >= fx(3)]

        def dl_low(bb):
            dv, bnd, _ = delta_L(g, bb, "hankel")
            return dv - bnd
        tools = []
        for r in (8, 12):
            tools.append(("S|r=%d" % r, (lambda rr: (lambda bb: delta_S(g, bb, rr)))(r), ptsS))
        tools.append(("D|kdef=3|su2=debye", lambda bb: delta_D(g, bb, "debye", 3)[0], ptsD))
        tools.append(("D|kdef=4|su2=debye", lambda bb: delta_D(g, bb, "debye", 4)[0], ptsD))
        tools.append(("D|kdef=4|su2=hankel", lambda bb: delta_D(g, bb, "hankel", 4)[0], ptsDh))
        tools.append(("L|su2=hankel", lambda bb: delta_L(g, bb, "hankel")[0], ptsL))
        tools.append(("L_LOWER|su2=hankel", dl_low, ptsL))
        for (label, fun, pp) in tools:
            vals = [fun(p) for p in pp]
            for (thr_n, thr_d) in ((1, 100), (1, 10), (1, 2)):
                th = fx(thr_n, thr_d)
                cr = find_crossings(fun, pp, vals, th)
                rows.append("CROSS|tool=%s|name=%s|theta=%d:%d|window=%s..%s|beta=%s|json=0" % (
                    label, name, thr_n, thr_d, fstr(pp[0], 1), fstr(pp[-1], 1),
                    ";".join(fstr(c[0], 7) + ":" + c[1] for c in cr) or "none"))
            mx = []
            for i in range(1, len(pp) - 1):
                if vals[i] > vals[i - 1] and vals[i] >= vals[i + 1]:
                    bm, vm = refine_max(fun, pp[i - 1], pp[i + 1])
                    mx.append(fstr(bm, 4) + ":" + fstr(vm, 6))
            rows.append("MAX|tool=%s|name=%s|window=%s..%s|local_maxima=%s|value_at_window_start=%s|json=0" % (
                label, name, fstr(pp[0], 1), fstr(pp[-1], 1), ";".join(mx) or "none", fstr(vals[0], 6)))
        # error companions at selected points
        for p in pts:
            if p > fx(120):
                continue
            parts = ["beta=" + fstr(p, 2)]
            if p <= fx(5, 2):
                s8 = delta_S(g, p, 8)
                s12 = delta_S(g, p, 12)
                parts.append("S12=" + fsci(s12) + "|S12-S8=" + fsci(s12 - s8))
            if fx(1) <= p <= fx(60):
                d4, en, ed = delta_D(g, p, "debye", 4)
                d3 = delta_D(g, p, "debye", 3)[0]
                parts.append("D4=" + fsci(d4) + "|D4-D3=" + fsci(d4 - d3) + "|D_next=" + fsci(en) + "|D_relerr=" + fsci(ed))
                if p >= fx(3):
                    parts.append("D4h=" + fsci(delta_D(g, p, "hankel", 4)[0]))
            if p >= fx(1):
                meth = "hankel" if p >= fx(3) else "debye"
                dlv, bnd, eP = delta_L(g, p, meth)
                parts.append("L=" + fsci(dlv) + "|L_bound=" + fsci(bnd) + "|P_relerr=" + fsci(eP))
            rows.append("CURVE|name=%s|%s|json=0" % (name, "|".join(parts)))
    bad = [c for c, ok in checks if not ok]
    rows.append("CHECKS|n=%d|failed=%d|bad=%s|json=0" % (len(checks), len(bad), ",".join(bad) or "none"))
    src = open(__file__, "rb").read()
    gsrc = open(d + "/GROUPS.hbp", "rb").read()
    head = ("T2_ASYM_HEAD|script=t2_asym.py|script_sha256=%s|input=GROUPS.hbp|input_sha256=%s|integer_only=1|"
            "fixed_point=10^%d|exact_plaquette_curves_evaluated=0|json=0") % (
        hashlib.sha256(src).hexdigest(), hashlib.sha256(gsrc).hexdigest(), PREC)
    with open(d + "/ASYM.hbp", "w") as f:
        f.write("\n".join([head] + rows) + "\n")
    print("checks", len(checks), "failed", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
