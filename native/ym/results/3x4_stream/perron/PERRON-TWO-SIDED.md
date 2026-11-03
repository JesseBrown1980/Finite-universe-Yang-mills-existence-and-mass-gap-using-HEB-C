# The Perron level from both sides, and at every coupling (draft, November 2, 2026)

**On 3×4, 94.070673 ≤ λ₁(H′) ≤ 94.070936 J_E,** a bracket 0.000263 J_E wide. One exact pass over the store bounds λ₁(H′) from above as well
as from below, and one more pass raises the side from below using vectors that are already solved. Claims are tagged MEASURED, DERIVED (a short
proof written here) or CONJECTURE. Each number below names the tool that measured it. A number here counts as certified, by the author's tools, when `perroncert check` and
`check_d_strict.py` agree on it. An outside seat's Go checker, written separately, prints the same values, rows and M on these vectors, as predicted in writing beforehand: section 5. A second seat's `fullrebuild` recomputed all 45,508,080 rows from the rules, with 0 mismatches: section 5. The tool that proposes vectors, [`perronritz.rs`](../../../crates/evolvers/src/bin/perronritz.rs), measures in
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
| H′ is W-self-adjoint | On every pair, exactly: `allpairs`, 1,632,625,631 off-diagonal pairs with w_h z_hj = w_j z_jh, 0 mismatches and 0 unpaired entries, in section 5. On all rows: `check_d_strict.py --self-adjoint`, a random form drawn from SHA-256. The pass also requires E_ab = E_ba exactly on its vectors, and prints how many pairs it compared. With one vector it prints `E_self_adjoint=OPEN` |
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
| T = 93, 12 passes | 93.061051 | 44,742,735 | `perroncert check`, `check_d_stream.py`, `check_d_strict.py` on another machine, and the outside seat's Go checker |
| T = 93.7, 5 passes | 93.718415 | 44,742,735 | `perronritz pass`, and the outside seat's Go checker |
| T = 93.95, 3 passes | 93.955575 | 44,742,735 | `perronritz pass` |
| X₂ on 93, 93.7, plus γ d | 94.002305 | 44,742,735 | `perronritz pass` |
| T = 94.058, 9 passes, hosted climb, [run 41448187715](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41448187715) | 94.058570 | 44,742,735 | `perroncert check` and `check_d_strict.py` on that runner |
| X₃ on 93, 93.7, 93.95, γ = 316 | 94.064904 | 44,742,735 | `perronritz grid` |
| X₃ on 93, 93.7, 93.95 converged, γ = 0 | 94.065384 | 44,742,735 | `perronritz grid`, `perroncert check`, `check_d_strict.py`, and the outside seat's Go checker |
| X₃ on 93.7, 93.95 converged, 94.058, γ = 2 | **94.070673** | 45,507,968 | `perronritz grid`, `perroncert check`, `check_d_strict.py`, and the outside seat's Go checker |

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

### The outside seat's Go checker

An outside seat wrote this checker in Go, standard library and exact integers, from the wire format in [`PERRON-REVIEW.md`](PERRON-REVIEW.md). Its source is pinned by hash, `8009406c…`.
On a fresh hosted runner, [run 41509351749](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41509351749) fetched all 34 sectors and the four vectors from Hugging Face without a token, each pinned by SHA-256. Its log and artifact are in
[`outside-go-41509351749/`](outside-go-41509351749/). This seat's prediction is in [`TWO-SIDED-3x4.hbp`](TWO-SIDED-3x4.hbp), written at 19:25:15Z, and the first checker step began at 19:29:07Z.

| Vector | Predicted `t_cert_milli`, row, M | Printed by the Go checker |
|---|---|---|
| `d93000000.bin`, the control, in all 3 replays | 93061051, 44,742,735, 3 | 93061051, 44,742,735, 3 |
| `d93700000-pass5.bin` | 93718415, 44,742,735, 3 | 93718415, 44,742,735, 3 |
| `x3-b.bin` | 94065384, 44,742,735, 3 | 94065384, 44,742,735, 3 |
| `x3-c.bin` | **94070673**, 45,507,968, 3 | **94070673**, 45,507,968, 3 |

Each of the three replays also printed:

```
PASS merkle=PASS sector_hashes=PASS vector_hashes=PASS row_sums_zero=PASS W_self_adjoint=PASS
flat_rows=7 min_nonzero_mag=3 max_mag=36 weighted_residual=0
payload_zero_padding=742160 raw_tail_bytes=349114368 raw_tail_nonzero=347747335
```

