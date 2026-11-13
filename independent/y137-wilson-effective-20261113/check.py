#!/usr/bin/env python3
"""Issue #137: independent exact S3 Wilson tests and a Feshbach identity control.

No claim about the actual full-space E1->E2 Wilson weight is made by this test.
The full 24-link operator is checked without importing the original graph code.
The 3x3 integer Schur example tests cancellation between P and Q contributions.
"""
from itertools import permutations
from math import gcd

LX = 3
LY = 4
V = LX * LY
PERMS = tuple(permutations(range(3)))
LOC = {p: k for k, p in enumerate(PERMS)}
MUL = tuple(
    tuple(LOC[tuple(a[b[j]] for j in range(3))] for b in PERMS)
    for a in PERMS
)
INV = tuple(
    next(j for j in range(6) if MUL[i][j] == 0 and MUL[j][i] == 0)
    for i in range(6)
)
CHAR = tuple(sum(1 for j in range(3) if p[j] == j) - 1 for p in PERMS)


def pos(x, y):
    return (y % LY) * LX + (x % LX)


def prod(words):
    ans = 0
    for u in words:
        ans = MUL[ans][u]
    return ans


def wilson_sum(u):
    """Four horizontal length-3 and three vertical length-4 characters."""
    assert len(u) == 2 * V
    horizontal = sum(
        CHAR[prod(u[pos(x, y)] for x in range(LX))] for y in range(LY)
    )
    vertical = sum(
        CHAR[prod(u[V + pos(x, y)] for y in range(LY))] for x in range(LX)
    )
    return horizontal + vertical


def gauge(u, g):
    """U_e maps to g_source U_e g_target^{-1} at all 24 links."""
    assert len(g) == V
    ans = [0] * (2 * V)
    for y in range(LY):
        for x in range(LX):
            k = pos(x, y)
            ans[k] = MUL[g[k]][MUL[u[k]][INV[g[pos(x + 1, y)]]]]
            ans[V + k] = MUL[g[k]][MUL[u[V + k]][INV[g[pos(x, y + 1)]]]]
    return ans


def translate(u, sx, sy):
    ans = [0] * (2 * V)
    for y in range(LY):
        for x in range(LX):
            k = pos(x, y)
            src = pos(x - sx, y - sy)
            ans[k] = u[src]
            ans[V + k] = u[V + src]
    return ans


def reflect_x(u):
    """Reflection x -> -x reverses horizontal oriented links."""
    ans = [0] * (2 * V)
    for y in range(LY):
        for x in range(LX):
            k = pos(x, y)
            ans[k] = INV[u[pos(-x - 1, y)]]
            ans[V + k] = u[V + pos(-x, y)]
    return ans


def row_zero(u):
    return CHAR[prod(u[pos(x, 0)] for x in range(LX))]


def fixtures():
    rows = [[0] * (2 * V)]
    for k in range(2 * V):
        u = [0] * (2 * V)
        u[k] = 1 + k % 5
        rows.append(u)
    for k in range(27):
        rows.append([(k + 3 * j + j * j) % 6 for j in range(2 * V)])
    assert len(rows) == 52
    return rows


def symmetry_replay():
    assert sorted(set(CHAR)) == [-1, 0, 2]
    assert all(CHAR[INV[g]] == CHAR[g] for g in range(6))
    assert all(MUL[g][INV[g]] == 0 for g in range(6))
    samples = fixtures()
    gauge_checks = 0
    translation_checks = 0
    reflection_checks = 0
    for u in samples:
        observed = wilson_sum(u)
        assert -7 <= observed <= 14
        # For a shifted observable O - 7/2, |2*O - 7| <= 21.
        assert abs(2 * observed - 7) <= 21
        for v in range(V):
            for group in range(6):
                g = [0] * V
                g[v] = group
                assert wilson_sum(gauge(u, g)) == observed
                gauge_checks += 1
        for sx in range(LX):
            for sy in range(LY):
                assert wilson_sum(translate(u, sx, sy)) == observed
                translation_checks += 1
        assert wilson_sum(reflect_x(u)) == observed
        reflection_checks += 1

    # The 18 commuting ordered pairs form eight simultaneous-conjugacy
    # classes: an independent eight-flat count for the periodic S3 torus.
    commuting = 0
    classes = set()
    for a in range(6):
        for b in range(6):
            if MUL[a][b] != MUL[b][a]:
                continue
            commuting += 1
            u = [0] * (2 * V)
            for y in range(LY):
                u[pos(LX - 1, y)] = a
            for x in range(LX):
                u[V + pos(x, LY - 1)] = b
            assert wilson_sum(u) == 4 * CHAR[a] + 3 * CHAR[b]
            classes.add(min(
                (MUL[g][MUL[a][INV[g]]], MUL[g][MUL[b][INV[g]]])
                for g in range(6)
            ))
    assert commuting == 18
    assert len(classes) == 8

    # Negative controls: a single-link character is not gauge invariant,
    # and a single-row winding character is not translation invariant.
    zero = [0] * (2 * V)
    changed = [0] * V
    changed[0] = 1
    assert CHAR[gauge(zero, changed)[0]] != CHAR[zero[0]]
    one_link = [0] * (2 * V)
    one_link[0] = 1
    assert row_zero(one_link) != row_zero(translate(one_link, 0, 1))
    assert gauge_checks == 3744
    assert translation_checks == 624
    assert reflection_checks == 52
    print(
        f"Y137_WILSON_FULLSPACE|fixtures={len(samples)}"
        f"|gauge={gauge_checks}|translations={translation_checks}"
        f"|reflections={reflection_checks}|commuting_pairs={commuting}"
        f"|flat_orbits={len(classes)}|negative_controls=2|status=PASS|json=0"
    )


