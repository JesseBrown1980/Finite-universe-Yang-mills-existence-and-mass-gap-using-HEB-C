# Integer Sturm ladder: matrix jumps and timing tricks

How the finite S₃ 2×2-torus gap is being certified across the coupling ratio
r = JB/JE, using exact relations to avoid recomputation and a SHA-keyed
certificate ledger so nothing is computed twice. Integer arithmetic only;
every output line ends `json=0`.

## What one certificate is

For H = JE·E + JB·M on the 1,393 gauge-orbit states, the verifier builds the
integer matrix B = W(1000·JE·E + 1000·JB·M − t·W) and runs interval
LDLᵀ/Sturm elimination, using a pivot only when its interval excludes zero and
rounding every Schur update outward. The count of negative pivots is the number
of eigenvalues of H below t/1000.

- count = 1 ⇒ E₀ < t < E₁
- count ≥ 1 ⇒ E₀ < t
- a threshold exactly on an eigenvalue makes a pivot interval contain zero; the
  verifier **fails closed** and gives no count (seen at r = 0, t = 6.000 = E₁)

## The matrix jumps: exact relations that replace computation

| trick | what it gives for free | status |
|---|---|---|
| **Scaling** | count at (k·JE, k·JB, k·t) = count at (JE, JB, t) for any integer k > 0 | exact; one certificate covers a whole ray |
| **Monotone cells** | M ⪰ 0, so every eigenvalue of E + r·M is non-decreasing in r; on [a, b], gap/JE ≥ E₁(a) − E₀(b) | exact lemma; turns two endpoint certificates into a continuous interval |
| **Translation sectors** | Z₂×Z₂ translations commute with H; the matrix splits exactly into four integer blocks (385, 336, 336, 336); counts add | PR #14; this verifier cross-checked it on the full matrix at 6 anchors |
| **Predict-then-verify** | the next ratio and thresholds are predicted from certified data plus PR #11's exact second-order law (integer square roots); one certificate confirms or refutes | prediction is never recorded as a result |
| **SHA-keyed ledger** | each certificate is keyed by sha256(mode, matrix shas, JE, JB, t, digits); a repeat is a lookup | `ledger.hbp`; reruns resume |

What SHA does **not** do: a hash fingerprints a result once it exists. It
carries no information about an uncomputed spectrum. Measured: (1, 2, 18.250)
and (2, 4, 36.500) are the same matrix up to scale with provably equal counts,
and their hashes differ in 128 of 256 bits.

## Measured timings (2 vCPU sandbox, scale 10^digits)

| verifier | matrix | digits | ms per certificate |
|---|---|---|---|
| Python (`independent/third_seat/sturm_py.py`) | full 1,393 | 80 | 143,662 – 165,161 |
| Rust (`sturmrs`, this directory) | full 1,393 | 80 | 152,210 – 167,224 |
| Rust | full 1,393 | 30 | 78,305 |
| Rust | four sectors, summed | 30 | 6,322 – 7,516 (median 6,890) |
| PR #14 on GitHub runner | four sectors | 30 | 6,158 |

The language did not matter (Python ≈ Rust): the cost is the elimination
itself. The sector split did (about 12×).

## Cross-checks performed

- Rust on the full matrix reproduces the archived Python results exactly:
  negative = 1, 1, 0, 3 at (1,1,13.240), (3,5,50.840), (1,1,7.000), (1,1,13.300).
- Rust on the full matrix reproduces PR #14's four anchors: (1,2,18.250),
  (2,5,34.400), (2,5,39.400), (1,3,19.300), each negative = 1.
- Rust on the four sectors equals the full matrix at (1,2,18.250) → 1 and
  (1,1,13.300) → 3.
- The ladder re-certifies every 10th anchor on the full matrix and stops on any
  mismatch.

## Results so far (snapshot of `ledger.hbp`; still running)

Gap lower bounds per unit JE, each certified:

| kind | r | bound |
|---|---|---|
| rung | 0 | E₀ < 0.001, E₁ > 5.999, gap > 5.998 (exact: 0 and 6) |
| rung | 1 | E₀ < 7.750, E₁ > 13.187, gap > 5.437 |
| anchor | 3 | E₀ < 19.244, E₁ > 20.711, gap > 1.467 |
| cell | [3, 3.297] (192/64 – 211/64) | gap > 0.366 on the whole interval |
| cell | [3.297, 3.531] (211/64 – 226/64) | gap > 0.248 on the whole interval |

Rungs measured at r = 0, 1, 2, 3, 5, 6, 8, 9, 15, 21, 27, 45, 63, 81, 135,
189, 243 trace the gap profile; the cells give continuous coverage. Above
r = 10⁴ PR #11's rigorous bound (gap > JE²/JB) takes over.

`ledger_pilot_fullmatrix_bugged_jump.hbp` is kept as evidence of a fixed bug:
the first jump rule calibrated E₀'s offset to the target bound itself and
could only step 1/64.

## Reproduce

```bash
cd independent/ladder
(cd sturmrs && cargo +1.81.0 build --release)
mkdir -p work && python3 ../seat_sturm_integer_matrix.py > work/full.matrix
python3 ../seat_translation_sectors.py work/sectors
python3 ladder.py 10000 6600     # ratio end, time budget in seconds; resumes from ledger.hbp
python3 rungs.py                 # fixed rungs
```

`ladder.py` checks the full-matrix sha `137285e0…` and all four sector shas
before running.

## Scope

Finite S₃ gauge model on one 2×2 torus. No infinite-volume, continuum or Clay
Yang–Mills claim follows. Receipts are integrity, not authenticated provenance.