Two fault controls ran, each rejected with empty standard output. One flipped payload byte stopped at the merkle comparison, and d = 0 on the first non-flat row stopped at the positivity test:
`FAIL: non-flat row 1 has nonpositive d: 0 / 2094576564`.

The scope of this check:

- **The values are computed.** The source floors (9,000,000·M·d_h + 1,000,000·Σ z d_j) / d_h on every non-flat row, and holds none of the blind values. The workflow states an expected value for the control alone.
  The blinding was partial: this seat's status messages named these values before the run.
- **Self-adjointness.** It draws x and y from −3..3 with one fixed seed. One bad pair (h, j) passes when x_h y_j = y_h x_j, which 289 of the 2,401 tuples satisfy (0.12036…, by enumeration). `check_d_strict.py` tests the same
  property modulo 2⁶¹ − 1, with a false-pass chance of about 10⁻¹⁸. The Go checker's two fault controls in this run stop before that test. On a fixture with every hash repaired, it reports 1,071 of 1,198 single-pair faults, as predicted, and all 211 row-sum faults: below.
- **The rows.** It reads them as stored, with the merkle and the sector hashes checked. `fullrebuild` compares them with the definition of H: section 7.

### Every 3×4 row against the definition of H

`second-seat/fullrebuild.rs`, run at the operator's word, recomputes each row from the rules: S₃ from permutations, the lattice, the gauge fixing, the canonical key, weight, M and every move. It compares each one with the store.
Its prediction was written first, in [`FULLREBUILD-RUN.hbp`](FULLREBUILD-RUN.hbp): 45,508,080 rows, 0 mismatches, with any mismatch falsifying store = H. It printed, in [`FULLREBUILD-3x4.out`](FULLREBUILD-3x4.out):

```
FULLREBUILD|L=3x4|V=12|nl=24|n=45508080|rows_rebuilt=45508080|rows_read=45508080|canonical_key_mismatch=0|weight_mismatch=0|M_mismatch=0|entries_mismatch=0|merkle=PASS|secs=7870|json=0
```

It exited 0 with an empty standard error, after 7,870 s on 6 threads, and every progress row read 0 mismatches. After it ended, its executable and source still matched the hashes recorded before the run (`202e8f3e…`, `2e9ea995…`), and
all 34 local sector files matched the public manifest `9213927b…`, by [`hash_store.py`](hash_store.py).

The scope of this check:

- **The key list** comes from `passA.bin` (`eefd7752…`, public) and is verified: each key must recompute as canonical, keys ascend strictly, a move outside the list counts as a mismatch, and the recomputed weights must equal the store's,
  which `check_d_strict.py` ties to `passA.bin`, whose weights sum to exactly 6¹³.
- **Controls.** It matches all rows on 2×2, 2×3 and 3×3. With a store's merkle repaired after one changed entry, M or weight, it reports exactly that mismatch and exits 2, on 4 of 4 controls: [`FULLREBUILD-CONTROLS.hbp`](FULLREBUILD-CONTROLS.hbp).
- **Who and where.** The second seat wrote it, separately from the store's builder, and it ran on this seat's machine. A replay on another machine is open: section 7.

### Every off-diagonal pair, exactly

[`allpairs`](../../../crates/evolvers/src/bin/allpairs.rs) compares w_h z_hj with w_j z_jh on every off-diagonal pair of the stored rows, in exact integers, with no random vector. An entry with no partner counts as a failure. It reads through `roomio`, so every pass recomputes the payload merkle. An outside seat recommended this check, and the operator relayed its approval.
Its prediction was written first, in [`allpairs/ALLPAIRS-RUN.hbp`](allpairs/ALLPAIRS-RUN.hbp), with any nonzero counter falsifying W-self-adjointness of the stored rows. It printed, in [`allpairs/ALLPAIRS-3x4.out`](allpairs/ALLPAIRS-3x4.out):

```
ALLPAIRS|L=3x4|sector=Sx+Sy+|n=45508080|rows_read=45508080|entries=3310759342|header_entries=PASS|diag=45508080|pairs=1632625631|passes=4|cap_entries=470000000|value_mismatch=0|lower_without_upper=0|upper_without_lower=0|columns_not_ascending=0|column_out_of_range=0|zero_z=0|positive_offdiag=0|row_sum_nonzero=0|zero_weight=0|missing_diag=0|flats=7|flat_w=1,3,2,3,3,2,4|flat_w_sum=18|sum_w=13060694016|codes=13060694016|whole_space_count=PASS|merkle=PASS|verdict=PASS|secs=2704|json=0
```

