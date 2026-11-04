# HTTP-0 measured Yang–Mills test campaign — 2026-11-04

**Purpose:** run the existing *mathematical computations* through both native command-line and Yang–Mills HTTP-0 execution, and separately test the newer HEB-C HTTP-0 `3^16` certificate namespace. Record timing and byte equality rather than assuming a throughput improvement.

## Why this distinction matters

The newer HEB-C HTTP-0 portal provides **43,046,721 virtual ternary addresses** with **732 populated observations/receipts** (729 Clay/Taylor–Green values and 3 Yang–Mills records). This is a sparse integrity-indexing service. It does **not** calculate 43 million new eigenvalues, accelerate a 45.5-million-row Hamiltonian rebuild, or provide extra compute cores.

The established `native/ym/backend` HTTP-0 execution layer **does run real** finite Yang–Mills tools. It invokes the *same* `ymsec`, `flatcomp`, `cluster`, `shellschur` etc. as the direct CLI. Its `verify` command intentionally **re-executes** the job and compares full canonical `run.hbp`, `index.hbi`, and `run.anchor`. Speed improvements therefore come primarily from independent-job parallelism, one shared build, and avoiding unnecessary repeated downloads, **not** from the virtual address count.

## Tests actually launched by the new PR

The [measured HTTP-0 campaign workflow](../.github/workflows/http0-ym-full-suite.yml) triggers alongside the existing [native Rust full regression](../.github/workflows/native-rust.yml) and [all eleven cloud-seat result replays](../.github/workflows/hebc-ym-cloud-replay.yml).

| Lane | Computation or verification | Independence and scope |
|---|---|---|
| Build/unit | Rust 1.81 `cargo test --workspace --all-targets`, Clippy zero warnings, release binary build | Tests every Rust member of `native/ym`; one shared build is transferred to all HTTP-0 lanes |
| Five concurrent native sectors | All four S₃ character sectors of the finite 2×2 lattice, plus a mixed-coupling spectral count | Each is genuinely calculated by direct CLI and via HTTP-0, then independently **recomputed on both routes** and all three canonical files compared byte-for-byte |
| Original cloud replays | Eleven pinned cloud result packages `zbell`, `zcalib`, `zconf`, `zconfcert`, `zcurve`, `zcutoff`, `zgap2`, `zlevel`, `zlight`, `zteleport`, `zwilson` | Original prediction seals, SHA-256, Rust replay and preserved FAIL/OPEN outcomes; runs in separate GitHub jobs |
| New HTTP-0 portal | Rust endpoint tests of the **3^16** Yang–Mills certificate domain, independent Python hash/Git-object audit, tamper controls | Verifies that original 3×4 source records are authentic. **Does not recompute** their 45.5M rows or all-pairs scan |
| Existing required gates | YM native-integer-gauge, no-float, no-float-base, compiled no-float, integer tools | Keep operator's existing required checks and exception controls unchanged |

For every direct-versus-HTTP-0 finite sector/count lane, the measured script records `cli_secs` and `http0_secs` from the **same GitHub runner**, plus a canonical byte comparison. The two measurements are sequential and may be affected by warm page caches. A single run is not enough to establish a reproducible throughput advantage.

## What these tests do *not* rerun

The complete 3×4 **45,508,080 Hamiltonian row reconstruction** and **1,632,625,631 weighted-pair check** use an approximately **27.2 GB sector store**; the existing controlled 3×4 fan-out downloads 34 SHA-256-pinned sectors. The source-audit job only reads the three HBP summary receipts. It is a category error to label that source-audit check as a whole-store recalculation.

Those heavy jobs must be run on sufficiently provisioned storage/CPU using the registered Hamiltonian definitions, independent checker code, pinned store and fail-closed controls. The existing [3×4 fan-out](../.github/workflows/hebc-ym-3x4-fanout.yml) also has an explicit operator-approved production threshold/control gate, which this PR does not bypass.

**Until new complete 3×4 runtime receipts appear, its independent full recomputation status remains HISTORICAL SOURCE RECORD — NOT_RERUN_IN_THIS_CAMPAIGN.** Perron source `gap_verdict=OPEN` remains OPEN.

## Acceptance rules

- Treat any missing job, timeout, unexpected output, hash mismatch, or failed control as **FAIL**. No replacement values, synthetic sectors, unregistered code edits or relaxed tests.
- Report actual `cli_secs` and `http0_secs` before claiming a speedup. A loopback HTTP wrapper should not be expected to beat the same executable on raw CPU time.
- Preserve the independent source SHA-256 pins and the `3^16` sparse address noncollision between Yang–Mills and Clay/Taylor–Green.
- For this PR, merging is conditional on every required workflow and the new measured campaign; do not equate a green source-index check with completed 3×4 full-row mathematics.

[Measured route script](../native/ym/scripts/http0_full_tests.sh) · [All eleven cloud replays](../.github/workflows/hebc-ym-cloud-replay.yml) · [3×4 original records](../native/ym/results/3x4_stream/perron/PERRON-RESULT.hbp)
