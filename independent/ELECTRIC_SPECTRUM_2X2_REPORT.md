# The electric spectrum of the periodic 2×2 S₃ torus, and gap(E) = 6

**November 3, 2026.** Scope: the 1,393 gauge-invariant orbits of the periodic 2×2 S₃ torus at J_B = 0, and the every-ratio bound on that same torus. Integer only, `float_used=0`. Receipts are HBP rows in [`electric_spectrum_2x2.measure`](electric_spectrum_2x2.measure), 330 rows, all `json=0`. The section on the formula gap(E) = 3·min(4, Lx, Ly) covers every periodic torus, with its receipt in [`electric_gap_formula.measure`](electric_gap_formula.measure), 80 rows. A second seat attacked this report at head `689d85d` with the verdict not refuted. Its evidence is in [`reviews/opus55-electric-gap/`](reviews/opus55-electric-gap/README.md), and its findings are applied below, dated November 3.

## Result

The torus has 8 links and 4 vertices, each vertex 4-valent, and its graph is a 4-cycle with doubled edges. E = Σ_links (3 − Σ_t R_t), with t over the 3 transpositions.

**Eigenvalue 0 is simple, nothing lies strictly between 0 and 6, and 6 has multiplicity 4. So gap(E) = 6 exactly.**

The whole spectrum, MEASURED. Each engine count is read at a T between that cost and the next, with T in thousandths.

| Cost c | m[c] | Eigenvalues up to c | Engine read at T | Sectors pp, pm, mp, mm |
|---:|---:|---:|---:|---|
| 0 | 1 | 1 | 1700, 4700, 5999 | 1, 0, 0, 0 |
| 6 | 4 | 5 | 6001, 7700 | 3, 1, 1, 0 |
| 12 | 34 | 39 | 13700 | 15, 8, 8, 8 |
| 15 | 40 | 79 | 16700 | 25, 18, 18, 18 |
| 18 | 176 | 255 | 20950 | 75, 61, 61, 58 |
| 21 | 192 | 447 | 23300 | 123, 109, 109, 106 |
| 24 | 499 | 946 | 24300 | 262, 227, 227, 230 |
| 27 | 192 | 1,138 | 27050 | 310, 275, 275, 278 |
| 30 | 176 | 1,314 | 31700 | 360, 318, 318, 318 |
| 33 | 40 | 1,354 | 34700 | 370, 328, 328, 328 |
| 36 | 34 | 1,388 | 37700 | 382, 335, 335, 336 |
| 42 | 4 | 1,392 | 43700 | 384, 336, 336, 336 |
| 48 | 1 | 1,393 | 48500 | 385, 336, 336, 336 |

Costs 3, 9, 39 and 45 have multiplicity 0. The multiplicities sum to 1,393, the Burnside count (6⁵ + 3·2⁵ + 2·3⁵)/6.

## Why this count

GPT-6's [review of the every-ratio theorem](GPT6_THEOREM_REVIEW_2026-11-03.md) says of the bound's one named input:

> The exact gap(E)=6 remains an explicit antecedent supplied by earlier native spectral work, not a new independent certificate.

[Stage 2C](../STAGE2C_TORUS_1393_SPARSE_REPORT.md) reached the value by the per-link eigenvalues and one verified eigenmode. This track counts it three ways, on matrices from GPT-6's builder and from the separate seat's builder.

| Route | Matrix from | Method | Reads | Tag |
|---|---|---|---|---|
| 1 | [`gpt6_2x2_from_permutations.py`](gpt6_2x2_from_permutations.py), operator SHA-256 `b6c608f5…` | P(E) = 0, exact, on all 1,393 basis vectors, with the 13 costs as the roots of P. Each P/(x − c) at E is nonzero. The multiplicities are read back from traces | 0 with multiplicity 1, 6 with multiplicity 4, and no eigenvalue between | MEASURED |
| 2 | The same, in four translation sectors | GPT-6's interval Sturm engine, unchanged, at 16 thresholds | 1 at 1.7, 4.7, 5.999. 5 at 6.001, 7.7 | MEASURED |
| 3 | [`indep_verify.py`](../native/ym/independent/indep_verify.py), the full 1,393-dimensional matrix | Signs of leading minors through the Rust kernel, by CRT past the Hadamard bound of 39,006 bits | N = 1 at 5.999, N = 5 at 7.7 | MEASURED |

