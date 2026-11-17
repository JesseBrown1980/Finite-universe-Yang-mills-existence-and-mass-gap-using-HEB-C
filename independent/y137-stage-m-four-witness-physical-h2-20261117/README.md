# Issue #137 Stage M — original physical H² and exact rational 4D Ritz witnesses

**Research draft, November 17, 2026.** This stage combines the accepted full original-S₃ source and original K5-inclusive Stage L moments to certify the physical residuals of two four-vector near-Ritz witnesses. This is an independent full-H **residual gate**, not the finite physical first-gap theorem (already source-conditionally certified) and not the first-excitation Wilson weight.

## Exact source identities

Let u1,u2 be the frozen original rational 20,736-dimensional trial vectors, and let v1,v2 be the two actual full-physical residual directions, with D=10^9 and d the positive original 4×4 Gram Schur determinant.

    v_i = d (I-P_old)(D H-z_seed_i)u_i
        = d D (I-P_old) H u_i.

Thus H u_i has the exact orthogonal decomposition

    H u_i = P_old H u_i + v_i/(d D).

If x_i are old Galerkin coordinates, k_i=K_old*x_i, C_j=<old_basis,H v_j>_W, E_ij the original residual Gram numerators, and Htt_ij=<v_i,Hv_j>_W, the entire four-vector original-physical H² matrix follows:

    <H u_i,H u_j>_W = k_i^T G_old^-1 k_j + E_ij/(d D²)
    <H u_i,H v_j>_W = k_i^T G_old^-1 C_j + Htt_ij/(d D)
    <H v_i,H v_j>_W = Stage-L K5-inclusive three-entry physical H² matrix.

Every field is an exact integer or rational from frozen previously accepted sources. There is **no need for another K5 source sweep** to obtain these four-vector physical moments. The implementation loads and SHA-checks all originals, independently rebuilds old x_i/G/K and the four exact source-residual cross identities, verifies the original four-vector generalized Ritz pencil, and checks exact positive semidefiniteness of H², 468²G-H² and the projection-exterior residual matrix H²-H G^-1 H.

For each original four-vector Ritz lower endpoint z/D the source forms a primitive integer cofactor direction of D H4-z G4, computes its exact physical Rayleigh energy and the exact nonnegative full-H normalized residual variance:

    R² = (<psi,H²psi>_W/<psi,psi>_W)
         - (<psi,Hpsi>_W/<psi,psi>_W)².

The residue is then enclosed by an outward integer square root. The witness is a genuine four-dimensional rational trial state; it is *not yet* the complete 20,738D low Ritz eigendirection. Any first/second full physical eigendirection assertion needs separate isolation (E3..E8 cluster accounted for), and Wilson spectral-weight proof needs observable-specific signed amplitudes.

**Benchmarks are separate:** Best previously certified combined Wilson-transfer error 0.011911898006; proposed next diagnostic target 0.003; strict sufficient positivity threshold <1/700 (~0.001428571). Nothing in this stage can automatically be called a 0.003 Wilson transfer result just because the full-H residual shrinks. Current physical finite first gap, conditional on the original whole-nonflat floor, is 0.039677591 < (E2−E1)/J_E < 0.040004463. Issue #137 Wilson spectral weight HOLD.

Run:

    python3 -I -B independent/y137-stage-m-four-witness-physical-h2-20261117/exact_four_full_h2.py toy
    python3 -I -B independent/y137-stage-m-four-witness-physical-h2-20261117/exact_four_full_h2.py real OLD CROSS GRAM HTT H2

The hosted workflow downloads the immutable original producer artifacts, recreates original old trial vectors, computes full physical H², and reports the two rational witness residual ceilings. Failure of any source hash, Gram consistency or exact PSD check leaves the result HOLD.
