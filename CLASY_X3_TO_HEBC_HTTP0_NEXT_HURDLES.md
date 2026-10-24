# Clasy X3 → HEB-C HTTP-0 → finite Yang–Mills: pinned reference, measured integration, and next hurdles

**Updated:** 2026-10-24. **Execution:** Rust 1.81.0, safe code, integer-only arithmetic, Clippy -D warnings, zero JSON serialization, no JavaScript/Node/V8. **Display:** not required.

## Provenance

- Pinned Clasy X3 upstream: [Clasy-repo-x-3-](https://github.com/JesseBrown1980/Clasy-repo-x-3-/tree/63cbf283b900457f8dfc59ac0e42d3efcbc9aedb), commit `63cbf283b900457f8dfc59ac0e42d3efcbc9aedb`.
- Mathematical guide: [X3-PROOF.md](CLASY_X3_PINNED_REFERENCE.md), preserved as a separate historical research reference; do not silently promote finite-shell identities into continuum PDE or Yang–Mills claims.
- Mathematically pinned code: [native/vendor/clasy_x3](native/vendor/clasy_x3) — the original Clasy 81-mode library, Host8 read-only integer identity codec, canonical tribit representation and upstream 27-mode dependency are supplied locally and compiled via a Cargo **path dependency**, requiring no crates.io runtime package.
- Implemented native kernel adapter: [native/src/clasy_portal.rs](native/src/clasy_portal.rs), integrated in [native/src/main.rs](native/src/main.rs).
- The existing [single-plaquette gauge Hamiltonian](native/src/hamiltonian.rs) is a different physical/mathematical model. There is no assumption that 81 finite-field shell amplitudes are SU(2) gauge fields, that Clasy's invariant is a Yang–Mills Ward identity, or that the two operators have the same spectrum.

## Exact Clasy laws reproduced

In Clasy X3, `P=1,000,999`, `K=81`, `W=30,722` (order 81), and the exact total drift `D81=900,647`:

```text
NL[n] = u[n] * (u[n+1] - u[n-1]) (mod P)  for 1 <= n <= 79
NL[0] = -floor(S / 2); NL[80] = -S + floor(S / 2), S=sum interior NL (mod P)
Q(u) = sum_n u[n] (mod P)
Q(u[t]) + t * nu * D81 = Q(u[0]) (mod P)
prism81(NL)[0] = 0
unprism81(prism81(u)) = u
```

This is a valid exact finite-field shell identity, not a statement about 4D interacting quantum gauge mass gaps. The update itself is **not injective** (see the explicit counterexample in Clasy X3's pinned proof); invertibility of the number-theoretic transform does not make the evolution time-reversible.

## Real HTTP-0 architecture now implemented (headless default)

This project uses **HTTP-0 as the name of an internal virtual address / dispatch kernel**, not an invented wire-level HTTP protocol. `/clasy/{ordinal}/{nu}/{steps}` and `/spectrum/{JE}/{JB}` are optional loopback HTTP/1.1 adapters to separate native functions. The mathematical executables run fully offline without sockets or screens.

- **Virtual coordinate**: `virtual_id = (ordinal × 1,000,003) mod 23,000,000,000` (exact integer arithmetic and lazily mapped identifiers, not 23 billion allocated states).
- **Deterministic physical input**: three real-codec Host8 stub identities `mix(word(global_room) XOR SEED)` at `global_room = 3 × (virtual_id mod 12,500,000,000) + {0,1,2}`. These are freshly regenerated canonical bytes from the pinned source algorithm, not claimed fresh physical disk measurements. The input SHA-256 commits the exact 24-byte source.
- **X3 state projection**: the original `OmegaOmnibitRoom::unpack_state(333_360)` gives 81 finite-field coordinates from 3 × 27 room trits. It is a model projection; arbitrary 64-bit source words cannot be recovered from the projected 81 finite-field amplitudes.
- **State evolution**: for each tick, run the pinned upstream `ShellModel81::step()`, separately check `predicted_step81()`, all 81 state residues and `Q+t nu D81`. The exact NTT-81 forward/inverse check is performed on initial and final states.
- **HBI / HBP / SHA / SH / HASH**: one HBP row per tick binds the pinned code commit, virtual address, canonical input-source SHA, viscosity, compensated invariant and 81-coordinate state SHA. HBI stores each record's byte offset, length, checksum and chain link. A plain-text anchor pins root hashes; verification walks all rows and **re-executes all steps** with the pinned Clasy source. The unkeyed anchor is a hash commitment and must be pinned separately for independently authenticated provenance.
- **Optional loopback server**: conventional HTTP/1.1 GET routes return `json=0` plain text, with a bounded 243-step computation per request. No HTML or GPU frame work is in the hot loop.
- **Boundary**: the 23B namespace measures addressability, **not** time or memory to evolve 23B independent states.

## Exact reproduction commands

```bash
cd native
cargo +1.81.0 test --all-targets --offline --locked
cargo +1.81.0 clippy --all-targets --offline --locked -- -D warnings
cargo +1.81.0 build --release --offline --locked

# Clasy X3 81-mode universe, one virtual kernel × 243 measured steps:
target/release/hebc clasy-run 0 1 243 clasy-single
target/release/hebc clasy-verify clasy-single

# Bounded, actually executed batches:
target/release/hebc clasy-batch 81 243 clasy-batch-81
target/release/hebc clasy-batch 243 81 clasy-batch-243

# Independent S3 finite Hamiltonian:
target/release/hebc spectrum 1 1
target/release/hebc sector double
target/release/hebc sector torus2

# Optional loopback; no JavaScript, JSON, remote service or display:
target/release/hebc serve 5088
curl http://127.0.0.1:5088/clasy/3/1/9
curl http://127.0.0.1:5088/spectrum/1/1
```

The `clasy-batch` receipt directories contain `kernel-NNN/run.hbp`, `index.hbi`, `run.anchor`, `run.measure` for each actually computed kernel plus a `batch.measure` commitment to the per-kernel anchor roots. SHA roots and unit tests are checked by GitHub Actions.

## Measured integration (GitHub Actions run 40129645904)

- **22 Rust unit tests passed**, zero-warning Clippy, `--offline --locked` release build.
- One Clasy instance: 243 self-stepping transitions; 243 HBP/HBI records; independent whole-trajectory reproduction; zero detected invariant deviations.
- 81 active independent Clasy kernels × 243 steps each = **19,683 actual finite-shell state transitions**, 81 × 81 = 6,561 active shell coordinate locations across the batch, not 19,683 distinct particles.
- GitHub runner time for the complete batch, including record generation and per-kernel re-execution: `2,315,323,617 ns`. This is not an HTTP network benchmark, not a matched alternative-runtime speedup, and not physical quantum hardware.
- Deterministic receipt replay, all 81 kernel anchors checked as written, negative HBP tamper control rejected; `/clasy` and `/spectrum` HTTP/1.1 loopback smoke tests passed.
- Clasy kernel 0, nu 1, 243 steps final state SHA-256:
  `87f15ce8a42d944f21c862caaa092f4c3e7845c3b840acf6f127030d8948d6ee`
- Existing gauge single-plaquette interacting `J_E=J_B=1` spectral gap bound remains `[727730,727732]/65536` in exact lattice energy units. This is not the unrelated Clasy total-drift invariant.

## The next hurdles, in implementation order

| Priority | Concrete next hurdle | Exact proof/test gate | What it would establish |
| --- | --- | --- | --- |
| 1 | **Double open plaquette, 7 links, physical dimension 11** | Build Hamiltonian by Gauss-projecting the **same 7-link electric and magnetic operators**; exhaustively enumerate independent S3 gauge classes; exact self-adjoint matrix and independently certified ground/excited eigenvalue intervals; include positive/zero controls | First real *multi-plaquette* interacting gauge gap; more meaningful than a 6-vertex graph-gap or just counting 11 states |
| 2 | **Periodic 2×2 torus, physical dimension 1,393** | Gauge constraint and basis/orbit enumeration, loop-sector accounting, sparse self-adjoint interacting Hamiltonian and reliable exact/rational energy enclosures with independent matrix check | Finite-volume changes in interacting gauge gaps, not a claim that Hilbert-space dimension or 2Q-trit-per-link encoding is a quantum simulation |
| 3 | **Repeat with variable couplings and spatial sizes** | Sweep `J_E/J_B` and number of plaquettes; keep physics units, boundary conditions and normalization explicit; separately report exact lower spectral bounds and solver residuals | Determines whether the finite gap closes, stays open or changes with increasing system size |
| 4 | **Q-trit address / cache / Host8 I/O comparison** | Identical source states, identical physical operations, controlled compiler/hardware and cache-hit/miss separation; HBP/HBI source SHA pinning and cold/warm measurements | Tests whether HTTP-0 virtual addressing and memoization actually improve resource use compared with conventional in-memory execution |
| 5 | **Clasy model bridge, if physically proposed** | Specify an explicit map from 81-mode shell variables to gauge-invariant observables; prove that the transfer/operator and invariant are respected by that map; test counterexamples | Only then could Clasy supply a mathematically justified *Yang–Mills-specific* simplification rather than a separate useful verification precedent |
| 6 | **4D compact-simple continuum Yang–Mills** | Construct the gauge-invariant nontrivial continuum theory with all required axioms, and prove a strictly positive mass gap uniformly through continuum and infinite-volume limits | Required for Clay Millennium Yang–Mills existence and mass-gap problem; **not solved** by any finite S3/Clasy computation here |

## Known limitations

1. A 512×512 classical gauge-equivariant run represents 1,048,576 encoded Q-trit positions but does **not** diagonalize a corresponding many-body quantum Hamiltonian.
2. Clasy's modular total invariant does **not** bound the unreduced energy/norm independent of the shell resolution. Its finite-field algorithm may not be injective even though its NTT is invertible.
3. The finite graph Laplacian gap 3 is distinct from the interacting single-plaquette gap `E1-E0`.
4. Independent authenticating hardware/physical disk measurement is not established by regenerating a source identity; that tests reproducibility of an identified software input.
5. Root anchors are unkeyed SHA commitments, not cryptographic signatures or authentication of the experimental operator.