The conclusion from these rows is DERIVED, with its steps under path F.

## The derivation

**One link.** By Peter–Weyl, L²(S₃) splits over the irreps ρ into V_ρ ⊗ V_ρ*. The class sum Σ_t R_t acts on V_ρ by 3χ_ρ(t)/χ_ρ(e). So 3 − Σ_t R_t has cost 0 on the trivial irrep, 6 on the sign, and 3 on the 2-dimensional standard irrep τ, with dimensions 1, 1 and 4. Path A measures this on the 6×6 matrix.

**The spectrum lies in 3Z.** Let A_l be 3 − Σ_t R_t on link l. Each satisfies A_l(A_l − 3)(A_l − 6) = 0. Operators on different links act on different tensor factors, so they commute. Σ_t R_t commutes with conjugation, so A_l preserves gauge-invariant functions. E = Σ_l A_l. Commuting diagonalizable operators diagonalize together, so every eigenvalue of E is a sum of 8 values in {0, 3, 6}, and lies in 3Z ∩ [0, 48]. DERIVED. The same facts are MEASURED on the 1,393 matrix in `ELECTRIC_C_LINKS`: the 8 link matrices sum to E on 1,393 of 1,393 rows, 28 of 28 pairs commute, and 8 of 8 satisfy the cubic.

**Vertices.** The gauge-invariant states of an assignment of irreps to links number the product over vertices of dim Inv, with dim Inv = (χ(e)-product + 3 χ(t)-product + 2 χ(c)-product)/6. All irreps of S₃ are real, so link orientation is free. At a 4-valent vertex with k ends in τ and s ends in the sign:

| k | dim Inv |
|---:|---|
| 0 | 1 for s even, 0 for s odd |
| 1 | 0 |
| 2 | 1 |
| 3 | 1 |
| 4 | 3 |

**The low costs.** Cost 3 needs one τ, which leaves a vertex with k = 1, so m₃ = 0. Cost 6 is either one sign, which leaves a vertex with k = 0 and s = 1, or two τ. Two τ need the same two endpoints, so they sit on the two parallel links of one doubled edge. That gives one state on each of the 4 doubled edges, m₆ = 4, each a length-2 Wilson loop χ_τ(U_a U_b). Cost 9 is either three τ, which would need a triangle or three parallel links, or one sign and one τ, which has k = 1. The graph is bipartite with at most 2 parallel links, so m₉ = 0.

**Sectors.** Translation in x fixes each x-pair loop and swaps the y-pair loops. Translation in y does the reverse. So the x-pair loops span (+,+) and (+,−), and the y-pair loops span (+,+) and (−,+). With the constant, pp = 3, pm = 1, mp = 1, mm = 0. `ELECTRIC_C_LOOPS` measures this by exact rank.

**Reflection.** S = Π_l sgn(U_l) is gauge invariant, since each vertex has 4 ends, and each link move flips it. So S E S = 48 − E, and m[c] = m[48 − c]. `ELECTRIC_C_REFLECTION` measures it on 1,393 of 1,393 rows.

The hand count of the full table from the vertex rule was written into the prediction before any run. The file holds 34 at cost 12, 40 at cost 15, 176 at 18, 192 at 21 and 499 at 24, and the runs equal it. The split 34 = 4 + 30 is confirmed by count: 2 sign links carry 4 states, 4 τ links carry 30, and 1 sign link with 2 τ links carries 0, in `ELECTRIC_G_SPLIT`.

## The paths

The code is [`electric_spectrum_2x2.py`](electric_spectrum_2x2.py), one mode per path. Each exits 1 at the first check that fails.

**A, one link.** `a`. A = 3I − Σ_t R_t, from the multiplication table. A(A − 3)(A − 6) = 0 exact, and each product of two of the factors is nonzero. Ranks 5, 2, 5 give multiplicities 0×1, 3×4, 6×1 by exact fraction-free elimination.

