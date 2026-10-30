# zcurve, cloud seat: test B, straight r versus curved j (2026-10-30)

The cloud seat's independent run of dictionary test B ("a straight line is symmetric; a curve is
not"), beside acer's `../dictionary-tests-2026-10-30/`. Integer only, Rust 1.81 with no
dependencies, clippy `-D warnings` exit 0, records in HBP (json=0).

## Model

Same lattices as zlevel (27, 81, 243 cells, nested triples). At level k:
r_k = R_k + R_k² (straight), J_k = I + R_k + R_k² (symmetric j), j_k = I + R_k − R_k² (curved j).

## Result (`RESULT.hbp`): 16 of 16 PASS

Predictions were frozen in `PREREG.md` (SHA-256 `51f05feb…`) before any code was written.

| | symmetric J | curved j |
|---|---|---|
| symmetric | yes, like r | no |
| reach time, every ordered pair | identical | identical |
| all levels at once | all-ones | every entry ±1; −1 count 351 / 3,240 / 29,403 |
| rank over GF(3) | 1 | full: 27 / 81 / 243 |
| distinct outputs from the M single-cell states | 1 | M |
| determinant, one level | 0 | 4 (≡ 1 mod 3) |

The symmetric J keeps only the total: every starting cell gives the same output, and where it was
is lost. The curved j keeps every cell distinct and is invertible mod 3. Reach is unchanged, so
the per-level reach results carry over and only the all-ones product (PR #40's Q5) is specific to
the symmetric j. The mirror I − R + R² passes the same checks (acer, PR #41).

## Replay and integrity chain (HBI → HBP → SHA → SH → HASH, json=0)

`run.sh` checks the prediction seal, builds with Rust 1.81, runs clippy and checks byte identity
with `RESULT.hbp`; `hebc-ym-cloud-replay.yml` runs it on the exact PR head. `SHA256SUMS` covers
every other file, `ZCURVE.hbi` holds the chained `EMIT` rows
(`pid[0] = sha16("EMITTER-SEED|YM-ZCURVE-2026-10-30-CLOUD")`), and
`ZCURVE.seal = sha256(SHA256SUMS + ZCURVE.hbi)`.
