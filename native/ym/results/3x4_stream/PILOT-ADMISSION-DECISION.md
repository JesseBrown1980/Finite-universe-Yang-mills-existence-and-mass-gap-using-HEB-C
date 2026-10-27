# 3×4 pilot (run 40391283682): admission decision

**Decision: HOLD.** The pilot finished and sealed with `PASS`, but it measured nothing that
the admission rule needs. `PRODUCTION-ADMISSION.md` cannot get its `COL_BYTES` and
`RESERVE` values from it, so no production concurrency can be derived and production is
not admitted.

| item | value |
|---|---|
| run | 40391283682, conclusion `success` (129 of 129 jobs) |
| commit | `9f929a8083b9f94a13a95f56622054cc4f46ca4f` (2026-10-26 16:56 −03), workflow `hebc-ym-stream-3x4-pilot.yml` |
| sealed receipt | `HEBC-YM-STREAM-3X4-PILOT.hbp`, SHA-256 `008029a484ee4592c5e374221e2d309e3a6b4d14ce4e937ed4908bf058879ef7` (`sha256sum -c` passes), committed here |
| binary | `ymstream 3 4 1000 9000 <26 thresholds> r 128`, one of 128 classes per job, `WORKERS=$(nproc)` (4) |

## Why it cannot set the admission values

- **What the rule needs.** `COL_BYTES` is the largest measured per-block increase in
  resident memory plus that block's peak temporary allocation. `RESERVE` is the measured
  idle resident memory of the same binary on the same sector. Both are bytes, rounded up
  to whole MiB.
- **What the pilot ran.** `ymstream` is the constant-memory streaming orbit counter. Its
  workflow describes it as "no matrix is stored". It holds no column blocks, so it has
  no per-block memory to measure.
- **What it recorded.** It recorded no memory figure of any kind: no `VmHWM`, no RSS and
  no byte count. Its only resource figure is wall time per class: 97,313–222,494 ms,
  20,790,519 ms in total.
- **Timing.** The pilot was committed on 26 October. The admission rule's measured-value
  clauses were frozen on 27 October.

The production allowance is unchanged: `BUDGET = 12 × 2³⁰` bytes, with `RESERVE` charged
inside it. The design estimate of 8 blocks is not a measured value, so it is not used. With
`COL_BYTES` and `RESERVE` unmeasured, the cap `⌊(BUDGET − RESERVE)/COL_BYTES⌋` is undefined.
The Lean admission theorem (`HebcShadow/Admission.lean`) is unchanged. It has no
measured values to be run against.

## What the pilot did establish

These are recomputed independently from the sealed receipt, not taken from its summary lines:

- All 128 classes are present, with class indices exactly 0–127.
- The sum of per-class gauge orbits is 2,177,317,873. That equals the
  `YMSTREAM_TOTAL` orbit count and its Burnside count (`orbits_match=1`).
- Each of the four one-dimensional sectors `Sx±Sy±` passes two checks:
  - the per-class representative counts sum to the sector's `states`;
  - the summed character values divide exactly by 48 and give the same number.

  | sector | states |
  |---|---|
  | Sx+Sy+ | 45,508,080 |
  | Sx+Sy− | 45,304,566 |
  | Sx−Sy+ | 45,305,003 |
  | Sx−Sy− | 45,329,747 |

These checks belong to the 3×4 run's own dimension reconciliation, which
`PRODUCTION-ADMISSION.md` requires the run to earn for itself. They do not admit production.

## What would lift the HOLD

The HOLD lifts only after a separate memory pilot, frozen before it runs, of the production
column-block runner itself. That pilot must:

- measure `VmHWM` with the runner idle on a sector, to give `RESERVE`;
- measure, for every block of every pilot cell, the increase in resident memory plus the
  peak temporary allocation, to give `COL_BYTES`;
- record both as integer bytes, together with block dimensions, sector, commit and
  receipt hashes.

Then `CAP` is computed, `PRODUCTION-ADMISSION.md` is filled in from those receipts, and the
Lean admission check is re-run on the values. Production is admitted only if `CAP ≥ 1` and
every other frozen gate passes.
