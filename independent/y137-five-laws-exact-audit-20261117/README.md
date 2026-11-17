# Issue #137 — exact audit of five proposed mathematical laws

2026-11-17 research draft. This is an independent **zero-float, fail-closed rational falsification suite**. It deliberately separates algebraic identities from numerical source certification and from conjectural extrapolations. Original finite 3×4 S₃ gap conditionally certified. Actual first-excitation original seven-loop Wilson spectral weight HOLD, 4D continuum OPEN.

## 1. Padé hypothesis for the 3×3 high-cluster gap

The registered one-pole continuation is

    c2_Pade(r)=43/(1-43/(21r)),
    gap(r)=3r-21/r-c2_Pade(r)/r².

No new fitted parameter is introduced, but a rational continuation is **not** a proof that the full original Feshbach self-energy has this pole. Against the frozen PR #268 3×3 source intervals the one-pole formula is **excluded** at *both* r=9 and r=27 and compatible at r=81,243. The exact r=9 prediction is 23.9794520547945 J_E, while the frozen interval is (23.938578,23.939630) J_E. At r=27 the prediction is 80.1583969465649 J_E, below the certified (80.161963,80.163325) interval. The proposed second two-pole formula has no explicit complete expression in the current request, so the checker labels it UNVERIFIABLE instead of inventing a rational approximant. The proposed r=9 interval lower bound 23.938519 differs from the frozen source's 23.938578; original source remains authoritative.

## 2. Exact rational Chebyshev envelope

The accepted original 3×4 *full nonflat* interval at the true E2 upper endpoint has

    gQ=94.0682, bQ=468, E2hi=69.949433884,
    kappa=(bQ-E2hi)/(gQ-E2hi).

The standard minimax inverse-residual contraction is

    rho=(sqrt(kappa)-1)/(sqrt(kappa)+1).

It obeys the **exact rational upper bound**

    rho<49/81  iff  kappa<(65/16)^2=4225/256,

proved using only positive-denominator integer cross-multiplication. The degree test 2*(49/81)^m<epsilon reproduces the accepted PR #268 theoretical inverse-residual degree table exactly at m=11,13,15,20. This is an accurate and useful exact integer envelope.

The suggested identity rho=(bQ-gQ)/(bQ+gQ-2E) is **not** the minimax Chebyshev factor; it is the conventional optimally damped Richardson factor. The unshifted E=0 Richardson factor is approximately 0.665278, not 49/81 ≈0.604938. The number 49/81 is a convenient rational upper envelope, **not yet an established 3-adic structural law**. Note E2/J_E≈69.949, rather than an energy of 0.04: 0.04 is approximately the FIRST GAP E2−E1 in these units.

## 3. Original seven-loop Wilson centering and two-energy orthogonality

For the original weighted physical 3×4 coordinate P projector, O is diagonal multiplication and POQ=QOP=0. With exact true eigenstates

    psi_i=x_i ⊕ [-R_i B x_i],  R_i=(QHQ-E_i)^(-1),

the exact true-state orthogonality identity for E1≠E2 is

    <x2,x1>_W + <R2 Bx2,R1 Bx1>_W=0.

Consequently replacing O by O−mu*I changes the true E1→E2 amplitude by **zero** for any rational mu. On finite nonorthogonal numerical trial vectors, the exact shift correction is **−mu * <trial2,trial1>_W**; discarding this term is invalid.

Because the original seven-loop faithful-character integer value obeys −7≤O(x)≤14 on every gauge orbit, choosing the conservative *global* midpoint mu=7/2 gives

    ||Q (O−7/2 I) Q|| <=21/2=10.5,

a **25% reduction** from the source-unshifted global upper bound 14, independent of incomplete finite K3 sample extrema. This reduces the **operator-norm factors** in a source residual bound but does NOT alone prove a 25% reduction of the actual total signed Wilson transfer error or the current true-eigenstate angle penalty. If more precise full-Q extrema are independently proved, a different rational center may improve this guarantee.

## 4. Full physical bilinear residual transfer

Let the original signed full-Q nonflat leg of two source states be u_i and its numerical approximation v_i, let delta_i=(QHQ−Ei)v_i+B x_i (with the sign convention u_i=−R_i Bx_i), and let g_i be the source-certified positive spectral distance from Ei to the *entire* Q spectrum. Then e_i=u_i−v_i=−R_i delta_i and ||e_i||<=||delta_i||/g_i. For A=Q(O−mu I)Q,

    |<u2,A u1>−<v2,A v1>|
      <= (||delta2||/g2)*||A v1||
         + (||delta1||/g1)*||A* v2||
         + ||A||*(||delta1||/g1)*(||delta2||/g2).

The two **directional** norms are computable exactly from original integer multiplication O and the actual source vectors; their exact full-Q uncertainty still requires the complete exterior shell4 residual. This is an algebraic Cauchy-Schwarz theorem (independent toy exact-tested), not a new original-source residual receipt. Using only the 155,378 interior K3 residual coordinates would silently drop essential exterior error.

## 5. Square-root-free strict rational weight acceptance

For real original S3 transitions with an independently certified signed exact numerator interval [Nlo,Nhi] and strictly positive **squared** physical norm upper bounds D1plus,D2plus, require:

    (Nlo>0 OR Nhi<0)        # strict zero exclusion

Set N_abs_lower=Nlo when Nlo>0, otherwise N_abs_lower=−Nhi. For rational target p/q≥0 with q>0 require the exact integer cross-multiplied test

    q * N_abs_lower² > p * D1plus * D2plus.

All four quantities are exact rational pairs; clear all positive denominators to implement with integer multiplication and integer comparisons. The executable rejects zero-containing numerator intervals and strict equality, and accepts an independent positive rational toy.

A target p/q=1/1000 may be used for candidate quantitative results but is **not necessary to establish positivity**. For mere positive original spectral weight, strict Nlo>0 or Nhi<0 and finite positive physical norms suffice.

## Parallel work and limits

The two ongoing source lanes remain separate: PR #279 exact full physical E2-only versus BOTH spectral bracket scans and PR #276's source-specific original Wilson directional Q-dual, joined to Stage E true W-flat angles in #278. This five-law exact audit **neither alters the original immutable 80 atlas records and its 13-row receipt nor asserts the 3×3 high-cluster model is the first-excitation 3×4 Wilson transition**. It contributes a verified rational inverse contraction envelope, a structural centering improvement and an exact bilinear/error acceptance formula that can be attached to future source-specific signed proofs.

Do not promote any proposed two-pole fit or a numerically positive fixed-sample Wilson signal to a true first-excitation Wilson theorem absent its actual source-conditioned projector transfer and independently reviewed strict signed margin.

Run:

    python3 -I -B independent/y137-five-laws-exact-audit-20261117/audit.py
