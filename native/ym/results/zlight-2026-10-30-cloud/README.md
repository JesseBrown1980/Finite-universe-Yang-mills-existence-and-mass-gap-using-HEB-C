# zlight, cloud seat: an instant global hash layer versus light at c = 1 (2026-10-30)

The cloud seat's independent implementation of the zlight test. It was written without reading the
acer implementation (`../zlight-2026-10-30/`). Integer only, Rust 1.81, clippy `-D warnings` exit 0,
records in HBP with SHA-256 sidecars (json=0).

## Model

- A 33 × 33 grid of `u32` cells, all 0 at the start. Steps 0 to 48.
- A laser fires at step 0 from S = (0,16). Its front advances exactly one cell per step (c = 1) in
  its aim direction and leaves its payload in every cell it passes.
- Seven universes: aim east or north × payload 1, 2 or 3, plus a baseline with no laser.
- Target T = (32,16), 32 cells from S, on the east beam's path. The north beam never reaches it.
- Global layer z: a SHA-256 Merkle root over all 1,089 cells, every step.
- Local layer at T: SHA-256 of T's own cell.

## Pre-registration

`PREREG.md` was frozen before any code was written (SHA-256 `a285be40…`, in `PREREG.md.sha256`).

## Result (`RESULT.hbp`)

| | prediction | measured | verdict |
|---|---|---|---|
| P1 | global root differs from baseline at step 0 in all 6 laser runs | step 0 in all 6 | PASS |
| P2 | T's local hash first differs at step 32 (east), never (north) | 32 / never | PASS |
| P3 | steps 0–31: T's local view sequence identical in all 7 runs | 1 distinct, 0 bits | PASS |
| P4 | step 32: 4 distinct local views | 4 | PASS |
| P5 | step 0: 7 distinct global roots | 4 | FAIL |

Registered verdict: **FAIL**, on P5 alone. The prediction was wrong, not the layers: at step 0 the
front is still in S for both aims, so the root encodes the payload but not yet the aim.
One step later the root takes 7 distinct values. That line is in `RESULT.hbp` as
`ZLIGHT_POSTHOC|not_preregistered=1`, and it does not change the verdict.

So the z layer changes at the moment the laser fires and carries the full event from step 1 on.
The target's own cell changes exactly when the light arrives. A reader of T's own cell learns
0 bits about aim or payload before arrival.

## Runs

- `RESULT.run1.hbp` is the first run, from `run1/main.rs`. That source failed clippy
  (`format_collect`) only.
- `src/main.rs` fixes that lint and adds the post-hoc step-1 line. Its run, `RESULT.hbp`, has
  registered lines byte-identical to run 1.
- `run.sh` rebuilds both versions in a scratch copy, outside the workspace, and checks that each
  reproduces its record byte for byte. Its output is `REPRO.hbp`: both byte-identical, clippy exit 0.

## Integrity chain (HBI → HBP → SHA → SH → HASH, json=0)

| layer | file | role |
|---|---|---|
| HBI | `ZLIGHT.hbi` | One chained `EMIT` row per file in sorted path order. `pid[0] = sha16("EMITTER-SEED|YM-ZLIGHT-2026-10-30-CLOUD")`, `pid[n] = sha16(pid[n-1] + "|" + path)`, where sha16 is the first 16 hex of SHA-256. |
| HBP | `PREREG.md`, `RESULT.hbp`, `RESULT.run1.hbp`, `REPRO.hbp` | Predictions, measurements and the reproduction. |
| SHA | `SHA256SUMS`, `*.sha256` | SHA-256 of every file except the three chain files. |
| SH | `run.sh` | The reproduction procedure. |
| HASH | `ZLIGHT.seal` | `sha256(SHA256SUMS + ZLIGHT.hbi)`. |

To verify: `sha256sum -c SHA256SUMS`, then `cat SHA256SUMS ZLIGHT.hbi | sha256sum` against `ZLIGHT.seal`.
