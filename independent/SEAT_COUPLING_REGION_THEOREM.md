# Finite S₃ 2×2 torus: certified coupling-region gap theorem

**Status:** Exact analytic extension of the **existing** Stage 2G `E0` upper enclosures and PR #9 / Stage 2H `E1` strict lower thresholds. It reuses the *same* finite 1,393-dimensional Hamiltonian and does not claim any lattice-size, continuous-gauge-group or 4D result.

## Hypotheses: verified finite Hamiltonian structure

For nonnegative couplings,
`H(JE,JB) = JE E + JB M`,
acting on gauge-invariant functions with the positive Gauss-orbit weighted inner product `<f,g>_W = sum_i w_i f_i g_i`.

The independently reconstructed and natively hash-matched operator has:

- `E`: 1,393 × 1,393 weighted-self-adjoint electric graph Laplacian, nonpositive offdiagonal, zero row sum; `0 <= E_ii <= 24`. Hence `E` is positive semidefinite, and every Gershgorin disk is contained in `[0,2 E_ii] ⊆ [0,48]`. The matrix is diagonally similar to a symmetric matrix, so its eigenvalues are real and `||E||_W <= 48`.
- `M`: a diagonal magnetic potential, `M_ii∈{0,...,12}`, so `||M||_W <= 12`.
- The electric offdiagonal graph is connected, so for **JE > 0** its stoquastic Hamiltonian has an irreducible positive ground state (Perron–Frobenius), unique in the finite sector, irrespective of JB≥0. **A strictly positive finite-dimensional gap follows qualitatively for every JE>0, JB≥0.** No quantitative constant uniform over the entire unbounded/open parameter range is asserted.

The linked independently written script `independent/seat_coupling_region.py` regenerates the complete original integer operator from PR #7, checks all 1,393 row sums, Gershgorin conditions, offdiagonal signs, orbit weights, weighted Hermiticity and magnetic bounds, and insists the two pinned PR #9 1,393-pivot complete inertia receipts are present. It uses `seat_integer_ratio.IntegerRatio`, whose numerator and denominator are both Python `int` values; comparisons use exact integer cross-products and division constructs reduced integer pairs, never floating point or `fractions.Fraction`. No new diagonalization is performed.

## Exact Weyl/Lipschitz proof

Let `λ0(J)<λ1(J)≤...` be the energy eigenvalues ordered with multiplicity. For two coupling pairs `J,J0`, write

`δH = (JE-JE0) E + (JB-JB0) M`.

The spectral norm satisfies

`||δH||_W ≤ 48 |JE-JE0| + 12 |JB-JB0|`.

Weyl's inequality applied to `λ0` and `λ1` separately gives

`|[λ1(J)-λ0(J)] - [λ1(J0)-λ0(J0)]| ≤ 2||δH||_W`.

Thus, **for all nonnegative couplings on this same fixed 1,393-dimensional model**, if a baseline gap is rigorously `g(J0)>L`, then

`g(J) > L - 96 |JE-JE0| - 24 |JB-JB0|`.

This remains a valid inequality when the right-hand side is negative, but establishes a **strict positive lower bound** only where the right-hand side is positive.

The baseline certified inputs, *not freshly re-proved by this script*, are:

| Couplings | Original Stage 2G bound `E0 ≤` | PR #9 independent Stage 2H bound `E1 >` | Strict `g >` |
|---|---:|---:|---:|
| `1,1` | `7.634199` | `13.240` | `5.605801` |
| `3,5` | `36.699228` | `50.840` | `14.140772` |

## New finite coupling-region results

For **every real coupling pair**, not only sampled rationals, in either closed box:

| Region | Electric coupling `JE` | Magnetic coupling `JB` | Strict finite-model gap lower bound |
|---|---|---|---|
| Near (1,1) | `[99/100,101/100]` | `[19/20,21/20]` | `g > 3.445801` |
| Near (3,5) | `[59/20,61/20]` | `[24/5,26/5]` | `g > 4.540772` |

The first rectangle consumes no more than `96(1/100)+24(1/20)=2.16` of the initial strict `5.605801` baseline. The second consumes `96(1/20)+24(1/5)=9.6` of the initial strict `14.140772` baseline. These coarse but exact constants are **not** optimal, and neither computation assumes `E1` is isolated from `E2`.

Since `H(s JE, s JB)=s H(JE,JB)` for any real `s>0`, multiplying each certified rectangle by a positive scale `s` scales its gap bound by `s`. These conical families remain strictly positive for each `s>0`, but the bound tends to zero as `s→0`.

## Why there is no coupling-global uniform gap

At the origin `H(0,0)=0`, and the gap is exactly zero. More strongly, **JE=0, JB>0** has eight magnetic-only flat-connection ground states, so `g(0,JB)=0`. Along `(JE,JB)=(ε,ε)`, `g(ε,ε)=ε g(1,1)→0`. Even on the normalized simplex `JE+JB=1`, `JE→0` gives `g→0` by the `||JE E||≤48JE` Weyl bound. Therefore it is mathematically impossible to prove a single `c>0` valid across **all** positive couplings without restricting normalization away from these degeneracies.

Conversely, on any **compact** finite-coupling subset bounded away from `JE=0`, the finite eigenvalues vary continuously and the qualitative gap is strictly positive everywhere; compactness guarantees some positive uniform constant, though this is not an explicit constructive bound outside the regions above.

## Reproduction and acceptance

```bash
python3 independent/seat_coupling_region.py > /tmp/seat_coupling_region.measure
cmp /tmp/seat_coupling_region.measure independent/seat_coupling_region.measure
```

The dedicated GitHub Actions workflow independently executes the mathematical source rebuild, checks exact output and rejects missing anchors. Every line ends `json=0`.

**Remaining scientific gates:** coupling coverage beyond these regions by tighter uniform estimates and a range of lattice sizes, an independently specified continuous-group gauge theory and controlled thermodynamic/continuum limits, and an axiom-compliant 4D quantum Yang–Mills construction. No statement here closes the Clay Millennium problem.

## Integer-only execution invariant

All numerical proof code in this branch represents every exact ratio as a reduced pair of Python integer numerator and integer denominator. No `fractions.Fraction`, native `float`, `Decimal`, complex arithmetic, numerical eigensolver, or floating-point timing is used by these verifier paths. The `seat_integer_only_gate.py` CI gate parses all independent seat Python sources, rejects forbidden numeric constructs, and exercises integer-pair arithmetic self-tests. Pinned certificate text remains byte-identical after the refactor; the mathematical rational endpoints have not changed.
