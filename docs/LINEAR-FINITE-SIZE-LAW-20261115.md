# A linear finite-size law for the gap above the eight flat states

Seat ACER-CLAUDE-FABLE52, November 15, 2026, at the operator's direction ("do the linear finite-size law next"). Status: **DERIVED here, with every inequality checked in exact
rationals by [`linear_finite_size_law.py`](linear_finite_size_law.py); a draft for refutation.** It rests on the two-number bound of
[`VECTOR-BOUND.md`](../native/ym/results/3x4_stream/perron/vector/VECTOR-BOUND.md) and `product_bound.py`, which a second seat and GPT-6 have read. Each statement is about one finite
torus; uniformity in size stays with the stability route.

## Statement

On the periodic L × L lattice of the S₃ model, H = J_E (E + r M), for every **L ≥ 4** and every **r ≥ 3L/2 + 6**:

    E₉ − E₈  ≥  3r − 18 − 27 (L² + 9)(L + 1) / (4 L r)  >  0      (in J_E).

So the finite-size step of the stability plan, which used r ≥ 4L² (section 6 of [`YM_TOPOLOGICAL_STABILITY_PROOF.md`](YM_TOPOLOGICAL_STABILITY_PROOF.md)), holds from a coupling that
grows linearly with the side: 12 against 64 at L = 4, 18 against 256 at L = 8, 102 against 16,384 at L = 64. As r grows at fixed L the bound tends to 3r − 18, the shape 3r of the
measured gap.

The constant 6 is what this proof gives with one fixed choice of parameters; it is not the best possible. `product_bound.py`, fitting its two numbers freely, finds a positive bound
from about 3L/2 + 1 on L = 3 to 8.

## Inputs, from the repository

With e = ε² and h = η for the vector d = ε^a η^b (a, b the numbers of plaquettes whose holonomy is a transposition, a 3-cycle), `product_bound.py` gives, for every non-flat
configuration,

    (H′d)/d = 3·nl·(1 − e) + a·A + b·B + x·D_TT + y·D_TC + z·D_CC,      nl = 2L²,

where x, y, z count the links between two T plaquettes, a T and a C, two C, and

    A = 2r − 4 − 8h + 12e,      B = 3r − 12e/h + 12e,
    D_TT = 2 − 3e + 4h − (1 + 2h²)/e   (for 0 < h < 1; at the lump (2, 0) the value D_TT′ = 2 − 3e + 4h − (2h + h²)/e applies),
    D_TC = −1 − 1/h + 2h + 3e (1/h − 1),      D_CC = −3e (1/h − 1)².

The constraints used below: a is even; x ≤ adj(a) = 2a − min(⌈2√a⌉, L, ⌈2√(P − a)⌉) for 0 < a < P = L², and adj(P) = 2P; y + 2z ≤ 4b; x, y, z ≥ 0.
Then E₉ ≥ λ₁(H′) ≥ min (H′d)/d and E₈ ≤ 3·nl, so E₉ − E₈ ≥ min over non-flat lumps of [a·A + b·B + x·D_TT + y·D_TC + z·D_CC] − 6L²·e.

(The two forms of the T–T weight: for h < 1 the "same" form is the smaller, since (1 + 2h²) − (2h + h²) = (1 − h)² ≥ 0.)

## Proof

Fix h = 1/4, s = 1 + 2h² = 9/8, c = s (1 + 1/L), e = c/r. For L ≥ 4 and r ≥ 12: 0 < e < 1/3, and D_TT, D_TC, D_CC are all ≤ 0 (D_TT = 3 − 3e − rL/(L + 1) < 0; D_TC = −9/2 + 9e < 0;
D_CC = −27e < 0).

**Step 1, the C side.** With y, z ≥ 0 and y + 2z ≤ 4b: y·D_TC + z·D_CC ≥ 4b·min(D_TC, D_CC/2). Put K_C = B + 4·min(D_TC, D_CC/2). Both candidates are ≤ 0, so
K_C ≥ B + 4 D_TC + 2 D_CC = 3r − 18 − 54e.

