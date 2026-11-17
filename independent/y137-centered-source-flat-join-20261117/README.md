# Issue #137 — exact centered Wilson physical-source acceptance join

Research draft, November 17 2026. This is a side-by-side falsifiable source-specific test of the user's rational Wilson centering idea. It is stacked on the already hosted original unshifted PR #278 dual-plus-true-flat source join, and reuses its exact conditional true E1/E2 eight-flat sine enclosures. Both the centered dual source and the centered 8x8 operator source are independently recomputed from original 3x4 S3 gauge-orbit data.

## Two independently hosted original-source inputs

1. Centered original Wilson dual [PR #281](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/281), hosted run #44119924916: the full original seven-loop integer O2=2O−7I on both flat and nonflat gauge orbits, full shell4 residuals and signed Q dual corrections at true physical E1/E2 upper endpoint energies. The source certifies positive fixed-flat-direction squared O2 normalized transition lower >0.004232581 over both true physical energy windows. This corresponds to a fixed-flat-direction centered O=O2/2 squared weight lower >0.001058145. Nonorthogonal trial overlap is correctly included.
2. Centered original 8x8 full-Q Oeff [PR #282](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/282), hosted run #44120602178: all 64 signed rational original S3 O−7/2 effective-observable matrix intervals across both true E1/E2 physical energy brackets, including complete shell4 physical residual and rigorous true-energy resolvent drift. The maximum entrywise error radius decreases from the unshifted 0.147048109574 to centered 0.110286082181.

Both input receipts and source run/head/job IDs are frozen exactly into this PR. The new verifier refuses absent/malformed original source rows, mixed operator-scale denominators, wrong physical windows, missing exterior shell4 and inconsistent O2 shifted dual source.

## Independent strict true-flat transition test

For exact physical normalized *flat* components x_i of the simple E1/E2 eigenvectors and the original fixed source flat unit vectors v_i,

    x_i=c_i v_i+h_i,  h_i orthogonal to v_i,
    ||h_i||<=s_i, c_i>=sqrt(1-s_i²).

Stage E signed four-moment transfer supplies source-conditional s1<=0.003429010525, s2<=0.009197961975. Independently accepted original W-flat eigendirection-to-true physical state transfer remains source-conditional pending complete peer audit.

Use the centered matrix receipt's signed integer A_ij with denominator 2*T² to represent the **integer O2 effective operator** with the numerators unchanged and denominator T². This is exactly consistent with the centered source dual, whose lower squared fixed-direction weight is for O2, NOT for O−7/2. The source-specific full-Q QOQ correction and exact scalar shift are therefore represented with the same observable everywhere.

Then the exact rational sufficient gate is

    true_signed_unnormalized_abs >
      sqrt(1-s1²)*sqrt(1-s2²)*sample_O2_lower
       - s1*zstar2_O2 - s2*z1_O2 - s1*s2*||M_O2||,

with zstar2 and z1 the deflated exact source matrix-action norms enlarged by the complete 64-entry centered source interval. Source Q-floor and exact B†B=72I give the operator norm bound for O2. The verifier applies outward integer roots and strict signed cross comparisons.

A positive strict margin would imply nonzero true O2 transition in the simple E1/E2 state, and thus nonzero original seven-loop Wilson E1/E2 transition by exact eigenstate orthogonality and O=O2/2+(7/2)I. Full Feshbach state norms are positive finite from the source Q spectral floor; high-precision normalization is unnecessary for proving positivity, though necessary for a quantitative normalized lower weight. A nonpositive margin is an honest HOLD for this sufficiency criterion; it does not imply the physical true transition vanishes.

## Acceptance policy

The calculation must emit true source signal, contamination, strict signed margin, exact E2-only and joint-sine feasibility frontiers, and negative control under increased E2 angle. Even if a candidate margin is positive, the original physical Wilson weight remains HOLD pending independent source and proof review. The whole finite 3x4 S3 spectral E2-E1 gap remains conditionally certified, while the continuum mass-gap theorem remains OPEN.

Reproduce with the dedicated hosted workflow y137-centered-source-flat-join.yml.


## Hosted original-source acceptance result

[Hosted run #44121731435](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44121731435) completed all exact integer, no-float, source provenance, 64-entry centered matrix and false-control gates successfully. The source audit accepts the **calculation**, but the actual first original Wilson weight is **HOLD** because the strict signed sufficient margin remains negative.

All numbers below are exactly outward-rounded integers per 10^12. Because the joined source is the integer **O2=2(O−7/2 I)**, the first table is stated in the O2 units actually verified by the source.

| Exact source quantity (O2 units) | Per trillion |
|---|---:|
| Certified fixed flat-direction source amplitude lower | 65,058,289,248 |
| E1/E2 cosine-adjusted true transition signal lower | 65,055,154,676 |
| Full Q/deflated/eigendirection contamination upper | 134,574,028,374 |
| **Strict signed true flat transition margin** | **−69,518,873,698** |

Dividing the signal, contamination and margin by **two** yields the physical centered observable O−7/2 I, whose matrix element between true distinct physical eigenstates is exactly the original seven-loop Wilson matrix element:

- Guaranteed centered signal lower: 0.032527577338.
- Certified centered contamination upper: 0.067287014187.
- **Signed centered margin: −0.034759436849 (HOLD).**

The previous unshifted original true-flat acceptance (#278) yielded signal 0.032060426466, contamination 0.103852473556, signed margin −0.071792047090. Thus centering improves this precise source-conditioned sufficient test substantially, although no positive true-state Wilson certificate follows.

The **exact integer bisection sufficient frontiers** for the *centered* source, with all other accepted input bounds frozen, are:

- Keep s1=0.003429010525 and require s2 **≤0.003418880542** (strict positivity at this recorded integer bound). Current s2=0.009197961975, so an improvement factor approximately 2.69 is still needed in this particular proof method.
- Alternatively improve **both** accepted sine ceilings by a common multiplicative scale **≤0.484814396289** (the recorded sufficient integer scale). This is a sufficient but not physically necessary condition.

Neither frozen original full-Schur bracket-splitting attempt in PR #279 (seven E2-only cutoffs; three E1 and three E2 simultaneous) tightened the source-conditional Stage E energy intervals. The previous simple 40/60-iteration Q Jacobi depth tests also failed to improve the unshifted entry error. Those negative controls favor source-specific projector and observable-action improvements rather than merely adding iterations or cutoffs.

The original finite 3x4 S3 first energy gap remains conditionally accepted. Issue #137 original normalized first-excitation Wilson weight remains HOLD, and the four-dimensional continuum Yang–Mills theorem remains OPEN. Independent scientific review of all source-conditional Stage E, centered dual, centered matrix, and this joined inequality is still required.
