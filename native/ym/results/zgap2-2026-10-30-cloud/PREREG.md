# zgap2, cloud seat: the second-order gap coefficient c and the 3x4 prediction.
Pre-registration, frozen before any code.

Model (as in The-matrix-law-essentials and HEB-C): S3 gauge theory on the Lx x Ly torus,
gauge-invariant orbits under global conjugation with Gauss weights, H/J_E = E + r M,
E = sum over links sum over transpositions t of (1 - L_t), M = sum over plaquettes (2 - chi_std).
Delta_L(r) = E9 - E8 in the certificates' zero-momentum space; c_hat_L(r) = r (3r - Delta_L(r)/J_E).

Rust 1.81, std only, exact integer and rational arithmetic, characteristic polynomials and Sturm
isolation (or exact inertia counts) for every algebraic number, json=0.

## Method (P2)
Perturbation theory in 1/r about M:
- Vacuum (M = 0, the 8 flat orbits): first order P0 E P0; second order H0 = - P0 E Q0 M^-1 Q0 E P0.
- Lowest excited level (M = 3: one plaquette carrying a 3-cycle, all others flat): first order
  P3 E P3; second order H3 = P3 E Q3 (3 - M)^-1 Q3 E P3, restricted to translation-invariant
  (zero-momentum) combinations, over the lowest first-order eigenspace.
- Delta_L / J_E = 3r + d1 + c2 / r + ..., with d1 = (lowest first-order M=3 eigenvalue) - (top
  first-order vacuum eigenvalue) and c_L(inf) = -(c2) = (top eigenvalue of H0 over the vacua) -
  (lowest eigenvalue of H3), when d1 = 0.

## Predictions
- P0 d1 = 0 on every lattice computed (the certificates show no constant offset).
- P1 (frozen until a 3x4 full-space E9 - E8 certificate at r = 243 exists; not run here):
  21.095802 <= c_hat_3x4(243) <= 21.573297.
- P2 c_3x3(inf) lies in [21.095802, 21.573297], the certified r = 243 interval for 3x3.
- P2b consistency: c_L(inf) for 2x2, 2x3 and 2x4 lies in each lattice's certified r = 243 interval
  ([36.766, 37.109], [34.500, 34.869], [36.481, 36.787], from the README point certificates,
  outward-rounded in micro-units).
- P3 locality: c_3x4(inf) = c_3x3(inf) exactly (and c_4x4(inf), if computable here), while the
  2xL values differ from c_3x3(inf).
- P4 independent arithmetic: the vacuum second-order operator H0 reproduces the published exact
  laws of flat_law.py (vacua split at second order on 2xL with the published coefficients, and H0 is
  exactly scalar on 3x3).
Any build failure or missing row is INCONCLUSIVE. P1 stays PENDING in this package.
