# Outside benchmark: one open D3 plaquette against a published matrix

Seat ACER-CLAUDE-FABLE52, 2026-11-15, at the operator's direction. Prediction and program pushed in `fbabe91` before the run.

This repository's S3 rule (three transposition moves per link; magnetic `r(2 - chi)`) is applied by brute force to all 1,296 link states of one open plaquette and reduced to the three gauge orbits (216, 432, 648 states). The result is compared with the D3 one-plaquette Hamiltonian matrix (3.3.27) and tables 3.11 and 3.12 of the Bologna thesis *Quantum simulation of non-Abelian gauge theories* (amslaurea.unibo.it/id/eprint/29471), with `lE = 1`, `lB = r/2` and the constant `2r`.

| Check | Result |
|---|---|
| characteristic polynomial equals the thesis matrix, r = 9 | equal: x^3 - 81x^2 + 1854x - 11016 |
| the same, r = 12 | equal: x^3 - 96x^2 + 2592x - 17280 |
| electric limit levels | 0, 12, 24 (thesis table 3.11) |
| magnetic limit levels, thesis units | -4, 0, 2 (thesis table 3.12) |

One-plaquette levels at r = 9: 9.259170151, 26.024237127, 45.716592721 (floors); gap 16.765066976. At r = 12: 9.958962160, 32.266706190, 53.774331649; gap 22.307744030.

Run 1 stopped at the electric-limit check with an instrument fault: the grid root finder counted each exact integer root twice. That row is kept as `RESULT-BENCH-RUN1-INSTRUMENT-FAULT.hbp`; the check now tests the integer roots exactly. The polynomial comparison passed in both runs.

Scope: one open plaquette. It tests the rule and its convention against an outside source. It says nothing about the 3x4 torus numbers; no published value for that system was found in the search of 2026-11-15.
