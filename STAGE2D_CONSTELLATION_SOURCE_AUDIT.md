# Stage 2D — Original Asolaria Constellation contract inside HEB-C

**Date:** 2026-10-24  
**Code:** `native/src/constellation_gate.rs`  
**Original source (vendored byte-for-byte):** `native/vendor/constellation_lattice/oscillator.rs` and `trit.rs`  
**Original owner:** [Clasy X3](https://github.com/JesseBrown1980/Clasy-repo-x-3-/tree/63cbf283b900457f8dfc59ac0e42d3efcbc9aedb) at full commit `63cbf283b900457f8dfc59ac0e42d3efcbc9aedb`.

### Why this integration

Constellation already has a local **three-direction** transition lattice; do not invent a new nine-cat engine or replace the source implementation. The canonical code defines:

- Three balanced ternary directions, with distinct `NegativeZero=-1`, `CenterZero=0`, `PositiveZero=+1`.
- Five representation edges: Null↔First occupancy, First↔Binary, Binary↔Triad, Triad↔Glyph27, Glyph27↔Binary commit.
- All three transition directions at **each** edge and each sector, not one global forward pass followed by a reversal.
- A local involution on transition keys; all six original **role bindings** receive the identical transition key (`Fischer`, `Mtp`, `Hrm`, `Mcp`, `QuantCatalog`, `EngineCatalog`).
- Existing sector-width levels **3, 27, 243**. Exact local-key counts are **45, 405, 3,645**; barriers advance only on completed levels. The original source `advance_completed_barrier` multiplies sector count by **nine**, not simply three, on each outer barrier (`3→27→243`). The threefold inner directions and the outer barrier's ninefold growth must not be confused.
- Separate source documentation mentions a constellation contract with **9, 81 and 729 worker roles**; *this bridge does not claim those are instantiated as services*. Role *types* per key (six) are different from the numbers in the worker constellation specification.

The exact upstream source files were preserved and compiled directly in the native Rust crate via `#[path]`. Existing `Clasy`, `S3`, `torus2` and receipt implementations remain in place.

### What was actually verified

The independent audit calls the **original** `level_transition_keys`, `bind_roles`, and `advance_completed_barrier` functions. It checks all 4,095 exact local keys, inverse/hold coverage, unchanged six-role bindings and rejection of partially completed barriers.

The torus overlay is a **deliberately narrow address-index experiment**: from each of the 1,393 existing gauge-invariant S3 torus orbit representatives, derive the canonical residual-conjugation orbit key and assign its label to one of the original 243 sectors by `canonical_key % 243`. Check that this *index label* is unchanged under every local gauge transformation on each representative. This is **not** a proof that Constellation contains the Yang–Mills Hamiltonian; it is not an invertible encoding of all 1,393 orbit states into 243 addresses and cannot preserve the spectrum without additional information. Many orbit states share the same label.

The audit records:

```text
scope=source_transition_and_observer_index_only
sectors=3,27,243
key_counts=45,405,3645
torus_basis=1393
c1_binding=UNVERIFIED
z_instant_binding=UNVERIFIED
shadow_cat_torus_binding=UNVERIFIED
physics_gap_inference=NONE
```

**C1**, **Z-instant** and the connecting **Shadow Cat torus residual law** have **not** been assigned formulas or implementation stubs. The supplied dictionary/Book of Laws terminology is respected: until a matching source-defined operator is identified, the audit fails closed to *scientific claims about their integration*.

### HBI / HBP / SHA / SH / HASH

The pinned original source bytes, all local transition keys, and the gauge-invariant torus-address projection have separately computed SHA-256 commitments. The plain-text HBP contains the scope, source commit, original Git blobs, SHA-256 digest, SH first-16-hex locator, key counts and hashes, torus orbit count, projection hash and explicitly unverified bindings. HBI contains byte offset/size, row SHA and chain. An anchor commits to the HBP/HBI roots. Re-running the verifier rebuilds the **entire** key enumeration and all torus gauge label checks, then compares all receipt bytes. Tampering the index or body must fail.

The anchor is a **self-contained hash commitment**, not an authenticated external signature. This does not imply communication between independent physical machines or a continuum Yang–Mills proof.

### Reproduce natively

```bash
cd native
cargo +1.81.0 test --all-targets --locked --offline
cargo +1.81.0 clippy --all-targets --locked --offline -- -D warnings
cargo +1.81.0 build --release --locked --offline
target/release/hebc constellation-audit constellation-evidence
target/release/hebc constellation-verify constellation-evidence
```

Generated files: `constellation-evidence/run.hbp`, `index.hbi`, `run.anchor`, `run.measure`. They are reproducible (hashes and bytes deterministic), no floating point, no JSON serialization, no JS/Node/V8 and no display required.

### Next hurdle before connecting the physics

Find the *canonical executable* C1 and Z-instant dictionary entries and the existing Constellation linkage implementation. Pin them by source commit and preserve all original bytes. Then test against the same 1,393 gauge-invariant torus classes: is there a **well-defined gauge-compatible map** from each Shadow Cat torus and residual to a physical observable? Can it preserve the electric/magnetic operator or spectral bounds? Test missing-view counterexamples and Shannon information accounting. Only after passing those gates is it legitimate to say the Shadow Cat residual mechanism has been integrated into the finite Yang–Mills calculation.
