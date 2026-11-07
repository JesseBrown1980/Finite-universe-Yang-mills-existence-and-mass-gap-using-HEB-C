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

## Hosted measured results — 2026-11-07 UTC

[Dedicated GitHub Actions run 42332389073](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/42332389073) **PASS**. It ran the project's strict integer audit on the added script, reconstructed all 11 orbit states and their weighted Hamiltonian, verified interacting/electric characteristic polynomials, counted both lowest interacting levels by exact integer symmetric inertia, and recomputed the 43-million-step Wilson trial correlation using 144-term exact rational enclosures. The full 29-row hosted HBP output is pinned in [MEASURED-20261106.hbp](MEASURED-20261106.hbp), preserving the preregistered numerical miss.

**First interacting finite gap**: `1.096113 < E0 < 1.096114`, `3.274551 < E1 < 3.274552`, hence `2.178437 < E1−E0 < 2.178439` at `J_E=J_B=1`. This is a separate finite 1×1 system, not the 3×4 Perron certificate.

**Gauge-invariant Wilson trial correlation at dimensionless Euclidean time t = 1**:

| Number of finite time steps N | Certified correlation interval | Certified absolute error to continuous-time semigroup |
|---:|---|---|
| `27` | [0.053826033701524255, 0.053826033701524256] | [0.002990598483824288, 0.002990598483824289] |
| `81` | [0.055776224779961874, 0.055776224779961875] | [0.001040407405386669, 0.001040407405386670] |
| `243` | [0.056464430804065222, 0.056464430804065223] | [0.000352201381283321, 0.000352201381283322] |
| `729` | [0.056698611679000604, 0.056698611679000605] | [0.000118020506347939, 0.000118020506347940] |
| `19,683` | [0.056812249867264573, 0.056812249867264574] | [0.000004382318083970, 0.000004382318083971] |
| `531,441` | [0.056816469861863712, 0.056816469861863713] | [0.000000162323484831, 0.000000162323484832] |
| **`43,046,721 = 3^16`** | **[0.056816630181347677, 0.056816630181347678]** | **[0.000000002004000866, 0.000000002004000867]** |
| **Continuous-time `e^{-H}` reference** | **[0.056816632185348543, 0.056816632185348544]** | 0 by definition |

The continuous-time value is a **mathematical limit of the same finite spatial Hamiltonian**, not a measurement from nature or a physical spacing limit. There is **no claim of convergence of 4D SU(2) lattice theories as their spatial spacing approaches zero** here.

**CRT and jumps:** Chinese-remainder reconstruction independently matched the first **eight exact integer moment numerators** under a rigorous bound below half the two-prime modulus product, with source values `p1=1000081` and `p2=1000003`. Separate modular power cubing and binary powering matched for all seven specified powers of three at each of those primes; direct stepping checked short runs. The residues of a high power do **not** reconstruct the huge real or rational state vector. The rational Taylor/binomial arithmetic, not the modular residue alone, establishes the reported physical-time correlation interval.

**Falsifier preserved:** prediction 10's `0.0568166301459` point expectation **MISSED**; the measured exact-rational bracket is `0.056816630181347677..678`. Its preregistered broad error interval of 1–3×10⁻⁹ held. This is an observed prediction miss, not a failed source-code checker.

