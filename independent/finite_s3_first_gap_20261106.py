#!/usr/bin/env python3
"""Proof-derived, integer-only lower bound for the FIRST S3 torus gap.

No eigenvalue computations and no external dependencies. The bound uses
(i) gap(E) = 3*min(4,Lx,Ly), (ii) a ground-state transform, and
(iii) an explicit orbit-graph diameter bound 2*(Lx*Ly+1).
This is *not* a certificate of the continuum Yang-Mills mass gap.
"""
from __future__ import annotations
import argparse
from math import gcd


def integer_power(base: int, exp: int) -> int:
    """Fail closed for negative exponents; multiplication cannot create floats."""
    if not isinstance(exp, int) or exp < 0:
        raise ValueError('NEGATIVE_EXPONENT_UNCERTIFIED')
    value = 1
    for _ in range(exp):
        value *= base
    return value


def bound(lx: int, ly: int, je: int, jb: int) -> dict[str, int]:
    if min(lx, ly, je) < 1 or jb < 0:
        raise ValueError('require Lx,Ly,JE >= 1 and JB >= 0')
    plaquettes = lx * ly
    loops = plaquettes + 1
    girth = min(4, lx, ly)
    # Each non-tree S3 link is a product of <=2 transpositions.
    diameter_upper = 2 * loops
    degree_upper = 6 * plaquettes  # 3 moves per each of 2*plaquettes links
    magnetic_upper = 3 * plaquettes
    # An integer upper bound on the neighbour-to-neighbour Harnack ratio.
    harnack = degree_upper + (magnetic_upper * jb + je - 1) // je
    # Ground-state comparison: gap(H)>=JE gap(E) (min psi/max psi)^2.
    numer = 3 * girth * je
    denom = integer_power(harnack, 2 * diameter_upper)
    common = gcd(numer, denom)
    return dict(lx=lx, ly=ly, je=je, jb=jb, loops=loops,
                girth=girth, orbit_diameter_upper=diameter_upper,
                local_harnack=harnack, electric_gap=3*girth,
                numerator=numer//common, denominator=denom//common,
                # Unreduced expression is easier to independently reproduce.
                raw_numerator=numer, raw_base=harnack,
                raw_exponent=2*diameter_upper)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--lx', type=int, default=3)
    ap.add_argument('--ly', type=int, default=4)
    ap.add_argument('--je', type=int, default=1)
    ap.add_argument('--jb', type=int, default=9)
    a = ap.parse_args()
    b = bound(a.lx, a.ly, a.je, a.jb)
    print('FIRST_GAP_THEOREM|'+'|'.join(f'{key}={value}' for key,value in b.items())+'|scope=fixed_finite_S3_torus|status=DERIVED|json=0')
    print(f"ASSERTED_MATH|gap(H)>=({b['raw_numerator']}/{b['raw_base']}^{b['raw_exponent']})"
          ' in Hamiltonian units|not_a_numeric_inertia_replay=1|json=0')


if __name__ == '__main__':
    main()
