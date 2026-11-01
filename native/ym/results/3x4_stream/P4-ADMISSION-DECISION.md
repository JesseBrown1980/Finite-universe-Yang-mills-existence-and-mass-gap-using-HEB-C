# 3×4 memory pilot P4 (run 41053502633): admission values measured

**Outcome: `PILOT_PASS` (all gates).** This is the first pilot run under
[`MEMORY-PILOT-SPEC.md`](MEMORY-PILOT-SPEC.md), and it measured both values the admission rule
needs. The decision for the earlier pilot, [`PILOT-ADMISSION-DECISION.md`](PILOT-ADMISSION-DECISION.md),
stays as it was: that run measured no memory.

| item | value |
|---|---|
| run | 41053502633, `workflow_dispatch`, conclusion `success`, runner exit 0 |
| commit | `6c34c35bab4aae9e2890c07ec6b14d3cd71ffb6a` (an ancestor of `main`) |
| sealed receipt | `p4-41053502633/HEBC-YM-3X4-MEMORY-PILOT.hbp`, SHA-256 `72de6ee4cdebeea76ef8f2b4b1572a416f8b62154960bbea11650d975896a271` (`sha256sum -c` passes) |
| host | ubuntu24 hosted runner, 4 × AMD EPYC 7763, MemTotal 16,367,524 kB, dedicated cgroup v2 |
| sector | 3×4 Sx+Sy+, n = 45,508,080, 3,356,267,422 rooms, payload 26,850,881,536 B, merkle `ec03c5f8…2a0b` |

All five source files the receipt pins (the spec, the workflow, `memory_pilot_runner.py`,
`roomschur.rs`, `ymroom.rs`) have the same SHA-256 on `main` as in the receipt.

## Measured values (integers, bytes)

| K | peak P | bound | within | seconds |
|---|---|---|---|---|
| 1 | 1,881,739,264 | 2,956,984,320 | 1 | 346 |
| 2 | 2,770,747,392 | 3,846,176,768 | 1 | 1,026 |
| 4 | 4,227,149,824 | 5,624,561,664 | 1 | 1,188 |

No OOM kills. Column 0's SCOL output has the same SHA-256 (`c867f9c9…`) at K = 1, 2 and 4.

- **`COL_BYTES` = 889,192,448** (848 MiB): the measured per-block value, which is larger than the declared 728,129,280.
- **`RESERVE` = 2,067,791,872** (1,972 MiB): the declared 2,067,157,872 rounded up to whole MiB. It is larger than the measured idle value of 993,001,472.
- **`CAP` = ⌊(12,884,901,888 − 2,067,791,872) / 889,192,448⌋ = 12.** Recomputed here: (12,884,901,888 − 2,067,791,872) // 889,192,448 = 12.

Build times on the runner: pass A 1,315 s, pass B 14,852 s.

## What this does and does not change

- The admission values are now measured, so `PRODUCTION-ADMISSION.md`'s condition "the HOLD
  stands until a run under it ends `PILOT_PASS`" is met.
- **Production is still not started.** Starting it needs a frozen production spec and
  separate operator direction. No gap verdict exists for 3×4.
- These values are for `roomschur` at the pinned sha. `roomjump` (J2, local) printed its own
  admission row (`COL_BYTES=1092193920`, `RESERVE=2201375600`, CAP 6 at a 9 GB budget). A
  production run on `roomjump` needs its own measurement, or must use the larger of the two.