**B, characters.** `b`. All 3⁸ = 6,561 assignments on 2×2, 865 with states, total 1,393. All 3¹² = 531,441 assignments on 2×3, 21,489 with states, total 47,449, and low table m₀ = 1, m₃ = 0, m₆ = 3, m₉ = 2, with m₇₂ = 1 at the top.

**C, the real matrix.** `c`. The builder runs through `runpy` and its pin matches. P(x) = Π(x − c) over the 13 costs from B. P(E) applied to each of the 1,393 basis vectors gives 0 in every entry. For each c, P/(x − c) at E gives a nonzero entry, recorded as `ELECTRIC_C_WITNESS`, so P is the minimal polynomial and every listed cost is an eigenvalue. trace(E) = 33,432 = Σ c·m[c]. trace(E²) = 838,512 = Σ c²·m[c]. The traces of the 14 prefix products of P form a triangular system, and solving it gives the multiplicities from the matrix alone: `0:1,6:4,12:34,15:40,18:176,21:192,24:499,27:192,30:176,33:40,36:34,42:4,48:1`, equal to the character table.

**D, inertia counts.** GPT-6's [`gpt6_sturm_sectors.py`](gpt6_sturm_sectors.py) and [`gpt6_sturm_interval.py`](gpt6_sturm_interval.py), byte-identical to main, at (J_E, J_B) = (1, 0). The four sector matrices match their SHA pins. All 16 certified rows read the cumulative table, with `ambiguous=0`. T = 6000 sits on the eigenvalue: exit 1, no `GPT6_STURM` row, `no sign-definite pivot: UNCERTIFIED`, stopping in the first sector. It is recorded as `ELECTRIC_D_SINGULAR`.

**E, the second engine.** `INDEP_MINORS=…/indep-minors.exe WORKERS=3 python3 -X utf8 indep_verify.py 2 2 0 5999000,7700000`, from `native/ym/independent`. N = 1 and N = 5, 641 primes of 62 bits, 0 reshuffles, 2,748 s at below-normal priority. The kernel's hash is in `INDEP_RUN`. Its build's dependency file names `native/ym/independent/minors/src/main.rs`, and that file's blob is the one on main, recorded in `ELECTRIC_E_RUN`.

Beside this, November 3. The priority of the runs of paths D and E is `NOT_MEASURED|reason=NOT_REACHABLE_FROM_HERE`: `lane=local_below_normal` in their rows is a literal in the assembler, and the launcher left no record. The second seat's own engine runs were at below-normal priority, confirmed by process class.

**F, the conclusion.** `f MEASURE` reads the pinned rows and prints each step. It fails on a missing or changed row. Since November 3 its required rows also hold the code hash and the kernel hash in `INDEP_RUN`, the same code hash in the `ELECTRIC_ENGINE` row of `indep_verify.py`, and the source blob in `ELECTRIC_E_RUN`, each at its pinned value.

1. From path A and `ELECTRIC_C_LINKS`, the spectrum of E lies in 3Z ∩ [0, 48].
2. From D at T = 1700, 4700, 5999 and E at 5.999, exactly one eigenvalue lies below each T. Every row of E sums to 0, so the constant is in the kernel and is that eigenvalue. So 0 is simple and 3 is absent.
3. From D at T = 6001, 7700 and E at 7.7, the count is 5. So 4 eigenvalues lie in [5.999, 6.001), and step 1 leaves only 6 there. So m₆ = 4.
4. So gap(E) = 6 exactly.
5. Routes 1 and 2 share the matrix and differ in method. Route 1 reaches the same conclusion from P(E) = 0 and the traces of its prefix products alone.
6. Each of the 13 gaps, between consecutive costs and above the top, holds a certified T, and all 16 counts equal the cumulative table. MEASURED.

**G, the formula.** `g FOLDER`, added on November 3, in the section on the formula below.

## The every-ratio bound on this torus

`same` runs [`seat_global_coupling.py`](seat_global_coupling.py) and compares what it holds. Its rows, weights and magnetic diagonal equal GPT-6's on 1,393 of 1,393 rows. Every diagonal is 24, the graph diameter is 8, and its bound function equals 6/(24 + 12r)¹⁶ exactly at r = 0, 1, 2, 10. So it uses this same E in this same normalisation.

