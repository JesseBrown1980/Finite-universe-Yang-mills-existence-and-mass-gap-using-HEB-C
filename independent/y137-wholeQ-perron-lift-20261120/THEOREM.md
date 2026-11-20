# #137 — original finite whole-Q Perron lift: independent weighted sum-of-squares proof

**Scope:** The 3×4 periodic S₃ finite weighted physical orbit Hamiltonian, its entire nonflat compression QHQ and the positive original Sx+Sy+ lattice-symmetry quotient. This proof supplies the precise mathematical implication connecting the *separately source-verified* 45,508,080-row positive Perron comparison certificate to a uniform lower bound on **every** original nonflat physical gauge orbit. The mathematical proof is independent of the prior sector solver.

## Exact operator and spatial symmetry

By [independent physical P/Q source acceptance #341](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/341), the full original Hilbert space has integer orbit weights w(x)>0, and in J_E units

\[
H(r)_{xy}=(72+rM(x))\delta_{xy}-c(x,y), \qquad
c(x,y)\geq0,\quad w(x)c(x,y)=w(y)c(y,x).
\]

The entire physical Q subspace is the W-orthogonal complement of exactly eight magnetic-flat gauge orbits. Denote its principal compression by D=QHQ. The lattice translation/reflection symmetry group G preserves the 72 physical transposition moves, the plaquette costs M, the residual conjugation orbit weights and the set of eight flat states. Its action commutes with D and induces a finite quotient on the nonflat orbit set. The original positive (+,+) sector store represents the full symmetry-invariant Hamiltonian, **including its seven flat rows**. Its **nonflat principal compression** represents D on G-invariant nonflat functions: the nonflat diagonal remains unchanged, while all flat columns are omitted from the action. Each quotient matrix row is constructed by summing physical moves to each quotient orbit. The independent original 45,508,080-row rebuild [merged PR #332](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/332) reconstructs the actual canonical sector keys, weights, magnetic costs and every electric row from those original rules; the full 34-file original source is separately cryptographically authenticated.

### Exact flat-row boundary of the original certificate

The authenticated original `Sx+Sy+` room store has **45,508,080 total quotient rows**, including **seven magnetic-flat quotient rows** (see `PERRON-RESULT.hbp`, `RESULT_P0`, and `PERRON-REVIEW.md`, Section 2). Therefore the actual nonflat sector principal compression has **45,508,073 rows**. Its published `x3-c.bin` has one 64-bit entry per original sector row: the accepted strict checker requires **zero on every flat row** and **strictly positive on every nonflat row**. The full original gauge-invariant space has **2,177,317,873 orbits**, of which **eight** are flat, so the physical Q space has exactly **2,177,317,865 nonflat orbits**.

In particular, if `P_+` projects onto the seven sector flats, then the comparison operator is `D_+=(I-P_+)H_+(I-P_+)` *restricted to its nonflat range*. The published vector is first restricted to its **45,508,073 nonflat entries**. The quotient lift takes place on this restricted space, and is strictly positive there. There is no requirement that the **uncompressed** `H_+ d` inequality hold on flat rows; genuine P/Q electric edges can make those zero-vector rows negative. The diagonal entries of `D_+` must **retain** all original contributions from moves touching flat states, as in a principal compression, not a graph Laplacian with its boundary degree removed.

This distinction is checked by the added exact weighted **one-flat/three-nonflat toy** in `verify_lift.py`. The full W-self-adjoint example has a flat-to-Q boundary with `(H d)_flat=-10` for a vector `d=(0,2,1,1)`, but its Q principal compression still satisfies `D d=(8,5,5)` and `D d - 4d=(0,1,1)\ge 0`. This is the finite analogue of the actual archived zero-flat, positive-nonflat Perron witness.

## Sector comparison vector lifts to all original nonflat gauge orbits

Let q(x) denote the symmetry orbit containing full nonflat physical gauge orbit x, and let D_+ be the exact quotient operator defined by

\[
(D_+v)(q(x))=\sum_{y\text{ nonflat}}D_{xy}\,v(q(y)).
\]

The right-hand side is independent of the choice of x in the same G orbit because G commutes with D. Given a **strictly positive** vector d_+ on every quotient state, define the lift d(x)=d_+(q(x))>0 on every full nonflat physical orbit. Then for every x,

\[
\boxed{(Dd)(x)=(D_+d_+)(q(x)).}
\]

Consequently, any exact certificate D_+d_+≥t d_+ produces **pointwise Dd≥t d across the entire nonflat full Hilbert space**, including nontrivial momentum/reflection sectors. The proof neither supposes that the original Perron eigenvector lies in every sector nor infers a bound from interlacing in the wrong direction. It constructs a globally positive comparison vector directly.

## Independent weighted ground-state transformation proves the lower bound

The full original nonflat compression D has nonpositive offdiagonal entries -c(x,y), exact W-detailed balance and a strictly positive d. For any vector f, write f(x)=d(x)u(x). Direct weighted expansion and pairing of every reversible edge gives the exact identity

\[
\begin{aligned}
\langle f,(D-tI)f\rangle_W
&=\sum_x w(x)\,d(x)\,\big[(D-tI)d\big](x)\,|u(x)|^2\\
&\quad+\frac12\sum_{x\neq y}
w(x)c(x,y)d(x)d(y)|u(x)-u(y)|^2.
\end{aligned}
\]

Every term is nonnegative if Dd≥t d. Therefore D−tI is positive semidefinite in the **whole W Hilbert space**, proving

\[
\boxed{\lambda_{\min}(QHQ)\geq t.}
\]

This weighted sum-of-squares derivation is an independent proof of the Barta/Collatz–Wielandt implication that does not assume irreducibility or diagonalize the 2,177,317,865-dimensional gauge-invariant space. It applies to all full nonflat Q states because the lifted d is strictly positive everywhere and the identity is exact for all f.

## Connection to authenticated original Perron and Wilson data

The previously independently checked original positive top comparison vector x3-c.bin has SHA-256

**f5c5428db1fc5d91d2ab891689f0dac7263dc26c8f9b60a2db82728f6ea0dcd1**.

The original exact whole-sector comparison certificate gives the accepted finite quotient minimum

\[
t=\frac{94\,070\,673}{10^6}\,J_E=94.070673\,J_E
\]

from exact integer row inequalities, with an outside independently authored Go checker, the corrected full certificate controls and the separately accepted source/physical row evidence. The original full 45,508,080-row independent hosted replay and composite original 34-sector integrity acceptance are recorded in merged PR #332. Those original full dataset and positive witness facts are **separate authenticated computational premises** for this mathematical theorem, not data newly generated by the tiny proof toy.

The Wilson eigenbranch/projector transfer conservatively uses

\[
\gamma=\frac{94\,068\,200}{10^6}\,J_E=94.068200\,J_E,
\]

with an exact positive floor margin of **2,473 micro-J_E** below the certified t. The same whole physical Q in this proof is the nonflat Q already fixed and independently signed off in merged #341. Thus the mathematical sector-to-whole-Q lift is fully compatible with the exact physical W-inner product, the source-to-Schur algebra in merged #343, and the abstract matrix Loewner bound in merged #338.

## Source-independent exact controls and final theorem boundary

The [independent integer-only toy](verify_lift.py) tests a nontrivial weighted full three-state nonflat Z-matrix with W=(1,2,2), an S₂ exchange symmetry and a two-orbit quotient, plus a four-state original-P/Q-boundary analogue with a zero-flat, positive-nonflat witness. The quotient d_+=(2,1)>0 lifts to d=(2,1,1)>0, and at threshold t=4 the full physical comparison defect is exactly (0,1,1). Multiple independent u vectors verify the exact weighted ground-state sum-of-squares identity as an integer equality. Nine errors must fail closed: wrong W weight, wrong reverse edge, broken symmetry edge, broken symmetry diagonal, positive offdiagonal, false quotient row, zero/negative comparison vector and excessive threshold. The original conserved difference t−γ is also checked using integer micro-J_E units, with ordinary and optimized Python producing identical receipts.

**Mathematical theorem acceptance:** whole-Q symmetry orbit lift of a strict sector comparison vector and weighted positive-vector spectral-floor implication are proved, conditional on the *separately audited original* positive 45M source certificate and exact sector-to-full operator definition. **Final first-Wilson squared spectral-weight positivity** remains SOURCE-CONDITIONAL / FORMAL HOLD pending one joined proof review confirming that the original Perron witness, exact source/Schur moments, full original E1/E2 branch and Wilson action are all consistently the same physical finite Hamiltonian. Four-dimensional continuum Yang–Mills remains OPEN.