def dot(x, y):
    assert len(x) == len(y)
    return sum(a * b for a, b in zip(x, y))


def matvec(h, x):
    return [dot(row, x) for row in h]


def schur_replay():
    """Toy integer H3, P dimension two, Q dimension one, both Q tails nonzero."""
    h = [
        [11, -16, -11],
        [-16, 38, 16],
        [-11, 16, 11],
    ]
    eigen = [
        (0, (1, 0, 1)),
        (6, (1, 1, -1)),
        (54, (-1, 2, 1)),
    ]
    for lam, v in eigen:
        assert matvec(h, v) == [lam * x for x in v]
    assert dot(eigen[0][1], eigen[1][1]) == 0
    assert dot(eigen[0][1], eigen[2][1]) == 0
    assert dot(eigen[1][1], eigen[2][1]) == 0
    a = (h[0][:2], h[1][:2])
    b = (h[2][0], h[2][1])
    d = h[2][2]
    assert d == 11 and d > 6
    ys = []
    for lam, v in eigen[:2]:
        x = v[:2]
        den = d - lam
        bx = dot(b, x)
        assert den > 0
        # Exact Schur residual: (A - lam I)*x - B^T B*x/(D-lam) = 0.
        for j in range(2):
            assert den * (dot(a[j], x) - lam * x[j]) - b[j] * bx == 0
        assert (-bx) % den == 0
        y = (-bx) // den
        assert y == v[2]
        ys.append(y)
    x1 = eigen[0][1][:2]
    x2 = eigen[1][1][:2]
    y1, y2 = ys
    op = (2, -1, 4)
    p = sum(x2[k] * op[k] * x1[k] for k in range(2))
    q = y2 * op[2] * y1
    full = sum(eigen[1][1][k] * op[k] * eigen[0][1][k] for k in range(3))
    assert (p, q, full) == (2, -4, -2)
    assert p + q == full
    n1 = dot(eigen[0][1], eigen[0][1])
    n2 = dot(eigen[1][1], eigen[1][1])
    num = full * full
    den = n1 * n2
    gg = gcd(num, den)
    assert (num // gg, den // gg) == (2, 3)

    # A nontrivial dark control: identity must have zero E1->E2 overlap,
    # including the Q term. Dropping Q gives the wrong answer.
    dark = dot(x1, x2) + y1 * y2
    assert dark == 0
    assert p != full

    # An intentionally faulty P-Q coupling must break the Schur equation.
    bad_b = (-10, 16)
    assert (dot(bad_b, x1) % (d - 0)) != 0

    # Fully exact residual-bound calibration on the same toy.
    # yhat_1=2, yhat_2=-1, ||r_1||=11 and d-lambda_1=11.
    yhat1, yhat2 = 2, -1
    residual1 = (d - 0) * yhat1 + dot(b, x1)
    residual2 = (d - 6) * yhat2 + dot(b, x2)
    assert (residual1, residual2) == (11, 0)
    eps1, eps2 = 1, 0
    assert abs(residual1) <= (d - 0) * eps1
    assert abs(residual2) <= (d - 6) * eps2
    trial = p + yhat2 * op[2] * yhat1
    certified_err = abs(op[2]) * (
        abs(yhat2) * eps1 + abs(yhat1) * eps2 + eps1 * eps2
    )
    assert trial == -6 and abs(trial - full) == certified_err == 4
    assert not (abs(trial - full) <= 3)
    print(
        "Y137_SCHUR_TOY|P_dim=2|Q_dim=1|lambda=0,6,54"
        "|flat_amp=2|tail_amp=-4|full_amp=-2|weight=2/3"
        "|identity_dark=0|faulty_coupling_rejected=1"
        "|tail_omission_rejected=1|residual_bound=4"
        "|status=PASS|json=0"
    )


if __name__ == "__main__":
    symmetry_replay()
    schur_replay()
    print("Y137_NEXT_VERDICT|scope=observable_algebra_and_toy_only|status=PASS|full_weight=OPEN|json=0")
