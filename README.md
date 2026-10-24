# Finite-universe Yang–Mills experiments using HEB-C HTTP-0

**Canonical executable: [native/](native/)** · **[Stage 2 audited results](STAGE2_SCALING_SPECTRAL_AUDIT_2026-10-24.md)** · **[Architecture and research plan](HEBC_HTTP0_HEADLESS_YANG_MILLS_PLAN.md)** · **[CI Rust 1.81 tests](../../actions/workflows/native-rust.yml)**

This repository builds a **headless, integer-only Rust 1.81** HEB-C kernel with virtual HTTP-0 addresses, HBI/HBP/SHA/SH/HASH integrity receipts, and the first small finite non-Abelian gauge-field model. There is **no JavaScript, Node, V8, JSON, or float arithmetic in the native engine**. The original browser/Clasy X3 demonstrator is superseded; its code is retained in earlier Git history, not the active root.

## Current implemented and checked

- A **2D periodic S3 finite-group gauge-link lattice** with exact group multiplication/inversion, plaquette holonomies, integer Wilson-character action, local gauge transformations, and a toy gauge-equivariant update.
- A six-vertex, all-transpositions **S3 Cayley graph** with independently checkable integer eigenvectors and the exact spectrum \`0,3,3,3,3,6\` (**finite-graph gap 3**). This is *not* a 4D quantum Yang–Mills mass-gap calculation.
- Deterministic 243-step **headless native Rust** run with independent gauge invariance/equivariance tests and exact replay.
- **23,000,000,000 virtual Q-trit address slots**, with 8,192 actual arithmetic probes per step: 1,990,656 operations. No 23 billion allocated states, sockets, particles, or quantum amplitudes.
- SHA-256 implemented in safe Rust and checked against standard known vectors; indexed HBP/HBI records, a chain hash and an anchor. **Receipt integrity is not proof of scientific provenance**, and an anchor must be pinned independently to make tampering externally detectable.
- Optional localhost HTTP/1.1 text adapter for virtual addresses (the HTTP-0 *kernel* is an internal abstraction, not a new standard HTTP wire version).

## Stage 2: measured, checked

- **19/19 Rust unit tests**, zero-warning Clippy, and a validated 3x3 single-plaquette interacting Hamiltonian with exact rational Sturm spectral enclosures.
- **Gauss-law invariant dimensions:** 3 (one open plaquette), 11 (two), 1,393 (periodic 2x2 torus). The latter two are **Hilbert-space dimension counts only**; their interacting Hamiltonians are pending.
- **512x512 headless engineering stress:** 524,288 gauge links, **1,048,576 canonically encoded Q-trits**, 3 exact toy-model steps, receipt verification and identical replay. Large-lattice classical state processing is not the same computation as a many-body quantum spectrum.
- **[Reproducible Stage 2 report](STAGE2_SCALING_SPECTRAL_AUDIT_2026-10-24.md)** · **[Passing GitHub Actions run](../../actions/runs/40126662720)**

## Reproduce

\`\`\`sh
cd native
cargo +1.81.0 test --all-targets --offline
cargo +1.81.0 clippy --all-targets --offline -- -D warnings
cargo +1.81.0 build --release --offline
./target/release/hebc gap
./target/release/hebc sector single
./target/release/hebc sector double
./target/release/hebc sector torus2
./target/release/hebc spectrum 1 1
./target/release/hebc run 3 512 0 stress-512
./target/release/hebc verify stress-512
./target/release/hebc run 243 4 8192 evidence-native
./target/release/hebc verify evidence-native
./target/release/hebc serve 5088
\`\`\`

On Windows use \`target\release\hebc.exe\`.

Read the source-specific instructions at [native/README.md](native/README.md), and the larger research obligations in [HEBC_HTTP0_HEADLESS_YANG_MILLS_PLAN.md](HEBC_HTTP0_HEADLESS_YANG_MILLS_PLAN.md).

## Correct scientific scope

The Clay Yang–Mills existence and mass-gap problem concerns construction of a mathematically controlled *four-dimensional quantum field theory* for a compact simple gauge group, with a strictly positive mass gap. A finite S3 graph eigenvalue gap, a classical gauge-covariant toy state update, and a zero-allocation virtual namespace **do not constitute that proof**.

Existing [Clasy X3](https://github.com/JesseBrown1980/Clasy-repo-x-3-) results concern a separate exact 81-mode finite-field invariant; [Host8](https://github.com/JesseBrown1980/finite-reversible-ternary-physics) studies an independently scoped D3Q27 ternary lattice. The projects can exchange address/receipt interfaces, but their different physics kernels must not be assumed mathematically equivalent.
