# Issue 137: original S3 Wilson coordinate Feshbach simplification

Research draft, November 17, 2026. This is an original-source operator structural identity and a fixed-sample numerical test. Positive first-excitation Wilson weight remains HOLD; 4D continuum existence/mass-gap remains OPEN.

## Exact structural theorem for the original observable

The genuine seven-loop faithful-character summed Wilson observable on the 3x4 S3 torus is an integer-valued multiplication operator on each gauge-equivalence orbit. The original 24-link independent source and its weighted orbit graph establish gauge invariance and the character values. Thus O is diagonal in the canonical weighted gauge-orbit basis.

P is the original 8-flat coordinate projector and Q=I-P includes all nonflat physical gauge-orbit coordinates. Because this is a disjoint coordinate partition in the *original* weighted Hilbert space,

    POQ = QOP = 0,

as exact operators on the complete 2,177,317,873-dimensional finite physical model. This need not hold after changing P to a non-coordinate Ritz/Krylov projector, or changing O to a non-multiplication operator.

Let B=QHP and R_i=(QHQ-E_i)^(-1). With psi_i=x_i plus y_i, y_i=-R_i B x_i, the actual true-state Feshbach effective Wilson operator is

    O_eff(E2,E1) = POP + B^dag R2 QOQ R1 B.

The two general-purpose mixed POQ and QOP contributions vanish **structurally for this original source**. The QOQ term is essential and may cancel part of POP. Full eigenstate norms and actual E1/E2 flat eigenvector directions are still required for any true-state transition proof.

## Source-authenticated fixed-sample test

The independent source file exact_original_wilson_blocks.py pins the original PR 178 24-link Wilson script and PR 180 complete Q-dual receipt and K3 construction source by exact Git blobs. It reconstructs all eight flat and 155,378 nonflat physical K3 coordinates, both frozen even trial flat vectors, and both twenty-step original Q Jacobi trial vectors at the historical sample energies 69.909875505 and 69.949729820.

It reports the signed two nonzero original operator blocks

    F = <p2, O_P p1>_W
    T = <q2, O_Q q1>_W.

The two mixed block contractions are exactly zero, and F+T must reproduce the archived original conventional unshifted Wilson fixed-sample overlap, with exact W normalization and signed sample overlap. Controls reject deleting T, changing the original P-Q support rule, omitting the exact nonzero sample overlap under an observable scalar shift, and changing the frozen sources.

The earlier PR 180 certified an original seven-loop Q-resolvent-dressed **fixed-sample** squared Wilson transition greater than 0.000416300. Neither it nor this new test identifies the true physical E1/E2 eigenvectors. Q trials here are approximations after 20 iterations, not exact inverse-action vectors.

## Next numerical acceptance

A physical true-eigenstate certificate will require (i) full original source-specific 8x8 two-energy effective Wilson interval, including the double-resolvent QOQ term, (ii) true-energy eight-flat Schur spectral projector intervals, and (iii) exact original full-state norms and a strictly nonzero signed Wilson transition lower bound. The atlas's theoretical polynomial inverse-residual m=15 result is not a Wilson overlap error. Retain source-conditional full finite gap 0.039677591<(E2-E1)/J_E<0.040004463, actual first Wilson weight HOLD, Issue 137 OPEN, and 4D continuum OPEN.

Reproduce with the dedicated hosted workflow y137-coordinate-wilson-feshbach.yml.
