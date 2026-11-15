#!/usr/bin/env python3
"""Perturbation theory in the electric term for the open-grid S3 model, against the certified gaps.

Unperturbed: r * M (magnetic, diagonal). Ground state: the flat orbit (M = 0). First excited manifold:
one reflection flux on one plaquette (M = 2), one orbit per plaquette.
First order: the electric term restricted to each manifold (the flux hops between plaquettes that share a link).
Second order: sum over intermediate orbits n outside the manifold of V_an V_nb / (E_manifold - r M_n).
The lowest level of each effective matrix is bracketed by exact integer inertia counts. Integers only.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import open_grid as og  # noqa: E402

R = 9
S = og.S
GRIDS = ((1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (2, 2))


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def lowest(rows, den):
    """Bracket (units 1e-9) of the lowest eigenvalue of the symmetric integer matrix rows/den."""
    n = len(rows)
    H = [dict((j, rows[i][j]) for j in range(n) if rows[i][j]) for i in range(n)]
    W = [1] * n

    def cnt(x):  # levels of rows/den below x/S  <=>  levels of S*rows below x*den
        for shift in range(4):
            c = og.below(H, W, (x + shift) * den, S)
            if c is not None:
                return c
        og.need(False, "zero_pivot")

    lo, hi = -1000 * S, 1000 * S
    og.need(cnt(lo) == 0 and cnt(hi) >= 1, "range")
    while hi - lo > 2:
        m = (lo + hi) // 2
        if cnt(m) >= 1:
            hi = m
        else:
            lo = m
    return lo, hi + 4


def exact_gaps():
    out = {}
    for line in open(os.path.join(HERE, "RESULT-GRID-RUST.hbp"), encoding="utf-8"):
        if line.startswith("GRID_LEVELS|"):
            d = dict(kv.split("=", 1) for kv in line.strip().split("|")[1:] if "=" in kv)
            out[(int(d["a"]), int(d["b"]))] = (int(d["gap_lo"]), int(d["gap_hi"]))
    return out


def main():
    exact = exact_gaps()
    worst1 = worst2 = 0
    for a, b in GRIDS:
        g = og.Grid(a, b)
        H, W = g.matrix(R)
        n, L = len(W), len(g.links)
        Hm, _ = g.matrix(1, electric=0)
        M = [Hm[i].get(i, 0) for i in range(n)]
        flat = [i for i in range(n) if M[i] == 0]
        man = [i for i in range(n) if M[i] == 2]
        og.need(len(flat) == 1 and len(man) == a * b and all(W[i] == 3 for i in man) and W[flat[0]] == 1, "manifolds")
        f = flat[0]
        den = 1
        for i in range(n):
            for q in (M[i], abs(2 - M[i])):
                if q:
                    den = den * q // gcd(den, q)
        den *= R
        # ground state
        e0_1 = (H[f][f] - R * M[f]) * den  # first order: 3L - self moves, times den
        e0_2 = e0_1 - sum(H[f][k] * H[k].get(f, 0) * (den // (R * M[k])) for k in H[f] if k != f)
        # excited manifold, first and second order (times den)
        idx = {i: t for t, i in enumerate(man)}
        first = [[H[i].get(j, 0) * den for j in man] for i in man]
        second = [row[:] for row in first]
        for i in man:
            for k, v in H[i].items():
                if k in idx:
                    continue
                w = den // (R * (2 - M[k])) if M[k] != 2 else None
                og.need(w is not None, "degenerate_intermediate")
                for j, v2 in H[k].items():
                    if j in idx:
                        second[idx[i]][idx[j]] += v * v2 * w
        og.need(all(second[i][j] == second[j][i] for i in range(len(man)) for j in range(len(man))), "effective_symmetric")
        l1, l2 = lowest(first, den), lowest(second, den)
        g0_1 = (e0_1 * S) // den
        g0_2 = (e0_2 * S) // den
        pt1 = (l1[0] - g0_1 - 1, l1[1] - g0_1 + 1)
        pt2 = (l2[0] - g0_2 - 1, l2[1] - g0_2 + 1)
        ex = exact[(a, b)]
        d1 = max(abs(pt1[0] - ex[1]), abs(pt1[1] - ex[0]))
        d2 = max(abs(pt2[0] - ex[1]), abs(pt2[1] - ex[0]))
        worst1, worst2 = max(worst1, d1), max(worst2, d2)
        og.emit("PT_GRID", a=a, b=b, plaquettes=a * b, links=L, units="1e-9", exact_gap_lo=ex[0], exact_gap_hi=ex[1],
                first_order_gap=pt1[0], second_order_gap=pt2[0], first_order_minus_exact=pt1[0] - ex[0],
                second_order_minus_exact=pt2[0] - ex[0])
    og.emit("PT_VERDICT", N1=int(worst2 <= 150000000), N2=int(1000000000 <= worst1 <= 1500000000),
            worst_first_order_distance=worst1, worst_second_order_distance=worst2, units="1e-9")


if __name__ == "__main__":
    main()
