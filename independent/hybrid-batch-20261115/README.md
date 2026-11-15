# Hybrid no-store certificate: a batch of torus points, November 15, 2026

Seat ACER-CLAUDE-FABLE52, at the operator's direction ("hybrid batch first on the 20 cells"). The method is the registered one of
[`VECTOR-BOUND.md`](../../native/ym/results/3x4_stream/perron/vector/VECTOR-BOUND.md); its sources are unchanged. New here: `point.sh`, which fits the vector at 17 targets and then 8 finer
ones, and the 20-cell workflow. Predictions K1 to K7 were pushed before the run (`PREDICTION.hbp`).

Certified lower ends of E₉ − E₈ in J_E. Each certificate was recounted and recomputed by the separately written `hybridcheck` (verdict PASS on every row below).

| Torus | Cut | r = 5 | r = 6 | r = 7 | r = 8 | r = 9 |
|---|---:|---:|---:|---:|---:|---:|
| 4×4 | 14 | 3.706246 | 10.695162 (registered 11.012989) | 16.188650 | 20.281959 | registered 23.947629 |
| 4×5 | 13 | | 7.407438 | 14.783929 | 19.724871 | registered 23.618291 |
| 5×5 | 11 | | 1.767201 | 9.401598 | 16.025860 | registered 21.792208 |
| 5×5 | 13 | | | | | **23.333209** |
| 4×6 | 13 | | | | | **23.305930** |
| 5×6 | 11 | | | | | **19.470409** |

4×4 at r = 4: the certificate at this cut is below E₈'s upper end (−6.385824), so it gives no information there.

**Not measured.** 6×6 (four cells): the programs stop with "each side at least 3, at most 32 plaquettes". 7×7 and 8×8 (three cells): killed before any fit; the 6×6 table alone took 6.3 GB. So K5 and K6 are not measured, and sizes above 32 plaquettes need the tools extended.

**Predictions.** K1, K2, K4, K7 met. K3 met at r = 7 and 8, missed at r = 6 (4×5 came in 3.29 below 4×4, the prediction allowed 2.5). K5, K6 not measured.

**Run 1** stopped at the gate on all 20 cells because the vector program accepts at most 3 threads and the workflow passed 4; no point ran (`RUN1-INSTRUMENT-FAULT.hbp`).

Each number is a statement about one finite torus. A number that falls with size at a fixed cut measures the method; the gap itself stays near 3r − 21/r on every torus where the cut is high enough.

## The widened run (tori of 33 to 48 plaquettes)

Run 43717787958, ten hosted cells, with the widened copies written by `widen.py`. Nine cells ended, each with
`hybridcheck` verdict PASS; one (6x8 at r=12) was stopped at the six-hour limit. Rows: [`RESULT-WIDE.hbp`](RESULT-WIDE.hbp)
and [`wide-rows/`](wide-rows/).

Two new certified points:

| torus | r | cut | E9 - E8 at least |
|---|---|---|---|
| 4x7 | 9 | 13 | 22.760421 |
| 4x8 | 9 | 13 | 20.687246 |

With the registered 4x4 (23.947629), 4x5 (23.618291) and 4x6 (23.305930), the 4xL floors at r=9 fall slowly with L.

On 6x6, 5x7, 5x8 and 6x7 the certificate returned by this fitted-table method is the table floor (for example 80.0
at cut 11 on 6x6): a valid lower bound that sits below E8. Those sizes are certified by the program in
[Rust-program-for-large-tori](https://github.com/JesseBrown1980/Rust-program-for-large-tori) (6x6 at r=9: 16.904567).

Predictions K5 and K8 to K11 are judged in `RESULT-WIDE.hbp`: K8 met for 4x7, missed for 4x8 by 0.81; K11 met;
K5, K9 and K10 missed on the sizes above.
