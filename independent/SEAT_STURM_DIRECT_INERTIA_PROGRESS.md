# Direct integer Sturm inertia: independently reconstructed finite S₃ torus

**STATUS: PARTIAL CERTIFICATE ONLY.** The full 1,393-pivot inertia and Stage 2H strong E₁ threshold remain **UNCERTIFIED by this auditor**.

This is a separate mathematical verification route on top of [the independent finite-operator reconstruction](seat_yang_mills_audit.py), not a repeat of `torus2_inertia.rs` or `torus2_independent.rs`. Nothing here modifies the native Hamiltonian or its Rust proof claims.

## Matrix and theorem

For each coupling, reconstruct exactly the 1,393 × 1,393 `W`-symmetric integer matrix

`B = W · (1000 · H(JE,JB) - t_num · I)`

using the source model's orbit weights `W`, electric sparse operator, and diagonal magnetic action. The inertia of `B` equals that of `H - (t_num/1000) I` because `W` is positive diagonal and `H` is self-adjoint in the `W`-weighted inner product. Equivalently, the symmetric matrix `W^(1/2)(H - tI)W^(-1/2)` is congruent to `B`.

A symmetric no-pivot Schur/LDL elimination has congruence-preserving pivots. **If all 1,393 pivot signs were proved nonzero, counting negative pivots would establish the full negative inertia**, a completely different positive-definiteness check from adding the Stage 2H rank-one Cholesky term.

This auditor does **not** complete all 1,393 pivots. It certifies a strict prefix of the successive Schur signs, and therefore the inertia of the corresponding **leading principal submatrix only**. This is *not* sufficient to conclude that the full model has exactly one eigenvalue below the threshold.

## Exact arithmetic methodology

`seat_sturm_integer_matrix.py` regenerates the matrix from the independently implemented S₃ permutation/orbit constructor in PR #7, checks weighted symmetry, and writes a simple **non-JSON integer exchange file**.

`seat_sturm_prefix.cpp` uses only signed 128-bit integer arithmetic; it does not compute or compare floating-point eigenvalues. Each Schur entry is enclosed in an integer interval at scale `10^12`. For a nonzero pivot interval `d` and known offdiagonal intervals `x,y`, it encloses `x*y/d` by testing the corner products and outward integer floor/ceiling divisions, then subtracts intervals with outward bounds. It refuses a pivot if its interval includes zero, and never guesses the sign. Unit tests exhaustively exercise small interval numerator/denominator combinations. The workflow compiles with signed-overflow sanitization.

Each of the accepted prefix intervals encloses its exact mathematical Schur complement by induction, assuming checked arithmetic does not overflow. This is why CI deliberately uses `-fsanitize=undefined -fno-sanitize-recover=undefined` and records the checked full calculation.

## Reproduced outcomes

| Couplings (JE,JB) | Threshold `t_num/1000` | Prefix checked / 1393 | Negative pivots in prefix | Inference |
|---|---|---:|---:|---|
| 1,1 | 13.240 | 1,100 | 1 | Exact inertia for 1,100 × 1,100 leading principal block |
| 3,5 | 50.840 | 1,300 | 1 | Exact inertia for 1,300 × 1,300 leading principal block |

**Full certificate deliberately fails closed at current precision**: the first pivot interval containing zero occurs at row 1,120 for (1,1), and row 1,326 for (3,5), using zero-based row indices. These failures mean **interval overestimation**, not a discovered zero eigenvalue or counterexample. The remaining pivot signs, including full-matrix negative inertia, are **unknown** from this calculation. Do not infer the Stage 2H claimed strict `E1` thresholds from this evidence.

For completeness, an exploratory floating-point direct LDL diagnostic did produce one negative eigen-direction at each threshold; this is *not part of the proof or the committed measure*, and is not an acceptance gate.

## Execute

```bash
python3 independent/seat_sturm_integer_matrix.py > /tmp/seat_sturm_matrix.txt
g++ -O2 -std=c++17 -Wall -Wextra -Werror \
  -fsanitize=undefined -fno-sanitize-recover=undefined \
  independent/seat_sturm_prefix.cpp -o /tmp/seat_sturm_prefix
/tmp/seat_sturm_prefix --selftest
{
  /tmp/seat_sturm_prefix /tmp/seat_sturm_matrix.txt 1 1 13240 1100
  /tmp/seat_sturm_prefix /tmp/seat_sturm_matrix.txt 3 5 50840 1300
} > /tmp/seat_sturm_prefix.measure
cmp /tmp/seat_sturm_prefix.measure independent/seat_sturm_prefix.measure
```

## Next proof gate

A higher-precision fraction-free or rigorously verified LDL/Sturm method that certifies **all 1,393 pivot signs** at both thresholds is still required. Any new verifier must be checked from a fresh read of the operator, include sign/overflow controls, and run without changing PR #4/#5/#6. Once full inertia is independently proved, combine it with the separately established `E0 < t` to derive `E1 > t`.

No uniform infinite-volume gap, continuum four-dimensional Yang–Mills theorem, confinement, string tension, or independent physical attestation follows from these finite computations.
