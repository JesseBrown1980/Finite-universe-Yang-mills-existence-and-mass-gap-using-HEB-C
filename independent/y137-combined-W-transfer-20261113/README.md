# #137 — combined exact 7D Schur, sharp B norm and complete W-state transfer

This is the next independent post-merge calculation after finite S3 r=9 source-conditional certificates #182 (true energy intervals), #183 (Q-directional drift), #184 (centered Schur branch identification), #185 (full-Q norms and exact B*B=72I) and #186 (exact 7D orthogonal Schur-source correction).

The original unshifted conventional seven-loop Wilson source certificate from merged #180 establishes a **strict positive normalized fixed-sample Q-resolvent-dressed** squared transition >416300/10^9, hence fixed sample amplitude >1/50, and the raw Wilson norm is ≤14. That result is *not yet* a certified exact E1→E2 spectral weight. The sufficient sign-transfer gate is a sum of rigorously certified normalized true-to-fixed sample state errors <1/700.

The exact 7D source result from merged #186 reduced the source-flat sine-angle upper bounds to E1 ≤0.050165123494 and E2 ≤0.114715901341. However, both #184 and #186 still used the older global B coupling norm estimate ≤24 in the *energy-dependent directional Schur error*. Merged #185 subsequently established the much sharper exact operator identity B*B=72I, so **||B||=√72=6√2**. This branch composes those improvements, preserving every original source SHA and normalizing in the complete Q Hilbert space.

## Exact refinement

The Schur operator obeys \(S(E)-S(z)=-(E-z)I-(E-z)B^*R_E R_zB\). The accepted 7D source error bound only concerns the centered action that rotates the flat eigenvector, so its Q-dependent energy term may rigorously use

    epsilon_extra(E,z) <= |E-z| ||B|| ||R_z Bx||/(gamma-E).

This runner substitutes the **outward integer upper** on √72, while preserving the previously accepted full-Q \(\|R_zBx\|\) upper and source floor γ=94.0682. The new term must be strictly smaller than the old norm-24 term, and both are printed. Since the *same term* enters the full absolute Rayleigh bound, the valid null-branch quantity is also tightened by exact integer subtraction:

    mu_new = mu_old - epsilon_old + epsilon_new.

The strict \(\mu_{\mathrm{new}}<\delta\) gate is checked before recomputing the centered sine-angle ceiling:

    sin(theta_new) <= (U_centered + Lambda_orthogonal_action + epsilon_new) /
                      (delta - mu_new).

Both the old source-energy and new 7D-source residual inputs come from accepted independent hashes and integer witness receipts; no source matrix is recomputed or guessed in this composition-only test.

## Complete full-state normalization again

The accepted source Q resolvent norm intervals from #185 are independently used, and the already certified true E1/E2 energy windows are preserved. The phase-aligned P-unit direction distance upper is the outward integer value

    d_P = sqrt(2[1-sqrt(1-sin²theta_new)]).

The exact entire Q-space tail difference upper is

    d_Q <= sqrt72*d_P/(gamma-E_hi)
           + |E-z| ||R_zBx||/(gamma-E_hi).

The P and Q summands are orthogonal, so the unnormalized error is bounded by \(\sqrt{d_P^2+d_Q^2}\). For the actual two complete W states, the script uses their **positive lower full-state norms** and the rigorous normalization inequality \(\|u/\|u\|-v/\|v\|\|\le\|u-v\|/\sqrt{\|u\|\|v\|}\). Every Q-tail and normalization term is outward-rounded by integer isqrt and checked against the earlier accepted #185 outputs. The pure-int source file does not generate synthetic Q data; it derives this updated result from already accepted exact mainline receipts.

## Prediction, acceptance and HOLD protocol

