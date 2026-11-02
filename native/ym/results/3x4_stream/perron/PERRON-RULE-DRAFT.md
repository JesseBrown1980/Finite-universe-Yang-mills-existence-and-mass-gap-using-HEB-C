# 3×4 gap rule by the Perron bound (DRAFT, not registered, not run)

This draft registers nothing and starts nothing. The registered rule,
[`GAP-VERDICT-RULE-3X4.md`](../GAP-VERDICT-RULE-3X4.md), stays in force and unchanged. If this draft is
approved, the operator's word adds it as a separate rule with its own sidecar. The derivation it relies on is
in [`PERRON-BOUND.md`](PERRON-BOUND.md).

## 1. What it would certify

With `t_cert` the value printed by `perroncert check` on the store below, for the whole gauge-invariant 3×4
space, all momenta and all symmetry sectors:

- **G1.** E₉ − E₈ ≥ `t_cert` − 72 J_E, for every r ≥ 9.
- **G2.** At r = 9, E₉ − E₈ ≥ `t_cert` − U, where U is the smallest measured t with whole-space
  N_ball(t) ≥ 8. MEASURED so far: U = 70.036 J_E, from K = 2 (`shellschur`, 8,042 states, `negative=8`).

Both are statements about this one finite lattice.

## 2. Inputs

| Input | Value |
|---|---|
| Store | 3×4 Sx+Sy+, n = 45,508,080, payload merkle `ec03c5f8…`, checked on every pass |
| Sector flats, P0 | MEASURED: 7 flat, diagonals all 72, 0 couplings |
| Whole-space flats | MEASURED, `ball 3 4 1` then `flatcomp`: 8 flat, diagonals all 72, 0 couplings |
| Coupling | `JE=1000 JB=9000`, so r = 9 |
| Solver | `perroncert solve`, solve threshold 93 J_E (`t_milli=93000000`), `PERRONCERT_INNER=16:200`, saving `d` after every sweep |

The solve threshold needs no multiple-testing guard. The bound is exact for any positive `d`, so a poor threshold
gives a weaker number, never a false one. It may be raised later by a warm start from a saved `d`.

## 3. Predictions, written before the run

All CONJECTURE until measured:

1. The solver at 93 J_E does not diverge.
2. `t_cert` ≥ 93 J_E within 15 full passes, and the tightest row has low M, as on 3×3.
3. The level λ₁(H′) lies in [93.9, 94.13] J_E. The upper end comes from the K = 5 sector ball, 94.121950. The
   lower end comes from 3×3's gap of 23.94 added to the cluster top of 70.03.
4. Local run time about 2.7 hours with the disk otherwise idle, about 3.7 hours while the exact verifier runs.

## 4. What stops it

No certified value is printed, or the run counts as FAIL with no verdict, if any of these occurs:

- a positive off-diagonal entry, a non-positive `d` on a non-flat row, a nonzero `d` on a flat row, or a merkle
  mismatch;
- `t_cert` above a rigorous upper bound on E₈(+,+) from a sector-ball count, which would mean the code or the
  argument is wrong;
- the separately written checker differing from `perroncert check` in any field it reports.

If the solver diverges, that gives no bound. It means only that 93 J_E is too high, and a lower threshold is
then chosen and recorded.

## 5. Before it counts as a verdict

1. `check_d_stream.py`, written separately, agrees with `perroncert check` on the final `d`, on the same store.
2. The `d` file and its SHA-256 are published, so anyone can re-check it in one pass over the public store.
3. A second-seat review of the derivation, including the whole-space lift.
4. The operator's word.

## 6. What it does not establish

- Anything about infinite volume. Here `t_cert` − 72 gives way as the lattice grows, because the flat bound
  ignores the vacuum energy shift.
- Anything below r = 9.
- It changes neither the 60M production result nor the registered V1 and V2 stages.
