# Exact-integer 3×4 finite S3 FIRST spectral gap at r=9 — conditional certificate

November 8, 2026. POST-EXPLORATION, not prediction-first; independent mathematical review required.

The full periodic 3×4 S3 gauge Hamiltonian H=J_E(E+rM), r=9, has 2,177,317,873 physical orbit states (not 45,508,080). Energies are indexed one-based.

## Conditional result

Assuming the already accepted original 3×4 positive Perron vector and its pointwise whole-space nonflat orbit lift from merged finite PR #131, the executable integer-only certificate establishes

    69.89 J_E < E1 < 69.92 J_E
    69.93 J_E < E2 < 69.96 J_E
     0.01 J_E < E2-E1 < 0.07 J_E.

**Precisely named accepted source hypothesis:** `lambda_min(QHQ_whole) >= 94.070673 J_E`, where Q is the W-orthogonal coordinate complement of the eight magnetic-flat physical orbit basis states. The accepted Perron proof establishes this nonflat *principal-compression* lower bound first, via a positive sector vector and an invariant pointwise whole-space lift (`native/ym/results/3x4_stream/perron/PERRON-BOUND.md`, §1 and §2, especially §2 line 40). Only then does interlacing imply `E9_full >= 94.070673 J_E`. **The E9 bound alone is not sufficient for this Schur certificate**; the full-Q principal-compression bound is the explicit assumption checked in the proof composition and named in the current HBP field `accepted_source_assumption=lambda_min_QHQ_whole_GE_94070673/1000000`.

It rechecks the pinned original Perron HBP Git blob and the source value, but does NOT replay or download the 45,508,080-row store. The original historical OPEN Perron receipt remains untouched. The second seat's independent review approved the mathematical derivation subject to this label correction and the original all-orbit lift assumption. The reviewer rebuilt the 8/264/7770/147344 census using a different gauge fixing and established the same four inertia counts using a separate trial inverse and characteristic-polynomial method. The [review source and report](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/tree/f08be736aeb999a51ea9f288474f2f9c8bd3e853/review/pr136-second-reviewer-20261108) are preserved on branch `cloud-seat-pr136-review-20261108` (head `f08be73`). The original post-exploration HBP (before the terminology correction) is preserved byte-identically at `independent/MEASURED-S3-3X4-R9-FIRST-GAP-20261108.pre-review-label.hbp` (original Git blob `3ebe0a5c80568a6965b786dd97be85befb5366d2`). Only that one label was updated in the current receipt; its four threshold counts and matrix hashes are unchanged.

## All-state residual from a small exactly reconstructed neighborhood

Using six exact S3 permutations, 24 oriented electric links and a spanning-tree gauge fixing (13 remaining free group elements modulo global conjugation), the checker reconstructs the full physical orbit graph near all eight magnetic-flat holonomy classes:

| Distance from the eight flats | Number of physical orbit states |
|---|---:|
| 0 | 8 |
| 1 | 264 |
| 2 | 7,770 |
| Total trial space | 8,042 |
| Exterior residual targets (one further electric move) | 147,344 |

It checks all 72 electric transposition moves per included state, the full flat conjugacy classification, the 18-unit raw flat weight, and exact weighted adjointness on every Q−Q and P−Q internal link. Each exterior target and weighted electric coefficient is retained explicitly, not silently cut off.

## Exact Schur sandwich

In the weighted physical orbit inner product define K_z=W(bH−aI) for the rational threshold z=a/b, b=100, partitioned into eight flats P and all nonflats Q:

    C=P K_z P; F=Q K_z P; A=Q K_z Q;
    S(z)=C − F^T A^-1 F.

The original full-space Perron comparison gives A >= gamma W_Q with gamma=b*(94.070673-z)>0. Hence N_full(z)=n_-(S(z)) by the exact Schur congruence. Form an arbitrary integer trial X_int (Q×8) with support inside the two-move nonflat neighborhood. The checker uses precisely four fixed-point integer Jacobi iterations with scale L=10^9; no assumption that these solve exactly is needed.

Define the complete residual R=L F−A X_int, including all 147,344 exterior rows, and

    U=L² C−L(F^T X_int+X_int^T F)+X_int^T A X_int,
    G=6 R^T (W_Q)^-1 R.

Both U and G are integer 8×8 matrices, recomputed from exact graph coefficients. The resolvent identity yields

    L² S(z) = U−R^T A^-1 R.

Since A^-1 <= gamma^-1 (W_Q)^-1, with gamma=gamma_num/10^6, the two exact integer witnesses are

    LOWER = 6 gamma_num U − 10^6 G,
    UPPER = U,

and their integer Sylvester negative-inertia counts satisfy

    n_-(UPPER) <= N_full(z) <= n_-(LOWER).

All determinants are evaluated by fraction-free integer Bareiss, with nonzero leading pivots and SHA-256 hashes of the 8×8 U and G entries. There are no floating-point, fractions, JSON or large full-space eigensolvers in the final source.

## Certified thresholds

| z/J_E | n_negative LOWER | n_negative UPPER | Conclusion |
|---|---:|---:|---|
| 6989/100 | 0 | 0 | E1 > 69.89 |
| 6992/100 | 1 | 1 | E1 < 69.92 |
| 6993/100 | 1 | 1 | E2 > 69.93 |
| 6996/100 | 6 | 2 | E2 < 69.96 |

The 6996/100 lower and upper counts need not agree: n_-(UPPER)=2 already forces at least two full-space levels below it. These one-sided inequalities isolate the ACTUAL first two eigenlevels and give 0.01<E2-E1<0.07 in units J_E.

## Scope and verification

Execute from repository root:

    python3 -I independent/finite_s3_3x4_r9_first_gap.py

Hosted checks must reproduce the literal post-exploration HBP output byte-for-byte, reject deliberate defects, preserve the original source hashes, and pass the repo's no-float and Rust gates. The separate real S3 1×1 Schur-inertia method control in this PR reproduces twelve direct-versus-Schur thresholds and five rigorous nonzero-residual sandwiches; it is NOT a surrogate for the 3×4 calculation.

Unresolved: independent reviewer audit of the new 3×4 proof composition, direct second-machine repeat of the old massive store check, strictly positive first-state zero-momentum winding-sum spectral weight, any SU(2) 4D spatial continuum/Clay claim. No QNN/Opus local plan or production job has been changed.
