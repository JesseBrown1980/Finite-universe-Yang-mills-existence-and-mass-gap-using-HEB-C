# Native HEB-C finite gauge kernel — Rust 1.81

The canonical headless engine. It uses the Rust standard library only, integer
arithmetic only, and plain-text receipts. Inside it are the S₃ finite-group
gauge lattice, the exact single-plaquette, two-plaquette and 2×2 torus
Hamiltonians with their certificates, virtual HTTP-0 addressing, and the
vendored Clasy X3 kernel. The sector tools and the HTTP-0 execution backend for
larger lattices are in [`ym/`](ym/README.md).

## Quick start

```sh
cargo +1.81.0 test --all-targets --offline
cargo +1.81.0 clippy --all-targets --offline -- -D warnings
cargo +1.81.0 build --release --offline
./target/release/hebc gap
./target/release/hebc sector torus2
./target/release/hebc spectrum 1 1
./target/release/hebc run 243 4 8192 evidence-native
./target/release/hebc verify evidence-native
./target/release/hebc clasy-run 0 1 243 clasy-evidence
./target/release/hebc clasy-verify clasy-evidence
./target/release/hebc serve 5088
```

On Windows use `target\release\hebc.exe`.

## The 2×2 torus: 1,393 states

- **Stage 2C, the operator** ([report](../STAGE2C_TORUS_1393_SPARSE_REPORT.md),
  [`src/torus2.rs`](src/torus2.rs)). An eight-link, four-face S₃ operator,
  exactly projected from 1,679,616 raw configurations to 1,393 gauge-invariant
  orbit states, with 32,385 nonzeros. It is weighted self-adjoint and gauge
  invariant. Its electric-only gap is 6·J_E, and the magnetic end has 8 flat
  ground states.
- **Stage 2G, rational bounds** ([report](../STAGE2G_TORUS2_RATIONAL_GAP_CERTIFICATE.md),
  [`src/torus2_bounds.rs`](src/torus2_bounds.rs)). Exact-rational E₀, E₁ and gap
  enclosures, with gap lower bounds 0.671034 at (1, 1) and 0.344589 at (3, 5).
  They come from a positive Collatz ground-state witness and a weighted
  orthogonal Wilson trial vector.
- **Stage 2H–2I, tight certificates and an independent verifier**
  ([2H](../STAGE2H_TORUS2_INTEGER_INERTIA_CERTIFICATE.md),
  [2I](../STAGE2I_INDEPENDENT_VERIFIER_AND_SCALING.md),
  [`src/torus2_independent.rs`](src/torus2_independent.rs)).
  - **(1, 1):** E₀ ∈ [7.634198, 7.634199], E₁ ∈ [13.240000, 13.242733], gap ∈ [5.605801, 5.608535].
  - **(3, 5):** E₀ ∈ [36.699227, 36.699228], E₁ ∈ [50.840000, 50.842050], gap ∈ [14.140772, 14.142823].
  - **Scaling:** the vacuum energy is about 1.91 per plaquette at (1, 1) and
    scales extensively across the 3-, 11- and 1,393-state systems.

```sh
cargo +1.81.0 run --release --offline --locked -- torus2-spectrum 1 1 torus2-evidence
cargo +1.81.0 run --release --offline --locked -- torus2-bounds 1 1 torus2-bounds-1-1
cargo +1.81.0 run --release --offline --locked -- torus2-independent 1 1 indep-1-1
cargo +1.81.0 run --release --offline --locked -- torus2-independent-verify 1 1 indep-1-1
cargo +1.81.0 run --release --offline --locked -- torus2-scaling
```

## Stage 2B: the two-plaquette Hamiltonian

[Report](../STAGE2B_DOUBLE_PLAQUETTE_EXACT_SPECTRUM.md),
[`src/double_plaquette.rs`](src/double_plaquette.rs).
- **The operator.** A seven-link, two-plaquette S₃ Hamiltonian built from all
  279,936 raw configurations and reduced to 11 gauge-invariant orbit states.
  It is weighted self-adjoint, with integer Sturm enclosures and a
  signed-determinant cross-check.
