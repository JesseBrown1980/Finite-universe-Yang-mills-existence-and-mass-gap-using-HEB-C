# Stage G — exact eight-flat Wilson action feasibility test

**2026-11-16, independent small-model check.** Tracks [issue #236](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/issues/236) separately from the accepted Stage E/F findings. The executable authenticates four original Git blobs and reconstructs all eight commuting-pair flat gauge orbits using the 3×4 S₃ lattice's tree gauge fixing and simultaneous conjugation. The full-Q action norm is intentionally not calculated.

## Target and precise limitation

Original #180 establishes the strict fixed-sample **unshifted** Wilson amplitude `|<U2,O U1>| > 1/50`. The two exact normalized original full-Q-resolvent-dressed samples appear in #180 and #185; Stage E/F uses their identical flat vectors and sample energy numerators. For the accepted full-state error upper bounds

```
d1 = 3235251105 / 10^12
d2 = 8676646901 / 10^12
```

the sufficient first Wilson positivity inequality is

```
d2 ||O U1||_W + d1 ||O* U2||_W + 14 d1 d2 < 1/50.
```

O is a *real diagonal multiplication observable* in the canonical gauge-orbit basis, therefore W-self-adjoint, with global |O| <= 14. The common upper action-norm threshold `c < 1.64600168247627...` is only a proposed sufficient target.

The cheap exact test is designed to **refute this sufficient route for the original unshifted observable** if even its *lower* action-norm contributions are too large.

## Reconstructed flat data, before hosted acceptance

Canonical group-theoretic enumeration gives

```
Wflat = (1,3,2,3,3,2,2,2)
Oflat = (14,8,5,6,0,2,-7,-7)
```

where `Oflat[i]=4 chi(a_i)+3 chi(b_i)` for the faithful real S₃ character `chi`. The original exact #180 flat vectors are independently checked against historical #184's frozen vectors.

For each sample's flat vector v and exact Q-resolvent tail q, with `||q|| <= q_upper`, W-orthogonality gives the rigorous lower bound

```
||O U||_W^2 >= [sum_i Wflat_i Oflat_i^2 v_i^2] /
                   [(sum_i Wflat_i v_i^2)(1 + q_upper^2)].
```

Here the accepted #185 outward Q tail ceilings are 259788930946/10^12 and 254910334285/10^12. All source-bound identities, sample vector/energy IDs, original Q-trial Gram and W norm receipts, and the independent flat enumeration must match exactly. The executable proves conservative `||O U1|| > 8`, `||O U2|| > 4` by cross-multiplication, plus tighter downward-rounded endpoints. These **necessary lower bounds** suffice to disprove the proposed sufficient gate for these same samples, since

```
8*d2 + 4*d1 + 14*d1*d2 > 1/50.
```

This rejects only the **raw, unshifted, fixed-sample action-norm sufficient method** at the accepted `d1,d2`; it does not prove anything about absence of a true Wilson transition, a shifted observable, or a different certified sample.

## Controls and source seal

The script rejects changed original Git-blob hashes (#180 original Wilson receipt, #185 W-normalization receipt, original 3×4 S₃ definition, historical centered-trial definition), altered orbit weights, changed observable values, swapped fixed trial vectors/energies, missing Q norm upper, omitted original Q-trial identity and invalid negative controls. Source identity must match the same exact dressed fixed samples; no K3 20-step vector is passed off as an exact resolvent solution.

The hosted workflow runs the repository's strict integer-only and no-floating-point gates, independently checks the negative controls, verifies the exact cross-multiplied inequality and stores all SHA-256 receipt digests and the complete test output. Keep this research **DRAFT** for independent review, with #137 **OPEN/HOLD**.

Follow-on candidates are a source-authenticated shifted observable `O-alpha I` with corrected fixed-sample overlap and action norms, or an operator-specific transition bound avoiding the global triangle inequality. Do not launch a costly full-Q unshifted action computation once this cheap no-go is independently accepted.

## Hosted production result — scoped exact PASS

[Run #43942690259](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43942690259), job `133564075990`, **SUCCESS**. Strict integer-only/no-FP source audit, original Stage D forged-SHA/energy-swap refusal, four pinned Git source blobs, matched original #180/#185 samples, exact eight-flat enumeration, negative controls, exact inequality comparisons and SHA artifact upload PASS. The four original result lines are preserved verbatim, with run/source provenance, in [RESULT-STAGE-G-FLAT-20261116.hbp](RESULT-STAGE-G-FLAT-20261116.hbp). Independent scientific review remains pending.

The exact squared W-action lower fractions emitted for the original *unshifted* observable are:

| Original sample | Certified lower endpoint, strictly greater than | Simpler exact lower |
|---|---:|---:|
| `||O U1||_W` | 8.271659711561 | 8 |
| `||O* U2||_W` | 4.176870452630 | 4 |

The decimal endpoints are **downward-rounded to 12 places**; the source uses the exact integer squared fractions and comparison. The two denominator/Q norm identities and eight physical flat weights were checked against pinned receipts.

With the accepted Stage E/F error *ceilings*, even the conservative lower numbers yield an LHS **strictly greater than**

```
(8*d2 + 4*d1 + 14*d1*d2)
= 82747175468638171058470 / 10^24
= 0.082747175468638171058470 > 0.02 = 1/50.
```

Thus the present **raw, unshifted original-sample action-specific sufficient test** fails by more than fourfold before examining any nonflat Wilson action. Improving the conservative eigendirection error bounds or using a different, correctly re-certified observable/sample remains a possible mathematical route. This numerical obstruction does **not** establish that the true Wilson spectral weight vanishes.

**Disposition:** scoped small exact test PASS, raw-unshifted Stage G norm route **NO-GO with current d1/d2**, full-Q action norm **not computed**, shifted observable **not tested**, Wilson first-excitation spectral weight **HOLD**, issue #137 **OPEN**, PR **DRAFT** pending independent review.

## Separate candidate gate: previously certified shift `O - 7/2 I` and both exact sample amplitude upper bounds

The original #180 dual residual calculation certifies more than the sample-amplitude lower endpoints: it supplies the signed centre and a strict absolute error for `O2 = 2O-7`, plus a complete-Q upper bound on the fixed-sample overlap. Using only those original integer receipts and the original eight-flat normalization lower bounds, a **new source-conditional analytic test** can upper-bound the actual *normalized* sample amplitudes of both `O-7/2 I` and raw `O`. This is separate from the accepted fixed-sample positivity result.

For `Oshift=O-7/2 I`, the eight-flat action lower uses `(2Oflat-7)^2/4`; exact-Q normalization uses the same upper tail norm. The certified global norm is `||Oshift||<=21/2`. If `C` is the original #180 centre numerator, `E` its absolute error and `H` the source-certified full-Q overlap absolute upper (all in the original same integer scale), then with original flat squared unnormalized vector norms `P1,P2`:

```
|<U2,(O-7/2 I)U1>| <= (|C|+E) / [2*b*T^2*sqrt(P1*P2)]
|<U2,O U1>| <= (|C|+E+7H) / [2*b*T^2*sqrt(P1*P2)]
```

where `b=10^9`, `T=10^12`, and the implementation rounds `sqrt(P1*P2)` **down** and resulting amplitude ceilings **up**. It independently requires original #180's certified shifted raw centre and *unshifted overlap correction*, rather than assuming fixed samples are orthogonal. A sample Q-tail is nonnegative norm, so replacing full sample normalization by flat-only gives a valid (looser) upper amplitude bound.

The proposed exact comparisons are:

- Shifted flat action norm lower: `||Oshift U1||>5`, `||Oshift U2||>2`, giving strict linear transfer cost greater than `5d2+2d1=0.049853736715`.
- Original shifted actual sample amplitude **upper** is approximately `0.037261136` (requires hosted exact-rational verification).
- Original raw actual sample amplitude **upper** is approximately `0.050347150`; the raw linear transfer cost alone exceeds `8d2+4d1=0.082354179628`.

If the hosted comparisons PASS, **both the raw and the specific already-certified 7/2-shifted first-order action-norm sufficient inequalities are excluded with the present frozen E/F conservative state errors**, even allowing each original sample's actual amplitude instead of only its previously certified lower amplitude. The original #180 *fixed-sample amplitudes remain positive*; the obstruction concerns the cost of transferring them to the true eigenstates with the present general norm bounds. Other shifts, improved eigendirection bounds or direct Wilson-specific projector estimates remain open.
