# 3×4 production fan-out, revision 1: local rerun and local merge (NOT RUN)

This revision sits **beside** `PRODUCTION-FANOUT-SPEC.md`. That file stays frozen and unchanged
(its `.sha256` sidecar, checked by the workflow gate, still verifies). Revision 1 adds one lane: a
hosted job that does not finish (§4 of the spec) may be re-run **on the operator's local machine**,
where there is no 350-minute limit, and the merge may then run locally. It changes no binary
source, argument, threshold, column split rule, tolerance rule or registered gap rule. Running
anything under it needs separate operator direction.

## 0. Why

- The control (run 41294035019) finished columns 0:4 at K = 4 in 10,123 s, 677 s under the 3 h C2
  limit. Production jobs use K = 8. Their wall time is **not measured**. If time grew in
  proportion to column count it would be about 20,246 s against the 21,000 s job timeout
  (CONJECTURE: a sweep re-reads the whole store whatever K is, so the growth is probably less than
  proportional, but that has not been measured either).
- Under §4 a job that times out is INCONCLUSIVE and its columns must be re-run from scratch. Without
  this revision the only re-run lane is another hosted job, with the same limit.
- `.github/workflows/hebc-ym-3x4-fanout.yml` runs the hosted `merge` job only when **all**
  column jobs succeed. If any job times out, no hosted merge happens. This revision defines the
  merge that is used instead.

## 1. Local binary

- Source: `native/ym/crates/sturmrs/src/bin/roomschur.rs` at SHA-256
  `8c2ebe8039654017ed1510e7e4f18a02dd410efb29e8df6a82bd72c4a2104cbe`, the **same source the
  hosted jobs build**. The local segmented-store build (binary `a8007c15…`, source from
  `c25b4ac`) that produced `native/ym/results/3x4_room_backed/receipts/pilot3x4-local/pilot.out` is **not** used for production:
  its source differs, and spec §7 requires its own control for any change of binary.
- Built with `cargo +1.81 build --release` in a clean checkout of a `main` commit that contains
  this file. `cargo +1.81 clippy --release -- -D warnings` must exit 0. The binary's SHA-256
  and the checkout's head go into the local receipt (§5).
- The checkout must be made with `git -c core.autocrlf=false clone`. A local build on 2026-10-30
  (`D:/ym-3x4-room-run/rebuild-2e4846e/build1.log`) failed with exit 101 because a vendored crate's
  checksum no longer matched (`num-bigint/src/biguint/multiplication.rs`), the line-ending
  conversion on checkout. A build that fails, or a binary from any other checkout, is not used.

## 2. Local store

- The pinned source reads one file, not `seg:` sectors. The local store is the concatenation, in
  order, of the 34 sector files 341–374 (27,200,000,000 B), the same construction as the
  workflow (`cat sector-341.rooms … sector-374.rooms > store.rooms`).
- Before concatenation every sector must pass `sha256sum -c SECTORS-341-374.sha256` (34 OK), the
  file from `datasets/Jessedbrown/ym-3x4-room-store` commit `160726aa`. Sectors may come from the
  dataset or from `D:/ASOLARIA-HOST8-ROOMS-300G/`; either way the checksum file decides.
- After concatenation the size must be exactly 27,200,000,000 B. `roomschur` re-checks the
  payload merkle `ec03c5f8…` on every pass, as on the hosted runner.
- Disk: 27.2 GB for the store. D: had 41 GB free on 2026-11-01 (MEASURED, `df`).

## 3. Local control L1 (before any local production job)

| id | control | pass condition |
|---|---|---|
| L1 | local job, columns 0:4, arguments of spec §1 at `t_milli=60000000`, `TOL=1000` | its `SCOL` rows are byte-identical to `native/ym/results/3x4_stream/control/scol-0-4.out` (hosted, pinned source) **and** to `native/ym/results/3x4_room_backed/receipts/pilot3x4-local/pilot.out`, 548 of 548 |

There is no wall-time condition, because the local lane has no time limit. L1 runs once per
local binary SHA-256. A new local build (another machine, another toolchain patch) needs its own L1.

## 4. Which columns may be run locally

- **Only** the column range of a hosted job that is INCONCLUSIVE under spec §4 (timed out,
  cancelled, killed, or no `SHELL_SCHUR_COLS` row), in a production run that passed the gate. The
  hosted run's ID and the job's matrix entry are recorded.
- A hosted job that completed is never re-run locally, and its rows are never replaced.
- The local K may differ from 8. Each column's updates do not depend on which other columns share
  its pass (spec §2), so the split never changes an `SCOL` row. Every local job must print
  `ROOMSCHUR_ADMISSION|…|admitted=1` under the local `ROOMSCHUR_BUDGET`, which is recorded.
- Local arguments are identical to the hosted dispatch: `JE=1000 JB=9000 FDIG=12 MAXSWEEP=400`, the
  same `t_milli`, the same `TOL` as the stage being run.
- **No checkpoints, as in spec §4.** A local job that is killed (out of memory, reboot, the Claude
  Code background-shell memory reaper) or prints no `SHELL_SCHUR_COLS` row is INCONCLUSIVE and
  re-runs from scratch. A local job lasting hours is started outside Claude Code, or with
  `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1`, on operator direction.

## 5. Records

For each hosted run: run ID, head commit, and every `fanout-production-<i>` artifact downloaded
before it expires, with its `SHA256SUMS-<tag>` checked. For each local job:

```
LOCAL_JOB|cols=a:b|k=K|t_milli=T|tol=TOL|exit=0|secs=S|bin_sha256=…|src_sha256=8c2ebe80…|head=…|replaces_hosted_run=<id>|replaces_job=<cols>|json=0
```

with `scol-<a>-<b>.out`, `.err` and a `SHA256SUMS` beside it. L1 gets the same row with
`replaces_hosted_run=none` and its comparison line
`LOCAL_CONTROL|L1=PASS|scol_rows=548|bin_sha256=…|json=0`.

## 6. Merge

If the hosted merge job ran and completed, its `SHELL_SCHUR` row is the result and this section is
not used. Otherwise the merge runs locally with the L1-checked binary over the local store:

```
ROOMSCHUR_MERGE=<all SCOL files> roomschur store.rooms 0 1000 9000 <t_milli> 12 <TOL> 400
```

It is INCONCLUSIVE unless all of these hold:

1. every column 0–136 appears **exactly once** across the hosted-completed and local files;
2. every `SCOL` row carries `core_fp=4de7413741e7a4a6` and the dispatch's `t_milli`;
3. every file comes from a completed hosted job of the gated run, or from a local job recorded under
   §5 after L1 passed with the same binary SHA-256;
4. all files belong to the same stage (same `TOL`).

The merge output, every input file and their SHA-256 sums are committed together as the production
receipt, with the hosted run ID. If the merge reports `ambiguous > 0`, stage 2 (spec §6.4) re-runs
**all** columns at `TOL=100`, under the same hosted-first, local-rerun rules.

## 7. Unchanged

- The registered rule `GAP-VERDICT-RULE-3X4.md` (SHA-256 `d635a6e5…`) and its only admissible
  threshold, `t_milli=60000000`, which gives a vacuum lower bound, **not a gap**.
- The workflow and its gate. This revision adds no code.
- Production HOLD until the operator directs a dispatch. There is no 3×4 gap verdict.
