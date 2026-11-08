#!/usr/bin/env python3
"""Second-reviewer reconstruction of PR #136's 3x4 S3 r=9 Schur sandwich. Integers only.

Shares no code with independent/finite_s3_3x4_r9_first_gap.py: different link layout, spanning tree and
canonical form; exterior residual rows built from each exterior state's own 72 moves; X from integer
Gauss-Seidel; U from X^T A X directly; inertia from the exact characteristic polynomial (Faddeev-LeVerrier
in integers) and Descartes' rule, which is exact for the real-rooted polynomial of a symmetric matrix.
"""
import sys
from itertools import permutations

LX, LY = 3, 4
NS = LX * LY
NL = 2 * NS
JB_OVER_JE = 9
FLOOR_NUM, FLOOR_DEN = 94070673, 1000000   # lambda_min(H restricted to nonflat orbits) >= 94.070673 J_E


def fail(msg):
    print("RECON_FAIL|" + msg + "|json=0", flush=True)
    sys.exit(2)


PERMS = sorted(permutations(range(3)), reverse=True)        # my own element order
ID = PERMS.index((0, 1, 2))
COMP = [[PERMS.index(tuple(p[q[i]] for i in range(3))) for q in PERMS] for p in PERMS]
INVS = [next(j for j in range(6) if COMP[i][j] == ID) for i in range(6)]
FIX = [sum(p[i] == i for i in range(3)) for p in PERMS]
CHI = [f - 1 for f in FIX]                                   # standard character
TRANSP = [i for i in range(6) if FIX[i] == 1]
assert len(TRANSP) == 3


def site(x, y):
    return (x % LX) + LX * (y % LY)


def hlink(x, y):  # (x,y) -> (x+1,y)
    return 2 * site(x, y)


def vlink(x, y):  # (x,y) -> (x,y+1)
    return 2 * site(x, y) + 1


# spanning tree: row y=0 horizontals, then every column's verticals y=0..LY-2
TREE = [(site(x, 0), site(x + 1, 0), hlink(x, 0)) for x in range(LX - 1)]
TREE += [(site(x, y), site(x, y + 1), vlink(x, y)) for x in range(LX) for y in range(LY - 1)]
TREE_SET = {l for _, _, l in TREE}
FREE = [l for l in range(NL) if l not in TREE_SET]
if len(TREE) != NS - 1 or len(FREE) != NL - NS + 1:
    fail("tree")
ENDS = {}
for x in range(LX):
    for y in range(LY):
        ENDS[hlink(x, y)] = (site(x, y), site(x + 1, y))
        ENDS[vlink(x, y)] = (site(x, y), site(x, y + 1))


def canon(U):
    """U: list of NL ints. Gauge-fix along TREE (U_l -> g_s U_l g_t^-1), then min over global conjugation."""
    g = [None] * NS
    g[site(0, 0)] = ID
    for s, t, l in TREE:
        g[t] = COMP[g[s]][U[l]]
    out = []
    for l in FREE:
        s, t = ENDS[l]
        out.append(COMP[COMP[g[s]][U[l]]][INVS[g[t]]])
    best = None
    for h in range(6):
        hi = INVS[h]
        c = tuple(COMP[COMP[h][a]][hi] for a in out)
        if best is None or c < best:
            best = c
    return best


def unkey(key):
    U = [ID] * NL
    for l, a in zip(FREE, key):
        U[l] = a
    return U


def wt(key):
    return len({tuple(COMP[COMP[h][a]][INVS[h]] for a in key) for h in range(6)})


def mag(U):
    s = 0
    for x in range(LX):
        for y in range(LY):
            p = COMP[COMP[COMP[U[hlink(x, y)]][U[vlink(x + 1, y)]]][INVS[U[hlink(x, y + 1)]]]][INVS[U[vlink(x, y)]]]
            s += 2 - CHI[p]
    return s


def moves(key):
    U = unkey(key)
    out = {}
    for l in range(NL):
        old = U[l]
        for t in TRANSP:
            U[l] = COMP[t][old]
            k = canon(U)
            out[k] = out.get(k, 0) + 1
        U[l] = old
    if sum(out.values()) != 3 * NL:
        fail("moves")
    return out


