# T3 closed-form evaluation. Integer arithmetic only (no float, fractions, decimal, math).
# No fusion-rule iteration and no path enumeration: every number below is a binomial,
# Catalan or factorial expression from NOTE.md, or a root of the integer polynomial U_{k+1}(x/2).
import sys

KS = range(1, 13)
NMAX = 30


def gcd(a, b):
    a = -a if a < 0 else a
    b = -b if b < 0 else b
    while b:
        a, b = b, a % b
    return a


def R(n, d=1):
    if d < 0:
        n, d = -n, -d
    g = gcd(n, d)
    return (n // g, d // g)


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


def sci(num, den, sig=12):
    # decimal string of num/den with sig significant digits, integers only
    if num == 0:
        return "0"
    sign = "-" if (num < 0) != (den < 0) else ""
    num, den = abs(num), abs(den)
    e = 0
    while num >= den * 10 ** (e + 1):
        e += 1
    while num < den * 10 ** e:
        e -= 1
    shift = sig - 1 - e
    if shift >= 0:
        q = (2 * num * 10 ** shift + den) // (2 * den)
    else:
        q = (2 * num + den * 10 ** (-shift)) // (2 * den * 10 ** (-shift))
    if q >= 10 ** sig:
        q //= 10
        e += 1
    s = str(q)
    return "%s%s.%se%d" % (sign, s[0], s[1:], e)


out = []
fails = 0


def check(name, ok, detail=""):
    global fails
    if not ok:
        fails += 1
    out.append("CHECK|name=%s|result=%s|%s|json=0" % (name, "PASS" if ok else "FAIL", detail))


C = [catalan(m) for m in range(16)]
out.append("CATALAN|m=0..15|C=%s|json=0" % ",".join(str(c) for c in C))

table_lines = []
for k in KS:
    M = [reflection(n, k) for n in range(NMAX + 1)]
    table_lines.append("k=%d|n=0..30|M=%s" % (k, ",".join(str(x) for x in M)))
    ok = all(M[n] == 0 for n in range(1, NMAX + 1, 2))
    ok = ok and all(M[2 * m] == C[m] for m in range(min(k, 15) + 1))
    if 2 * k + 2 <= NMAX:
        ok = ok and M[2 * k + 2] == C[k + 1] - 1
    check("k%d_reflection_prefix_and_break" % k, ok)
    # Cayley-Hamilton identity on the reflection values
    rec = True
    for n in range(k + 1, NMAX + 1):
        s = 0
        j = 1
        while 2 * j <= k + 1:
            s += (-1) ** (j + 1) * binom(k + 1 - j, j) * M[n - 2 * j]
            j += 1
        rec = rec and s == M[n]
    check("k%d_reflection_satisfies_U_recurrence" % k, rec)
    P = lambda h: [(-1) ** j * binom(h - j, j) for j in range(16)]
    num, den = P(k), P(k + 1)
    q = [0] * 16
    for i in range(16):
        acc = num[i]
        for t in range(1, i + 1):
            acc -= den[t] * q[i - t]
        q[i] = acc
    check("k%d_gf_matches_reflection" % k, all(q[m] == M[2 * m] for m in range(16)))
    D = [C[m] - M[2 * m] for m in range(16)]
    polys = {0: 1, 1: 2 * k + 2, 2: 2 * k * k + 7 * k + 4, 3: 2 * (k + 3) * (k + 4) * (2 * k + 1) // 3}
    N5 = 2 * k + 10
    polys[4] = N5 * (N5 - 1) * (N5 * N5 - 13 * N5 + 34) // 24
    pk = True
    for r, v in polys.items():
        m = k + 1 + r
        if r <= k + 1 and m <= 15:
            pk = pk and D[m] == v
    for m in range(16):
        if m <= 2 * k + 2:
            r = m - k - 1
            three = binom(2 * m, r) - 2 * binom(2 * m, r - 1) + binom(2 * m, r - 2)
            pk = pk and D[m] == three
    check("k%d_deficit_polys" % k, pk, "D=%s" % ",".join(str(x) for x in D))

with open("T3_TABLE.txt", "w") as fh:
    fh.write("\n".join(table_lines) + "\n")
for line in table_lines:
    out.append("TABLE|" + line + "|json=0")

for k in KS:
    out.append("BREAK|k=%d|t_fp=%d|n_break=%d|M_break=%d|C=%d|deficit=1|D_k+2=%d|D_k+3=%d|json=0" % (
        k, 2 * k + 1, 2 * k + 2, C[k + 1] - 1 if k + 1 <= 15 else -1, C[k + 1], 2 * k + 2, 2 * k * k + 7 * k + 4))

for k in KS:
    v1 = R(-1, 4 ** (k + 1) * fact(2 * k + 2))
    v2 = R(2 * k * k + 5 * k + 4, 4 ** (k + 2) * fact(2 * k + 4))
    out.append("GAUGE2D|k=%d|first_power=%d|value=%s|next_power=%d|next_value=%s|json=0" % (
        k, 2 * k + 2, rs(v1), 2 * k + 4, rs(v2)))

S = 1 << 200


def U_scaled(n1, X):
    if n1 == 0:
        return 1
    p0, p1 = 1, X
    for _ in range(1, n1):
        p0, p1 = p1, X * p1 - S * S * p0
    return p1


for k in KS:
    n = k + 2
    lo, hi = 2 * S - (20 * S) // (n * n), 2 * S
    ok = U_scaled(k + 1, lo) < 0 < U_scaled(k + 1, hi)
    for _ in range(230):
        mid = (lo + hi) // 2
        if U_scaled(k + 1, mid) > 0:
            hi = mid
        else:
            lo = mid
    X = hi
    X2, X4, S2, S4 = X * X, X ** 4, S * S, S ** 4
    d_str = sci(X, S)
    cube = (16 * S4 - X4, 3072 * X4)           # (sec^4 - 1)/3072 = (1/[2]^4 - 1/16)/192
    surf = (16 * S4 - X4, 1024 * X4)           # single open cube: 3 x cube
    t12 = (4 * S2 - X2, 16 * X2)               # tan^2/16
    t22 = (16 * S4 - X4, 256 * X4)             # (sec^4 - 1)/256
    var = (-(4 * S2 - X2), 4 * S2 * 3072)      # -sin^2/3072
    ham = (-256 * (4 * S2 - X2), 1053 * X2)    # -(256/1053) tan^2
    out.append("QDIM|k=%d|bisect_bracket_ok=%d|d_half=%s|d_half_sq=%s|c6_cube_part=%s|open_cube_beta6=%s|torus1x2_beta2=%s|torus2x2_beta4=%s|variant_u_beta6=%s|ham_dc4_formula=%s|json=0" % (
        k, 1 if ok else 0, d_str, sci(X2, S2), sci(*cube), sci(*surf), sci(*t12), sci(*t22), sci(*var), sci(*ham)))
    check("k%d_bisect_bracket" % k, ok)
    # first differing order and coefficient per observable, with the small-k corrections of NOTE.md
    if k == 1:
        f3 = "4:%s" % sci(-1, 384)
        oc = "4:%s" % sci(-1, 64)
        t22s = "4:%s" % sci(37, 768)
        plq = "3:%s" % sci(-1, 96)
        hm = sci(-178, 351)
    elif k == 2:
        f3 = "6:%s" % sci(11, 11520)
        oc = "6:%s" % sci(43, 15360)
        t22s = "4:%s" % sci(*t22)
        plq = "5:%s" % sci(11, 1920)
        hm = sci(*ham)
    else:
        f3 = "6:%s" % sci(*cube)
        oc = "6:%s" % sci(*surf)
        t22s = "4:%s" % sci(*t22)
        plq = "5:%s" % sci(6 * cube[0], cube[1])
        hm = sci(*ham)
    out.append("FIRSTDIFF|k=%d|f3D=%s|dP3D=%s|open_cube=%s|torus1x2=2:%s|torus2x2=%s|pillow=%d:%s|f2D_free=%d:%s|variant_u_f3D=6:%s|ham_dc4_conj=%s|psi6=%s|json=0" % (
        k, f3, plq, oc, sci(*t12), t22s, 2 * k + 2, sci(-1, fact(2 * k + 2)),
        2 * k + 2, sci(-1, 4 ** (k + 1) * fact(2 * k + 2)), sci(*var), hm, sci(X2, S2)))

# exact anchors for the decimal routine
check("anchor_k4", sci(7, 27648) == "2.53182870370e-4")
check("anchor_k2_cube", sci(1, 1024) == "9.76562500000e-4")

for line in out:
    print(line)
print("END|checks=%d|failed=%d|json=0" % (sum(1 for r in out if r.startswith("CHECK")), fails))
sys.exit(1 if fails else 0)
