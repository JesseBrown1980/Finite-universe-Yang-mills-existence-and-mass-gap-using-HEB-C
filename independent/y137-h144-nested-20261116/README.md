# Y137 exact nested 12→24→48→96→144 Ritz matrices

Research draft, November 16, 2026. Uses the original finite 3×4 periodic S₃ Hamiltonian at r=9 with strictly integer arithmetic. The accepted 12-dimensional PR #238 source and receipt are pinned by original Git blob and SHA-256; they are copied unchanged into the top-left principal blocks of all larger matrices. The accepted Stage C/D/E/F/G result files are unchanged.

## Fixed nested construction

Start from all eight gauge-flat orbit indicators and the four original first- and second-step Wilson Krylov vectors Bv₁, Bv₂, ABv₁, ABv₂, with B=QHP and A=QHQ. Append 0, 12, 36, 84, or 132 exact nonflat Q-orbit indicator columns chosen by the same deterministic source score and sorted list.

For each source Q index i, the integer score is

s(i) = wᵢ[144((Bv₁)ᵢ²+(Bv₂)ᵢ²) + floor(((ABv₁)ᵢ²+(ABv₂)ᵢ²)/72²)].

Choose highest-scoring indices first, tie-breaking by original canonical ordering. Greedily skip all neighbors of selected indices. The resulting 132 orbit directions are **pairwise nonadjacent in the authenticated K2 electric graph**, so their physical metric and Hamiltonian blocks are diagonal. Other rankings could yield better Ritz values; this one is frozen and reproducible.

## Exact rank and Ritz bounds

For n in {12,24,48,96,144}, compute the complete physically weighted generalized pair

Gₙ[a,b]=⟨bₐ,b_b⟩_W,   Kₙ[a,b]=⟨bₐ,Hb_b⟩_W.

The full n×n integer matrices are saved as CSV GitHub Actions artifacts. They are symmetric and have the original frozen 12×12 principal submatrix. The rank n is certified by checking all four strict positive leading minors of the residual four-Krylov Gram after projecting away the added orthogonal coordinate directions:

G_Krylov,remaining = G_Krylov - Σ_selected wᵢ cᵢcᵢᵀ.

For every exact energy numerator z < 72×10⁹, the 132-dimensional diagonal coordinate block in 10⁹K-zG is strictly positive. Thus the inertia of the n-dimensional pair is exactly the inertia of a 12×12 Schur matrix. All denominators are positive; multiplying by their product preserves inertia. Identical diagonal groups are aggregated exactly to keep integer sizes small. Fraction-free symmetric Bareiss/Sylvester signs then certify the first and second Ritz brackets at precision 10⁻⁹.

Min–max nesting implies both Ritz upper bounds can improve or remain equal as n increases; it does not imply a positive first Wilson spectral weight.

## Source controls

The experiment must reproduce: original W=(1,3,2,3,3,2,2,2), original 8,034 K2 nonflat states, original 72 electric moves per row, 20,736 unordered internal weighted pairs, 500,664 original exterior source records, zero source self-loops, original 12×12 Gram and Hamiltonian SHA-256, strictly positive exact Gram ranks, symmetric full projected matrices, independent row/pair cross-block checks, exact canonical orbit index receipt and both finite Ritz intervals at each n.

## Full physical residual gate

The 8,034 K2 states support all projected matrices, but H acting on the source vectors can reach the 147,344 exterior K3 orbits. A certified full-state norm and improved Wilson transfer must account for those amplitudes and physical orbit weights. The source-only Ritz result is a **variational upper bound**, conditional on the original physical source. Full-state residual, strict eigendirection error and positive first-excitation Wilson spectral weight remain HOLD. Issue #137 remains open; the 4D continuum mass-gap problem remains open.

Reproduction:

    python3 -I -B independent/y137-h144-nested-20261116/nested_ritz.py toy
    python3 -I -B independent/y137-h144-nested-20261116/nested_ritz.py real

Hosted workflow: .github/workflows/y137-h144-exact-nested-ritz.yml.
