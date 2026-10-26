# HEB-C HTTP-0 backend for the finite S₃ Yang–Mills sector tools

Execution and verification layer for the finite-lattice spectral certificates.

## What is here

| Path | Content |
|---|---|
| `crates/torusl`, `crates/evolvers`, `crates/sturmrs` | Copied from The-matrix-law-essentials `8fd12e6` (`ymsec`, `onfly`, `flatcomp`, `ddcore`, `cluster`, `shellschur`, …). One deliberate change: the `ymsec` size guard now admits lx·ly ≤ 10 (was 9), so 2×5 can be built; the mathematics is untouched. The backend does no mathematics of its own. |
| `backend/` | `hebc_ym_http0`: the HTTP-0 execution and verification layer. |
| `vendor/`, `.cargo/config.toml` | Vendored `num-bigint`/`num-integer`/`num-traits`/`autocfg`, so every build is `--offline --locked`. |
| `python/shell_gap_cert.py`, `python/monotone_cells.py` | Certificate builders, copied; `shell_gap_cert.py` gained only a `--lattice LXxLY` parameter (default output is byte-identical to the original on the 3×3 receipts). |
| `reference/ym3x3_frozen_8fd12e6.hbp` | The **frozen** 3×3 reference: pinned matrix SHA-256s, flatcomp lines and the r = 27 / 243 certificates. New work is compared against it and never edits it. |
| `scripts/route_identity.sh` | Runs the same jobs headless and through the loopback route and compares the canonical bytes. |

## Shards and receipts

One job = one tool run = one disk shard `ROOT/shards/<spec>`:

- `run.hbp` – canonical scientific lines; runtime fields (`ms=`, `elapsed_ms=`) are removed.
- `index.hbi` – per-line offset, length, SHA-256 and a running hash chain.
- `run.anchor` – job spec plus the digests of `run.hbp` and `index.hbi`.
- `run.measure` – runtime metadata only (removed fields, wall time, tool binary SHA-256, exit code). **Never compared.**

`verify` re-executes the job in a fresh staging directory and compares `run.hbp`,
`index.hbi` and `run.anchor` byte for byte. A job reading a sector matrix first
checks the matrix SHA-256 against its `sector` shard. An existing `.inflight-*`
staging directory blocks the job until an operator runs `quarantine`.
`HEBC_YM_FRESH=1` refuses to reuse any existing shard.

The headless command and the HTTP-0 route call the same `job`/`verify` function.

```
hebc_ym_http0 job ROOT SPEC | verify ROOT SPEC | cat ROOT SPEC | quarantine ROOT SPEC
hebc_ym_http0 serve ROOT PORT MAX_REQUESTS     # 127.0.0.1 only
  POST /job/<spec>   GET /verify/<spec>   GET /shard/<spec>   GET /health
specs: sector/LX/LY/SX/SY  flatcomp/LX/LY/SX/SY  cluster/LX/LY/SX/SY/JE/JB/WANT/GUARD
       count/LX/LY/SX/SY/JE/JB/T/FDIG/TOL  countcols/LX/LY/SX/SY/JE/JB/T/FDIG/TOL/A/B
```

## Split Schur columns (large cores)

`countcols` jobs compute disjoint column ranges of the Schur complement and
emit one `SCOL` record per core entry. `countmerge` merges the run.hbp files
placed in `ROOT/scol/<count id>/`. The merge (HEB-C `shellschur`) requires:
- exactly one record for every (row, column) of the core, with duplicates
  and missing entries rejected;
- the same run tag on every record (n, JE, JB, t, shell_max, core size, a
  64-bit fingerprint of the ordered core indices, F).

A merge that passes reproduces the unsplit count (2×2, core 87: 27 = 27; core
662: 135 = 135). The dense interval LDLᵀ of the merged core is the remaining
serial step: 152,908 ms for the 1,137-state 3×3 (+,+) core at r = 9 on a GitHub
runner (sealed receipt, The-matrix-law-essentials).

## Build

```
cd native/ym
cargo +1.81.0 build --release --offline --locked
cargo +1.81.0 clippy --release --all-targets --offline --locked -- -D warnings
scripts/route_identity.sh target/release /tmp/ri 5191 sector/2/2/1/1 count/2/2/1/1/1/27/64000/15/10
```

## Reproducibility and independent verification

The GitRAM regeneration lane (`.github/workflows/hebc-ym-3x3-regenerate.yml`)
rebuilds everything from the same source on fresh machines and compares with
the frozen reference. That establishes **reproducibility**. Stronger confidence
comes from a separately implemented verifier of the same inertia counts, which
is the next item in development.

## Full space from line sectors

On a non-cyclic translation group, the full physical space splits into isotypic
parts, one for each subgroup K with T/K cyclic. The `tx`, `ty`, `td` and `ta`
sector modes build V^K, the states invariant under the translations along one
line, and [`python/full_space_mobius.py`](python/full_space_mobius.py) recovers
every part by Möbius inversion. On the 3×3 lattice the eight nonzero momenta
fall into two orbits of four, {(±1, 0), (0, ±1)} and {(±1, ±1)}. With
`--orbit`, one representative line per orbit is counted, and the symmetric
partner reuses it.

[`scripts/full_space_mobius_check.sh`](scripts/full_space_mobius_check.sh)
runs every job through the HTTP-0 route. It compares the result with the
reflection-only full-space count. On 2×2 at r = 9 the result is 8 = 8 at the
gap thresholds, and 616 = 616 at t = 90.123457 J_E, where 449 of the states
carry nonzero momentum
([`results/full_space_mobius/`](results/full_space_mobius/)).

## N-Nest gate

[`python/nnest_gate.py`](python/nnest_gate.py) arranges a result as a tree of
agent reports and independent watchers:

```text
node_green = (reported == watcher_recomputed) AND all(child_green)
```

| Depth | Node | Watcher |
|---|---|---|
| 0 | full-space count | Möbius sum, plus the reflection-only route |
| 1 | invariant count N(V^K) | sum of its sector counts |
| 2 | count shard | re-execution through HTTP-0, byte compared |
| 3 | sector shard | re-execution through HTTP-0, plus the matrix SHA-256 |

Nodes move through DESCRIBED → EDGE_MINED → PATH_FOUND → CONVERGED or
MISTAKE_FLAGGED, and a failure is reported with its address path. The
controls check four things:
- **C1.** A clean tree is green.
- **C2.** A re-run gives a byte-identical verdict.
- **C3.** Removing one leaf's evidence holds the tree: a fraction of the
  evidence does not certify.
- **C4.** A fault planted at each depth, 3 down to 0, is flagged first at that
  depth.

All four pass on the 2×2 validation
([`2x2_nnest_gate.hbp`](results/full_space_mobius/2x2_nnest_gate.hbp)).
