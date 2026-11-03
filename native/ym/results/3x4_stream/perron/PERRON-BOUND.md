# Perron lower bound on the level above the flat cluster (draft, November 2, 2026)

**On the 3×4 store the bound certifies 94.070673 J_E, by the author's two checkers and an outside seat's Go checker, and λ₁(H′) ≤ 94.070936 J_E.** The first certificate was 93.061051, and
[`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md) has how it rose. All 45,508,080 rows of that store match the definition of H, by a second seat's full rebuild, and all 1,632,625,631 off-diagonal pairs satisfy w_h z_hj = w_j z_jh exactly. The verdict stays open until the steps in section 4 are done. Claims
are tagged MEASURED, DERIVED (a short proof written here) or CONJECTURE. The rows and hashes are in
[`PERRON-RESULT.hbp`](PERRON-RESULT.hbp), and [`PERRON-REVIEW.md`](PERRON-REVIEW.md) explains how to check them.

"Gap" here means E₉ − E₈, the gap above the eight flat states. The vacuum splitting E₂ − E₁ lies inside the flat cluster,
where the two lowest ball levels on 3×4 differ by about 0.04 J_E. The tools' `t_cert_milli` keeps the name `t_milli`: at
JE = 1000 it counts 10⁻⁶ J_E, so 93061051 means 93.061051 J_E.

## 1. The bound

In the orbit basis, H = J_E·E + J_B·M, where E is a graph Laplacian: each of the 3·nl single-link moves puts
−1 in the row of the orbit it leads to, and M is diagonal. So every off-diagonal entry is ≤ 0. Let F be the
flat states (M = 0) and H′ be H with the rows and columns of F removed.

**DERIVED.** For any vector d > 0 on the non-flat states,

    E_{|F|+1}(H)  ≥  λ₁(H′)  ≥  min_h (H′d)_h / d_h.

1. **First inequality, Cauchy interlacing.** The orbit states are W-orthogonal, so H′ is a principal
   compression of H in a symmetrizable form, with |F| rows removed.
2. **Second inequality, Barta / Collatz–Wielandt.** H′ = s − N with N ≥ 0 entrywise, so λ₁(H′) = s − ρ(N).
   For d > 0, D⁻¹ N D has largest row sum max_h (Nd)_h/d_h, and ρ(N) is at most that.

Both steps hold for any d > 0, and a poor d simply gives a weaker bound. The solver is therefore untrusted: the only thing
checked is one exact integer pass over the rows, and that pass also verifies the signs, the positivity of d and the
store's merkle. The cost is the number of passes the solver wants plus one check pass, and memory is one integer per row.

## 2. From the sector to the whole space

**DERIVED.** Let X be all gauge orbits, and let G be the lattice symmetries that define the Sx+Sy+ sector.
G preserves H and maps flats to flats. Lift d from the sector by d̃(x) = d(rep x), with d̃ = 0 on flats. Each
sector row has one −1 per move into a target G-orbit, and its diagonal is 3·nl minus the moves that return to
the same orbit. Therefore

    (H′_whole d̃)(x) = J_B M(x) d̃(x) + J_E Σ_moves (d̃(x) − d̃(m·x)) = (H′_sector d)(rep x).

The ratios are the same at every x, so the same minimum bounds λ₁(H′_whole). Interlacing in the whole space,
with its 8 flat orbits removed, gives

    E₉(whole gauge-invariant space, all momenta and symmetry sectors)  ≥  min_h (H′_sector d)_h / d_h.

So one certificate on one sector's rows bounds the 9th level of the whole space.

**The sector statement.** The same pass gives E₈(+,+) ≥ t_cert directly, with 7 flat states in the sector. It needs only the
rows, and the whole-space statement above adds the lift.

**The gap.** The 8 flat orbits are mutually W-orthogonal, with diagonal 3·nl and zero couplings between them
(`flatcomp`), so E₈ ≤ 3·nl J_E by min-max, for every r. M ⪰ 0, so E₉ can only rise with r. A certificate
at r = 9 therefore gives

    E₉(r) − E₈(r)  ≥  t_cert − 3·nl    for every r ≥ 9.

At r = 9 alone, a tighter upper bound on E₈ can replace 3·nl, from a count on a whole-space ball.

**Growth with r.** DERIVED, pointed out by an external reviewer. With the same d, each row's ratio at r is its ratio at
r = 9 plus (r − 9)·M_h, in units of J_E. Every non-flat row has M ≥ 3 (MEASURED below), so

    E₉(r) − E₈(r)  ≥  t_cert − 3·nl + 3(r − 9)    for every r ≥ 9.

**Volume.** These are statements about one finite lattice. With the flat bound, t_cert − 3·nl shrinks as the lattice grows,
because 3·nl omits a vacuum shift that grows with volume, about nl/12 at r = 9.

## 3. Measured so far

### P0 on the 3×4 store

MEASURED. `flatcomp --room` on the store, merkle `ec03c5f8…` checked: 7 flat states, all diagonals exactly 72,
0 flat-flat couplings, as predicted before the run. This is the registered precondition P0, and it passed.

### The upper side on 3×4

MEASURED:

- **Whole-space flats.** `ball 3 4 1` then `flatcomp`: 8 flat states, all diagonals 72, 0 couplings. So E₈ ≤ 72 for every r.
- **E₈ at r = 9.** On the K = 2 whole-space ball (8,042 states), 0 levels lie below 69.900 and exactly 8 below 70.036.
  On K = 3 (155,386 states), exactly 8 lie below 70.031. Both are counted by `shellschur`, and K = 3 had 2,276 core
  columns with all of them decided. By interlacing, E₈ ≤ 70.031 at r = 9. The count is on a whole-space ball, so this bounds
  the 8th level of the cluster.
- **E₈(+,+) from above.** On the sector balls, counted by `schurcert` on `shellschur`'s column rows: 7 below 96.7 and
  8 below 96.8 at K = 3; 7 below 94.5 and 8 below 94.6 at K = 4. So E₈(+,+) ≤ 94.6.
- **Ball levels.** The 8th (+,+) level of the K = 3, 4 and 5 balls is 96.756025, 94.562413 and 94.121950. K = 5 has
  441,946 states, and a count of its ordering is open.

### The key table

MEASURED from `passA.bin` alone, [`PASSA-CENSUS-3x4.hbp`](PASSA-CENSUS-3x4.hbp). The weights sum to exactly
6¹³ = 13,060,694,016, one for each gauge-fixed configuration, so the rows cover the whole orbit space up to the top shell.
Non-flat rows have M from 3 to 36. The 7 flat rows have weights 1, 3, 2, 3, 3, 2, 4, which sum to 18, the number of commuting
pairs in S₃. DERIVED: a reflection swaps the classes of (c, c) and (c, c⁻¹), of 2 states each, which gives the row of
weight 4. That is why the whole space has 8 flat orbits and this sector has 7.

### Rows rebuilt from the definition

MEASURED by [`verify_sample_rows.py`](verify_sample_rows.py), separately written from the store's builder. It derives S₃ from
permutations, the plaquettes from the lattice and the symmetries from reflections and translations, then rebuilds each row's
weight, M and entries from the 3·nl moves. Every row matches on 2×2 (211) and 2×3 (2,646), and 2,250 sampled rows match on
3×3, including the tightest row, across three sector files. Its 14 damage controls all exit 2.

On 3×4, an outside seat replayed it on GitHub Actions, [run 41441400030](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41441400030), from the public data on a fresh runner: 2,564 of
2,564 rows match, including the tightest row 44,742,735 and all 3 rows at M = 3, and the merkle recomputed from the download
matches. A local run, [`VERIFY34.hbp`](VERIFY34.hbp), matched 4,264 of 4,264 rows, with at least 88 from every one of the 34
sectors. The same seat's [run 41444444894](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41444444894) matched 5,556 of 5,556 rows across all 34 sectors, with 385,827 exact weighted
pairs w_h·z_hj = w_j·z_jh. These are samples of the 45,508,080 rows. On all rows, the same run's `check_d_strict.py` passes row sums,
the key table and W-self-adjointness.

**All 45,508,080 rows.** MEASURED by `second-seat/fullrebuild.rs`, written by the second seat: every row recomputed from the rules and compared with the store, 0 mismatches in canonical key, weight, M or entries, and merkle PASS, in 7,870 s, as predicted in writing first: [`FULLREBUILD-3x4.out`](FULLREBUILD-3x4.out) and [`FULLREBUILD-RUN.hbp`](FULLREBUILD-RUN.hbp). [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md), section 5, has its scope.

**All 1,632,625,631 off-diagonal pairs.** MEASURED by [`allpairs`](../../../crates/evolvers/src/bin/allpairs.rs): w_h·z_hj = w_j·z_jh on every pair in exact integers, 0 mismatches and 0 unpaired entries, with merkle PASS on each of 4 passes, in 2,704 s, as predicted in writing first: [`allpairs/ALLPAIRS-3x4.out`](allpairs/ALLPAIRS-3x4.out) and [`allpairs/ALLPAIRS-RUN.hbp`](allpairs/ALLPAIRS-RUN.hbp). The same section has its scope and its controls.

### The bound on 3×4

MEASURED on the store, with its merkle checked on every pass. The solve started from d = 0 at threshold 93 J_E and ran
12 full passes with `PERRONCERT_INNER=16:200`, in 10,055 s:

    t_cert = 93.061051 J_E, tightest row 44,742,735, M = 3, 0 positive off-diagonal entries

Two checks on the same `d`, SHA-256 `956b73bc…`, each one more full pass over the store:

| Checker | Result | Time |
|---|---|---|
| `perroncert check` | same value, row and M | 628 s |
| `check_d_stream.py`, separately written Python, same author | same value, row and M | 1,863 s |
| `check_d_strict.py` on another machine, run by an outside seat, [run 41444444894](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41444444894) | same value, row and M, with row sums, the key table and W-self-adjointness passing on all rows | 2,038 s |

An external review found that `check_d_stream.py` relies on `assert`, which `python -O` removes. MEASURED: under `-O`, a
changed byte printed `merkle=PASS` with exit 0. The recorded run used `python -I`, so its row stands. The fail-closed
replacement is [`check_d_strict.py`](check_d_strict.py), with its controls in [`STRICT-CONTROLS.hbp`](STRICT-CONTROLS.hbp),
and it also checks every row's structure. The outside run above used it.

The predictions were committed in `155acdd` before the run:

| Prediction | Result |
|---|---|
| The solve at 93 J_E stays bounded | Met. The largest change in `d` fell from 66,654 at pass 6 to 15 at pass 12 |
| `t_cert` ≥ 93 J_E within 15 full passes | Met. It was already 93.061053 at pass 6 |
| The tightest row has low M | Met, M = 3 |
| λ₁(H′) lies in [93.9, 94.13] J_E | Met, by a later bracket: 94.070673 ≤ λ₁(H′) ≤ 94.070936. This run alone showed λ₁(H′) ≥ 93.061 |
| About 2.7 hours with the disk idle | 2.79 hours |

The rule draft's stop conditions all stayed clear, and `t_cert` sits below the rigorous upper limit E₈(+,+) ≤ 94.6.

Section 2 and the upper side then give, on this lattice, E₉ − E₈ ≥ 21.061051 + 3(r − 9) J_E for every r ≥ 9, and
E₉ − E₈ ≥ 23.030051 J_E at r = 9, subject to the open items in section 4.

### The bound raised the same day

MEASURED by `perroncert check` and `check_d_strict.py`, which agree on value, row and M, with all structure checks passing, on the vector `x3-c.bin`, SHA-256 `f5c5428d…`:

    t_cert = 94.070673 J_E, tightest row 45,507,968, M = 3, 0 positive off-diagonal entries

It is a third divided difference of three solved vectors, one of them from a hosted climb: [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md). So on this lattice, subject to the open items below,

    E₉ − E₈ ≥ 22.070673 + 3(r − 9) J_E for every r ≥ 9,    E₉ − E₈ ≥ 24.039673 J_E at r = 9.

### 3×3 (+,+), n = 288,645, flat diagonal 54

MEASURED, each row one `perroncert solve` from d = 0 unless noted, on the final binary:

| Solve threshold | Sweeps | `t_cert` (J_E) | Tightest row |
|---|---|---|---|
| 60 | 60 | 64.349880 | M = 3 |
| 70 | 60 | 71.089439 | M = 3 |
| 72 | 80 | 72.652046 | M = 3 |
| 74 | 80 | 74.298793 | M = 3 |
| 75 | 80 | 75.156799 | M = 3 |
| 76 | 80 | 76.041088 | M = 3 |
| 76.4 | 80 | 76.295852 | M = 7 |
| 76.4 | 80, then 200 more | 76.403209 | M = 3 |
| 78 | stopped by itself at sweep 53 | none | |

**Warm starts with inner sweeps.** MEASURED, each from the saved vector for solve threshold 75, with
`PERRONCERT_INNER=12:200`, in [`warmcal33.sh`](warmcal33.sh):

| Solve threshold | Full passes | `t_cert` (J_E) | Tightest row |
|---|---|---|---|
| 76.2 | 10 | 76.221846 | M = 3 |
| 76.3 | 10 | 76.312729 | M = 3 |
| 76.4 | 10, and within 0.000007 by pass 4 | 76.404038 | M = 3 |
| 76.43 | 8 | **76.431504** | M = 3 |
| 76.5 | 8 | diverges, with a negative value | |
| 76.7 and 77 | | stops with an error | |

`perroncert check`, `check_d.py` and `check_d_stream.py` give the same 76.431504, row and M. Before `d` settles, the
value can fall below where it started: with plain sweeps at 76.4 it read 72.0 after two sweeps, starting from 75.157. So
a warm start writes to its own file and keeps the old vector.

**Where the level is.** CONJECTURE, from fits of 1/(t_cert − t) = a/(λ₁ − t) + b: a = 3.44 on 2×2, 5.79 on 2×3 and 12.05 on
3×3, where the fit gives λ₁ = 76.448. Extending a to 3×4, and taking the K = 5 ball level as a ceiling, gives
λ₁(H′) between about 93.82 and 94.12 J_E on 3×4.

- **Earlier full-space certificate, for comparison.** 8 levels below 71.9 J_E, from the full 10,097,891-state run.
  The Perron value is higher, from one sector's rows.
- **Three checkers.** `perroncert check`, `check_d.py` and `check_d_stream.py` give the same value on the same `d`:
  74.298793, same row, same M. The two Python files were written separately, in exact integers.
- **A changed byte.** One flipped payload byte makes `flatcomp --room` and `perroncert check` exit with an error and print
  no value.
- **Inner sweeps.** With low rows in RAM, 8 full passes reach the same 74.298793 that plain sweeps took 80 for, and
  12 passes at 76 give 76.041221. This changes only how d is found.

### The whole-space lift

MEASURED by `shellschur`, separate code from `perroncert`:

| Lattice | λ₁(H′), sector and whole space | Levels of whole-space H below it | E₉, whole space |
|---|---|---|---|
| 2×2 | same bracket, [46.466796, 46.468750] | 8 | [46.576171, 46.578124] |
| 2×3 | same bracket, [58.441406, 58.443359] | 8 (7 in the sector) | open |

### Sector balls against whole-space balls

MEASURED by script, in `PERRON-RESULT.hbp`. At K = 2 and K = 3 on 3×3, and K = 3 on 3×4, every sector level overlaps a
whole-space level at the same K, and exactly one whole-space level in the list is left over. That one sits inside the
cluster, which fits the single (−,−) flat state. Measuring its sector directly is open.

## 4. Open

| Step | Run that measures it |
|---|---|
| The vector at the top | Done to 0.000263 J_E of the level: 94.070673 by both checkers, and λ₁(H′) ≤ 94.070936 from the same store, in [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md). The hosted climb reached 94.058570 by both checkers, [run 41448187715](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41448187715) |
| E₉ itself on 3×4 | Interlacing leaves E₉ above λ₁(H′): by about 0.11 J_E on 2×2 and 0.02 on 3×3. The earlier CONJECTURE that λ₁(H′) ≈ 94.0 read low by 0.07. The cluster top of 70.03 plus 3×3's gap of 23.94 gives 93.97 |
| That the store's rows are H, on 3×4 | Done: `second-seat/fullrebuild.rs` recomputed all 45,508,080 rows from the rules, with 0 mismatches and merkle PASS, as predicted in writing first: [`FULLREBUILD-3x4.out`](FULLREBUILD-3x4.out). Earlier: three samples, with 385,827 exact weighted pairs. Open: a replay on another machine |
| W-self-adjointness of the stored rows, on 3×4 | Done: `allpairs` compared all 1,632,625,631 off-diagonal pairs exactly, 0 mismatches, as predicted in writing first: [`allpairs/ALLPAIRS-3x4.out`](allpairs/ALLPAIRS-3x4.out). Open: a second seat's review and a replay on another machine |
| A checker written by someone else | Done: an outside seat's Go checker, from the formats in [`PERRON-REVIEW.md`](PERRON-REVIEW.md), prints 94070673, row 45,507,968, M = 3, as predicted, with its merkle, hash, row-sum and self-adjoint checks passing, [run 41509351749](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41509351749). [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md), section 5, has its values and its scope, and section 7 what stays open on it |
| The argument itself | Three reviewers accept it on reading, with the lift conditional on the row check, now done on all rows. A second seat attacked the new tools and the lift with its own whole-space builds on 2×2 and 2×3, and refuted no printed bound: [`REVIEW-OPUS55.md`](REVIEW-OPUS55.md) |
| A verdict by this route | A rule revision and the operator's word: [`PERRON-RULE-DRAFT.md`](PERRON-RULE-DRAFT.md) |
| Uniformity in volume, and the continuum limit | Separate obligations. Each result here is a statement about one finite lattice |
