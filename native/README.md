## Stage 2C: periodic 2×2 torus now has an actual 1,393D sparse Hamiltonian

**[Reproducible Stage 2C mathematical report](../STAGE2C_TORUS_1393_SPARSE_REPORT.md)** · **[Rust 1.81 implementation](src/torus2.rs)** · **[CI](.github/workflows/native-rust.yml)**

The periodic torus is now an **eight-link, four-face interacting finite S₃ operator**, exactly projected to **1,393 gauge-invariant orbit-value states** (from 1,679,616 raw configurations). The sparse electric matrix contains **32,385 nonzero entries** and is verified for weighted self-adjointness, gauge invariance and reproducible SHA-committed HBI/HBP records.

The exact electric-only gap is **6×J_E**. Magnetic-only coupling gives **eight degenerate flat-connection ground states** and hence **gap zero**. With both couplings positive, a connected stoquastic electric graph establishes unique ground state and therefore a **qualitatively positive** finite-volume gap. **Mixed-coupling numerical eigenvalue bounds remain uncomputed**, so Issue #2 stays open.

To reproduce from the native directory: *cargo +1.81.0 run --release --offline --locked -- torus2-spectrum 1 1 torus2-evidence*, then *cargo +1.81.0 run --release --offline --locked -- torus2-verify torus2-evidence*.

## Stage 2B milestone — full interacting double-plaquette spectrum

**[Exact 11D two-plaquette Hamiltonian report](../STAGE2B_DOUBLE_PLAQUETTE_EXACT_SPECTRUM.md)** · **[Rust-native implementation](src/double_plaquette.rs)** · **[Reproducible CI](../.github/workflows/native-rust.yml)**

The active Rust 1.81 engine now constructs the coupled **seven-link, two-plaquette finite S₃ Hamiltonian** from all **279,936** raw configurations and independently verifies the reduction to **11** gauge-invariant orbit states. Unlike the earlier 11-dimensional sector count, this now includes the *actual gauge-invariant electric and magnetic operators* with exact weighted self-adjointness, integer-only Sturm spectral enclosures, and an independent signed-determinant cross-check.

For `J_E=J_B=1`, the double-plaquette interacting excitation gap is **strictly between 10 and 12** lattice-energy units. The `J_E=J_B=0` control is correctly not certified as gapped. The finite 2×2 torus **1,393D Hamiltonian is still outstanding**, and neither finite model proves a 4D continuum Yang–Mills gap.

```bash
cargo +1.81.0 run --release --locked --offline -- double-spectrum 1 1 double-1-1
cargo +1.81.0 run --release --locked --offline -- double-verify double-1-1
```

## Clasy X3 integration: separate 81-mode finite-field kernel

The pinned upstream [Clasy X3](https://github.com/JesseBrown1980/Clasy-repo-x-3-/tree/63cbf283b900457f8dfc59ac0e42d3efcbc9aedb) is available as `vendor/clasy_x3/` with an offline path-only Cargo dependency. The adapter in `src/clasy_portal.rs` reconstructs 3 canonical Host8 room stubs per requested virtual HTTP-0 kernel ID, runs the original 81-mode Clasy evolution, independently checks its finite-field drift invariant and transform roundtrip, and writes indexed HBP/HBI/SHA-chain receipts with a verifier that re-executes the trajectory.

```sh
cargo +1.81.0 run --release --offline --locked -- clasy-run 0 1 243 clasy-single
cargo +1.81.0 run --release --offline --locked -- clasy-verify clasy-single
cargo +1.81.0 run --release --offline --locked -- clasy-batch 81 243 clasy-batch-81
cargo +1.81.0 run --release --offline --locked -- clasy-batch 243 81 clasy-batch-243
cargo +1.81.0 run --release --offline --locked -- serve 5088
```

HTTP/1.1 text endpoints: `/clasy/3/1/9` and `/spectrum/1/1`. The internal *HTTP-0* namespace is a computational addressing abstraction, not a wire protocol or 23 billion instantiated services. Clasy shell amplitudes are *not* Yang–Mills gauge field variables. The next mathematical hurdle is the interacting double-plaquette 11-dimensional Hamiltonian; see [the guide](../CLASY_X3_TO_HEBC_HTTP0_NEXT_HURDLES.md).


# Native HEB-C finite gauge kernel — Rust 1.81

Canonical no-screen engine. Rust standard library only, no external dependencies, no network for computation, no JavaScript, V8, Node or JSON and no floating-point numeric operations.

Quick start:

\`\`\`sh
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
./target/release/hebc cache-demo 243 4
./target/release/hebc address 123
./target/release/hebc clasy-run 0 1 243 clasy-evidence
./target/release/hebc clasy-verify clasy-evidence
./target/release/hebc clasy-batch 81 243 clasy-batch
./target/release/hebc serve 5088
\`\`\`

On Windows use \`target\release\hebc.exe\` rather than \`./target/release/hebc\`.

**The model:** S3 non-Abelian six-element finite group, oriented links on a *two-dimensional* periodic finite lattice, exact local gauge transformations and gauge-invariant integer plaquette action \`sum(2 - character_2(P))\`. The \`advance\` operation is a mathematically gauge-equivariant **toy** deterministic link rule, not a quantum field Hamiltonian or invertible quantum unitary. The graph-gap certificate checks the six-vertex S3 central Cayley Laplacian generated by three transpositions; its exact spectrum is \`0,3,3,3,3,6\`, hence positive **finite graph** gap 3, *not* a measured physical Yang–Mills excitation mass or the Clay continuum conjecture.

**Q-trits:** \`-1/0/+1\` are virtual discrete values. They are not arbitrary coherent quantum qutrit amplitudes. There are 23,000,000,000 addressable *identifiers*, not that many instantiated executing kernels, states, sockets, or particles. Only requested probes are actually evaluated.

**Receipt chain:** \`run.hbp\` contains one record per model transition; \`index.hbi\` gives exact seek offsets, \`run.anchor\` pins the HBP/HBI digests and final chain hash, and \`run.measure\` is plain text metrics. A SHA-256 digest is an integrity fingerprint, *not* a compressed reversible state or proof of experimental provenance. The anchor needs independent pinning outside the same directory for external provenance. The \`verify\` command checks recorded bytes; unit tests and deterministic replay execute separate checks.

**HTTP-0:** internal name for the address/kernel abstraction, not an HTTP wire-protocol version. The optional loopback adapter offers read-only \`/health\`, \`/gap\` and \`/qtrit/{ordinal}\` over ordinary HTTP/1.1. Nothing is displayed and native \`run\` needs no TCP connection.

**Benchmarking:** simulation transitions are self-stepping counters. Performance uses the integer nanosecond duration of an independent wall-clock instrument for comparison; the timer does not determine state updates. A disk-free kernel is not thereby proven faster than an optimally cached native in-memory kernel. The physical 300 GB Host8 substrate is not accessed here.

Stage 2 audited spectral and scale results: [report](../STAGE2_SCALING_SPECTRAL_AUDIT_2026-10-24.md). Interacting finite gauge Hamiltonian is currently solved only for the single square (3-dimensional Gauss-invariant basis); larger physical sector dimensions are enumerated but not diagonalized.

**Clasy X3 81-shell integration:** [CLASY_X3_PINNED_REFERENCE.md](../CLASY_X3_PINNED_REFERENCE.md) and [CLASY_X3_CONTINUUM_HURDLES_GUIDE.md](../CLASY_X3_CONTINUUM_HURDLES_GUIDE.md).

See [implementation and research plan](../HEBC_HTTP0_HEADLESS_YANG_MILLS_PLAN.md).