- **The gap.** At J_E = J_B = 1 the gap is strictly between 10 and 12.

```sh
cargo +1.81.0 run --release --locked --offline -- double-spectrum 1 1 double-1-1
cargo +1.81.0 run --release --locked --offline -- double-verify double-1-1
```

## Constellation source audit

[Audit](../STAGE2D_CONSTELLATION_SOURCE_AUDIT.md); source pinned in
`vendor/constellation_lattice/`.
- **The original code.** The Clasy Constellation oscillator and trit code is
  compiled byte for byte into the build.
- **What runs.** The audit executes the original 3/27/243 sector transition
  barriers and all 45/405/3,645 local keys, with six role types per key.
- **The index.** A gauge-invariant 243-sector index of the 1,393 torus orbit
  labels is written with HBI/HBP/SHA/SH/HASH receipts.
- **Next bindings.** The C1, Z-instant and Shadow Cat torus residual bindings
  are the next items to source.

```sh
cargo +1.81.0 run --release --offline --locked -- constellation-audit constellation-evidence
cargo +1.81.0 run --release --offline --locked -- constellation-verify constellation-evidence
```

## Clasy X3 kernel

[Clasy X3](https://github.com/JesseBrown1980/Clasy-repo-x-3-/tree/63cbf283b900457f8dfc59ac0e42d3efcbc9aedb)
is vendored at `vendor/clasy_x3/` as an offline path dependency.
`src/clasy_portal.rs` reconstructs three canonical Host8 room stubs per virtual
kernel ID and runs the 81-mode evolution. It checks the finite-field drift
invariant and the transform round trip, and writes HBP/HBI/SHA-chain receipts
whose verifier re-executes the trajectory. Batches of 81 × 243 and 243 × 81
transitions run in CI. Guides: [pinned reference](../CLASY_X3_PINNED_REFERENCE.md),
[continuum guide](../CLASY_X3_CONTINUUM_HURDLES_GUIDE.md),
[roadmap](../CLASY_X3_TO_HEBC_HTTP0_NEXT_HURDLES.md).

```sh
cargo +1.81.0 run --release --offline --locked -- clasy-batch 81 243 clasy-batch-81
cargo +1.81.0 run --release --offline --locked -- clasy-batch 243 81 clasy-batch-243
```

## Kernel details

- **Lattice.** S₃ links on a periodic two-dimensional lattice, with exact
  local gauge transformations and the integer plaquette action
  Σ(2 − χ₂(P)). `advance` is a gauge-equivariant deterministic link rule used
  for replay and stress tests. The six-vertex Cayley Laplacian generated by
  the three transpositions has exact spectrum 0, 3, 3, 3, 3, 6.
- **HTTP-0 addressing.** 23,000,000,000 addressable Q-trit identifiers taking
  values −1/0/+1. Only the requested probes are evaluated. The loopback
  HTTP/1.1 adapter serves `/health`, `/gap`, `/qtrit/{ordinal}`,
  `/clasy/{ordinal}/{nu}/{steps}`, `/spectrum/{JE}/{JB}` and `/constellation`.
- **Receipts.**
  - `run.hbp` holds one record per transition.
  - `index.hbi` gives exact seek offsets.
  - `run.anchor` pins the HBP/HBI digests and the final chain hash.
  - `run.measure` holds plain-text metrics.
  - `verify` checks the recorded bytes, and pinning the anchor externally gives
    outside provenance.
- **Benchmarking.** State updates count transitions. Timing uses integer
  nanoseconds from an independent clock.
- **Stress.** A 512×512 lattice: 524,288 links and 1,048,576 canonically
  encoded Q-trits, with exact steps and identical replay.

Plan: [HEBC_HTTP0_HEADLESS_YANG_MILLS_PLAN.md](../HEBC_HTTP0_HEADLESS_YANG_MILLS_PLAN.md).
Stage 2 audit: [STAGE2_SCALING_SPECTRAL_AUDIT_2026-10-24.md](../STAGE2_SCALING_SPECTRAL_AUDIT_2026-10-24.md).
