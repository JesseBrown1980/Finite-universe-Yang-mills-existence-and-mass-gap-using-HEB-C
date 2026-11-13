# #137 — 14 frozen K3 exact-energy microbrackets at r = 9

The first r=9 finite S3 gap certificate was strengthened by merged #179 to E1 in (69.908, 69.92), E2 in (69.948,69.9567503) and E2-E1>0.028 (in J_E). Its conservative W-normalized Schur error made the subsequent projector lane #181 insufficient for a true first-Wilson-weight theorem. Merged #180 **independently** certifies a strictly positive *original unshifted conventional seven-loop* Wilson transition for two **frozen exact-Q-resolvent-dressed trial vectors/energies**; it has not identified the true eigendirections.

This lane makes the next independent measurement: evaluate exact inertia at 14 more threshold points near the historical K3 trial Ritz locations, to tighten **true finite-H spectral windows** while keeping the trial eigenvalue estimates separate from proof claims.

## Freeze, source, arithmetic

The exact 14-point grid at denominator 10^9, floor 94.0682 J_E, 20 Jacobi iterations at scale 10^12, original K3/checker hashes, and the **two previously measured U/G hashes** were sealed in [PREDICTION.hbp](PREDICTION.hbp) *before replay.py was written*. The two historical sample energies 69.909875505 and 69.949729820 are **probe locations only**.

The replay reconstructs all 155,378 K3 Q orbits, all 1,985,218 shell-4 residual orbits and their weighted electric edges from the pinned source. At every point \(z=a/10^9\), it recomputes the source U and G 8×8 integer quadratic forms and exact full-Q-residual Gram, with the accepted lift-free floor \(\gamma=94.0682J_E\). The 8×8 lower L is

    L = 6*(10^9*94068200 - a*10^6)*U - 10^6*G.

Independent negative eigenvalue counts use characteristic-polynomial Descartes on the whole 8×8 and reflection-even 7×7 matrices and an explicit odd scalar, not the source's original Sylvester routine. An independent check of every nonempty principal minor (255 per point) verifies G PSD. Negative controls are source hash, individual freeze fields, exact sector splitting, full shell-4 graph size, PSD and monotone count constraints.

## Full-space count conversion, not Ritz estimates

When \(\gamma>z\), the full-H number \(N(z)\) of levels strictly below z equals the negative inertia of the exact 8-flat Schur complement S(z). For each source trial matrix, the accepted Feshbach residual identity gives

    n_-(U) <= N(z) <= n_-(L).

The exterior residual is complete by the K3 graph construction. These inequalities hold no matter how well the 20 Jacobi steps approximate the resolvent. Reflection sectors are accounted for by exact integer congruence; the already accepted #176/#177 E3 lower bound at 69.9686993 allows \(N(z)\le2\) at all frozen thresholds. Each U/G matrix is recalculated, source-hashed and independently recounted; the original Ritz root estimates do not enter any theorem bound.

Because the trial matrices change with z, their individual count *bounds* need not be monotone. Instead the true \(N(z)\) is monotone: at threshold i, the lower count is at least the max of all earlier lower counts, and the upper count is at most the min of all later upper counts. This logically valid closure also preserves [0,1] or [1,2] points explicitly as HOLDS.

Starting from accepted windows E1 in (69.908,69.92), E2 in (69.948,69.9567503), the script tightens only via:

- \(N(z)\le0\) proves E1 above z.
- \(N(z)\ge1\) proves E1 below z.
- \(N(z)\le1\) proves E2 above z.
- \(N(z)\ge2\) proves E2 below z.

Strict endpoint claims are justified when the enclosing symmetric forms have verified nonzero eigenvalues and the matched sector inertia excludes a Schur zero at those thresholds; otherwise the conservative nonstrict boundary is retained. All denominators and energy gaps are integer arithmetic and emitted in numerator/denominator form. The output records exact points, enclosures, SHA fingerprints and an explicit conditional scope.

## Next projector transfer

If this lane yields smaller true E1/E2 windows, rerun the previously source-checked directional Schur projector test (#181) at the frozen #180 trial pairs. Compute an **improved directional energy drift bound** using \(\|B x\|\) as well as the source Frobenius bound \(\|B\|_F\), not just \(\|B\|_F^2\), and separately enclose the 8-flat effective Q-resolvent correction. The result must keep all state-error terms and full W normalizations; certifying a true E1→E2 Wilson weight requires a positive rational final amplitude interval. A sufficient conservative target already filed on #137 is a sum of normalized eigenstate-vs-fixed-sample errors <1/700.

## Run and acceptance

    python3 -I -B independent/y137-k3-microbrackets-20261113/replay.py

Hosted CI checks the original pre-result freeze git blob, the two old U/G matrices, the complete source-rebuilt 14-point replay, exact 14/14 independent inertia and PSD checks, and repository no-float/native gates. File the new output receipt **after** hosted measurement and require byte-identical reproduction at the final merged head. An inconclusive bracket is a valid HOLD; it is never promoted into a theorem.
