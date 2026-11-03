# A Perron vector with few numbers, and a bound on the level above the flat cluster with no store

**Status: OPEN.** A second seat on this seat's model read it at `f24c5cb`, and its verdict is PASS, [below](#the-second-reader). GPT-6, on another model, read it at `e0466bd`, and its verdict is PASS at the four points it checked, [below](#a-reader-on-another-model). A verdict on the gap needs the operator's word. Everything here concerns one finite torus at a time. Uniformity in volume and the continuum limit are separate obligations.

Claims carry MEASURED, DERIVED (a short proof written here) or CONJECTURE. Energies are in J_E, and r = J_B / J_E. The Perron route is in [`../PERRON-BOUND.md`](../PERRON-BOUND.md).

## The question

The certified 3×4 value, 94.070673 at r = 9, uses a vector of 45,508,080 integers, and a 4×4 store would take 17 to 35 TB. The operator directed this test: how far does a vector with few numbers go?

## The vector

Let a and b count the plaquettes of a configuration whose holonomy is a transposition and a 3-cycle, so M = 2a + 3b. Call (a, b) its lump. Here d = g(a, b):

- **Product form:** d = ε^a η^b, two numbers.
- **Lump form:** one free value per lump.

Both are positive and gauge invariant, and set to 0 on the flat states. Any such d enters the Barta bound of `PERRON-BOUND.md` as it stands. `min (H′d)/d` is concave in log g, so a fit has one optimum to find.

## The bound with no store

**DERIVED.** A move on a link ℓ by a transposition s changes only the two plaquettes holding ℓ. In the frame of ℓ their holonomies x and y become s·x and s·y. So the change in (a, b) depends only on the link's pattern. With t, t′ transpositions and c, c′ 3-cycles:

| Pattern (x, y) | Moves, as (Δa, Δb) × count |
|---|---|
| e, e | (+2, 0) × 3 |
| e, t | (0, 0) × 1, (0, +1) × 2 |
| e, c | (+2, −1) × 3 |
| t, t, the same in the frame | (−2, 0) × 1, (−2, +2) × 2 |
| t, t′, different | (−2, +1) × 2, (−2, +2) × 1 |
| t, c | (0, −1) × 1, (0, 0) × 2 |
| c, c′ | (+2, −2) × 3 |

The ratio at a configuration is then

    (H′d)/d = r(2a + 3b) + Σ_links Σ_moves (1 − g(a′, b′)/g(a, b)),   with g(0, 0) = 0,

and it depends on the configuration only through (a, b) and the number of links of each pattern. Those numbers obey:

1. **Each plaquette holds 4 links:** 4a = n(e,t) + n(t,c) + 2 n(t,t), 4b = n(e,c) + n(t,c) + 2 n(c,c), and the n's sum to nl, the number of links.
2. **Parity:** a is even, since the signs of all plaquettes multiply to +1.
3. **Adjacency:** at most 2|S| − min(⌈2√|S|⌉, min(Lx, Ly), ⌈2√(P − |S|)⌉) links have both plaquettes in a set S of plaquettes, for 0 < |S| < P. The proof is in the head of [`local_table.py`](local_table.py).

[`local_table.py`](local_table.py) writes every integer solution as a row of a table. Every non-flat gauge orbit of the torus has its row there. So for any g,

    E₉(whole gauge-invariant space)  ≥  λ₁(H′)  ≥  min over the table of the ratio,

and E₈ ≤ 3·nl, as in `PERRON-BOUND.md`. Every non-flat orbit has M ≥ 3, by parity, so the same g gives E₉ − E₈ ≥ (t − 3·nl) + 3(r − r_fit) for every r ≥ r_fit. The chain uses no rows of H.

## Measured on the stores

**The rule against every stored row.** Each signature of a real store must be a row of the table, exactly (`local_table.py --check`):

| Store | Rows checked | Store signatures | Table rows | Missing |
|---|---:|---:|---:|---:|
| 3×3 | 288,638 | 542 | 997 | **0** |
| 3×4 | 45,508,073 | 3,660 | 6,505 | **0** |

