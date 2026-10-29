# 3×4 production memory pilot on the GitHub hosted runner (frozen before it runs)

This fixes how `COL_BYTES` and `RESERVE` of `PRODUCTION-ADMISSION.md` are measured, and
how the measurements decide admission, before any pilot run. **Writing this spec does not
lift the HOLD. Only a valid run under it can.** It changes no count, threshold, gate or
sealed receipt, and nothing measured on Host8 counts here.

## 1. What is measured: the production unit

- **The unit.** One `roomschur` process (the room-backed form of `shellschur`, the same
  arithmetic) on the 3×4 Sx+Sy+ sector, with the matrix in a room store built on the
  runner by `ymroom` (pass A, then pass B).
- **Why not `shellschur`.** `shellschur` reads the whole text matrix into RAM, and `ymsec`
  keeps a 13 GB `Vec<bool>` over 6¹³ tree configurations.
  `benchmarks/onfly_3x4.hbp` records `full_inertia_certificate=NOT_FEASIBLE_with_current_tools`
  for that path: a stored matrix of about 3.40×10⁹ entries is about 40 GB. So
  `roomschur` is the only production unit that can fit a hosted runner.
- **Column block.** One core column of the Schur complement. Its resident state is one
  lo/hi enclosure pair per state, checked i64. The declared exact allocation is
  `COL_BYTES_decl = 16·n`. `K` blocks are resident and swept together (`ROOMSCHUR_K = K`).
- **Fixed part.** The declared allocation outside the column pool is
  `RESERVE_decl = 41·n + 3·64 MiB`: diagonal, core flags and index arrays, plus three
  64 MiB read buffers.

For n = 45,508,080 (pass A, equal to CI pilot run 40391283682):

| quantity | value (bytes) | MiB-rounded |
|---|---|---|
| `COL_BYTES_decl` | 728,129,280 | 728,760,320 |
| `RESERVE_decl` | 2,067,157,872 | 2,067,791,872 |

`CAP_decl = ⌊(12,884,901,888 − 2,067,157,872) / 728,129,280⌋ = 14`. That is the
declared design value. **It is not an input**: only the measured values below can admit
production.

## 2. Preconditions (all must hold before the pilot may be dispatched)

| # | precondition | state on 2026-10-29 |
|---|---|---|
| P1 | `ymroom` and `roomschur` merged to `main`, authored as Jesse Daniel Brown, with the required CI (Rust 1.81, `clippy -D warnings`, no floats) green on the merge commit | open: on branch `ym-3x4-room-backed` (`c07eef7`), not merged |
| P2 | builder identity: `ymroom text` equal byte for byte to `ymsec` on 2×3, 2×4 and 3×3, rerun in CI | reported EXACT on Host8; not yet in CI |
| P3 | runner identity: `roomschur` and `shellschur` give record-identical `SHELL_SCHUR`/`SCOL` output on 3×3 at t = 60, 72 and 90 million (JE = 1000, JB = 9000), in CI | PENDING |
| P4 | this spec, the pilot workflow and its controls (§7) committed, with their SHA-256 values recorded in the workflow | this file; workflow not written |

A pilot run that starts without every precondition is not a pilot under this spec.

## 3. Runner and budget (frozen)

- **Runner.** `runs-on: ubuntu-24.04`, a GitHub-hosted standard runner, pinned rather than
  `ubuntu-latest`. The receipt records `ImageOS`, `ImageVersion`, `nproc`, `MemTotal`
  from `/proc/meminfo`, the CPU model, the kernel, the cgroup version, and the free bytes
  of every mounted volume.
- **Budget.** `BUDGET = 12 × 2³⁰ = 12,884,901,888` bytes for the whole `roomschur`
  process (`PRODUCTION-ADMISSION.md`), unchanged.
- **Store volume.** The room store goes on the volume with the most free space. Its
  size, `16·n` header bytes plus `8·nnz` payload bytes, must fit with at least 1 GiB to
  spare, or the run stops `INCONCLUSIVE (disk)`.
- **Store binding.** The store's payload merkle and entry count are recorded. If a
  sealed Host8 pass-B receipt exists by then, both must equal it; any difference stops
  the run `INCONCLUSIVE`.

## 4. Measurements (all integers)

The phases run in one job, in order:

1. **Build.** `ymroom passa`, then `ymroom build`. The receipt records wall seconds,
   `ru_maxrss` and n, nnz, the merkle and `w_self_adjoint`. The build is not part of
   `RESERVE`; it is a separate process.
2. **Sweeps.** `roomschur` at JE = 1000, JB = 9000, t = 60,000,000, on core columns
   `0..K`, for **K = 1, 2 and 4**. Each run uses `MAXSWEEP = 2`, so two full sweeps over
   the store, with `WORKERS = nproc`.

Each `roomschur` run:

