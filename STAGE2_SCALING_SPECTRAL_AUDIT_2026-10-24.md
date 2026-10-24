# Stage 2 — interacting finite gauge spectral certificate and scalable HEB-C tests

**Date:** 2026-10-24
**Implementation:** \`native/src/hamiltonian.rs\`, \`native/src/lib.rs\`, \`native/src/main.rs\`.
**Verified GitHub Actions:** [run 40126662720](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/40126662720); **PASS**, Rust 1.81.0, zero-warning Clippy, 19/19 tests, release build, headless replay, HBP/HBI receipt checks and deliberate corruption rejection.
**Native runtime constraints:** integer-only calculations, no JavaScript, V8, Node, JSON, floating-point physics, screen or physical Host8 storage required.

## 1. Mathematically appropriate physical-state counts

These are *gauge links* and *encoded discrete variables*, not empirically identified elementary particles. An S3 link has 6 values and encodes into two balanced Q-trits. A graph with V connected vertices and E oriented links can be gauge fixed onto n=E−V+1 independent fundamental cycles; residual conjugation reduces physical wavefunctions to simultaneous-conjugacy orbits of S3^n.

By Burnside's lemma, the exact gauge-invariant Hilbert dimension is

\`\`\`text
D_phys(n) = (6^n + 3*(2^n) + 2*(3^n))/6 .
\`\`\`

| Geometry | V | E | Encoded Q-trits | Raw Hilbert dimension | Gauge-invariant Hilbert dimension |
| --- | ---: | ---: | ---: | ---: | ---: |
| One open plaquette | 4 | 4 | 8 | 6^4 = 1,296 | 3 |
| Two adjacent open plaquettes | 6 | 7 | 14 | 6^7 = 279,936 | 11 |
| Periodic 2x2 torus | 4 | 8 | 16 | 6^8 = 1,679,616 | 1,393 |

For the single square, \`single_plaquette_gauss_orbits()\` explicitly enumerates 1,296 link assignments and all four local gauge transformations, recovering exactly three orbits of sizes 216, 648, 432. The multi-loop sector dimensions are counted by exact Burnside arithmetic; full double-plaquette and torus Hamiltonian matrices are **not yet constructed**.

## 2. Exact interacting 3x3 quantum Hamiltonian in the Gauss-law sector

The normalized irreducible S3 characters form an orthonormal basis for single-plaquette class functions under the uniform Haar measure. In \`[trivial, standard(2D), sign]\` order, the standard Wilson-character multiplication matrix is exactly:

\`\`\`text
chi_std =  [0 1 0]
           [1 1 1]
           [0 1 0]
\`\`\`

It is *already symmetric*. Introducing sqrt(2) off-diagonal entries by re-normalizing characters would be incorrect.

The four-link electric Casimir energies are 0, 12*J_E, 24*J_E. With magnetic term J_B*(2I−chi_std):

\`\`\`text
H_phys = [2*J_B          -J_B               0       ]
         [ -J_B         12*J_E+J_B        -J_B      ]
         [  0             -J_B          24*J_E+2*J_B]
\`\`\`

This is a self-adjoint, interacting finite single-plaquette gauge Hamiltonian when \`J_B>0\`. Unlike the previous Cayley graph gap 3, its first excitation gap is \`E1(J_E,J_B)−E0(J_E,J_B)\`.

**Exact integer Sturm isolation:** Eigenvalue intervals are enclosed by integers divided by 65,536. The algorithm uses leading principal-minor sign variations in i128 arithmetic and binary search, with no floating-point computations. A distinct independent test expands the full 3×3 characteristic determinant with integer operations, verifies that every reported interval brackets a root, and checks the electric-only and magnetic-only exactly solvable controls.

| J_E | J_B | E0 interval (numerators / 65536) | E1 interval | Gap enclosure (numerators / 65536) | Rigorous positive gap |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0 | [0,1] | [786432,786433] | [786431,786433] | Yes; exact analytic gap 12 |
| 0 | 1 | [0,1] | [131072,131073] | [131071,131073] | Yes; exact analytic gap 2 |
| 1 | 1 | [125140,125141] | [852871,852872] | **[727730,727732]** | Yes |
| 3 | 5 | [603267,603268] | [2699361,2699362] | [2096093,2096095] | Yes |
| 0 | 0 | [0,1] | [0,1] | [-1,1] | **No**; zero-coupling degenerate control |

The last row confirms the algorithm does not incorrectly certify a positive gap when the Hamiltonian is identically zero. Unit tests cover 0..=32 for *both* couplings in an independently calculated characteristic-polynomial test, and 0..=20 in detailed Sturm count checks. These are finite-dimensional statements with integer lattice-energy units; there is no continuum or infinite-volume extrapolation.

## 3. Actual large-lattice engineering tests (a distinct experiment)

These runs evolve a deterministic **classical, gauge-equivariant toy rule** over an S3 link lattice, not the interacting quantum Hamiltonian above. The stress simulations confirm native integer-state processing and receipt scaling, not exponential-size quantum many-body evolution.

| Headless lattice | Sites | Gauge links | Encoded Q-trits | Executed ticks | Virtual probes | CI elapsed (run section) | Final state SHA-256 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 4x4 | 16 | 32 | 64 | 243 | 1,990,656 | 4.876799 ms | \`5e4b49aff8fedc3836cffdbcc664456f19786117eef2805b256d16bccceae262\` |
| 64x64 | 4,096 | 8,192 | 16,384 | 81 | 331,776 | 71.613717 ms | \`ea5a81397cfef7e3d06c095c8aeb24a91bb78a1a906500345ae2b3793b8055a0\` |
| 128x128 | 16,384 | 32,768 | 65,536 | 9 | 0 | 22.898601 ms | \`e417dc755732a7b1a8c618f6fb88f6c06f0db7c867c8a354166f880ed3cd25cc\` |
| **512x512** | **262,144** | **524,288** | **1,048,576** | **3** | **0** | **122.781315 ms** | \`5d6f748ecf6078116efbcb748ebe6eec2fa1653169ccd7e1383e04b89b5b9b64\` |

- The 512x512 state is stored as **524,288 bytes** of link labels (1 byte per six-valued S3 link). Its **1,048,576 Q-trits** are the equivalent canonical two-Q-trit encoding, not allocated distinct coherent quantum qutrits.
- The \`HBP/HBI\` and anchor files verified after each run; exact replay including SHA digests passed for both 128x128 and 512x512.
- Expanded native gauge-equivariance tests include lattice sides 2, 3, 4, 8, 16, 32, 64, 128, 256 and 512.
- \`run.measure\` includes independent integer nanosecond wall timing; timestamps are not used to advance the model.
- Numbers are from one shared hosted CI runner, not calibrated hardware benchmarks. Distinct tick and address-probe counts prevent valid direct claims of performance superiority between sizes.
- A 23-billion-ID address namespace does not imply 23 billion active particles/kernels or 23 billion physical quantum states.
- The HBI/HBP/SHA/SH/HASH chain checks recorded integrity relative to an anchor; externally trusted provenance requires independently pinning the anchor.

## 4. Reproduction and acceptance

\`\`\`sh
cd native
cargo +1.81.0 test --all-targets --offline
cargo +1.81.0 clippy --all-targets --offline -- -D warnings
cargo +1.81.0 build --release --offline
./target/release/hebc sector single
./target/release/hebc sector double
./target/release/hebc sector torus2
./target/release/hebc spectrum 1 1
./target/release/hebc spectrum 3 5
./target/release/hebc run 81 64 4096 stress-64
./target/release/hebc verify stress-64
./target/release/hebc run 9 128 0 stress-128
./target/release/hebc verify stress-128
./target/release/hebc run 3 512 0 stress-512
./target/release/hebc verify stress-512
\`\`\`

CI captures \`evidence-native\`, \`stress-64\`, \`stress-128\` and \`stress-512\` HBP/HBI/anchor/measurement as downloadable **GitHub Actions artifacts**. These measured runtime artifacts are not committed into the source tree.

## 5. Pending scientific milestones

1. **Double open plaquette (physical dimension 11):** construct the fully projected **electric and magnetic** operators on the same underlying seven-link graph, verify hermiticity and independent gauge projection, and certify its low-energy gap.
2. **2x2 periodic torus (dimension 1,393):** construct a sparse physical Hamiltonian and establish an exact/rational or independently bounded low-energy spectrum with tractable memory and certifiable residuals. Do not mislabel graph-only enumeration as a quantum simulation.
3. **More lattices and coupling scans:** verify finite-volume behavior, boundary conditions, unit conventions and whether gaps remain bounded as size changes.
4. **Continuum problem:** a proof of 4D Yang–Mills existence and a strictly positive mass gap requires a controlled nontrivial quantum continuum limit with non-Abelian compact simple Lie group. Finite S3 tests do not establish it.

**Verdict:** Stage 2 single-plaquette interacting spectral certificate and million-encoded-Q-trit *classical engineering stress* are reproducible and passing; a multi-plaquette interacting spectrum and a continuum theorem remain open.
