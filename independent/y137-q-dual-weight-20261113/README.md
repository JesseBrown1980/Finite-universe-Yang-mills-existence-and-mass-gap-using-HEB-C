# #137 — source-pinned full-Q Wilson effective transition with dual residuals

This is the **next actual 3×4 periodic S3 at r=9 numerical calculation** after the frozen K3 energy-grid lane (#179). The source pair is the historical estimated K3 Ritz roots Ehat1=69909875505/10^9 and Ehat2=69949729820/10^9; these are **fixed sample energies**, not exact certified eigenvalues. The pair and the algorithmic controls were sealed in PREDICTION.hbp (commit b605f489) before replay.py was written. The accepted lift-free Q floor is gamma=94.0682 J_E, conditional on the corresponding existing source certificate.

The script imports the same pinned K3 graph as the merged #176/#177 certificates and reconstructs its 155,378 nonflat Q states plus 1,985,218 weighted shell-4 exterior targets. An independent S3 permutation/24-link Wilson builder from merged #178 computes the conventional sum of four horizontal and three vertical faithful-character winding loops on **every trial state**, including the eight flats. It also checks the flat holonomy formula and reflection selection.

It computes two seven-dimensional reflection-even approximate flat null vectors with **integer Cramer's-rule inverse iterations** on the exact K3 U matrix at the two frozen sample energies. Their 8-flat lifts are exact integer vectors. Twenty source-Jacobi iterations yield the finite-support Q vectors and the full K3 W-normalized trial overlap, with flat and Q contributions separately. Every Q residual is rebuilt from the CSR operator and the full shell-4 edge list; the exact squared W norm is compared to the original source Gram form G.

## Corrected Q transition and certified dual error

Write the W-orthonormal Hamiltonian in P/Q blocks (or use the equivalent W-adjoint formulas in raw orbit coordinates). At fixed sample E_i<gamma and flat vectors x_i, let \(\hat y_i\) be a trial Q vector and

    r_i = (D-E_i) yhat_i + B x_i,
    y_i = yhat_i - (D-E_i)^(-1) r_i.

The actual resolvent-dressed Q vectors at these **fixed trial parameters** are uniquely defined by the positive Q floor. For \(O_2=2O-7\), which obeys \(\|O_2\|\le21\), solve two approximate dual Q problems with trial vectors \(u_{21},u_{12}\):

    d_21 = O_2 yhat_1 - (D-E_2)u_21,
    d_12 = O_2 yhat_2 - (D-E_1)u_12.

Then the full Q-corrected O2 transition has the explicit signed center

    Acenter = <x2,O2_P x1> + <yhat2,O2_Q yhat1>
              - <r2,u21> - <r1,u12>

and an **absolute** error bounded by

    err <= ||r2|| ||d21||/(gamma-E_2)
         + ||r1|| ||d12||/(gamma-E_1)
         + 21 ||r1|| ||r2||/[(gamma-E_1)(gamma-E_2)].

This follows from the exact self-adjoint resolvent identity and Cauchy-Schwarz. It replaces the old \(\|O\hat y\|\) first-order term by an independently measurable dual residual. The code reconstructs both dual residuals including **every shell-4 exterior edge** and rounds integer square roots strictly outward. The very same source floor controls both resolvents.

If abs(Acenter)>err, the code may print a **strict rational positive lower weight for the two resolvent-dressed *fixed sample vectors*** after upper-bounding both norms using \(\|y_i-\hat y_i\|\le\|r_i\|/(\gamma-E_i)\). Such a successful sign test establishes a genuine nonzero matrix element for that fixed flat pair with exact infinite-Q dressing. It is **not** a certified \(E_1\to E_2\) spectral transition until the eight-flat null projectors and true energies are rigorously enclosed.

## First hosted result — sign certified for the fixed trial parameters

The initial hosted replay at [run 43487300716](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43487300716) passed including the strict no-float and integer-only audits. Its original ten exact output rows were filed **after the run** in [RESULT-WILSON-Q-DUAL.hbp](RESULT-WILSON-Q-DUAL.hbp). A later code revision adds a required sample-overlap bound and will produce a new output receipt; the older ten rows remain the pre-revision evidence.

Results:

- All **155,378 Q states** and **1,985,218 shell-4 targets** were reconstructed. The independent 24-link Wilson observable attained the exact theoretical endpoints **-7 and 14** on the K3 orbits.
- For the two frozen sample energies, the finite-K3 trial residual norms, rounded outward, are **0.170814** and **0.174313** relative to the W-normalized trial vectors. Their whole-Q residual sums agree **exactly** with the original G forms including the shell-4 contributions.
- The raw finite-trial normalized Wilson squared amplitude is between **0.001158787** and **0.001158788** (both decimal endpoints are integer-rounded), matching the earlier K3 exploratory magnitude.
- After evaluating both dual-residual correction terms and the second-order remainder using the accepted Q floor, the shifted observable O2=2O-7 signed amplitude interval excludes zero. The **fixed-sample sign test passes** by a large, explicitly positive integer margin.
- The resulting rigorous rational lower bound for the **shifted O-7/2 observable** between the two **exact Q-resolvent-dressed, frozen sample-flat vectors and frozen sample energies** has a decimal lower endpoint of at least **0.001059210** in normalized squared weight. The exact numerator and denominator are in the receipt. It is a *conditional fixed-sample effective-operator result*, **not** yet the true first-excitation spectral weight.

**Shift correction that must be certified separately:** Replacing the original raw Wilson O by O-7/2 leaves a transition unchanged only when the two states are exactly orthogonal. These frozen approximate states are **not** certified orthogonal. The new replay therefore computes a full-Q-resolvent enclosure for their actual overlap (including quadratic residuals), then uses

    2|<Psi2,O Psi1>| >= |<Psi2,(2O-7)Psi1>| - 7|<Psi2,Psi1>|.

A positive unshifted fixed-sample sign is announced only when the **overlap-corrected** margin is strictly positive using integer-outward bounds. If negative, the true raw fixed-sample transition remains HOLD. The exact E1/E2 spectral weight remains OPEN regardless of the fixed-sample verdict.

This is an independently reproducible numerical outcome for the actual K3 trial and complete nonflat Q correction. The result makes the next task precise: certify the true energy-dependent eight-flat eigendirections close enough to this pair that the positive interval survives after the projector error. The source-frozen (E_1,E_2) brackets are now stronger on main via PR #179 (first gap >0.028), but a direction-sensitive Schur error bound must still be computed; the previous broad matrix trace bound near 0.00936 is insufficient by itself.

## Independent acceptance and remaining theorem obligation

The run must pass source and frozen-grid pins, independent full-link S3 Wilson reconstruction on the actual K3 state keys, complete weighted shell-4 residual squared norms agreeing with Gram G **exactly**, both dual residuals, exterior weighted-balance checks, and strict no-float audits. Negative controls on #178 already establish that a single-link character and a single winding row are invalid symmetry substitutes. The full result should record the approximate-trial overlap, the signed dual-corrected center, each separate error, and either a positive rational fixed-sample enclosure or an explicit HOLD.

The missing final gate is an independent **uniform energy-dependent eight-flat spectral projector** interval from the actual Schur matrix. The new source-backed energy brackets of PR #179 are a starting point; old K3 Ritz roots are not certified true energies. To transfer any fixed-sample positive transition to the true eigenstate weight, separately enclose the flat-vector and energy perturbation of the P/Q effective operator and both full W normalizations, then prove that the final rational amplitude interval excludes zero. Until this is done issue #137 stays OPEN.

Run:

    python3 -I -B independent/y137-q-dual-weight-20261113/replay.py

The hosted workflow stores integer receipts from this calculation without changing historical evidence.
