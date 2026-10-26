"""Independent verifier: S3 lattice gauge Hamiltonian on the Lx x Ly torus.

Written separately from the production tools (torusl/ymsec, flatcomp, cluster,
shellschur). It imports none of them and shares no code with them. Integer
arithmetic only (Python int and numpy int64 modular arithmetic), json=0.

Construction
  group     S3 as permutations of (0,1,2); the three transpositions T; the real
            character chi of the standard representation (2, 0, -1 on the
            identity, transpositions and 3-cycles).
  links     U_x(s) from s to s+x and U_y(s) from s to s+y, s on the torus.
  gauge     g_s acts as U_x(s) -> g_s U_x(s) g_{s+x}^-1 (likewise y).
  orbits    fix a spanning tree to the identity by a gauge transformation
            (solved outward from the root); the remaining freedom is global
            conjugation of the non-tree links. An orbit is a conjugation class
            of non-tree tuples, labelled by its lexicographically least member.
  H         H = J_E E + J_B M, with
            E = sum over links of (3 - sum_{t in T} L_t),  L_t U = t U,
            M = sum over plaquettes of (2 - chi(U_p)),
            U_p = U_x(s) U_y(s+x) U_x(s+y)^-1 U_y(s)^-1.
  matrix    A[O][O'] = 3 nl delta - c(O -> O') + J_B/J_E-scaled magnetic diagonal,
            with c(O -> O') the number of moves from any member of O into O'.
            W = diag(conjugation-orbit size) makes W A symmetric.
  count     #eigenvalues of A below t = #negative eigenvalues of
            B = W (1e6 E + r 1e6 M) - t W     (Sylvester for the pencil (WA, W)),
            computed as sign changes of the leading principal minors of a
            randomly permuted B. Each minor is found modulo enough 31-bit primes
            to exceed twice its Hadamard bound, and its sign is read from the
            balanced mixed-radix (Garner) digits.

usage: python indep_verify.py LX LY R T_MILLI[,T_MILLI...] [SEED]
"""

from __future__ import annotations

import random
import sys
from itertools import permutations, product

import numpy as np

# ---------------------------------------------------------------- S3

ELEMS = sorted(permutations(range(3)))
IDX = {g: i for i, g in enumerate(ELEMS)}


def mul(a: int, b: int) -> int:
    """(a b)(i) = a(b(i))."""
    pa, pb = ELEMS[a], ELEMS[b]
    return IDX[tuple(pa[pb[i]] for i in range(3))]


def inv(a: int) -> int:
    pa = ELEMS[a]
    out = [0, 0, 0]
    for i, v in enumerate(pa):
        out[v] = i
    return IDX[tuple(out)]


E_ID = IDX[(0, 1, 2)]
MUL = [[mul(a, b) for b in range(6)] for a in range(6)]
INV = [inv(a) for a in range(6)]
TRANSP = [i for i, p in enumerate(ELEMS) if sum(p[k] != k for k in range(3)) == 2]
# fixed points: e has 3 -> chi 2; transposition has 1 -> chi 0; 3-cycle has 0 -> chi -1
CHI = [{3: 2, 1: 0, 0: -1}[sum(p[k] == k for k in range(3))] for p in ELEMS]

# ---------------------------------------------------------------- lattice


