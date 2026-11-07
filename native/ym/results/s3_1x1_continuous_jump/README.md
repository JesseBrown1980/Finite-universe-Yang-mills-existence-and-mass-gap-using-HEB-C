# One exact finite Yang–Mills Hamiltonian, 43-million-step matrix jump, continuous-time Wilson correlation

**Status:** preregistered at commit `031d11923fd877166b2baf72c4e7eb745c4e362e` before the test code. The independent code in this folder reconstructs the actual **`S₃` Kogut–Susskind electric-plus-magnetic Hamiltonian** on a **1×1 periodic two-spatial-dimensional torus**. It is not a generic toy transfer matrix. It is also **not the 3×4 operator**, not four-dimensional SU(2), and not a physical molecular or nanoparticle measurement.

## Why this is a useful place to start

This tiny spatial torus contains two oriented link holonomies `a,b ∈ S₃`. There are **36 raw pairs**. Simultaneous gauge conjugation `(a,b) → (gag⁻¹, gbg⁻¹)` leaves **11 gauge-invariant orbits** with positive orbit sizes summing to 36. That is small enough to reconstruct the exact operator, calculate its finite first excitation rather than its eighth-to-ninth separation, and subject a gauge-invariant Wilson observable to millions of **time** subdivisions.

At `J_E=J_B=1`, define

```text
E f(a,b) = Σ_(link=a,b) Σ_(t in 3 transpositions) (f(a,b) − f(t*link,other))
M(a,b)   = 2 − χ_std(aba⁻¹b⁻¹)
H        = E + M.
O(a,b)   = χ_std(aba⁻¹b⁻¹)   (gauge invariant)
```

The gauge orbit basis is not uniformly weighted. The exact integer checker carries orbit multiplicities in `W` and proves `W H = Hᵀ W`. It verifies 11×11 characteristic polynomials using integer Faddeev–LeVerrier and counts eigenvalues by **integer Bareiss determinants and inertia of `W(H−sI)`**. The frozen expectations for the actual interacting spectrum are:

```text
P_E(x)=x(x−12)(x−9)^2(x−6)^5(x−3)^2
P_H(x)=(x−6)^3 (x^3−21x²+135x−252)
       (x^5−36x^4+468x^3−2655x²+6138x−4104)
1.096113 < E0 < 1.096114 (J_E)
3.274551 < E1 < 3.274552 (J_E)
2.178437 < E1−E0 < 2.178439 (J_E)
```

These are finite `S₃` spectra. Their lower bound is on the **first energy splitting of this 11-state model**, unlike the **3×4** certified `E₉−E₈≥24.039673 J_E` above the eight-state cluster, which this test does not overwrite.

## Exactly what is compared

Let `u=2(O−1/2)` on gauge orbits. The uniform, weighted group-average state at `J_B=0` has `⟨O⟩=1/2` and `⟨(O−1/2)²⟩=9/4`. The *electric-only* Euclidean Wilson correlation is exactly

```text
C_E(t) = (1/2)e^(−3t) + e^(−6t) + (1/2)e^(−9t) + (1/4)e^(−12t).
```

The checker certifies the formula from the finite electric matrix and integer spectral moments.

For the **interacting H=E+M**, start with the same *fixed, centered trial vector* `f=O−1/2` and define

```text
C(t)  = ⟨f, exp(−tH) f⟩_W / 36.
C_N(t=1) = ⟨f, (I − H/N)^N f⟩_W / 36,
N=27,81,243,729,19683,531441,43046721.
```

**Important:** the constant function is no longer the interacting ground state when `J_B=1`. Thus `C(t)` for this chosen trial state is **not** claimed to be the *vacuum-connected* interacting Wilson correlation and cannot be used to extract `E₁−E₀` without further projection. The first gap comes from the independent exact inertia test above. The positive matrix exponential `exp(−H)` is the mathematically continuous-time Euclidean semigroup of **this same finite H**; it is not a continuum limit in **spatial lattice spacing**, an actual 4D gauge field, or an empirical quantum interference curve.

For `N=3^k`, compute the step `T_N=I−H/N` and its final vector using only **k exact modular cubings**, with independent modular binary powering and short direct-step controls. Different N mean a different Euler approximation to the *same* fixed-time semigroup. In real arithmetic `(I−H/N)^N → exp(−H)` as `N→∞`, an elementary finite-dimensional fact. The test measures convergence with mathematically rigorous outward rational intervals.

### No floating-point computations

The exact trial correlation uses all integer moments `μ_j = uᵀ W H^j u /144`. A Taylor polynomial of order **144** encloses the continuum reference. The binomial expansion of `(I−H/N)^N` is evaluated in **integer numerator/denominator pairs**, with the same truncation bound valid uniformly in N. Since `0≤H≤15` spectrally (the row-sum norm bound and W-self-adjointness), the omitted absolute correlator tail is bounded by

```text
(9/2) × 15^145 / 145!  < 2×10^(-81)
```

for either Taylor or binomial series. All reported decimal endpoints are **outward rounded from rational values**; the program does not use `float`, `Decimal`, `Fraction`, or a JSON data path. The runtime records every mathematical control and prints a verified SHA-256 fingerprint of the modular jumped state.

The first **eight** integer moment numerators are independently reconstructed from **two modular residues** using the Chinese remainder theorem, with `p₁=1000081`, `p₂=1000003`. Their certified magnitudes are at most `324×15^7`, strictly below half of `p₁ p₂`, making the signed reconstruction unique. The high-step modular powers are **not** claimed to reconstruct the enormous exact numerator of the `43,046,721`-step rational trajectory; that distinction prevents a misleading CRT claim.

## Registered prediction miss and real-world interpretation

The frozen expected 43-million-step approximate correlation was `0.0568166301459`; an independent calculation predicts the more accurate value around `0.05681663018135`. The frozen point estimate is therefore recorded as a **MISS** and preserved, while the precommitted **error window** `1×10^-9 < C(1)−C_N(1) < 3×10^-9` is expected to hold. The hosted run must publish the actual bracket and the mismatch, never silently rewrite the freeze.

This program shows how a discrete series of **computational time slices** approximates the continuous-time evolution of a real, gauge-invariant finite-group Hamiltonian. It does **not** establish that physical spacetime is discrete. To compare with nature requires correctly parameterized continuum `SU(2)` or other physical gauge observables, a genuine physical-time/lattice-spacing calibration, and external measurement data. To prove the **Clay** four-dimensional existence-and-mass-gap theorem additionally requires all-scale spatial renormalization, nontrivial reconstructed continuum quantum fields and a uniform positive *first* physical gap. For this task consult [the 4D companion PROBLEM.md](https://github.com/JesseBrown1980/yang-mills-4-dimensional-continum-proof/blob/main/PROBLEM.md), [Shadow Cat PR #34](https://github.com/JesseBrown1980/yang-mills-4-dimensional-continum-proof/pull/34), and the [finite 3×4 spectral certificates](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/blob/main/README.md).

## Reproduce

```bash
python3 -I -X utf8 native/ym/results/s3_1x1_continuous_jump/test_s3_1x1_continuous_jump.py
```

Workflow `.github/workflows/s3-wilson-continuous-jump.yml` runs the hosted checker with negative controls and publishes a SHA-256-sealed HBP receipt. Once the result is committed the workflow must replay it byte-for-byte. **Do not infer a real-world physical mass from the dimensionless `J_E=J_B=1` example.**
