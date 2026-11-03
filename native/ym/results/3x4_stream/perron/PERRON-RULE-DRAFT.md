# 3×4 gap rule by the Perron bound (draft)

The registered rule, [`GAP-VERDICT-RULE-3X4.md`](../GAP-VERDICT-RULE-3X4.md), stays in force. If this draft is approved, the
operator's word adds it as a separate rule with its own sidecar. The derivation it relies on is in
[`PERRON-BOUND.md`](PERRON-BOUND.md).

**Note, November 3, 2026.** This draft stays on HOLD by the operator's word. Since it was written, the exact pair test `allpairs` was hardened and rerun on the full store (#85), and a separate route with no store reached 4×4 to 5×5 (#89), which this draft leaves out of its scope.

## 1. What it would certify

With `t_cert` the value printed by `perroncert check` on the store below, for the whole gauge-invariant 3×4
space, all momenta and all symmetry sectors, the gap above the eight flat states obeys:

- **G1.** E₉ − E₈ ≥ `t_cert` − 72 + 3(r − 9) J_E, for every r ≥ 9.
- **G2.** At r = 9, E₉ − E₈ ≥ `t_cert` − U, where U is the smallest measured t with whole-space
  N_ball(t) ≥ 8. MEASURED so far: U = 70.031 J_E, from K = 3 (`shellschur`, 155,386 states, `negative=8`).

Both are statements about this one finite lattice.

## 2. Inputs

| Input | Value |
|---|---|
| Store | 3×4 Sx+Sy+, n = 45,508,080, payload merkle `ec03c5f8…`, checked on every pass |
| Sector flats, P0 | MEASURED: 7 flat, diagonals all 72, 0 couplings |
| Whole-space flats | MEASURED, `ball 3 4 1` then `flatcomp`: 8 flat, diagonals all 72, 0 couplings |
| Coupling | `JE=1000 JB=9000`, so r = 9 |
| Solver | `perroncert solve`, saving `d` after every sweep. The first run solved at 93 J_E (`t_milli=93000000`) from d = 0, with `PERRONCERT_INNER=16:200`. A warm start at 93.7 J_E, with `PERRONCERT_INNER=16:500`, starts from that vector. The vector with the highest value so far is a third divided difference of three solved vectors: [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md) |
| Certificate | Any positive `d` is admissible. What counts is the value `perroncert check` prints for the published file, named by its SHA-256 |

The bound holds for any positive `d`, so a poor threshold simply gives a weaker number. The threshold may be raised by a
warm start from a saved `d`.

## 3. Predictions, written before the run

All CONJECTURE until measured:

1. The solver at 93 J_E does not diverge.
2. `t_cert` ≥ 93 J_E within 15 full passes, and the tightest row has low M, as on 3×3.
3. The level λ₁(H′) lies in [93.9, 94.13] J_E. The upper end comes from the K = 5 sector ball, 94.121950. The
   lower end comes from 3×3's gap of 23.94 added to the cluster top of 70.03.
4. Local run time about 2.7 hours with the disk idle, about 3.7 hours while the exact verifier runs.

These stand as written in `155acdd`. The results at 93 J_E are in [`PERRON-BOUND.md`](PERRON-BOUND.md), section 3.

## 4. What stops it

The run counts as FAIL, and prints no certified value, if any of these occurs:

- a positive off-diagonal entry, a non-positive `d` on a non-flat row, a nonzero `d` on a flat row, or a merkle
  mismatch;
- `t_cert` above a rigorous upper bound on E₈(+,+) from a sector-ball count, or above the side from above of `perronritz pass`, which would
  mean the code or the argument is wrong;
- the separately written checker differing from `perroncert check` in any field it reports.

A divergent solve means the threshold is too high, and a lower one is then chosen and recorded.

## 5. Before it counts as a verdict

1. A separately written checker agrees with `perroncert check` on the final `d`, on the same store: `check_d_stream.py` for
   the vector at 93 J_E, and `check_d_strict.py` from then on.
2. The `d` file and its SHA-256 are published, so anyone can re-check it in one pass over the public store.
3. A second-seat review of the derivation, including the whole-space lift.
4. Separate code rebuilding 3×4 rows from `passA.bin` and the definition of H, all of them by `second-seat/fullrebuild.rs`: done, 45,508,080 rows, 0 mismatches, [`FULLREBUILD-3x4.out`](FULLREBUILD-3x4.out). The
   whole-space statement counts after this step. Before it, the sector statement E₈(+,+) ≥ `t_cert` is the one in hand.
5. Another seat's pass over the published `d` and store, by a checker written by someone else: done, an outside seat's Go checker, [run 41509351749](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41509351749), with its scope in [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md), section 5.
6. The operator's word.
