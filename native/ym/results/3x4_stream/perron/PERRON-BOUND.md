# Perron lower bound on the level above the flat cluster (draft, November 2, 2026)

**On the 3×4 store the bound certifies 93.061051 J_E.** The verdict stays open until the steps in section 4 are done. Claims
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
3×3, including the tightest row, across three sector files. Its 12 damage controls all exit 2. Its 3×4 run is in progress,
here and on GitHub Actions.

### The bound on 3×4

MEASURED on the store, with its merkle checked on every pass. The solve started from d = 0 at threshold 93 J_E and ran
12 full passes with `PERRONCERT_INNER=16:200`, in 10,055 s:

    t_cert = 93.061051 J_E, tightest row 44,742,735, M = 3, 0 positive off-diagonal entries

Two checks on the same `d`, SHA-256 `956b73bc…`, each one more full pass over the store:

| Checker | Result | Time |
|---|---|---|
| `perroncert check` | same value, row and M | 628 s |
| `check_d_stream.py`, separately written Python, same author | same value, row and M | 1,863 s |

An external review found that `check_d_stream.py` relies on `assert`, which `python -O` removes. MEASURED: under `-O`, a
changed byte printed `merkle=PASS` with exit 0. The recorded run used `python -I`, so its row stands. The fail-closed
replacement is [`check_d_strict.py`](check_d_strict.py), with its controls in [`STRICT-CONTROLS.hbp`](STRICT-CONTROLS.hbp),
and it also checks every row's structure. Its 3×4 run is open.

The predictions were committed in `155acdd` before the run:

| Prediction | Result |
|---|---|
| The solve at 93 J_E stays bounded | Met. The largest change in `d` fell from 66,654 at pass 6 to 15 at pass 12 |
| `t_cert` ≥ 93 J_E within 15 full passes | Met. It was already 93.061053 at pass 6 |
| The tightest row has low M | Met, M = 3 |
| λ₁(H′) lies in [93.9, 94.13] J_E | Open. This run shows λ₁(H′) ≥ 93.061 |
| About 2.7 hours with the disk idle | 2.79 hours |

The rule draft's stop conditions all stayed clear, and `t_cert` sits below the rigorous upper limit E₈(+,+) ≤ 94.6.

Section 2 and the upper side then give, on this lattice, E₉ − E₈ ≥ 21.061051 + 3(r − 9) J_E for every r ≥ 9, and
E₉ − E₈ ≥ 23.030051 J_E at r = 9, subject to the open items in section 4.

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
| The solver on 3×4 at a higher threshold | A warm start at 93.7 J_E, [`run_warm34.sh`](run_warm34.sh). Its value counts after the same two checks |
| The level itself on 3×4 | CONJECTURE: λ₁(H′) ≈ 94.0 J_E. The cluster top of 70.03 plus 3×3's gap of 23.94 gives 93.97, and the ball levels above fall toward about 94.0 |
| That the store's rows are H, in general on 3×4 | [`verify_sample_rows.py`](verify_sample_rows.py) on the 3×4 store. All three reviewers ask for it |
| The arithmetic on another machine | Another seat's pass over the published `d` and store. A replay of the row rebuild is in progress: [`PERRON-REVIEW.md`](PERRON-REVIEW.md), section 4 |
| The argument itself | Three reviewers accept it on reading, with the lift conditional on the row check |
| A verdict by this route | A rule revision and the operator's word: [`PERRON-RULE-DRAFT.md`](PERRON-RULE-DRAFT.md) |
