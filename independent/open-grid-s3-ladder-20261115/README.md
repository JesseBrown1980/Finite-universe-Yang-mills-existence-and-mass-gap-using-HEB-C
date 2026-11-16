# Open grids of S3 plaquettes: how the first gap moves with size and coupling

Seat ACER-CLAUDE-FABLE52, 2026-11-15, at the operator's direction. Every prediction file was pushed before its run. Missed predictions are listed with the met ones.

## What is measured

The S3 Kogut-Susskind rule of this repository on an open a x b grid of plaquettes, H = (electric) + r (magnetic). The gauge-invariant space of P plaquettes is one group element per loop up to one global conjugation: (6^P + 2*3^P + 3*2^P)/6 states (3, 11, 49, 251, 1,393, 8,051, 47,449, 282,251, 1,686,433, 10,097,891 for P = 1 to 10). The gap is E1 - E0, the two lowest levels.

Scope: open-boundary grids. The 3x4 torus of the main result is a different system. A statement about the gap of an infinite grid is outside what these finite runs show; see "Reading".

## Methods, in the order they were built

| Program | What it certifies | Reach |
|---|---|---|
| `open_grid.py` | both levels, exact integer inertia counts | about 50 states |
| `rust/src/main.rs`, default mode | both levels, two-sided: approximate fixed-point LDL^T with diagonal pivoting, then a rigorous entry-by-entry bound of the residual; `#levels below x - eps <= neg(D) <= #levels below x + eps` | 8,051 states (dense) |
| same, `sparse` | E0 two-sided (Collatz-Wielandt on a positive integer vector), E1 from above (exact Ritz problem of two integer vectors, 256-bit products). **E1 from below is NOT_CERTIFIED**, so the gap has a certified upper end and an estimate | 282,251 states |
| same, `cheb` | the same two certificates; matrix held as one u32 column per move, threads, vectors by Chebyshev-filtered subspace iteration (4x2 in 31 s against 758 s) | 10,097,891 states (10 plaquettes) |

Rust 1.81, `cargo clippy --release -- -D warnings` exit 0, integers only. An earlier interval-elimination method is kept in the record (`RESULT-CENTRE-RUN1-PARTIAL.hbp`, `RESULT-CENTRE-RUN2-PARTIAL-NO-PIVOT.hbp`, `RUN-6x1.txt`): it stops when a pivot interval contains zero, which happens at small coupling and on 6x1 at r = 9.

Twelve plaquettes (6x2, 4x3) need about 140 GB of columns and are out of reach of these programs.

## Gaps at r = 9 (`RESULT-GRID-RUST.hbp`, `RESULT-SPARSE.hbp`)

| Grid | States | Gap |
|---|---|---|
| 1x1 | 3 | 16.765065 .. 16.765069 |
| 2x1 | 11 | 15.701569 .. 15.701573 |
| 3x1 | 49 | 15.327304 .. 15.327308 |
| 4x1 | 251 | 15.151157 .. 15.151197 |
| 5x1 | 1,393 | 15.052328 .. 15.052368 |
| 6x1 | 8,051 | estimate 14.9908 (interval method ended NOT_CERTIFIED; a certified run is in the hosted cells) |
| 7x1 | 47,449 | upper end 14.9556 |
| 2x2 | 251 | 14.801616 .. 14.801620 |
| 3x2 | 8,051 | 14.562050 .. 14.562054 |

Predictions L1 to L4 met; addendum 1: M3 met, M2 and M4 met through 5x1 certified, M1 missed (the state count of six plaquettes is 8,051; the prediction wrote 7,953).

## The centre: where the gap is smallest (`RESULT-CENTRE.hbp`, `RESULT-CENTRE-CELLS.hbp`, `RESULT-SPARSE.hbp`)

Coming from the magnetic side the gap is about 2r - lam (lam = largest adjacency eigenvalue of the plaquette graph); from the electric side about 12 - r. The two meet at r* = (12 + lam)/3, and the scan in steps of one third of r finds the smallest gap there on every grid.

| Shape | Grid | States | Smallest gap on the scan | at r | Kind |
|---|---|---|---|---|---|
| ladder | 1x1 | 3 | 10.2880 | 3 | certified |
| ladder | 2x1 | 11 | 9.4346 | 10/3 | certified |
| ladder | 3x1 | 49 | 8.8579 | 13/3 | certified |
| ladder | 4x1 | 251 | 8.5764 | 11/3 | certified |
| ladder | 5x1 | 1,393 | 8.4270 | 11/3 | certified |
| ladder | 6x1 | 8,051 | 8.3221 | 14/3 | certified (hosted cells) |
| ladder | 7x1 | 47,449 | 8.2473 | 14/3 | upper end |
| two wide | 2x2 | 251 | 8.0180 | 14/3 | certified |
| two wide | 3x2 | 8,051 | 7.1438 | 14/3 | certified (hosted cells) |
| two wide | 4x2 | 282,251 | 6.6624 | 14/3 (only point run) | upper end |

Steps: ladder 0.149, 0.105, at least 0.075; two wide 0.874, at least 0.482. The scan is coarse, so each true minimum is at or below the listed value.

Predictions: C1, C2, C4 met, C3 missed (predicted between 4 and 8 on every grid; all six came in above 8, from 8.018 to 10.288); D1, D2, D3 met; F1, F4 met, F2 missed low (4x2 at 6.6624 against a predicted 7.0 to 8.018), F3 missed (the E0 bracket at r = 9 on 7x1 is 0.006 wide).

