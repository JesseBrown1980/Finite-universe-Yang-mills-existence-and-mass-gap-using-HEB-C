# Issue #137 — source-conditioned eight-flat eigenprojector error diagnostic

This lane performs the remaining **directional Schur error calculation** on the actual 3×4 S3 finite-lattice K3 source at r=9, using the newly certified E1/E2 intervals from merged PR #179. It is an independent necessary gate before transferring the positive **fixed-sample** Wilson/Q-resolvent matrix element of draft #180 to the exact E1→E2 spectral weight. The already observed sample flat vectors and sample energies were frozen in [PREDICTION.hbp](PREDICTION.hbp) before the new code.

**Source and exact scope.** Q-floor gamma=94.0682 J_E; K3 has 155,378 nonflat trial orbits and 1,985,218 complete exterior residual targets. The E1 interval is (69.908,69.92) and E2 is (69.948,69.9567503) J_E, both conditional on the accepted source. E3≥69.9686993. The source-pinned 8×8 U/G/G-gram matrices are recomputed at sample energies 69.909875505 and 69.949729820 with **20 integer Jacobi steps** and must exactly match both SHA-256 hashes already produced by #180's first hosted run.

### Schur projection inequalities

Work in the W-orthonormal eight-flat coordinates. For trial raw-flat vector v and Wp=diag(w_flat), let q=vᵀWp v. Then xhat=Wp^(1/2)v/sqrt(q) is unit. At rational z=a/b below the Q floor, the true self-adjoint Schur pencil is S(z)=A-zI-Bᵀ(D-zI)⁻¹B in these coordinates. The integer construction provides quadratic-form inequalities

    U/(bT²) - [PS G/(6 gnum bT²)] <= S_W(z) <= U/(bT²),
    gnum=b*FLOOR-a*PS, T=10¹², PS=10⁶.

For the W-normalized error Δ=Wp⁻¹/² [PS G/(6gnum bT²)] Wp⁻¹/², Δ is PSD. Hence, with \(\delta_v=xhat^T\Delta xhat\), and \(\mathrm{tr}\Delta\), the norm of its action on this particular direction is rigorously bounded by

    ||Δ xhat||² <= (tr Δ) δ_v.

This uses the exact direction-specific **vᵀGv** rather than solely the broad trace bound of PR #179. The bound on \(\|(U/(bT²))xhat\|\) uses \(\sum_i (Uv)_i²/w_i\), with the correct W normalization; all sqrt evaluations round **up** in integers.

For energy uncertainty, the resolvent identity and full-source \(D\ge\gamma I\) give

    ||S(E)-S(z)|| <= |E-z| [1 + ||B||²/((gamma-E)(gamma-z))].

The source Q-to-flat coupling B has an **exact rational Frobenius bound** \(||B||² \le \sum_{i,k} w_{Q,i} C_{ik}²/w_{flat,k}\), reconstructed from all K3 C entries, without forming a huge dense matrix. Maximize \(|E-z|\) over the certified E1/E2 windows. Combine these three errors for a *rigorous rational upper bound* on \(\|S(E_i)xhat_i\|\).

By monotonicity of the Schur pencil \(S'(z)=-I-B^\top(D-z)^{-2}B\preceq-I\), and the accepted **full-H level separation**, the simple Schur null direction has gap greater than 0.028 J_E at E1 and greater than 0.0119490 J_E at E2. Therefore

    sin angle(xhat_i, actual normalized P-null direction)
       <= min(1, ||S(E_i)xhat_i|| / gap_i).

The script reports the untruncated upper bound to reveal a **HOLD** when it is ≥1, rather than claiming a meaningful projector enclosure. Even a nontrivial sin-angle bound alone would not close the Wilson weight issue; one must propagate the projector perturbation through the Q-resolvent, O_eff and full W norms, and prove a positive rational lower bound on the true spectral weight.

## Actual hosted result: projector transfer remains HOLD

The first source-pinned calculation [hosted run 43490246508](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43490246508) **passed** its exact replay and integer-only/no-float audits. Its three exact reported rows were filed *after the run* as [RESULT-K3-PROJECTOR.hbp](RESULT-K3-PROJECTOR.hbp), with a subsequent CI gate requiring byte-identical reproduction. The hash of each recomputed 8×8 U/G matrix matched the frozen prior #180 trial matrix.

At E1's historical sample 69.909875505, the W-normalized `U` residual is bounded above by 0.000000000631, the **directional PSD Schur error** by 0.003456712890, and the maximum certified energy-parameter variation by 0.020120910038. The resulting `||S(E1)xhat1|| <=0.023577623559`, divided by the already certified null-gap >0.028, gives **sin(angle1) <=0.842057984250**. This is nontrivial but too broad to establish the Wilson transition.

At E2's historical sample 69.949729820, the directional Schur error is at most 0.003537919283 and the maximal energy-parameter variation at most 0.013974184152. With the <0.000000000623 U residual this gives `||S(E2)xhat2|| <=0.017512104058`. The available E2 null-gap is >0.011949; consequently the reported spectral estimate is **sin(angle2) <=1.465570680225**, which is *vacuous* (the universal bound sin≤1 is stronger).

**Verdict: projector transfer HOLD.** Reducing only the energy brackets cannot remove the ~0.0035 directional Schur-residual term; improving only the Jacobi digit precision also cannot overcome the exterior source uncertainty. A successful full E1/E2 positive Wilson certificate requires both tighter true energy intervals and a sharper direction-sensitive **full-Q dual/effective Schur residual** enclosure (or an exact source reduction), then propagating the resulting eigendirection error through O_eff. The current Q-dual *fixed-sample* positivity is independently useful, but cannot yet be promoted.

### Reproducibility

All arithmetic is exact integers and integer-square-root outward rounding; the source pins (including U/G hashes of PR #180) and the prediction's git blob are checked by hosted CI. New-head result and all repository no-float/native check groups must pass before a scientific acceptance decision. Negative controls include wrong U/G hash and energy bracket.

    python3 -I -B independent/y137-schur-projector-20261113/replay.py

**Status:** this PR tests whether the current source plus certified spectral windows can yield a sufficiently narrow projector guarantee. Until an actual positive spectral-weight bound is obtained, issue #137 remains OPEN.
