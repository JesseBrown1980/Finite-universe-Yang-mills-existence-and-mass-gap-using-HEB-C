# Y137 Stage J — full 20,736 × 2 physical old-to-residual Hamiltonian coupling

**Research draft, 2026-11-16.** This branch stacks on independent exact physical Htt / four-vector Ritz PR #252 and retains its original sources unchanged.

## Exact target

The original 20,736-dimensional trial space is spanned by eight flat coordinate vectors, four overlapping K2 Krylov columns, 132 selected K2 coordinate vectors, and 20,592 selected K3 coordinate vectors. Two new physical residual vectors v_j were constructed in PR #251 as d(I-P_old)(D H-z_j)u_j, D=10^9, with positive exact 2×2 weighted Gram. Define C_aj = <basis_a, H v_j>_W.

The COMPLETE basis has only **28,634 distinct supported physical orbits** (8 flat + 8,034 K2 + 20,592 K3). Therefore all 41,472 old-to-new entries are obtained by evaluating H v_j on exactly these rows and contracting with the original old basis. Each row uses all 72 original S3 electric moves:

    w_x(Hv_j)(x) = w_x[(72+9M_x)v_j(x) - Σ_y n(x,y)v_j(y)]

Maximum raw electric moves: 28,634 × 72 = **2,061,648**, partitioned into 8 deterministic disjoint shards. No fake coordinate-only projector may replace the four overlapping Krylov columns, which must sum over all 8,034 K2 rows.

## Hard gates

- Rebuild original source under frozen Git blob pins for the original S3 3×4 Hamiltonian, H20736 builder and PR #249 rank-2 residual Gram receipt. Reconstruct the exact 633,919-orbit new residual support from source.
- Verify 28,634 distinct original rows, unique row-to-coordinate mapping, source SHA fingerprints across every shard, all 72 moves/row and exact SHA-256 file integrity. Independently rebuild the original K2 Krylov amplitudes during fan-in.
- Recover original full 20,736 integer trial coefficients u_i and frozen E_ij from the accepted source. Require ALL FOUR exact identities **D u_i^T C_{\cdot j} = E_ij**. This is the exact bilinear Hamiltonian self-adjointness / orthogonal-residual Gram identity; no tolerance is permitted.
- Retain the full 20,736×2 signed-integer matrix TSV, its SHA-256, head commit, source script SHA and the immutable source support hash in the workflow's production artifact. A forged weighted reverse edge must fail the toy control.

## Research boundary

A passing fan-in finishes the missing off-diagonal block C and, together with the preexisting exact old K/G and PR #251 exact Htt, makes the full 20,738-dimensional generalized Galerkin pencil available. **It does not automatically certify the first two 20,738-dimensional Ritz roots**, the physical full-space eigenvector normalization, or first-excitation Wilson spectral weight. Those require separate exact-inertia / full-H residual / Wilson transition gates. Issue #137 stays OPEN and Wilson stays HOLD until all independent criteria are satisfied. The continuum 4D Yang–Mills question stays open.

## Reproducible commands

    python3 -I -B independent/y137-h20736-shell3-20261116/sparse_h20736.py real
    python3 -I -B independent/y137-full-cross-20261116/exact_old_new_coupling.py toy
    python3 -I -B independent/y137-full-cross-20261116/exact_old_new_coupling.py pilot
    python3 -I -B independent/y137-full-cross-20261116/exact_old_new_coupling.py shard 0
    python3 -I -B independent/y137-full-cross-20261116/exact_old_new_coupling.py fanin build/y137-cross-shards

Workflow: .github/workflows/y137-full-cross-eight-shard.yml
