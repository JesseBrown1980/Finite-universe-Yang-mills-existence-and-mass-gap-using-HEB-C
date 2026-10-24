# Stage 2B — Two-plaquette interacting S₃ Hamiltonian: exact Gauss projection and spectral gates

**Date:** 2026-10-24. **Platform:** Rust 1.81.0, Clippy with `-D warnings`, exact integer arithmetic, no floating-point physics, no JSON, JavaScript, Node, V8, GPU or display requirement.

**Source:** [native/src/double_plaquette.rs](native/src/double_plaquette.rs). **CLI:** `double-spectrum`, `double-verify`; optional headless HTTP-0 loopback route `/double-spectrum/{JE}/{JB}`. **Passing initial CI:** [GitHub Actions 40131212312](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/40131212312).

## 1. Precisely defined seven-link geometry

There are six vertices, seven oriented S₃-valued links, and two adjacent square faces sharing one edge:

```text
v0 -------e0------> v1 -------e4------> v4
 |                     |                     |
e3                    e1                    e5
 |                     |                     |
 v                     v                     v
v3 -------e2------> v2 -------e6------> v5

e0:(0,1) e1:(1,2) e2:(3,2) e3:(0,3)
e4:(1,4) e5:(4,5) e6:(2,5)
```

The two oriented plaquette holonomies are
`P_L = U0 U1 U2^-1 U3^-1`,
`P_R = U4 U5 U6^-1 U1^-1`.
The right holonomy is transported to v0 via U0, giving `U0 P_R U0^-1). Under local gauge rotations the two based holonomies transform by simultaneous conjugation, which is classified exhaustively.

**Raw Hilbert space:** `6^7 = 279,936` link configurations; *physical* (Gauss-invariant) orbit-valued functions: **11 dimensions**, independently corroborated by a full 279,936-state gauge-generator BFS.

The sorted simultaneous-conjugation class codes are:

```text
keys    = [0, 1, 3, 6, 7, 8, 9, 18, 19, 21, 22]
weights = [7776, 23328, 15552, 23328, 23328, 46656, 46656, 15552, 46656, 15552, 15552]
sum(weights) = 279936
```

## 2. Electric and magnetic terms from the SAME physical links

For every raw link configuration, the **electric** gauge-invariant operator is

```text
H_E = sum_{link=0..6} sum_{t in S3 transpositions} (I - L_{link,t})
```

where `L_{link,t}` multiplies the selected link on the left by a transposition `t`. Transpositions form an entire conjugacy class, making this sum gauge invariant. No assumed diagonal electric energies or disconnected products were inserted.

The **magnetic** operator is the diagonal two-plaquette character potential

```text
H_B = (2 - chi_standard(P_L)) + (2 - chi_standard(P_R)).
H(J_E,J_B) = J_E * H_E + J_B * H_B.
```

The 11×11 representation uses orbit values, with exact physical inner product

```text
< f,g > = sum_{i=0}^{10} orbit_weight[i] * f[i] * g[i].
```

Therefore the matrix need not be symmetric in the unweighted Euclidean inner product. The program verifies the **correct self-adjointness identity** `weight[i] * H[i,j] = weight[j] * H[j,i]` for every pair, and tests gauge invariance under local vertex moves.

## 3. Exact, integer-only low-energy spectral certification

The matrix has integer entries for integer couplings. For each leading principal submatrix, the implementation computes the characteristic polynomial using exact integer Faddeev–LeVerrier recurrences.

At **half-integer** rational probes `x=(2k+1)/2`, no integer-matrix principal minor can have an eigenvalue exactly equal to x: every rational algebraic integer must be an integer. Exact signs of principal determinants therefore allow a Sturm inertia count without zero-pivot ambiguity.

Each energy is isolated in an interval of width **1 energy unit**. The excitation-gap enclosure subtracts the two eigenvalue enclosures conservatively. It can certify positivity without pretending the generally irrational roots are exactly known by a finite decimal expansion.

| J_E | J_B | E0 interval | E1 interval | Certified E1−E0 interval | Strictly positive? |
| ---: | ---: | --- | --- | --- | --- |
| 0 | 0 | (-0.5, 0.5) | (-0.5, 0.5) | (-1, 1) | **No** |
| 1 | 0 | (-0.5, 0.5) | (11.5, 12.5) | (11, 13) | Yes |
| 0 | 1 | (-0.5, 0.5) | (1.5, 2.5) | (1, 3) | Yes |
| 1 | 1 | (3.5, 4.5) | (14.5, 15.5) | **(10, 12)** | **Yes** |
| 3 | 5 | (17.5, 18.5) | (49.5, 50.5) | **(31, 33)** | **Yes** |

All figures are finite-model **lattice-energy units**. In addition to the polynomial/Inertia implementation, a separate exact signed-permutation determinant dynamic program tests the leading-minor signs at every certified low-energy endpoint. The two methods have different arithmetic implementations.

## 4. Actual native tests and replay controls

- Exhaustive 279,936-configuration orbit coverage, 11 independent classes and independently reconstructed Gauss orbits.
- Six-vertex local gauge action and two holonomy classes; invariance for all group-element transformations on representative configurations.
- Exact weighted self-adjointness, generator row-sum zeros, electric and magnetic coupling composition, and negative-coupling rejection.
- Exact spectral intervals under five coupling pairs, including `(JE,JB)=(0,0)` as the deliberately gapless control.
- Headless native `double-spectrum` writes HBP/HBI/SHA/SH/HASH and anchor with source matrix SHA-256, orbit weights and spectral bounds.
- `double-verify` **reconstructs** the 279,936-state orbit classification, rebuilds the full 11×11 matrix, re-computes exact spectral bounds and compares the entire HBP/HBI and root anchor. A deliberately tampered receipt must fail.
- Repeat runs must reproduce identical receipts and anchors for each coupling pair.
- CI also smoke-tests `GET /double-spectrum/1/1` over an optional ordinary HTTP/1.1 loopback adapter, with internal virtual-kernel dispatch named HTTP-0.

## 5. Reproduce with pinned toolchain

```bash
cd native
cargo +1.81.0 test --all-targets --locked --offline
cargo +1.81.0 clippy --all-targets --locked --offline -- -D warnings
cargo +1.81.0 build --release --locked --offline

target/release/hebc double-spectrum 1 1 double-1-1
target/release/hebc double-verify double-1-1
target/release/hebc double-spectrum 0 0 double-0-0
target/release/hebc double-verify double-0-0
```

Windows: `target\release\hebc.exe`. The workflow uploads exact native receipts for the five tested couplings and replays.

## 6. What is still open

The present result is **a nontrivial interacting, exactly constructed finite two-plaquette S₃ Hamiltonian**, not a proof of the continuum Yang–Mills existence and mass-gap Millennium Prize problem. In particular, neither Clasy X3's 81-mode modular shell invariant nor HEB-C's 23-billion-ID virtual address namespace changes the infinite-dimensional continuum proof obligations.

**Next scientific gate:** [Issue #2](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/issues/2) — build the gauge-invariant **1,393-dimensional periodic 2×2 torus** sparse electric/magnetic Hamiltonian, certify lowest eigenvalues, compare volume dependence and explicit topological sectors. Only then do finite-size scaling tests become meaningful.
