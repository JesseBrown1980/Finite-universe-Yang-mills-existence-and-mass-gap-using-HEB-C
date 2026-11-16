# #137 — exact 12×12 flat-plus-Krylov effective Hamiltonian

**Research draft, November 16, 2026.** A separate experiment on the original finite periodic 3×4 \(S_3\), \(r=9\), designed to give two low Ritz eigenvalues and a basis for sharper full-space residual and Wilson-sample tests. All original Stage B–G source data and certificates remain unchanged.

## Frozen basis and provenance

Let \(P\) be the original **eight gauge-flat canonical orbits** in the physical \(W\)-metric; \(Q=I-P\). Let the two original fixed-sample flat column vectors \(v_1,v_2\) be read **byte-for-byte from the SHA-pinned merged PR #180 receipt** (not from a newly optimized or moved trial). Set \(B=QHP\), \(A=QHQ\) and four nonflat vectors

\[
f_1=Bv_1,\qquad f_2=Bv_2,\qquad
g_1=Af_1,\qquad g_2=Af_2.
\]

The proposed basis consists of \(\{p_1,\ldots,p_8,f_1,f_2,g_1,g_2\}\). A full weighted 12×12 **generalized** matrix pencil, not an ordinary Euclidean 12×12 matrix, is essential:

\[
G_{ij}=\langle b_i,b_j\rangle_W,\qquad
K_{ij}=\langle b_i,Hb_j\rangle_W,
\qquad \det(K-\lambda G)=0.
\]

In this model \(H_{PP}=72I\) in the flat basis; its weighted matrix is \(72W_P\). The source \(Bv_j\) is supported on the 264 first nonflat one-link orbits and \(ABv_j\) on shell 1–2, so all **projected** entries can be exactly built from the original pinned 8,034-row nonflat K2 graph without recomputing the 20.7M-state Stage C source. Full-Q exterior effects are retained in the physical diagonal (72 moves); future **full-space residual** norms must explicitly include the shell-3 exterior of \(Ag_j\).

## Exact acceptance gates

1. Reconstruct the original eight-flat order and weights \(W_P=(1,3,2,3,3,2,2,2)\), and the original 8,034 K2 nonflat row graph, using the source-pinned existing K3 graph architecture. Check original \(\sum_i W_{Q,i}C_{ip}C_{iq}=72W_{P,p}\delta_{pq}\) exactly and verify that both original flat samples match their Git blob.
2. Enforce full 72-move per-row counts, including flat destinations, supported K2 edges, shell-3 exterior and genuine self loops. Independently verify weighted reciprocity \(W_i c_{ij}=W_j c_{ji}\).
3. Calculate all 144 integer entries of \(G\) and \(K\). Recompute the complete Q4×Q4 projected Hamiltonian in two independent forms: ordered CSR rows and weighted unordered pairs; require **16/16 exact matches**. Verify full symmetry and strict positive definiteness of the 4×4 Krylov Gram (eight flat rows have positive diagonal metric and are orthogonal to Q).
4. Calculate negative inertia of the 12×12 generalized pencil at both original frozen energies, and if available bracket its first two Ritz eigenvalues exactly to \(\le 10^{-9}\) in the original energy units. Use a 4×4 exact Schur complement with the positive \(P\) block for energies strictly below 72. Report **upper Ritz bounds**, not exact full-state eigenvalues.
5. Exact integer arithmetic throughout. Planted source corruption, wrong orbit weights, broken W-reciprocity, missed or doubled pair edges, and singular Gram must REFUSE rather than supply a false spectral PASS.

## What would establish a genuine improvement in #137?

A sharper Ritz **upper bound** alone is not sufficient to improve the accepted first-excitation full-state spectral or Wilson-weight certificate. The next independent acceptance stage must:
- Compute \(R=(H-\lambda)\mathcal B x\) for its **full** 20.7M-state operator, explicitly including all occupied shell-3/exterior components. Certify \(\|R\|_W\) and true spectral isolation using a global complement lower bound, with a valid **angle** or full-state-distance upper estimate.
- Compare both relevant eigendirections to the accepted full-Q resolvent-dressed original PR #180 Wilson samples, including metric normalization, flat direction and energy dependence.
- Only after improved individual distances and a valid fixed-sample transition/observable bound are established may the finite first-excitation Wilson positivity gate be evaluated. The existing strict \(\sum_i d_i<1/700\) sufficient test, or a independently proved observable-specific alternative, remains **HOLD**.

**Research scope:** the 12-dimensional pencil is one carefully chosen candidate, not a claim of optimal rank, continuum mass gap, or evidence that the actual Wilson transition is nonzero. Preserve issue #137 OPEN and PRs DRAFT until the complete source and spectral gates pass.

## Reproduction

\`\`\`sh
python3 -I -B independent/y137-12x12-krylov-20261116/exact_krylov_12.py toy
python3 -I -B independent/y137-12x12-krylov-20261116/exact_krylov_12.py real
\`\`\`

The workflow [y137-h12-exact-krylov.yml](../../.github/workflows/y137-h12-exact-krylov.yml) records full matrices, SHA-256, exact leading Gram minors, graph edge census and Ritz brackets from the original pinned source.