**The finite statement.** For every J_E > 0 and J_B ≥ 0, on the 1,393-state periodic 2×2 S₃ torus,

gap(J_E E + J_B M) ≥ 6 J_E / (24 + 12 J_B/J_E)¹⁶ > 0.

GPT-6 read the analytic argument as PASS with gap(E) = 6 as its one named antecedent, and that antecedent is what this report counts. DERIVED. At J_B = 0 the exact gap is 6 J_E, and the bound there reads 6 J_E/24¹⁶.

## The prediction and what happened

Each file was pushed before the runs it predicts, and the workflow checks each stands as committed.

Beside this, November 3. The push times come from GitHub's activity feed and the run times from the run folder, read by the second seat and read again by the unit applying its findings. MEASURED for paths C, D and E: `2e7afed` pushed at 19:39:40Z with the first run file at 19:45:35Z, `4ee2845` at 20:04:06Z with its first T at 20:04:14Z, and `ea23e31` at 20:12:13Z with its first T at 20:12:21Z. Paths A and B survive on disk as re-runs from 20:24Z, so their first run time is `NOT_MEASURED|reason=NOT_REACHABLE_FROM_HERE`. Git order holds for all five: the three prediction commits come first, and the script arrives in `056de0f`. The workflow step checks ancestry and bytes, and its name now says so.

| File | Commit | Holds |
|---|---|---|
| [`ELECTRIC-SPECTRUM-2X2-PREDICTION.hbp`](ELECTRIC-SPECTRUM-2X2-PREDICTION.hbp) | `2e7afed` | The brief's rows, and the full table, traces and cumulative counts worked by hand |
| [`ELECTRIC-SPECTRUM-2X2-RETRY-PREDICTION.hbp`](ELECTRIC-SPECTRUM-2X2-RETRY-PREDICTION.hbp) | `4ee2845` | Replacement T after the first four stops |
| [`ELECTRIC-SPECTRUM-2X2-RETRY-PREDICTION-2.hbp`](ELECTRIC-SPECTRUM-2X2-RETRY-PREDICTION-2.hbp) | `ea23e31` | A second list for (18, 21) and (27, 30), the fourth sector's count, and the mirror rule |

`predictions` reads every row against the receipt, with a three-valued verdict. **53 rows: 47 MET, 0 MISS, 6 NOT_MEASURED.** Each count the engines returned equals its prediction. The six are places where a registered T produced no count:

| ID | Registered | Happened |
|---|---|---|
| D9 to D12 | Counts 255, 447, 946, 1,138 at T = 19700, 22700, 25700, 28700 | The engine stopped closed at each, so no count at these T. Replacement T in the same open intervals read the predicted counts |
| R1, R4 | 8 further T in each of (18, 21) and (27, 30) | The engine stopped closed at all 16. S1 and S2 then certified T = 20950 and T = 27050, with 255 at 75, 61, 61, 58 and 1,138 at 310, 275, 275, 278, as registered |

Correction, November 3. The second seat found that `predictions` read a wrong value as NOT_MEASURED on 14 of its 24 needle rows: A1, A2, A3, B1, B2, B3, B4, C1, C2, C3, C4, C5, C6 and F1. Each needle row now has a head, which names the receipt row up to its value. A row with that head and a changed value reads MISS. A receipt with no such row reads `NOT_MEASURED|reason=NO_ROW`. The 53 rows on this receipt are byte-equal to the pinned ones, so 47 MET, 0 MISS, 6 NOT_MEASURED stands, and the red controls are under Replay. Its probe, rerun on the fixed script, reads MISS on 23 of the 24. It reads MET on D4, where it appends a character and leaves the needle as a substring, as its report says, and a changed `sturm_rows` at D4 reads MISS in the controls.

## Where the engine stops

The engine stopped closed at 26 of the 42 thresholds off the spectrum, all between 18 and 30, each with `no sign-definite pivot: UNCERTIFIED`. Every attempt is in the receipt, with its certified sectors.

