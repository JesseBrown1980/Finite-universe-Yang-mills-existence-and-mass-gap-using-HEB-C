#!/usr/bin/env python3
"""S3 Kogut-Susskind rule of this repository on an open a x b grid of plaquettes, worked directly in the
gauge-fixed space: one group element per independent loop (6^P raw states, P = a*b), reduced by the
global conjugation to (6^P + 2*3^P + 3*2^P)/6 orbits, in place of 6^links brute force.
Levels are bracketed by exact integer inertia counts. Integers only.

usage: open_grid.py A B R [charpoly]
"""
import sys
from collections import deque
from itertools import permutations, product

G = tuple(permutations(range(3)))
IDX = {a: i for i, a in enumerate(G)}
MUL = tuple(tuple(IDX[tuple(G[a][G[b][i]] for i in range(3))] for b in range(6)) for a in range(6))
INV = tuple(next(b for b in range(6) if MUL[a][b] == 0 and MUL[b][a] == 0) for a in range(6))
TRANS = tuple(i for i in range(1, 6) if MUL[i][i] == 0)
CHAR = tuple(sum(int(G[a][j] == j) for j in range(3)) - 1 for a in range(6))
CONJ = tuple(tuple(MUL[MUL[g][a]][INV[g]] for a in range(6)) for g in range(6))
S = 1000000000


def ipow(base, e):
    out = 1
    for _ in range(e):
        out *= base
    return out


def emit(label, **f):
    print(label + "|" + "|".join("%s=%s" % kv for kv in f.items()) + "|json=0", flush=True)


def need(c, why):
    if not c:
        emit("GRID_REFUSE", reason=why)
        raise SystemExit(1)


class Grid:
    def __init__(self, a, b):
        self.a, self.b = a, b
        vid = lambda x, y: x * (b + 1) + y  # noqa: E731
        self.nv = (a + 1) * (b + 1)
        self.links = []
        hx, vy = {}, {}
        for x in range(a):
            for y in range(b + 1):
                hx[(x, y)] = len(self.links)
                self.links.append((vid(x, y), vid(x + 1, y)))
        for x in range(a + 1):
            for y in range(b):
                vy[(x, y)] = len(self.links)
                self.links.append((vid(x, y), vid(x, y + 1)))
        # plaquette: bottom, right, top^-1, left^-1
        self.plaq = [(hx[(x, y)], vy[(x + 1, y)], hx[(x, y + 1)], vy[(x, y)]) for x in range(a) for y in range(b)]
        adj = {}
        for k, (u, v) in enumerate(self.links):
            adj.setdefault(u, []).append((v, k, 1))
            adj.setdefault(v, []).append((u, k, -1))
        self.tree, seen, dq = [], {0}, deque([0])
        while dq:
            u = dq.popleft()
            for v, k, sgn in adj[u]:
                if v not in seen:
                    seen.add(v)
                    self.tree.append((u, v, k, sgn))
                    dq.append(v)
        tree_ids = {t[2] for t in self.tree}
        self.kept = tuple(k for k in range(len(self.links)) if k not in tree_ids)
        need(len(self.kept) == a * b and len(self.tree) == self.nv - 1, "tree_and_loop_count")

    def canonical(self, U):
        h = [0] * self.nv
        for u, v, k, sgn in self.tree:
            h[v] = MUL[h[u]][U[k]] if sgn == 1 else MUL[h[u]][INV[U[k]]]
        key = tuple(MUL[MUL[h[self.links[k][0]]][U[k]]][INV[h[self.links[k][1]]]] for k in self.kept)
        return min(tuple(CONJ[g][x] for x in key) for g in range(6))

    def magnetic(self, U):
        return sum(2 - CHAR[MUL[MUL[MUL[U[p[0]]][U[p[1]]]][INV[U[p[2]]]]][INV[U[p[3]]]]] for p in self.plaq)

    def matrix(self, r, electric=1):
        keys = sorted({min(tuple(CONJ[g][x] for x in key) for g in range(6))
                       for key in product(range(6), repeat=len(self.kept))})
        index = {k: i for i, k in enumerate(keys)}
        n, L = len(keys), len(self.links)
        W = [len({tuple(CONJ[g][x] for x in k) for g in range(6)}) for k in keys]
        H = [dict() for _ in range(n)]
        for i, key in enumerate(keys):
            U = [0] * L
            for k, x in zip(self.kept, key):
                U[k] = x
            H[i][i] = electric * 3 * L + r * self.magnetic(U)
            for k in range(L):
                old = U[k]
                for t in TRANS:
                    U[k] = MUL[t][old]
                    j = index[self.canonical(U)]
                    H[i][j] = H[i].get(j, 0) - electric
                U[k] = old
        for i in range(n):
            for j, v in H[i].items():
                need(W[i] * v == W[j] * H[j].get(i, 0), "detailed_balance")
        return H, W


