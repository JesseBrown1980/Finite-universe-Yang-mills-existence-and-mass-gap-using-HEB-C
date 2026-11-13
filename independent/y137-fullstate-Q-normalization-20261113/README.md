# #137 — exact P→Q coupling Gram and *full W-normalized eigenstate* error budget

This is the next source-conditional certification step after the merged exact K3 energy microbrackets (#182), improved Q-directional Schur drift (#183), and both independently identified true eight-flat null directions (#184). Merged #180 supplies a **strictly positive original unshifted seven-loop Wilson fixed-sample** normalized squared transition >416300/10^9 between its chosen **exact Q-resolvent-dressed** flat sample vectors. The goal is to transfer that result to the true full-H E1 and E2 eigenstates.

The two true finite-H spectral windows, centered projector angle ceilings, source U/G SHA pins, gamma=94.0682 and the exact original Wilson fixed-sample lower-weight obligation were frozen in PREDICTION.hbp **before authoring this new source test**. The prior C source/replay version is unchanged.

## 1. Exact 8×8 B coupling Gram

Let P project onto eight flat orbit basis states and Q onto all nonflat gauge orbits. With the real W inner product, the P→Q coupling has raw matrix C and exact normalized Gram

    M = Cᵀ W_Q C,     W_P = diag(w_flat)
    B* B = W_P^(-1/2) M W_P^(-1/2).

Reconstruct all 155,378 Q states and the 1,985,218 shell-4 exterior objects using the accepted pinned K3 source; **all** P/Q C rows come from this graph. Rebuild the 8×8 **integer** M. Its trace must independently reproduce the previously accepted \(\mathrm{tr}(B^\ast B)=576\). The new falsifiable pre-result hypothesis is the much sharper **\(\boxed{M=72W_P}\)**, suggested by the two old source trial directions having \(\|Bx\|\approx\sqrt{72}\). This is a *hypothesis until exact hosted reconstruction*.

Whether or not the identity holds, the code finds the smallest **integer** \(K\in[1,576]\) satisfying \(KW_P-M\succeq0\), via exact checks of **all 255 principal minors** per candidate, and verifies \(K-1\) fails. Consequently the certified bound \(\|B\|\le\sqrt K\) is correct even if the 72-identity is rejected. A deleted P/Q electric edge provides a negative control: deleting one nonzero C coefficient must change the exact weighted Gram. Matrix rows, weights, K, source census and the control verdict are filed as exact integers.

## 2. Independently bound the exact Q-resolvent-dressed *sample* norms

For each source-pinned *flat-unit* sample direction v at frozen energy z, the previously merged #180 20-step K3 source trial has flat raw part \(T v\), \(T=10^{12}\), and Q trial \(\widehat y\). The **exact rational Q trial norm** is recovered independently from #180's filed integer full W norm:

    ||yhat||² = (norm_W - T² vᵀW_P v)/(T² vᵀW_P v).

The **complete** Q residual squared norm is recovered independently from the source Gram G

    ||r_z||² = (vᵀGv)/(6 b² T² vᵀW_Pv),    b=10^9.

The two reconstructed norms must match #184's independently filed per-trillion outward-rounding ceilings **exactly**. For \(R_z=(QHQ-z)^{-1}\), the accepted whole-Q floor gives

    max(0,||yhat||-||r_z||/(gamma-z))
         <= ||R_z Bv|| <= ||yhat||+||r_z||/(gamma-z).

All square roots are rounded outward with integer isqrt. This yields a rigorously enclosed norm for the **entire exact Q-resolvent-dressed sample state** \(T_z v=(v,-R_zBv)\), not just the 155,378-source Q slice.

## 3. Transfer from true eight-flat eigendirections to full normalized W eigenstates

At each true E_i from the certified #182 energy intervals, let x_i be the unit W-flat component of the exact simple eigenstate, phase aligned with the fixed-sample unit v_i. The #184 source-conditional centered Schur certificate has \(\sin\angle(x_i,v_i)\le s_i\), with

    s1<=0.108258863901,    s2<=0.253465115951.

The script uses the **sharp phase distance** implied by the sine ceiling,

    d_i=||x_i-v_i||<=sqrt(2[1-sqrt(1-s_i²)]),

with exact outward rational integer roots. This is tighter than the rough \(\sqrt2\,s_i\) bound.

For the Q components, the resolvent identity yields

    ||R_E B x_i - R_z B v_i||
       <= ||B|| d_i/(gamma-E) + |E-z| ||R_z Bv_i||/(gamma-E).

The code uses the exact integer 8×8 Gram bound \(\|B\|\le\sqrt K\), the #182 **true-energy brackets**, and the accepted #180/#184 full-Q residual norms. P/Q are W-orthogonal, so the total unnormalized state error is at most \(\sqrt{d_i^2+q_{\mathrm{err},i}^2}\).

For arbitrary nonzero full-state vectors u and v, the following exact normalization inequality is valid:

    ||u/||u|| - v/||v|||| <= ||u-v||/sqrt(||u||||v||).

Proof: writing a=||u||, b=||v|| and c=<u,v>/(ab), the normalized distance squared is 2−2c, while ||u-v||²/(ab)=a/b+b/a−2c≥2−2c. In our calculation both unnormalized states have unit P-component, and the accepted Q-tail enclosures give stronger **positive lower full-state norms** to use in the denominator. The emitted output includes independent exact intervals for the sample and true full-state norms, P/Q error components, and the final **normalized full-H state-distance ceilings**.

This is a genuine full-space Hilbert norm enclosure, conditional on the accepted source Q-floor and projector bounds. It still may be too broad to certify positive Wilson weight; no success is presumed.

## 4. Final rational spectral-weight gate

The accepted exact **unshifted** conventional seven-loop O has \(\|O\|\le14\), and #180 proves its **normalized fixed-sample amplitude is strictly greater than 1/50** (because its normalized squared weight >416300/10^9>1/2500). Thus, for two true normalized states Psi_i and the two exact-Q-dressed normalized samples U_i,

    |<Psi2,O Psi1>| >= |<U2,O U1>| - 14[||Psi1-U1||+||Psi2-U2||].

If the sum of independently certified full normalized-state errors is **strictly below 1/700**, the code may report a strictly positive rational lower bound for the true first Wilson spectral weight. If not, the acceptance verdict is **HOLD** and issue #137 stays open. All failure controls stop on incompatible K3 graph, source hashes, receipts, missing full-Q residuals or invalid rational normalization.

This lane may identify a major exact norm shortcut while simultaneously demonstrating how much *true eigendirection* accuracy remains to be gained. A HOLD is scientifically useful: the next work then targets the eight-flat Schur source/exterior residual rather than further Q normalization guesses.

## First hosted result: exact B isometry; full-state transfer HOLD

The first source-pinned [hosted run 43511704782](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43511704782) **PASSED** including all K3 source checks, exact no-floating-point and integer-only checks. Its six output rows were filed **after** the run as [RESULT-FULL-W-NORM.hbp](RESULT-FULL-W-NORM.hbp); the revised workflow requires byte-identical reproduction on the final head.

The previously frozen exact coupling-Gram hypothesis **was confirmed**. The full 8×8 raw integer `M=CᵀW_Q C` is diagonal with entries

    diag(M) = (72,216,144,216,216,144,144,144)
    diag(W_P) = (1,3,2,3,3,2,2,2)

Hence `M=72 W_P` **exactly**, so `B*B=72I_8` and the actual operator norm is `||B||=sqrt(72)=6sqrt(2)`. The complete source has **264 nonzero P/Q coupling entries**. This result is considerably stronger than the old `||B||<=24` Frobenius bound. The exact integer minimal-PSD test certified `K=72`, rejected `K=71`, verified the full weighted trace 576 and rejected a simulated missing-edge witness. It is a separate source-conditional finite Hamiltonian structure result.

The full Q-resolvent-dressed norm intervals (integer-rational outward enclosures, units J_E) are:

| Quantity | Fixed sample 1 | Fixed sample 2 |
| --- | ---: | ---: |
| `||R_z Bv||` | [0.245203944133, 0.259788930946] | [0.240019603536, 0.254910334285] |
| Complete fixed sample `||(v,-R_zBv)||` | [1.029623705155, 1.033194216323] | [1.028401385686, 1.031978332392] |
| Complete true eigenstate with **unit flat P component**, before normalization | [1.021221826434, 1.043424637589] | [1.011201082923, 1.057786913153] |
| True-vs-sample aligned flat P error | ≤0.108418281771 | ≤0.255560061211 |
| Q error from P-direction rotation | ≤0.038080440021 | ≤0.089910305721 |
| Q error from true-vs-sample energy shift | ≤0.000014791630 | ≤0.000017225718 |
| **Full normalized W-state distance** | **≤0.112068242735** | **≤0.265669528365** |

The total rigorously enclosed true-vs-fixed-sample normalized state distance is **≤0.377737771100**, whereas the sufficient positivity target inherited from merged #180 is **<1/700≈0.001428571429**. The source-based inequality therefore gives an explicit **HOLD**, with a gap of over 264× in this sufficient bound. The code reports `transfer_sufficient_gate=0`, `true_E1_E2_positive_Wilson_weight=0` as an *unproved* acceptance status, never as a claim that the actual physical matrix element vanishes.

**New mathematical priority:** the complete full-state normalizations are now rigorously enclosed; the source Q-energy dependence contributes only about `1.5–1.7×10^-5` per state. The overwhelming contribution is the currently permitted flat projector rotation (0.1084/0.2556), itself driven by the residual Schur uncertainty of roughly 0.0035–0.004. The next calculation should prioritize a sharper exact **source Q Schur error action**, likely by improving exterior residual/Schur spectral bounds or a larger/source-efficient Krylov Feshbach certificate. Additional digits in the same K3 trial and slightly narrower energy windows alone will not close this factor-264 error budget. Another possible route is an operator-specific Wilson transition interval requiring much less uniform eigenvector accuracy.

## Run

    python3 -I -B independent/y137-fullstate-Q-normalization-20261113/replay.py

Dedicated hosted CI must verify the pre-code frozen prediction and accepted #180/#184 receipt files, run the exact K3 source Gram and independent full-norm integer propagation, pass strict no-float and native gates, then file the *post-result* output and require a byte-identical replay at the accepted final head.
