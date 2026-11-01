# 3×4 gap-verdict rule: DRAFT for operator approval (NOT REGISTERED)

This is a draft. The fan-out workflow only accepts a rule at
`GAP-VERDICT-RULE-3X4.md` with a `.sha256` sidecar, so this file registers nothing and
starts nothing. If it is approved, it is copied to that name, unchanged except for the status
line.

It follows the rule the 2×L and 3×3 zero-momentum certificates already use
(`native/ym/python/volume_point.py`, `shell_gap_cert.py`), adapted to what the 3×4 store can
measure. It changes no count, threshold or gate already registered.

## 1. What the 3×3 rule does, and why 3×4 cannot copy it as-is

- **3×3 rule.** A block eigensolver gives intervals for the lowest levels in the four
  zero-momentum C2v sectors. Then `t1` = top of the 8 lowest + 2 and
  `tB` = ⌊E₉ lo / 1000⌋·1000 − 1000. The lowest 8 must be 7 in (+,+) and 1 in (−,−). The certificate
  is `N(t1) = 8`, `N(tB) = 8` summed over the four sectors, giving E₈ < t1 ≤ tB ≤ E₉.
- **3×4 gaps.** There is no 3×4 eigensolver run, so `t1` and `tB` cannot be set from
  intervals. Only the (+,+) sector store exists (`Sx+Sy+`, n = 45,508,080, 7 flat states). The
  (−,−), (+,−) and (−,+) stores have not been built.

## 2. Two facts this rule depends on

1. **Thresholds.** `t_milli` is in units where J_E = 1000 (`JE=1000`, `JB=9000`, so r = 9).
   `t_milli = 1,000,000 · t` for t in units of J_E.
2. **Flat bound.** E₈ ≤ 3 × (number of links) = 3 × 24 = **72 J_E** on 3×4 (the README's
   flat-state bound). In (+,+) this needs the 7 flat states' electric diagonal to equal 72 and
   their mutual couplings to be 0, as `flatcomp` showed for 3×3 (54 and 0). **Precondition
   P0:** `flatcomp` on the 3×4 (+,+) store must print `flat_states=7`, `flat_diag_max=72` and
   `flat_flat_couplings=0`. Without P0 there is no verdict.

## 3. What t = 60M measures (and why it is not a gap verdict)

At t = 60 J_E, the hosted control and the spec's 137-column production measure
`N₊₊(60)`. On 3×3 the cluster sits near 52.5 J_E at r = 9. Scaled by links (24/18) it is
expected near 70 J_E on 3×4, so `N₊₊(60) = 0` is expected (CONJECTURE). A clean `0`
would certify **E₁(+,+) ≥ 60 J_E**, a vacuum-energy lower bound, not a gap. It is still
worth running: it is the cheapest production and it tests the whole pipeline.
Registered as `GAP_RULE_THRESHOLD|t_milli=60000000|role=vacuum_lower_bound_not_gap|`.
`ambiguous > 0` or `negative > 0` at 60M is recorded as measured. It is not a FAIL: the 60
J_E expectation is a scaling estimate, not a registered bound.

## 4. Stage V1 rule: sector (+,+) only

- **Threshold ladder, fixed in advance:** `tB ∈ {76, 80, 84, 88}` J_E, that is
  `GAP_RULE_THRESHOLD|t_milli=76000000|`, `…80000000|`, `…84000000|`, `…88000000|`.
  Run in increasing order.
- **At each ladder point** the merged `SHELL_SCHUR` row gives `negative` and `ambiguous`.
  - `negative = 7, ambiguous = 0`: the 8th (+,+) level is ≥ tB. Go to the next point.
  - `negative > 7, ambiguous = 0`: the 8th (+,+) level is < tB, so record that **upper** bound
    and stop the ladder.
  - `ambiguous > 0`: rerun the point with TOL = 100 (the spec's stage 2). If still ambiguous,
    the point is INCONCLUSIVE and the ladder stops.
  - `negative < 7`: contradicts the flat bound and P0. **FAIL**, with no verdict.
- **V1 verdict.** With tB* = the largest ladder point that gave `7, 0`, and every lower
  ladder point also `7, 0`:
  **E₈(+,+) − E₇(+,+) > tB* − 72 J_E** at r = 9. This is the gap above the (+,+) cluster in that
  one symmetry sector only. It is not the zero-momentum E₉ − E₈, and not the full-space gap.
- **Expected values (CONJECTURE, not used by the rule).** The gap law at r = 9 gives
  E₉ − E₈ ≈ 3r − 21/r ≈ 24.7 J_E. The 3×3 point value is 23.94. If the 3×4 cluster is near
  70, E₉ is near 94. Then every ladder point should give `7, 0`, and tB* = 88 would certify a
  sector gap > 16 J_E.

## 5. Stage V2 rule: the zero-momentum gap E₉ − E₈ (needs three more stores)

As in 3×3, summed over the four C2v sectors: `N(tB) = 8`, with (+,+) = 7, (−,−) = 1,
(+,−) = 0 and (−,+) = 0, and `ambiguous = 0` in every sector. With the flat bound E₈ ≤ 72 this
gives **E₉ − E₈ > tB − 72** in the zero-momentum sector. It needs the (−,−), (+,−) and (−,+)
stores to be built (about 4 h each on the pass-B build), uploaded and controlled like (+,+).
**The full physical space** (all momenta) is a further stage, as on 3×3, and is not covered
by this rule.

## 6. What production costs at the ladder points (blocker for the current spec)

The current fan-out spec splits **137** core columns into 18 jobs. That core size is for
t = 60M. The core grows with t: on 3×3 it was 101 at 60M, 1,137 at 72M and 2,940 at 90M.
The 3×4 core at 76–88M is not measured. It is likely in the thousands, which means hundreds
of jobs per ladder point. **The job matrix in `PRODUCTION-FANOUT-SPEC.md` §2 must be
revised to compute its column count from the core size** before any ladder point runs.
Measuring the core size at each ladder point is cheap: it is printed in the setup pass.

## 7. Order

1. Control C1–C3 (running, run 41294035019).
2. Production at t = 60M (137 columns, current spec). Expect `N = 0`.
3. P0 (`flatcomp` on the 3×4 (+,+) store).
4. A spec revision for core-sized job matrices, with the core size measured at 76M first.
5. Ladder V1, in increasing order.
6. V2 only after the three other sector stores exist.

Production HOLD is unchanged by this draft. There is no 3×4 gap verdict.
