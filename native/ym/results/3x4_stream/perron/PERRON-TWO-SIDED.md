# The Perron level from both sides, and at every coupling (draft, November 2, 2026)

**On 3×4, 94.070673 ≤ λ₁(H′) ≤ 94.070936 J_E,** a bracket 0.000263 J_E wide. One exact pass over the store bounds λ₁(H′) from above as well
as from below, and one more pass raises the side from below using vectors that are already solved. Claims are tagged MEASURED, DERIVED (a short
proof written here) or CONJECTURE. Each number below names the tool that measured it. A number here counts as certified, by the author's tools, when `perroncert check` and
`check_d_strict.py` agree on it. The independent verdict is pending until the Go checker in section 7 passes. The tool that proposes vectors, [`perronritz.rs`](../../../crates/evolvers/src/bin/perronritz.rs), measures in
one pass and stands behind those two for the side from below.

A separate seat tried to refute all of this: [`REVIEW-OPUS55.md`](REVIEW-OPUS55.md). Every printed bound it could test holds, and section 6 lists
what it found and what changed.

Notation: H′ is H with the flat rows and columns removed, R(t) = (H′ − t)⁻¹, and s is perroncert's uniform source, 10⁶·2³⁰.
perroncert solves (H′ − t) d = s, so d = R(t) s.

## 1. Where the excess comes from

**DERIVED.** At a solved vector, (H′d)_h / d_h = t + s / d_h, so the tightest row is the row with the largest d, and
t_cert − t = s / d_max. MEASURED at T = 93.95: s / 192,571,261,487 = 5,575.8, and the row reads 93,955,575.

## 2. The side from above

**DERIVED.** H′ is W-self-adjoint. For any vectors d_1 … d_k that vanish on the flat rows, let G_ab = ⟨d_a, d_b⟩_W and
A_ab = ⟨d_a, H′d_b⟩_W. By min-max, λ₁(H′) ≤ θ₁, the smallest root of det(A − θG). Every entry is an exact integer. The tool prints the
least integer θ ≥ 0 at which A − θG stops being positive definite, tested by fraction-free elimination.

A single resolvent carries a large background from the uniform source (on 3×4, d at T = 93 alone gives only 185.0). The span of a few
resolvents at different thresholds removes it.

Steps that could fail, and what tests each:

| Step | Test |
|---|---|
| H′ is W-self-adjoint | On all rows: `check_d_strict.py --self-adjoint`, a random form drawn from SHA-256. The pass also requires E_ab = E_ba exactly on its vectors, and prints how many pairs it compared. With one vector it prints `E_self_adjoint=OPEN` |
| The vectors vanish on the flat rows | The pass refuses any vector that does not |
| A sum or product leaves its range | On every path to a printed number in `pass` and `grid`, products are checked and exit 2 with no value, and JE and JB are limited to 2⁴⁰. Sums use 256 bits. Unit tests hold the second seat's three cases |
| The bisection logic | Exact on a 2×2 by hand, against separate code below, and against the second seat's exact inertia |

## 3. Free steps of inverse iteration

**DERIVED.** H′ has off-diagonals ≤ 0, so R(t) ≥ 0 entrywise for t < λ₁. The resolvent identity gives
R(t₂) − R(t₁) = (t₂ − t₁) R(t₂) R(t₁), and in general, with X_k the divided difference of the d_i over t_1 … t_k,

    X_k = Σ_i d_i / Π_{j≠i} (t_i − t_j) = R(t_1) … R(t_k) s > 0,    (H′ − t_k) X_k = X_{k−1}.

So k solved vectors give k − 1 extra steps of inverse iteration with no further solve, and the source cancels. The value of X_k is
t_k + min_h X_{k−1}(h) / X_k(h).

**It can only rise.** DERIVED. Let μ be the value of X_{k−1}, so (H′ − μ) X_{k−1} ≥ 0. Applying R(t_k) ≥ 0 gives
X_{k−1} + (t_k − μ) X_k ≥ 0, so t_k + X_{k−1}/X_k ≥ μ at every row. The proof needs only t_k < λ₁. MEASURED by the second seat in exact rationals: 57,968
steps on 1,500 random Z-matrices, every threshold order, with 0 failures of the identity, the equation, positivity, monotonicity or value ≤ level.