It exited 0 with an empty standard error, after 2,704 s in 4 passes, each holding at most 470,000,000 upper entries (3.5 GiB). Its executable and source kept their recorded hashes (`c68f25b4…`, `f4ea7e85…`). Those hashes belong to the original executable, at commit `8faadb0`. The corrected one is below.

The scope of this check:

- **What it reads.** The stored rows and weights. A change that keeps the weighted equality on both sides of a pair passes it, and `fullrebuild` reports that change: 2 entries, on each such control.
- **Controls.** On 2×2, 2×3 and 3×3, at large and small windows, with a store's merkle repaired after one change: 49 of 49 outcomes as predicted in writing first, in [`allpairs/CONTROLS.hbp`](allpairs/CONTROLS.hbp). A changed value is one mismatch, a moved column is two unpaired entries, and a changed weight breaks every pair of its row. An unrepaired byte stops it at the merkle with exit 1.
- **The counts beside the pairs.** On the same rows it finds ascending columns in range, no zero entry, no positive off-diagonal, a diagonal on every row and every row sum 0. The weights sum to 6¹³ = 13,060,694,016, with flat weights 1, 3, 2, 3, 3, 2, 4 summing to 18, as in `passA.bin`.
- **Who and where.** This seat wrote it, and it ran on this seat's machine. A second seat's review, an exact pair test in the outside seat's own code, and a replay on another machine are open: section 7.

### Faults that reach each checker's gates

[`allpairs/fixture-controls/run_fixture_controls.py`](allpairs/fixture-controls/run_fixture_controls.py) puts one fault at a time into a small copy of the 2×2 store, with the merkle, the sector hash and the manifest recomputed, so each checker's later gates see it. The public store stays as it is.
[run 41575947849](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41575947849) on hosted Linux built the Go checker from its pinned source `8009406c…` with go1.24.13, the version of its own run, and `allpairs` on Rust 1.81. Every outcome below was predicted in writing first, in [`allpairs/ALLPAIRS-RUN.hbp`](allpairs/ALLPAIRS-RUN.hbp), and met, in [`allpairs/fixture-controls/FIXTURE-CONTROLS.hbp`](allpairs/fixture-controls/FIXTURE-CONTROLS.hbp).

| Checker | Clean store | One row-sum fault, on each of 211 rows | One pair fault, on each of 1,198 pairs |
|---|---|---|---|
| The outside seat's Go checker | Passes, with the predicted values | 211 reported, at its row-sum gate | 1,071 reported, at its self-adjoint gate with the predicted residual. 127 pass |
| `check_d_strict.py` | Passes, with the predicted value | 211 reported: 204 at its row-sum gate, and the 7 flat rows at its flat-diagonal gate | 1,198 reported, at its self-adjoint gate |
| `allpairs` | Passes | 211 reported by row sum, with every pair clean | 1,198 reported, each as one value mismatch with row sums clean |

The 127 are the pairs where x_h y_j = y_h x_j under the Go checker's fixed seed: 10.6% on this fixture, against 289 of 2,401 tuples, 12.04%, over the range. On 3×4, `allpairs` above measures every pair exactly.

### The count gates, corrected

A review the operator relayed on November 3 found that the original `allpairs` let `OPEN` through on its two count gates, `header_entries` and `whole_space_count`: its verdict tested `!= "FAIL"`. A gate reads `OPEN` when the header gives nothing to compare. The recorded 3×4 line prints `PASS` on both gates, so that result stands as recorded.

| Executable | Source | SHA-256 | Exit 0 needs | What ran on it |
|---|---|---|---|---|
| Original | `f4ea7e85…`, at commit `8faadb0` | `c68f25b4…` | Each count gate at `PASS` or `OPEN` | The 3×4 run, the 49 controls, [run 41575947849](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41575947849) |
| Corrected | `5ab04b18…` | `d78f263f…` | Both count gates at `PASS` | 62 header cases, the 49 controls again, [run 41604837594](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41604837594) |
| Corrected, rebuilt from the source pinned at `0fd24d3` | `5ab04b18…` | `cdb22218…` | Both count gates at `PASS` | The 3×4 run, the 62 header cases and the 49 controls again |

