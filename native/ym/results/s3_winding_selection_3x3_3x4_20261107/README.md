# 3×3 and 3×4 periodic finite S₃: exact winding-sector tests and 3¹⁶ time slices

**Status:** prediction-first independent extension of the [1×1 true-vacuum Wilson result (PR #127)](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/127) and the [2×2 first-excitation operator reversal (PR #128)](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/128). **Both PRs are drafts**. This experiment is built separately against `main`, does not import their source, and does not change their stored certificates.

The 17 new predictions were frozen **before the executable** at commit `3acdca0825fbf6a548686ccf1aae3838fd7b5a8e`, in [PREDICTION.hbp](PREDICTION.hbp). The dedicated workflow must independently rebuild every output, reject six wrong models/claims, and publish its exact HBP receipt.

## Scale and why the correct scope matters

For a periodic `Lx×Ly` torus there are `V=Lx*Ly` sites, `2V` positively oriented links and `V+1` independent loop holonomies after spanning-tree gauge fixing. Residual simultaneous `S₃` conjugation gives the *complete* gauge-invariant orbit count

```text
dim(H_phys) = (6^(V+1) + 3*2^(V+1) + 2*3^(V+1)) / 6
```

by Burnside and the centralizer sizes `6,2,3` for the three `S₃` conjugacy classes.

| Spatial torus | Complete physical Hilbert space | Existing available finite evidence |
|---|---:|---|
| **3×3** | **10,097,891 states** | The existing 59,246-state vacuum ball and 32-dimensional block-Krylov Ritz space, plus separately named native zero-momentum certificates. Compressed **Ritz-level differences do not prove a complete first gap** |
| **3×4** | **2,177,317,873 states** | The existing **45,508,080 stored operator rows**, which support `E₉−E₈` and high-cluster Perron bounds. **They are not the full 2.177-billion-state gauge-invariant space**, and `E₉−E₈` is not `E₁−E₀` |

We do **not** construct a dense multi-million-state Hamiltonian, certify the interacting `E₁` sector, or claim a real-world glueball mass in this test.

## 3×3: exchange-even and exchange-odd winding probes

Write `χ` for the real two-dimensional standard character of `S₃`. Let `W_x(y)` be the horizontal, closed noncontractible three-link holonomy around row `y`, and `W_y(x)` the vertical three-link holonomy around column `x`. Every `χ(W)` is **gauge invariant** under independent gauge transformations at *all* lattice vertices.

Define

```text
O_plus  = Σ_(y=0..2) χ(W_x(y)) + Σ_(x=0..2) χ(W_y(x))
O_minus = Σ_(y=0..2) χ(W_x(y)) − Σ_(x=0..2) χ(W_y(x)).
```

Exchanging `x` and `y` on the square torus preserves the Hamiltonian and maps `O_plus` to itself and `O_minus` to its negative. Both are valid, physically different **symmetry channels**. The **interacting** first excitation can belong to either, depending on the actual finite spectrum: **the 2×2 evenness result cannot be carried to 3×3 without new full-space information**.

## 3×4: rectangle has no x/y axis-exchange symmetry

The two side lengths differ. A difference `χ(W_x(0))−χ(W_x(1))` is **not generally a one-step translation eigenoperator** when there are four rows. The correct real odd-momentum channel under **unit translation in the four-site y direction** is

```text
O_alt  = χ(W_x(0)) − χ(W_x(1)) + χ(W_x(2)) − χ(W_x(3))
O_sum  = χ(W_x(0)) + χ(W_x(1)) + χ(W_x(2)) + χ(W_x(3))
T_y(O_alt) = −O_alt;       T_y(O_sum) = O_sum.
```

Both are gauge invariant because each `W_x(y)` is a closed horizontal winding. The `O_alt` state lives in momentum `k_y=π` relative to the **uniform electric vacuum**, and `O_sum` in `k_y=0`. This is a **sector-selection identity**, not evidence that the *interacting* first excitation is in either sector.

## Exact result at the pure-electric endpoint

Set `J_E=1, J_B=0` so `H=E`. The `S₃` electric operator on each oriented link is

```text
E_link f(U) = 3 f(U) − Σ_(t in 3 transpositions) f(U with link -> t*link).
```

For any standard-character Wilson loop of length `ℓ`, `Σ_t χ(g t h)=0` by the standard `S₃` representation, and `E χ(W)=3ℓ χ(W)`. The code independently checks every `6³=216` possible three-link word and all **1,944 single-link transposition changes**; for four-link loops, it checks all `6⁴=1,296` words and **15,552 moves**. Therefore:

| Lattice / observable | Pure-electric energy | Uniform-vacuum one-point | Exact connected variance |
|---|---:|---:|---:|
| 3×3 `O_plus` | `9 J_E` | 0 | 6 |
| 3×3 `O_minus` | `9 J_E` | 0 | 6 |
| 3×4 `O_alt` | `9 J_E` | 0 | 4 |
| 3×4 `O_sum` | `9 J_E` | 0 | 4 |
| 3×4 vertical four-link winding, per loop | `12 J_E` | 0 | 1 |

The variances follow by **independent Haar counting**: each traced Wilson loop has mean zero and variance one; the individual loops in each sum use disjoint positively oriented links. The existing separately verified electric-spectrum theorem `gap(E)=3 min(4,Lx,Ly)` gives `gap(E)=9` for both tori at `J_B=0`. These new eigenfunction identities exhibit **first-gap observables at the electric endpoint** without diagonalizing 10 million or 2 billion states. This **does not** imply their overlaps with interacting `J_B>0` first states.

## Exact continuous-*time* correlation and ternary jumps

Because `O|Ω_E>` is an `E=9` eigenvector and the uniform electric vacuum satisfies `E|Ω_E>=0`, the connected **Euclidean-time** correlation is exactly

```text
C_3x3(t)=6 exp(-9 t);   C_3x4(t)=4 exp(-9 t),   at J_E=1, J_B=0.
C_N(t=1)=m (1−9/N)^N,  N=3^k, k=3,4,5,6,9,12,16.
```

No multi-billion-component vector is allocated: this is an **exactly identified one-eigenvalue sector**, so time evolution reduces to one scalar transfer factor. That does **not** mean arbitrary interacting gauge dynamics can be compressed to one scalar.

The host computes rigorous integer-rational enclosures for `exp(-9)` using the positive Taylor series for `exp(9)` with an explicit factorial tail. For `C_N`, it encloses the exact logarithmic series

```text
−N log(1−9/N) = 9 + Σ_(k≥2) 9^k/(k N^(k−1))
```

by 28 positive terms and a geometric tail, and converts the resulting rational bounds to **outward decimal intervals**. With `N=3^16=43,046,721`, **16 modular cubings** of the scalar eigenmode are compared independently against binary modular exponentiation at `p=1,000,081` and `p=1,000,003`. These residues **verify the jump algorithm, not reconstruct the entire real amplitude or gauge-state vector**.

The test also applies independent vertex-gauge transformations to 48 deterministic raw configurations **per lattice**—`48×9×6=2,592` configurations on 3×3 and `48×12×6=3,456` on 3×4—and checks exact electric move covariance, magnetic plaquette covariance, axis exchange or fourfold y translation. It runs six named falsifiers including false parity, false translation parity, bare open-link gauge invariance, a false electric eigenvalue, incorrect cubing and an incorrect character variance.

## The *interacting* first excitation is still the next gate

We cannot infer the `J_B>0` interacting mass gap, first-excitation symmetry or Wilson overlap by reusing the `J_B=0` formula.

**3×3:** Determine the *complete interacting* lowest levels, including the axis-exchange parity and spatial momentum of the global first excitation. The 59,246-orbit ball's Ritz energy *difference* is not a full-space gap certificate. If the existing 1,122,211-state zero-momentum and lower-bound certificates support a full-space transfer at a selected `r`, first confirm that gate before measuring `O_plus` or `O_minus` overlap.

**3×4:** Determine the interacting global `E₁` quantum numbers before choosing `O_alt` or `O_sum`. The existing `E₉−E₈` bound near `r=9` is a high-cluster certificate and does not supply that first state. A 45.5-million-row suboperator can assist selected sector or variational checks, but cannot silently replace the full 2.177-billion-orbit physical Hilbert space.

This is evidence that finite-group lattice systems admit exactly gauge-invariant discrete observables and mathematically continuous-*time* correlations; it is **not** proof that nature's spacetime is discrete, and it is **not** a spatial-spacing continuum SU(2) or four-dimensional Clay mass-gap proof.

## Reproduce

```bash
python3 -I -X utf8 native/ym/results/s3_winding_selection_3x3_3x4_20261107/verify_winding_and_slices.py
```

[Hosted workflow](../../../.github/workflows/s3-winding-selection-3x3-3x4.yml) tests prediction-first exact source, independent modular jump, HBP replay, and six falsifiers. The successful output is archived at `MEASURED-20261107.hbp` after the hosted run. No original spectral receipt is altered.
