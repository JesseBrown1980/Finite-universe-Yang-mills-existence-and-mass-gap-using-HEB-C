# Issue #137 — exact two-residual full-physical Krylov rank, November 16, 2026

**Research draft — stage 1 of a proposed 20,736→20,738 residual-guided Galerkin extension.** The experiment uses the *two original rational low-energy trial vectors* already frozen in [PR #247](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/247). It does not scan 429 million physical orbit rows and does not modify accepted Stage C/D/E/F/G certificates.

Write (D=10^9), and let (u_i) be the two original trial states with distinct frozen 144-dimensional seed energy numerators (z_i). Define the exact full-physical residuals (r_i=(DH-z_i)u_i) and residual Krylov directions (t_i=(I-P_{m old})r_i), where (P_{m old}) is the **actual weighted-orthogonal projection onto the full 20,736-dimensional old Galerkin subspace**, not projection onto its 28,634 occupied physical orbit coordinates. Since (u_i) belong to that old subspace,

[
t_i=D(I-P_{m old})Hu_i,quad
langle u_i,t_jangle_W=0.
]

Therefore both full-physical residual directions can be represented by **at most two additional vectors** and the nested Galerkin dimension is 20,736 plus the exact rank of the new 2×2 Gram matrix.

## Exact rank certificate

Rebuild the original signed/weighted S₃ 72-move source for all nonzero K2 and selected K3 source rows. Reconstruct the original physical (r_1,r_2) amplitudes on all eight flat states, 8,034 nonflat K2 states, 147,344 K3 states and all touched K4 destinations. Independently compare each self norm to the original hashes in the frozen [PR #247 full-residual receipt](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/blob/research/y137-h429m-full-residual-projection-20261116/independent/y137-h429m-residual-projection-20261116/RESULT-H429M-FULL-RESIDUAL-PROJECTION-20261116.hbp).

Compute the exact cross Gram

[
T_{ij}=langle r_i,r_jangle_W-b_i^mathsf{T}G_{m old}^{-1}b_j,
qquad b_i=(D K_{m old}-z_i G_{m old})x_i,
]

using the physically weighted full residual cross action. Evaluate each old-space inverse term by eliminating the 8 flat + 132 K2 + 20,592 K3 independent coordinate directions, leaving a 4×4 positive definite integer Schur matrix. Signed 5×5 bordered Bareiss determinants supply all three numerator entries with one common strictly positive integer denominator. Require the original two diagonal projection entries and full residual norms to match their accepted SHA-256 receipts exactly.

**Rank decision:** if (T_{11}>0), (T_{22}>0), (T_{11}T_{22}-T_{12}^2>0), the new directions are independent and the Galerkin space gains **exactly two** dimensions: 20,738. If determinant zero, the new rank is lower and the code reports that instead of asserting 20,738.

**Exact old-to-new Hamiltonian couplings:** physical self-adjointness implies (langle u_i,Ht_jangle_W=T_{ij}/D) for these two original source trial vectors. This is an exact 2×2 subblock. A **complete new projected Ritz calculation** additionally requires (K_{t_it_j}=langle t_i,Ht_jangle_W), and subsequently new eigenvectors, full-space residuals and the Wilson sample-specific transfer acceptance.

The source stage is designed to fail closed on frozen source/receipt changes, noninteger original weighted-flux divisions, nonpositive old Schur minors, missing reciprocal source actions, or disagreement with independent full-H self norms. No float calculations or unreviewed spectrum substitutions are allowed.

## Reproduce

```sh
python3 -I -B independent/y137-h20736-shell3-20261116/sparse_h20736.py real
python3 -I -B independent/y137-two-residual-krylov-20261116/exact_residual_gram.py toy
python3 -I -B independent/y137-two-residual-krylov-20261116/exact_residual_gram.py real
```

Hosted workflow: `.github/workflows/y137-two-residual-krylov.yml`. Record the exact rank, signed cross numerator digest, 2×2 determinant sign and coefficient bit lengths, and original receipt provenance. **Positive first Wilson spectral weight remains HOLD, issue #137 OPEN, and four-dimensional continuum mass gap OPEN.**