**The vectors.** At r = 9. "Checker" is the pinned `perroncert check` on every row. Its value equals the fit's in each row read so far.

| Lattice | Numbers in d | Fit, on the census table | Pinned check, every row | Flat bound | From above |
|---|---:|---:|---:|---:|---:|
| 3×3 | 2 | 69.986514 | **69.986514** | 54 | 76.448399 |
| 3×3 | 30 | 73.502035 | **73.502035** | 54 | 76.448399 |
| 3×4 | 2 | 85.120864 | **85.120864** | 72 | 94.070936 |
| 3×4 | 49 | 89.921453 | **89.921453** | 72 | 94.070936 |
| 3×4, the certified vector | 45,508,080 | | 94.070673 | 72 | 94.070936 |

The prediction for 3×4, committed at `c91db51` before that run: at least 80 with two numbers and at least 88 with one value per lump, each above 72. Both met. Rows in [`VECTOR-RUN.hbp`](VECTOR-RUN.hbp).

**Lower coupling on 3×4.** The vector of 49 numbers fitted at r = 5.4 reads **72.133111** through `perroncert check` at JB = 5400, on every row, tight at M = 12, as predicted in writing first to the last digit. So on 3×4, by the lift and the flat bound of `PERRON-BOUND.md`,

    E₉ − E₈ ≥ 0.133111 + 3(r − 5.4) J_E   for every r ≥ 5.4.

The earlier limit on 3×4, from a solve, is r = 6.076, and that row stays in [`../PERRON-TWO-SIDED.md`](../PERRON-TWO-SIDED.md). The move comes from fitting the vector at the coupling in question, since a lower coupling needs little of the vector's shape.

## The bound on lattices with no store

[`prodvec`](../../../../crates/evolvers/src/bin/prodvec.rs) `fit` on the table of `local_table.py`, then [`check_local_bound.py`](check_local_bound.py), which recomputes the minimum in Python integers from the table and g, with no shared code. MEASURED as computations. The statements on E₉ and E₈ are DERIVED from them.

| Torus | nl | Flat bound 3·nl | Two numbers | One value per lump | E₉ − E₈ ≥, at r = 9 |
|---|---:|---:|---:|---:|---:|
| 3×3 | 18 | 54 | 69.939027 | 73.106758 | 19.106758 |
| 3×4 | 24 | 72 | 85.120864 | 89.291147 | 17.291147 |
| **4×4** | 32 | 96 | 106.150577 | **112.252744** | **16.252744** |
| 4×5 | 40 | 120 | 127.118270 | 134.017195 | 14.017195 |
| 5×5 | 50 | 150 | 154.016734 | | 4.016734 |

On 5×5 the fit of one value per lump runs out of the range of its fixed point at the highest lumps, which leaves a weak 88.499986 in its row, so the two-number value is the bound there. The 4×4 two-number value comes from [`product_bound.py`](product_bound.py), which found a better pair than `prodvec` did (106.126509), and an exact evaluation of the table at that pair gives the same 106.150577. Rows in [`LOCAL-RUNS.hbp`](LOCAL-RUNS.hbp). The tables themselves regenerate from `local_table.py`, and their hashes are in those rows.

**4×4 at lower coupling,** one value per lump, each fit at its own r:

| r | 6 | 7 | 8 | 9 |
|---|---:|---:|---:|---:|
| E₉ − E₈ ≥ | 0.472613 | 6.290085 | 11.488057 | 16.252744 |

So on 4×4, E₉ − E₈ ≥ 0.472613 + 3(r − 6) J_E for every r ≥ 6.

**Every size, by a formula.** [`product_bound.py`](product_bound.py) needs no table. In the two-number form the ratio at any configuration is 3·nl(1 − ε²) + a·A + b·B + x·D_TT + y·D_TC + z·D_CC, with constants set by ε², η and r, and x, y, z the numbers of neighbouring pairs of defects. It minimizes that over each lump's constraints, at the vertices, in exact rationals. At the same (ε², η) it equals the exact minimum of the tables for 3×3, 3×4 and 4×4, and of the real 3×4 store's table.