## Larger grids, upper ends (`RESULT-CHEB.hbp`; predictions H1 to H7 frozen at commit 78bdcb2)

Thirty hosted cells (run 43707802823), this machine, and a cloud container. Smallest certified upper end of the gap over the couplings run for each grid:

| Shape | Grid | States | Smallest upper end | at r | Couplings run (thirds) |
|---|---|---|---|---|---|
| ladder | 6x1 | 8,051 | 8.2273 | 13/3 | 13, 15 (and certified 8.3221 at 14) |
| ladder | 8x1 | 282,251 | 8.1106 | 13/3 | 12 to 15 |
| ladder | 9x1 | 1,686,433 | 8.0784 | 13/3 | 13 to 15 |
| ladder | 10x1 | 10,097,891 | 8.1379 | 14/3 | 14 only |
| two wide | 3x2 | 8,051 | 7.0743 | 13/3 | 13, 15 (and certified 7.1438 at 14) |
| two wide | 4x2 | 282,251 | 6.5893 | 13/3 | 11 to 16 |
| two wide | 5x2 | 10,097,891 | 6.3029 | 13/3 | 12 to 16 |
| three wide | 3x3 | 1,686,433 | 6.0629 | 13/3 | 11 to 17 |

Every minimum sits at 13/3, one scan step below the 14/3 used in the table above; the 14/3 values there are one step above the minimum. Two-wide steps at the minimum: 0.485, 0.286.

Predictions: H1 met (5x2 at 14/3: 6.3799). H2 and H3: the value bands met, the location missed (13/3 against a predicted 14/3 or above). H4: 8x1 and 9x1 missed low, 10x1 met. H6 missed (the E0 bracket is wider than 0.001 scaled on 3x3 at 15 to 17 thirds, 5x2 at 14 to 16 thirds, and 10x1). H7 met: the 5x2 row at 14/3 from this machine (6 threads) and from a hosted cell (4 threads) is the same row byte for byte. H5 (6x1 at r = 9, dense and certified) and the cloud witness are filed when they end.

## How this relates to the registered torus results

The repository's main results are on the torus (periodic lattice), where a single transposition flux is forbidden (their number is even) and the gap above the eight flat states is about 3r: at r = 9 at least 24.04 on 3x4 and, with no store, at least 23.95, 23.62 and 21.79 on 4x4, 4x5 and 5x5 (`native/ym/results/3x4_stream/perron/vector/VECTOR-BOUND.md`). On an open grid one transposition flux is allowed, so the first gap here is about 2r - lam. The two sets of numbers are different quantities.

The no-store hybrid certificate of that document gives a certified lower end in about a minute per point; it is the route to sizes beyond ten plaquettes, where the programs of this folder stop. The open two-plaquette matrix of this folder is the Stage 2B matrix of the repository (`STAGE2B_DOUBLE_PLAQUETTE_EXACT_SPECTRUM.md`), rebuilt.

## Perturbation theory in the electric term

Ground state: the flat orbit. First excited manifold: one reflection flux on one plaquette (cost 2r).

- First order (`RESULT-PT.hbp`): gap = 2r - lam: 18, 17, 16.586, 16.382, 16.268 for the ladders and 16 for 2x2, equal to the hand values. It lies 1.20 to 1.30 above the certified gap on all six grids (N2, N3 met).
- Second order at r = 9: **missed** (N1). It lies 4.10, 1.69, 1.14, 0.89, 0.74 and 0.17 below the certified gap. The rotation flux (3r) is only r = 9 above the reflection flux and couples to it with strength of the same size.
- Exploratory widened manifold (`pt_explore.py`, after the run): no better; kept only as a record.
- Scaling test (`RESULT-PT-SCALING.hbp`), 1x1, 2x1, 3x1 at r = 9, 90, 900: the first-order error falls by 9.8, 10.1 and 10.2 from r = 90 to r = 900 (S1 met). The second-order error falls by 985, 44 and 66; the frozen band was 50 to 200, so S2 is **missed** as frozen. At r = 900 the second-order gap is within 0.000011, 0.000053 and 0.000054 of the exact gap of about 1,799. Run 1 refused at r = 900 because the search range in `pt_check.py` was +-1000; it is kept as `RESULT-PT-SCALING-RUN1-INSTRUMENT-FAULT.hbp`.

## Reading (the seat's, tagged)

- MEASURED: on every grid the gap is large on both sides and smallest near r* = (12 + lam)/3, about 14/3.
- MEASURED: at the centre the ladder levels off near 8.1 (upper ends 8.227, 8.111, 8.078 for 6, 8, 9 plaquettes); the two-wide strip is lower with shrinking steps (upper ends 7.074, 6.589, 6.303); the one three-wide grid, 3x3, is lower again (6.063).
- CONJECTURE: a strip of fixed width is one-dimensional in its long direction, so each width keeps a positive smallest gap as it gets longer, and those limits fall as the width grows. Whether they fall to zero as the width grows is the open question; it is the finite-grid form of asking whether this S3 model has a phase transition between its two sides. The repository cites a published first-order transition for this S3 model; whether this centre is that transition waits on mapping the couplings.
- Open: a certified lower end for E1 beyond 8,051 states.
