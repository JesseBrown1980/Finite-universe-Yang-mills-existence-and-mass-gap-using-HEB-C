# Independent unconditional 3×4 finite S₃ first-gap existence without the Perron store

**2026-11-08.** New standalone elementary proof for the FULL periodic spatial 3×4 finite-S₃ gauge-invariant Hamiltonian at r=9. It shows the physical first energy gap is **strictly positive** with an astronomically small but explicit exact lower bound, entirely independently of the 45,508,080-row Perron certificate. It does **not** prove the sharper 0.01 J_E numerical bound, positive first-excitation winding overlap, or a continuum physical Yang–Mills gap.

The 14-row [prediction](PREDICT-UNCONDITIONAL-3X4-S3-FIRST-GAP-20261108.hbp) was committed first, before the independent [checker](verify_unconditional_3x4_s3_first_gap.py). The checker never reads the original huge row store, positive vector, or Schur certificate.

## Step 1 — Burnside's lemma on the complete gauge-orbit space

There are V=3×4=12 vertices, E=2V=24 oriented positive links and V−1=11 spanning-tree links. Gauge fixing leaves 13 free S₃ elements modulo simultaneous conjugation at the root. Centralizer sizes for the 6 S₃ elements are 6 once, 2 three times, and 3 twice. Burnside gives

\[
N=\frac{6^{13}+3(2^{13})+2(3^{13})}{6}
=\boxed{2\,177\,317\,873}.
\]

The independent checker constructs S₃ from all permutations of three letters, recomputes every multiplication and centralizer and obtains the exact orbit count. The 45,508,080-row symmetry quotient is not substituted for the full orbit space.

## Step 2 — connected graph and simple ground state

The electric matrix is E=72I−A, where 72=24×3 is the number of elementary one-link transposition moves. Every one of the three transpositions is a unitary involution on link configurations, and together they generate all of S₃. Thus each of the 24 links can be changed independently along a transposition word: the original finite configuration graph is connected. Its image under local gauge equivalence is a connected gauge-orbit graph.

In the orbit-indicator basis, A is an irreducible nonnegative integer matrix (row transition counts), and H=J_E(E+rM) has nonpositive off-diagonals. The orbit-weighted positive inner product makes H similar to a real symmetric matrix. Add a sufficiently large scalar to −H and apply the classical Perron–Frobenius theorem for irreducible nonnegative matrices: the lowest eigenvalue of H is simple at every finite r≥0. Therefore

\[
\boxed{E_2(r)>E_1(r)\quad\hbox{for every finite }r\ge0.}
\]

This proof is **not** the earlier 45.5M-row numerical positive-vector Perron bound and requires no store. It establishes *strict positivity* on this fixed finite lattice only.

## Step 3 — unconditional explicit integer lower bound at r=9

Each of 12 plaquettes has magnetic cost 2−χ(g) ∈ {0,2,3}, so 0≤M≤36I. The 72 electric unitary involutions imply 0≤E≤144I. Hence the complete spectrum of H(9)/J_E is real and lies in [0,468].

The full gauge-orbit matrix H(9)/J_E has **integer entries** in the orbit-indicator basis, despite not being symmetric in the ordinary Euclidean inner product. Its characteristic polynomial p is monic over ℤ. The squarefree part q=p/gcd(p,p′) is also monic over ℤ, has m distinct *real* roots with 2≤m≤N, and has positive integer discriminant

\[
1\le \operatorname{disc}(q)
=\prod_{i<j}(\lambda_i-\lambda_j)^2.
\]

The physical first gap is one of the distinct root differences because the ground eigenvalue is simple. Every other difference is at most 468 in absolute value. Therefore

\[
\frac{E_2(9)-E_1(9)}{J_E}
\ge468^{-\left(\binom{m}{2}-1\right)}
\ge\boxed{468^{-2\,370\,356\,558\,953\,963\,127}}>0.
\]

The exponent is an independently checked integer. The bound is *vastly weaker* than 0.01 J_E. It does not turn the source-conditional 0.01 lower bound into an unconditional numerical estimate and cannot be used as a nonzero continuum-unit mass floor.

## Step 4 — additional independent arithmetic check on the large-r certificate

From the six source-stated nonzero entries of 16C₁ in the published 8×8 flat-sector Schur coefficient, the new script computes its characteristic polynomial by **two different integer algorithms**: signed principal-minor determinants and Newton power traces. Both give

\[
\det(zI-16C_1)=z^4(z^2-72^2)(z^2-24^2).
\]

Thus the first two source-stated coefficients have eigenvalue difference 3. The script also verifies the exact rational large-r remainder and outward enclosures at r=10000 and 100000, including the published interval [271961,328039]/10¹⁵ for r=100000. These checks are independent **spectral algebra** on the stated matrix; they are *not* a new independent re-enumeration of the 264 gauge orbits in the first shell. The prior horizontal-first checker already supplied that separate gauge-theoretic reconstruction.

