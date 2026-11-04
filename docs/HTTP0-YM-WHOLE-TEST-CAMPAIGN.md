# HTTP-0 measured Yang–Mills test campaign — 2026-11-04

**Purpose:** run the existing *mathematical computations* through both native command-line and Yang–Mills HTTP-0 execution, and separately test the newer HEB-C HTTP-0 `3^16` certificate namespace, recording timing and byte equality.

## Two HTTP-0 layers

The newer HEB-C HTTP-0 portal provides **43,046,721 virtual ternary addresses** with **732 populated observations/receipts** (729 Clay/Taylor–Green values and 3 Yang–Mills records). This is a sparse integrity-indexing service: it reads and checks stored records.

The established `native/ym/backend` HTTP-0 execution layer runs the finite Yang–Mills tools. It invokes the same `ymsec`, `flatcomp`, `cluster`, `shellschur` etc. as the direct CLI. Its `verify` command **re-executes** the job with the same binary and compares full canonical `run.hbp`, `index.hbi`, and `run.anchor`. Speed can come from independent-job parallelism, one shared build and fewer repeated downloads, CONJECTURE until a run measures it.

## Tests launched by PR #111

The [measured HTTP-0 campaign workflow](../.github/workflows/http0-ym-full-suite.yml) triggers alongside the existing [native Rust full regression](../.github/workflows/native-rust.yml) and [all eleven cloud-seat result replays](../.github/workflows/hebc-ym-cloud-replay.yml).

| Lane | Computation or verification | Scope |
|---|---|---|
| Build/unit | Rust 1.81 `cargo test --workspace --all-targets`, Clippy zero warnings, release binary build | Tests every Rust member of `native/ym`; one shared build is transferred to all HTTP-0 lanes |
| Five concurrent native sectors | All four S₃ character sectors of the finite 2×2 lattice, plus a mixed-coupling spectral count | Each is calculated by direct CLI and via HTTP-0, then **recomputed on both routes** with the same binary, and all three canonical files compared byte-for-byte |
| Original cloud replays | Eleven pinned cloud result packages `zbell`, `zcalib`, `zconf`, `zconfcert`, `zcurve`, `zcutoff`, `zgap2`, `zlevel`, `zlight`, `zteleport`, `zwilson` | Original prediction seals, SHA-256, Rust replay and preserved FAIL/OPEN outcomes; runs in separate GitHub jobs |
| New HTTP-0 portal | Rust endpoint tests of the **3^16** Yang–Mills certificate domain, separately implemented Python hash/Git-object audit, tamper controls | Checks that the three 3×4 source records match their pinned bytes and recorded fields |
| Existing required gates | YM native-integer-gauge, no-float, no-float-base, compiled no-float, integer tools | Keep operator's existing required checks and exception controls unchanged |

For every direct-versus-HTTP-0 finite sector/count lane, the measured script records `cli_secs` and `http0_secs` from the **same GitHub runner**, plus a canonical byte comparison. The two measurements are sequential and may be affected by warm page caches. Speed stays OPEN from a single run.

## Results, [run 41858273610](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41858273610) at `d400da6`

PR #111 read 27 of 27 checks passing. Rows from the run's logs:

| Lane | `cli_secs` | `http0_secs` | Canonical files | Re-execution and route |
|---|---:|---:|---|---|
| `sector/2/2/1/1` | 0 | 1 | byte-identical | PASS |
| `sector/2/2/1/-1` | 0 | 0 | byte-identical | PASS |
| `sector/2/2/-1/1` | 0 | 1 | byte-identical | PASS |
| `sector/2/2/-1/-1` | 0 | 0 | byte-identical | PASS |
| `count/2/2/1/1/1/27/64000/15/10`, two jobs | 0 | 1 | byte-identical | PASS |

The clock counts whole seconds, so every timing here is inside its resolution. Workspace tests took 295 s and the shared optimized build 28 s. The campaign's last row reads `unit=success`, `route=success`, `source=success`, `full_3x4_hamiltonian_rebuild=NOT_RUN`, `full_3x4_weighted_pairs_recheck=NOT_RUN`.

## The 3×4 runs stay as recorded

The complete 3×4 **45,508,080 Hamiltonian row reconstruction** and **1,632,625,631 weighted-pair check** use an approximately **27.2 GB sector store**; the existing controlled 3×4 fan-out downloads 34 SHA-256-pinned sectors. The source-audit job reads the three HBP summary receipts.

Those heavy jobs must be run on sufficiently provisioned storage/CPU using the registered Hamiltonian definitions, independent checker code, pinned store and fail-closed controls. The existing [3×4 fan-out](../.github/workflows/hebc-ym-3x4-fanout.yml) also has an explicit operator-approved production threshold/control gate, which stays in force.

**A new full 3×4 recomputation: OPEN. The recorded runs stand as the source record.** Perron source `gap_verdict=OPEN` remains OPEN.

## Acceptance rules

- Treat any missing job, timeout, unexpected output, hash mismatch, or failed control as **FAIL**. No replacement values, synthetic sectors, unregistered code edits or relaxed tests.
- Report actual `cli_secs` and `http0_secs` before claiming a speedup. The loopback wrapper runs the same executable.
- Preserve the source SHA-256 pins and the `3^16` sparse address noncollision between Yang–Mills and Clay/Taylor–Green.
- For this PR, merging is conditional on every required workflow and the new measured campaign. A green source-index check covers the three receipts.

[Measured route script](../native/ym/scripts/http0_full_tests.sh) · [All eleven cloud replays](../.github/workflows/hebc-ym-cloud-replay.yml) · [3×4 original records](../native/ym/results/3x4_stream/perron/PERRON-RESULT.hbp)
