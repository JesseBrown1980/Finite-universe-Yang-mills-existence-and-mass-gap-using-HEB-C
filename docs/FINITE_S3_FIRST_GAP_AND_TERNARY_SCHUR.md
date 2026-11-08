# Fixed-finite S₃ Yang–Mills: first gap and ternary Schur route

**Date:** 2026-11-06. **Scope:** finite, connected periodic Lx×Ly square-cell tori and the specified *finite-group S₃* Kogut–Susskind Hamiltonian. This is **not** a 4D SU(N) continuum existence or mass-gap proof. This manuscript gives an analytic, extraordinarily weak, explicit bound for the *first* spectral gap at every fixed finite size and nonnegative magnetic coupling. It then specifies a separate, conditional route toward **sharp** first-level certificates using the existing 3×4 Perron evidence. The numerical 3×4 first-level route is **OPEN**; the repository's formal 3×4 gap-rule HOLD is unchanged.

## Definitions and exact theorem

Let p=Lx Ly, n_links=2p, k=p+1. Gauge fixing along a spanning tree identifies the physical orbit basis with simultaneous-conjugacy classes of k free S₃ link variables. Use the weight w(x)=the size of each conjugacy orbit (1,2,3,6), for which the electric operator E is W-self-adjoint. In the orbit basis, E has nonpositive off-diagonals, row sums zero, and for each row the total rate of off-diagonal electric transitions is at most q=3 n_links=6p. M is diagonal and has 0<=M_x<=3p. Consider H=J_E E+J_B M with J_E>0 and J_B>=0.

**Theorem.** Let g=min(4,Lx,Ly) (the girth of this periodic square-cell multigraph), D=2(p+1), and

    B = 6p + ceil(3p J_B/J_E).

Then the lowest eigenvalue is simple, and for eigenvalues counted in the *complete* physical gauge-invariant space,

    E_2(H)-E_1(H) >= 3*g*J_E / B^(2D) > 0.

The relation is exact as a real-number inequality, not a decimal estimate. Lx and Ly are finite positive integers and the underlying periodic lattice is connected. In particular at Lx=3,Ly=4,J_E=1,J_B=9,

    p=12, k=13, g=3, q=72, max M=36, B=396, D=26,
    E_2(H)-E_1(H) >= 9/396^52 > 0.

For this 3×4 torus the **full physical orbit-space dimension** is (6^13+3·2^13+2·3^13)/6 = 2,177,317,873. The stored 45,508,080-row 3×4 matrix is a symmetry-sector matrix, **not** the full physical Hilbert space. The bound above addresses the full physical space without enumerating it.

### Proof

1. **The exact electric gap.** The one-link electric class sum has eigenvalues 0,3,6 on the trivial, two-dimensional standard, and sign irreducible S₃ representations, respectively. The link terms commute. Gauge invariance requires each nontrivial spin-network support to have no degree-one vertex (one standard leg with any sign legs has no invariant, and one sign leg alone has no invariant). Consequently any nonzero support contains a cycle, hence at least g occupied links, each of cost >=3. Conversely a trace in the standard representation around a shortest cycle is a gauge-invariant electric eigenfunction of energy 3g. Thus gap(E)=3g, with the constant as unique zero mode.
2. **Irreducibility and ground state.** A transposition left-multiplication on any link is an electric move of strictly positive rate. Transpositions generate S₃, so the configuration graph, and its quotient by gauge transformations, is connected. For sufficiently large c, cI-H is entrywise nonnegative and irreducible. Perron–Frobenius implies that H has a unique strictly positive ground-state eigenvector psi in the orbit basis. H is self-adjoint in the weighted W inner product, and H>=0.
3. **Bound the orbit-graph diameter.** Choose the same spanning tree and a tree-gauge representative for any two gauge orbits. The k non-tree link values can be changed independently into the other representative's values, with at most two transpositions per link: every S₃ element has transposition word length <=2. Every move is a permitted edge of the orbit transition graph. Therefore the graph diameter is <=2k=D.
4. **Harnack bound.** Write a_ij=-E_ij>=1 for each off-diagonal orbit edge; the electric diagonal d_i satisfies 0<=d_i<=6p. In the eigen-equation, at each i,

       sum_(j != i) a_ij psi_j = (d_i + (J_B/J_E) M_i - E_1/J_E) psi_i
                                  <= (6p+3p J_B/J_E) psi_i <= B psi_i.

   The last inequality uses E_1>=0. Each positive neighbour term therefore gives psi_j<=B psi_i. Applying the same argument to the reverse edge, then walking a path of <=D steps between the smallest and largest entries, yields max(psi)/min(psi)<=B^D.
