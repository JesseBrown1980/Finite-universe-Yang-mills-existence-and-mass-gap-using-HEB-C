# Issue #137 — correlated two-energy Feshbach/Gram Wilson projector gate

Research draft, November 18, 2026. Primary target: **the original first-excitation seven-loop Wilson spectral weight** for the periodic finite 3×4 S3 Yang–Mills Hamiltonian. Stacks on source-pinned PR #285. The original Hamiltonian and observable are unchanged.

## Exact structural two-energy identity

In weighted physical flat/Q coordinates, let B=QHP, R_i=(QHQ-E_i)^(-1), and G21=I+B-sharp R2 R1 B. Since the exact full physical first and second eigenstates are orthogonal, <x2,G21 x1>_W=0.

The original integer observable O2=2O-7I defines the full-Q dressed effective matrix M2. For every rational c, <x2,M2 x1>_W=<x2,(M2-c G21)x1>_W. The actual original Wilson transition amplitude is half the O2 amplitude because the true eigenstates are orthogonal. Certified physical norm factors are positive.

## Correlated original-source representation

The frozen unshifted 64-entry weighted-bilinear matrix A0 and centered integer O2 matrix A2 share **the same four original Q inverse/residual SHA hashes**. Their exact shared-trial two-energy Gram center is Ghat=(2 A0 - A2)/7, with no nonintegral entries permitted. The rational shift c=p/q has exact source numerator Ac=(7q+p) A2 - 2p A0 and common denominator 7q T^2, T=10^12. The source retains W=(1,3,2,3,3,2,2,2).

Two gates are measured independently:

1. **Nominal joint-dark geometry.** Let g=W^-1 Ghat v1, s=W^-1 A2 v1 for the frozen original first-flat direction v1. The closest state simultaneously orthogonal to both the nominal Gram and nominal Wilson directions has a source W-sine distance obtained from an exact 2x2 Gram projection. The minimizer cstar=<s,g>_W/<g,g>_W removes the Gram-parallel nominal action. A nominal separation is a source diagnostic only.
2. **True physical dark-state exclusion.** Construct ten rational shifts: 0, 1, 2, 5/2, 11/4, 3, 13/4, 7/2, 4, and cstar. The actual effective matrix and the Gram for the true energies inherit source entrywise intervals R2 and R0. The safe combined radius is Rc=|7q+p| R2+|2p|R0; crucially it does not assume favorable covariance. Both accepted true W-flat E1 and E2 sine cones are carried into outward-rounded chord bounds. For a true Wilson-dark eigenstate, Gram orthogonality enforces <x2,(M2-c G21)x1>_W=0. The script uses the triangle inequality to derive a rigorous *necessary* upper bound on the frozen sample amplitude from the source-directional radius, both projector errors, and source operator norm (the dressed original O2 operator has the required full-Q factor 1+72/[(gamma-E1)(gamma-E2)], so both the 21 term and the shift term carry that factor). A strict positive signed margin would be a source-conditional candidate requiring independent review. Nonpositive means HOLD.

The exact W-adjoint rank-one projector trace equals the scalar amplitude square for both the unshifted and Gram-optimized nominal candidates. The independent verifier reads both 64-entry original HBP sources by their Git blob SHA pins, reconstructs four common Q SHA fields and all 10 candidates without importing the producer, and rejects 6 tampered receipts.

## Scientific interpretation

Shared source centers are exactly correlated algebraically, but the separate HBP interval radii cannot be treated as a certified covariance reduction. This diagnostic may show the best rational shift for a subsequent *direct same-Q joint dual-residual* calculation. A source-specific true E1 projector action estimate is the parallel target. Both are needed when the old conservative interval budget leaves a negative rigorous margin. Source-only Gram-dark exclusion is never promoted to a physical first-excitation Wilson certificate.

## Run

    python3 -I -B independent/y137-correlated-feshbach-gram-20261118/correlated_gram.py toy
    python3 -I -B independent/y137-correlated-feshbach-gram-20261118/correlated_gram.py real > RESULT.hbp
    python3 -I -B independent/y137-correlated-feshbach-gram-20261118/verify.py RESULT.hbp

**Scientific status:** source-conditional finite S3 gap PASS; original first-excitation seven-loop Wilson spectral weight HOLD pending strict certified true-projector lower bound; 4D continuum OPEN.