def charpoly(M):
    """Coefficients c[0..n] of det(lambda I - M) = sum c[k] lambda^(n-k); Faddeev-LeVerrier, exact integer division."""
    n = len(M)
    c = [0] * (n + 1)
    c[0] = 1
    Mk = [[0] * n for _ in range(n)]
    for k in range(1, n + 1):
        AM = [[sum(M[i][t] * Mk[t][j] for t in range(n)) for j in range(n)] for i in range(n)]
        for i in range(n):
            AM[i][i] += c[k - 1]
        Mk = AM
        tr = sum(sum(M[i][t] * Mk[t][i] for t in range(n)) for i in range(n))
        if tr % k:
            fail("faddeev_division")
        c[k] = -tr // k
    return c


def sign_changes(seq):
    s = [v for v in seq if v != 0]
    return sum(1 for a, b in zip(s, s[1:]) if (a < 0) != (b < 0))


def negative_eigs(M):
    n = len(M)
    if any(M[i][j] != M[j][i] for i in range(n) for j in range(n)):
        fail("not_symmetric")
    c = charpoly(M)
    if c[n] == 0:
        fail("singular")  # a zero eigenvalue: no strict conclusion
    # p(-lambda): coefficient of lambda^(n-k) gets (-1)^(n-k)
    neg = sign_changes([c[k] * (-1) ** (n - k) for k in range(n + 1)])
    pos = sign_changes(c)
    if neg + pos != n:
        fail("descartes_not_exact")
    return neg


def self_test():
    import random
    rnd = random.Random(7)
    for _ in range(300):
        n = rnd.randint(1, 6)
        B = [[rnd.randint(-9, 9) for _ in range(n)] for _ in range(n)]
        D = [rnd.choice([-3, -1, 1, 2, 5]) for _ in range(n)]
        M = [[sum(B[t][i] * D[t] * B[t][j] for t in range(n)) for j in range(n)] for i in range(n)]
        det = charpoly(M)[n] * (-1) ** n
        if det == 0:
            continue
        # Sylvester: inertia of B^T D B equals that of D when B is nonsingular
        if negative_eigs(M) != sum(1 for d in D if d < 0):
            fail("selftest_inertia")
    print("RECON_SELFTEST|pass=1|json=0", flush=True)


