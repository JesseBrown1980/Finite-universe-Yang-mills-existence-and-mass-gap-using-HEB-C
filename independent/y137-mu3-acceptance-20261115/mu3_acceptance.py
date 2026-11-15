#!/usr/bin/env python3
"""#137: the acceptance test for the real third moment, frozen before mu3 is computed.

Exact rational arithmetic only (integers and fractions.Fraction; no float, no division operator on numbers).

Setting (as in #197 and #198): X = b(QHQ - z) on Q, g <= X <= h, mu_k = B^T X^k B (8x8), F = B^T X^-1 B,
S(z) = U0 - F.

1. THE WINDOW FOR mu3.  The Gram matrices of the pair (B, XB) under the weights (X - g) and (h - X) are positive:

       [[mu1 - g mu0, mu2 - g mu1], [mu2 - g mu1, mu3 - g mu2]] >= 0
       [[h mu0 - mu1, h mu1 - mu2], [h mu1 - mu2, h mu2 - mu3]] >= 0

   so with D = mu1 - g mu0, C = mu2 - g mu1, E = h mu0 - mu1, G = h mu1 - mu2

       L = g mu2 + C D^-1 C  <=  mu3  <=  h mu2 - G E^-1 G = U        (Loewner order)

   A candidate mu3 is ACCEPTED only if it is an integer symmetric 8x8 matrix with L <= mu3 <= U.

2. THE FOUR-MOMENT BRACKET FOR S.  With tau = X^-1-weighted measure (moments F, mu0, mu1, mu2, mu3):

       Gauss   : F >= [mu0 mu1] [[mu1, mu2], [mu2, mu3]]^-1 [mu0; mu1]
       Lobatto : F <= ((g+h) mu0 - mu1 - b c^-1 b) / (g h),
                 b = (g+h) mu1 - mu2 - g h mu0,  c = (g+h) mu2 - mu3 - g h mu1

   so U0 - F_Lobatto <= S <= U0 - F_Gauss.

3. A KNOWN-ANSWER TEST.  A small integer X with known spectrum bounds and an integer B: the true mu3 lies in the
   window, the true S lies in the four-moment bracket, and tampered candidates are refused.

4. ON THE ARCHIVED mu0..mu2 at both energies: the window (against #197's cubic envelope), and the four-moment
   bracket evaluated at five scenario points of the window, as the range the real mu3 can produce.
"""
import os
import sys
from fractions import Fraction
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "y137-moment-radau-20261114"))
import moment_radau as mr  # the loaders, pins and integer helpers already on this branch

need, emit = mr.need, mr.emit
ONE = Fraction(1)


def F(m):
    return [[Fraction(x) for x in row] for row in m]


def n_of(m):
    return len(m)


def add(a, b):
    return [[x + y for x, y in zip(r, s)] for r, s in zip(a, b)]


def sub(a, b):
    return [[x - y for x, y in zip(r, s)] for r, s in zip(a, b)]


def scale(a, k):
    return [[x * k for x in r] for r in a]


def mul(a, b):
    cols = list(zip(*b))
    return [[sum(x * y for x, y in zip(r, c)) for c in cols] for r in a]


def tr(a):
    return [list(r) for r in zip(*a)]


def recip(x):
    need(x != 0, "zero_pivot")
    return Fraction(x.denominator, x.numerator)


def inv(a):
    n = n_of(a)
    t = [list(r) + [ONE if i == j else Fraction(0) for j in range(n)] for i, r in enumerate(a)]
    for k in range(n):
        p = next((i for i in range(k, n) if t[i][k] != 0), None)
        need(p is not None, "singular_matrix")
        t[k], t[p] = t[p], t[k]
        f = recip(t[k][k])
        t[k] = [x * f for x in t[k]]
        for i in range(n):
            if i != k and t[i][k] != 0:
                m = t[i][k]
                t[i] = [x - m * y for x, y in zip(t[i], t[k])]
    return [r[n:] for r in t]


def symmetric(a):
    n = n_of(a)
    return all(a[i][j] == a[j][i] for i in range(n) for j in range(n))


