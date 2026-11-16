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
