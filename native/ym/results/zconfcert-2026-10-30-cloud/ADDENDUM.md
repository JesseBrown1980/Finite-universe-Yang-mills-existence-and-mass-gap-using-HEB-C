# zconfcert addendum 1 (sealed before any certificate count is run)

## Change: L3 geometry
PREREG.md fixed L3 = 3 rows x 3 columns with d = 1, 2. The builder gives 1393 orbit states for each charged
L3 matrix (251 for the L2 charged matrices). Measured sturmrs cost of one count: 0.57 s on a 251-state
matrix, 243 s on a 1393-state matrix. Each energy needs about 25 to 35 counts, so the 3x3 cells need about
13 hours of counting and cannot be replayed on the exact head by the cloud-replay workflow.

L3 becomes the 3 rows x 2 columns strip (2 plaquettes), charges on row 1 at x = 0 and x = 1, d = 1 only.
The string link lies in exactly 2 plaquettes, so kappa_g(L3) = -5/72 is unchanged and Q5 (the L3/L2 ratio at
d = 1) is tested as registered. On L3, Q3 and Q4 are tested at d = 1 only and Q6 has no L3 cell. The 3x3
strip cells (d = 1, 2) move to the volume-scaling package, which needs a reduced (symmetry-sector) lane.
L2, every prediction's threshold, JE/JB, the bracketing and the width are unchanged.

## Disclosure: timing probes run before this addendum
Three sturmrs counts were run only to measure cost:
- L2 charged d = 3, JB = 10^7, T = 3*10^12 (E = 11.11 J_E): negative = 1.
- L3 (3x3) vacuum, JB = 10^7, T = 1 (E = 3.7*10^-12 J_E): negative = 0.
- L3 (3x3) charged d = 2, JB = 10^7, T = 1: run time 243 s.
None of these thresholds is within the second-order window of any registered prediction, so they carry no
information about Q3 to Q6.
