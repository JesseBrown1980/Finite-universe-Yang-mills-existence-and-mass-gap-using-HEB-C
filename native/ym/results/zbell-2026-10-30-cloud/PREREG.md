# zbell, cloud seat: Bell/CHSH test of the z layer. Pre-registration (frozen before any code)

Independent of acer. Integer only (every correlation kept as a count over n trials), json=0,
Rust 1.81, no dependencies except sha2 =0.10.8.

## Setup
Two sides, A and B, each with a setting a, b in {0,1} and an outcome in {+1,-1}.
n = 486 shared values lambda = 0..485 (2 x 3^5), the same list for every setting pair.
E(a,b)*n = sum over lambda of A*B.  S*n = E(0,0)n + E(0,1)n + E(1,0)n - E(1,1)n.
Local bound: |S| <= 2, i.e. |S*n| <= 2n = 972. Quantum (Tsirelson) bound: S^2 <= 8, i.e. (S*n)^2 <= 8n^2.
No-signalling: the count of A = +1 depends only on a, never on b; the count of B = +1 only on b.

## Models
- L-det: every deterministic local strategy (A0, A1, B0, B1 in {+1,-1}), 16 of them.
- L-hash: A = sign from bit 0 of sha256("A"|a|lambda), B from sha256("B"|b|lambda). Each side reads
  only its own setting and the shared lambda: the hash selection of earlier tests, made local.
- Z-PR: z sees both settings (the destination pull). A = (-1)^(lambda mod 2); B = A * (-1)^(a*b).
- Z-T: z sees both settings, tuned under the quantum bound. A = (-1)^(lambda mod 2); B = A, except
  that for (a,b) = (1,1) B = -A everywhere, and for the other three pairs B = -A on lambda < 72
  (flipped in even/odd pairs, so marginals stay balanced). E*n = 342 for three pairs, -342 for (1,1).
- Leak (negative control): as Z-PR, but A also reads b: A = (-1)^(lambda mod 2) if b = 0, A = +1 if b = 1.

## Predictions (exact integer equality)
- P1 L-det: all 16 strategies give |S| = 2 exactly; none exceeds 2.
- P2 L-hash: |S*n| <= 972, and no-signalling holds exactly.
- P3 Z-PR: S*n = 1944 (S = 4, the maximum), and no-signalling holds exactly: A = +1 on 243 of 486
  for every (a,b), and the same for B.
- P4 Z-T: S*n = 1368, above the local 972 and within the quantum bound (1368^2 = 1,871,424 <=
  8 * 486^2 = 1,889,568); no-signalling holds exactly.
- P5 Leak: the count of A = +1 differs between b = 0 and b = 1 (243 against 486), so a reader of
  A alone learns b instantly: the signalling a readable z would give.
Any build failure, missing line or unequal value is FAIL or INCONCLUSIVE, never PASS.
