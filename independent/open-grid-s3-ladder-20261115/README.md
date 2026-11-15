# Open grids of S3 plaquettes: certified gaps, a Rust route, and a perturbation-theory check

Seat ACER-CLAUDE-FABLE52, 2026-11-15, at the operator's direction. Every prediction file was pushed before its run.

## Method

The gauge-invariant space of P open plaquettes is one group element per independent loop up to one global conjugation: (6^P + 2*3^P + 3*2^P)/6 orbits. For two plaquettes this reduced matrix has the same characteristic polynomial as the 6^7 brute force of `benchmark-two-plaquette-d3-20261115`.

- `open_grid.py`: exact integer inertia counts (Python; practical to about 50 orbits).
- `rust/src/main.rs`: Rust 1.81, clippy `-D warnings` exit 0, integers only. Fixed-point subspace iteration gives an estimate; inertia counts in outward-rounded integer intervals certify the brackets (a count is reported only when every pivot interval excludes zero). Rust and Python brackets overlap on 1x1, 2x1, 3x1.

## Gaps at r = 9 (`RESULT-GRID-RUST.hbp`)

| Grid | Orbits | Gap E1 - E0 |
|---|---|---|
| 1x1 | 3 | 16.765065 .. 16.765069 |
| 2x1 | 11 | 15.701569 .. 15.701573 |
| 3x1 | 49 | 15.327304 .. 15.327308 |
| 4x1 | 251 | 15.151157 .. 15.151197 |
| 5x1 | 1,393 | 15.052328 .. 15.052368 |
| 2x2 | 251 | 14.801616 .. 14.801620 |

Predictions L1 to L4 met. 3x2 and 6x1 (7,953 orbits) are filed in `RUN-3x2.txt` and `RUN-6x1.txt` when their run ends (addendum 1).

## Perturbation theory in the electric term

Ground state: the flat orbit. First excited manifold: one reflection flux on one plaquette (cost 2r).

- First order (`RESULT-PT.hbp`): gap = 2r - (largest adjacency eigenvalue of the plaquette graph): 18, 17, 16.586, 16.382, 16.268 for the ladders and 16 for 2x2, equal to the hand values. It lies 1.20 to 1.30 above the certified gap on all six grids (N2, N3 met).
- Second order at r = 9: **missed** (N1). It lies 4.10, 1.69, 1.14, 0.89, 0.74 and 0.17 below the certified gap. The rotation flux (3r) is only r = 9 above the reflection flux and couples to it with strength of the same size.
- Exploratory widened manifold (`pt_explore.py`, after the run): no better; it mixes orders (excited manifold at first order, ground level at second) and is kept only as a record.
- Scaling test (`RESULT-PT-SCALING.hbp`), 1x1, 2x1, 3x1 at r = 9, 90, 900: the first-order error falls by 9.8, 10.1 and 10.2 from r = 90 to r = 900 (S1 met). The second-order error falls by 985, 44 and 66; the frozen band was 50 to 200, so S2 is **missed** as frozen (one grid falls faster, one slightly slower). At r = 900 the second-order gap is within 0.000011, 0.000053 and 0.000054 of the exact gap of about 1,799.

Reading: the lowest excitation is a reflection flux that hops between neighbouring plaquettes; the series in electric/magnetic converges to the exact gap as r grows, and at r = 9 it is outside the range where two orders are enough.

Run 1 of the scaling test refused at r = 900 because the eigenvalue search range in `pt_check.py` was +-1000; it is kept as `RESULT-PT-SCALING-RUN1-INSTRUMENT-FAULT.hbp`, and the range is now +-100000.

## Scope

Open-boundary grids. The 3x4 torus of the main result is a different system.
