# Exact rational projector-angle acceptance checker

`check_projector.py` implements Theorem B/C in [THEOREM.md](THEOREM.md) using Python `fractions.Fraction` without floats, external packages, or producer imports.

**Scope:** isolated mathematical arithmetic verifier. A PASS is *conditional on the supplied authentic lower/upper Schur matrices and the separately certified true E1/E2 branch*. No original physical matrices are embedded in this PR. An isolated synthetic PASS cannot promote the Wilson certificate.

Input: JSON with **stringified rational scalars** and 8x8 symmetric **W-bilinear** (not operator) `schur_lower` and `schur_upper`; `weights` diagonal positive entries, 8-component `witness`; `sample_energy`, `gamma`, `upper_energy`, `window_drift`, `coupling_norm_sq_upper`, `envelope_norm_upper`, `projected_residual_upper`, `compressed_singular_lower`, and `target_sine_upper`.

The source must independently establish that the actual physical Schur bilinear S(E) lies between L and U at sample energy z, that the true energy E satisfies |E-z|<=window_drift and E<=upper_energy<gamma, and that ||B||^2<=coupling_norm_sq_upper. The bound `envelope_norm_upper` is checked against a weighted Frobenius norm of (U-L)/2. The residual bound is checked against the exact projected midpoint residual plus verified energy-window perturbation. The singular lower is certified by exact strict PD of K G^-1 K - (delta+eta)^2 G on the 7D W-orthogonal complement. The final sine cap is checked by an exact rational squared inequality.

Run: `python3 -I -B independent/y137-eigenbranch-projector-audit-20261118/check_projector.py certificate.json`.

Run controls: `python3 -I -B independent/y137-eigenbranch-projector-audit-20261118/test_projector.py`. The controls use a **synthetic** eight-state fixture, and eight deliberate changes are rejected. This exercises algebra, not the original finite S3 source.

**Next original-model operation:** prepare two authenticated JSON certificates from #317's exact 8x8 Stage D Schur matrices and #311/#284 matched witnesses, with correctly oriented W-bilinear coordinates and original energy brackets; run both. If the coarse common Lipschitz enclosure yields HOLD, develop a tighter endpoint-resolvent/Loewner approach. Independently check all source fingerprints, endpoint inertia and branch labels before any original-Wilson theorem acceptance.

Status: original-model projector numerical verdict OPEN; finite original first-Wilson source-conditional candidate / formal HOLD; four-dimensional continuum OPEN.