| L × L | E₉ − E₈ ≥ at r = 9 | r = 12 | r = 16 | r = 24 | Least r with a positive bound, in steps of 1/8 |
|---:|---:|---:|---:|---:|---:|
| 3 | 15.903 | 27.513 | 41.569 | 67.709 | 5.5 |
| 4 | 10.151 | 23.015 | 38.105 | 65.318 | 7.125 |
| 5 | 4.013 | 18.439 | 34.621 | 62.898 | 8.375 |
| 6 | −4.957 | 11.564 | 29.386 | 59.343 | 9.875 |
| 7 | −15.030 | 4.028 | 23.431 | 55.256 | 11.375 |
| 8 | −26.831 | −4.912 | 16.509 | 50.510 | 12.875 |

The least r grows by about 1.5 per unit of L over this range. Rows in [`PRODUCT-SCAN.hbp`](PRODUCT-SCAN.hbp).

**The rule on real 4×4 configurations.** `check_local_bound.py` builds S₃ link configurations, computes each move from the definition by recomputing every plaquette, and requires the signature to be in the table and the ratio to be at least the bound: uniform random, walks from a flat configuration, and descents in M, which reach (a, b) = (0, 1), the lump where the two-number form is tight. No configuration fell outside the table, and none read below the bound: 30,000 on 4×4 at r = 9, reaching 69 lumps, with a lowest ratio of 112.252744 against the bound 112.252744, and 6,000 each on 3×3, 3×4 and 4×5, 2,000 on each two-number row, and 6,000 at r = 6 on 4×4.

**Exhaustive on real configurations.** [`localaudit`](../../../../crates/evolvers/src/bin/localaudit.rs) goes through gauge-fixed link configurations from the definition of H. It applies each move, recomputes the two plaquettes holding its link, and requires the row to be in the table and the ratio to be at least the bound.

| Torus and range | Configurations | Flat | Not in the table | Below the bound | Least ratio | Bound |
|---|---:|---:|---:|---:|---:|---:|
| 3×3, all | 60,466,176 | 18 | 0 | 0 | 73.106758 | 73.106758 |
| 4×4, M ≤ 8 | 2,151,666 | 18 | 0 | 0 | 112.252754 | 112.252744 |
| 4×4, M ≤ 12 | 119,790,810 | 18 | 0 | 0 | 112.252744 | 112.252744 |
| 4×4, M ≤ 14 | 624,556,890 | 18 | 0 | 0 | 112.252744 | 112.252744 |

On 3×3 its count of configurations per lump equals the store's weights, on all 29 lumps. On 4×4 the least ratio reaches the bound exactly, at (a, b) = (0, 3). Above M = 14 on 4×4 the evidence is the proof, the samples above and the second reader's walks and hunts below.

**The adjacency limit, by brute force.** Over every subset of plaquettes on 3×3, 3×4, 4×4, 4×5 and 5×5, 33,554,432 subsets on the last, no size exceeds the limit, and it is reached at 8, 9, 11, 12 and 16 sizes respectively.

**Can these checks go red?** [`mutate_local_table.py`](mutate_local_table.py) changes one entry of the rule or one constraint at a time, and all 20 changes are caught on the 3×3 store. `localaudit` exits 2 with the bound one unit above the least ratio, and with one lump's rows taken out of the table. Rows in [`AUDIT-RUNS.hbp`](AUDIT-RUNS.hbp) and [`MUTATE-3x3.hbp`](MUTATE-3x3.hbp).

## The second reader

A second seat on this seat's model, in a separate session and with its own code, read the pinned commit `f24c5cb`. Its report and ledger stay as it wrote them: [`review-opus55/VECTOR-REVIEW.md`](review-opus55/VECTOR-REVIEW.md), [`review-opus55/REVIEW.hbp`](review-opus55/REVIEW.hbp). Its verdict:

