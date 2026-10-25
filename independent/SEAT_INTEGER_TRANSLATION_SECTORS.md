# Integer-only translation-sector acceleration for the fixed finite S₃ torus

**Draft independent verifier.** Scope: 1,393-state periodic 2×2 spatial lattice, gauge group S₃, existing operator SHA `b6c608f50f81f3bf48fb0203b48e0e3bfc867037dc1d0a96633aa80b962137f3`. No new physical operator and no continuum/volume-uniform claim.

## Actual matrix trick

The precise symmetry is the spatial translation group `Z₂ × Z₂`. On the raw eight oriented links (four x-oriented and four y-oriented), each translation relabels its vertex while preserving link orientation. A translation of a gauge-orbit basis state must be **followed by exact spanning-tree gauge fixing and S₃ conjugacy canonicalization**. Simply permuting the five tree-gauge variables would be incorrect.

The independent `seat_translation_sectors.py` builds the native-SHA-matched model from PR #7, then verifies, **entirely with integers**:

1. Four maps on all 1,393 orbit states are genuine permutations, preserve positive Gauss weights and magnetic energy, and commute with **every electric matrix coefficient**.
2. Both generators square to the identity; the group law for every composition is exact.
3. The 1,393 configurations form 385 translation orbits: 319 of length 4, 51 of length 2, and 15 of length 1.
4. Every allowed translation character (`T_x,T_y`) gets one signed orbit basis vector. A character incompatible with an orbit's stabilizer has no vector for that orbit; **do not force four equal blocks**.
5. The projected integer electric and magnetic operators obey exact weighted self-adjointness and the **full intertwining identity** `H B_chi = B_chi H_chi` on every source vertex for every character basis vector. The four character spaces have total dimension 1,393 and form a direct sum.

| Character | Projected dimension | Directed electric coefficients | Matrix SHA-256 |
|---|---:|---:|---|
| `(+,+)` | 385 | 7593 | `fb6dbb3acbd411f61779f98881e6545d21ab7a39816c351d755fafe2c3f2c652` |
| `(+,-)` | 336 | 6526 | `9dc22f4bb6f410ebfcdc0bfb3854bf6d2827901ee379ed685772649d28315d48` |
| `(-,+)` | 336 | 6526 | `88eb8250eaf85815f155f09656f8a4dd19733148dd9e4505af978bed5974a75b` |
| `(-,-)` | 336 | 6400 | `d7dce164177f2b5498a367c9df78ff8d64c8d173a262daa65815b321ff21b653` |

The reduction `1,393 → 385+336+336+336` is *exact*. Weighted block masses are `orbit_size * original_Gauss_weight`, and signed amplitudes are only `+1/-1`. There are no square roots, decimal trigonometric characters, floats, or JSON. The four matrices use the same integer-only Sturm input grammar as PR #8.

## Direct-sum proof of inertia

Each block contains the exact integer electric matrix `E_chi`, diagonal `M_chi`, and positive weights `W_chi`. For any integers `JE,JB,T`, the verifier constructs

`B_chi = W_chi (1000 JE E_chi + 1000 JB M_chi - T I)`.

Integer outward-rounded Schur elimination counts its negative pivots only if **every pivot interval is sign-definite**. By the symmetry decomposition and Sylvester's law, the full Hamiltonian's negative count below threshold `T/1000` is exactly the **sum** of all four block counts. The `seat_translation_sturm.py` verifier fails closed on any ambiguous pivot, missing source, altered SHA, or incomplete sector; no threshold is assumed positive by definition.

Four known full-matrix control thresholds, also verified via the other seat's independent Python and native GMP audit, have the expected complete split:

| `JE,JB,T` | `++` negative | `+-` negative | `-+` negative | `--` negative | Sum |
|---|---:|---:|---:|---:|---:|
| `1,1,13240` | 1 | 0 | 0 | 0 | **1** |
| `3,5,50840` | 1 | 0 | 0 | 0 | **1** |
| `1,1,7000` | 0 | 0 | 0 | 0 | **0** |
| `1,1,13300` | 3 | 0 | 0 | 0 | **3** |

