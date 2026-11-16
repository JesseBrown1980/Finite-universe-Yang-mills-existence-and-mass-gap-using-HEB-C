# Outside benchmark: two open D3 plaquettes against the published 11x11 matrices

Seat ACER-CLAUDE-FABLE52, 2026-11-15, at the operator's direction ("Do its largest plaquette"). Prediction and program pushed in `1a6b8ad` before the run. Two of four predictions met; the frozen verdict row reads mismatch and is kept (`RESULT-BENCH2.hbp`).

The largest system in the Bologna thesis (amslaurea.unibo.it/id/eprint/29471) is two open plaquettes sharing a link. This repository's rule is applied by brute force to all 279,936 link states and reduced to the eleven gauge orbits.

## Frozen run

| Check | Result |
|---|---|
| Q1 eleven gauge orbits | met |
| Q2 electric characteristic polynomial equals printed `H_1E` | **missed** |
| Q3 magnetic levels -8, -4, -4, -2, -2, 0, 0, 2, 2, 4, 4 | met (brute force equals the thesis text; the printed `H_B` gives them once entry (8,5) is set to 2; as printed it has (5,8) = 2 and (8,5) = 0) |
| Q4 full polynomial equals the thesis matrix in the symmetrised reading | **missed** |

## What the difference is

Brute-force electric levels: 0, 12, 18, 21, 24, 30, 36, all integers. The printed block `[[18,0,e],[0,24,-e],[e,-e,21]]` with `e = 3 sqrt(2)/2` has levels 21 and 21 +- 3 sqrt(2). The seven link electric terms commute and each has levels 0, 3, 6, so every electric level of the model is an integer; the printed off-diagonal entries are inconsistent with that.

## After the run (exploratory, `explore_block.py`, `RESULT-EXPLORE.hbp`)

With the printed diagonal kept (18, 24, 21 on the last three basis states), the two off-diagonal electric entries removed, and `H_B` entry (8,5) set to 2, the full characteristic polynomial of the thesis matrix equals the brute-force one exactly at r = 9 and at r = 12. The same holds with 18 and 24 exchanged; the other four placements fail.

## Reading

The rule of this repository agrees with the published two-plaquette D3 Hamiltonian at both couplings once two printed entries are corrected: `H_B`(8,5) and the off-diagonal electric pair. Both corrections were found after the frozen run, so that agreement is an exploratory result. The thesis author has not been asked.

Scope: two open plaquettes. Nothing here bears on the 3x4 torus numbers.