> **Overall: PASS. I did not refute the claim.** Every step of the chain holds by proof and by a run. All four numbers reproduce to the micro from my own table on my own code. Each of the four is attained by a real link configuration, so each is the true minimum of the ratio for its vector, and no configuration falls below it. Rayleigh-Ritz from above stops 5.3 to 16.3 J_E above the claimed values. Every sabotage turned a check red, with one exception that I list in section 7.

MEASURED by its runs:

| Check | Result |
|---|---|
| The move table, written by hand before it opened `local_table.py` | 108 of 108 frame triples. All 3·nl moves recomputed from all plaquettes on 43,836 hunt states and 2,375,704 low-M orbits: 0 mismatches |
| The adjacency limit | Every subset of 10 tori, up to 2³⁰ subsets: 0 violations |
| The tables | Equal to its own signature sets on all 5 tori: 997, 6,505, 29,422, 130,981 and 465,479 rows |
| Full censuses | 3×3, 60,466,176 configurations, and 3×4, 13,060,694,016: 18 flats in 8 classes, 0 outside the rule, real minima 73.106758 and 89.291147, equal to the tables' |
| Class walks | 4×4, 3¹⁶ assignments, and 4×5, 3²⁰: 0 outside the rule, minimum equal to t |
| Hunt | 468,432,981 accepted states across 4×4 at r = 9 and r = 6, 4×5 and 5×5: 0 below t, 0 outside the rule, and the tight row of each is a real configuration |
| From above | E₉ ≤ 117.575598 (4×4), 105.584008 (4×4, r = 6), 140.955674 (4×5), 170.282263 (5×5) |

It lists what stays open after its checks. It shares this seat's model, so a misreading of H, or a slip in the shared linear algebra, stays open until another model or a person reads its sections 2 and 3. At 4×4 and above, real configurations past the low-M cuts were reached by search, on top of the walks. It ran on one machine, and it did not run `check_local_bound.py` or `product_bound.py`. One sabotage stayed green: a planar-only adjacency limit leaves `py_exact_t.py` at 112252744 at r = 9, since the tight row does not use the limit, and its `subsets`, `hunt`, `census` and `classes` each catch that error. Its misses, P8, P12 and a control design error, are kept in its ledger.

Correction, beside that sentence on the sabotage that stayed green: the tight row does rest on the limit. Its 2 links of (c, c) sit on the cap 2·3 − 4 = 2 for 3 plaquettes, and the planar-only limit gives the same 2, so that sabotage cannot move the row. With 3 such links the ratio falls to 96.972626, as GPT-6's control below found. [`review-gpt6/CAP-CHECK.hbp`](review-gpt6/CAP-CHECK.hbp) reads each value from the pinned vectors in exact fractions. The reader's section 7 carries the same wording and stays as written, and its conclusion stands: the value of t alone cannot see that sabotage at r = 9.

Its note on the commit: `f24c5cb` holds no vector for 4×4, 4×5 or 5×5. `e814659` holds them as `G-local-*`, and they are hash-equal to its `given/` on all six (MEASURED).

The author's rerun of its checks, in [`review-opus55/RECHECK-BY-THE-AUTHOR.hbp`](review-opus55/RECHECK-BY-THE-AUTHOR.hbp): the four numbers, `py_e8_dressed.py` on six tori and `py_hybrid_recheck.py` at cuts 8 and 10 give what it reports, the sabotage runs go red, and `clippy -D warnings` exits 0 on Rust 1.81. Its `review/` builds from a copy outside this repository, since `native/ym/Cargo.toml` is a workspace root above that folder. Its 34 large vectors are on the run disk, hashed in [`review-opus55/BIG-FILES.hbp`](review-opus55/BIG-FILES.hbp). The `.hybrid` vectors behind the table below are among them. Of the 39 Ritz vectors its rows name, 20 are absent from its folder, including those behind the upper values on 4×4 at both couplings and on 4×5. Those values stand on the A, B and C rows in `out/` and rerun from `ritz`, and the same file lists each absent vector.

