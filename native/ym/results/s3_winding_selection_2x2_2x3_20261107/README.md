# Exact selection of the 2x2 finite S3 first excitation; 2x3 symmetry bridge

Status: **frozen predictions first**, exact integer proof candidate with dedicated independent GMP inertia gate. This package builds on the 1x1 winding-observable calculation in PR #127 and remains separate from the 3x4 high-cluster gap and the four-dimensional continuum problem.

## The new finding: the observable must change with lattice symmetry

The earlier 1x1 first excitation was visible through an *odd winding difference*. That cannot simply be reused unchanged on the larger 2x2 system. The full 2x2 finite S3 gauge Hamiltonian at JE=JB=1 has 1,393 gauge orbits, 7,776 tree-gauge configurations, and 32,385 nonzero electric entries. It has exact axis-exchange symmetry: 746 even states, 647 odd states.

Define the gauge-invariant characters around the two noncontractible loops at the origin:

    X(U) = chi_std(Ux(0,0) Ux(1,0))
    Y(U) = chi_std(Uy(0,0) Uy(0,1))
    O_plus = X+Y
    O_minus = X-Y

The gauge transformation at each winding basepoint conjugates the holonomy, so X,Y are gauge-invariant. Exact axis exchange maps O_plus to itself, O_minus to its negative. The ground state is unique and even by Perron positivity. H commutes with the exchange permutation; the full W-self-adjointness and covariance relations are verified on all orbit rows.

**Parity-resolved exact Sturm tests** on the 746/647 blocks at JE=JB=1 are preregistered:

| Threshold (JE units) | Expected number of even eigenvalues below | Expected number of odd eigenvalues below |
|---|---:|---:|
| 13.240000 | 1 | 0 |
| 13.242650 | 2 | 0 |
| 13.600000 | 2 | 1 |

The six counts use outward-rounded 90-digit GMP Schur-complement intervals and fail closed on ambiguous pivots. If all six pass, the global E0 and E1 are even and E2 is odd, while the next even excitation E3 is at least 13.6. This guarantees **exactly zero** overlap of O_minus with E1 (by parity), reversing the successful 1x1 operator choice.

## A strict **positive** E1 overlap for O_plus, without floating point

A positive 850-power Perron approximant to K=60I-H, from the all-ones vector, is exactly even. By W-weighted integer residual arithmetic and the certified E1>13.24 lower bound, its squared angle from the true interacting vacuum is less than 10^(-80).

Take the exactly centered integer vector u=(norm_W(v)^2) O_plus v - <v,O_plus v>_W v, which is even and W-orthogonal to v. For 230 powers of K, calculate exactly

    F = <u,K^230 u>_W / <u,u>_W.

Positivity of H and the conservative spectral bound H<=60 imply 0<=K<=60. If O_plus had zero spectral weight on E1, all its even excited spectral support would have energy at least 13.6. The most adverse possible ground leakage (using the Perron-angle certificate) would yield

    F <= (60-13.6)^230 + 60^230 / 10^80.

The exact integer witness verifies a *strict violation* of that inequality. This proves nonzero spectral overlap with the actual global E1 once the GMP inertia counts establish the energy ordering. The verifier also forms a conservative rational lower bound on the fraction of u's spectral weight on E1 using E1>13.24 and E3>=13.6. No unverified decimal eigenvector is needed.

The previously measured exploratory eigenvalues are approximately E0=7.634198412937, E1=13.242627514800, E2=13.242702738054. These decimals are *not* substituted for the integer Sturm certificates. The true first gap is E1-E0 about 5.608429, and the much smaller separation E2-E1 about 0.000075 is exactly why parity control matters.

## 2x3 extension: exact operator-selection protocol, not yet a first-gap certificate

For 2x3, the full gauge-invariant orbit space has 47,449 states. There is no x/y axis-exchange symmetry because the sides are unequal. A valid odd operator instead comes from translation by one cell along the size-two x cycle:

    O_tx(U) = chi_std(P_0,0(U)) - chi_std(P_1,0(U)).

The separate verifier uses 96 deterministic 12-link configurations and 576 local gauge transformations, checks each plaquette character, x-translation oddness, magnetic covariance and the 36 local electric moves. It also tests that a bare link character is not generally gauge invariant.

This establishes an exact **selection sector**, not whether the *global first excitation* on 2x3 lies inside it. A full exact 47,449-state first-gap and operator-weight certificate is the next independent computation. **Do not claim 2x3 E1 visibility from these symmetry checks.**

## Reproduce (hosted Rust-independent GMP + Python integer arithmetic)

    python3 -I native/ym/results/s3_winding_selection_2x2_2x3_20261107/exact_selection_2x2.py /tmp/s3-parity
    g++ -O3 -std=c++17 -Wall -Wextra -Werror native/ym/results/s3_winding_selection_2x2_2x3_20261107/inertia_gmp.cpp -lgmpxx -lgmp -o /tmp/s3-inertia
    /tmp/s3-inertia /tmp/s3-parity/even.matrix 13242650
    /tmp/s3-inertia /tmp/s3-parity/odd.matrix 13242650
    python3 -I native/ym/results/s3_winding_selection_2x2_2x3_20261107/verify_2x3_symmetry.py

The exact integer input freeze is PREDICTION.hbp at commit 9858660f3254c4c03092deade18363c4cc2dc06d. The full independent row regeneration is anchored by the pre-existing exact 2x2 operator SHA in independent/gpt6_2x2_from_permutations.py. The paired output matrices carry SHA-256 digests, and the new workflow runs six independent Sturm counts plus explicit negative controls.

**Scope:** finite two-dimensional spatial tori with Euclidean time, finite group S3, fixed JE=JB=1. These are not continuous SU(3), four-dimensional R4, a real laboratory mass, or a Clay Millennium solution.
