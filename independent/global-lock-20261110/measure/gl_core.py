#!/usr/bin/env python3
"""Global-lock measurement core: finite S3 lattice gauge on a periodic LX x LY torus.

Model (the only part of the frozen prediction read before the run):
  H/J_E = s_E*E + r*M,  E = sum over links of h_E,  h_E = 3I - sum_t L_t (t the 3 transpositions),
  M = sum over plaquettes of m_p,  m_p = 2 - chi_std(g_p),  r = J_B/J_E,  s_E = +1,
  on the gauge-invariant physical space (gauge orbits of S3 link configurations).

Integer only.  No float, no fractions module, no division operator; rationals are
reduced or unreduced integer pairs.  The group primitives, tree gauge, canonical key,
orbit weight, magnetic cost and the 72-move electric neighbour map are ported from
the merged checker independent/finite_s3_3x4_r9_first_gap.py (#136), generalised from
3x4 to LX x LY; gl_measure.py reproduces that checker's 3x4 census as an equivalence test.

Certificate (Haynsworth inertia with a trial resolvent, as in #136 / #155):
  P' = the 8 flat orbits (M=0) and every orbit with M=3 (one 3-cycle plaquette).
  C  = everything else; every C state has M >= 4 (sign parity: M=1,2,5 impossible).
  For lambda below a certified floor fl <= lambda_min(H_CC):
      count(H < lambda) = neg(S(lambda)),  S the exact Schur complement onto P',
      U(lambda) - G(lambda)/(fl-lambda) <= S(lambda) <= U(lambda),
  U the min-max form on span{(psi, -Y psi)} (unconditional), G the weighted Gram of the
  exact residual over the complete support (ball and its complete one-step exterior).
  fl comes from the complete M=4 census:  H_CC >= lambda'  when
      (3N + 4r - rho44 - lambda')(6r - lambda') >= P2max,
  rho44 = max row sum of the electric moves inside M=4, P2max = max two-step
  M4 -> (M>=6) -> M4 path count (Schur test).  E >= 0 is DERIVED from representation
  theory (each link term h_E has spectrum {0,3,6}; ELECTRIC-TERM-NOTE.hbp); the code's
  check electric_sign_is_plus_one tests the sign factor s_E = +1 of the run and nothing more.
"""
import hashlib
import sys
from collections import Counter
from itertools import permutations


def check(t, label):
    if not t:
        print("FAILED|check=" + label + "|json=0", flush=True)
        raise SystemExit(1)


def emit(label, **fields):
    print(label + "|" + "|".join(str(k) + "=" + str(v) for k, v in fields.items()) + "|json=0", flush=True)


def dec_floor(n, d, places):
    """floor(n/d) to `places` decimals, as a string (outward for a lower bound)."""
    check(d > 0, "positive_denominator")
    s = 1
    for _ in range(places):
        s *= 10
    q = (n * s) // d
    neg = q < 0
    q = -q if neg else q
    ip, fp = divmod(q, s)
    out = str(ip) + "." + str(fp).rjust(places, "0")
    return ("-" + out) if neg else out


