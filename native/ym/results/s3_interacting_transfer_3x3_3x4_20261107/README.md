# Interacting 3×3: transfer the certified first gap to the full Hilbert space; 3×4: exact flat-state winding selection

**Status: prediction-first certificate-composition experiment.** The 13 predictions in [PREDICTION.hbp](PREDICTION.hbp) were frozen at commit `550926527cda3ed7024d6bc91e638ce12ab4dc9d` **before** the checker was written. This program independently reconstructs the small magnetic-flat configurations and audits **preexisting** 3×3 full-space and zero-momentum HBP certificates. It does **not** run a fresh 10,097,891-dimensional inertia calculation or construct the 2,177,317,873-dimensional 3×4 Hamiltonian.

## 1. New full-3×3 first-gap consequence from existing independent certificates

The original [full physical-space certificate](../3x3_full_space/CERTIFY-RESULT.md) at `J_E=1, r=J_B/J_E=9` (hosted run [40725530804](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/40725530804)) proves by its stored exact interval-inertia calculations:

```text
dim(H_full) = 10,097,891
dim(H_zero-momentum T) = 1,122,211
N_full(52.533422) = N_T(52.533422) = 8
N_full(71.900000) = N_T(71.900000) = 8
=> E_9^full(9) >= 71.900000 J_E
```

(The ordering `E₁,E₂,…` here is **one-based** in the native first-gap reports.) The original HBP [CERTIFY-3X3-FULLSPACE.hbp](../3x3_full_space/CERTIFY-3X3-FULLSPACE.hbp) includes all **340 green `NNEST` nodes** of the verified full-space certificate.

Now use an **exact fact about the Hamiltonian itself**: the periodic 3×3 `S₃` lattice has exactly **eight independent magnetic-flat, gauge-invariant configurations**. All eight lie in the zero-spatial-momentum sector `T`. On the eight-dimensional flat trial subspace, the electric operator has the exact compression

```text
P_flat H(r) P_flat = 54 I_8,   at every coupling r>=0.
```

Why: there are 18 oriented links; each has three transposition moves, giving diagonal electric energy `18×3=54`. Every one-link transposition move out of a flat state produces nonzero plaquette potential, so there are no flat-to-flat electric transitions. The magnetic term vanishes on every flat state. Thus the min–max principle gives

```text
E_8^T(r) <= 54.
```

The magnetic term is nonnegative, so for **all `r>=9`**, `H(r)-H(9)=(r-9)M>=0` and `E_9^full(r)>=E_9^full(9)>=71.9`. Therefore

```text
E_8^T(r) <= 54 < 71.9 <= E_9^full(r),   all r>=9.
```

This forces **every one of the lowest eight full-space levels into the zero-momentum `T` sector for every `r>=9`**. It is not just an observation at `r=9`. It is an exact **certificate-composition theorem**, provided the original pinned full-space certificate and the magnetic-flat Hamiltonian identities hold.

### The full-space first gap at r=27 follows

The existing [pinned zero-momentum 3×3 sector reference](../../reference/ym3x3_frozen_8fd12e6.hbp), from `The-matrix-law-essentials` commit `8fd12e6a54354f0b7483e05db56eeec97946a81c`, contains the independently preexisting exact `SHELL_CLUSTER_CERT|L=3x3|r=27`:

```text
N_T(t0)=0,       N_T(ts)=1
E1^T(27) in [53.493345, 53.493390] JE
E2^T(27) in [53.495357, 53.495404] JE
E2^T-E1^T in [0.001967, 0.002059] JE
```

By the global low-eight transfer proved above, the **same E₁ and E₂ are the first two levels of the complete 10,097,891-state Hamiltonian**. The full finite 3×3 first gap therefore satisfies

```text
0.001967 <= E2^full(27)-E1^full(27) <= 0.002059  (JE units).
```

This is a substantive **new logical consequence of previously certified** r=9 full-space and r=27 zero-momentum bounds. The new checker revalidates their recorded rows, threshold ordering, eigenvalue-count relations, min–max hypotheses, exact interval subtraction and source provenance. It does **not** independently redo the underlying 10-million-state or 1.12-million-state inertia. Acceptance of the numerical enclosure depends on the authenticity and correctness of those earlier certificates; if either source is withdrawn, the composed statement must be withdrawn as well.

