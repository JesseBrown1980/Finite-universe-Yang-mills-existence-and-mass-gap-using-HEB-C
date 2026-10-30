# Addendum 1 (sealed after run 1, before run 2)

Run 1 (`RESULT.run1.hbp`, kept) did not implement the registered definitions in two places:
1. The vacuum operator was built with denominators (0 - M_j), so it already is the energy-shift
   operator H0 = -P0 E Q0 M^-1 Q0 E P0 (the negative of flat_law's kappa matrix). The code then
   formed c = -(lambda_min(H3) + min eig(H0)). The registered definition is
   c_L(inf) = (top eigenvalue of H0) - (lowest eigenvalue of H3).
2. The P4 law check compared the top two vacuum levels. The published flat_law coefficient is
   the splitting of the two lowest levels (kappa_0 - kappa_1 with kappa descending).
Run 2 changes only these two expressions. Every prediction (P0, P1, P2, P2b, P3, P4) and every
interval stays exactly as frozen in PREREG.md (a1ab70c4…), and run 2 decides them.
Run 1 printed min eig(H0) and lambda_min(H3); for 3x3, 3x4 and 4x4, where H0 is scalar, those
lines already fix the run-2 values, so this addendum is sealed with that in view.