Every one of the four block computations must finish its full number of pivots; zero-containing pivots are not tolerated. The controls prove the code doesn't simply force a total of one negative eigenvalue. They also show the three lowest levels at the last threshold occur in the fully symmetric translation sector **for these tested couplings only**; don't generalize excited-state classification.

## Speed and SHA boundaries

An exploratory local Python integer-interval run at `10^30` scale gave approximately **11.6 seconds** for the `1,1,13240` four-sector pass and **6.8 seconds** for `3,5,50840`, against the previously reported `~80 seconds` per full-matrix integer check. Platform, pivot ordering, arithmetic implementation and source size differ; these are **observed local timings**, not a universal 16× guarantee. Other full controls can take longer.

SHA-256 pins the native full operator and **each exact sector matrix**. A matching SHA allows previously verified results to be reused once a trusted execution receipt exists; **hashing a new uncomputed threshold does not yield a spectral answer**. This prototype does not yet claim an authenticated cross-host persistent SG-RAM cache. Full HBP/HBI or signed provenance must be connected separately before relying on remote cache hits.

## Reproduction

```bash
python3 independent/seat_translation_sectors.py /tmp/sector_s3 \
  > /tmp/sector_s3.measure
cmp /tmp/sector_s3.measure independent/seat_translation_sectors.measure

{
  python3 independent/seat_translation_sturm.py /tmp/sector_s3 1 1 13240 30 1
  python3 independent/seat_translation_sturm.py /tmp/sector_s3 3 5 50840 30 1
  python3 independent/seat_translation_sturm.py /tmp/sector_s3 1 1 7000 30 0
  python3 independent/seat_translation_sturm.py /tmp/sector_s3 1 1 13300 30 3
} > /tmp/translation_sturm.measure
cmp /tmp/translation_sturm.measure independent/seat_translation_sturm.measure
```

All numeric state is integer and CI also runs the integer-only AST regression gate. Stable output is pipe delimited with `json=0`; wall-clock telemetry, if printed, uses integer nanoseconds and is not in pinned proof results.

The next scientific gate is to test **new** integer-coupling Sturm anchors in the interval `2<JB/JE<10000` without silently assuming the threshold or the faster runtime works. A complete full-matrix result is only certified when all four sector eliminations succeed and their summed inertia is correct. Do not mark new adaptive cells PASS until this is done.

**Limits:** Fixed finite S₃, periodic 2×2 spatial torus, no SU(N) continuum, large-volume family, uniform physical mass gap or Clay Millennium proof. Keep draft pending non-author mathematical review.

## Four new integer-sector pilot anchors: sharper cells now reach r=3

The direct-sum integer Sturm verifier has additionally been run on four new integer triples `(JE,JB,T)`: `(1,2,18250)`, `(2,5,34400)`, `(2,5,39400)`, `(1,3,19300)`. All four sectors completed at each threshold with no ambiguous pivots, yielding exactly **one negative eigenvalue** per full direct sum. The canonical deterministic results are in `seat_translation_pilot.measure`, separate from the four original controls.

Because one eigenvalue below `T/1000` means `E0<T/1000<E1`, exact integer cross-products yield continuous normalized cell bounds:

- `2 <= r <= 5/2`: `18250*2-34400=2100>0`, so `gap(E+rM)>2100/2000=21/20`.
- `5/2 <= r <= 3`: `39400-19300*2=800>0`, so `gap(E+rM)>800/2000=2/5`.

These are two further rigorous *whole-interval* results, not point samples, and require no floating-point eigenvalues or fractional runtime state. Together with the six PR #13 cells, the sharper cell coverage extends over `0<=r<=3` in this fixed finite S₃ model. **`3<r<10000` remains without sharp new cells**. PR #12's extremely weak but positive analytic bound still covers it, and PR #11's rigorous quadratic magnetic-end inequality applies at `r>=10000`.

The SHA check authenticates sector matrix bytes against a fixed trusted pin and detects tampering in CI. It cannot predict an uncomputed spectral answer. A future HBP/HBI/SG-RAM cache must retain the trusted original input hash, exact parameters, verifier version and original observed receipt; this PR does not silently implement an unsigned shared cache.