**Where exact arithmetic meets a real solver.** High rows carry very little of X_k, and a solver's leftover or rounding can outweigh it
there. MEASURED on 3×3, thresholds 76.2, 76.3, 76.4: the vectors alone predict 76.448118, and `perroncert check` on the pure X₃ gives
76.409643 at a row with M = 20. So the proposal is x = X_k + γ d_k. At a row the ratio is (A + γB) / (X + γd), so one read of the row
gives every γ, and `perronritz grid` measures the exact value for a whole grid of γ in one pass. Any positive x is admissible, so a poor
proposal can only give a weaker number.

## 4. Every coupling

**DERIVED.** H′(r) = E′ + r M on the same rows, so for one vector the ratio at a row is e_h + r M_h. The pass keeps
e_M = min_{M_h = M} e_h for each magnetic number, and the side from below at any r is min_M (e_M + r M). On 3×4 that is 32 numbers: M runs from 3 to
36 without 5 and 35. For a fixed d it can only rise with r, because M ≥ 0. With M ≥ 3 on non-flat rows and E₈ ≤ 3·nl for every r, one vector solved at
coupling r₀ gives, by the argument of [`PERRON-BOUND.md`](PERRON-BOUND.md) section 2,

    E₉(r) − E₈(r)  ≥  t_cert(r₀) − 3·nl + 3(r − r₀)    for every r ≥ r₀.

The coupling enters only on the diagonal, so the lift holds at every r₀. MEASURED by the second seat with its own whole-space builds: whole-space and
sector ratios are exactly equal at every orbit, at 84 (r₀, r) pairs on 2×2 and 54 on 2×3.

**How far the flat bound reaches.** This route ends where λ₁(H′) meets 3·nl. On 3×3, the second seat's exact brackets give λ₁ in
[53.689314, 53.689315] at r = 4, below 54, and [54.114091, 54.114092] at r = 4.06. So it ends between r = 4 and r = 4.06 there. Below that, a sharper
upper bound on E₈ than the flat one is needed.

## 5. Measured

### Against separate code

`shellschur` brackets λ₁(H′) with separate code, and the second seat's exact checks close in further. Rows: [`TWO-SIDED-SMALL.hbp`](TWO-SIDED-SMALL.hbp), and
[`REVIEW-OPUS55.md`](REVIEW-OPUS55.md) for the last column.

| Lattice | `shellschur` bracket | From below, `grid` and `perroncert check` | From above, `pass` | Second seat, exact |
|---|---|---|---|---|
| 2×2 | [46.466796, 46.468750] | 46.466823 | 46.467674 | ceil(λ₁) = 46.467674, by exact inertia of W(H′ − θ) |
| 2×3 | [58.441406, 58.443359] | 58.441733 | 58.443134 | λ₁ in [58.443132, 58.443133] |
| 3×3 | | 76.448116 | 76.448399 | λ₁ in [76.448397, 76.448398] |

### 3×3

Each row of this table is one `grid` pass, with `perroncert check` giving the same value on the written vector.

| Vectors | γ | `t_cert` (J_E) | Tightest M |
|---|---|---|---|
| X₃ on 74, 75, 76 | 0 | 76.408740 | 3 |
| X₂ on 76.2, 76.4 | 0 | 76.445360 | 3 |
| X₃ on 75, 76.2, 76.4 | 0 | 76.447078 | 3 |
| X₃ on 76, 76.2, 76.4 | 211 | 76.447590 | 3 |
| X₄ on 75, 76, 76.2, 76.4 | 316 | 76.447681 | 4 |
| X₅ on 74, 75, 76, 76.2, 76.4 | 316 | 76.447690 | 7 |
| X₃ on 76.2, 76.3, 76.4 | 2 | **76.448116** | 3 |

For comparison, the warm start at T = 76.43 reads 76.431504. `check_d_strict.py` gives the same 76448116 on the best vector here. From above: λ₁(H′) ≤ 76.448399,
stable to 3 × 10⁻⁶ across pairs and the triple. The second seat's own vector, from a Chebyshev filter of 800 products, reads **76.448397** through the pinned `perroncert check`.

At other couplings, `perroncert check` at JB = 6000 and 4000, on two vectors, prints the value, row and M of the pass's table. The second seat compared values at 544 (JB, vector)
pairs with 0 mismatches, and a crafted tie showed row and M can differ at equal value. The final tool now reports the lowest row at a tie, as `perroncert check` does.

Solving at a lower coupling, from d = 0: E₉(6) ≥ 64.504251 and E₉(5) ≥ 59.028025. The second seat's vector at r = 4.06 reads 54.114091 through the pinned `perroncert check`, so on 3×3,

    E₉ − E₈ ≥ 0.114091 + 3(r − 4.06) J_E    for every r ≥ 4.06, subject to the lift.

