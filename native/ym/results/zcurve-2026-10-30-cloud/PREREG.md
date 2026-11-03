# zcurve, cloud seat: test B, straight r versus curved j. Pre-registration (frozen before any code)

Independent of acer's test B. Integer only, json=0, Rust 1.81, no dependencies.
Same lattices as zlevel: M = 3^N cells, N in {3, 4, 5}, digit k = level k. R_k rotates digit k.

Operators at level k:  r_k = R_k + R_k^2 (straight, both ways)
                       J_k = I + R_k + R_k^2 (symmetric j, as in zlevel and PR #40)
                       j_k = I + R_k - R_k^2 (curved j: reaches all three, not symmetric)
Nested products: Jall = J_0 ... J_(N-1),  jall = j_0 ... j_(N-1).

## Predictions (exact integer equality)
- P1 symmetry: r_k^T = r_k and J_k^T = J_k; j_k^T != j_k (for every k and N).
- P2 reach: under the cascade (step s applies level s-1), j_k gives the same reach time as J_k for every
  ordered pair (a, b), so all zlevel reach results carry over unchanged.
- P3 nested product: jall has every entry in {+1, -1}, so it reaches everything in one application, and
  jall != all-ones. Count of -1 entries = (9^N - 3^N)/2: 351, 3240, 29403.
- P4 information: over GF(3), rank(Jall) = 1 and rank(jall) = M. The symmetric j keeps only the total and
  loses where things were; the curved j keeps everything (it is invertible mod 3).
  Single level: det(J) = 0 and det(j) = 4 over the integers, det(j) = 1 mod 3.
- P5 applied to each of the M single-cell states, Jall gives 1 distinct output and jall gives M distinct outputs.
Any build failure, missing line or unequal value is FAIL or INCONCLUSIVE, never PASS.
