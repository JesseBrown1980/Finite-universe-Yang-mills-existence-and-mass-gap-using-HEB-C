# Y137 — exact CRT and Berkowitz verification of the 12×12 generalized Krylov Hamiltonian

**Research draft, November 16, 2026.** Completely separate exact-integer verification of [PR #238](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/238). Input is its frozen eight-flat/four-Krylov 12×12 weighted Gram \(G\) and Hamiltonian \(K\), identified by Git object hash and their original independent SHA-256 records. No full-space Wilson positivity claim.

## Hosted exact result — November 16, 2026

[Original hosted run #43956875971](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43956875971) completed both source and real calculation jobs successfully. The entire original numerical output is pinned in [RESULT-H12-MODULAR-20261116.hbp](RESULT-H12-MODULAR-20261116.hbp), with independent source Git blob and original 12×12 matrix fingerprint. Its workflow must reproduce every numerical row byte-for-byte.

| Verification | Exact result |
| --- | --- |
| Full generalized polynomial degree | 12 |
| Reduced determinant polynomial degree | 8 |
| Coefficient comparison, full vs reduced | **13/13 exact** |
| Eigenvalue 72 (projected multiplicity) | **Exactly four** |
| Full 12×12 Gram leading minors | **12/12 positive** |
| Original fixed energy negative inertia | **0, 1** |
| Ritz lower/upper boundary negative inertia | **0→1, 1→2** |
| Maximum primes for a reconstructed leading determinant | **34** certified 31-bit primes |
| Original Ritz intervals | **Unchanged, exact** |
| Full-space residual / Wilson spectral weight | **NOT COMPUTED / HOLD** |

The exact full degree-12 coefficient SHA-256 is `addfa148103001666e15805a976b565a90782b939e619d70319110e2f179d040`; the reduced degree-eight coefficient SHA-256 is `a5aa36775e079cd7d4c468c008108f582d10b30103c5062ac8a6fc61ae2721fd`. The polynomial identity is an **exact algebraic optimization**; no practical wall-clock speed advantage has yet been demonstrated. The original Ritz energy enclosures remain (69.924680131ldots69.924680132) and (69.963663574ldots69.963663575).

## New structural result: four exact flat Ritz values

The original *physical-weighted generalized pencil* has block form

\[
G=\begin{pmatrix}W&0\\0&G_4\end{pmatrix},
\qquad
K=\begin{pmatrix}72W&C\\C^\mathsf T&K_4\end{pmatrix},
\qquad W=\operatorname{diag}(1,3,2,3,3,2,2,2).
\]

By the block determinant identity, for an exact integer energy numerator \(z\) with \(D=10^9\),

\[
\boxed{
\det(zG-DK)=432(z-72D)^4
\det\Big((z-72D)(zG_4-DK_4)-D^2C^\mathsf TW^{-1}C\Big).
}
\]

Both sides are **polynomials over \(\mathbb Z[z]\)**. The projected \(C^\mathsf TW^{-1}C\) is an integer 4×4 matrix for this frozen physical source. The rightmost determinant has degree eight, rather than twelve. If \(\det(C^\mathsf TW^{-1}C)\ne0\), exactly **four** generalized Ritz eigenvalues equal 72; the remaining eight are the roots of the reduced polynomial. This decomposition follows from the rank of the \(8\times4\) flat–Krylov coupling, **without presuming a gauge/translation-group symmetry projector**.

The exact original matrix gives \(\det(W)=432\), a full-rank \(C^\mathsf TW^{-1}C\), and equality of all 13 coefficients between two **independent polynomial constructions**:
- Full 12×12 **Samuelson–Berkowitz division-free** characteristic recurrence over the commutative ring \(\mathbb Z[z]\), extracting \(\det(zG-DK)\).
- Separate 4×4 Samuelson–Berkowitz computation on the reduced *quadratic-polynomial matrix*, multiplied by \(432(z-72D)^4\).

This is not the characteristic polynomial of \(K\) alone, which would have the wrong eigenvalues because \(G\ne I\).

## Independent modular-CRT inertia

At both original sample energies and the four earlier accepted one-billionth Ritz-bracket endpoints, the verifier computes all 12 leading principal determinants of \(DK-zG\) by:

1. Deterministic primality tests and **31-bit prime-field Gaussian elimination**. Inverse pivots are taken modulo primes, not by applying integer Bareiss division in finite fields.
2. Incremental integer CRT, with a rigorous row-\(\ell_1\) Leibniz determinant bound \(|\det A|\le\prod_i\sum_j|a_{ij}|\). The *signed* integer determinant is uniquely reconstructed only after the CRT modulus \(M>2B\).
3. One extra, previously unused prime to detect accidental reconstruction/coding mistakes, exact Sylvester inertia from leading-minor signs, and direct comparison of the full determinant against the independently calculated Berkowitz polynomial evaluated at the same exact integer energy numerator.

The positive 12×12 Gram is similarly certified. The old independent full-12 Bareiss verifier is retained, providing **three complementary exact routes**: source row/pair projection, fraction-free full determinant signs, and prime-field CRT with a division-free polynomial factorization. The modular method is a correctness/cost experiment; practical speedups must be measured against the established implementation on the same hardware and bit sizes.

## Why no automatic Maschke/Wigner micro-blocks?

The finite project uses a **3×4** periodic torus, whose translation group is \(\mathbb Z_3\times\mathbb Z_4\), rather than \(\mathbb Z_L^2\). The physical basis has already been quotiented by local gauge symmetry. Character projectors can block diagonalize a Hamiltonian **only after** a concrete group action \(U(g)\) is verified on the *chosen* 12-dimensional subspace and is shown to preserve both \(G\) and \(K\). No such nontrivial representation is currently certified for this particular sample-selected Krylov space. The explicit algebraic factorization above is an immediately valid structural reduction.

## Acceptance boundaries

- Verify source hash, dimensionality, W symmetry, frozen 12×12 matrices, exact polynomial coefficient identity, exactly-four degeneracy at energy 72, full 12×12 Gram positivity, and six exact inertia counts.
- Preserve previous Ritz intervals:
  \(\lambda_1^{(12)}\in(69.924680131,69.924680132)\) and
  \(\lambda_2^{(12)}\in(69.963663574,69.963663575)\).
- Preserve **full-space residual NOT_COMPUTED**, **Wilson_weight HOLD**, and continuum \(\mathrm{SU}(2)\) OPEN. This is a certified *projected* problem, not proof of an actual whole-space eigenvalue or first-excitation Wilson transition.
- Do not merge into main before independent hosted verification and reviewer acceptance.

## Run

\`\`\`sh
python3 -I -B independent/y137-h12-modular-20261116/modular_berkowitz.py toy
python3 -I -B independent/y137-h12-modular-20261116/modular_berkowitz.py real
\`\`\`
