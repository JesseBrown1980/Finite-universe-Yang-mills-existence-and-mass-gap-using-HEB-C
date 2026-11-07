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

The six counts use outward-rounded 90-digit GMP Schur-complement intervals and fail closed on ambiguous pivots. These are **six thresholds/blocks in one GMP implementation**, not six independently written eigensolvers. If all six pass, the global E0 and E1 are even and E2 is odd, while the next even excitation E3 is at least 13.6. This guarantees **exactly zero** overlap of O_minus with E1 (by parity), reversing the successful 1x1 operator choice.

## A strict **positive** E1 overlap for O_plus, without floating point

A positive 850-power Perron approximant to K=60I-H, from the all-ones vector, is exactly even. By W-weighted integer residual arithmetic and the certified E1>13.24 lower bound, its squared angle from the true interacting vacuum is less than 10^(-80).

Take the exactly centered integer vector u=(norm_W(v)^2) O_plus v - <v,O_plus v>_W v, which is even and W-orthogonal to v. For 230 powers of K, calculate exactly

    F = <u,K^230 u>_W / <u,u>_W.

Positivity of H and the conservative spectral bound H<=60 imply 0<=K<=60. If O_plus had zero spectral weight on E1, all its even excited spectral support, *apart from rigorously bounded approximate-vacuum leakage*, would have energy at least 13.6.

**Correction from independent mathematical review (2026-11-07): both low modes need a leakage allowance.** Let phi=v/||v||_W, psi be the exact normalized vacuum, delta=sin²(angle(phi,psi))<10^-80, mu=<phi,O_plus phi>, and u_prime=(O_plus-mu)phi. The exact integer program now separately checks **V=||u_prime||_W²>=1** through `dot(u,u)>=norm**3`. For O_plus the operator norm is at most 4 and |mu|<=4. If the *true* E1 overlap vanished, then |<E1,u_prime>|<=8||phi-psi|| and its squared weight is <=128 delta (using ||phi-psi||²<=2 delta). Since u_prime is orthogonal to phi, its ground-component fraction is <=delta. Dividing by V>=1 gives a **combined normalized low-energy fraction <=129 delta**. Thus the **corrected** null-overlap implication is

    F <= (60-13.6)^230 + 129 * 60^230 / 10^80.

The new checker explicitly computes the exact *positive integer excess* of its 230-step response over this strengthened threshold. Its SHA-256 is pinned to the independently calculated witness `2d5504cbc526c07d7264b3a055f3bee5550a1cf62dc4ce869f9e6670f8d8cc3f`; this input was provided in the independent review **before** implementation of the correction. The integer proof rejects the old assumption that ground-state leakage alone suffices.

The corrected exact integer witness still strictly violates the null-case bound, establishing nonzero overlap with the global E1 **conditional on the separately certified GMP inertia counts**. No unverified decimal eigenvector is required. This is a strict sign certificate, not yet a tight enclosure of the first spectral weight magnitude.

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

The exact integer input freeze is PREDICTION.hbp at commit 9858660f3254c4c03092deade18363c4cc2dc06d. The full independent row regeneration is anchored by the pre-existing exact 2x2 operator SHA in independent/gpt6_2x2_from_permutations.py. The paired output matrices carry SHA-256 digests, and the workflow runs six parity-resolved Sturm counts, four structural/symmetry controls, and an additional **validly formatted but deliberately altered symmetric even-sector matrix**: two diagonal entries are changed to -1,000,000, and the same GMP inertia checker must detect at least two negative eigenvalues at threshold 13.24, unlike the source matrix's one. This detects wrong-operator acceptance, not merely malformed input.

**Scope:** finite two-dimensional spatial tori with Euclidean time, finite group S3, fixed JE=JB=1. These are not continuous SU(3), four-dimensional R4, a real laboratory mass, or a Clay Millennium solution.
