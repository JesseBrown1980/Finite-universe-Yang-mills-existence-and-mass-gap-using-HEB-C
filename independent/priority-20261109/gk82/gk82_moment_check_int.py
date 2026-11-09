"""Integer/rational check of the hand arithmetic reported by the B-hunter lane.

Question: are Grosse-Kuehnelt 1982's printed beta^3 differences of the plaquette
energy E(beta) for Delta(6 n^2) against SU(3) (1/972 for n=4, 1/1296 for n>=6)
equal to the single-plaquette moment defect Delta E[f^4]/3!, with f = Re tr U / 3?

Method: enumerate Delta(6 n^2) inside SU(3) as D*P (P cyclic, a+b+c=0 mod n) and
-D*P (P a transposition), take traces in Z[x]/(x^n - 1), average |t|^2k and t^k
exactly, reduce mod the n-th cyclotomic polynomial, and read the rational constant.
SU(3) Haar values used: E|t|^2=1, E t^3=1, E|t|^4=2, E t^4=0, E t^2 conj(t)=0,
E t^3 conj(t)=0 (triality and Schur counting; NAMED inputs, not computed here).
Integer pairs only (reduced num, den), no Fraction, no floats. Output: HBP rows on stdout.
Port of gk82_moment_check.py (Fraction version, sha256 3c46c79c...), whose GK82_CHECK rows it reproduces.
"""
import sys
from math import gcd


def ipow(b, e):
    """b to a non-negative integer power, by repeated multiplication."""
    if e < 0:
        raise ValueError("negative exponent")
    r = 1
    for _ in range(e):
        r *= b
    return r


class Q:
    """A reduced integer pair num, den with den > 0 and gcd 1, checked after every operation."""

    __slots__ = ("n", "d")

    def __init__(self, n, d=1):
        if type(n) is not int or type(d) is not int or d == 0:
            raise TypeError("Q takes two ints with den != 0")
        if d < 0:
            n, d = -n, -d
        g = gcd(n, d)
        self.n, self.d = n // g, d // g

    def __add__(self, o):
        o = o if isinstance(o, Q) else Q(o)
        return Q(self.n * o.d + o.n * self.d, self.d * o.d)

    __radd__ = __add__

    def __neg__(self):
        return Q(-self.n, self.d)

    def __sub__(self, o):
        return self + (-(o if isinstance(o, Q) else Q(o)))

    def __mul__(self, o):
        o = o if isinstance(o, Q) else Q(o)
        return Q(self.n * o.n, self.d * o.d)

    __rmul__ = __mul__

    def over(self, k):
        """Division by a nonzero int k."""
        return Q(self.n, self.d * k)

    def __eq__(self, o):
        o = o if isinstance(o, Q) else Q(o)
        return self.n * o.d == o.n * self.d

    def __hash__(self):
        return hash((self.n, self.d))

    def __str__(self):
        return str(self.n) if self.d == 1 else "%d%s%d" % (self.n, chr(47), self.d)

def pmul(a, b, n):
    r = [0] * n
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    r[(i + j) % n] += x * y
    return r

def padd(a, b):
    return [x + y for x, y in zip(a, b)]

def conj(a, n):
    r = [0] * n
    for i, x in enumerate(a):
        r[(-i) % n] += x
    return r

def polydivmod(num, den):
    num = num[:]
    q = [0] * max(1, len(num) - len(den) + 1)
    while len(num) >= len(den) and any(num):
        while num and num[-1] == 0:
            num.pop()
        if len(num) < len(den):
            break
        c = num[-1] // den[-1]
        assert c * den[-1] == num[-1]
        k = len(num) - len(den)
        q[k] = c
        for i, d in enumerate(den):
            num[i + k] -= c * d
        while num and num[-1] == 0:
            num.pop()
    return q, num

_cyc = {}
def cyclotomic(n):
    if n in _cyc:
        return _cyc[n]
    p = [-1] + [0] * (n - 1) + [1]
    for d in range(1, n):
        if n % d == 0:
            p, rem = polydivmod(p, cyclotomic(d))
            assert not any(rem)
    while p and p[-1] == 0:
        p.pop()
    _cyc[n] = p
    return p

def value(a, n):
    """Reduce a (in Z[x]/(x^n-1)) mod Phi_n; must be a rational constant."""
    _, rem = polydivmod(a[:], cyclotomic(n))
    rem = rem + [0]
    assert not any(rem[1:]), ("not constant", rem)
    return rem[0]

def mono(e, n, s=1):
    r = [0] * n
    r[e % n] = s
    return r

def traces(n):
    out = []
    for a in range(n):
        for b in range(n):
            c = (-a - b) % n
            out.append(padd(padd(mono(a, n), mono(b, n)), mono(c, n)))  # P = identity
            out.append([0] * n)  # P = cyclic
            out.append([0] * n)  # P = cyclic^2
            for k in (a, b, c):  # three transpositions times -1: trace -omega^{a_k}
                out.append(mono(k, n, -1))
    return out

def moment(ts, n, p, q):
    acc = [0] * n
    for t in ts:
        m = mono(0, n)
        for _ in range(p):
            m = pmul(m, t, n)
        ct = conj(t, n)
        for _ in range(q):
            m = pmul(m, ct, n)
        acc = padd(acc, m)
    return Q(value(acc, n), len(ts))

def f_moment(mom, k):
    # E[f^k], f = (t + conj t)/6
    from math import comb
    s = sum(comb(k, j) * mom[(j, k - j)] for j in range(k + 1))
    return (s if isinstance(s, Q) else Q(s)).over(ipow(6, k))

su3 = {(1, 0): 0, (0, 1): 0, (2, 0): 0, (1, 1): 1, (0, 2): 0, (3, 0): 1, (2, 1): 0,
       (1, 2): 0, (0, 3): 1, (4, 0): 0, (3, 1): 0, (2, 2): 2, (1, 3): 0, (0, 4): 0}
su3 = {k: Q(v) for k, v in su3.items()}

def coeffs(mom):
    e2, e3, e4 = f_moment(mom, 2), f_moment(mom, 3), f_moment(mom, 4)
    e1 = f_moment(mom, 1)
    assert e1 == 0
    # <f> = kappa2 b + kappa3 b^2 over 2 + kappa4 b^3 over 6, mean zero
    return e2, e3.over(2), (e4 - 3 * e2 * e2).over(6)

print("GK82_CHECK_HEAD|script=gk82_moment_check_int.py|arith=integer_pairs_only|float_used=0|json=0")
c_su3 = coeffs(su3)
print("GK82_CHECK|group=SU(3)_Haar_named_inputs|plaq_b1=%s|plaq_b2=%s|plaq_b3=%s|json=0" % tuple(str(x) for x in c_su3))
for n in (4, 6, 8):
    ts = traces(n)
    assert len(ts) == 6 * n * n
    mom = {k: moment(ts, n, k[0], k[1]) for k in su3}
    c = coeffs(mom)
    d4 = f_moment(mom, 4) - f_moment(su3, 4)
    print("GK82_CHECK|group=Delta(6*%d*%d)|order=%d|E_abs_t_4=%s|E_t_4=%s|E_t_3=%s|plaq_b1=%s|plaq_b2=%s|plaq_b3=%s|Delta_E_f4=%s|Delta_E_f4_over_3fact=%s|E_series_b3=%s|json=0"
          % (n, n, len(ts), mom[(2, 2)], mom[(4, 0)], mom[(3, 0)], c[0], c[1], c[2], d4, d4.over(6), -c[2]))