The corrected executable also stops on a header that repeats a key, or that writes `n=` or `payload_bytes=` outside canonical form. It reads `entries=`, `nl=` and `L=` outside canonical form as `OPEN`. It stops on a store with no rows, where the original printed `merkle=PASS` with no merkle computed.

[`allpairs/failclosed/run_header_controls.py`](allpairs/failclosed/run_header_controls.py) puts one header change at a time on a copy of the 2×2 store, with the rows and the merkle as they are, and runs both executables. All 124 outcomes were predicted in writing first, in [`allpairs/failclosed/HEADER-PREDICTION.hbp`](allpairs/failclosed/HEADER-PREDICTION.hbp), and met: 124 of 124 on this machine, in [`allpairs/failclosed/HEADER-CONTROLS.hbp`](allpairs/failclosed/HEADER-CONTROLS.hbp), and again on hosted Linux with both built from source on Rust 1.81, [run 41604837594](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41604837594), with the same rows.

| On the 62 header cases | Original | Corrected |
|---|---|---|
| A count gate at `OPEN` | 22 cases, each exit 0 with `verdict=PASS` | 26 cases, each exit 2 with `verdict=FAIL` |
| A count gate at `FAIL` | 5 cases, each exit 2 | 3 cases, each exit 2 |
| The run stops, exit 1 | 14 cases | 30 cases |
| Exit 0 | 42 cases | 2 cases: the clean store, and the one that removes the fields this tool leaves unread |
| A store whose header reads `YMROOMHDR\|n=0\|payload_bytes=0\|w_self_adjoint=PASS\|json=0` | Exit 0, `verdict=PASS`, `pairs=0`, `merkle=PASS` | Exit 1, `reason=n is 0` |

The scope of this correction:

- **The repeat.** With the corrected executable, the 49 controls gave the same 49 outcomes, and all 131 rows match the original [`allpairs/CONTROLS.hbp`](allpairs/CONTROLS.hbp) apart from `secs=`: [`allpairs/failclosed/CONTROLS-REPEAT.hbp`](allpairs/failclosed/CONTROLS-REPEAT.hbp). On hosted Linux, the fixture faults on all three checkers gave a file byte-identical to the original's, `3ff98769…`.
- **Unit tests.** 19 pass on Rust 1.81, and clippy with `-D warnings` exits 0. With the old rule put back, 2 of them fail. With the header check removed 1 fails, with an empty store allowed 1 fails, and with lenient numbers 4 fail.
- **The fields it reads.** `L`, `n`, `nl`, `entries`, `payload_bytes`, `payload_merkle` and `w_self_adjoint`. It prints `sector`, and leaves `rooms`, `stream_bytes`, `chunk`, `keys_sha256` and `json` unread, as one case measures.
- **Rebuilds.** An unexpected result, recorded as a failure of byte reproducibility in [`allpairs/failclosed/pin-0fd24d3/PIN-RUN.hbp`](allpairs/failclosed/pin-0fd24d3/PIN-RUN.hbp): three builds of one source on Windows gave three file hashes, `d78f263f…`, `cdb22218…` and `9bc0675a…`. They differ by 24 and 20 bytes, all in the linker's time stamps and PDB GUID, and [`allpairs/failclosed/pe_normal_hash.py`](allpairs/failclosed/pe_normal_hash.py) gives `953fa422…` for all three with those fields zeroed. A replay compares the source hash and that normal hash. The first prediction for the 3×4 run named `d78f263f…`. The operator directed a rebuild from the pin before the start, so the run used `cdb22218…`, under a new prediction, and both rows are in the record.
- **The original evidence.** Every receipt of the 3×4 run stays as it was, with its hashes, and `git show 8faadb0:native/ym/crates/evolvers/src/bin/allpairs.rs` gives its source.

The operator then directed a full 3×4 run with the corrected executable, rebuilt from the source pinned at `0fd24d3`. Its prediction was written first, in [`allpairs/failclosed/pin-0fd24d3/PIN-RUN.hbp`](allpairs/failclosed/pin-0fd24d3/PIN-RUN.hbp), with every output row the same as the original's apart from `secs=`. It printed, in [`allpairs/failclosed/pin-0fd24d3/ALLPAIRS-3x4-PIN.out`](allpairs/failclosed/pin-0fd24d3/ALLPAIRS-3x4-PIN.out):

