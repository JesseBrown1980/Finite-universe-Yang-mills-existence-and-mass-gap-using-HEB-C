# #137 — actual directional Q-resolvent improvement of eight-flat projector energy drift

The earlier accepted source-conditional eight-flat Schur projector diagnostic (#181) has E1 sine-angle upper 0.842057984250 and E2 upper 1.465570680225 (vacuous). Its principal uncertainties are the conservative K3 Q-exterior Schur residual and uncertainty in the true E1/E2 energies. The latter was bounded using the **global** \(\|B\|_F^2=576\), which is safe but ignores the strongly localized flat eigendirections.

This new lane computes and checks a **strictly sharper direction-specific coupling bound from the actual finite S3 Hamiltonian**. The prediction, historical sample energies/flat trial vectors, exact source U/G hashes, source floor and prior projector bounds were frozen in PREDICTION.hbp **before writing the replay**. This is independently useful even while the separate K3 microbracket lane #182 is running.

## The new exact estimate

Use the source's W-orthonormal P/Q block Hamiltonian H=(A Bᵀ;B D), and D=QHQ≥gamma I with gamma=94.0682 J_E. The energy-dependent 8×8 Schur pencil is

    S(z) = A-zI-Bᵀ(D-zI)^(-1)B.

For a normalized eight-flat vector x and two energies E,z below gamma, the exact resolvent identity gives

    ||[S(E)-S(z)]x||
      <= |E-z| [ 1+ ||B|| ||(D-zI)^(-1)Bx||/(gamma-E) ].

This improves the old universal bound using \(\|B\|_F^2/[(\gamma-E)(\gamma-z)]\). The exact K3 graph verifies \(\|B\|_F^2=576\), so \(\|B\|\le24\).

The key **new directional quantity** \(\|R_z Bx\|\) is bounded twice, independently:

1. Direct coupling: \(\|R_z Bx\|\le\|Bx\|/(\gamma-z)\), with \(\|Bx\|^2=\sum_i w_{Q,i}(\sum_k C_{ik}v_k)^2/(v^\top W_P v)\). All these C rows and W weights are from the pinned actual graph.
2. Source Q trial: the 20-step integer Jacobi \(Yv\) with flat part SCALE·v supplies a finite-support \(\widehat y\), satisfying \( (D-z)\widehat y + Bx=r\). Therefore \(\|R_zBx\|\le\|\widehat y\|+\|r\|/(\gamma-z)\). Both the complete W-norm of Yv and the full-Q residual \(\|r\|^2=v^\top Gv/[6b^2\mathrm{SCALE}^2 v^\top W_Pv]\) are exactly rebuilt, including **every shell-4 residual** through the accepted K3 G.

Take the smaller of the two outward-rounded bounds, then the smaller of the new drift and the accepted global drift. Both are sound for the entire certified E interval. The source U-residual and direction-specific PSD Schur error are computed unchanged from #181; the code **must reproduce both prior sine-angle upper endpoints exactly** before printing new ones.

## Acceptance and scope

The current energy brackets are those already merged on main: E1∈(69.908,69.92), E2∈(69.948,69.9567503), in J_E. The 8-flat E1 null separation exceeds 0.028 and the E2 separation exceeds 0.011949. The code prints raw and improved energy drift, exact B norms, full Q residual, the total Schur null residual and each new sine-angle bound with outward integer rounding.

Any positive improvement is a *verified reduction in conservative projector uncertainty*, not yet a positive Wilson E1→E2 first spectral-weight theorem. The source Q-tail contribution to the Schur matrix remains bounded by the old PSD envelope; the actual normalized E1/E2 vectors are not certified close enough to the fixed trial pair. The conservative sufficient target from issue #137 is a combined W-normalized state error <1/700.

After microbracket PR #182 completes, rerun this exact method with its certified narrower windows **only after separately freezing the new endpoint inputs**. No Ritz estimate or previously unproved E level is promoted to a theorem.

    python3 -I -B independent/y137-directional-Q-projector-20261113/replay.py

CI must check the frozen prediction blob, two U/G source hashes, strict #181 comparison, complete hosted output and no-float/native integer gates, and file the exact receipt only after the measurement.
