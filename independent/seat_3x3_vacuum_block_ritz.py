#!/usr/bin/env python3
"""Integer-only 3x3 finite-S3 vacuum-ball block-Krylov Ritz solver.

Solves the near-degenerate 4-fold vacuum cluster on the 3x3 S3 torus
(10,097,891 full states) compressed to graph balls K=1 (206), K=2 (4,454),
and K=3 (59,246 states).

Seeds an 8-dimensional subspace with all eight flat vacua simultaneously,
avoiding single-vector deflation drift. Evaluates exact generalized
Rayleigh-Ritz eigenvalues using fraction-free Bareiss elimination.

Outputs exact micro-unit enclosures for all 8 vacuum states.
Zero floats, Decimal, Fraction, true division, or JSON.
"""
import argparse
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import sys
from time import monotonic_ns

EXPECTED_MATRIX_SHA = {
    "b33_k1.matrix": "a9de0a8c8f070b7ded4b158290dad6b8d97fc83aabb17e1fe64de62b89a17a40",
    "b33_k2.matrix": "82339f3d4bed2a311d2443d555ab65d7190f8d94ad7a6babb276c553b96e3ffe",
    "b33_k3.matrix": "d86a347ba16d00c73482400ea24d58be83d00d00811aa50dd994a661f2b2c866",
}


def load_matrix(path):
    path_obj = Path(path)
    raw = path_obj.read_bytes()
    digest = sha256(raw).hexdigest()
    expected = EXPECTED_MATRIX_SHA.get(path_obj.name)
    if expected is not None:
        assert digest == expected, f"matrix sha mismatch for {path_obj.name}"

    toks = raw.split()
    n = int(toks[0])
    w = [int(x) for x in toks[1:1 + n]]
    mag = [int(x) for x in toks[1 + n:1 + 2 * n]]
    rest = [int(x) for x in toks[1 + 2 * n:]]
    assert len(rest) % 3 == 0
    return n, w, mag, rest, digest


def build_system(n, w, mag, rest, je, jb):
    col = [[] for _ in range(n)]
    for k in range(0, len(rest), 3):
        i, j, z = rest[k], rest[k + 1], rest[k + 2]
        col[j].append((i, 24 * je * z))
        if i != j:
            num = 24 * je * w[i] * z
            assert num % w[j] == 0
            col[i].append((j, num // w[j]))
    for i in range(n):
        col[i].append((i, 24 * jb * mag[i]))
    return col


def h_apply(col, v):
    out = defaultdict(int)
    for j, vj in v.items():
        if vj == 0:
            continue
        for i, aij in col[j]:
            out[i] += aij * vj
    return {k: val for k, val in out.items() if val != 0}


def wdot(w, u, v):
    if len(u) > len(v):
        u, v = v, u
    return sum(w[i] * ui * v.get(i, 0) for i, ui in u.items())


def inertia(m):
    """Bareiss fraction-free leading-minor sequence."""
    a = [row[:] for row in m]
    k_dim = len(a)
    prev = 1
    signs = [1]
    for k in range(k_dim):
        p = a[k][k]
        if p == 0:
            raise ValueError("zero pivot: uncertified threshold")
        signs.append(1 if p > 0 else -1)
        for i in range(k + 1, k_dim):
            x = a[i][k]
            for j in range(i, k_dim):
                top = p * a[i][j] - x * a[k][j]
                q, rem = divmod(top, prev)
                if rem:
                    raise ValueError("non-exact Bareiss division")
                a[i][j] = q
                a[j][i] = q
            a[i][k] = 0
            a[k][i] = 0
        prev = p
    return sum(s != t for s, t in zip(signs, signs[1:]))


def bracket(a, b, k, scale=1000000, upper=4800):
    k_dim = len(a)

    def count(t):
        c = [[scale * b[i][j] - t * a[i][j] for j in range(k_dim)] for i in range(k_dim)]
        return inertia(c)

    lo, hi = 0, upper * scale
    assert count(lo) <= k and count(hi) > k
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if count(mid) <= k:
            lo = mid
        else:
            hi = mid
    return lo, hi


def solve_block_ritz(matrix_path, je, jb, order=3):
    start = monotonic_ns()
    n, w, mag, rest, mat_sha = load_matrix(matrix_path)
    col = build_system(n, w, mag, rest, je, jb)

    flats = [i for i in range(n) if mag[i] == 0]
    assert len(flats) == 8, f"expected 8 flat vacua, found {len(flats)}"

    basis = [{f: 1} for f in flats]
    last = basis
    for _ in range(order):
        last = [h_apply(col, b) for b in last]
        basis.extend(last)

    hcols = [h_apply(col, b) for b in basis]
    dim = len(basis)
    a = [[wdot(w, u, v) for v in basis] for u in basis]
    b = [[wdot(w, u, hv) for hv in hcols] for u in basis]

    for i in range(dim):
        for j in range(dim):
            assert a[i][j] == a[j][i]
            assert b[i][j] == b[j][i]

    if inertia(a) != 0:
        raise ValueError("Gram matrix not positive definite")

    energies = []
    for k in range(8):
        lo, hi = bracket(a, b, k, scale=1000000)
        energies.append((lo // 24, hi // 24))

    e0_lo, e0_hi = energies[0]
    e1_lo, e1_hi = energies[1]
    e6_lo, e6_hi = energies[6]
    e7_lo, e7_hi = energies[7]
    gap_lo = e1_lo - e0_hi
    gap_hi = e1_hi - e0_lo
    upper_gap_lo = e7_lo - e6_hi
    upper_gap_hi = e7_hi - e6_lo
    elapsed_ms = (monotonic_ns() - start) // 1000000

    name = Path(matrix_path).name
    e_str = ",".join(f"{lo}" for lo, _ in energies)
    print(
        f"HEBC-3X3-BLOCK-RITZ|matrix={name}|matrix_sha={mat_sha[:16]}|states={n}|"
        f"JE={je}|JB={jb}|order={order}|subspace_dim={dim}|"
        f"E0={e0_lo}/1000000|E1={e1_lo}/1000000|gap=[{gap_lo},{gap_hi}]/1000000|"
        f"upper_gap=[{upper_gap_lo},{upper_gap_hi}]/1000000|"
        f"all_8_vacua_micro={e_str}|symmetry_diff={gap_lo - upper_gap_lo}|"
        f"ms={elapsed_ms}|kind=VACUUM_BLOCK_RITZ_UPPER_BOUNDS|json=0"
    )
    return energies


def main():
    p = argparse.ArgumentParser(description="3x3 Vacuum-ball block-Krylov Ritz solver")
    p.add_argument("matrix", type=str, help="path to .matrix file")
    p.add_argument("je", type=int, help="JE coupling")
    p.add_argument("jb", type=int, help="JB coupling")
    p.add_argument("--order", type=int, default=3, help="Krylov block order (default 3)")
    args = p.parse_args()
    solve_block_ritz(args.matrix, args.je, args.jb, args.order)


if __name__ == "__main__":
    main()