### 3×4

Rows: [`TWO-SIDED-3x4.hbp`](TWO-SIDED-3x4.hbp), with the predictions written before each pass and how each came out. Every row below has merkle PASS and the tightest row at M = 3.

| Vector | `t_cert` (J_E) | Tightest row | Measured by |
|---|---|---|---|
| T = 93, 12 passes | 93.061051 | 44,742,735 | `perroncert check`, `check_d_stream.py`, and `check_d_strict.py` on another machine |
| T = 93.7, 5 passes | 93.718415 | 44,742,735 | `perronritz pass` |
| T = 93.95, 3 passes | 93.955575 | 44,742,735 | `perronritz pass` |
| X₂ on 93, 93.7, plus γ d | 94.002305 | 44,742,735 | `perronritz pass` |
| T = 94.058, 9 passes, hosted climb, [run 41448187715](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41448187715) | 94.058570 | 44,742,735 | `perroncert check` and `check_d_strict.py` on that runner |
| X₃ on 93, 93.7, 93.95, γ = 316 | 94.064904 | 44,742,735 | `perronritz grid` |
| X₃ on 93, 93.7, 93.95 converged, γ = 0 | 94.065384 | 44,742,735 | `perronritz grid`, `perroncert check`, `check_d_strict.py` |
| X₃ on 93.7, 93.95 converged, 94.058, γ = 2 | **94.070673** | 45,507,968 | `perronritz grid`, `perroncert check`, `check_d_strict.py` |

The hosted climb reached 94.058570 at 12,110 s. The divided difference of its T = 94.058 vector with two lower ones took one more pass.

From above, by `perronritz pass`: **λ₁(H′) ≤ 94.070936 J_E** on the T = 93.7, 93.95 and 94.058 vectors, and 94.070937 on the top vector alone. The first pass, on lower vectors, gave 94.071171, and the second seat's
store-free pass gave 94.071173. The level fits of the climb read 94.0654, 94.0703, 94.0709 on the way up. The span of all four vectors of the last pass prints `OPEN`, because the top vector is an exact combination of the other three.

**Correction beside the earlier text.** This doc and the second seat both held λ₁(H′) ≈ 94.0711 as a CONJECTURE, from the first pass. The last pass excludes that value: the level lies below 94.070936.

The gap above the eight flat states, by section 2 of `PERRON-BOUND.md`, subject to the open items in section 7:

    E₉ − E₈ ≥ 22.070673 + 3(r − 9) J_E for every r ≥ 9,    E₉ − E₈ ≥ 24.039673 J_E at r = 9.

**The same vectors on two machines.** MEASURED. Local Windows and hosted Linux, each with its own build of the solver, gave the same SHA-256 on the T = 93.95 vectors: `635e7273…` after 3 passes and
`cf273fbf…` after 6. At T = 94.03 they read the same 94.031828 with different hashes, because `perron_climb.py` keeps its best vector only on a strict rise, so the hosted stage started from `635e7273…`
and the local restart from `cf273fbf…`.

**At lower couplings,** from the T = 93 vector alone, with no new solve, by the coupling table of the first pass:

| r | 12 | 9 | 8 | 7 | 6.5 | 6 |
|---|---|---|---|---|---|---|
| E₉(r) ≥ (J_E) | 102.061051 | 93.061051 | 87.122453 | 79.745170 | 75.745170 | 71.321650 |

`perroncert check` at JB = 7000 on that vector prints 79745170, row 44,743,136, M = 8, as predicted in writing beforehand. The table passes the flat bound of 72 at r = 6.076 (exactly 1093567/180000 = 6.075372 by
the second seat), so E₉ − E₈ > 0 for every r ≥ 6.076 on 3×4, subject to the same items. A solve at a lower coupling is open.

### Which tool made which row

| Tool | SHA-256 | Source | Rows |
|---|---|---|---|
| `perronritz.exe` | `cdddf4f2…` | [`perronritz-pass1.rs.at-pin`](perronritz-pass1.rs.at-pin) | The first pass on 3×4, and x on 93, 93.7 through its `jump` mode |
| `perronritz-grid.exe` | `42b31b05…` | [`perronritz-grid.rs.at-pin`](perronritz-grid.rs.at-pin) | Grids 1 and 2 on 3×4 |
| `perronritz-final.exe` | `e166b468…` | [`perronritz.rs`](../../../crates/evolvers/src/bin/perronritz.rs) | Grid 3 and the last pass on 3×4, and [`TWO-SIDED-SMALL.hbp`](TWO-SIDED-SMALL.hbp) |

