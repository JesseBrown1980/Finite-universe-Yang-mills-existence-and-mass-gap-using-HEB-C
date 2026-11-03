# Other-seat full finite-S₃ Sturm inertia certificate

**Result:** Direct integer-arithmetic Sturm/LDL elimination now certifies all 1,393 pivot signs at both Stage 2H thresholds. This audit shares the finite Hamiltonian definition with PR #4 but does **not** call, copy, or use its positive rank-one Cholesky factor, witness vector, or inertia method.

**Source base:** PR #7's independent permutation-group finite-operator reconstruction; PR #8's exact weighted-symmetric matrix exchange. This PR is stacked on PR #8. No native code changed.

## Exact theorem and matrix

Write `W=diag(w_i)` for the strictly positive integer Gauss orbit weights, and `H=J_E E+J_B M` for the real self-adjoint finite `S₃` Hamiltonian. Given integer threshold numerator `T` (denominator `1000`), form the symmetric **integer** matrix

`B = W (1000 H - T I)`.

The independent exporter reconstructs `W`, `E`, `M` and checks `W E = E^T W`; its complete serialized operator SHA-256 agrees with the native operator, `b6c608f50f81f3bf48fb0203b48e0e3bfc867037dc1d0a96633aa80b962137f3`.

Let `K=W^(1/2) (1000 H-T I) W^(-1/2)`. It is symmetric and similar to `1000H-TI`, so their eigenvalues and inertia agree. Since `B=W^(1/2) K W^(1/2)`, Sylvester's law of inertia gives `inertia(B)=inertia(1000H-TI)`.

For any symmetric permutation of the remaining variables and nonzero scalar Schur pivot `d`, the standard congruence identity

`inertia(A) = inertia(d) + inertia(A_rest - a a^T/d)`

holds. The verifier selects a minimum-degree variable whose complete pivot interval excludes zero, then Schur-eliminates it. This permutation is **congruent**, so reordering does not change the eigenvalue sign counts. A sequence of 1,393 sign-certified pivots proves full inertia without computing the eigenvalues.

## Rigorous directed-arithmetic verification

`independent/seat_sturm_biginterval.cpp` uses GMP arbitrary-precision **integers only**, storing each real symmetric Schur coefficient as an enclosing interval of scaled integers, with `S=10^100`. Initial integer entries are represented exactly by `[B_ij S,B_ij S]`.

For an interval numerator product `x*y` and pivot `d` bounded away from zero, all four endpoint products are considered, negative denominators are sign-normalized, and `mpz_fdiv_q` / `mpz_cdiv_q` round the extremal quotient outward. Schur subtraction uses `[A_lo - q_hi, A_hi - q_lo]`. By induction, the exact scaled Schur entry always remains inside the stored interval. Therefore the sign of each pivot is mathematically certified when its interval does not include zero.

The tool checks positive/negative-denominator quotient enclosures exhaustively over small integer intervals. There are no IEEE floating-point arithmetic operations and no fixed-width integer overflow for the matrix arithmetic. It fails closed if it cannot select a pivot with a sign-definite interval, instead of guessing a sign. In these two runs, every one of the 1,393 pivots has a sign-definite interval; no 2×2 pivot was required. The source uses no JSON and all final results carry `json=0`.

This is a **full direct Sturm inertia certificate**, but technically it is **arbitrary-precision outward-rounded interval arithmetic**, NOT exact-rational Bareiss elimination. A separate exploratory `seat_sturm_exact_gmp.cpp` performs exact GMP rational LDL with a 2×2 fallback, but the dense rational calculation was too expensive to finish in the initial audit. No claim is made that its full run succeeded.

## Results

| Coupling | Threshold `T/1000` | Negative pivots | Positive pivots | Sign-ambiguous pivots | Full inertia |
|---|---:|---:|---:|---:|---|
| `JE=1,JB=1` | `13.240` | **1** | **1392** | **0** | certified |
| `JE=3,JB=5` | `50.840` | **1** | **1392** | **0** | certified |

The locally executed verifier completed in ~41 seconds per coupling on the audit host. The source, pinned result, and dedicated CI establish rerunnable provenance; the local timing itself is not a universal benchmark.

An exact ground-state enclosure from PR #7's independently reconstructed operator gave

- `E0(1,1) <= 7.634199 < 13.240`
- `E0(3,5) <= 36.699228 < 50.840`.

Because `B` has exactly one negative eigenvalue and zero zero eigenvalues, precisely **one** eigenvalue of `H` lies below each threshold. Therefore

- `E1(1,1) > 13.240`, so `E1-E0 > 5.605801` finite model units.
- `E1(3,5) > 50.840`, so `E1-E0 > 14.140772` finite model units.

This independently verifies **the strong Stage 2H lower bounds**. It does **not** independently check the more refined Stage 2H/Ritz `E1` upper bound, the exact excitation-sector label, continuum behavior, or a theorem for arbitrary couplings.

## Reproduction

```bash
python3 independent/seat_sturm_integer_matrix.py > /tmp/seat_s3_1393.txt
g++ -O3 -std=c++17 -Wall -Wextra -Werror \
  independent/seat_sturm_biginterval.cpp -lgmpxx -lgmp -o /tmp/seat_s3_big
/tmp/seat_s3_big --selftest

{
  /tmp/seat_s3_big /tmp/seat_s3_1393.txt 1 1 13240
  /tmp/seat_s3_big /tmp/seat_s3_1393.txt 3 5 50840
} | grep '^HEBC-STURM-BIG|result=PASS' > /tmp/seat_s3_full.measure

cmp independent/seat_sturm_full_inertia.measure /tmp/seat_s3_full.measure
```

## Cross-check and scientific limits

The input is the finite **2D spatial, 2×2 periodic, S₃ lattice operator**, not a continuum `SU(N)` Hamiltonian. Two distinct code paths reconstruct it: Rust native and the PR #7 independent permutation-group program. The full direct Sturm run constitutes a different spectral **certificate method** than Stage 2H's rank-one positive-definiteness test.

Independent mathematical review of the arithmetic implementation and a second host reproduction remain separate quality gates. Matching SHA receipts authenticate integrity only relative to a trusted pin; they do not independently establish who ran the computation.

**No claim** of a uniform gap over all lattice volumes, continuous groups, continuum four-dimensional quantum Yang–Mills, confinement, string tension, or the Clay Millennium problem follows from these results. Keep the pull request draft until review.
