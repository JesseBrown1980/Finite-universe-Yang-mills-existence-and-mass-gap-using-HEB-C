# Stage F — E2-dominated full-state error decomposition and trial interpolation

**Research draft: November 16, 2026.** Stacked on draft Stage E PR #234. All Stage C, D and E accepted files are untouched. The next test is a small, fixed-grid sensitivity experiment; it does not add new physics assumptions or independently prove the first Wilson weight.

## Input and frozen controls
- Exact signed `mu3_six` at both frozen energies, SHA-verified by the merged Stage D parser; exact four-moment Schur brackets; Stage E 3-moment energy windows.
- Stage E original receipt and source-conditional `E1=0.003235251105`, `E2=0.008676646901` CENTRE_MOVED normalized error; total `0.011911898006`. Stage F *must* reconstruct both exact components for alpha=8/8.
- Fixed original Wilson sample `v0` and Stage E centre-inverse-iterated `v1`; test only `v(alpha)=(8-alpha)*v0+alpha*v1`, `alpha=0,1,...,8`, independently for E1 and E2. This uses exact integer directions with W-normalized comparisons, not a claim that the original Wilson observable has the same amplitude on the new sample.

## Breakdown

For each trial, recompute from exact Stage E data:
1. Centred 8-flat residual, full four-moment width action using exact 7D weighted complement PSD, and the resulting eigendirection sine ceiling.
2. Certified energy-window drift and eigengap.
3. Q-tail rotation and Q-tail energy-shift terms.
4. Full state normalized error with positive Q norm lower bounds.
5. Trial displacement from the *fixed accepted Wilson sample*, its Q-spread, and the triangle cost added to the true/sample error.

A separately reconstructed integer formula must reproduce the accepted `fw.compose` output **at every trial**. The best combination is the sum of the best per-eigenstate bounds; the two vectors may be interpolated independently. Any improvement remains a **research candidate** pending external arithmetic/source review.

## Precalculation exact structural result

At alpha=8/8 the accepted E2 trial-vector W-flat displacement is **3693022069/10^12**. Since the current transfer adds `sqrt(displacement^2 + Qspread^2)` as a positive triangle term, **the E2 displacement alone exceeds 1/700**, regardless of the Schur width or energy-window reduction. This proves a limitation of the *present fixed-Wilson-sample triangle route with the Stage E moved vector*. It is **not** an assertion that the underlying transition vanishes or that all interpolants fail.

The two best previously certified state error terms must both improve, since E1's current error alone also exceeds 1/700. A new Wilson sample with independently certified amplitude or direct observable-specific bound may avoid the triangle penalty.

## Acceptance and review boundary

No assertion about best interpolated alpha or an improved numerical error until dedicated hosted results arrive. Check exact SHA inputs; reject out-of-range alpha, corrupt source, old Stage E regression, bracket nesting or integer arithmetic failures. Capture source/receipt SHA-256 and the Actions commit. Maintain PR **DRAFT**, #137 **OPEN/HOLD**, and independent C/CPT seat #233 separately.

Run: `python3 -I -B independent/y137-stage-f-budget-20261116/stage_f_budget.py`.
