# zlevel, cloud seat: j instant per level, r travelling (2026-10-30)

The cloud seat's independent per-level test, beside acer's `../perlevel-2026-10-30/`. Integer only,
Rust 1.81 with no dependencies, clippy `-D warnings` exit 0, records in HBP (json=0).

## Model

Rings of M = 3^N cells, N = 3, 4, 5 (27, 81, 243), read as triples nested N levels deep: base-3
digit k of a cell is its place in its level-k triple. Every ordered pair of cells is measured.

- r on the ring (the radius, straight and bidirectional): one step reaches both neighbours, c = 1.
- triangle r: R_0 + R_0², cyclic inside each level-0 triple.
- j at level k: J_k = I + R_k + R_k², joining the three cells that differ only in digit k.
  Cascade: step s applies level s − 1.

## Result (`RESULT.hbp`): 18 of 18 PASS

Predictions were frozen in `PREREG.md` (SHA-256 `5ec4b2cf…`) before any code was written.

| | N = 3 | N = 4 | N = 5 |
|---|---|---|---|
| steps for j to reach everything | 3 | 4 | 5 |
| steps for ring r to reach everything | 13 | 40 | 121 |
| pairs where j arrives first | 594 / 702 | 6,132 / 6,480 | 57,732 / 58,806 |
| pairs where r arrives first | 30 | 108 | 348 |

- j costs exactly one step per level; the product of all levels is the all-ones matrix, which
  reaches every cell in one application. r needs up to (M − 1)/2 steps.
- Inside a level, triangle r and j reach every sibling in 1 step. On the ring, one third of
  sibling pairs take 2 steps.
- Every pair where r beats j sits across a level boundary: neighbours 1 apart for r, k + 1 steps
  apart for j. No pair inside a triple does.
- The third seat's Python reference reproduced the three pair counts exactly.

## Replay and integrity chain (HBI → HBP → SHA → SH → HASH, json=0)

`run.sh` checks the prediction seal, builds with Rust 1.81, runs clippy and checks byte identity
with `RESULT.hbp`. The workflow `hebc-ym-cloud-replay.yml` runs it on the exact PR head.
`SHA256SUMS` covers every other file, `ZLEVEL.hbi` holds the chained `EMIT` rows
(`pid[0] = sha16("EMITTER-SEED|YM-ZLEVEL-2026-10-30-CLOUD")`, `pid[n] = sha16(pid[n-1] + "|" + path)`),
and `ZLEVEL.seal = sha256(SHA256SUMS + ZLEVEL.hbi)`.