def main():
    self_test()
    # flats: all commuting pairs (a,b) as seam holonomies
    flats = {}
    pairs = 0
    for a in range(6):
        for b in range(6):
            if COMP[a][b] != COMP[b][a]:
                continue
            pairs += 1
            U = [ID] * NL
            for y in range(LY):
                U[hlink(LX - 1, y)] = a
            for x in range(LX):
                U[vlink(x, LY - 1)] = b
            if mag(U) != 0:
                fail("flat_mag")
            flats.setdefault(canon(U), (a, b))
    P = sorted(flats)
    if pairs != 18 or len(P) != 8 or sum(wt(k) for k in P) != 18:
        fail("flat_census")
    shells = [P]
    seen = set(P)
    nbr = {}
    for _ in range(3):
        nxt = set()
        for k in shells[-1]:
            if k not in nbr:
                nbr[k] = moves(k)
            nxt.update(nbr[k])
        nxt -= seen
        seen |= nxt
        shells.append(sorted(nxt))
    S1, S2, S3 = shells[1], shells[2], shells[3]
    print(f"RECON_CENSUS|flat={len(P)}|commuting_pairs={pairs}|flat_weight_sum={sum(wt(k) for k in P)}"
          f"|shell1={len(S1)}|shell2={len(S2)}|exterior_shell3={len(S3)}|json=0", flush=True)
    for k in S3:
        nbr[k] = moves(k)  # the exterior side, computed from each exterior state itself
    Q = S1 + S2
    qi = {k: i for i, k in enumerate(Q)}
    pi = {k: i for i, k in enumerate(P)}
    w = {k: wt(k) for k in P + Q + S3}
    M = {k: mag(unkey(k)) for k in P + Q + S3}
    if any(M[k] == 0 for k in Q + S3):
        fail("nonflat_with_zero_M")
    # detailed balance on every edge touching K2 (both directions computed from moves)
    for x in P + Q + S3:
        for y, c in nbr[x].items():
            if y in nbr and y != x and w[x] * c != w[y] * nbr[y].get(x, 0):
                fail("detailed_balance")
    # flats: no flat-flat or flat self-return moves
    for k in P:
        if any(y in pi for y in nbr[k]):
            fail("flat_flat_coupling")
    print("RECON_BALANCE|edges_checked=all_touching_K2|flat_flat=0|json=0", flush=True)

    def Hxy(x, y):  # J_E = 1
        c = nbr[x].get(y, 0)
        if x == y:
            return 3 * NL - c + JB_OVER_JE * M[x]
        return -c

    results = []
    for a, lo_exp, hi_exp in ((6989, 0, 0), (6992, 1, 1), (6993, 1, 1), (6996, None, 2)):
        b = 100
        nq = len(Q)
        LS = 10 ** 12
        # K = W(bH - aI); F = Q K P; A = Q K Q restricted to K2
        F = [[w[q] * b * Hxy(q, p) for p in P] for q in Q]
        diag = [w[q] * (b * Hxy(q, q) - a) for q in Q]
        offs = [[(qi[y], w[q] * b * Hxy(q, y)) for y in nbr[q] if y in qi and y != q] for q in Q]
        # Gauss-Seidel on A X = LS F inside K2, integer floor
        X = [[0] * 8 for _ in range(nq)]
        for _sweep in range(40):
            for i in range(nq):
                row = [LS * F[i][k] for k in range(8)]
                for j, v in offs[i]:
                    xj = X[j]
                    for k in range(8):
                        row[k] -= v * xj[k]
                X[i] = [r // diag[i] for r in row]
        # residual R = LS F - A X on every nonflat row: K2 rows, then exterior rows from the exterior side
        R = []
        for i in range(nq):
            row = [LS * F[i][k] - diag[i] * X[i][k] for k in range(8)]
            for j, v in offs[i]:
                for k in range(8):
                    row[k] -= v * X[j][k]
            R.append((w[Q[i]], row))
        for y in S3:
            row = [0] * 8
            for x, c in nbr[y].items():
                if x in qi:
                    v = w[y] * b * (-c)          # A_yx
                    for k in range(8):
                        row[k] -= v * X[qi[x]][k]
            R.append((w[y], row))
        G6 = [[sum((6 // wy) * r[i] * r[j] for wy, r in R) for j in range(8)] for i in range(8)]
        C = [[w[p] * (b * Hxy(p, p2) - a * (p == p2)) for p2 in P] for p in P]
        FX = [[sum(F[q][i] * X[q][j] for q in range(nq)) for j in range(8)] for i in range(8)]
        AX = []
        for i in range(nq):
            row = [diag[i] * X[i][k] for k in range(8)]
            for j, v in offs[i]:
                for k in range(8):
                    row[k] += v * X[j][k]
            AX.append(row)
        XAX = [[sum(X[q][i] * AX[q][j] for q in range(nq)) for j in range(8)] for i in range(8)]
        U = [[LS * LS * C[i][j] - LS * (FX[i][j] + FX[j][i]) + XAX[i][j] for j in range(8)] for i in range(8)]
        gnum = b * FLOOR_NUM - a * FLOOR_DEN
        if gnum <= 0:
            fail("floor")
        LOW = [[6 * gnum * U[i][j] - FLOOR_DEN * G6[i][j] for j in range(8)] for i in range(8)]
        nlo, nhi = negative_eigs(LOW), negative_eigs(U)
        results.append((a, nlo, nhi))
        print(f"RECON_THRESHOLD|z={a}/100|n_neg_lower={nlo}|n_neg_upper={nhi}|gs_sweeps=40|scale=10^12|json=0", flush=True)
    r = {a: (lo, hi) for a, lo, hi in results}
    e1_gt = r[6989][0] == 0          # N(69.89) <= 0
    e1_lt = r[6992][1] >= 1          # N(69.92) >= 1
    e2_gt = r[6993][0] <= 1          # N(69.93) <= 1
    e2_lt = r[6996][1] >= 2          # N(69.96) >= 2
    print(f"RECON_VERDICT|E1_gt_6989={int(e1_gt)}|E1_lt_6992={int(e1_lt)}|E2_gt_6993={int(e2_gt)}|E2_lt_6996={int(e2_lt)}"
          f"|first_gap_in=(1/100,7/100)={int(e1_gt and e1_lt and e2_gt and e2_lt)}|conditional_on=lambda_min_nonflat_GE_94070673e-6|json=0")


if __name__ == "__main__":
    main()
