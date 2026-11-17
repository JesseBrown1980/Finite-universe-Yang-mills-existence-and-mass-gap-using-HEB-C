# #137 — inverse Wilson dark-endpoint sweep and center Schur pulse (pilot)

Research draft, Nov 17, 2026. An exact, original-source pilot of the proposed outside-in / center-balancing idea. This is a new *inverse-feasibility* approach, in contrast to repeated tightening of individual eigendirection inequalities.

## Start from the forbidden endpoint

Let x1,x2 be the actual true W-flat normalized physical first-two eigendirections, S(E2) the true second-energy Feshbach Schur operator, and K(E2,E1) the true full-Q centered seven-loop Wilson effective operator (in integer form O2=2O−7I). A dark first excitation must satisfy

    S(E2) x2 = 0
    <x2,K(E2,E1)x1>_W = 0.

It must also obey both accepted source-conditional spectral windows. If one can prove that **no** x1,x2 and physical source matrices inside the authenticated enclosures satisfy both equations, the first Wilson weight is strictly positive. This is an exclusion certificate, rather than an attempt to synthesize a desired measurement.

## Exact original-source pilot

Two original sources are used together, without assuming they are exact full-Q truth:

1. Original source-authenticated PR #282 centered physical 64 signed 8x8 Wilson entries, Feshbach O2 integer on W-flat metric, at both accepted E1/E2 energy brackets. All shell4 residual effects were included in its rigorous entrywise intervals. This pilot uses its CENTRAL signed matrix, not the entire interval box. Frozen original hosted Git blob pin.
2. Original signed Stage E four-moment true Schur lower/upper 8x8 Loewner matrices from PR #234, including the actual independently recorded physical energy windows, μ3 source and Q-floor. The source center is Sstar=(L+H)/2 at historical sample E2 parameter z2. Its exact symmetric interval radius is bounded by the weighted trace of the half-width plus the full accepted true-energy drift bound from BdaggerB=72I.

Fix historic original flat E1 direction v1. Let sstar=Kstar v1 be the source's **centered** Wilson action in weighted W-flat coordinates, where the source's signed bilinear matrix A and metric W satisfy sstar proportional to W^-1 A v1. For historic E2 direction v2, let n=<sstar,sstar>_W and a=<v2,sstar>_W. The exact closest direction on the hyperplane with **zero source Wilson transition** is

    v_dark = n v2 - a sstar.

This is the weighted-orthogonal projection of v2 onto sstar-perp, with irrelevant rational scale cleared. A source dark state is thus *constructed*, not assumed to be physically possible.

The first **outside-in** scan walks the 9 rational vectors

    v(k) = 8 n v2 - k a sstar,   k=8,7,...,0.

At k=8 the source Wilson bilinear is EXACTLY ZERO by integer cancellation. At k=0 this is the original historic v2. The second **center-pulse** scan moves the dark endpoint toward the *independently source-recentered* Stage E E2 Schur witness vc:

    v_pulse(p) = (8-p) v_dark + p n vc,   p=0,1,...,8.

For every point, the verifier measures exact integer/outward rational W-flat rotation from historic v2, original centered source Wilson amplitude (per 1e12), Schur-center residual lower and upper, the E2 physical energy-drift/Loewner-source uncertainty ceiling, and whether that **specific vector** could be an actual Schur-null direction within the accepted source uncertainty. The two scans are the user's "from the outsides in" and "pulse from the center" rendered as mathematical paths; no floating-point optimization or fabricated physics is used.

## Acceptance boundaries

At any fixed candidate unit direction v, the accepted Schur source L<=Strue(z2)<=H and the true E2 energy-window drift imply

    ||Sstar v||_W <= eps_total

is **necessary** for v to be the exact null vector of a true physical S(E2). If the computed Schur-center residual lower bound strictly exceeds eps_total, the candidate can be excluded as a physical eigenvector. This is a valid single-vector mathematical exclusion.

However Kstar is only the central source approximation, while the true K(E2,E1) differs within the full-Q matrix intervals, and x1 differs from the historic v1 within its accepted E1 source cone. **Excluding the exact Kstar-dark endpoint does not exclude every potentially dark Ktrue/E1 configuration**. A successful true original Wilson positivity theorem needs a robust constrained *all-source* dark-exclusion inequality over all allowed matrices and true eigendirections, or a signed-positive true projector trace. Until that robust step passes, the calculation is an exploratory inverse diagnostic and first Wilson spectral weight stays HOLD.

A later **robust** source test would minimize ||Sstar x2||_W over the family

    <x2,(Kstar+delta_K)(v1+delta_x1)>_W=0

under exact accepted interval bounds delta_K, delta_x1, and certify the minimum exceeds eps_total. That is a finite 8D semialgebraic/exact rational inequality, not a massive new Hamiltonian basis calculation.

All original hashes and exact integer/no-float gates are checked by the hosted CI source. The finite 3x4 S3 physical gap remains source-conditionally certified, issue #137 true original Wilson weight HOLD, continuum 4D theorem OPEN.