An exploratory **independent BigInt preflight** predicted (before the new Python hosted replay) new conditional flat-projector sine upper bounds 0.043364646417 and 0.095928035901, full-normalized W-state error uppers 0.044731270536 and 0.099359189983, and combined upper 0.144090460519. All were sealed in [PREDICTION.hbp](PREDICTION.hbp) before writing the new code, and the new hosted replay **must match them exactly**.

Even if this numerical prediction is reproduced, the combined 0.144090460519 remains above 1/700≈0.001428571429, so the required verdict is an explicit **HOLD**. A negative result here means *proof not yet achieved*, not that the physical transition vanishes. Source independence, direction/energy selection, exact whole-Q W normalization and both original fixed-sample positive Wilson inputs remain recorded.

The next mathematical source step should reduce the dominant K3 **shell-4 exterior residual**, which the accepted #180 source receipt shows contributes more than 999999999 parts per billion of the complete Q residual square. A targeted compressed K4/K5 source Krylov/Feshbach calculation or stronger exact exterior resolvent supersolution is needed; simply adding inner K3 Jacobi digits cannot remove that boundary. Alternate operator-specific Wilson signed intervals are acceptable only with complete rational Q-error, eigenstate and normalization controls.

## First hosted combined result: accepted inputs, strict Wilson HOLD

The first [hosted run 43515558442](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43515558442) **PASSED** with exact input receipts and all four original frozen exploratory numerical predictions. Its five exact output rows were filed **after that run** as [RESULT-COMBINED-FULL-W.hbp](RESULT-COMBINED-FULL-W.hbp). The subsequent workflow requires a byte-identical replay at the final head. The original successful result was independently precomputed in BigInt arithmetic using accepted #184/#185/#186 receipts, before the new hosted Python checker was authored.

| Rigorously source-conditional quantity | E1 | E2 |
| --- | ---: | ---: |
| Prior accepted #186 true-flat sine-angle upper | 0.050165123494 | 0.114715901341 |
| New exact `sqrt72` Q-energy extra upper | 0.000125511135 | 0.000146165063 |
| New absolute Rayleigh `mu` upper | 0.002785767511 | 0.003112956068 |
| **New centered true-flat sine-angle upper** | **0.043364646417** | **0.095928035901** |
| Phase-aligned unit-flat error upper | 0.043374848196 | 0.096038826045 |
| Q error from P-angle upper | 0.015234822746 | 0.033788065983 |
| Q error from energy upper | 0.000014791630 | 0.000017225718 |
| **Complete normalized full-W state error upper** | **0.044731270536** | **0.099359189983** |

The summed normalized true-vs-fixed state error upper is now **0.144090460519**, improving the previous accepted #185 bound of 0.377737771100 by a factor of about 2.6. This uses no new eigenvalue or source estimates: it composes independently accepted exact Gram/7D Schur/Q-tail receipts with strictly outward integer arithmetic.

**Proof obligation still HOLD.** The sufficient sign-transfer bound from the original unshifted seven-loop fixed-sample positive amplitude >1/50 and operator norm≤14 is combined error **<1/700≈0.001428571429**. This result remains about 101 times larger. The Q-energy variation (~1.5–1.7×10^-5) is negligible; nearly all of the remaining guaranteed error arises from residual allowed eigendirection rotations. Accepted #180's exact source Q residual is >99.9999999% shell-4 exterior, so the next substantial proof work must improve the **exterior Schur Q source** through a targeted larger-shell source reduction or a sharper rigorous boundary resolvent certificate, with an operator-specific signed Wilson bound as an alternative. The actual E1→E2 first spectral weight remains unproven and issue #137 stays OPEN.

## Run

    python3 -I -B independent/y137-combined-W-transfer-20261113/replay.py

Acceptance requires frozen pre-host predictions, independently accepted #184/#185/#186 exact receipt bytes, exact integer-only/no-floating-point CI and native verification. File fresh hosted result after the run, then enforce byte-identical replay at the accepted final head. The true first Wilson spectral weight remains OPEN on issue #137 unless the final strict rational sign gate passes.
