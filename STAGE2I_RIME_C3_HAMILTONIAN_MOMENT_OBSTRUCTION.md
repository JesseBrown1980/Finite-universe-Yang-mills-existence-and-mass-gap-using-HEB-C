# Stage 2I — RIME C3 extension test against the actual finite torus Hamiltonian

**Research status:** an exact counterexample to one *specific* natural full-Hamiltonian bridge; not a disproof of all Shadow Cat/RIME interpretations, not a Yang–Mills continuum theorem.

## Source and model being tested

This continues the source-grounded [Stage 2E original-law audit](STAGE2E_SHADOW_RESIDUAL_TORUS_MATH_AUDIT.md) and its **original** Law 71 C0→C1→C2→C0 winding action, without substituting a novel Shadow Cat operator.

The actual Rust 1.81 implementation [native/src/torus2.rs](native/src/torus2.rs) constructs the 1,393-dimensional gauge-orbit Hilbert space of the eight-link, four-face periodic 2×2 finite \(S_3\) lattice. In the orbit-value basis \(|i\rangle\), its inner product is \(\langle f,g\rangle_W=f^\dagger Wg\), where \(W_{ii}\) is the physical orbit cardinality (one, two, three, or six). The self-adjoint native Hamiltonian is \(H(J_E,J_B)=J_EH_E+J_BH_B\). This audit reuses **that same implementation**; no replacement dynamics or approximate eigensolver.

On the eight flat-connection classes, based holonomies \((X,Y)\) commute. Their simultaneous-conjugacy classes support the order-three winding map
\[
R(X,Y)=(Y^{-1},XY^{-1}),\quad R^3=1.
\]
There are two fixed points and two three-cycles, exactly as in Stage 2E. This is a mathematical *structural match* for the source-defined Law 71 cyclic representation, **not** a measurement of physical Shadow Cat propagation or faster-than-light signaling.

## Exact no-go theorem: basis-preserving unitary symmetry

**Assume** a unitary \(U\) acting on all 1,393 gauge-invariant basis states, unitary for the actual \(W\) inner product, such that:

1. On *each* of the eight normalized flat orbit-value basis vectors \(|i\rangle/\sqrt{w_i}\), it agrees with the above \(R\), up to a complex phase.
2. \(U\) commutes with the native \(H_E\); or alternatively it commutes with \(H(1,1)\); or with \(H(3,5)\).

The assumptions are mutually incompatible. In particular, no such **exact basis-preserving unitary symmetry** is a full extension of this flat C3 action for the specified operators.

**Proof:** For any self-adjoint \(H\) commuting with \(U\), all normalized spectral moments
\[
m_k(i;H)=\frac{\langle i|WH^k|i\rangle}{w_i}=(H^k)_{ii}
\]
must agree between a state and its image under \(U\), for every integer \(k\ge0\). Phases cancel. In the exact native model, the flat class with Wilson pair \((X,Y)=(0,1)\) maps by \(R\) to \((1,1)\); they correspond to physical orbit indices 271 and 276, both of orbit weight three.

The following entries are **pure integer matrix powers** of the *actual* sparse Hamiltonian, measured from the same pair. Every first, second and third moment is equal, but the fourth is not:

| Hamiltonian | \(m_1\) both | \(m_2\) both | \(m_3\) both | \(m_4\) at 271 | \(m_4\) at 276 | Difference |
|---|---:|---:|---:|---:|---:|---:|
| \(H_E=H(1,0)\) | 24 | 600 | 15,552 | 417,192 | 416,784 | 408 |
| \(H(1,1)\) | 24 | 600 | 15,648 | 426,792 | 426,384 | 408 |
| \(H(3,5)\) | 72 | 5,400 | 424,224 | 35,123,112 | 35,090,064 | 33,048 |

Each fourth-moment difference contradicts the corresponding commuting-unitary hypothesis, regardless of how that unitary would act on the other 1,385 basis directions. This is stronger than Stage 2E's observation that the flat subspace is not closed under \(H_E\): an extension that leaks into the nonflat sector is **still unable** to satisfy these particular requirements.

An independent discriminating control checks the natural axis swap \((1,0)\leftrightarrow(0,1)\), for which all four moments agree. The test is not simply rejecting every nontrivial state permutation.

## Interpretation and boundaries

The no-go concerns exactly the original flat holonomy three-cycle, a **unitary action that maps flat basis states exactly**, and commutation with each stated native finite-model Hamiltonian. The tests do **not** rule out a nonunitary operator, a representation mixing flat states, different physical degrees of freedom, a modified lattice Hamiltonian, distinct temporal calling dynamics, or other source-defined maps. None of those alternatives is *established* by the present code, either.

In particular:
- Law 70's \(2/3\) retained and \(1/3\) passed fractions are separate from the signed Law 71 \(-1/3\) calling parameter. Their algebraic relation does not supply the missing Hamiltonian operator.
- HTTP-0 remains an internal virtual addressing and computation abstraction, not a wire-speed or superluminal signaling claim.
- RIME's already-arrived frozen snapshots do not become physical instantaneous remote transmissions through this spectral calculation.
- No finite \(S_3\) model establishes the four-dimensional continuum compact-simple Lie-group Yang–Mills mass gap.

## Reproduce and challenge

From \`native/\`:

\`\`\`sh
cargo +1.81.0 test --all-targets --locked --offline
cargo +1.81.0 clippy --all-targets --locked --offline -- -D warnings
cargo +1.81.0 build --release --locked --offline
target/release/hebc rime-hamiltonian-audit rime-hamiltonian-evidence
target/release/hebc rime-hamiltonian-verify rime-hamiltonian-evidence
\`\`\`

The audit computes all spectral moments from the verified original operator, checks the exact witnesses (including first three equal moments), checks the valid axis-swap negative control and writes \`run.hbp\`, \`index.hbi\`, \`run.anchor\`, and \`run.measure\`. The verifier fully rebuilds the native matrix and evidence rather than trusting saved text. CI tests HBI/HBP byte identity and deliberate corruption rejection. The SHA anchor is an integrity fingerprint; an outside signature/physical provenance must be independently pinned.

## Next constructive target

For a positive full RIME-to-Hamiltonian bridge, the source must specify an actual executable calling operator \(C\), its representation space, an observation map linking it to gauge observables, and which conservation/commutator/causal properties it is supposed to satisfy. Any proposed revised \(C\) should be tested independently against all 1,393 states and the weighted inner product. A failed natural symmetry hypothesis should not be relabeled as a physical discovery.