**Step 2, the T side.** With 0 ≤ x ≤ adj(a) and D_TT ≤ 0: x·D_TT ≥ adj(a)·D_TT. Put K_T = A + 2 D_TT = 2r/(L + 1) + 6e > 0 and μ(a) = 2a − adj(a) ≥ 0. Then
a·A + adj(a)·D_TT = a·K_T + μ(a)·|D_TT|.

So every non-flat lump has excess at least a·K_T + μ(a)·|D_TT| + b·K_C (with D_TT′ in place of D_TT at the lump (2, 0)). By cases:

- **a = 0:** b ≥ 1, excess ≥ K_C.
- **a = 2, b = 0:** adj(2) = 1 for L ≥ 3, excess ≥ 2A + min(0, D_TT′) ≥ 7r/2 − 9, since (2h + h²)/e = (9/16)·r/c ≤ r/2.
- **a = 2, b ≥ 1:** 2A + D_TT ≥ 3r − 9 > 0, so excess ≥ K_C.
- **4 ≤ a ≤ P − 4:** μ(a) ≥ min(4, L) = 4, excess ≥ 4|D_TT| = 4 (rL/(L + 1) − 3 + 3e) ≥ 3.2r − 12.
- **a > P − 4:** excess ≥ a·K_T ≥ (L² − 3)·2r/(L + 1) ≥ 3r, since 2L² − 3L − 9 ≥ 0 for L ≥ 3.

Each of 7r/2 − 9, 3.2r − 12 and 3r is at least 3r − 18. Hence min excess ≥ 3r − 18 − 54e, and

    E₉ − E₈ ≥ 3r − 18 − (54 + 6L²)·e = 3r − 18 − 27 (L² + 9)(L + 1)/(4 L r).

**Step 3, positivity.** The right side is positive when r² − 6r > (9/4)(L² + L + 9 + 9/L), that is r − 3 > √(9 + (9/4)(L² + L + 9 + 9/L)). For L ≥ 4,
(3L/2 + 3)² ≥ 9 + (9/4)(L² + L + 9 + 9/L), because that reduces to L² − 3L − 3 ≥ 0. So r ≥ 3L/2 + 6 suffices. ∎

## Checked by the program

`python -I docs/linear_finite_size_law.py 7 200`, exact rationals, rows in [`LINEAR-LAW-20261115.hbp`](LINEAR-LAW-20261115.hbp):

- On L = 4 to 7, at seven couplings each from the threshold upward, the **exact** minimum of the two-number bound over every lump and every vertex of its polytope (the machinery of
  `product_bound.py`, copied unchanged) is at least the closed form of the proof, which is at least the simple form of the statement, which is positive. Example, L = 4 at r = 12:
  exact 20.531250, closed form 6.750000, statement 0.421875.
- On every L from 4 to 200, at six couplings each from the threshold to 1000 L, the sign conditions, K_T > 0, statement ≤ closed form and statement > 0 hold: 1,182 points, 0 failures.

The exact minimum sits well above the closed form (its tight lump is (0, 1), one 3-cycle), so the constant 6 has room: Step 1 charges four T–C links to every C plaquette, and one
3-cycle alone has none.

## Scope and what stays open

- Square tori with L ≥ 4. L = 3 and rectangles need their own case list (the adjacency cap uses the shorter side).
- The statement inherits the scope of the two-number bound: the pattern table, the three constraints and the chain E₉ ≥ λ₁(H′) ≥ min ratio, E₈ ≤ 3·nl of `VECTOR-BOUND.md`.
- It is a finite-size law: the threshold grows with L. A threshold independent of L is the stability theorem's claim, whose constant r₀ is not available as a number
  ([`STABILITY-ROUTE-CHECKS-20261115.md`](STABILITY-ROUTE-CHECKS-20261115.md)).
- A reader on another model, and a proof in a proof assistant, are open.