class Torus:
    def __init__(self, lx: int, ly: int):
        self.lx, self.ly, self.n = lx, ly, lx * ly
        self.nl = 2 * self.n
        # link ids: x-link of site s is s, y-link is n + s
        # spanning tree: x-links along the bottom row y = 0 (x < lx-1) and
        # y-links in every column (y < ly-1)
        tree = [self.site(x, 0) for x in range(lx - 1)]
        tree += [self.n + self.site(x, y) for x in range(lx) for y in range(ly - 1)]
        self.tree = sorted(tree)
        self.free = [l for l in range(self.nl) if l not in set(tree)]
        # BFS order of the tree from the root (0,0): (site, parent link, parent site)
        order, seen = [(self.site(0, 0), None, None)], {self.site(0, 0)}
        frontier = [self.site(0, 0)]
        tree_set = set(tree)
        while frontier:
            nxt = []
            for s in frontier:
                for l in tree_set:
                    a, b = self.ends(l)
                    for u, v in ((a, b), (b, a)):
                        if u == s and v not in seen:
                            seen.add(v)
                            order.append((v, l, s))
                            nxt.append(v)
            frontier = nxt
        assert len(order) == self.n
        self.order = order
        self.plaquettes = [
            (self.site(x, y), self.n + self.site((x + 1) % lx, y), self.site(x, (y + 1) % ly), self.n + self.site(x, y))
            for x in range(lx)
            for y in range(ly)
        ]

    def site(self, x: int, y: int) -> int:
        return (x % self.lx) + self.lx * (y % self.ly)

    def ends(self, l: int) -> tuple[int, int]:
        if l < self.n:
            s = l
            x, y = s % self.lx, s // self.lx
            return s, self.site(x + 1, y)
        s = l - self.n
        x, y = s % self.lx, s // self.lx
        return s, self.site(x, y + 1)

    def gauge_fix(self, u: list[int]) -> list[int]:
        """Gauge transformation making every tree link the identity."""
        g = [None] * self.n
        g[self.order[0][0]] = E_ID
        for v, l, s in self.order[1:]:
            a, b = self.ends(l)
            if a == s:  # U from s to v: g_s U g_v^-1 = e  ->  g_v = g_s U
                g[v] = MUL[g[s]][u[l]]
            else:  # U from v to s: g_v U g_s^-1 = e  ->  g_v = g_s U^-1
                g[v] = MUL[g[s]][INV[u[l]]]
        out = []
        for l in range(self.nl):
            a, b = self.ends(l)
            out.append(MUL[MUL[g[a]][u[l]]][INV[g[b]]])
        assert all(out[l] == E_ID for l in self.tree)
        return out

    def label(self, u: list[int]) -> tuple[tuple[int, ...], int]:
        """Orbit label (least conjugate of the free tuple) and conjugation-orbit size."""
        fixed = self.gauge_fix(u)
        q = tuple(fixed[l] for l in self.free)
        conj = {tuple(MUL[MUL[h][a]][INV[h]] for a in q) for h in range(6)}
        return min(conj), len(conj)

    def magnetic(self, u: list[int]) -> int:
        tot = 0
        for a, b, c, d in self.plaquettes:
            up = MUL[MUL[MUL[u[a]][u[b]]][INV[u[c]]]][INV[u[d]]]
            tot += 2 - CHI[up]
        return tot


def build(lx: int, ly: int):
    tor = Torus(lx, ly)
    labels: dict[tuple[int, ...], int] = {}
    weight: list[int] = []
    reps: list[tuple[int, ...]] = []
    for q in product(range(6), repeat=len(tor.free)):
        lab, size = None, None
        conj = {tuple(MUL[MUL[h][a]][INV[h]] for a in q) for h in range(6)}
        lab = min(conj)
        if lab not in labels:
            labels[lab] = len(reps)
            reps.append(lab)
            weight.append(len(conj))
    n = len(reps)
    rows: list[dict[int, int]] = []
    mag: list[int] = []
    for lab in reps:
        u = [E_ID] * tor.nl
        for l, a in zip(tor.free, lab):
            u[l] = a
        mag.append(tor.magnetic(u))
        row: dict[int, int] = {}
        for l in range(tor.nl):
            for t in TRANSP:
                w = list(u)
                w[l] = MUL[t][w[l]]
                j = labels[tor.label(w)[0]]
                row[j] = row.get(j, 0) + 1
        rows.append(row)
    # W A symmetric: w_i c(i->j) == w_j c(j->i)
    for i, row in enumerate(rows):
        for j, c in row.items():
            assert weight[i] * c == weight[j] * rows[j].get(i, 0), "W A not symmetric"
    return tor, n, weight, rows, mag


# ---------------------------------------------------------------- inertia


def primes_below(limit: int, count: int, skip: set[int]) -> list[int]:
    out, p = [], limit - 1
    while len(out) < count:
        if p not in skip and all(p % d for d in range(2, int(p**0.5) + 1)):
            out.append(p)
        p -= 1
    return out


