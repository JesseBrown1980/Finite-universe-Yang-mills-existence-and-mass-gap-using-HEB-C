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
