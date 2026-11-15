#!/usr/bin/env python3
"""AFTER THE RUN (exploratory, not predicted). The frozen second-order check missed: the rotation flux
(cost 3r = 27) lies only r = 9 above the reflection flux (cost 2r = 18) and couples to it strongly
(on one plaquette 8 moves one way and 12 back, product 96, against a denominator of 9).
Here the excited manifold is widened to every orbit with exactly one non-identity plaquette (a reflection
or a rotation), the full matrix is restricted to it, and the ground level is taken at second order.
Integers only."""
import os
import sys
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import open_grid as og  # noqa: E402
import pt_check as pt  # noqa: E402

R = 9
exact = pt.exact_gaps()
for a, b in pt.GRIDS:
    g = og.Grid(a, b)
    H, W = g.matrix(R)
    n = len(W)
    Hm, _ = g.matrix(1, electric=0)
    M = [Hm[i].get(i, 0) for i in range(n)]
    keys = sorted({min(tuple(og.CONJ[c][x] for x in key) for c in range(6))
                   for key in product(range(6), repeat=a * b)})
    single = [i for i, k in enumerate(keys) if sum(1 for x in k if x != 0) == 1]
    og.need(len(single) == 2 * a * b and len(keys) == n, "single_flux_orbits")
    f = M.index(0)
    den = 1
    for i in range(n):
        if M[i]:
            den = den * M[i] // pt.gcd(den, M[i])
    den *= R
    e0 = (H[f][f]) * den - sum(H[f][k] * H[k].get(f, 0) * (den // (R * M[k])) for k in H[f] if k != f)
    # symmetric form on the single-flux orbits: A_ij = W_i * H_ij (W_i H_ij = W_j H_ji)
    sub = [dict((single.index(j), v) for j, v in H[i].items() if j in single) for i in single]
    Ws = [W[i] for i in single]

    def cnt(x):
        for shift in range(4):
            c = og.below(sub, Ws, x + shift, og.S)
            if c is not None:
                return c
        og.need(False, "zero_pivot")

    lo, hi = -1000 * og.S, 1000 * og.S
    while hi - lo > 2:
        m = (lo + hi) // 2
        if cnt(m) >= 1:
            hi = m
        else:
            lo = m
    gap = lo - (e0 * og.S) // den
    ex = exact[(a, b)]
    og.emit("PT_EXPLORE", a=a, b=b, single_flux_orbits=len(single), units="1e-9", exact_gap_lo=ex[0],
            reflection_and_rotation_flux_gap=gap, minus_exact=gap - ex[0])