def isqrt(n: int) -> int:
    x = int(n**0.5) if n < 2**52 else 1 << ((n.bit_length() + 1) // 2)
    while x * x > n:
        x = (x + n // x) // 2
    while (x + 1) * (x + 1) <= n:
        x += 1
    return x


LAST = {}


def leading_minor_signs(B: list[list[int]]) -> list[int]:
    n = len(B)
    bits = 0
    for row in B:
        bits = max(bits, (isqrt(sum(v * v for v in row)) + 1).bit_length())
    need = (bits * n + 2) // 30 + 2
    LAST.update(hadamard_bits_per_row=bits, hadamard_bits=bits * n, primes=need)
    mods = primes_below(1 << 31, need, set())
    res = np.zeros((need, n), dtype=np.int64)
    B64 = np.array(B, dtype=np.int64)  # |entries| < 2^63 checked below
    assert max(abs(v) for row in B for v in row) < (1 << 62)
    for k, p in enumerate(mods):
        M = B64 % p
        det = 1
        for i in range(n):
            piv = int(M[i, i])
            if piv == 0:
                raise RuntimeError("zero pivot modulo a prime; reshuffle")
            det = det * piv % p
            res[k, i] = det
            if i + 1 < n:
                invp = pow(piv, p - 2, p)
                f = (M[i + 1 :, i] * invp) % p
                M[i + 1 :, i + 1 :] = (M[i + 1 :, i + 1 :] - (f[:, None] * M[i, i + 1 :][None, :]) % p) % p
    # CRT: D = sum r_i c_i (mod M), read in the balanced range (-M/2, M/2]
    M = 1
    for m in mods:
        M *= m
    coef = []
    for m in mods:
        Mi = M // m
        coef.append(Mi * pow(Mi % m, m - 2, m))
    signs = []
    for idx in range(n):
        x = sum(int(res[i, idx]) * coef[i] for i in range(len(mods))) % M
        if x > M // 2:
            x -= M
        signs.append((x > 0) - (x < 0))
    return signs


def count_below(n, weight, rows, mag, r, t_milli, seed):
    """#eigenvalues of A = E + r M below t_milli/1e6 (strict), A in the orbit basis."""
    rng = random.Random(seed)
    LAST["retries"] = 0
    for attempt in range(8):
        LAST["retries"] = attempt
        perm = list(range(n))
        rng.shuffle(perm)
        pos = {v: i for i, v in enumerate(perm)}
        B = [[0] * n for _ in range(n)]
        for i in range(n):
            ii = pos[i]
            diag_e = sum(rows[i].values())  # = 3 nl (every move counted)
            for j, c in rows[i].items():
                B[ii][pos[j]] -= weight[i] * c * 1_000_000
            B[ii][ii] += weight[i] * (diag_e * 1_000_000 + r * 1_000_000 * mag[i] - t_milli)
        try:
            signs = leading_minor_signs(B)
        except RuntimeError:
            continue
        if 0 in signs:
            continue
        neg, prev = 0, 1
        for s in signs:
            neg += s != prev
            prev = s
        return neg
    raise RuntimeError("could not find a permutation with nonzero leading minors")


def main(argv):
    import hashlib

    lx, ly, r = int(argv[0]), int(argv[1]), int(argv[2])
    ts = [int(x) for x in argv[3].split(",")]
    seed = int(argv[4]) if len(argv) > 4 else 1
    code = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    print(f"INDEP_RUN|code_sha256={code}|command=python indep_verify.py {' '.join(argv)}|seed={seed}|json=0", flush=True)
    tor, n, weight, rows, mag = build(lx, ly)
    flat = sum(1 for m in mag if m == 0)
    k = len(tor.free)
    burnside = (6**k + 3 * 2**k + 2 * 3**k) // 6
    print(
        f"INDEP_BUILD|L={lx}x{ly}|gauge_orbits={n}|burnside={burnside}|weight_sum={sum(weight)}|six_pow_free={6**k}"
        f"|free_links={k}|tree_links={len(tor.tree)}|flat_states={flat}|WA_symmetric=PASS|json=0",
        flush=True,
    )
    if n != burnside or sum(weight) != 6**k:
        print("INDEP_BUILD|result=FAIL|reason=structure_mismatch|json=0", flush=True)
        sys.exit(1)
    failed = False
    for t in ts:
        try:
            neg = count_below(n, weight, rows, mag, r, t, seed)
            print(
                f"INDEP_COUNT|L={lx}x{ly}|r={r}|t_milli={t}|N={neg}|method=multimodular_leading_minors_random_permutation|seed={seed}"
                f"|hadamard_bits={LAST['hadamard_bits']}|primes_31bit={LAST['primes']}|reshuffle_retries={LAST['retries']}|result=COMPUTED|json=0",
                flush=True,
            )
        except RuntimeError as e:
            failed = True
            print(
                f"INDEP_COUNT|L={lx}x{ly}|r={r}|t_milli={t}|seed={seed}|result=INCONCLUSIVE|reason={str(e).replace(' ', '_')}"
                f"|hadamard_bits={LAST.get('hadamard_bits', '-')}|primes_31bit={LAST.get('primes', '-')}|reshuffle_retries={LAST.get('retries', '-')}|json=0",
                flush=True,
            )
    if failed:
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
