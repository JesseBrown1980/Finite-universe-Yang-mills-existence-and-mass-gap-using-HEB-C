# Y137 Stage L — original-source full-physical residual norm acceptance

**Research draft (November 17, 2026), stacked on Stage K draft PR #257.** This branch freezes the next precise full-physical acceptance protocol and exercises its weighted source and residual mathematics on a small exact independent toy. The production 3×4 source and true Ritz vectors have not yet been computed in this branch. No first-excitation Wilson spectral weight or continuum claim.

## Why this gate is smaller than the complete physical space

The old 20,736 basis has exactly 8 flat + 8,034 K2 + 20,592 selected K3 physical source orbits. The two new residual vectors have 7,902 *unselected* K2 + 126,752 *unselected* K3 + 499,265 touched K4 orbits. Their union therefore has at most:

    8 + 8,034 + (20,592 + 126,752) + 499,265 = 654,651

physical orbit coordinates. For **any** exact integer coefficient vector in the completed 20,738D trial space, the original finite S3 Hamiltonian acts through at most:

    654,651 × 72 = 47,134,872

raw original electric moves, and magnetic diagonal terms on the occupied input orbits. The output of this one-step action may extend into exterior K5 gauge-orbit targets. All touched targets must be accumulated in the original weighted physical Hilbert space. The estimate is per witness, not a claim that K5 has already been enumerated.

## Production protocol for the full-H eigenvector error

1. Obtain **two certified actual low-energy trial/Ritz witnesses** (signed integer coefficient vectors, rational energy centres, exact Gram normalization) in the complete 20,738D generalized pencil; use Stage K 10×10 Schur inverse with a separate rational witness/error gate rather than substituting an old two-vector sample. Rebuild the original old Gram and H, complete accepted cross block C, new 2×2 Gram and actual physical Htt from frozen SHA-pinned outputs.
2. Construct each witness's physical original gauge-orbit amplitude \`psi(x)\` by contracting all four old non-coordinate K2 Krylov columns, all old coordinate indicators and both exact physical residual directions \`v_j=d(I-P_old)(DH-z_j)u_j\`. Check **exact metric norm** \`N=<psi,psi>_W = coeff^T G_ext coeff >0\` and **exact energy** \`K=<psi,H psi>_W=coeff^T H_ext coeff\`.
3. Stream the original 72 S3 electric moves for every nonzero source orbit, using source-pinned canonical neighbor enumeration. For target y, accumulate **weighted flux** \`F_y = sum_x w_x n(x,y) psi(x)\`. Check source-weight reciprocity \`w_x n(x,y)=w_y n(y,x)\` (sampled pilot and exhaustive/independently summarized target gates as appropriate), full 72-move input row census and flux divisibility by original positive \`w_y\`. Set \`(H psi)(y)=(72+9M_y)psi(y)-F_y/w_y\`, including every exterior K5 output. Do not drop a nonzero target to fit a memory cap; use sharded target aggregation/external sort if needed.
4. At an exact rational energy \`z/D\`, define \`r(y)=(D H-z I)psi(y)\`. Certify exact source moment identity:

       R2 = sum_y w_y r(y)^2
          = D^2 * <H psi,H psi>_W - 2 D z * K + z^2 * N.

   The **W-normalized full physical residual squared** in \`J_E^2\` units is \`R2/(D^2*N)\`. Use integer cross-products and outward rational intervals to provide a strict bound; this full-H residual includes every K5 contribution.
5. Independently compute the **projected residual** \`b=(D K_ext-z G_ext)coeff\` and squared norm \`b^T G_ext^{-1}b\` using the existing 4×4 old Schur plus the 2×2 residual Gram inverse. Require \`R2-b^T G_ext^{-1}b >= 0\` exactly (after clearing denominators). This is the Pythagorean projection/exterior leakage certificate. Forge a deleted K5 target, a reversed weighted edge, a changed Wilson diagonal, and an omitted Krylov coefficient: each must fail at its own gate.
6. Only after a certified physical eigenstate separation denominator is available from the earlier whole-H eight-flat Schur certificate may a full-H residual imply an eigendirection angle bound. This angle proof must track the first two physical eigenstates separately from the E3..E8 cluster and use the *physical* spectral windows, not a Galerkin-only gap.
7. Certify the **specific** full weighted gauge-invariant summed-winding O+ action norms and signed sample overlap. Apply a strict outward-rational Wilson transfer inequality (or directly certify an isolated spectral projector) with exact full-state normalization and separately verified momentum sector. **Wilson stays HOLD until the final positive lower bound is established.**

## Toy acceptance on this draft

The checked-in \`exact_residual_toy.py\` uses a five-orbit weighted self-adjoint Hamiltonian, all 72 moves per input row, one exact non-coordinate old column, one newly added basis direction and an exterior one-step target mimicking the K5 gate. It checks two distinct direct/scattered physical H constructions, original Gram/H moments versus projected coefficients, exact full residual variance identity, projected-vs-full W residual inequality, and **two mandatory false controls** (drop exterior flux and forge a weighted reverse edge). It additionally computes an observable-specific exact weighted action norm without asserting an actual spectral weight.

Run locally:

    python3 -I -B independent/y137-stage-l-physical-residual-20261117/exact_residual_toy.py toy

This is a **method/acceptance pilot only**. It does not certify 3×4 physical eigenvector angles, Wilson spectral weight or any continuum claim. Research PR #257 and original source artifacts remain untouched. Issue #137 OPEN/HOLD.
