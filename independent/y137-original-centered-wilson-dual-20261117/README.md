# #137 — centered original seven-loop Wilson dual: actual full physical Q source

Research draft, November 17 2026. Source-specific numerical follow-up to the exact five-law audit #280, stacked on original source full-Q directional dual PR #276. Original finite spectral gap source-conditionally certified; true first-excitation summed-winding Wilson weight HOLD.

The original faithful-character seven-loop Wilson O is diagonal multiplication with universal physical orbit values -7 through 14. Center at rational midpoint mu=7/2 and work with the exact integer observable

    O2=2*O-7*I=2*(O-(7/2)*I).

This gives ||Q O2 Q|| <= 21, whereas doubling the original unshifted norm cap 14 gives 28. The centered universal Q operator norm is 25% smaller and all physical S3 computations remain exact integers. The full observable is centered, including POP.

## Original-source calculation

The script dual_centered.py replicates the original PR #276 source-specific dual machinery, substituting integer diagonal O2 for O, using norm cap 21 in the quadratic full-Q residual and true energy-window drift bounds, and adding exact fixed-trial overlap controls. The program reconstructs the 24-link original S3 seven-loop O, both accepted true E1/E2 physical energy upper-endpoint K3 Q trials, both complete shell4 physical residuals, both independent directional dual solves and their complete shell4 residuals, and the original POP and QOQ signed contributions. Immutable original #178/#180 source and Bdagger B=72 I receipt pins are required.

For the original fixed flat vectors v_i and their numerical Q trial legs, it checks the exact integer identity

    M_O2_trial = 2*M_O_trial-7*<trial2,trial1>_W.

The overlap of the fixed trial states is nonzero, so omitting the final term is explicitly rejected. The signed source dual estimator and all errors are recalculated for O2. There is NO assumption that historical fixed samples are exact eigenvectors.

For true physical eigenstates psi1 and psi2 with E1!=E2, exact orthogonality implies

    <psi2,(O-(7/2)I)psi1>=<psi2,O psi1>.

Thus strict nonzero true O2 transition means nonzero original O transition, with signed amplitude divided by 2 and squared spectral weight divided by 4. This exact invariance is NOT available for nonorthogonal fixed samples without the overlap correction above.

The hosted output reports source lower fixed-direction squared weight for O2, conservative centered weight floor after dividing by four, complete source signed residual and true-energy drift errors, and the original sample-shift defect SHA. It always emits actual_first_excitation_Wilson_weight=HOLD; positive fixed-direction signal alone is not the true first Wilson weight.

## Acceptance and comparison

The previously accepted original unshifted source PR #276 had fixed-direction squared Wilson weight >0.001027970 across both physical energy windows. Centering may increase or decrease the signed fixed-trial signal even though it decreases the universal Q norm contribution; compare the actual signed margins, dual errors, drift errors and normalized fixed-direction weight. Do not infer a uniform 25% reduction in total Wilson transfer error.

To use a favorable centered source in the original E1/E2 projector test, recompute the centered low-block observable and its deflated source action. Reusing the unshifted PR #278 eight-flat entry matrix without the exact scalar shift correction is prohibited. Original finite 3x4 gap already source-conditionally proved; first Wilson visibility HOLD; continuum Yang-Mills OPEN.

Run: python3 -I -B independent/y137-original-centered-wilson-dual-20261117/dual_centered.py centered