def to_int(a):
    den = 1
    for r in a:
        for x in r:
            den = den * x.denominator // gcd(den, x.denominator)
    return [[int(x * den) for x in r] for r in a]


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def det_int(a):
    n = len(a)
    t = [row[:] for row in a]
    sign, prev = 1, 1
    for k in range(n - 1):
        if t[k][k] == 0:
            swap = next((i for i in range(k + 1, n) if t[i][k]), None)
            if swap is None:
                return 0
            t[k], t[swap] = t[swap], t[k]
            sign = -sign
        piv = t[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                t[i][j] = (piv * t[i][j] - t[i][k] * t[k][j]) // prev
        prev = piv
    return sign * t[-1][-1]


def psd(a):
    """positive semidefinite: every principal minor is >= 0 (exact)."""
    need(symmetric(a), "nonsymmetric_matrix_in_order_test")
    m, n = to_int(a), n_of(a)
    for d in range(1, n + 1):
        for ix in combinations(range(n), d):
            if det_int([[m[i][j] for j in ix] for i in ix]) < 0:
                return False
    return True


def pd(a):
    need(symmetric(a), "nonsymmetric_matrix")
    m, n = to_int(a), n_of(a)
    return all(det_int([row[:k] for row in m[:k]]) > 0 for k in range(1, n + 1))


def le(a, b):
    return psd(sub(b, a))


def trace(a):
    return sum(a[i][i] for i in range(n_of(a)))


def window(mu0, mu1, mu2, g, h):
    D, C = sub(mu1, scale(mu0, g)), sub(mu2, scale(mu1, g))
    E, G = sub(scale(mu0, h), mu1), sub(scale(mu1, h), mu2)
    need(pd(D) and pd(E), "weighted_Gram_blocks_not_positive_definite")
    L = add(scale(mu2, g), mul(mul(C, inv(D)), C))
    U = sub(scale(mu2, h), mul(mul(G, inv(E)), G))
    need(symmetric(L) and symmetric(U), "window_symmetry")
    return L, U


def accept(cand, L, U):
    """the acceptance test for a candidate mu3: (accepted, reason)."""
    n = n_of(L)
    if len(cand) != n or any(len(r) != n for r in cand):
        return False, "shape"
    if any(Fraction(x).denominator != 1 for r in cand for x in r):
        return False, "not_integer"
    c = F(cand)
    if not symmetric(c):
        return False, "not_symmetric"
    if not le(L, c):
        return False, "below_the_window"
    if not le(c, U):
        return False, "above_the_window"
    return True, "inside_the_window"


def bracket3(U0, mu0, mu1, mu2, g, h):
    D, C = sub(mu1, scale(mu0, g)), sub(mu2, scale(mu1, g))
    E, G = sub(scale(mu0, h), mu1), sub(scale(mu1, h), mu2)
    lo = sub(U0, scale(sub(mu0, mul(mul(D, inv(C)), D)), Fraction(1, g)))
    hi = sub(U0, scale(add(mu0, mul(mul(E, inv(G)), E)), Fraction(1, h)))
    return lo, hi


def bracket4(U0, mu0, mu1, mu2, mu3, g, h):
    s, gh = g + h, g * h
    a_inv = inv(mu1)
    P = sub(mu3, mul(mul(mu2, a_inv), mu2))
    need(pd(P), "Gauss_block_not_positive_definite")
    T = sub(mu1, mul(mul(mu2, a_inv), mu0))
    f_gauss = add(mul(mul(mu0, a_inv), mu0), mul(mul(tr(T), inv(P)), T))
    b = sub(sub(scale(mu1, s), mu2), scale(mu0, gh))
    c = sub(sub(scale(mu2, s), mu3), scale(mu1, gh))
    need(pd(c), "Lobatto_block_not_positive_definite")
    f_lob = scale(sub(sub(scale(mu0, s), mu1), mul(mul(b, inv(c)), b)), Fraction(1, gh))
    return sub(U0, f_lob), sub(U0, f_gauss)


def ppm(x, y):
    q = Fraction(x) * 1000000 * recip(Fraction(y))
    return q.numerator // q.denominator


def known_answer():
    """a 12-state X with integer entries, 3 columns in B: every quantity exact."""
    n, k = 12, 3
    seed = 20261115
    def nxt():
        nonlocal seed
        seed = (seed * 1103515245 + 12345) % 2147483648
        return seed
    X = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            v = nxt() % 7 - 3
            X[i][j] = X[j][i] = v
    radius = max(sum(abs(X[i][j]) for j in range(n) if j != i) for i in range(n))
    for i in range(n):
        X[i][i] = 60 + nxt() % 40
    g, h = 60 - radius, 99 + radius          # Gershgorin: every eigenvalue lies in [g, h]
    need(g > 0, "known_answer_g_positive")
    B = [[nxt() % 9 - 4 for _ in range(k)] for _ in range(n)]
    Xf, Bf = F(X), F(B)
    V1 = mul(Xf, Bf)
    mu0, mu1 = mul(tr(Bf), Bf), mul(tr(Bf), V1)
    mu2, mu3 = mul(tr(V1), V1), mul(tr(V1), mul(Xf, V1))
    Ftrue = mul(tr(Bf), mul(inv(Xf), Bf))
    U0 = scale(mu0, Fraction(1))
    S = sub(U0, Ftrue)
    L, U = window(mu0, mu1, mu2, g, h)
    ok_true, why = accept([[int(x) for x in r] for r in mu3], L, U)
    lo3, hi3 = bracket3(U0, mu0, mu1, mu2, g, h)
    lo4, hi4 = bracket4(U0, mu0, mu1, mu2, mu3, g, h)
    in3 = le(lo3, S) and le(S, hi3)
    in4 = le(lo4, S) and le(S, hi4)
    nested = le(lo3, lo4) and le(hi4, hi3)
    # tampered candidates
    big = [[int(x) for x in r] for r in mu3]
    step = int(trace(sub(U, L))) + 1
    up = [r[:] for r in big]; up[0][0] += step
    down = [r[:] for r in big]; down[0][0] -= step
    skew = [r[:] for r in big]; skew[0][1] += 1
    r_up, r_down, r_skew = accept(up, L, U), accept(down, L, U), accept(skew, L, U)
    emit("Y137_MU3_KNOWN_ANSWER", states=n, columns=k, g=g, h=h, true_mu3_accepted=int(ok_true), reason=why,
         true_S_inside_three_moment_bracket=int(in3), true_S_inside_four_moment_bracket=int(in4),
         four_moment_inside_three_moment=int(nested),
         width_four_per_million_of_three=ppm(trace(sub(hi4, lo4)), trace(sub(hi3, lo3))),
         tampered_above=r_up[1], tampered_below=r_down[1], tampered_asymmetric=r_skew[1])
    need(ok_true and in3 and in4 and nested, "known_answer_failed")
    need(not r_up[0] and not r_down[0] and not r_skew[0], "tampered_candidate_was_accepted")


def archived(index):
    src = mr.read(mr.CACHE, "source", "Y137_CACHE_POINT")[index]
    m1 = mr.read(mr.MU1, "mu1", "Y137_MU1_COMPLETE_POINT")[index]
    m2 = mr.read(mr.MU2, "mu2", "Y137_D11_MU2_POINT")[index]
    n2 = mr.read(mr.N2, None, "Y137_N2_ENVELOPE_POINT")[index]
    z = mr.Z[index]
    U0i, G0 = mr.matrix(src["U0"]), mr.matrix(src["G0"])
    M0i = [[x // 6 for x in row] for row in G0]
    M1i, M2i = mr.matrix(m1["exact_mu1_8x8"]), mr.matrix(m2["actual_K3_mu2_8x8"])
    need(mr.sha(M0i) == m1["wholeQ_mu0_sha256"] and mr.sha(M1i) == m1["wholeQ_mu1_sha256"]
         and mr.sha(M2i) == m2["actual_K3_mu2_sha256"], "frozen_three_real_moment_hashes")
    g, h = 94068200000 - z, 468000000000 - z
    U0, mu0, mu1, mu2 = F(U0i), F(M0i), F(M1i), F(M2i)
    L, U = window(mu0, mu1, mu2, g, h)
    need(le(L, U), "window_is_empty")
    # the cubic envelope of #197
    env_lo, env_hi = F(mr.matrix(n2["mu3_lower_8x8"])), F(mr.matrix(n2["mu3_upper_8x8"]))
    inside_env = le(env_lo, L) and le(U, env_hi)
    w_env, w_win = trace(sub(env_hi, env_lo)), trace(sub(U, L))
    lo3, hi3 = bracket3(U0, mu0, mu1, mu2, g, h)
    w3 = trace(sub(hi3, lo3))
    w_orig = trace(scale(mu0, Fraction(1, g)))
    emit("Y137_MU3_WINDOW", sample_num=z, window_nonempty=1, window_inside_197_cubic_envelope=int(inside_env),
         window_trace_per_million_of_197_envelope=ppm(w_win, w_env),
         window_lower_integer_sha256=mr.sha(to_int(L)), window_upper_integer_sha256=mr.sha(to_int(U)),
         three_moment_width_per_million_of_original=ppm(w3, w_orig))
    target = index + 1
    rows = []
    for num in (1, 2, 4, 6, 7):                      # scenario points L + (num/8)(U - L)
        t = Fraction(num, 8)
        m3 = add(L, scale(sub(U, L), t))
        lo4, hi4 = bracket4(U0, mu0, mu1, mu2, m3, g, h)
        nested = le(lo3, lo4) and le(hi4, hi3) and le(lo4, hi4)
        w4 = trace(sub(hi4, lo4))
        neg = [mr.inertia(to_int(x)) for x in (hi4, lo4)]
        rows.append((num, ppm(w4, w_orig), ppm(w4, w3), int(nested), neg))
        emit("Y137_MU3_SCENARIO", sample_num=z, point_eighths=num,
             four_moment_width_per_million_of_original=ppm(w4, w_orig),
             four_moment_width_per_million_of_three_moment=ppm(w4, w3),
             inside_three_moment_bracket=int(nested), inertia_upper=neg[0], inertia_lower=neg[1],
             target_negative_inertia=target)
    return inside_env, rows


def main():
    known_answer()
    out = [archived(0), archived(1)]
    emit("Y137_MU3_ACCEPTANCE", samples=2, known_answer="PASS",
         real_mu3="NOT_COMPUTED", window_inside_197_envelope=int(all(o[0] for o in out)),
         scenario_points_nested=int(all(r[3] for o in out for r in o[1])),
         widest_scenario_per_million_of_three_moment=max(r[2] for o in out for r in o[1]),
         narrowest_scenario_per_million_of_three_moment=min(r[2] for o in out for r in o[1]),
         Wilson_weight="HOLD")


if __name__ == "__main__":
    main()
