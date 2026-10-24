## Stage 2C: periodic 2×2 torus now has an actual 1,393D sparse Hamiltonian

**[Reproducible Stage 2C mathematical report](STAGE2C_TORUS_1393_SPARSE_REPORT.md)** · **[Rust 1.81 implementation](native/src/torus2.rs)** · **[CI](.github/workflows/native-rust.yml)**

The periodic torus is now an **eight-link, four-face interacting finite S₃ operator**, exactly projected to **1,393 gauge-invariant orbit-value states** (from 1,679,616 raw configurations). The sparse electric matrix contains **32,385 nonzero entries** and is verified for weighted self-adjointness, gauge invariance and reproducible SHA-committed HBI/HBP records.

The exact electric-only gap is **6×J_E**. Magnetic-only coupling gives **eight degenerate flat-connection ground states** and hence **gap zero**. With both couplings positive, a connected stoquastic electric graph establishes unique ground state and therefore a **qualitatively positive** finite-volume gap. **Mixed-coupling numerical eigenvalue bounds remain uncomputed**, so Issue #2 stays open.

To reproduce from the native directory: *cargo +1.81.0 run --release --offline --locked -- torus2-spectrum 1 1 torus2-evidence*, then *cargo +1.81.0 run --release --offline --locked -- torus2-verify torus2-evidence*.

## Implemented Stage 2B: interacting two-plaquette operator

**Milestone passed:** [full 11D Hamiltonian and independent integer spectral audit](STAGE2B_DOUBLE_PLAQUETTE_EXACT_SPECTRUM.md). The original next hurdle (Gauss-projected electric and magnetic Hamiltonian on a shared seven-link two-plaquette geometry) is now implemented and tested. The next **open** finite-volume milestone is the 1,393-dimensional torus Hamiltonian and size/coupling spectral comparison. Clasy X3 remains a distinct 81-mode finite-field kernel and does not replace this gauge-Hamiltonian calculation.

## Clasy X3 as an exact-integer verification precedent — implementation added

