# Addendum 1 (sealed after run 1, before run 2)

Run 1 (`RESULT.run1.hbp`, kept): K1 PASS, K3 PASS, K2 FAIL (T_half 26 and 82, ratio 3.15), sound
INCONCLUSIVE. The sound start put the density step only in the rest channel, whose particles do not
stream, so the step barely propagated (first crossing at tick 75 for Lx = 24, none for Lx >= 48).

Run 2 adds, without changing run 1's measures or rows:
- nu2 from the later decay window, where the square wave's faster harmonics are gone:
  T_q = first tick with 4 A(t) <= A(0); nu2 = ln2 * Ly^2 / (4 pi^2 (T_q - T_half)), integer-bounded.
  Prediction V2: the two nu2 intervals (Ly = 24 and 48) differ by less than 15% of the larger.
- Sound2: start every channel at 1, then raise both face channels along x (indices 22 and 4) to 2 for
  x < Lx/2 and lower both to 0 otherwise: a density step of +-2 with zero momentum, in moving channels.
  c2 = 2 Lx / (t_5 - t_1) from D(t) crossings as before, Lx in {24, 36, 48, 60, 72}, run 8 Lx ticks.
  Prediction S2: c2 at every Lx lies in [1/2, 3/2]; measured values reported against sqrt(2/3) and 0.8937.
