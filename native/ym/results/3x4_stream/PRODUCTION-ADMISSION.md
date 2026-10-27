# 3×4 production: the admission rule (frozen before any production run; conservative bounds and reserve added 2026-10-27, before any pilot memory value was read)

This fixes, ahead of time, how many column blocks a 3×4 production runner may hold at
once. The rule is the Never-Explode bound from the Asolaria reductions work
(`what-is-asolaria---how-do-we-get-reductions-in-everything`, F04 §4): a chamber enters
only while the resident set stays within a fixed budget. It does not change any count,
threshold or gate. It decides only what is allowed into memory.

## Quantities (integers, bytes)

- **`BUDGET`:** the memory a runner may give to resident column blocks.
  `BUDGET = 12 × 2³⁰` (12 GiB), leaving headroom below the hosted runner's 16 GiB for the
  binary, the sector index and the operating system.
- **`COL_BYTES`:** a **conservative upper bound** on one active column block, including
  its temporary buffers and allocator overhead. It is not an average or a single typical
  observation. The design estimate is about 1.44 × 10⁹. The pilot replaces it with the
  largest per-block increase in resident memory it measures, over every block of every
  cell, plus that block's peak temporary allocation, rounded up to whole MiB. Production
  cannot start until that measured value is written here.
- **`RESERVE`:** the fixed runtime footprint outside the column pool: the binary, the
  sector index and the stream state. It is the pilot's measured idle resident memory of
  the same binary on the same sector with no column blocks resident, rounded up to whole
  MiB. `BUDGET` covers the whole process, so `RESERVE` is charged against it.
- **`CAP = ⌊(BUDGET − RESERVE) / COL_BYTES⌋`:** the most column blocks resident at once. With
  the design estimate and no reserve, that is 8.

## The rule

A column block is admitted only if `(active + 1) · COL_BYTES + RESERVE ≤ BUDGET`. Otherwise
it waits until a resident block finishes and is released. Release only ever lowers
`active`.

## Why it cannot overflow

Let `S = active · COL_BYTES + RESERVE`. It holds that `S ≤ BUDGET` at the start
(`active = 0`, as long as `RESERVE ≤ BUDGET`). An admission happens only when the
post-admission value satisfies `S + COL_BYTES ≤ BUDGET`, and a release only decreases `S`.
So `S ≤ BUDGET` is forward-invariant: it holds after every step, for **any** order of
arrivals and completions. Because `COL_BYTES` and `RESERVE` are upper bounds, the
process's resident memory can never exceed `BUDGET`, by construction rather than by luck.

## Runtime gate

Every production cell records, as integers:

- the peak resident set of its process, read from `/proc/self/status` (`VmHWM`, in kB),
  converted to bytes;
- the largest `active` it reached;
- the **largest projected admission value** it tested against the budget,
  `max (active + 1) · COL_BYTES + RESERVE`;
- `COL_BYTES` and `RESERVE`.

| condition | outcome |
|---|---|
| peak `active > CAP` | INCONCLUSIVE (the rule was not obeyed) |
| peak resident bytes `> BUDGET` | INCONCLUSIVE (an upper bound was wrong) |
| the largest projected admission value `> BUDGET` | INCONCLUSIVE (the rule was not obeyed) |

Any of these sends production back to re-measure `COL_BYTES` and `RESERVE`, without
adjusting any count.

## Rolling re-proof

Nothing carries over from 3×3. The 3×4 run must earn its own dimension reconciliation
(Burnside = character formula = Σ sector dimensions), its own core table and its own
seals, as each lattice size before it did.