## A reader on another model

GPT-6 rebuilt the bound at `e0466bd` with its own exact-integer checker, reading only the pinned vectors. Its review stays as it wrote it: [`review-gpt6/REVIEW-e0466bd.md`](review-gpt6/REVIEW-e0466bd.md). Its verdict:

> **Verdict: PASS for the store-free local-rule bound at the four checked lattice/coupling points, with an independent exact-integer implementation and additional physical/configuration checks. HYBRID (low-M exact + high-M lumps) is a separately scoped lead and is not yet independently certified by this seat.**

MEASURED by its runs, as its review reports them:

| Check | Result |
|---|---|
| The move table, S₃ built from scratch | 108 of 108 triples reproduce the 7 rows, 0 disagreements |
| The adjacency limit, re-derived | Every subset on 3×3, 3×4, 4×4, 4×5 and 5×5: 0 violations, reached at 8, 9, 11, 12 and 16 sizes, equal to the counts above |
| Exact minimum from the pinned vectors | 112.252744, 96.472613, 134.017195 and 154.016734, over 29,422, 29,422, 130,981 and 465,479 candidates, tight at the same rows as above |
| Real 4×4 configurations | 1,250 seeded, 136 flat, 1,114 tested, all 96 moves from full plaquette holonomies: 0 below the bound, least 112.252772 |
| Controls | The bound raised by 1 micro: FAIL, exit 2. A cap of 3 rather than 2 links of (c, c) at (0, 3): ratio 96.972626 |
| The E₈ formula, as numbers | 93.506098468 at r = 9 and 92.508066615 at r = 6 on 4×4 |

It states the chain in its own words, from interlacing and Barta to E₈ ≤ 3·nl and the growth 3(r − r_fit), in its section on proof scope. Its first hand copy of the 4×4 vector held three transcription errors and gave FAIL, and the copy checked against the Git blob gave PASS; its review keeps that. It names three checks as still to come: rebuilding the Ritz upper values, building the 16-dimensional E₈ space, and attacking the hybrid certificate. The hashes of its sources are in [`review-gpt6/REVIEW.hbp`](review-gpt6/REVIEW.hbp), and the source files are in its conversation with the operator.

## Two results from the second reader that raise the numbers

Both lie outside the claim it was asked to attack, and nobody but their writer has attacked them yet. The author's rerun above reaches only the small cuts. GPT-6 evaluated the E₈ formula as numbers.

**A tighter E₈, for min(Lx, Ly) ≥ 4.** DERIVED by the reader, with each matrix element confirmed in exact integers by `py_e8_dressed.py`. The author rederived the blocks by hand, after reading them. For each flat orbit f take its indicator and the function that counts moves into f. On such a torus two moves or three cannot connect distinct flats, so H on these 16 functions is block diagonal over f, each block [[3·nl, −√(3·nl)], [−√(3·nl), 3·nl + 4r]], and

    E₈ ≤ 3·nl + 2r − √(4r² + 3·nl).

On 3×3 and 3×4 a three-link dual loop connects flats, and the check prints FAIL there with nonzero cross elements, as the reader predicted.

**A hybrid vector, a lead.** Let d be the actual vector on every orbit with 0 < M ≤ cut, one value per lump above the cut, and 0 on the flats. Rows at M ≤ cut are exact. Rows above are the table's rows, with a move into a lump at M ≤ cut taken at the largest d in that lump. Barta applies as before when the model holds every non-flat orbit with M ≤ cut. `py_lump_counts.py` checks that per lump against C(P; a, b)·N(a, b), with N = 12·3^a·2^b for even a ≥ 2 and N = 12·2^b + 6(−1)^b for a = 0. That N is the Frobenius count on a torus with one puncture per defect (DERIVED by the author), and each row below has `bad=0`.