| Open interval | Stops | Certified at |
|---|---:|---:|
| (18, 21) | 14 | 20950 |
| (21, 24) | 2 | 23300 |
| (24, 27) | 1 | 24300 |
| (27, 30) | 9 | 27050 |

Two facts, each with its tag. At non-integer T the exact pivots are nonzero: a principal minor of W(E − T) is det W times the characteristic polynomial of an integer matrix at T, and a monic integer polynomial has only integer rational roots. DERIVED. So these stops read the width of the enclosure at the engine's 40 digits, its command-line default. CONJECTURE, as the width was left unmeasured.

Beside this, November 3, MEASURED by the second seat at 5 of the 26 stopped thresholds, local: GPT-6's engine, sha `6d7353ff…`, called through its own `run()` with a digits argument. Each of these T stops at 40 digits and certifies with more.

| T | Digits | Reads | Sectors pp, pm, mp, mm |
|---:|---|---:|---|
| 18300 | 120 | 255 | 75, 61, 61, 58 |
| 19700 | 60, 80, 120, 200 | 255 | 75, 61, 61, 58 |
| 22700 | 80, 120 | 447 | 123, 109, 109, 106 |
| 25700 | 80, 120 | 946 | 262, 227, 227, 230 |
| 28700 | 80, 120 | 1,138 | 310, 275, 275, 278 |

So at these 5 T the stop reads the enclosure width at 40 digits. They include all four registered thresholds D9 to D12, each at its predicted count. The rows D9 to D12 stay `NOT_MEASURED`, as the registered run is the engine's command line at 40 digits. The other 21 stops keep the CONJECTURE. Log: [`engine_digits_runs.log`](reviews/opus55-electric-gap/engine_digits_runs.log). The applying unit repeated T = 19700 at 60 digits through the filed driver and read the same row.

The two intervals (18, 21) and (27, 30) behave as one, since B(48 − T) = −S B(T) S and S is a diagonal of signs. Of the T run on both sides, 9 of 9 pairs stop alike with complementary sector counts, as registered in S3. MEASURED. Every threshold off the spectrum below 18 and above 30 certified on its first run, including all of those the statement uses.

## The formula gap(E) = 3·min(4, Lx, Ly)

**DERIVED, retagged on November 3, for every periodic Lx × Ly S₃ torus with Lx, Ly ≥ 1.** The builder's rows stay as pinned: `ELECTRIC_B_FORMULA` reads `tested_on=2x2,2x3|tag=CONJECTURE`, and prediction row B11 reads `tag=CONJECTURE`. The second seat proposed the argument, and the unit applying its findings checked it with mode `g`, in [`electric_gap_formula.measure`](electric_gap_formula.measure).

The states of E sit on assignments of irreps to links, and the cost of an assignment is the sum of its link costs, as in the derivation above. Take an assignment with at least one state, and let S be its set of nontrivial links.

1. At a vertex, one τ end has no invariant, with any number of sign ends beside it, and an odd number of sign ends with no τ end has none. So S has degree at least 2 at every vertex it touches, with a loop counted twice.
2. A nonempty finite set of links with that property holds a cycle, since a set with no cycle is a forest and a forest has a vertex of degree 1. So S has at least girth links, where girth is the length of the shortest cycle of the torus multigraph. A loop is a cycle of length 1, and two parallel links are a cycle of length 2.
3. Each nontrivial link costs at least 3, so every nonzero cost is at least 3·girth.
4. τ on a shortest cycle, with the trivial irrep elsewhere, has k = 2 at each vertex of the cycle and dim Inv = 1 there, so it has one state, at cost 3·girth. So gap(E) = 3·girth. The all-trivial assignment has one state and is the only one at cost 0, so 0 is simple.
5. The girth of the torus multigraph is min(4, Lx, Ly). With min(Lx, Ly) = 1, a link along the side of length 1 is a loop. With min(Lx, Ly) = 2, every link joins two distinct sites, and the two links between neighbours along the side of length 2 are parallel. With min(Lx, Ly) = 3, every site has 4 distinct neighbours, which rules out loops and parallel links, and a line along the side of length 3 is a cycle. With min(Lx, Ly) ≥ 4, every site has 4 distinct neighbours, and a cycle of length 3 would need its steps to cancel in each direction, since each side is longer than 3. That takes an even count of steps in each direction, against 3 odd. A plaquette is a cycle of length 4.

