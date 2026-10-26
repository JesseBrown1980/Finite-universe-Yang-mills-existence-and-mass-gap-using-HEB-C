# 3×3 full space at r = 9: stage B specification (frozen)

Fixed before any stage B count is read. Stage A (run 40381004053) is complete:
16 sectors cover the physical space, with the dimension reconciliation
1,122,211 + 4 × 2,243,920 = 10,097,891. This equals the Burnside count
(6¹⁰ + 3·2¹⁰ + 2·3¹⁰)/6.

## Thresholds

| Name | t (J_E) | t_milli | Role |
|---|---|---|---|
| t1 | 52.533422 | 52533422 | upper bound on E₈, from the zero-momentum r = 9 certificate |
| t_F | 71.900000 | 71900000 | full-space threshold, below the magnetic shell m = 8 at 72 J_E |

t_F replaces 76.472000 for the full space. Every full-space number below is
computed from t_F, and nothing is carried over from the zero-momentum
threshold 76.472000 or from its gap interval.

## Counts

- **What is counted.** For each of the 16 sectors, the negative count of
  W(1000(J_E E + J_B M)) − t W at t1 and at t_F (J_E = 1000, J_B = 9000; FDIG 12,
  TOL 1000).
- **How.** Run through hebc_ym_http0, split into countcols cells and joined by
  a strict countmerge wherever the core exceeds 100 rows.
- **Acceptance.** Every count must report ambiguous = 0 and result = PASS.

## Assembly

`python/full_space_mobius.py` turns the sector counts into a full-space count
N_full(t) by Möbius inversion over the line subgroups. It requires three
things:
- every isotypic count is nonnegative;
- the dimension reconciliation equals the gauge-orbit count;
- the symmetric lines agree: N(V^{K_x}) = N(V^{K_y}) and N(V^{K_d}) = N(V^{K_a}).
  These lines are computed independently, and their agreement is a cross-check.

The N-Nest gate runs on the assembled tree.

## Certificate arithmetic, fixed now

| Verdict | Outcome |
|---|---|
| PASS | (N_full(t1), N_full(t_F)) = (8, 8), with every gate below passing |
| MISMATCH | any other successfully computed and assembled pair |
| INCONCLUSIVE | any count AMBIGUOUS or failed, or any integrity or assembly gate failed |

**If PASS, at r = 9.** E₈ < t1, since E₈^full ≤ E₈^(zero momentum) < t1, and
E₉ ≥ t_F. So E₉ − E₈ > 71.900000 − 52.533422 = **19.366578 J_E** over the full
physical space.

**If PASS, for all r ≥ 9.** E₉(r) is non-decreasing in r (M ⪰ 0), so
E₉(r) ≥ 71.9. The flat trial space bounds E₈ ≤ 54: it has 8 states with M = 0,
electric diagonal 54 and zero flat–flat electric couplings (stage A flatcomp).
So E₉ − E₈ ≥ 71.9 − 54 = **17.9 J_E** for all r ≥ 9, over the full physical
space.

**If MISMATCH with N_full(t_F) > 8.** The count above 8 is the number of
states, at any momentum, below 71.9 J_E. It is reported along with the
isotypic parts that carry them. A full-space gap then needs lower thresholds
and a new specification.

**If MISMATCH otherwise**, for example (7, 7) or (7, 8): the pair is reported
as computed.

The certificate's scope is the full physical space of the 3×3 torus at
coupling r = 9, and for all r ≥ 9 through the one-point ray. Uniformity in
volume is the separate topological-stability route.