```
ALLPAIRS|L=3x4|sector=Sx+Sy+|n=45508080|rows_read=45508080|entries=3310759342|header_entries=PASS|diag=45508080|pairs=1632625631|passes=4|cap_entries=470000000|value_mismatch=0|lower_without_upper=0|upper_without_lower=0|columns_not_ascending=0|column_out_of_range=0|zero_z=0|positive_offdiag=0|row_sum_nonzero=0|zero_weight=0|missing_diag=0|flats=7|flat_w=1,3,2,3,3,2,4|flat_w_sum=18|sum_w=13060694016|codes=13060694016|whole_space_count=PASS|merkle=PASS|verdict=PASS|secs=2705|json=0
```

It exited 0 with an empty standard error, after 2,705 s in 4 passes of 705, 557, 738 and 701 s, and its executable and source kept their hashes. [`allpairs/failclosed/compare_pin_run.py`](allpairs/failclosed/compare_pin_run.py), written while the run was going, judged it against the operator's requirements: 31 of 31 met, in [`allpairs/failclosed/pin-0fd24d3/PIN-COMPARE.hbp`](allpairs/failclosed/pin-0fd24d3/PIN-COMPARE.hbp). Both count gates read `PASS`, with 0 mismatches, 0 unpaired entries, every structure counter 0, and merkle PASS on each of 4 passes. Apart from `secs=`, all 5 rows match the original run's, `609bc96f…` in both. That judge reported all 20 faults put to it and passed the 2 copies that should pass: [`allpairs/failclosed/pin-0fd24d3/COMPARE-CONTROLS.hbp`](allpairs/failclosed/pin-0fd24d3/COMPARE-CONTROLS.hbp). The small controls ran again on this exact executable, with the same rows: [`allpairs/failclosed/pin-0fd24d3/HEADER-CONTROLS-PIN.hbp`](allpairs/failclosed/pin-0fd24d3/HEADER-CONTROLS-PIN.hbp) and [`allpairs/failclosed/pin-0fd24d3/CONTROLS-PIN.hbp`](allpairs/failclosed/pin-0fd24d3/CONTROLS-PIN.hbp). To repeat the run and its judgement from the public files: [`allpairs/failclosed/reproduce_pin_run.sh`](allpairs/failclosed/reproduce_pin_run.sh).

The scope of this run: this seat wrote the tool, and it ran on this seat's machine, on the same store as the original run. It reads the stored rows and weights, as above. A replay on another machine is open.

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

Its first objections as a hostile reader stand as open items: the upper side bounds λ₁(H′) and E₉ has a lower bound only, and on 3×4 the rows are matched to H on samples plus all-rows structure checks. `fullrebuild` has since matched all 45,508,080 rows: section 5.

## 7. Open

| Item | Run that measures it |
|---|---|
| The outside seat's Go checker, further | Its values, and its row-sum and self-adjoint gates on fixtures, are measured, in section 5. Open: an exact pair test in its own code, which goes beyond a wider range for x and y. Earlier runs, on its branch's [`independent-go-perron-20261102.yml`](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/blob/audit/independent-go-perron-20261102/.github/workflows/independent-go-perron-20261102.yml): the first stopped after the row loop on the format text this seat gave it, corrected in `PERRON-REVIEW.md`, and diagnostic run [41499253445](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41499253445) printed `trailing=742160 nonzero=0 merkle_matches=true`, as predicted in writing beforehand |
| Every 3×4 row against the definition of H | Done on this seat's machine: all 45,508,080 rows, 0 mismatches, as predicted in writing first, in section 5. Open: a replay on another machine from the public files, about 2.2 h at 6 threads |
| Every off-diagonal pair, exactly | Done on this seat's machine, by the original executable and by the corrected one: 1,632,625,631 pairs, 0 mismatches, each as predicted in writing first, in section 5. Open: a second seat's review of `allpairs`, and a replay on another machine from the public files, about 2,705 s here, with [`allpairs/failclosed/reproduce_pin_run.sh`](allpairs/failclosed/reproduce_pin_run.sh) |
| The gap below r = 6.076 on 3×4 | A solve at lower coupling, then the same checks. On 3×3 the flat bound's route ends between r = 4 and 4.06 |
| `perroncert` guards at absurd inputs | A hardened build with checked products, once the pinned runs are done |
| A verdict by this route | A rule revision and the operator's word: [`PERRON-RULE-DRAFT.md`](PERRON-RULE-DRAFT.md) |
| Uniformity in volume | A separate obligation. Each result here is a statement about one finite lattice. The volume-uniform proof is the research track named in the README's theory route |
| The continuum limit | A further obligation beyond uniformity in volume, named in the same place |