One more consequence. At cost 3·girth, S has exactly girth links, all τ, so S is one shortest cycle. So m at the gap is the number of shortest cycles: the 4 doubled edges on 2×2, the 6 lines of length 3 on 3×3, and the 16 plaquettes with the 8 lines of length 4 on 4×4.

Mode `g` checks these steps, MEASURED:

| Row | Scope | Reads |
|---|---|---|
| `ELECTRIC_G_VERTEX` | All 81 tuples of irreps at a vertex | dim Inv depends on k and s alone, with one τ end at 0 and odd sign ends with no τ at 0 |
| `ELECTRIC_G_GIRTH` | Every Lx, Ly from 1 to 12 | The shortest cycle, found by removing each link and taking the shortest path between its ends, equals min(4, Lx, Ly) on 144 of 144 |
| `ELECTRIC_G_TORUS` | Every Lx, Ly from 1 to 6, with 3×7, 4×7, 5×7, 6×7, 7×7 and 8×8 | Every assignment of cost up to the formula, 12,066,273 of them on 8×8: 0 states between 0 and the formula, and m at the formula equal to the number of shortest cycles, on 42 of 42 tori |

The second seat's 28 tori, by its own character path, with its own incidence and character table. MEASURED, local, and replayed in the workflow. Each reads the formula, and each m equals `ELECTRIC_G_TORUS`, on 28 of 28 rows of `ELECTRIC_G_SECOND_SEAT`:

| Gap | Full table with Burnside and reflection closure, m at the gap in brackets | Table truncated at cost 15, m at the gap in brackets |
|---:|---|---|
| 3 | 1×1 (2), 1×2 (2), 1×3 (3), 1×4 (4), 1×5 (5), 2×1 (2) | |
| 6 | 2×2 (4), 2×3 (3), 3×2 (3), 2×4 (4), 2×5 (5) | |
| 9 | 3×3 (6), 3×4 (4), 4×3 (4), 3×5 (5) | 3×6 (6), 3×7 (7) |
| 12 | 4×4 (24) | 4×5 (25), 4×6 (30), 4×7 (35), 5×5 (25), 5×6 (30), 5×7 (35), 6×6 (36), 6×7 (42), 7×7 (49), 8×8 (64) |

Its logs hold 21 of the 28. For the other seven, 1×1, 1×2, 1×4, 2×1, 2×4, 2×5 and 3×3, the readings are in its report, and the applying unit ran its filed script on them, into [`seven_tori_rerun.log`](reviews/opus55-electric-gap/seven_tori_rerun.log). That run reads 9 with m = 6 on 3×3 and 3 on 1×N and 2×1, as its report does, and 6 on 2×4 and 2×5.

## Replay

[`.github/workflows/electric-spectrum-2x2.yml`](../.github/workflows/electric-spectrum-2x2.yml), on hosted Linux, replays against the pinned rows: A, B, C, the same-operator check, F, the prediction check, and D at all 16 certified thresholds. Each of the 27 recorded stops replays as a stop. It checks the engines' hashes and the three prediction files against their commits. [Run 41715880472](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41715880472), on commit `188ec59` with Python 3.12.3, passed both jobs in full. The receipt was made on Python 3.13.14 on Windows, so the rows are the same on the two. Since November 3 the workflow also replays path G, checks the hashes of the second seat's files and replays its character path on its 28 tori. [Run 41739812762](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41739812762), on commit `c0e96bf` with Python 3.12.3, passed both jobs with these steps and the red controls below.

Red controls, each of which must exit 1 with its reason:

