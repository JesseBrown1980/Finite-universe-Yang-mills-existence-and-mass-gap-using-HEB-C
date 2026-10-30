# zwilson, cloud seat: certified spatial Wilson loops of the S3 vacuum on the open ladder.
Pre-registration, frozen before the Wilson-loop builder, the series solver or any count is run.

Model (unchanged): H/J_E = E + r M on the L2 open ladder (2 rows x 4 columns, plaquettes p0, p1, p2), the
same geometry and vacuum sector as zconfcert. Observable: W(C) = chi_std(U_C), unnormalised (the
dimension-normalised loop is W/2; both are reported). Loops C_A = 1 x A rectangles on columns 0..A,
A = 1, 2, 3. Couplings r = 1/27, 1/9, 1/3, 1. Rust 1.81, integer arithmetic only, json=0, every
computation an HTTP-0 job.

## Exact strong-coupling series
<W(C_A)> = sum_k c_{A,k} r^k is computed to order k = A + 1 by Rayleigh-Schrodinger perturbation theory in
H0 = E, V = M, including every <psi_j|W|psi_{k-j}> term and the normalisation, with exact rationals:
- method A: gauge-orbit basis under global conjugation with Gauss weights (the zconfcert construction);
- method B: the full gauge-fixed configuration basis (6^3 states, unit weights, no orbit reduction).
Reduced resolvent by exact fraction-free elimination; std-only big integers.

## Certified finite-coupling values
Concavity of the ground energy in lambda gives, for H_lambda = H + lambda W,
  (E0(lambda) - E0(0)) / lambda <= <W> <= (E0(0) - E0(-lambda)) / lambda,
valid for a degenerate ground state as well. With certified brackets L, U of each energy:
  (L_+ - U_0) / lambda <= <W> <= (U_0 - L_-) / lambda.
Counts: sturmrs on W(1000 (JE E + JB M + LAM W) - T W) (the builder writes JB M + LAM W as the diagonal,
sturmrs is called with JB = 1), JE = 270000000000000, JB = r JE, lambda = 10^-8 (LAM = 2700000).
E0(0): bracket from the second-order prediction, doubling as in zconfcert, bisected to width <= 1 T unit
(3.7 * 10^-18 J_E). E0(+-lambda): bracket [E0(0) bracket -/+ 2 lambda] (|W| <= 2), bisected to width <= 1.
Final bracket counts re-executed by the backend's verify.

## Predictions
- W1 series: methods A and B give identical c_{A,k} for k <= A + 1; c_{A,k} = 0 for k < A; c_{A,A} > 0;
  c_{1,1} = 1/6.
- W2 certificates: every <W(C_A)> at every r enclosed with width <= 4 * 10^-9 and lower end > 0.
- W3 leading order: at r = 1/27, <W(C_A)> lies within [0.8, 1.25] x c_{A,A} r^A for A = 1, 2, 3.
- W4 convergence: |<W>/(c_{A,A} r^A) - 1| is smaller at r = 1/27 than at r = 1/9, every A.
- W5 area law: <W(C_{A+1})> < <W(C_A)> certified at every r; at r = 1/27 the ratio
  <W(C_{A+1})>/<W(C_A)> lies within [0.8, 1.25] x (c_{A+1,A+1} / c_{A,A}) r.
Measured, not predicted: the values at r = 1/3 and 1, the two-term series comparison.
Fail-closed: a failed series job, missing shard, failed verify, uncertain count or uncertified bracket
makes the affected prediction INCONCLUSIVE.