def dec_ceil(n, d, places):
    s = 1
    for _ in range(places):
        s *= 10
    q = -((-n * s) // d)
    neg = q < 0
    q = -q if neg else q
    ip, fp = divmod(q, s)
    out = str(ip) + "." + str(fp).rjust(places, "0")
    return ("-" + out) if neg else out


GRP = tuple(permutations(range(3)))
INDEX = {a: i for i, a in enumerate(GRP)}
MUL = tuple(tuple(INDEX[tuple(GRP[a][GRP[b][i]] for i in range(3))] for b in range(6)) for a in range(6))
INV = tuple(next(b for b in range(6) if MUL[a][b] == MUL[b][a] == 0) for a in range(6))
TRANS = tuple(i for i in range(1, 6) if MUL[i][i] == 0)
CHAR = tuple(sum(int(GRP[a][j] == j) for j in range(3)) - 1 for a in range(6))
CONJ = tuple(tuple(MUL[MUL[g][a]][INV[g]] for a in range(6)) for g in range(6))
check(len(TRANS) == 3 and sorted(CHAR) == [-1, -1, 0, 0, 0, 2], "S3_tables")


class Lattice:
    def __init__(self, LX, LY):
        self.LX, self.LY = LX, LY
        V = LX * LY
        self.V = V
        self.NL = 2 * V
        self.N3 = 3 * self.NL          # number of electric moves = 3 * links
        def pos(x, y):
            return (x % LX) * LY + (y % LY)
        self.pos = pos
        tree = [(pos(0, y), pos(0, y + 1), V + pos(0, y)) for y in range(LY - 1)]
        tree += [(pos(x, y), pos(x + 1, y), pos(x, y)) for y in range(LY) for x in range(LX - 1)]
        self.tree = tuple(tree)
        tids = {k for _, _, k in tree}
        self.kept = tuple(k for k in range(2 * V) if k not in tids)
        check(len(self.kept) == V + 1 and len(tree) == V - 1, "tree_and_kept_links")
        kl = []
        for k in self.kept:
            if k < V:
                s = k
                x, y = divmod(s, LY)
                kl.append((k, s, pos(x + 1, y)))
            else:
                s = k - V
                x, y = divmod(s, LY)
                kl.append((k, s, pos(x, y + 1)))
        self.kept_links = tuple(kl)
        plaq = []
        for x in range(LX):
            for y in range(LY):
                i = pos(x, y)
                plaq.append((i, V + pos(x + 1, y), pos(x, y + 1), V + i))
        self.plaq = tuple(plaq)
        self.F = len(plaq)

    def from_key(self, key):
        U = [0] * self.NL
        for k, a in zip(self.kept, key):
            U[k] = a
        return U

    def canonical(self, U):
        h = [0] * self.V
        for u, v, k in self.tree:
            h[v] = MUL[h[u]][U[k]]
        key = tuple(MUL[MUL[h[s]][U[k]]][INV[h[d]]] for k, s, d in self.kept_links)
        return min(tuple(c[a] for a in key) for c in CONJ)

    @staticmethod
    def weight(key):
        return len({tuple(c[a] for a in key) for c in CONJ})

    def plaquettes(self, U):
        return [MUL[MUL[MUL[U[a]][U[b]]][INV[U[c]]]][INV[U[d]]] for a, b, c, d in self.plaq]

    def magnetic(self, U):
        return sum(2 - CHAR[p] for p in self.plaquettes(U))

    def mag_key(self, key):
        return self.magnetic(self.from_key(key))

    def neighbors(self, key):
        U = self.from_key(key)
        cnt = Counter()
        for k in range(self.NL):
            old = U[k]
            for t in TRANS:
                U[k] = MUL[t][old]
                cnt[self.canonical(U)] += 1
            U[k] = old
        check(sum(cnt.values()) == self.N3, "electric_moves_3_per_link")
        return cnt

    def burnside_dimension(self):
        n = self.V + 1
        a = b = c = 1
        for _ in range(n):
            a *= 6
            b *= 2
            c *= 3
        tot = a + 3 * b + 2 * c
        check(tot % 6 == 0, "burnside_integral")
        return tot // 6

    def enumerate_low(self, mmax):
        """All tree-gauge configurations with M <= mmax, by backtracking over kept links."""
        V = self.V
        kept_set = set(self.kept)
        order = []
        for pl in self.plaq:
            for k in pl:
                if k in kept_set and k not in order:
                    order.append(k)
        check(sorted(order) == sorted(self.kept), "enumeration_order_covers_kept")
        posn = {k: i for i, k in enumerate(order)}
        done_at = [[] for _ in order]
        for pi, pl in enumerate(self.plaq):
            ks = [posn[k] for k in pl if k in kept_set]
            check(len(ks) > 0, "plaquette_has_kept_link")
            done_at[max(ks)].append(pi)
        U = [0] * self.NL
        out = []
        plaq = self.plaq

        def rec(t, m):
            if t == len(order):
                out.append((tuple(U[k] for k in self.kept), m))
                return
            k = order[t]
            for g in range(6):
                U[k] = g
                mm = m
                for pi in done_at[t]:
                    a, b, c, d = plaq[pi]
                    p = MUL[MUL[MUL[U[a]][U[b]]][INV[U[c]]]][INV[U[d]]]
                    mm += 2 - CHAR[p]
                    if mm > mmax:
                        break
                if mm <= mmax:
                    rec(t + 1, mm)
            U[k] = 0
        rec(0, 0)
        return out


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def inertia(Mx):
    """Number of negative eigenvalues of an integer symmetric matrix, by fraction-free
    Bareiss elimination with symmetric pivoting (Sylvester sign changes of leading minors
    of the permuted matrix).  Returns None if a 2x2 pivot would be needed (undecided)."""
    n = len(Mx)
    for i in range(n):
        for j in range(i):
            check(Mx[i][j] == Mx[j][i], "inertia_input_symmetric")
    B = [row[:] for row in Mx]
    prev = 1
    sprev = 1
    neg = 0
    for k in range(n):
        if B[k][k] == 0:
            j = next((j for j in range(k + 1, n) if B[j][j] != 0), None)
            if j is None:
                return None
            B[k], B[j] = B[j], B[k]
            for row in B:
                row[k], row[j] = row[j], row[k]
        piv = B[k][k]
        if (piv < 0) != (sprev < 0):
            neg += 1
        sprev = piv
        Bk = B[k]
        for i in range(k + 1, n):
            Bi = B[i]
            bik = Bi[k]
            for j in range(k + 1, n):
                t = Bi[j] * piv - bik * Bk[j]
                q, rem = divmod(t, prev)
                if rem:
                    check(False, "bareiss_exact_division")
                Bi[j] = q
        prev = piv
    return neg
