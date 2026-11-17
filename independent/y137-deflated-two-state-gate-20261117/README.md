# Issue 137: exact two-state / deflated Wilson inequality (Rust 1.81)

Research draft, November 17 2026. This is a source-independent **conditional theorem checker**, not a physical first-Wilson-weight certificate. It uses the existing locked num-bigint and num-integer dependencies of sturmrs. Even if candidate fractions make the algebraic gate PASS, output always states source_authenticated=NO and actual_Wilson_weight=HOLD.

## Complete theorem, including missing cross terms

For normalized exact physical psi1 and psi2, and W-orthonormal trial u1,u2, let Q denote projection onto the trial pair. Write

    psi1 = a*u1 + b*u2 + xi1
    psi2 = c*u1 + d*u2 + xi2

where xi1 and xi2 are orthogonal to both trial vectors. Independent source certificates must provide

    m1 >= |b|, m2 >= |c|
    eps1 >= ||xi1||, eps2 >= ||xi2||
    w11 >= |<u1,O u1>|, w22 >= |<u2,O u2>|
    w12 >= |<u1,O u2>|, w21lower <= |<u2,O u1>|
    z1,z2 >= ||(I-Q) O u1||, ||(I-Q) O u2||
    zstar1,zstar2 >= ||(I-Q) O* u1||, ||(I-Q) O* u2||
    M >= ||O||.

Set c1sq = 1-m1^2-eps1^2, c2sq = 1-m2^2-eps2^2. Both must be strictly positive. Define

    C = m2*w11 + m1*w22 + m1*m2*w12
      + eps2*(z1 + m1*z2)
      + eps1*(zstar2 + m2*zstar1)
      + M*eps1*eps2.

By exact orthogonal expansion and triangle/Cauchy-Schwarz,

    |<psi2,O psi1>| >= sqrt(c1sq*c2sq)*w21lower - C.

Therefore the STRICT rational polynomial inequality

    c1sq*c2sq*w21lower^2 > C^2

is sufficient for a positive exact E1-to-E2 Wilson transition, provided that each of the thirteen input bounds has separately been certified for the same original physical vectors and observable. The full formula retains both off-diagonal mixing-times-deflated-Wilson cross terms. There is no assumption that trial vectors occupy different exact symmetry sectors.

The executable checks the exact inequality with reduced positive-denominator BigInts. It rejects any missing, duplicate, negative, inexact, extra or denominator-zero field; it also checks all positive magnitude bounds are compatible with the Wilson norm ceiling. Only the algebra is proved by source-independent test data.

## Correct spectral scale and proof obligations

The accepted physical intervals are

    E1/J_E in (69.909429421,69.909586556)
    E2/J_E in (69.949264147,69.949433884)
    E3/J_E > 69.968699300.

Thus the guaranteed E3-to-E2 separation is 0.019265416 J_E, **not** larger than the 0.039677591 J_E first gap. For genuine Ritz u_i with Rayleigh mu_i, original full-H residual rho_i, and mu_i < E3_lower, high-sector leakage of each **trial** obeys ||(I-P12)u_i|| <= rho_i/(E3_lower-mu_i). This is not directly the source field eps_i = ||(I-Q)psi_i||. The two-subspace principal-angle identity can translate the combined two trial high leakages into a uniform upper bound on the exact low-state trial-complement leakage; source-specific enclosures and strict positive denominators are mandatory.

For an exact orthonormal Ritz pair, <u1,u2>=<u1,H u2>=0. With eta_i=(I-P12)u_i, these equations imply

    (E1-E2)*<u1,psi1>*<psi1,u2>
       = -<eta1,(H-E2)eta2>.

This can yield a **conditional second-order mixing bound**, but only once high-sector residual norms and a positive lower first-state fidelity are certified. No automatic second-order assertion follows from Ritz orthogonality alone. The accepted Stage M four-vector full physical residual ceilings, approximately 0.4161 and 0.4072 J_E, are currently too large for useful division by the E3 separation; they do not imply any positive Wilson theorem.

Similarly, source-defined corrections of O u_i by (H-E_j)q are exactly orthogonal to the true psi_j, but their **Q-projected** components must be recomputed; replacing deflated norms with corrected versions without adjusting the low-space Wilson matrix is invalid. This first verifier uses q=0 until independent source-backed q identities are available.

## Reproducibility and hold policy

    cd native/ym
    cargo test --offline --locked --package sturmrs --bin y137_deflated_wilson_gate
    cargo run --offline --locked --package sturmrs --bin y137_deflated_wilson_gate -- toy
    cargo run --offline --locked --package sturmrs --bin y137_deflated_wilson_gate -- verify exact.txt

A supplied exact.txt must have exactly the 13 keys listed in the Rust source, in key=numerator/denominator format. Even a conditional arithmetic PASS is not a source-authenticated numerical result. A direct signed spectral-moment route is also possible: for exact normalized ground psi1 and E2<L3<=E3, define A=<O psi1,(L3-H)O psi1>-(L3-E1)*|<psi1,O psi1>|^2. Then A>0 implies positive first-Wilson weight. Its true-ground lower bound remains uncomputed. Both routes keep Issue 137 OPEN and the original Wilson weight HOLD, independent of the already certified conditional finite-model energy gap. The 4D continuum theorem is OPEN.
