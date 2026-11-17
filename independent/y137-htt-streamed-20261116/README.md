# Y137 Stage I — exact residual-to-residual Hamiltonian in eight source-backed shards

Research DRAFT (November 16, 2026), stacked on PR #249. This stage computes only the missing physical residual-to-residual 2x2 Hamiltonian block of the already certified 20,738-dimensional nested Galerkin trial space.

## Physical construction

For original frozen seeds z1=69924497999, z2=69963565334, D=10^9, set r_i=(D H-z_i)u_i and t_i=(I-P_old)r_i, where P_old is the true W-orthogonal projector onto the original noncoordinate 20,736-dimensional Galerkin subspace. Let d>0 be the original 4x4 Schur Gram determinant and v_i=d t_i. The physical weighted Gram(v) must exactly reproduce d times the original, SHA-frozen positive definite 2x2 residual Gram numerator.

The eight flat, 132 selected K2 indicators, and 20,592 selected K3 indicators vanish under the projection. On unselected K2, compute the exact noncoordinate Krylov projector by four integer Cramer determinants. On unselected K3 and touched K4, reconstruct the original weighted electric flux into each orbit and divide exactly by its positive orbit weight. This provides a common physical support of at most **7,902 K2 + 126,752 K3 + 499,265 K4 = 633,919 coordinates** for both residual directions.

Stream all 72 original involutive S3 electric moves on every supported physical row: at most **45,642,168 raw electric transitions**. The eight hosted matrix jobs each rebuild and SHA the common support, then compute their assigned every-eighth sorted original orbit row. Each job emits all four directed weighted H_ij entries with magnetic diagonal 72+9M and exact electric off-diagonal counts. A deterministic pilot checks weighted reverse-edge reciprocity against the original generator.

The independent fan-in validates all eight support SHA fingerprints and original-source SHA pins, verifies every raw move and row census, rejects H12 versus H21 asymmetry, and checks exact positive-semidefinite inequalities 0 <= H_tt <= 468 Gram(v). The 468 bound follows from the 72 involutive electric translations (0 to 144) plus 12 original plaquettes (at most 9*3*12=324). Source artifact SHA receipts and per-shard provenance are retained.

## Hard acceptance boundaries

Original original-generator Git blob: 91bd1e80cbfcfb76198966aa177d097ecfbe8143.
Original H20736 source Git blob: d0d9d3d14d804450a31ed8e98c01a031b9a53596.
Original signed exact H20738 receipt Git blob: 90f9c002f6fe8df2ecd4b5e725de3f9153fbab10.

This is an exact H_tt computation, not the entire new H20738 generalized Ritz eigensolve. Even after H_tt is accepted, separately compute new Ritz witnesses, their complete full-physical residuals (possibly through K5), and positive Wilson first-excitation spectral weight before changing issue #137 from OPEN/HOLD. Four-dimensional continuum existence/mass gap remains OPEN. Leave this research PR draft pending independent review.

## Commands

python3 -I -B independent/y137-h20736-shell3-20261116/sparse_h20736.py real

python3 -I -B independent/y137-htt-streamed-20261116/exact_htt_stream.py toy

python3 -I -B independent/y137-htt-streamed-20261116/exact_htt_stream.py pilot

python3 -I -B independent/y137-htt-streamed-20261116/exact_htt_stream.py shard 0

python3 -I -B independent/y137-htt-streamed-20261116/exact_htt_stream.py fanin build/y137-htt-shards

Workflow: .github/workflows/y137-exact-htt-eight-shard.yml
