# zconfcert, cloud seat: certified finite-coupling energies of the S3 static-charge sector.
Pre-registration, frozen before the charged-sector builder or any count is run.

Model (unchanged): H/J_E = E + r M, E = sum over links sum over transpositions t of (1 - L_t), M = sum over
plaquettes (2 - chi_std(U_p)). Static charges: std at site a, its conjugate at site b.
V(d, r) = E_charged(d, r) - E_vac(r) on the same lattice. Rust 1.81, std + the workspace's existing crates,
integer arithmetic only, json=0. Every count runs as a job of the HTTP-0 backend (hebc_ym_http0 serve),
which stores run.hbp / index.hbi / run.anchor shards; the driver talks to it over HTTP/1.1.

## Geometries (open boundaries, so no periodic image of the pair exists)
- L2: ladder, 2 rows x 4 columns, 3 plaquettes. Charges on row 0 at x = 0 and x = d, d = 1, 2, 3.
  Each string link lies in exactly 1 plaquette.
- L3: strip, 3 rows x 3 columns, 4 plaquettes. Charges on row 1 at x = 0 and x = d, d = 1, 2.
  Each string link lies in exactly 2 plaquettes.

## Construction
- Gauge-invariant states: comb spanning tree, free links, orbit representatives under global
  conjugation, Gauss weights (as torusl / zgap2). Electric matrix from link moves L_t, magnetic diagonal.
- Charged sector: add one auxiliary link l from b to a. It carries no electric and no magnetic term.
  Gauge-invariant states of the augmented graph with l in irrep R are exactly the sector with static charge R
  at one end and its conjugate at the other, each once. The R = std sector is selected exactly by adding the
  penalty 10 (E_l - 3)^2 (eigenvalue 0 on std, 90 on trivial and sign), which commutes with H.
- Matrices are written in the existing exchange format (weights, magnetic diagonal, electric triples) and
  checked exactly W-self-adjoint by the builder.
- Counts: sturmrs (interval Sturm inertia, outward rounding) on B = W(1000 (JE Z + JB M) - T W) with
  JE = 270000000 and JB = 0, 10^7, 3*10^7, 9*10^7, 27*10^7 (r = 0, 1/27, 1/9, 1/3, 1). Energy in J_E units
  = T / (1000 JE). negative(T) = 0 certifies E0 > T; negative(T) >= 1 certifies E0 < T.
- Bracketing: start at the second-order prediction (first-order 2 r N_p, second-order N_p s_vac r^2 plus,
  for the charged sector, 3 d + n_g d (s_str - s_vac) r^2, s_vac = -1/12, s_str = -17/144) plus or minus
  m = max(10 |second-order term|, 10^-6); double m until the bracket is certified (at most 20 times), then
  bisect to width <= 270 (10^-9 J_E). V intervals by outward interval subtraction.

## Predictions
- Q1 builder: every matrix is exactly W-self-adjoint; at r = 0 the vacuum ground energy is 0 and the charged
  ground energy is 3 d, each certified by counts at T = 1000 JE E0 -/+ 1.
- Q2 certificates: every E_vac(r) and E_charged(d, r) at r = 1/27, 1/9, 1/3, 1 enclosed with width
  <= 10^-9 J_E; V(d, r) intervals recorded.
- Q3 second order: at r = 1/27, kappa_eff(d) = (V - 3 d) / (d r^2) lies within 15% of
  kappa_g = n_g (s_str - s_vac): -5/144 on L2, -5/72 on L3, for every d.
- Q4 convergence: |kappa_eff(1/27) - kappa_g| < |kappa_eff(1/9) - kappa_g| for every geometry and d.
- Q5 local mechanism: kappa_eff(L3, d=1) / kappa_eff(L2, d=1) at r = 1/27 lies in [1.7, 2.3]
  (two plaquettes per string link against one).
- Q6 confinement: sigma(d, r) = V(d+1, r) - V(d, r) certified > 0 for every measured d and r.
- Q7 HTTP-0 replay of #56: the sealed zconf calculation, run as an HTTP-0 job from a byte-identical copy of
  its source, gives a run.hbp byte-identical to the sealed RESULT.hbp (sha256 bb9ca0f4...dc64), and the
  backend's verify re-execution passes.
Measured, not predicted: sigma(d, r) values, kappa_eff at r = 1/9, 1/3, 1.
Fail-closed: a missing shard, failed verify, uncertain Sturm count, uncertified bracket or exceeded budget
makes the affected prediction INCONCLUSIVE.