## Stronger independent unconditional bound — ground-state transform and exact electric Poincaré inequality

After the original fourteen predictions and the discriminant proof were frozen, [eight supplemental predictions](PREDICT-GROUND-TRANSFORM-3X4-S3-FIRST-GAP-20261108.hbp) were **separately frozen before implementation** of a second, independently written [ground-transform checker](verify_ground_transform_3x4_s3.py). The original predictions, verifier and ten-row historical receipt remain unaltered.

**First: exact unperturbed electric spectral gap.** On one raw link the S₃ electric Laplacian is L=3I−Σ_t L_t, where t ranges over the three transpositions. The second checker reconstructs all six permutations, forms its exact 6×6 integer Cayley Laplacian and evaluates all principal minors. It obtains
\[
\det(zI-L)=z(z-3)^4(z-6),
\]
so the unweighted product electric operator on 24 links has **spectral gap exactly 3** (nontrivial eigenvalues are sums of the 24 independent-link eigenvalues).

**Second: a constant-size upper bound on raw graph distance.** Every S₃ group element has transposition word length at most two, as the checker proves by breadth-first enumeration of the six-element Cayley graph. Any two raw 24-link fields can therefore be connected by at most \(24\cdot2=48\) electric moves.

**Third: bound the positive ground state's condition number without calculating it.** Let \(g_x>0\) be the unique raw-field ground eigenvector of \(H(9)/J_E\), normalized arbitrarily. The matrix eigenvalue equation at each *raw field* x is
\[
(72+9M_x-\lambda_0)g_x
=\sum_{y\sim x}g_y,\qquad 0\le M_x\le36,\quad\lambda_0\ge0.
\]
Every neighbor contribution is positive, so for every electric edge \(x\sim y\),
\[
g_y\le396\,g_x,\qquad
396=72+9(36).
\]
Applying this inequality along a path of at most 48 electric moves gives
\[
\boxed{g_{\max}/g_{\min}\le396^{48}.}
\]
No value of \(g_x\) or full configuration-space eigenvector is required.

**Fourth: compare Poincaré Rayleigh quotients exactly.** For a real function f on the raw field space, the ground-state transform of the stoquastic operator gives the exact Dirichlet identity
\[
\langle gf,(H/J_E-\lambda_0)gf\rangle
=\tfrac12\sum_{x\sim y}g_xg_y(f_x-f_y)^2,
\]
where the sum is over directed electric edges and their multiplicity. Its numerator is at least \(g_{\min}^2\langle f,E f\rangle\); the squared distance of \(gf\) from the ground line is at most \(g_{\max}^2\min_c\sum_x(f_x-c)^2\). The exact electric spectral gap 3 therefore yields
\[
\Delta_{\rm raw}(H/J_E)
\ge3\left(\frac{g_{\min}}{g_{\max}}\right)^2
\ge\frac{3}{396^{96}}.
\]
Since H commutes with all local gauge transformations and its raw ground state is unique and positive, the raw ground state is gauge invariant. Restricting to gauge-invariant excitations cannot produce a lower first excited level than the unrestricted raw spectral gap. Thus for the **full 2,177,317,873-orbit finite physical Hilbert space**
\[
\boxed{\frac{E_2(9)-E_1(9)}{J_E}\ge\frac{3}{396^{96}}>0.}
\]

This bound is **much stronger** than the earlier discriminant-only \(468^{-2\,370\,356\,558\,953\,963\,127}\), but remains vastly smaller than the source-conditional measured \(0.01\). It also depends on the fixed finite number of links, and is **not uniform across increasing spatial volume or vanishing spacing**. Six independent false statements, including claiming a 0.01 unconditional floor, are required to fail closed. The checker certifies the integer denominator, not any numerical eigenvalue or first-excitation observable overlap.

## Verification gates still OPEN

- The sharper numerical 3×4 r=9 enclosure 0.01<(E₂−E₁)/J_E<0.07 still requires the accepted whole-nonflat compression floor 94.070673 J_E; an independent complete **second-machine full-row/full-pair** replay has not been run by this checker.
- The first-state translation-zero-momentum summed-winding observable weight remains **OPEN** under [issue #137](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/issues/137).
- Larger-lattice hybrid E₉ vector evidence requires an independently complete orbit-representative and positivity audit under [issue #100](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/issues/100).
- The 4D nontrivial SU(2) weak-coupling continuum construction and physical mass gap remain OPEN.

The hosted proof checker rejects eight named false hypotheses: incorrect Burnside count, cycle rank, electric generators, magnetic maximum, spectral ceiling, discriminant exponent, unconditional promotion of 0.01, and a falsely claimed first-state overlap.

**Acceptance:** unconditional finite first-gap **existence** without store; *not* unconditional certification of the accepted conditional numerical value, first-state visibility, or continuum physics.