- **Runs in its own cgroup.** A fresh cgroup v2 directory with the memory controller
  enabled, entered by `cgroup.procs` before `exec`. After the process exits, the receipt
  records `memory.peak`, `memory.events` (`oom`, `oom_kill`) and a 1 s sample of
  `memory.stat anon`, taking its maximum.
- **Runs under `/usr/bin/time -v`.** The receipt records `Maximum resident set size`
  (kernel `ru_maxrss`, in KiB; multiplied by 1024 to give bytes) and the exit status.
- **Keeps its outputs.** The receipt keeps its `ROOMSCHUR_ADMISSION` line and its `SCOL`
  lines.

**Accounting rule (fixed now).** The resident peak of a run is

`P(K) = max(ru_maxrss·1024, sampled anon maximum)`.

`memory.peak` also counts reclaimable page cache from streaming the store. It is
recorded but not used, because it would charge cached file pages to the process.

**Derived values (outward rounding, whole MiB):**

```
COL_BYTES_meas = ⌈ max( P(2) − P(1),  ⌈(P(4) − P(2)) / 2⌉ ) ⌉_MiB
RESERVE_meas   = ⌈ max_K ( P(K) − K·COL_BYTES_meas ) ⌉_MiB
COL_BYTES      = max(COL_BYTES_meas, COL_BYTES_decl rounded up to MiB)
RESERVE        = max(RESERVE_meas,   RESERVE_decl rounded up to MiB)
CAP            = ⌊ (BUDGET − RESERVE) / COL_BYTES ⌋
```

`P(K) ≤ K·COL_BYTES + RESERVE` then holds for every measured K by construction. Taking
the maximum with the declared values means the admitted bound is never below the
program's own declared allocation.

## 5. Gates and outcomes

| outcome | when |
|---|---|
| `INCONCLUSIVE` (HOLD stays) | any precondition unmet; a missing, truncated, malformed or incompatible measurement (for example, no cgroup v2 memory controller, or `/usr/bin/time` absent); a transport or upload failure; a phase that does not finish in the job; a disk-fit failure; a store binding mismatch |
| `NOT_ADMISSIBLE` (HOLD stays, reason recorded) | every measurement valid, but `CAP < 1`, or any run has `oom` or `oom_kill > 0`, or any `P(K) > BUDGET` |
| `PILOT_PASS` | every measurement valid, `CAP ≥ 1`, no OOM events, every `P(K) ≤ BUDGET`, every `ROOMSCHUR_ADMISSION` line `admitted=1`, and the `SCOL` lines of column 0 byte-identical across K = 1, 2, 4 |

The last condition holds because the columns are independent, so adding resident
columns must not change any column's enclosure.

Only `PILOT_PASS` lets `COL_BYTES`, `RESERVE` and `CAP` be written into
`PRODUCTION-ADMISSION.md`, with a link to the pilot receipt. Production still needs
every other frozen gate: the runtime gate of `PRODUCTION-ADMISSION.md`, its own
receipts, and its own rolling dimension reconciliation. The pilot proves memory
admission only. It is not a count, and it says nothing about the gap.

## 6. Receipt bindings

`HEBC-YM-3X4-MEMORY-PILOT.hbp`, with its `.sha256` sidecar, records:

- the run ID, the workflow commit, and the SHA-256 of this spec, the workflow, `ymroom`,
  `roomschur` and both built binaries;
- the runner identity of §3;
- the build record (n, nnz, merkle, `w_self_adjoint`, seconds, `ru_maxrss`);
- for each K: the raw `ru_maxrss`, the sampled anon maximum, `memory.peak`,
  `memory.events`, exit status, seconds, the `ROOMSCHUR_ADMISSION` line, and the SHA-256
  of its `SCOL` output;
- the derived `COL_BYTES_meas`, `RESERVE_meas`, `COL_BYTES`, `RESERVE`, `CAP`, and the
  outcome line.

The sidecar is written on every outcome, not only on `PILOT_PASS`: the receipt step
does not stop at the first non-zero status. This avoids the packaging defect found in
the 3×3 certify step.

## 7. Controls (run in CI before the pilot, synthetic inputs only)

The derivation script must give the frozen outcome for each synthetic case:

- a missing `ru_maxrss` gives `INCONCLUSIVE`;
- `oom_kill = 1` gives `NOT_ADMISSIBLE`;
- `P(4) > BUDGET` gives `NOT_ADMISSIBLE`;
- `RESERVE ≥ BUDGET` gives `CAP = 0`, which is `NOT_ADMISSIBLE`;
- column-0 `SCOL` differing between K values gives `INCONCLUSIVE`;
- measured values below the declared ones are lifted to the declared ones;
- a clean synthetic set gives `PILOT_PASS` with the exact integer `CAP`.

No real measurement enters a control.
