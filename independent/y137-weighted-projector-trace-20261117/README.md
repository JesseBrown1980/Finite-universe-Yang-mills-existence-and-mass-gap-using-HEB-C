# Issue #137 — exact weighted flat-projector Wilson trace and Gram correlation

Research draft, 2026-11-17. Independent test of

    T(E2,E1)=tr(P2 K(E2,E1) P1 K(E2,E1)^sharp)
            = |<x2,K(E2,E1)x1>_W|^2,

where the *true* x_i are normalized W-flat components of the source-conditional simple physical E1/E2 eigenstates. K is the **integer twice-centered original seven-winding Wilson** O2=2O−7I effective operator, including complete QOQ double-resolvent contribution. P_i are rank-one W-flat orthogonal projectors, and sharp is the **Wflat-adjoint**. This is not ordinary Euclidean transpose in the archived orbit-coordinate representation.

## Structural and source gates

The archived original source #282 64-entry signed matrix A has entries of the Wflat *bilinear* form and common denominator 2*T² for Ocenter=(O−7/2 I), with T=10¹². For O2=2O−7I, the real coordinate operator matrix is

    K_ij = A_ij /(w_i T²)
    Ksharp_ij = A_ji /(w_i T²)
    P_i[a,b] = (v_i[a] * w_b * v_i[b]) / sum_k w_k*v_i[k]^2,

where original flat orbit weights are (1,3,2,3,3,2,2,2). The code independently expands the fourfold 8×8 matrix trace in exact rational pairs and recomputes the scalar contraction as

    T_trial = (v2^T A v1)^2/(T^4 * ||v1||_W² * ||v2||_W²).

Both must be *exactly* equal. A nonnormal three-dimensional weighted toy rejects replacing the W-adjoint with an ordinary Euclidean transpose.

This trace is initially for **the original fixed two flat sample projectors**, because the exact true P1,P2 still require certification. The real full-Q signed source-specific dual #281 supplies a lower squared **fixed-flat** weight >0.004232581 for O2 at all certified true physical E1/E2 energies, a source correlation lost when the 64 entry error boxes are treated independently. The accepted Stage E PR234 full-state/four-moment source plus PR277 normalized projection theorem supply the source-conditional true W-flat sine caps. The trace verifier expands the true-state changes into explicit linear and quadratic Wflat projector terms, with source-specific deflated M action norms, full-Q matrix-error inflation, and the exactly source-bounded ||K||.

This test reports an exact outward-rounded interval for the **true rank-one projector trace**, converting the certified positive fixed sample squared weight to a strict positive lower only if the signed true-source contamination margin is positive. If zero is still permitted, it emits HOLD. It cannot infer that T>0 merely because the historical fixed-flat source is bright.

## Exact two-energy overlap metric and correlation

For the same original 8-flat coordinates, let

    G(E2,E1)=I+Bdagger (QHQ-E2)^(-1) (QHQ-E1)^(-1) B.

Since the exact full physical E1 and E2 states are orthogonal,

    <x2, G(E2,E1) x1>_W=0.

To expose a source-level correlation, the code pins the **same four full-Q trial and residual SHA hashes** in original unshifted PR273 and original integer centered PR282. For their integer trial matrices (both common bilinear denominator T²),

    Mhat_O2=2*Mhat_original-7*Ghat

holds **exactly**, not approximately. The checker reconstructs the trial two-energy Gram Ghat entry-by-entry as (2*A_original-A_O2)/7 and rejects any nonintegral discrepancy. The true Gram error is enclosed independently from both complete original matrix-entry radius boxes, with no omission of physical exterior shell4. This conservative enclosure checks consistency of the original sample projections with true-state orthogonality; it is not automatically a sharp projector-rotation certificate.

The code emits the actual rank-one source trace metadata, whether the naive 64-entry sample bilinear box contains zero, the source-specific positive fixed-direction dual floor, separately weighted E1/E2 projector linear and quadratic contamination terms, the strict signed amplitude margin, a safe nonnegative trace lower and upper, and the orthogonality feasibility verdict.

## Acceptance and scientific scope

An exact positive projector-trace lower bound, once independently verified with authentic true physical eigendirections, implies positive original first-excitation Wilson spectral weight because O2 and O differ by a scalar plus factor two, and true states are orthogonal. The source-accepted nonflat spectral floor ensures full Feshbach state norms are finite and positive. Quantitative normalized weight requires dividing the unnormalized true flat trace by the two true positive full-state norm squares and by four for O2→O.

A **zero** projector-trace lower is a valid numerical HOLD. It does not disprove Wilson visibility. In particular, mathematically rewriting the amplitude as a trace cannot itself remove angular uncertainty; a new source restriction on true projectors or a sharper source-specific action bound is required to strengthen the result. This is a genuine original-S3 source test of the full 8×8 W-adjoint algebra and two-energy overlap constraints, not a toy substitute.

All exact-integer arithmetic is covered by the repository no-float and immutable source hashes. Source conditional finite 3×4 spectral gap remains established, actual first Wilson spectral-weight certificate remains HOLD absent strict positivity and independent review, continuum theorem OPEN.

Reproduce with .github/workflows/y137-weighted-projector-trace.yml and projector_trace.py real.
