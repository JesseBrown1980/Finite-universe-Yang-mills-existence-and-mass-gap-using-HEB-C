# 3×4 production: the admission rule (frozen before any production run)

This fixes, ahead of time, how many column blocks a 3×4 production runner may hold at
once. The rule is the Never-Explode bound from the Asolaria reductions work
(`what-is-asolaria---how-do-we-get-reductions-in-everything`, F04 §4): a chamber enters
only while the resident set stays within a fixed budget. It does not change any count,
threshold or gate. It decides only what is allowed into memory.

## Quantities (integers, bytes)

- **`BUDGET`:** the memory a runner may give to resident column blocks.
  `BUDGET = 12 × 2³⁰` (12 GiB), leaving headroom below the hosted runner's 16 GiB for the
  binary, the sector index and the operating system.
- **`COL_BYTES`:** the resident size of one active column block. The design estimate is
  about 1.44 × 10⁹. The **measured** value from the 3×4 streaming pilot replaces it before
  production: the pilot's largest per-column resident size, rounded up to whole MiB.
  Production cannot start until that measured value is written here.
- **`CAP = ⌊BUDGET / COL_BYTES⌋`:** the most column blocks resident at once. With the design
  estimate that is 8.

## The rule

A column block is admitted only if `(active + 1) · COL_BYTES ≤ BUDGET`. Otherwise it waits
until a resident block finishes and is released. Release only ever lowers `active`.

## Why it cannot overflow

Let `S = active · COL_BYTES`. It holds that `S ≤ BUDGET` at the start (`active = 0`). An
admission happens only when the post-admission value satisfies `S + COL_BYTES ≤ BUDGET`,
and a release only decreases `S`. So `S ≤ BUDGET` is forward-invariant: it holds after
every step, for **any** order of arrivals and completions. The resident set of column
blocks can never exceed `BUDGET`, by construction rather than by luck.

## Runtime gate

Every production cell records, as integers:

- the peak resident set of its process, read from `/proc/self/status` (`VmHWM`, in kB),
  converted to bytes;
- the largest `active` it reached;
- `COL_BYTES`.

| condition | outcome |
|---|---|
| peak `active > CAP` | INCONCLUSIVE (the rule was not obeyed) |
| peak resident bytes `> BUDGET + overhead`, where overhead is the measured idle footprint of the same binary on the same sector with no column blocks resident, recorded by the pilot | INCONCLUSIVE (the per-column estimate was wrong) |

Either case sends production back to re-measure `COL_BYTES`, without adjusting any count.

## Rolling re-proof

Nothing carries over from 3×3. The 3×4 run must earn its own dimension reconciliation
(Burnside = character formula = Σ sector dimensions), its own core table and its own
seals, as each lattice size before it did.
