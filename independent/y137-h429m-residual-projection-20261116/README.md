# Y137 — exact full-H residual projection against the 429,981,696-dimensional space

Research DRAFT, November 16, 2026. This experiment tests whether the 429-million-dimensional nested basis of PR #246 captures the *full physical Hamiltonian residual* of the two pre-existing 20,736-dimensional rational trial vectors (PR #242).

Only the original 28,634 supported physical orbit keys are required to generate the exact one-hop action of H; this is at most **2,061,648 candidate electric moves per trial**, versus over 30.95 billion moves for an exhaustive new-coordinate-row sweep.

## Orthogonal three-way decomposition

For R=(D H-z)u, with D=10^9, define P_old as the true W-orthogonal projector onto the original 20,736-dimensional Galerkin space, and P_new as the W-orthogonal projector onto the 429,960,960 new canonical orbit-indicator directions. They are orthogonal because every orbit supporting the original 20,736 directions is explicitly excluded from the new coordinate set.

Thus the original exact full-H source action must satisfy

||R||_W^2 = ||P_old R||_W^2 + ||P_new R||_W^2 + ||(I-P_old-P_new)R||_W^2.

Crucially, the original 20,736 Galerkin directions are NOT all physical coordinate axes. The original trial amplitudes occupy 28,634 canonical support orbits and contain four nonorthogonal Krylov directions. Therefore the old residual *coordinate support* is not the true projection P_old. We compute b = B_old^* W R from the authenticated sparse K/G and evaluate b^T G_old^-1 b, reducing its 20,736-dimensional Gram inverse to an exact **4×4 positive integer Schur matrix** after eliminating eight flats, 132 K2 orbit indicators and 20,592 shell-3 coordinate indicators. A 5×5 bordered integer determinant gives the exact remaining quadratic form.

All external shell-3 and shell-4 residual fluxes are independently rebuilt from the pinned original Hamiltonian and classified using the exact original S3 canonical-orbit rank/unrank. Original physical orbit weights are used to compute ||P_new R||_W^2 and ||outside R||_W^2 without floating-point arithmetic. The whole-space norm must exactly match the independently accepted full source residual. We also record the top 12 residual destination orbit ranks overall and outside the lex-selected 429m basis to guide a more useful future selection.

## Acceptance and scientific scope

Original frozen S3 generator, 20,736 source builder and 429m indexer must match their original Git hashes. Both original rational trial vectors and exact full-support residuals must be reconstructed. The old 4×4 Gram Schur must have four strictly positive leading minors; each physical old-source residual contraction must agree exactly with the projected K/G matrix. Three-way Pythagoras identity must hold without rounding.

A new-basis residual capture fraction quantifies the suitability of the lex-selected 429m basis, but **does not certify a new 429m Ritz eigenvalue, improved eigenvector angle, first-excitation Wilson spectral weight, or continuum Yang–Mills theorem**. The formal norm after removing P_new R is a projected residual benchmark, not automatically a residual of an accepted improved eigenvector.

First-excitation Wilson weight HOLD; issue #137 OPEN; research PR stays DRAFT.

Reproduce after rebuilding original 20,736 sparse source:
- python3 -I -B independent/y137-h20736-shell3-20261116/sparse_h20736.py real
- python3 -I -B independent/y137-h429m-residual-projection-20261116/residual_projection.py toy
- python3 -I -B independent/y137-h429m-residual-projection-20261116/residual_projection.py real
