# 3×4 production fan-out: compute plan (frozen 2026-10-31, NOT RUN)

This freezes **how** the 3×4 Schur production is computed on hosted runners: which binary
runs, how the 137 core columns are split into jobs, how the store reaches each job, and which
controls must pass first. It does **not** freeze the gap-verdict rule (see §7). It changes no
count, threshold or gate already registered. Running it needs separate operator direction.

## 1. What is computed

- **Matrix.** The 3×4 Sx+Sy+ sector, n = 45,508,080, stored as 34 room sectors
  (`seg:341:34:800000000:sector-`), payload merkle
  `ec03c5f8ea5abd37ed8f80e0e9e7f00e37840a753f33a1008fbd090b18072a0b`.
- **Binary.** `roomschur` from `native/ym/crates/sturmrs/src/bin/roomschur.rs`, source SHA-256
  `8c2ebe8039654017ed1510e7e4f18a02dd410efb29e8df6a82bd72c4a2104cbe` (the source pinned by P4),
  built with Rust 1.81 on the runner. `roomjump` is not used: its admission values were not
  measured on a hosted runner, and on 3×4 its enclosures came out wider than `roomschur`'s
  (J2, `RUN-LOG.md`).
- **Arguments.** `JE=1000 JB=9000 FDIG=12 TOL=1000 MAXSWEEP=400`, threshold `t_milli` as
  registered under §7. These are the arguments of the local pilot `pilot3x4`.
- **Output.** Each job prints `SCOL` rows for its columns. One merge job runs
  `ROOMSCHUR_MERGE=<all SCOL files>` and prints the final `SHELL_SCHUR` row
  (`negative`, `ambiguous`, `result`).

## 2. Split into jobs

- 137 core columns, `ROOMSCHUR_COLS=a:b`, **K = 8 columns per job**, so 18 jobs:
  17 jobs of 8 columns (0:8 … 128:136) and one job of 1 column (136:137).
- **Admission.** `CAP = 12` from P4 (`P4-ADMISSION-DECISION.md`). K = 8 is below the cap.
  Each job runs with `ROOMSCHUR_BUDGET = 12884901888` and must print `ROOMSCHUR_ADMISSION|…|admitted=1`.
- Columns are independent: each column's sequence of updates does not depend on which
  other columns share its pass (`roomschur.rs` header). So a split never changes an `SCOL` row.

## 3. Store delivery

1. Download the 34 sector files and `SECTORS-341-374.sha256` from
   `datasets/Jessedbrown/ym-3x4-room-store` (commit `160726aa` or a later commit whose
   `SECTORS-341-374.sha256` is byte-identical).
2. `sha256sum -c SECTORS-341-374.sha256` must report 34 OK. Any failure: the job is
   INCONCLUSIVE and runs nothing.
3. `roomschur` re-checks the payload merkle on every pass and stops on a mismatch.

The hosted runner had 91,335,168,000 bytes free on `/` in P4; the store needs 27,200,000,000.

## 4. No checkpoints: a job finishes in one sitting or counts for nothing

`roomschur` cannot resume a column. A job that hits the runner time limit, is killed, or
prints no `SHELL_SCHUR_COLS` row is INCONCLUSIVE. Its columns are re-run from scratch in a new
job. Partial `SCOL` output is never merged.

## 5. Controls before any production job

| id | control | pass condition |
|---|---|---|
| C1 | Hosted job on columns 0:4 with the arguments of §1 at `t_milli=60000000` | its `SCOL` rows (with `ms=` removed) are byte-identical to `receipts/pilot3x4-local/pilot.out`, 548 of 548 |
| C2 | Same job | wall time, measured from the first setup pass to `SHELL_SCHUR_COLS`, is below 3 h, so a K = 8 job fits the limit with margin |
| C3 | Same job | `sha256sum -c` 34 OK, `admitted=1`, no OOM kill |

If C2 fails, K and the job count are redesigned and this spec is revised before any
production job. Nothing is dispatched on an estimate.

## 6. Run order

1. C1–C3 (one job).
2. The 18 production jobs, in parallel.
3. The merge job. All 18 jobs must have completed under §4, with every column 0–136 present
   exactly once and every `SCOL` row carrying `core_fp=4de7413741e7a4a6`. Otherwise the merge is
   INCONCLUSIVE.
4. If the merge reports `ambiguous > 0`, a second stage reruns **all** columns with
   `TOL=100`, then merges again. Stage-1 output is kept beside it. No column is re-run with
   a different TOL from the others.

## 7. Not frozen here

- **The gap-verdict rule for 3×4**: the threshold set `t_milli`, and how `negative` and
  `ambiguous` counts become a statement about the gap. It must be registered separately, before
  the first production job, alongside the rules already used for 2×L and 3×3.
- Any change of binary (for example to `roomjump`) needs its own measured admission values on
  the hosted runner and a C1 control of its own.

Production HOLD is unchanged by this file. There is no 3×4 gap verdict.