| Torus, r | Cut | Sector states | E₉ ≥ | E₉ ≤ | E₈ ≤ | E₉ − E₈ ≥ | Store-free bound above |
|---|---:|---:|---:|---:|---:|---:|---:|
| 4×4, 9 | 14 | 825,865 | **117.453728** | 117.575598 | 93.506099 | **23.947629** | 16.252744 |
| 4×4, 6 | 14 | 825,865 | 103.521056 | 105.584008 | 92.508067 | 11.012989 | 0.472613 |
| 4×5, 9 | 13 | 1,358,823 | 140.546984 | 140.955674 | 116.928693 | 23.618291 | 14.017195 |
| 5×5, 9 | 11 | 473,677 | 168.020667 | 170.282263 | 146.228459 | 21.792208 | 4.016734 |

MEASURED by one Rust path, `review-opus55/review/src/bin/ritz.rs`, in seconds to minutes with no store. The separately written `py_hybrid_recheck.py` reproduces the row minima exactly on 4×4 at cut 8 (94.475741) and cut 10 (115.534179). The rows at the cuts in this table rest on the one path so far. On the controls the certificate stays below the known upper values: 3×4 at cut 14 gives 94.011545 against 94.070673, and the whole 3×3 space gives 76.443824 against 76.448397.

Retraction, kept beside: the reader's first hybrid numbers at cut 12 (3×4 93.829570, 4×4 117.345755) are not rigorous. A cut divisible by 3 misses the (0, cut/3) orbits with no two 3-cycles adjacent, since their only moves lead past the cut. The per-lump count caught it, and `py_missing_check.py` matches the missing counts exactly on four models. The table above uses complete cuts only.

## What limits it

**Volume.** With the flat bound, t − 3·nl falls as the lattice grows, at about 0.23 per link in the lump form at r = 9, in the table above. Part of that is the vacuum shift, about nl/12 at r = 9, which a dressed trial state for E₈ would recover (CONJECTURE, unmeasured here). Beside that, MEASURED by the second reader's formula above: its one-excitation state recovers 2.493901, 3.071307 and 3.771541 on 4×4, 4×5 and 5×5 at r = 9, against nl/12 = 2.667, 3.333 and 4.167. It grows as √(3·nl) once nl passes 4r²/3 (DERIVED), so an extensive shift on larger tori needs a trial state with many excitations.

**The interlacing step itself.** Removing the 8 flat states from H removes little once the vacuum carries small weight on exactly flat configurations. At fixed r that weight falls exponentially in volume, so λ₁(H′) approaches E₈ (CONJECTURE, by the count of virtual pairs, 3·nl/(4r)² on average). So this route reaches L up to about a multiple of r. The stability theorem in [`docs/YM_TOPOLOGICAL_STABILITY_PROOF.md`](../../../../../../docs/YM_TOPOLOGICAL_STABILITY_PROOF.md) is the route to uniformity, and this route gives explicit numbers at each L on the way.

## Open

| Item | Run that measures it |
|---|---|
| Another model's rebuild of the Ritz upper values and of the 16-dimensional E₈ space | GPT-6's own checkpoints, each from the definition of H, with the absent Ritz vectors rerun |
| An attack on the hybrid certificate at the cuts in its table | A separate program that reads the `.hybrid` vectors, recomputes every row at M ≤ cut from the definition of H and every table row above it, and counts each lump. GPT-6 names the same target: all 825,865 low-M states on 4×4, the count of each lump, and the preserved vectors |
| The hybrid form at lower r and on 6×6 and larger | The same certificate at those points, with the count of each lump |
| Vectors with more structure, such as a count of neighbouring pairs of each kind, to close the distance from 89.92 to 94.07 on 3×4 | The same census, with a wider lump |
| An upper bound on E₈ with many excitations, on 4×4 and beyond | A trial space with the flats and the low-M orbits, with its Rayleigh quotient |
| The other finite groups | The same table by brute force over pairs of group elements: Q8, 2T, 2O, 2I |
| A proof in Lean of the pattern table and the chain | A statement-only file and a proof file, on the layout of `anthropics/formal-math` |
| Larger tori in the lump form | A generator that keeps only the extreme rows of each lump |
| A verdict by this route | The operator's word |