**Relevant other repo results:** [Matrix Law Essentials PR #7](https://github.com/JesseBrown1980/The-matrix-law-essentials/pull/7) established an efficient `3^16` phase jump for a *reduced* nanoparticle grating model, not raw experimental replay; [CO ensemble PR #6](https://github.com/JesseBrown1980/The-matrix-law-essentials/pull/6) showed mean-error phase cancellation but persistent individual RMS errors in classical molecular models; [YM4 PR #34](https://github.com/JesseBrown1980/yang-mills-4-dimensional-continum-proof/pull/34) checked the exact retained Shadow Cat trit residual and showed an `S3` bare signed holonomy is not a gauge-invariant observable. These results are compatible methodological tests, not evidence that one experiment validates the others' physics. Their common lesson is that an efficient finite representation and a controlled observation map are possible; physical model validation and uniform continuum limit are **distinct proof obligations**.

## November 7: the **interacting vacuum**, not the previous trial vector

**Hosted result:** [GitHub Actions 42374612872](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/42374612872) **PASS**. Both the original PR #127 finite-`S3` trial-state test and the new **actual vacuum** test passed, as did four explicitly sabotaged negative controls. The true-vacuum test's 15 predictions were committed **before code** at `f24a0a890efeb1d058bb300b1e629ac52f44020f`. The first attempted hosted run exposed a billion-vs-quintillion spectral-filter coefficient mismatch; a subsequent run found one miswired sabotage. Both implementation failures remain in the CI history, while the predictions were **never rewritten**. Final 33-row hosted record: [MEASURED-INTERACTING-VACUUM-20261107.hbp](MEASURED-INTERACTING-VACUUM-20261107.hbp).

### 1. Identify the *physical finite* gauge vacuum

The 11×11 orbit-weighted Hamiltonian `H=E+M` is reconstructed independently from the original 36 link pairs, and is self-adjoint for the orbit-weight inner product `<x,y>_W=Σ_i w_i x_i y_i`. All **11** states are already gauge-invariant. Let `|Ω>` denote the normalized, positive, nondegenerate **lowest eigenvector of this interacting Hamiltonian**; unlike the earlier uniform trial vector, it solves `H|Ω>=E0|Ω>`.

Construct an integer vector `v=(18I−H)^729 (1,...,1)`, with every component strictly positive. Using the irreducible nonnegative Perron matrix `18I−H` and the Collatz–Wielandt inequalities gives an exact *rational* bracket for `E0`. The exact W-weighted Rayleigh residual and independently certified lower bound `E1>3.274551` then give

```text
1.096113506743925734 < E0 < 1.096113506743925735  [displayed outward]
ground-state excited-amplitude fraction after normalizing v < 1e-24
```

The actual rational Collatz bracket is **narrower than 10⁻²⁴**, despite the displayed 18-digit endpoints. The angular certificate is based on `||(H−<H>)v||_W / ((E1_lower−<H>)||v||_W)`. The method does **not** assume that `v` is already an exact eigenvector.

### 2. Exact operator selection rule: the first excited state is dark to the plaquette Wilson loop

Define the gauge-invariant observable

```text
O(a,b) = χ_std(a b a⁻¹ b⁻¹)
P3(x) = x³ − 21x² + 135x − 252
P5(x) = x⁵ − 36x⁴ + 468x³ − 2655x² + 6138x − 4104
charpoly(H) = (x−6)³ P3(x) P5(x).
```

Let `K=(H−6I)P3(H)`. **Exact integer matrix multiplication** verifies `rank(K)=5`, `P5(H)K=0` and `P5(H) O K=0`. Therefore `im(K)=ker(P5(H))` is an invariant five-dimensional Wilson-observable sector. The ground state belongs to that sector, but the **first excited eigenvalue** belongs to the complementary cubic `P3` sector. Since `H` is self-adjoint in the physical orbit-weighted inner product, states in these different spectral sectors are orthogonal.

Consequently,

```text
< E1 | O | Ω > = 0     EXACTLY (not merely numerically small).
```

The finite first gap still exists and is independently bracketed by integer symmetric inertia:

`2.178437 < E1−E0 < 2.178439` in `J_E` units.

But the **first excitation visible to this particular plaquette Wilson operator is `E2`**, in the same quintic sector as the ground state. Its separate exact root enclosures give

`3.565389 < E2 < 3.565390`, hence

`2.469275 < E2−E0 < 2.469277` in `J_E` units.

The test bounds nonzero spectral overlap using degree-four Lagrange polynomial filters **within the exactly invariant five-dimensional subspace**. Each approximate eigenprojector is checked by exact rational interval arithmetic at all five independently isolated roots, with operator error below `10⁻⁴`. The certified spectral weights include conservative `10⁻³` allowances for filtering and vacuum approximation:

| Full spectrum index (zero-based) | Energy above interacting vacuum | Wilson spectral weight `|<n|O|Ω>|²` |
|---|---|---|
| 1 | 2.178437–2.178439 | **0 exactly: dark to this Wilson loop** |
| 2 | 2.469275–2.469277 | **0.352632039–0.354632040** |
| 7 | 6.874226–6.874228 | 0.677360378–0.679360379 |
| 8 | 8.405668–8.405670 | 0.469141665–0.471141666 |
| 10 | 12.770260–12.770262 | 0.150021542–0.152021543 |

The ground `n=0` contributes only the disconnected term `<O>²`; that term is subtracted in the connected correlation. The other cubic-sector and `x−6` excitations are also invisible to this local Wilson operator in this 11-state model.

**Critical distinction:** the `n=1` state is **not unphysical**. It is a legitimate gauge-invariant state of the finite theory, but the chosen plaquette operator has exactly zero overlap with it. Therefore its connected correlator cannot be used alone to measure the true first gap.

### 3. Actual vacuum-connected, gauge-invariant Euclidean correlator

This time the object is the vacuum expectation, **not** the uniform trial-state matrix element of the earlier experiment:

```text
m = <Ω|O|Ω>  ≈ 1.2725570364975
C_O(t) = <Ω| O exp[-(H−E0)t] O |Ω> − m²
       = Σ_{n>0} |<n|O|Ω>|² exp[-(En−E0)t].
```

| Euclidean time `t` in inverse-`J_E` units | Certified connected correlation interval |
|---:|---|
| 0 | [1.653155625358, 1.653155625359] |
| 1 | **[0.030740631048, 0.030740631049]** |
| 2 | [0.002534511906, 0.002534511907] |
| 3 | [0.000214474028, 0.000214474029] |

The numerical enclosures use only integer numerator/denominator pairs. The ground vector is certified to have excited-state admixture less than `10⁻²⁴`. The stored rational energy shift `1096113506743925734/10¹⁸` is within `10⁻¹⁸` of `E0`, independently checked against the Collatz bracket. A 192-order exact Taylor moment expansion and the `0≤H≤15` spectral bound make the truncation tail smaller than `10⁻³⁰` for `0≤t≤3`. Combining that remainder, the vacuum-approximation bound and the shift error gives a conservative total absolute bound below `10⁻¹⁴` for all reported correlation values; displayed 12-digit intervals round **outward**.

### 4. Slice-by-slice versus 43-million-step matrix jump

Using the *same interacting vacuum* and rational shift, compare `(I−t(H−E_shift)/N)^N` at **fixed `t=1`**, with `N=3^k`, against `exp[-(H−E0)]`. The exact rational binomial series uses the same 192 certified integer moments, without allocating a 43-million-step state. Independently, `16` repeated cubings of the shifted 11×11 transfer operator **modulo each of two primes** agree with independent binary exponentiation. These modular comparisons verify the jump algorithm; they do not reconstruct the full huge rational state or its real continuum observable.

| `N` steps | True-vacuum connected `C_N(1)` | Error `C(1)−C_N(1)` |
|---:|---:|---:|
| 27 | 0.026803649194–0.026803649195 | 0.003936981853–0.003936981854 |
| 81 | 0.029386100449–0.029386100450 | 0.001354530598–0.001354530599 |
| 243 | 0.030284050454–0.030284050455 | 0.000456580593–0.000456580594 |
| 729 | 0.030587861541–0.030587861542 | 0.000152769506–0.000152769508 |
| 19,683 | 0.030734962567–0.030734962568 | 0.000005668480–0.000005668481 |
| 531,441 | 0.030740421090–0.030740421091 | 0.000000209957–0.000000209959 |
| **43,046,721** | **0.030740628456–0.030740628457** | **0.000000002591–0.000000002593** |
| Continuous time | **0.030740631048–0.030740631049** | 0 by definition |

These results improve the **finite-model physical interpretation**, not the statement about the spatial or infinite-volume continuum. Increasing the number of **time slices for the same finite spatial lattice** is not the (a	o0) Wilson lattice limit. Neither the finite first-gap value nor the Wilson-visible gap is a measured real-world particle mass. A spatial-size/coupling scaling family and valid four-dimensional SU(2) construction remain necessary for the Clay problem.

### Reproduce and provenance

```bash
python3 -I -X utf8 native/ym/results/s3_1x1_continuous_jump/test_s3_interacting_vacuum.py
```

The GitHub workflow checks the exact sector, five spectral projectors, four rigorous connected-time values, seven ternary slices, two independent 43M modular jumps, and **four deliberately false statements** (uniform vector is true vacuum, wrong signed observable, E1 visible, wrong cubing). The predictions are fixed in [PREDICT-INTERACTING-VACUUM-20261107.hbp](PREDICT-INTERACTING-VACUUM-20261107.hbp), and the complete certified output is in [MEASURED-INTERACTING-VACUUM-20261107.hbp](MEASURED-INTERACTING-VACUUM-20261107.hbp). Do not rewrite the earlier trial-state HBP receipt or its numerical prediction miss. The mathematical root and overlap certificates refer only to the **finite (S_3) 1×1 torus at (J_E=J_B=1)**.
