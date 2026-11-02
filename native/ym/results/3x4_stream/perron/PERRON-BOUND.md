# Perron lower bound on the level above the flat cluster (DRAFT, November 2, 2026)

This is a draft. It is not a registered rule, and it changes no threshold or gate. **The bound has not been run
on 3×4, and there is no 3×4 gap verdict.** No second seat has reviewed it. Every claim below is tagged MEASURED,
DERIVED (a short proof written here, not yet refereed) or CONJECTURE. The rows and hashes are in
[`PERRON-RESULT.hbp`](PERRON-RESULT.hbp).

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

Neither step needs d to be accurate. A poor d gives a weaker bound, never a false one. The solver is therefore
untrusted: the only thing checked is one exact integer pass over the rows, and that pass also verifies the
signs, the positivity of d and the store's merkle.

No Schur complement, core or interval arithmetic is involved. The cost is the number of passes the solver
wants plus one check pass, and memory is one integer per row.

## 2. From the sector to the whole space

**DERIVED.** Let X be all gauge orbits, and let G be the lattice symmetries that define the Sx+Sy+ sector.
G preserves H and maps flats to flats. Lift d from the sector by d̃(x) = d(rep x), with d̃ = 0 on flats. Each
sector row has one −1 per move into a target G-orbit, and its diagonal is 3·nl minus the moves that return to
the same orbit. Therefore

    (H′_whole d̃)(x) = J_B M(x) d̃(x) + J_E Σ_moves (d̃(x) − d̃(m·x)) = (H′_sector d)(rep x).

The ratios are the same at every x, so the same minimum bounds λ₁(H′_whole). Interlacing in the whole space,
with its 8 flat orbits removed, gives

    E₉(whole gauge-invariant space, all momenta and symmetry sectors)  ≥  min_h (H′_sector d)_h / d_h.

So one certificate on one sector's rows would bound the 9th level of the whole space.

**The gap.** The 8 flat orbits are mutually W-orthogonal, with diagonal 3·nl and no couplings between them
(`flatcomp`), so E₈ ≤ 3·nl J_E by min-max, for every r. M ⪰ 0, so E₉ cannot fall as r rises. A certificate
at r = 9 therefore gives

    E₉(r) − E₈(r)  ≥  t_cert − 3·nl    for every r ≥ 9, on that lattice.

At r = 9 alone, a tighter upper bound on E₈ can replace 3·nl, from a count on a whole-space ball. This is a
statement about one finite lattice. It says nothing about the infinite-volume limit.

## 3. Measured so far

### P0 on the 3×4 store

MEASURED. `flatcomp --room` on the store, merkle `ec03c5f8…` checked: 7 flat states, all diagonals exactly 72,
0 flat-flat couplings, as predicted before the run. This is the registered precondition P0, and it passed.

### The upper side on 3×4

MEASURED:

- **Whole-space flats.** `ball 3 4 1` then `flatcomp`: 8 flat states, all diagonals 72, 0 couplings. So E₈ ≤ 72
  for every r.
- **E₈ at r = 9.** On the K = 2 whole-space ball (8,042 states), 0 levels lie below 69.900 and exactly 8 below 70.036,
  counted by `shellschur`. By interlacing, E₈ ≤ 70.036 at r = 9.
- **E₈(+,+) from above.** On the sector balls, counted by `schurcert` on `shellschur`'s column rows: 7 below 96.7 and
  8 below 96.8 at K = 3; 7 below 94.5 and 8 below 94.6 at K = 4. So E₈(+,+) ≤ 94.6.
- **Ball levels.** The 8th (+,+) level of the K = 3, 4 and 5 balls is 96.756025, 94.562413 and 94.121950. K = 5 has
  441,946 states, and its ordering has not been confirmed by a count.

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
| 76.4 | 80, then 200 more | **76.403209** | M = 3 |
| 78 | stopped by itself at sweep 53 | none | |

- **Earlier full-space certificate, for comparison.** 8 levels below 71.9 J_E, from the full 10,097,891-state run.
  The Perron value is higher, from one sector's rows.
- **Above the level.** The solve at 78 diverges and certifies nothing.
- **Three checkers.** `perroncert check`, `check_d.py` and `check_d_stream.py` give the same value on the same `d`:
  74.298793, same row, same M. The two Python files were written separately, in exact integers.
- **A changed byte.** One flipped payload byte makes `flatcomp --room` and `perroncert check` print no result.
- **Inner sweeps.** With low rows in RAM, 8 full passes reach the same 74.298793 that plain sweeps took 80 for, and
  12 passes at 76 give 76.041221. This changes only how d is found.

### The whole-space lift

MEASURED by `shellschur`, which shares no code with `perroncert`:

| Lattice | λ₁(H′), sector and whole space | Levels of whole-space H below it | E₉, whole space |
|---|---|---|---|
| 2×2 | same bracket, [46.466796, 46.468750] | 8 | [46.576171, 46.578124] |
| 2×3 | same bracket, [58.441406, 58.443359] | 8 (7 in the sector) | not bisected |

### Sector balls against whole-space balls

MEASURED by script, in `PERRON-RESULT.hbp`. At K = 2 and K = 3 on 3×3, and K = 3 on 3×4, every sector level overlaps a
whole-space level at the same K, and exactly one whole-space level in the list has no sector partner. That one sits
inside the cluster, which fits the single (−,−) flat state. Its sector was not measured.

## 4. What is still to be measured

| Step that could fail | Run that measures it |
|---|---|
| The solver on 3×4: passes needed, and stability | `perroncert solve` on the 3×4 store, [`run_perron34.sh`](run_perron34.sh) |
| The level itself on 3×4 | CONJECTURE: λ₁(H′) ≈ 94.0 J_E. The cluster top of 70.03 plus 3×3's gap of 23.94 gives 93.97, and the ball levels above fall toward about 94.0 |
| That the check pass agrees across code on 3×4 | `check_d_stream.py` on the final `d` |
| The argument itself | A second-seat review. None has happened |

## 5. Not established

- The 3×4 gap, which has no verdict and no run behind it.
- Any infinite-volume statement. With the flat bound, t_cert − 3·nl shrinks as the lattice grows, because the bound
  ignores a vacuum shift that grows with volume (about nl/12 at r = 9).
- That this replaces the registered rule. Using it for a verdict needs a rule revision and the operator's word:
  see [`PERRON-RULE-DRAFT.md`](PERRON-RULE-DRAFT.md).
