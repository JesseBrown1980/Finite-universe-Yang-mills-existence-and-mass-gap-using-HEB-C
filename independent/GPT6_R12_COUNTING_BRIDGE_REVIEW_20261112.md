# Independent mathematical review: the r=12 spectral-counting bridge

Date: 2026-11-12. Scope: finite 3×4 S₃ Hamiltonian in the **48-symmetry-invariant sector**, subject to the explicitly recorded finite graph, tail-cap and orbit-reduction hypotheses. This derivation is mathematically independent of the spectrum-fitting routines.

## 1. Ground-state transform (weighted Z-matrix lemma)

Let `A` be real symmetric with `A[i,j] <= 0` for distinct indices and `u[i] > 0`. For any real vector `x`, the exact identity is

```
x^T A x - sum_i ((A u)_i / u_i) x_i^2
  = sum_{i<j} (-A[i,j]) u_i u_j
      * (x_i/u_i - x_j/u_j)^2 >= 0.
```

Thus `A >= diag((A u)_i/u_i)`. The identity holds with arbitrary real entries and is verified by expanding each square and comparing diagonal/off-diagonal terms. **It requires symmetry and the Z-matrix sign property**; a mere positive vector does not make it true for arbitrary matrices.

For a class-reduced operator `H` self-adjoint under positive diagonal weights `W`, use the symmetric congruence `A = W^(1/2)(H-tI) W^(-1/2)` and `u = W^(1/2) f`. The resulting quadratic-form lower bound is `W(H-tI) >= W diag((H-tI)f/f)`. No factor of `W` may be dropped when taking an inverse.

## 2. First Schur comparison, non-flat core C versus tail T

Partition `H-tI` into C/T blocks. Let `f>0` on all tail states and `D_T = diag(((H_TT-tI)f)/f)>0`. By the identity above, `W_T(H_TT-tI) >= W_T D_T >0`. Therefore, in the Loewner order on symmetric matrices,

```
0 < [W_T(H_TT-tI)]^(-1) <= (W_T D_T)^(-1).
```

Schur complementation of the symmetric `W(H-tI)` gives a lower comparator `W_C G(t)` when its exact C-to-tail entries and `D_T` use the same canonical tail/core graph. Consequently, by Haynsworth/Sylvester inertia,

```
N_<t(H in invariant sector)
  = n_-(Schur_C(W(H-tI)))
  <= n_-(W_C G(t)).
```

The equality uses **strict positivity of the entire T block**, not merely positivity of selected tail diagonal entries. The source tail-cap check must cover **every** tail orbit, and the canonical C/T edge table must truly correspond to the Hamiltonian in the 48-symmetry-invariant subspace.

## 3. Second Schur comparison, reduced core L versus its complement R

Set `B=W_C G(t)`, symmetric, and split the core into L/R by magnetic number. If `g>0` on all R and `d=G_RR g>0` componentwise, the same sum-of-squares identity yields

```
B_RR >= diag(W_a d_a / g_a) > 0.
```

Thus

```
B_RR^(-1) <= diag(g_a/(W_a d_a)).
K = B_LL - B_LR diag(g_a/(W_a d_a)) B_RL.
Schur_L(B) >= K.
N_<t(H in invariant sector) <= n_-(K).
```

Because any symmetric `X>=Y` satisfies `n_-(X)<=n_-(Y)`, this inequality is in the correct direction for a **lower bound on the (k+1)st invariant-sector eigenvalue**.

If each positive diagonal coefficient is rounded **up** to a dyadic multiple of `2^(-80)`, then `K_rounded <= K`. Its inertia is conservative: `n_-(K) <= n_-(K_rounded)`. Rounding down, or omitting `W`, can invalidate the claimed counting bound.

## 4. Exact inertia and independently checked cases

The frozen test has three thresholds (coupling `r=12`, cutoff 9, weight word `6,5,4,3`):

| Threshold t | Small L block | Previously reported n₋(K) | Permitted conclusion |
| --- | ---: | ---: | --- |
| 104.55 | 73 | 1 | Invariant-sector second eigenvalue ≥ 104.55 |
| 104.70 | 73 | 2 | Invariant-sector third eigenvalue ≥ 104.70 |
| 110 | 3 | 3 | Invariant-sector fourth eigenvalue ≥ 110 |

Our independent implementation re-parses the immutable canonical row table, reconstructs **every** weighted core/tail coefficient and reciprocal edge, checks the exact positive R-block witness, upward dyadic rounding, and all Bareiss divisibilities, then compares the sign changes to the three frozen inertia counts. Only these direct checks can establish that the particular numbers above were calculated without a hidden error.

Ritz upper bounds from three zero-extended trial vectors are logically separate from this counting lower bound. A positive invariant-sector first gap follows only after the comparison and Ritz enclosures are both accepted.

## 5. Explicit unresolved proof obligations

1. Reconstruct the full 111,906-orbit Hamiltonian or its complete symmetry-block decomposition and exclude lower nontrivial symmetry-sector excitations. None of the invariant-sector counts accomplishes this.
2. Independently validate the 48-class orbit identification, all C-to-T move multiplicities and the tail cap's **all-orbit** coverage. The algebra above is conditional on that mapping.
3. Retain the distinction between the non-flat **principal submatrix** and the actual full-space excitation spectrum. Interlacing a principal submatrix does not by itself place all missing whole-space eigenvalues.
4. The protected `r=9` launch cannot start without the independent sixth floor-freeze verdict and explicit user authorization. No scalar lower floor by itself gives spectral multiplicity or a continuum mass gap.

**Verdict:** The two Schur counting inequalities are mathematically correct under their stated symmetric-Z-matrix, positive-witness, full-tail and orbit-reduction hypotheses. Verification of the underlying representation and non-invariant sectors remains separate work.
