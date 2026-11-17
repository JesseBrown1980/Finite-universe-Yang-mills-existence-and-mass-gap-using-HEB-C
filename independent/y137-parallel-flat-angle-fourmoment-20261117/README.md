# Issue #137 — independent Stage E four-moment flat projector improvement

Research draft, Nov 17 2026. This **second true-flat eigendirection workstream** is stacked on the independently checked #275 original Wilson 64-entry matrix contraction, and **does not change** the original Wilson 8×8 source matrix.

The older accepted PR #184 flat Schur-null angle ceilings are `sinθ1<=0.108258863901` and `sinθ2<=0.253465115951`. Hosted Stage E PR #234 has source-conditionally certified *full W-normalized true-eigenstate-to-original exact-Q-dressed sample* distances `d1<=0.003235251105`, `d2<=0.008676646901` by the *CENTRE_MOVED* four-moment test. This branch independently imports the entire frozen Stage E output receipt with its exact Git blob `daf746ca35e44005406be18a872b38a3257e83ff`, verifies original source and historical regressions, and derives a mathematically safe true **W-flat** eigendirection sine ceiling.

For arbitrary normalized physical vectors psi and phi,

    ||Ppsi-Pphi|| <= ||psi-phi|| <= d.

For their nonzero P components, the exact geometric normalization identity gives

    ||Ppsi/||Ppsi|| - Pphi/||Pphi|||| <=
        d / sqrt(||Ppsi||*||Pphi||).

On the original eight-flat coordinate space, both the *true eigenstate* psi_i with energy E_i and the original *fixed-sample* exact-Q-dressed normalized state phi_i at historical sample z_i have flat component norm bounded below by

    (1+72/(gamma-max(E_i,z_i))^2)^(-1/2),

because B*B=72I and QHQ>=gamma=94.0682. The source Stage E true physical energy intervals furnish rigorous upper E_i endpoints. Therefore, with g_i=gamma-max(Ei_upper,z_i)>0,

    sin(angle_flat(xtrue_i,vold_i)) <= d_i*sqrt(1+72/g_i^2).

This is implemented with strict integer roots rounded outward to 1e-12. It is **conditional on independent acceptance of the Stage E original full-state error certificate**, whose PR #234 remains draft; it is never treated as an unqualified proof of Wilson visibility.

The script reuses unchanged #275 original source 64 signed matrix intervals from hosted PR #273, recomputes the **source-specific deflated flat Wilson transition** with improved angles and emits exact signal, contamination, signed margin, and HOLD/PASS-CANDIDATE labels. It never promotes the actual normalized first Wilson weight in a single source calculation. Negative controls reject altered Stage E source, mismatched original flat samples, missing physical energy-window containment, incorrect B isometry, invalid rounding, and source-scoped Wilson requirements. The complete original QOQ double-resolvent reduction is tackled independently by the parallel source-specific dual PR #276.

An improved flat angle is mathematically useful even if the signed Wilson-transition margin is still nonpositive. That would show that the first missing step is the *original observable-specific* QOQ signed source estimate and/or a sharper directional comparison, not another generic eigenstate expansion. The finite 3×4 S3 first spectral gap remains source-conditionally certified; true original first Wilson spectral weight HOLD; continuum theorem OPEN.