The final tool reproduces all 50 lower-side and upper-side rows of the earlier small receipts, [`TWO-SIDED-SMALL-rev1.hbp`](TWO-SIDED-SMALL-rev1.hbp). The second seat matched the earlier two on 215 fuzz cases and 13 small passes.

## 6. What the second seat found

All of it is in [`REVIEW-OPUS55.md`](REVIEW-OPUS55.md), with its scripts in [`second-seat/`](second-seat/). It refuted no printed bound.

| Finding | Status |
|---|---|
| D1. This doc attributed every value to the exact check, while some rows came from `perronritz` alone | Fixed: each row now names its tool |
| D2. Links to receipts that had not been added | Fixed by this commit |
| D3. `E_self_adjoint=PASS` printed with no comparison on one vector, and two vectors built proportional at a bad pair pass too | Fixed: `OPEN` with `E_pairs_compared=0`. The all-rows form carries this weight, as section 2 now says |
| D4. Overflow at absurd inputs: JB near 2¹²⁸, JE = 10³², or a crafted store printed a wrong value and exit 0 | Fixed in `perronritz`. `perroncert` stays pinned and shares this at those inputs, so hardening it is open. `check_d_strict.py` uses Python integers and refuses the crafted store. DERIVED by the second seat: at JE = 1000 and modest JB, rows with `check_d_strict.py`'s structure keep every term under 2¹¹⁶ for any i64 vector |
| D5. This doc said a symmetry break would leave the side from below untouched | Corrected: the step to E₉ is interlacing, which needs the same symmetry, so both sides rest on the all-rows form |
| D6. Row and M can differ from `perroncert check` at a tie, with equal value | Fixed: the lowest row wins, as there |
| D7. The printed value is 0 when θ₁ < 0, on negative-diagonal stores only | Sound, since 0 ≥ θ₁. Section 2 now says θ ≥ 0 |
| D8. Claims without rows: seven vectors, a timing, the pure γ = 0 failure, a one-vector label match, and which source made which row | Fixed: all in the rows now, the timing is dropped, and the table above names the sources |

Its first objections as a hostile reader stand as open items: the upper side bounds λ₁(H′) and E₉ has a lower bound only, and on 3×4 the rows are matched to H on samples plus all-rows structure checks.

## 7. Open

| Item | Run that measures it |
|---|---|
| The independent verdict: a checker written by someone else, on these vectors | Pending until it passes. The outside seat's Go checker, [`independent-go-perron-20261102.yml`](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/blob/audit/independent-go-perron-20261102/.github/workflows/independent-go-perron-20261102.yml) on its branch. Its first runs stopped after the row loop on the format text this seat gave it, corrected in `PERRON-REVIEW.md`. Its row conditions passed on all rows. Its diagnostic run [41499253445](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41499253445) printed `trailing=742160 nonzero=0 merkle_matches=true`, as predicted in writing beforehand. A later build, with the corrected format and all three vectors, is running: [run 41509351749](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41509351749). Its certificate values are open |
| Every 3×4 row against the definition of H | Running at the operator's word: `second-seat/fullrebuild.rs` recomputes each row from the rules, S₃ from permutations, the lattice, the gauge fixing, the canonical key, weight, M and every move, and compares it with the store. Prediction, written first in [`FULLREBUILD-RUN.hbp`](FULLREBUILD-RUN.hbp): 45,508,080 rows, 0 mismatches, and any mismatch falsifies store = H. It matches all rows on 2×2, 2×3 and 3×3. With a store's merkle repaired after one changed entry, M or weight, it reports exactly that mismatch and exits 2, on 4 of 4 controls: [`FULLREBUILD-CONTROLS.hbp`](FULLREBUILD-CONTROLS.hbp). The key list comes from `passA.bin` and is verified: each key must recompute as canonical, keys ascend strictly, a move outside the list counts as a mismatch, and the recomputed weights must equal the store's, which `check_d_strict.py` ties to `passA.bin`, whose weights sum to exactly 6¹³ |
| The gap below r = 6.076 on 3×4 | A solve at lower coupling, then the same checks. On 3×3 the flat bound's route ends between r = 4 and 4.06 |
| `perroncert` guards at absurd inputs | A hardened build with checked products, once the pinned runs are done |
| A verdict by this route | A rule revision and the operator's word: [`PERRON-RULE-DRAFT.md`](PERRON-RULE-DRAFT.md) |
