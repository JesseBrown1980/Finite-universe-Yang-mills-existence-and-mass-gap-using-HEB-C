# Stage 2I — Independent Spectral Verifier and Finite-Volume Scaling

**Scope:** The full gauge-invariant, 1,393-dimensional, eight-link, four-face periodic $2\times 2$ $S_3$ torus Hamiltonian in [`native/src/torus2.rs`](native/src/torus2.rs), evaluated alongside the single-plaquette (dim=3) and double-plaquette (dim=11) operators.
**Native platform:** Rust 1.81.0, exact integer/rational arithmetic, zero floating-point operations, zero JSON, Clippy `-D warnings` clean.
**Resolution:** Feature-branch implementation and CI gates satisfy the numerical benchmark and cross-geometry comparison scope of [Issue #2](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/issues/2). PR #4 remains a draft; merge, independent mathematical review, and any further reproducibility checks are separate gates.

---

## 1. Executive Summary & Certified Enclosures

Stage 2I introduces a separately coded checker ([`native/src/torus2_independent.rs`](native/src/torus2_independent.rs)) with a different rank-lift strength (48 versus 60) and receipt schema from Stage 2H ([`native/src/torus2_inertia.rs`](native/src/torus2_inertia.rs)). It **shares the same rank-one Cholesky mathematical method, iteration counts, native torus operator, and Stage 2G ground-energy enclosure**. It is a useful repeat implementation and cross-check, not independent mathematical confirmation of a different theorem.

The pair of implementations reproduces the same rational spectral intervals (all energies in finite lattice units rounded outward to denominator 1,000,000). The ground-state interval is imported from Stage 2G rather than recomputed independently in Stage 2I:

| Coupling $(J_E, J_B)$ | Ground Energy $E_0$ | Excited Energy $E_1$ | Mass Gap $\Delta = E_1 - E_0$ | Certified Strict Threshold |
| :---: | :---: | :---: | :---: | :---: |
| **$(1, 1)$** | **$[7.634198, 7.634199]$** | **$[13.240000, 13.242733]$** | **$[5.605801, 5.608535]$** | $E_1 > 13.240$ ($t = 13240/1000$) |
| **$(3, 5)$** | **$[36.699227, 36.699228]$** | **$[50.840000, 50.842050]$** | **$[14.140772, 14.142823]$** | $E_1 > 50.840$ ($t = 50840/1000$) |

Both coupling configurations certify **strictly positive finite-volume mass gaps** ($\Delta > 5.605$ at $(1,1)$ and $\Delta > 14.140$ at $(3,5)$).

---

## 2. Independent Verification Architecture

The Stage 2I verifier establishes independent mathematical validity through three decoupled components:

### A. Ground-State Collatz–Wielandt Re-enclosure
A strictly positive trial vector $v > 0$ is generated using a separately coded normalized shifted-power iteration on the entrywise nonnegative operator $M = (1 + \max_i H_{ii}) I - H$. For any positive $v$:
\[
\min_{i} \frac{(H v)_i}{v_i} \le E_0 \le \max_{i} \frac{(H v)_i}{v_i}
\]
Stage 2I constructs its own positive vector but calls `crate::torus2_bounds::enclose(je,jb)` for the accepted $E_0$ interval. The Collatz–Wielandt enclosure is established by Stage 2G; the second module **does not independently rederive** this interval.

### B. Independent Positive-Definiteness Certification
To prove $E_1 > t$, the verifier forms the integer symmetric matrix:
\[
A_t = W(H - tI) + \frac{48}{N} u u^\top, \quad u = W v, \quad N = v^\top W v
\]
with independent rank-lifting parameter $\alpha = 48$ (distinct from Stage 2H's 60).
By Weyl's interlacing theorem, the rank-one addition shifts at most one eigenvalue from $\le 0$ to $> 0$. An exact integer Cholesky factorization of $(A - f I) S^2$ with $f = N$ and $S = 10^6$ proves strict positive definiteness:
- All Cholesky pivots $L_{ii} > 0$ are non-zero integers.
- The residual $R = A S^2 - L L^\top$ is certified to be strictly diagonally dominant with positive diagonal by verifying:
\[
f S^2 > \sum_{j < i} \left\lceil \frac{L_{jj}}{2} \right\rceil + (D - 1 - i) \left\lceil \frac{L_{ii}}{2} \right\rceil \quad \forall i \in \{0, \dots, 1392\}
\]
At $(1,1)$, the certified residual margin is $1.83 \times 10^{27} > 0$. At $(3,5)$, it is $5.82 \times 10^{26} > 0$. Therefore $A_t \succ 0$, establishing algebraically that at most one eigenvalue of $H$ is $\le t$. Because $E_0 < t$, it follows that $E_1 > t$.

### C. Exact min–max upper bound and a non-certified truncated-vector variance diagnostic
The excited trial vector $z$ is constructed in the axis-swap antisymmetric reflection sector:
\[
z_i = v_i \cdot (\chi_{\text{standard}}(q_i[0]) - \chi_{\text{standard}}(q_i[2]))
\]
where $q_i[0]$ and $q_i[2]$ represent non-contractible Wilson lines along the $x$- and $y$-cycles of the torus.
Because the spatial reflection $\tau: x \leftrightarrow y$ commutes with $H$, the reflection-odd subspace $V^-$ is an invariant subspace of $H$, and $v \in V^+$. The implementation verifies exact orthogonality:
\[
\langle v, z \rangle_W = 0, \quad \langle v, H z \rangle_W = 0, \quad \langle z, H v \rangle_W = 0
\]
The Rayleigh quotient $\mathcal{R}_H(z) = \frac{\langle z, H z \rangle_W}{\langle z, z \rangle_W}$ provides a rigorous upper bound $E_1 \le \mathcal{R}_H(z)$.
A diagnostic resembling a residual-variance formula is also calculated:
\[
\eta^2 = \frac{\langle H z, H z \rangle_W}{\langle z, z \rangle_W} - \left( \frac{\langle z, H z \rangle_W}{\langle z, z \rangle_W} \right)^2
\]
**Important correction:** the implementation first truncates `z` and `Hz` *separately* by integer division by 1,000, then computes a Cauchy–Schwarz defect of those two truncated arrays. The result is exact for those truncated arrays, but it is **not the exact spectral variance of the original vector** and is not a certified Kato–Temple eigenvalue/eigenvector isolation bound. The certified $E_1$ upper enclosure instead follows from the separately checked exact weighted orthogonality and the Courant–Fischer two-vector min–max argument. Do not use the truncated diagnostic as a theorem or an additional narrow eigenvalue interval.

---

## 3. Cross-geometry finite-volume comparison (not a controlled scaling limit)

Issue #2 explicitly mandates comparing the 1,393-state torus with smaller volumes, accounting for topology, energy density, and boundary conditions.

The `torus2-scaling` command reports the following comparison of distinct finite geometries. Because the boundary conditions and shape change between examples, this is **not a controlled sequence of increasing periodic lattices**, nor a proof of an infinite-volume scaling law:

| Geometry | Vertices $V$ | Links $E$ | Faces $F$ | Physical Dim $D_{\text{phys}}$ | Coupling $(J_E, J_B)$ | Ground Energy Density $E_0 / F$ | First Excitation $E_1$ | Mass Gap $\Delta$ | Lowest Mode Classification |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Single Open Plaquette** | 4 | 4 | 1 | **3** | $(1,1)$<br>$(3,5)$ | $\approx 1.9095$<br>$\approx 9.2051$ | $\approx 13.0135$<br>$\approx 41.1889$ | **$11.104$**<br>**$31.984$** | Contractible $0^{++}$ glueball |
| **Double Open Plaquette** | 6 | 7 | 2 | **11** | $(1,1)$<br>$(3,5)$ | $[1.75, 2.25]$ (center $2.00$)<br>$[8.75, 9.25]$ (center $9.00$) | $[14.5, 15.5]$<br>$[49.5, 50.5]$ | **$(10, 12)$**<br>**$(31, 33)$** | Contractible $0^{++}$ glueball |
| **Periodic $2\times 2$ Torus** | 4 | 8 | 4 | **1,393** | $(1,1)$<br>$(3,5)$ | $\approx 1.9085$<br>$\approx 9.1748$ | $[13.240, 13.243]$<br>$[50.840, 50.843]$ | **$[5.605, 5.609]$**<br>**$[14.140, 14.143]$** | Non-contractible torelon flux doublet |

### Finite-model observations and open interpretation questions:

1. **Similar finite energy densities, not proof of extensivity**:
   Across all three system sizes, the ground state energy per plaquette $E_0 / F$ is remarkably uniform:
   - At $(1,1)$: $1.9095 \to 2.00 \to 1.9085$
   - At $(3,5)$: $9.2051 \to 9.00 \to 9.1748$
   The values are numerically similar for these three separately constructed geometries. This alone **does not prove** thermodynamic extensivity, a limiting energy density, or negligible boundary effects.

2. **Open-versus-periodic gap comparison (mode labels are provisional)**:
   On open lattices (single and double plaquettes), every gauge-invariant loop is contractible; the lowest excitation is a localized $0^{++}$ plaquette glueball with perimeter $4$, yielding $\Delta \approx 11.1$ at $(1,1)$ and $\Delta \approx 32.0$ at $(3,5)$.
   On the periodic torus ($T^2$), boundary periodicity introduces non-contractible Wilson loops wrapping around fundamental cycles of length $L = 2$. These winding flux states (**torelons**) have length $2$ rather than perimeter $4$.
   In pure electric coupling ($J_B = 0$), the torelon has energy $6 J_E$ while the glueball has $12 J_E$ (an exact ratio of $1/2$).
   In the interacting theory at $(1,1)$, the torelon gap drops to $\approx 5.61$, almost exactly half of the open glueball gap ($11.104$). At $(3,5)$, it drops from $\approx 31.98$ to $\approx 14.14$.
   The electric-only length-two Wilson-loop witness has exact eigenvalue $6J_E$, and a single length-four contractible loop is associated with $12J_E$ in the relevant electric-only setting. The observed interacting gap ratios are **not exactly 1/2**; nor does a hard-coded `mode_type` string establish an eigenvector's symmetry/topological-sector classification or confinement/string tension. Torelon/glueball identifications require independently checked projectors or sector-resolved spectral witnesses.

3. **Flat Potential Minima & Non-Degeneracy**:
   In the pure magnetic limit ($J_E = 0, J_B > 0$), the torus exhibits exactly 8 gauge-inequivalent flat connections ($\Delta = 0$). When electric coupling is introduced ($J_E > 0$), electric tunneling completely lifts the 8-fold flat degeneracy, generating a unique strictly positive ground state.

---

## 4. Software Provenance, CLI & Replay

The independent verifier saves four plain-text artifacts under schema `hebc.s3.stage2i.independent.v1`:
- `run.hbp`: Couplings, rational bounds, independently coded Cholesky margin, trial-vector witness SHA, and a *truncated-vector Cauchy–Schwarz diagnostic* (`kato_var_*` remains a legacy field name; do not treat it as a valid Kato–Temple spectral certificate). Code/provenance SHA must be bound separately to the reviewed commit.
- `index.hbi`: Byte lengths, row digests, and chained hashes.
- `run.anchor`: SHA-256 root digest committing to the evidence.
- `run.measure`: Measurement string including `independent_cholesky=PASS`; this module does not claim a separately checked exact LDL decomposition.

### Headless Reproduction Commands:

```bash
cd native
cargo +1.81.0 test --all-targets --offline --locked
cargo +1.81.0 clippy --all-targets --offline --locked -- -D warnings
cargo +1.81.0 build --release --offline --locked

# Stage 2I Independent Verifier
target/release/hebc torus2-independent 1 1 indep-1-1
target/release/hebc torus2-independent-verify 1 1 indep-1-1
target/release/hebc torus2-independent 3 5 indep-3-5
target/release/hebc torus2-independent-verify 3 5 indep-3-5

# Multi-Volume Scaling Comparison
target/release/hebc torus2-scaling
```

Adversarial corruption of `run.hbp` or `index.hbi` causes `torus2-independent-verify` to fail closed immediately.

---

## 5. Formal Resolution of Issue #2 & Scientific Boundary

- **Issue #2 Status: acceptance implementation CI-verified on draft PR #4; GitHub issue closure requires deciding whether feature-branch evidence is sufficient before merge.**
  - *Note 2026-11-01:* PR #4 was merged by the repository owner on 2026-10-26 with no recorded review, and Issue #2 was closed as completed on 2026-11-01 after rechecking the benchmarks on `main`. The boundary below is unchanged.
  - 1,393-state sparse Hamiltonian: Built, validated, and verified.
  - Quantitative rational bounds on $E_0$, $E_1$, and $\Delta$: Stage 2G ground enclosure plus two implementations of the rank-one inertia/min–max approach. The second implementation shares the Stage 2G ground interval.
  - Finite open-versus-periodic geometry comparisons: implemented. Controlled scaling across increasing periodic volumes and independently proven excitation-sector quantum numbers remain future work.
- **Scientific Boundary Disclosure**:
  These computations establish rigorously bounded positive gaps for specific finite $S_3$ lattice Hamiltonians. They do **not** independently prove confinement, string tension, a complete torelon/glueball quantum-number classification, an infinite-volume limit, or the four-dimensional continuum Yang–Mills existence and mass-gap theorem.
