# #137 — exact W-orthogonal seven-dimensional Schur residual bound

The accepted finite model already has full-H source-conditional E1/E2 energy windows (#182), exact directional full-Q drift (#183), independently identified eight-flat simple Schur eigendirections (#184), and complete full-W normalized sample-vs-true state error intervals (#185). The actual original unshifted seven-loop Wilson first-excitation spectral weight is still OPEN, because the combined **conservatively certified** normalized true-state error upper 0.377737771100 does not pass the simple sufficient <1/700 sign-transfer condition.

The dominant existing angle error comes from the source Q-residual Schur sandwich \(0\preceq X\preceq\Lambda\), where \(X\) is the unknown positive exact resolvent correction and \(\Lambda\) the accepted K3 upper matrix from the complete Q Gram G. Earlier #184 bounded **the entire** action \(\|Xx\|\) by \(\sqrt{\mathrm{tr}(\Lambda)\,\langle x,\Lambda x\rangle}\). However the true eigenvector-angle residual only involves \(P_x^\perp Xx\). This lane computes the exact strongest source upper bound on \(\Lambda\) restricted to the **W-orthogonal complement** of each accepted trial direction; this can be significantly smaller than \(\mathrm{tr}\Lambda\).

The exact input source SHA, U/G hashes, trial vectors, all 8×8 Gram PSD and 7×7 orthogonal-PSD gates were frozen in [PREDICTION.hbp](PREDICTION.hbp) before constructing new code or producing any orthogonal source measurement. A smaller answer is a hypothesis, not pre-accepted.

## Rigorous new inequality: positive Schur correction on the orthogonal complement

In W-orthonormalized eight-flat coordinates let x be the accepted unit flat trial vector. The source K3 variational Schur enclosure gives

    0 <= X <= Lambda,
    Lambda = W_P^(-1/2) [PS*G/(6 gamma_num*b*T²)] W_P^(-1/2),

where \(b=10^9\), \(T=10^{12}\), \(\mathrm{PS}=10^6\), \(\gamma_{\mathrm{num}}=b*94068200-a*\mathrm{PS}>0\), G is the complete exact 8×8 residual Gram, and all inequalities are self-adjoint Loewner inequalities.

For every unit w orthogonal to x, PSD Cauchy–Schwarz gives

    |<w,Xx>|² <= <w,Xw><x,Xx>
               <= <w,Lambda w><x,Lambda x>.

Take the supremum over all such w. Writing \(\lambda_{\perp}\) for the largest eigenvalue of \(\Lambda\) restricted to \(x^\perp\), this proves **without any unknown resolvent eigenvector or sign assumption**:

    ||(I-xx*) Xx|| <= sqrt(lambda_perp * <x,Lambda x>).

This is a valid source-conditioned **centered-error bound**. It can improve the old trace bound because \(\lambda_{\perp}\le \mathrm{tr}\Lambda\). It is inserted only into the accepted #184 **Rayleigh-centered** projector error; the separate \(|\mu|<\delta\) null-branch identification and the accepted E1/E2 energy drift remain mandatory.

## Exact 7×7 rational weighted computation

Let \(v\in\mathbb Z^8\) represent the flat trial direction and Wp=diag(w_flat). Choose a nonzero pivot p and construct seven exact integer basis vectors

    u_j = w_p v_p e_j - w_j v_j e_p,   j!=p.

They satisfy \(u_j^\top W_P v=0\) identically and span the full W-orthogonal complement; no square root or floating-point linear algebra is required. An intentionally altered vector fails this identity as a negative control.

Compute

    W7 = Uᵀ W_P U,
    G7 = Uᵀ G U.

With \(\Lambda_{\mathrm{raw}}=\mathrm{PS} G/T_s\), \(T_s=6\gamma_{\mathrm{num}}\, b\, T^2\), the claim \(\lambda_{\perp}\le K/10^{12}\) is equivalent to exact PSD of

    K*T_s*W7 - PS*10^12*G7.

The hosted checker finds the **smallest integer K** satisfying this PSD condition by testing **all 127 nonempty principal minors** of the 7×7 matrix, checks K−1 fails, verifies the upper bound from the accepted full-space trace, and separately verifies every one of the **255** principal minors of the actual 8×8 G is PSD. This is performed at both source-pinned historical samples with 20 exact K3 Jacobi steps and complete 1,985,218 shell-4 residual targets. The source U/G SHA fingerprints must equal previously accepted #180/#184 receipts.

The newly certified centered Schur correction action upper is

    sqrt((K/10^12) * PS*(vᵀGv)/(T_s*(vᵀW_Pv))).

The old trace bound is also independently recomputed and required to match accepted #184 **exactly**. The selected source-action upper is min(old,new), ensuring no degradation even from integer rounding. The #184 centered variational residual, Q-energy drift, Rayleigh \(\mu\), strict null spectral gap and original accepted sine-angle bounds are preserved unmodified. Final sine-angle ceilings are outward integer ratios of the new centered residual over \(\delta-|\mu|\).

## Hosted result — true-flat angle bounds improved again

The first exact hosted [run 43513738681](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43513738681) **PASSED** including both frozen U/G source SHA pins, all 255 source Gram PSD principal-minor checks, both seven-dimensional weighted orthogonal source matrices with **127-minor** exact integer PSD minimal-eigenvalue checks and K−1 failures, the orthogonal negative control, exact old-action/Rayleigh-angle replay and strict no-float/integer audits. Its four output rows were filed **after that hosted result** in [RESULT-ORTHOGONAL-SCHUR.hbp](RESULT-ORTHOGONAL-SCHUR.hbp); the final-head workflow now requires a byte-for-byte reproduction. An additional independent BigInt path checked both new rational PSD-action square roots and both selected centered angle ceilings.

| Source-conditioned quantity | E1 | E2 |
| --- | ---: | ---: |
| Prior full trace `tr Lambda` upper | 0.009300530420 | 0.009362116755 |
| **Restricted eigenvalue `lambda_max(Lambda on x_perp)` upper** | **0.001550262708** | **0.001413946947** |
| Old full-trace Schur PSD action bound | 0.003456712890 | 0.003537919283 |
| **New orthogonal Schur PSD action bound** | **0.001411276469** | **0.001374920069** |
| Prior centered true-flat sine-angle bound | 0.108258863901 | 0.253465115951 |
| **New certified centered true-flat sine-angle bound** | **0.050165123494** | **0.114715901341** |

Both new angles are mathematically nonvacuous and improve their predecessors by more than a factor of two while preserving the same accepted #182 energy brackets, #183 energy-dependent directional Q bound, #184 Rayleigh null-branch identification, and #185 full-space W-normalization definitions. The source PSD uncertainty decreased because only the part of the correction that could actually **rotate** each flat trial vector was bounded; its scalar component plays no role in this centered step.

**Next exact test:** replace only the accepted sine-angle input values in the full-normalized W-state calculation from merged #185 and recompute the rigorous Q rotation, energy dependence, sample and true state norms, normalized full-state distance, and <1/700 actual-Wilson first-weight sufficiency gate. Freeze those two accepted angle inputs on a fresh branch **before** its rerun. Even a successful twofold projector improvement may remain far from the strict positive-weight target, and a HOLD must be preserved if so.

## Scope and next step

A successful smaller orthogonal-source action establishes an improved *true eigendirection* bound for the finite 3×4 S3 r=9 model, conditional on the existing Q-space Perron floor. It is **not** the normalized actual first-Wilson spectral weight. After acceptance, independently recompute the full P+Q true eigenstate errors with the exact B*B=72 I identity from merged #185 and compare the sum against the source-sufficient <1/700 Wilson sign-transfer test. The branch must preserve a genuine HOLD if the result is still too broad.

If the restricted eigenvalue does not materially shrink the PSD exterior source uncertainty, a larger but compressed exact-Q Krylov/Feshbach or stronger source-weighted resolvent certificate is the next mathematical avenue; simply adding precision to the existing fixed K3 trial will not remove its shell-4 residual.

## Run

    python3 -I -B independent/y137-Schur-orthogonal-PSD-20261113/replay.py

Accept only after immutable pre-code prediction, source SHA, exact 8×8 and 7×7 PSD checks, independent old-angle replay, deleted/perturbed-orthogonality negative control, dedicated hosted run, strict no-floating and native Rust checks, post-result receipt, and fresh byte-for-byte exact-head replay. Issue #137 stays OPEN until the true full-state Wilson amplitude interval has a strictly positive rational lower endpoint.