5. **Ground-state transform.** With inner product weights w_i, set f_i=u_i/psi_i. The exact identity for this reversible electric graph is

       <u,(H-E_1)u>_W = (J_E/2) sum_(i,j) w_i a_ij psi_i psi_j (f_i-f_j)^2.

   By the variational characterization and the weighted Poincare gap of E, the first gap of H is at least J_E gap(E) [min(psi)/max(psi)]^2. Substitute steps 1 and 4 to obtain the theorem. QED.

**Interpretation:** This is a *first-gap* theorem for fixed finite S₃ systems and gives no useful physical mass scale at large sizes. The right side can be vastly smaller than the actual gap and goes to zero as size or coupling grows. It does not prove uniformity in volume, a nonzero continuum limit, or a 4D SU(N) mass gap.

## The connection to the 3×4 Perron certificate

Write P for the eight flat-vacuum orbit states, Q=I-P. Define

    A(z)=Q(H-zI)Q,
    S(z)=P(H-zI)P-PHQ A(z)^(-1) QHP.

Here positivity and inertia are understood in the W-weighted self-adjoint space; a full-space implementation must symmetrize via W-weighted congruence (or an equivalent exact symmetric generalized pencil), not silently treat the orbit matrix as Euclidean-symmetric. Whenever A(z)>0, the Haynsworth inertia formula gives N_H(z)=n_-(S(z)). For this S₃ model the full eight-dimensional P block is H_PP=72 J_E I_8 on 3×4. The 3×4 certificate currently reports a positive vector d on Q with H_QQ d >=94.070673 J_E d at r=9; the vector was built/checker-replayed in the reported Sx+Sy+ sector and requires the established symmetry-equivariant lift to the full Q space. That inequality **does not** itself determine E_1 or E_2, but for each z<94.070673 J_E it makes A(z) an invertible nonsingular M-matrix, conditional on the existing receipt and its full-space lift.

If A(z)d>=delta d with delta>0 and a>=max_i A(z)ii, let C=I-A(z)/a. Then C is nonnegative and ||C||_d <= alpha=1-delta/a <1. The exact Neumann expansion and absolute weighted-norm tail bound are

    A(z)^(-1) = a^(-1) sum_(n>=0) C^n,
    ||A(z)^(-1) - a^(-1) sum_(n=0..T-1) C^n||_d <= alpha^T/delta.

For T=3^k, the ternary grouping identity

    sum_(n=0..3^k-1) C^n = product_(j=0..k-1) (I+C^(3^j)+C^(2*3^j))

is **exact** for any fixed matrix C. It is a polynomial identity, not by itself an algorithmic promise of O(k) sparse matvecs: evaluating those high powers may create dense intermediate operators. NTT speedups require an independently demonstrated applicable translation-invariant structure.

A precise fail-closed numerical route is to enclose the eight-by-eight S(z) via interval arithmetic and the bounded tail, then prove its inertia is stable under that enclosure. A specific sufficient test is ||S_T^(-1)||_infinity * ||S-S_T||_infinity < 1; along the interpolation S_T+t(S-S_T) no eigenvalue crosses zero. Two rational thresholds a<b with N_H(a)=N_H(b)=1 certify E_2-E_1>=b-a. To isolate each endpoint further, find two adjacent thresholds with counts 0/1 around E_1 and 1/2 around E_2.

`schur_ternary_demo.py` tests the entire *finite-matrix mathematical calculation* using integer determinants, an exactly represented 3^k-term truncated resolvent, the positive witness, a rigorous remainder stability test, and comparison with independently calculated full-matrix inertia. The example is **12 states** (eight P, four Q), not the 3×4 S₃ operator. Its intentionally limited dense products should not be used to claim a 2.18-billion-state computation. A future 3×4 implementation must also retain the orbit weights exactly.

## Reproduction and boundary

    python3 finite_s3_first_gap.py --lx 3 --ly 4 --je 1 --jb 9
    python3 schur_ternary_demo.py

The first script calculates the integer constants in a written proof; it is **not** a brute-force eigenvalue checker. The second script demonstrates the exact algebra on a small Hamiltonian and checks three invalid-input controls. To graduate to a genuine numerical 3×4 first-gap certificate: replay the admitted full-space Perron witness; implement the non-flat resolvent's *action* on the eight boundary columns with rigorous truncation/error enclosures; obtain eight-by-eight Schur enclosures at registered rational thresholds; independently verify inertia and certificate hashes on the full 3×4 data. Until those checks, the **quantitative 3×4 first-gap certification remains OPEN**. Neither this work nor the finite-volume bound changes the project's formal 3×4 cluster-gap HOLD.