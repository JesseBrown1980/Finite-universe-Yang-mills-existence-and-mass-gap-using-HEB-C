# zconf, cloud seat: the S3 confining phase, static-charge potential and string tension.
Pre-registration, frozen before any code.

Model (as in every HEB-C certificate): H/J_E = E + r M, E = sum over links sum over transpositions t of
(1 - L_t), M = sum over plaquettes (2 - chi_std(U_p)). Static charges: the 2-dimensional irrep (std) at one
site and its conjugate at another, d links apart along a straight line. V(d, r) = E_charged - E_vacuum.
Rust 1.81, std only, exact integer and rational arithmetic, json=0.

## Method
Strong-coupling perturbation theory in r (the confining side, r -> 0).
- Electric eigenvalue of a link in irrep R: 3 - (sum over t of chi_R(t)) / dim R.
- At r = 0 the charged ground state is a string of std links along the path (Gauss law forces a
  nontrivial irrep on every path link; std is the cheapest that fuses std x std -> trivial at interior
  vertices).
- First order: <chi(U_p)> = 0 in both vacuum and string states (every plaquette has a link outside the
  string carried over the whole group), so V has no O(r) term.
- Second order: each plaquette contributes s_p = - sum over excited irrep assignments of its 4 links of
  |P_R (chi_p psi0)|^2 / (|psi0|^2 (E_R - E_0)). Plaquettes without a string link contribute the vacuum
  value s_vac; on a straight string every string link lies in exactly two plaquettes, each containing
  exactly one string link (value s_str). So V(d, r) = 3d + kappa d r^2 + O(r^3), kappa = 2 (s_str - s_vac).

## Predictions
- F1 link spectrum: trivial 0, sign 6, std 3 (exact).
- F2 V(d, 0) = 3 d exactly for d = 1..6 (minimal Gauss-law string, from F1).
- F3 kappa is an exact rational, negative (the string tension falls as the magnetic coupling grows), and
  the same for every d (each string link contributes the same two plaquettes).
- F4 independent arithmetic: s_vac and s_str computed (A) from characters and the group table and (B) from
  explicit integer permutation matrices projected on the std subspace (I - J/3) are identical rationals.
- F5 measured, not predicted: sigma(r) = 3 + kappa r^2 at r = 1/27, 1/9, 1/3, 1 (exact rationals), and the
  coupling where this second-order string tension would reach 0.
Scope: perturbative to O(r^2); finite-r certificates, Wilson loops and volume scaling are later packages.
Any build failure or missing row is INCONCLUSIVE.