def dense(H, n):
    return [[H[i].get(j, 0) for j in range(n)] for i in range(n)]


def below(H, W, num, den=S):
    """Number of levels below num/den: negative inertia of W*(den*H - num), by fraction-free elimination."""
    n = len(W)
    A = [[W[i] * (den * H[i].get(j, 0) - (num if i == j else 0)) for j in range(n)] for i in range(n)]
    neg, prev = 0, 1
    for k in range(n):
        piv = A[k][k]
        if piv == 0:
            return None
        neg += int((piv < 0) != (prev < 0))
        rowk = A[k]
        for i in range(k + 1, n):
            f = A[i][k]
            rowi = A[i]
            for j in range(k + 1, n):
                rowi[j] = (piv * rowi[j] - f * rowk[j]) // prev
        prev = piv
    return neg


def count(H, W, num):
    for shift in range(0, 5):
        c = below(H, W, num + shift)
        if c is not None:
            return c, num + shift
    need(False, "zero_pivot_inertia")


def level(H, W, k, lo, hi, tol):
    """Bracket of the k-th level (1-based) in units 1/S."""
    need(count(H, W, lo)[0] < k <= count(H, W, hi)[0], "level_range")
    while hi - lo > tol:
        m = (lo + hi) // 2
        c, m = count(H, W, m)
        if c >= k:
            hi = m
        else:
            lo = m
    return lo, hi


def charpoly(M):
    n = len(M)
    coeffs, A = [1], [[0] * n for _ in range(n)]
    for k in range(1, n + 1):
        A = [[sum(M[i][l] * (A[l][j] + (coeffs[-1] if l == j else 0)) for l in range(n)) for j in range(n)] for i in range(n)]
        tr = sum(A[i][i] for i in range(n))
        need(tr % k == 0, "Faddeev_division")
        coeffs.append(-tr // k)
    return tuple(coeffs)


def main():
    a, b, r = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    g = Grid(a, b)
    P = a * b
    H, W = g.matrix(r)
    n = len(W)
    need(6 * n == ipow(6, P) + 2 * ipow(3, P) + 3 * ipow(2, P), "orbit_count_formula")
    need(sum(W) == ipow(6, P), "orbit_sizes_sum")
    emit("GRID_SPACE", a=a, b=b, plaquettes=P, links=len(g.links), raw_link_states="6^%d" % len(g.links), gauge_orbits=n, r=r)
    if len(sys.argv) > 4 and sys.argv[4] == "charpoly":
        emit("GRID_CHARPOLY", a=a, b=b, r=r, charpoly=",".join(map(str, charpoly(dense(H, n)))))
        return
    top = (3 * len(g.links) * 2 + r * 3 * P + 1) * S
    tol = 1000 if n <= 60 else 100000
    e0 = level(H, W, 1, -S, top, tol)
    e1 = level(H, W, 2, e0[0], top, tol)
    emit("GRID_LEVELS", a=a, b=b, r=r, gauge_orbits=n, units="1e-9", E0_lo=e0[0], E0_hi=e0[1], E1_lo=e1[0], E1_hi=e1[1],
         gap_lo=e1[0] - e0[1], gap_hi=e1[1] - e0[0])


if __name__ == "__main__":
    main()
