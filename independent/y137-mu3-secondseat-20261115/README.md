# GPT-6 independent adversarial review: #137 μ3 acceptance window (15 Nov 2026)

**Scope:** independent mathematics and a small, explicit, exact adversarial source. This review is based on the current author's [PR #198](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/198), including \`independent/y137-mu3-acceptance-20261115/mu3_acceptance.py\`. Its real large-Q μ3 remains **NOT_COMPUTED** and the first Wilson spectral weight remains **HOLD**.

## Algebraic verdict: necessary Loewner window is correct

Let \`mu_k=Bᵀ X^k B\`, \`0<g I<=X<=h I\`. Positive spectral weights \`X-g\` and \`h-X\` on the pair \`(B,XB)\` yield respectively

    [[D,C],[C, μ3-g μ2]] >=0,  D=μ1-g μ0, C=μ2-g μ1
    [[E,G],[G, h μ2-μ3]] >=0, E=h μ0-μ1, G=h μ1-μ2.

For \`D,E>0\`, Schur complementation gives the submitted sharp window

    g μ2+C D^-1 C <= μ3 <= h μ2-G E^-1 G.

That is a valid **necessary** constraint on the true third moment. The four-moment Gauss bound on \`F=BᵀX^-1B\` and the Lobatto bound from \`(X-g)(h-X)\` are also algebraically correct, when the respective inverse blocks are positive definite. In the abstract truncated matrix-valued Hausdorff moment problem, the localizer inequalities characterize existence of **some representing measure**, subject to appropriate rank assumptions. They do not identify the moment of the **specific fixed finite operator** used for Yang–Mills.

## Independent archived 8×8 arithmetic replay — PASS

The separately authored `archived_window_replay.py` reads the original accepted-K3 whole-Q source/cache and μ1/μ2 files, pins their Git blob SHA-1 hashes, checks the original μ0/μ1/μ2 8×8 SHA-256 matrices, and independently calculates the matrix window and the #197 cubic envelope at both frozen energies. It uses **rational Gauss-Jordan inversion and symmetric Schur-elimination positivity checks**, rather than the original `moment_radau`/ `mu3_acceptance` helpers or principal-minor determinant enumeration.

| Frozen z integer | Independent μ3 window trace width, per million of #197 envelope | Verification |
|---|---:|---|
| `69909875505` (E1) | **53,853** | Pin, positive pivots, interval nesting PASS |
| `69949729820` (E2) | **53,856** | Pin, positive pivots, interval nesting PASS |

The replayer independently reproduces the original numerator-only fingerprints **and additionally seals the exact rational boundaries**, including each fraction's reduced numerator and denominator, in `RESULT-ARCHIVED-8X8.hbp`. This independently confirms the ~18.6× contraction measured by the author. The source archive and the independent calculation do **not** contain a real μ3; no actual four-moment full-Q Wilson-weight claim follows from these width numbers.

## Three adversarial exact 8×8 probes

Run \`python3 -I -B adversarial_mu3_check.py\`. It uses only standard-library exact fractions, defines a separate physical 16-state system \`X=diag(2I8,3I8)\`, \`B=[2I8;2I8]\`, and never imports the author's code.

**A. In-window forged physical value:** \`mu0=8I8\`, \`mu1=20I8\`, \`mu2=52I8\`, and the **actual** \`mu3=140I8\`. At \`g=1,h=4\`, the moment window is exactly \`[412/3 I8,428/3 I8]\`. **\`139I8\` is integral, symmetric, strictly inside that window**, and has positive Gauss/Lobatto pivots, so it passes the author's present \`accept(candidate,L,U)\` test. But the resulting four-moment Gauss lower bound \`F>=64/19 I8\` actually **excludes the known true** \`F=10/3 I8\` because \`64/19>10/3\`. This proves \`accept\` is only an *envelope plausibility filter*, never independent authentication of the actual Q5 calculation. The forged sequence has an alternative valid representing measure; it is not the moment of this chosen \`X,B\`. The proper gate must recompute source rows, μ2 regression, and μ3 from the **frozen operator**.

**B. Insufficient rational window fingerprint:** The code \`mr.sha(to_int(L))\` strips the common denominator used to clear an entire rational matrix. Consequently \`I8\` and \`(1/2)I8\` have **the same denominator-cleared integer matrix and thus identical hash input** despite being different rational matrices. This is a serialization ambiguity, not a SHA-256 cryptographic collision. Pin a canonical serialization of each entry as *reduced numerator and denominator*, with dimensions, \`g,h\`, sample z, source pins, and the candidate's exact integer-matrix hash. Existing \`window_lower_integer_sha256\` and \`window_upper_integer_sha256\` alone are inadequate to identify a rational boundary.

**C. Correct but rank-deficient true moment:** \`X=2 I8\`, \`B=2 I8\` has \`mu_k=4·2^k I8\`; \`D,E>0\` and the window is a single point \`L=U=mu3=32I8\`. The true moment passes \`accept\`, but \`P=μ3−μ2 μ1^-1 μ2=0\`, so \`bracket4()\` rejects an actual valid physical moment because \`inv(P)\` is undefined. The 8×8 large-Q calculation may have strictly positive pivots; that must be **checked after actual μ3**, and a singular case must be explicitly classified (rank-aware pseudoinverse with range proof, or HOLD), rather than presented as a fabricated μ3.

## Acceptance conditions before computing real Q5 μ3

1. Freeze both energy samples and every exact \`V1/b\` binary spool manifest and source byte count; verify all 18,598,040 Q5 amplitudes and group W weights.
2. Recompute all complete **72 raw Q5 electric moves per actual source** by a separately authored S₃/gauge-tree verifier; aggregate contributions to the same destination across shards **before** any bilinear product. Include a missing/replaced-edge and source-count red control.
3. Reproduce the already accepted μ2 **byte-identically** and verify both original μ0/μ1/μ2 and physical/source-unit pins; evaluate the signed actual μ3 with exact integer arithmetic and correct \`b=10⁹\` convention.
4. Require the necessary window and original #197 cubic envelope, and additionally the **positive definiteness/rank conditions** for the four-moment inversion. Do not infer true source provenance or unique μ3 from the window. Use full rational boundary hashes.
5. Carry the **actual** four-moment bracket through the full-state normalization transfer at both energies and check \`<1/700\`. The author's five affine interpolation scenarios give useful *illustrations*, but do not provide an interval-wide bound on the future measured four-moment width or the nonlinear normalized error.

**Review verdict:** \`GRAM_WINDOW=CONFIRMED\`; \`QUADRATURE_FORMULAS=CONFIRMED_WITH_RANK_HYPOTHESES\`; \`FIXED_SOURCE_MU3_IDENTIFIED_BY_WINDOW=REFUTED\`; \`CURRENT_RATIONAL_BOUNDARY_HASH=AMBIGUOUS\`; \`FIVE_SCENARIOS=NOT_UNIVERSAL_BOUNDS\`; \`REAL_Q5_MU3=HOLD\`; \`WILSON_WEIGHT=HOLD\`.
