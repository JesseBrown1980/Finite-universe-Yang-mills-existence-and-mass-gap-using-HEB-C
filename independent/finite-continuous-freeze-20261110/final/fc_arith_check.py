# FC assembly seat: integer-only re-check of the ARITHMETIC of derived formulas in the
# three lane row files. No torus, no group closure, no fusion iteration, no plaquette curve.
# Run: python3 -I -B fc_arith_check.py <fc-tests dir>
import sys
import hashlib

BASE = sys.argv[1]
out = []
fails = 0


def check(name, ok, detail=""):
    global fails
    if not ok:
        fails += 1
    out.append("CHECK|name=%s|ok=%d|%sjson=0" % (name, 1 if ok else 0, ("detail=%s|" % detail) if detail else ""))


def gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def q(n, d=1):
    if d < 0:
        n, d = -n, -d
    g = gcd(n, d)
    return (n // g, d // g)


def qadd(a, b):
    return q(a[0] * b[1] + b[0] * a[1], a[1] * b[1])


def qmul(a, b):
    return q(a[0] * b[0], a[1] * b[1])


def qstr(a):
    return "%d:%d" % a


def isqrt(n):
    if n < 2:
        return n
    x = 1 << ((n.bit_length() + 1) // 2)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


def iroot(n, k):
    lo, hi = 0, 1
    while hi ** k <= n:
        hi *= 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid ** k <= n:
            lo = mid
        else:
            hi = mid
    return lo


def fact(n):
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r


def binom(n, k):
    if k < 0 or k > n:
        return 0
    return fact(n) // (fact(k) * fact(n - k))


def catalan(m):
    return binom(2 * m, m) // (m + 1)


def sci12(num, den):
    # (sign, 12-digit mantissa, exponent) of num/den, round half up
    s = -1 if ((num < 0) != (den < 0) and num != 0) else 1
    num, den = abs(num), abs(den)
    # find e with 10^e <= num/den < 10^(e+1)
    e = len(str(num // den)) - 1 if num >= den else -1
    if num < den:
        while num * 10 ** (-e) < den:
            e -= 1
    if e >= 0:
        m2 = (num * 10 ** (11 - e) * 2 + den) // (2 * den) if 11 - e >= 0 else (num * 2 + den * 10 ** (e - 11)) // (2 * den * 10 ** (e - 11))
    else:
        m2 = (num * 10 ** (11 - e) * 2 + den) // (2 * den)
    if m2 >= 10 ** 12:
        m2 //= 10
        e += 1
    return (s, m2, e)


def parse_dec(tok):
    s = 1
    if tok.startswith("-"):
        s = -1
        tok = tok[1:]
    e = 0
    if "e" in tok:
        tok, ex = tok.split("e")
        e = int(ex)
    ip, fp = (tok.split(".") + [""])[:2]
    digits = (ip + fp).lstrip("0")
    e += len(ip.lstrip("0")) - 1 if ip.strip("0") else 0
    if not ip.strip("0"):
        lead = len(fp) - len(fp.lstrip("0"))
        e = e - lead - 1
    return (s, digits, e)


def round_int(v, drop):
    if drop <= 0:
        return v
    p = 10 ** drop
    return (v + p // 2) // p


def fixed_dec(num, den, places):
    # num/den rounded to `places` decimals, as string
    s = "-" if (num < 0) != (den < 0) and num != 0 else ""
    num, den = abs(num), abs(den)
    v = (num * 10 ** places * 2 + den) // (2 * den)
    ip, fp = divmod(v, 10 ** places)
    return "%s%d.%s" % (s, ip, str(fp).rjust(places, "0")) if places else "%s%d" % (s, ip)


S = 10 ** 40

# ---------------------------------------------------------------- T1 (S3 tori)
w = [1, 3, 2, 3, 3, 2, 2, 2]


def parse_gamma(txt):
    A = [[0] * 8 for _ in range(8)]
    for part in txt.split(","):
        part = part.strip()
        if not part.startswith("F") or ">" not in part:
            continue
        a, rest = part.split(">")
        b, v = rest.split(":")
        A[int(a[1:]) - 1][int(b[1:]) - 1] = int(v)
    return A


def charpoly(A):
    n = len(A)
    M = [[0] * n for _ in range(n)]
    c = [1]
    I = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    for k in range(1, n + 1):
        Mk = [[sum(A[i][l] * M[l][j] for l in range(n)) + (c[-1] * I[i][j]) for j in range(n)] for i in range(n)]
        AM = [[sum(A[i][l] * Mk[l][j] for l in range(n)) for j in range(n)] for i in range(n)]
        tr = sum(AM[i][i] for i in range(n))
        assert tr % k == 0
        c.append(-tr // k)
        M = Mk
    return c


rows1 = {}
for line in open(BASE + "/T1/ROWS.hbp"):
    f = line.rstrip("\n").split("|")
    d = dict(x.split("=", 1) for x in f[1:] if "=" in x)
    if "id" in d:
        rows1[d["id"]] = d

GV = parse_gamma(rows1["T1-B3"]["value"].split(";")[0])
GH = parse_gamma(rows1["T1-B4"]["value"].split(";")[0])
GS = [[GV[i][j] + GH[i][j] for j in range(8)] for i in range(8)]
check("T1_GammaV_charpoly_x4(x2-1)(x2-9)", charpoly(GV) == [1, 0, -10, 0, 9, 0, 0, 0, 0])
check("T1_GammaH_charpoly_x4(x2-1)(x2-9)", charpoly(GH) == [1, 0, -10, 0, 9, 0, 0, 0, 0])
check("T1_GammaV+H_charpoly_x4(x2-6)(x2-14)", charpoly(GS) == [1, 0, -20, 0, 84, 0, 0, 0, 0])
db = all(w[i] * G[i][j] == w[j] * G[j][i] for G in (GV, GH) for i in range(8) for j in range(8))
check("T1_detailed_balance_weights_1,3,2,3,3,2,2,2", db)
check("T1_zero_diagonal", all(GV[i][i] == 0 and GH[i][i] == 0 for i in range(8)))
sg = [1, -1, 1, -1, 1, 1, 1, 1]
check("T1_bipartite_under_sgn(a)sgn(b)", all(GS[i][j] == 0 or sg[i] * sg[j] == -1 for i in range(8) for j in range(8)))
check("T1_weights_sum_18_commuting_pairs", sum(w) == 18)

kap = {m: q(binom(2 * m - 2, m - 1), 4 ** (m - 1)) for m in (2, 3, 4)}
check("T1_kappa_2,3,4=1:2,3:8,5:16", [qstr(kap[m]) for m in (2, 3, 4)] == ["1:2", "3:8", "5:16"])
s14 = isqrt(14 * S * S)
s6 = isqrt(6 * S * S)
for tor in ["2x2", "2x3", "2x4", "2x5", "2x6", "3x3", "3x4", "3x5", "4x4", "4x5"]:
    Lx, Ly = int(tor[0]), int(tor[2])
    m = min(Lx, Ly)
    coef = qmul(q(max(Lx, Ly)), kap[m])
    row = rows1["T1-B-" + tor]
    if Lx != Ly:
        gap = qmul(coef, q(2))
        exp = row["value"]
        got = str(gap[0]) if gap[1] == 1 else "%d/%d" % gap
        check("T1_B_%s_E2-E1" % tor, got == exp, "%s_vs_%s" % (got, exp))
    else:
        num = coef[0] * (s14 - s6)
        val = fixed_dec(num, coef[1] * S, 6)
        exp = row["value"].split("~")[-1]
        check("T1_B_%s_E2-E1_decimal" % tor, val == exp, "%s_vs_%s" % (val, exp))
        v9 = fixed_dec(coef[0] * s14, coef[1] * S, 6)
        check("T1_B9_%s_swap_even" % tor, v9 in rows1["T1-B9"]["value"], v9)
check("T1_B6_square_ratio", fixed_dec(isqrt(21 * S * S) + 3 * S, 4 * S, 6) == "1.895644")
for L in (3, 4, 5, 6):
    v = q(-(4 * L + 57), 2)
    check("T1_C_2x%d" % L, rows1["T1-C-2x%d" % L]["value"] == "%d/%d" % v)
s2 = isqrt(2 * S * S)
c22 = fixed_dec(21 * 2 * S + 17 * s2 + 2 * s14, 2 * S, 6)
check("T1_C_2x2_decimal", rows1["T1-C-2x2"]["value"].endswith(c22), c22)
c3 = fixed_dec(27 * 2 * S + 17 * s2, 2 * S, 6)
check("T1_C3_2x2_decimal", c3 in rows1["T1-C3"]["value"], c3)
s5 = isqrt(5 * S * S)
check("T1_C6_(15-3sqrt5)/2", fixed_dec(15 * S - 3 * s5, 2 * S, 6) == "4.145898")
check("T1_B10_3x4_18", 3 * 3 * 4 // 2 == 18)
check("T1_B11_3x4_72", 6 * 3 * 4 == 72)

# ---------------------------------------------------------------- T2 (finite subgroups)
rows2 = {}
for line in open(BASE + "/T2/ROWS.hbp"):
    f = line.rstrip("\n").split("|")
    d = dict(x.split("=", 1) for x in f[1:] if "=" in x)
    if "id" in d:
        rows2[d["id"]] = d


def molien(qq, rr, pp, nmax):
    d = [0] * (nmax + 1)
    for a in range(0, nmax + 1, qq):
        for b in range(0, nmax + 1 - a, rr):
            d[a + b] += 1
            if a + b + pp <= nmax:
                d[a + b + pp] += 1
    return d


groups = [("Z3", (2, 3, 3)), ("Z4", (2, 4, 4)), ("Z6", (2, 6, 6)), ("Q8", (4, 4, 6)), ("DIC3", (4, 6, 8)),
          ("DIC4", (4, 8, 10)), ("DIC6", (4, 12, 14)), ("2T", (6, 8, 12)), ("2O", (8, 12, 18)), ("2I", (12, 20, 30))]
for name, (qq, rr, pp) in groups:
    d = molien(qq, rr, pp, 40)
    t1 = min(n for n in range(1, 41) if d[n] > 0)
    t, iota = t1 - 1, d[t1]
    haar = catalan(t1 // 2) if t1 % 2 == 0 else 0
    cl = q(iota, 2 ** (t + 1) * fact(t + 1))
    cp = q(iota, 2 ** (t + 1) * fact(t))
    pred = "(%d;%d;%d;%d;%s;%s)" % (t, iota, haar + iota, haar, qstr(cl), qstr(cp))
    exp = rows2["T2-A-" + name]["predicted"]
    check("T2_A_%s_from_Molien" % name, pred == exp, "%s_vs_%s" % (pred, exp))
small = {"Q8": (2, 3), "DIC": (1, 3), "2T": (1, 5), "2O": (1, 7), "2I": (1, 11)}
sm = rows2["T2-B-SMALL"]["predicted"]
for nm, (io, t) in small.items():
    c = q(io, 2 ** (t - 1) * fact(t))
    check("T2_B_SMALL_%s" % nm, ("beta^%d:%d" % (t - 1, c[1])) in sm and c[0] == 1, "beta^%d:%d" % (t - 1, c[1]))

# Hankel (DLMF 10.40.1): I_nu(x) e^-x sqrt(2 pi x) ~ sum_k (-1)^k a_k(nu) x^-k, a_k=prod_{j=1..k}(4nu^2-(2j-1)^2)/(k! 8^k)
def hankel(nu, K):
    res = []
    for k in range(K + 1):
        p = 1
        for j in range(1, k + 1):
            p *= 4 * nu * nu - (2 * j - 1) ** 2
        res.append(q((-1) ** k * p, fact(k) * 8 ** k))
    return res


def sdiv(a, b, K):
    r = []
    for k in range(K + 1):
        acc = a[k]
        for j in range(1, k + 1):
            acc = qadd(acc, qmul(q(-1), qmul(b[j], r[k - j])))
        r.append(qmul(acc, q(b[0][1], b[0][0])))
    return r


K = 5
P = sdiv(hankel(2, K), hankel(1, K), K)
check("T2_C_SU2_P_series", [qstr(x) for x in P] == ["1:1", "-3:2", "3:8", "3:8", "63:128", "27:32"], ",".join(qstr(x) for x in P))
one = [q(1)] + [q(0)] * K
Einv = sdiv(one, P, K)
Eser = [qadd(Einv[0], q(-1))] + Einv[1:]
check("T2_C_SU2_E_series", [qstr(x) for x in Eser] == ["0:1", "3:2", "15:8", "15:8", "135:128", "-45:32"], ",".join(qstr(x) for x in Eser))

SC = 10 ** 30
bx = {"Q8": "0.348038", "DIC3": "0.494155", "DIC4": "0.494925", "DIC6": "0.494926", "2T": "2.29211", "2O": "4.86716", "2I": "12.29801"}
ti = {"Q8": (3, 2), "DIC3": (3, 1), "DIC4": (3, 1), "DIC6": (3, 1), "2T": (5, 1), "2O": (7, 1), "2I": (11, 1)}


def todec(s, scale):
    neg = s.startswith("-")
    s = s.lstrip("-")
    ip, fp = (s.split(".") + [""])[:2]
    v = int(ip) * scale + (int(fp) * scale // 10 ** len(fp) if fp else 0)
    return -v if neg else v


bT = {}
for g, (t, io) in ti.items():
    rad = fact(t) * SC ** (t - 1) // (100 * io)
    bT[g] = 2 * iroot(rad, t - 1)
lawrow = rows2["T2-B-LAW-TRANSFER"]["predicted"]
for g, lab in (("Q8", "Q8"), ("DIC3", "Dic"), ("2T", "2T"), ("2O", "2O"), ("2I", "2I")):
    v = fixed_dec(bT[g], SC, 5)
    check("T2_LAW_TRANSFER_beta_T_%s" % g, ("%s(%s)" % (v, lab)) in lawrow, v)
for g in bx:
    u = SC - bT[g] * SC // todec(bx[g], SC)
    out.append("INFO|name=T2_undershoot_%s|u_percent=%s|json=0" % (g, fixed_dec(u * 100, SC, 2)))
ok_u = all(fixed_dec((SC - bT[g] * SC // todec(bx[g], SC)) * 100, SC, 2) in lawrow for g in ("Q8", "DIC3", "DIC4", "2T", "2O", "2I"))
check("T2_LAW_TRANSFER_undershoots_as_printed", ok_u)
lt = rows2["T2-B-LAW-T"]["predicted"]
cvals = [fixed_dec(todec(bx[g], SC), SC * (t + 1), 4) for g, t in (("DIC3", 3), ("2T", 5), ("2O", 7), ("2I", 11))]
check("T2_LAW_T_c_t", ";".join(cvals) in lt, ";".join(cvals))
Lam = [fixed_dec((t + 1) * (t + 3) * SC, 2 * todec(bx[g], SC), 3) for g, t in (("DIC3", 3), ("2T", 5), ("2O", 7), ("2I", 11))]
out.append("INFO|name=T2_Lambda_t|values=%s|json=0" % ";".join(Lam))
check("T2_LAW_T_Lambda_t", all(x[:5] in lt for x in Lam), ";".join(Lam))


def expfix(x, scale):
    # e^(x/scale) * scale, x >= 0, by halving and Taylor
    h = 0
    while x > scale // 8:
        x //= 2
        h += 1
    term, s, n = scale, scale, 1
    while term:
        term = term * x // (scale * n)
        s += term
        n += 1
    for _ in range(h):
        s = s * s // scale
    return s


for xs, n1 in (("4.3066", 6), ("4.8192", 8), ("5.4826", 12)):
    X = todec(xs, SC)
    lhs = expfix(X, SC)
    rhs = 2 * n1 * X * X // (3 * SC)
    rel = abs(lhs - rhs) * 10 ** 4 // rhs
    check("T2_FREEZE_x*_N1=%d" % n1, rel == 0, "rel_e4=%d" % rel)
check("T2_FREEZE_no_root_N1=2", expfix(2 * SC, SC) * 3 > 16 * SC)
check("T2_FREEZE_root_exists_N1=3", expfix(2 * SC, SC) < 8 * SC)
d1 = {"2T": (SC // 2), "2O": SC - isqrt(2 * SC * SC) // 2, "2I": (3 * SC - isqrt(5 * SC * SC)) // 4}
fl = rows2["T2-C-FREEZE-LAW"]["predicted"]
for g, xs in (("2T", "4.8192"), ("2O", "4.3066"), ("2I", "5.4826")):
    X = todec(xs, SC)
    bp = fixed_dec(X, d1[g], 3)
    dp = fixed_dec(3 * d1[g] * (X - SC), 2 * X * X, 4)
    check("T2_FREEZE_law_%s" % g, bp in fl and dp in fl, "%s;%s" % (bp, dp))
pp = rows2["T2-C-PEAK-PRODUCT"]["predicted"]
for g, a, b in (("2T", "0.14305", "8.91"), ("2O", "0.08445", "14.46"), ("2I", "0.04517", "27.50")):
    v = fixed_dec(todec(a, SC) * todec(b, SC), SC * SC, 3)
    check("T2_PEAK_PRODUCT_%s" % g, v in pp, v)
n1d1 = {"2O": 6 * SC - 3 * isqrt(2 * SC * SC), "2I": 9 * SC - 3 * isqrt(5 * SC * SC)}
for g, v in n1d1.items():
    out.append("INFO|name=T2_N1Delta1_%s|value=%s|json=0" % (g, fixed_dec(v, SC, 6)))

# ---------------------------------------------------------------- T3 (SU(2)_k)
rows3 = {}
for line in open(BASE + "/T3/ROWS.hbp"):
    f = line.rstrip("\n").split("|")
    d = dict(x.split("=", 1) for x in f[1:] if "=" in x)
    if "id" in d:
        rows3[d["id"]] = d
tab_text = open(BASE + "/T3/T3_TABLE.txt").read()
check("T3_table_sha256", hashlib.sha256(tab_text.encode()).hexdigest() == "3c8e7da5564a106b203d0b0fd8e5a87ce5b17f4370ab734f50880bf7359c526c")
lines = tab_text.split("\n")[:-1]
check("T3_table_12_lines", len(lines) == 12)
T = {}
for k in range(1, 13):
    r = rows3["T3-A%02d" % (12 + k)]
    rec = "k=%s|n=%s|M=%s" % (r["k"], r["n"], r["M"])
    check("T3_TABLE_row_k%d_equals_file_line" % k, rec == lines[k - 1])
    T[k] = [int(x) for x in r["M"].split(",")]
check("T3_odd_entries_zero", all(T[k][n] == 0 for k in T for n in range(1, 31, 2)))
check("T3_catalan_prefix", all(T[k][2 * m] == catalan(m) for k in T for m in range(0, min(k, 15) + 1)))
brk = rows3["T3-A03"]["predicted"]
check("T3_A03_break_values", all(("k%d:%d" % (k, catalan(k + 1) - 1)) in brk for k in range(1, 13)))
check("T3_A03_vs_table", all(T[k][2 * k + 2] == catalan(k + 1) - 1 for k in range(1, 13)))
okp = True
for k in range(1, 13):
    for r_, poly in ((1, 2 * k + 2), (2, 2 * k * k + 7 * k + 4)):
        m = k + 1 + r_
        if m <= 15:
            okp &= catalan(m) - T[k][2 * m] == poly
    m = k + 4
    if k >= 2 and m <= 15:
        okp &= (catalan(m) - T[k][2 * m]) * 3 == 2 * (k + 3) * (k + 4) * (2 * k + 1)
    m = k + 5
    N = 2 * k + 10
    if k >= 3 and m <= 15:
        okp &= (catalan(m) - T[k][2 * m]) * 24 == N * (N - 1) * (N * N - 13 * N + 34)
check("T3_A05_deficit_polynomials_vs_table", okp)
okr = True
for k in range(1, 13):
    for n in range(k + 1, 31):
        acc = 0
        for j in range(1, (k + 1) // 2 + 1):
            if n - 2 * j >= 0:
                acc += (-1) ** (j + 1) * binom(k + 1 - j, j) * T[k][n - 2 * j]
        okr &= acc == T[k][n]
check("T3_A09_recurrence_vs_table", okr)
check("T3_A12_monotone_in_k", all(T[k][n] <= T[k + 1][n] for k in range(1, 12) for n in range(31)))
for k in range(1, 13):
    num, den = -1, 4 ** (k + 1) * fact(2 * k + 2)
    nx = q(2 * k * k + 5 * k + 4, 4 ** (k + 2) * fact(2 * k + 4))
    r = rows3["T3-C02-k%02d" % k]
    check("T3_C02_k%d" % k, r["value"] == "%d:%d" % q(num, den) and r["next_value"] == qstr(nx)
          and r["first_nonzero_power"] == str(2 * k + 2) and r["next_power"] == str(2 * k + 4))
pil = rows3["T3-C03"]["predicted"]
check("T3_C03_pillow", all(("k%d -1:%d," % (k, fact(2 * k + 2))) in pil + "," for k in range(1, 13)))


def Ueval(k, X, Sc):
    # sign-exact value of U_{k+1}(x/2) * Sc^(k+1), x = X/Sc
    n = k + 1
    return sum((-1) ** j * binom(n - j, j) * X ** (n - 2 * j) * Sc ** (2 * j) for j in range(n // 2 + 1))


def dk(k):
    X = 2 * S
    step = S // 1000
    while Ueval(k, X, S) > 0:
        X -= step
    lo, hi = X, X + step
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if Ueval(k, mid, S) > 0:
            hi = mid
        else:
            lo = mid
    return lo


x2r = {1: q(1), 2: q(2), 4: q(3)}
X = {k: dk(k) for k in range(1, 13)}
for k in (1, 2, 4):
    check("T3_d_half_squared_exact_k%d" % k, abs(X[k] * X[k] - x2r[k][0] * S * S) < 5 * S)


def val(k, kind):
    # (num, den) for k in rational cases, else high-precision (num, den)
    if k in x2r:
        a, b = x2r[k]
        if kind == "tan2":
            return q(4 * b - a, a)
        if kind == "sec4m1":
            return q(16 * b * b - a * a, a * a)
        if kind == "sin2":
            return q(4 * b - a, 4 * b)
        if kind == "x2":
            return q(a, b)
    x2 = X[k] * X[k]
    SS = S * S
    if kind == "tan2":
        return (4 * SS - x2, x2)
    if kind == "sec4m1":
        return (16 * SS * SS - x2 * x2, x2 * x2)
    if kind == "sin2":
        return (4 * SS - x2, 4 * SS)
    if kind == "x2":
        return (x2, SS)


def tokens(txt):
    res = {}
    wds = txt.split(" ")
    for i in range(len(wds) - 1):
        wd = wds[i]
        if len(wd) > 1 and wd[0] == "k" and wd[1:].isdigit():
            v = wds[i + 1].rstrip(",;")
            if "=" in v:
                v = v.split("=")[-1]
            res[int(wd[1:])] = v
    return res


def cmp_token(tok, num, den):
    if ":" in tok:
        a, b = tok.split(":")
        return q(int(a), int(b)) == q(num, den)
    if "." not in tok and "e" not in tok:
        return q(int(tok)) == q(num, den)
    s, digits, e = parse_dec(tok)
    s2, m2, e2 = sci12(num, den)
    return s == s2 and e == e2 and digits == str(m2)[:len(digits)] if len(digits) == 12 else (s == s2 and e == e2 and digits == str(round_int(m2, 12 - len(digits))))


specs = [
    ("T3-C04", "tan2", 1, 16, range(1, 13), {}),
    ("T3-C05", "sec4m1", 1, 256, range(2, 13), {1: (37, 768)}),
    ("T3-C06", "sec4m1", 1, 1024, range(3, 13), {}),
    ("T3-C07", "sec4m1", 1, 3072, range(3, 13), {}),
    ("T3-C09", "sec4m1", 6, 3072, range(3, 13), {}),
    ("T3-C10", "x2", 1, 1, range(1, 13), {}),
    ("T3-C11", "sin2", -1, 3072, range(1, 13), {}),
    ("T3-C13", "tan2", -256, 1053, range(2, 13), {1: (-178, 351)}),
]
for rid, kind, mul, div, ks, special in specs:
    tk = tokens(rows3[rid]["predicted"])
    bad = []
    for k in ks:
        nm, dn = val(k, kind)
        if k not in tk or not cmp_token(tk[k], mul * nm, div * dn):
            bad.append(k)
    for k, (a, b) in special.items():
        if k not in tk or not cmp_token(tk[k], a, b):
            bad.append(k)
    check("T3_%s_coefficients" % rid.replace("T3-", ""), not bad, "bad_k=%s" % bad)
c06 = rows3["T3-C06"]["predicted"]
check("T3_C06_k1_k2", "k1: beta^4, -1:64" in c06 and "k2: beta^6, 43:15360" in c06
      and q(6 * -1, 384) == q(-1, 64) and qadd(q(3, 1024), q(-6, 46080)) == q(43, 15360))
c07 = rows3["T3-C07"]["predicted"]
check("T3_C07_k1_k2", "k1: first beta^4, -1:384 (then beta^6: 59:11520)" in c07 and "k2: first beta^6, 11:11520" in c07
      and qadd(q(1, 1024), q(-1, 46080)) == q(11, 11520) and qadd(q(15, 3 * 1024), q(11, 46080)) == q(59, 11520))
c09 = rows3["T3-C09"]["predicted"]
check("T3_C09_k1_k2", "k1: beta^3, -1:96" in c09 and "k2: beta^5, 11:1920" in c09 and qmul(q(6), q(11, 11520)) == q(11, 1920))
check("T3_C05_k1_exact", qadd(q(15, 256), q(-4, 384)) == q(37, 768))
check("T3_C13_k1_exact", qadd(q(-16, 81), q(-326, 1053)) == q(-178, 351))
# pi by Machin, for T3-C08
def arctan_inv(n, scale):
    s, term, k, sign = 0, scale // n, 1, 1
    while term:
        s += sign * (term // k)
        term //= n * n
        k += 2
        sign = -sign
    return s


PI = 16 * arctan_inv(5, S) - 4 * arctan_inv(239, S)
lim = PI * PI // 1536
check("T3_C08_pi2/1536=6.4255e-3", fixed_dec(lim, S * S, 7) == "0.0064255")
seq = []
for k in range(3, 13):
    nm, dn = val(k, "sec4m1")
    seq.append(nm * (k + 2) ** 2 * S * S // (dn * 3072))
check("T3_C08_c6(k)(k+2)^2_decreasing_and_above_limit", all(seq[i] > seq[i + 1] for i in range(len(seq) - 1)) and seq[-1] > lim)
# Hankel determinants of the SU(2) trace moments (Catalan with zeros): positive definiteness for T3-B03
def det(Mx):
    n = len(Mx)
    A = [r[:] for r in Mx]
    sign, prev = 1, 1
    for i in range(n):
        p = next((r for r in range(i, n) if A[r][i] != 0), None)
        if p is None:
            return 0
        if p != i:
            A[i], A[p] = A[p], A[i]
            sign = -sign
        for r in range(i + 1, n):
            for c in range(i + 1, n):
                A[r][c] = (A[r][c] * A[i][i] - A[r][i] * A[i][c]) // prev
        prev = A[i][i]
    return sign * A[n - 1][n - 1]


mom = [catalan(n // 2) if n % 2 == 0 else 0 for n in range(40)]
hd = [det([[mom[i + j] for j in range(N + 1)] for i in range(N + 1)]) for N in range(0, 14)]
check("T3_B03_Hankel_dets_SU2_moments_all_1_for_N<=13", all(h == 1 for h in hd), ",".join(str(h) for h in hd))

out.append("END|checks=%d|failed=%d|json=0" % (sum(1 for r in out if r.startswith("CHECK")), fails))
print("\n".join(out))