| Control | Reason it reports |
|---|---|
| An altered entry of E | `P_of_E_nonzero` |
| A dropped factor of P, c = 6 | `P_of_E_nonzero` |
| A wrong expected count at T = 4700 | `wrong independently measured inertia: expected 2 but saw 1` |
| A tampered sector matrix | `source matrix SHA mismatch` |
| An altered entry of the 6×6 matrix | `cubic_nonzero` |
| A wrong character of τ | `dim_inv_not_divisible_by_6` |
| A changed count in the receipt at T = 5999 | `missing_or_changed_row` |
| A changed count in the receipt at T = 23300 | `count_differs_from_the_table` |
| The certified row at T = 20950 removed | `a_gap_has_no_certified_T` |
| A spurious factor of P, c = 3, added November 3 | `factor_not_needed` |
| `INDEP_RUN` removed from the receipt, added November 3 | `missing_or_changed_row`, at `E_code` |
| A changed kernel hash in the receipt, added November 3 | `missing_or_changed_row`, at `E_kernel` |
| `ELECTRIC_E_RUN` removed from the receipt, added November 3 | `missing_or_changed_row`, at `E_kernel_source` |
| Path G with a wrong character of τ, added November 3 | `dim_inv_not_divisible_by_6` |
| Path G with the formula capped at 3, added November 3 | `girth_differs_from_the_formula`, at 4×4 |
| Path G with one τ end allowed at a vertex, added November 3 | `m_at_gap_differs_from_the_shortest_cycles`, at 1×2 |

The prediction check prints every verdict and exits 0, so a miss is recorded beside its row. Its controls, added November 3, read the verdicts:

| Control on the receipt | Verdict |
|---|---|
| A changed trace | C5 reads MISS, and C6 stays MET |
| The row of traces removed | C5 and C6 read NOT_MEASURED with reason NO_ROW |
| Changed rows at A, B, C, D and F | MISS at A2, A3, B3, B6, C1, D4 and F1 |
| A certified row added at T = 6000 | D4 reads MISS |

Path E stays a local receipt because of its cost, and F reads its rows.

To rerun on any machine:

```bash
python3 -I -X utf8 independent/electric_spectrum_2x2.py a
python3 -I -X utf8 independent/electric_spectrum_2x2.py b
python3 -I -X utf8 independent/electric_spectrum_2x2.py c
python3 -X utf8 independent/electric_spectrum_2x2.py same
python3 -I -X utf8 independent/electric_spectrum_2x2.py g independent/reviews/opus55-electric-gap
python3 -I independent/gpt6_sturm_sectors.py DIR
python3 -I independent/gpt6_sturm_interval.py DIR 1 0 T
```

[`electric_spectrum_2x2_assemble.sh`](electric_spectrum_2x2_assemble.sh) builds the receipt from one run folder.

## Open

- A non-author reading of `electric_spectrum_2x2.py`. GPT-6's builder and engine, and the separate seat's builder, came from other seats. Paths A, B, C and F are new code from this one. Beside this, November 3: the second seat read and attacked the script at head `689d85d`. A non-author reading of what came after it, path G and the heads of the prediction check, stays OPEN.
- The formula gap(E) = 3·min(4, Lx, Ly). CONJECTURE. The character path measures it at 2×2 and 2×3, where it reads 6. The branches at 3 and 4 are untested: 3×3 predicts 9 and 4×4 predicts 12. Beside this, November 3: retagged DERIVED in the section on the formula, where 3×3 reads 9 and 4×4 reads 12.
- The real matrix on 2×3. Path B counts by characters, and paths C, D and E ran on 2×2 only. Beside this, November 3, MEASURED by the second seat with its own gauge fixing, in [`real.rs`](reviews/opus55-electric-gap/real.rs) and [`real23.log`](reviews/opus55-electric-gap/real23.log): dim 47,449, nnz 1,726,321, and P(E) = 0 in checked i128 with the 23 character roots on 7,970 vectors, one per translation orbit, with `columns_nonzero=0`. The multiplicities read back from the prefix traces equal the character table, including m₆ = 3 and m₉ = 2, with costs 3 and 69 absent. Local, and its hosted replay stays OPEN.
- The bound at every ratio around this count. The Doob and Poincaré step stays a prose proof: GPT-6 read it as PASS and the second seat re-derived it line by line, and a machine check is OPEN. `seat_global_coupling.py` keeps its literal 6 and its row `electric_gap_antecedent=6`, tied to this count by the same-operator step of the workflow and by mode `c`.
- Larger lattices and the continuum.