For `r=243`, the same global low-eight-to-`T` identity remains valid, **but** the pinned reference explicitly says `first_splitting=INCONCLUSIVE`. That remains **OPEN**; the new test refuses to invent a numerical first-gap interval.

The pinned sector's `(1,1)` sign label for the first level at `r=27` **is not an independent determination of the spatial axis-exchange parity**. The actual `O_+` versus `O_-` interacting first-state overlap remains **OPEN**.

## 2. Independent eight-flat-state gauge and symmetry construction

Flat periodic `S₃` connections are classified by commuting pairs of global torus holonomies `(a,b)`, modulo simultaneous conjugation:

```text
a b = b a
(a,b) ~ (gag⁻¹,gbg⁻¹).
```

The checker enumerates all 36 raw pairs, verifies **18 commute**, partitions them into **eight** simultaneous-conjugation orbits, and separately constructs actual flat link configurations on **both** 3×3 and 3×4 spatial tori. For each class, it explicitly verifies every plaquette is magnetic-flat, checks 54/72 single-link transposition moves for leakage out of flatness, and **constructively solves for the gauge transformation** identifying each one-step x/y translation with the original flat state. It does not rely only on assuming homotopy invariance.

On **3×3**, exchanging the two torus axes permutes the eight flat orbits in four fixed orbits and two swapped pairs. Therefore the flat subspace has

```text
exchange-even dimension = (8+4)/2 = 6
exchange-odd dimension  = (8-4)/2 = 2.
```

The gauge-invariant three-link winding characters restrict to

```text
O_+|flat = 3 [χ_std(a)+χ_std(b)]   (flat rank 7)
O_-|flat = 3 [χ_std(a)-χ_std(b)]   (flat rank 4).
```

The `O_-` operator reverses exchange parity; `O_+` preserves it. Both parity sectors exist among flat states, so this does **not** decide the actual interacting first excitation's parity by itself.

On **3×4** the sides differ, so *axis exchange is not a symmetry*. For every one of the eight flat gauge classes the horizontal winding traces along the four rows are identical, yielding the **new exact zero**

```text
O_alt|flat = χ(W_x(0)) - χ(W_x(1))
           + χ(W_x(2)) - χ(W_x(3)) = 0.
```

Thus `O_alt P_flat = 0` on the *exact magnetic-flat subspace*. Meanwhile

```text
O_xsum|flat = 4χ_std(a)    (nonzero diagonal rank 6)
O_ysum|flat = 3χ_std(b)    (nonzero diagonal rank 6).
```

**Practical consequence:** the earlier 3×4 translation-`π` alternating observable has **no direct flat-to-flat transition amplitude**; the zero-momentum winding sums are more natural starting probes for the low flat-dominated cluster. That is an exact operator-selection statement for `P_flat`, **not** a proof that the alternating operator is dark to the interacting `E₁`, because an interacting eigenvector generally has nonflat components. Before declaring that, we need an independent full-space 3×4 low-state symmetry count.

## 3. Fail-closed verification and limits

```bash
python3 -I -X utf8 native/ym/results/s3_interacting_transfer_3x3_3x4_20261107/verify_flat_transfer.py
```

The dedicated [GitHub workflow](../../../../.github/workflows/s3-interacting-3x3-gap-transfer.yml) checks the full-space certificate's original 340-node count, T/full threshold equality, the 8 flat orbit construction, both lattice magnetic potentials, every one-link flat-to-nonflat move, and the r=27 exact bracket subtraction. It also requires **six red controls** to exit unsuccessfully: corrupt the zero-momentum count, falsely report the r=27 interval, invent an r=243 interval, falsely assert nonzero alternating winding on a flat state, alter the flat electric 54, or assert a bare open link character is gauge invariant. The original HBP certificates and all earlier prediction files remain **unchanged**.

**Unresolved:** 3×3 true first-state axis-exchange parity, positive `O_+` or `O_-` interacting spectral weight; 3×4 *global* first gap, first-state momentum, and interaction-vacuum overlap; any uniform-in-volume physical-unit mass-gap bound as spatial spacing goes to zero; nontrivial 4D `SU(2)` continuum existence. These statements are **not** proved by the present certificate composition, and the Clay Millennium Yang–Mills problem remains **OPEN**.
