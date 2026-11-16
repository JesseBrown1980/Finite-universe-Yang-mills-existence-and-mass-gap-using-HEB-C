# Y137 — exact sparse 20,736×20,736 Hamiltonian on original S₃ 3×4 torus

**Research DRAFT; November 16, 2026.** This is a larger **effective weighted Galerkin Hamiltonian**, not a larger physical lattice. It preserves the exact 144-dimensional [PR #241](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/241) basis and adds 20,592 authenticated shell-3 canonical orbit indicator directions. The underlying full physical space contains **2,177,317,873 gauge-orbit states**, distinct from the previously authenticated 20,738,636-state signed-source support.

## Physical matrix and sparse construction

The original 144-dimensional basis comprises eight flat orbit states, four frozen Wilson-derived Krylov vectors and 132 pairwise-nonadjacent K2 orbit indicators. We append 20,592 distinct shell-3 orbit indicators from the authenticated **147,344-state K2 exterior**.

The exact weighted generalized problem is

\[
K_{ab}=\langle b_a,Hb_b\rangle_W,\qquad
G_{ab}=\langle b_a,b_b\rangle_W.
\]

Relative to the old 144-dimensional span, all new indicators are orthogonal in the physical W metric; therefore the **full Gram is strictly positive definite by the authenticated rank-144 proof and positive orbit weights**. We retain the exact original 144×144 matrices as upper-left principal blocks.

The shell-3 orbit selector uses the original K2→shell-3 weighted source flux and old Krylov columns, sorted by an exact integer score, with ascending original source index to break ties. Selection is deterministic, not claimed optimal. For each selected orbit, the original S₃ canonical link generator explicitly enumerates all **72 electric moves**. It independently checks against the original K2→shell-3 weighted reverse records, the canonical orbit weight, the magnetic potential, genuine self-loop count and full detailed balance of every new selected-to-selected edge. Edges to unselected shell-3, K2 and shell-4 orbits remain part of the true operator: only the **projected matrix** is computed at this gate.

Store the full exact 20,736-dimensional symmetric matrices using **upper-triangular sparse coordinate triplets** in an Actions artifact, not dense arrays. A dense 20,736×20,736 matrix would contain 429,981,696 entries, most unnecessary for this physically local operator.

## Sequential acceptance gates

1. **Exact source and sparse matrix:** reproduce the pinned 144 source and Ritz intervals, all 8,034 K2 source rows, 147,344 exterior canonical states, exactly 20,592 new shell-3 basis indicators, their 72-move graph rows, weighted reverse links and physical potential diagonal. File the sparse Hamiltonian, Gram, complete source fingerprints and SHA-256 receipts.
2. **Ritz inertia and residual:** the inherited \(\lambda_{1,2}^{(20736)}\le\lambda_{1,2}^{(144)}\) follows by min–max, but an improved numerical Ritz bound requires a separately authenticated exact sparse solver or an exact subspace witness. Full-space residuals must include all transitions to **unselected shell-3 and shell-4** states.
3. **Positive first Wilson excitation:** compare the new exact eigendirection residual certificates to the original fixed-sample Wilson amplitude certificate and the strict transfer gate. No positivity claim from a larger matrix alone. Current state \`Wilson_weight=HOLD\`, issue #137 OPEN, continuous SU₂ continuum gap OPEN.

## Future 429,981,696-dimensional proposal

\(429,981,696=20,736^2\) is the **number of entries** in the present dense effective Hamiltonian. Making it the *dimension* of a subsequent matrix is an independent scale-up by a factor of 20,736 basis directions. Such a problem would have \(429,981,696^2\approx1.85\times10^{17}\) dense entries and require compressed/streaming matrix-free operators, at least tens of billions of local graph moves, construction of new physical-shell states, and rigorously audited sparse spectral/normalization certification. This is an optional later research target, not an automatic linear progression or accepted next numerical certificate.

## Reproduce

\`\`\`sh
python3 -I -B independent/y137-h20736-shell3-20261116/sparse_h20736.py real
\`\`\`

Source scope: full exact sparse **projected matrix**. Projected Ritz energies, full-space residual, Wilson weight and continuum mass gap remain HOLD until separately certified.