- Pinned source: [Clasy X3 commit `63cbf28`](https://github.com/JesseBrown1980/Clasy-repo-x-3-/tree/63cbf283b900457f8dfc59ac0e42d3efcbc9aedb), preserved under `native/vendor/clasy_x3/`; its finite-field law `Q(u_t)+t nu D81=Q(u_0) (mod 1,000,999)` is independently checked for 81 shell modes.
- Native headless HTTP-0 address dispatch is in `native/src/clasy_portal.rs`; it regenerates 3 source room identities using the original Host8 integer codec, applies exactly 81-mode Clasy update, and writes/checks HBP/HBI state hashes and chained anchor receipts.
- CI separately verifies 81 × 243 and 243 × 81 *actually executed* finite-shell transitions, and the independent 3×3 single-plaquette S3 Hamiltonian spectrum calculation; the S3 spectral calculation is not a 243-step simulation and is independent of Clasy's finite-field evolution.
- [Complete bridge plan and outstanding multi-plaquette hurdles](CLASY_X3_TO_HEBC_HTTP0_NEXT_HURDLES.md).

**The Clasy model does not constitute a Yang–Mills continuum limit, and the 11-dimensional/toroidal interacting Hamiltonians remain unimplemented.**


# HEB-C / HTTP-0: headless finite-universe Yang–Mills implementation plan

Status: implementation roadmap, not a continuum Yang–Mills existence/mass-gap proof. Date: 2026-10-24.

## Canonical execution contract

- **Rust 1.81.0** with \`cargo clippy --all-targets -- -D warnings\`; no unsafe.
- Integer-only mathematics (no floating-point physics or floats in the native code).
- **Zero Node.js, V8, JavaScript or JSON in the native engine.** Historical \`index.html\` is an archived, noncanonical prototype. Screens are optional, and there is no display pipeline in the core kernel.
- **HTTP-0** names a *virtual addressing and kernel-dispatch abstraction*, not a claim about an official wire protocol. Optional loopback transport uses an ordinary, explicitly identified HTTP/1.1 endpoint for compatibility.
- **Q-trit** names a three-valued discrete computational variable \`{-1, 0, +1}\`, not an arbitrary quantum qutrit state.
- Configurable logical kernel namespace: e.g. 23,000,000,000 addresses calculated as \`(ordinal * 1_000_003) mod 23_000_000_000\`. Only active states or cached results use memory; unallocated labels do not run computations.
- Native headless first. Do not wait for screens; do not read or write the 300 GB Host8 source in the simulation critical loop.
- Receipt chain: **HBI** seek offsets → **HBP** recorded observations → **SHA-256** input/record digest → **SH** short locator → **HASH** previous-digest chain → external *pinned* anchor. The chain authenticates the bytes relative to its root, but does not by itself establish experiment provenance or correctness.
- Cache keyed by kernel specification + initial state + step count + executable/code version + exact output digest. A bare SHA-256 digest cannot reconstruct arbitrary missing states; a deterministic rule plus a seed can.
- Wall-clock-free state updates: steps counted by transitions; use integer nanosecond durations only for benchmarking.

## Scientific stages

**Stage 1 — finite, non-Abelian prototype (this milestone):**
- Finite gauge group \`S3\` as a deliberately small *non-Abelian* reference, with 2D periodic oriented link variables.
- Exact integer link composition and inversion, local gauge transformations, Wilson-character plaquette observables, and explicitly named **toy gauge-equivariant** update rule.
- Exact 6-vertex Cayley-graph Laplacian built from all three transpositions. Eigenvalues \`0,3,3,3,3,6\`, finite graph spectral gap \`3\` in dimensionless lattice units. **This is not a four-dimensional Yang–Mills mass gap.**
- Verify gauge invariance, equivariance, full group tables, SHA vectors, receipt corruption rejection, deterministic replay, and measured virtual address throughput.
- Native executable: offline \`run\`, \`verify\`, \`gap\` and optional read-only loopback \`serve\`.

**Stage 2 — stronger finite-lattice Yang–Mills:**
- Introduce finite non-Abelian *link Hilbert space* and gauge-invariant Gauss-law sector, an explicit self-adjoint Hamiltonian/transfer operator containing electric and magnetic terms, and exact/rational spectral certification for small lattices. Differentiate a graph-kinetic gap from the interacting gauge-invariant Hamiltonian gap.
- Record the source inputs, lattice boundary conditions, coupling, volume, basis/truncation, energy unit, first two eigenvalues, and confidence/rigorous interval in HBP.
- Compare kernel execution against eager allocation, cached replay, disk-backed room streams, and memoized generation for *identical* initial conditions and equivalent physical work. Report work done versus addresses merely representable.
- Reproduce on multiple machines using independent executable hashes and independently re-executed checks.

**Stage 3 — continuum research obligations:**
- To approach the Clay problem one must construct a nontrivial four-dimensional quantum Yang–Mills theory for a compact simple Lie group (e.g. \`SU(2)\`), establish the axioms and gauge-invariant Hilbert space, and prove a **strictly positive, uniform** physical mass gap that survives lattice spacing \`a→0\` and infinite volume with controlled renormalization.
- A finite \`S3\` graph gap, discrete ternary reversibility, modular Clasy X3 conservation law, and an arithmetic 23-billion namespace **do not establish** those obligations.

## Acceptance gates

\`\`\`bash
cd native
cargo +1.81.0 test --all-targets --offline
cargo +1.81.0 clippy --all-targets --offline -- -D warnings
cargo +1.81.0 build --release --offline
cargo +1.81.0 run --release --offline -- run 243 4 8192 evidence
cargo +1.81.0 run --release --offline -- verify evidence
cargo +1.81.0 run --release --offline -- gap
\`\`\`

Do not mark Rust-native, scientific, or CI gates as passing until the corresponding command actually executes. Do not describe a SHA/checksum alone as a fresh re-execution.
