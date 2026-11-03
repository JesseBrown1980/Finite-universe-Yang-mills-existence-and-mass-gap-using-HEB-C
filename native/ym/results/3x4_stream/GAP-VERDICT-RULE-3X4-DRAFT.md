# 3×4 gap-verdict rule: DRAFT revision 2 for operator approval (NOT REGISTERED)

Revision 2 (2026-11-01) applies three review corrections: E₇(+,+) ≤ 72, not E₈, with a non-strict bound; only 60M is admissible; production is gated on a committed, passed control receipt. Revision 1 is in this file's git history.

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
2. **Flat bound, in the (+,+) sector (corrected after review, 2026-11-01).** The 7 flat states of
   (+,+) are 7 independent trial states. If their electric diagonal is 3 × 24 = 72 J_E and their
   mutual couplings are 0, the min-max principle gives **E₇(+,+) ≤ 72 J_E**. It does **not** give
   E₈ ≤ 72. That needs an eighth independent trial state, the (−,−) flat state, with its own
   energy bound verified (V2). **Precondition P0:** `flatcomp` on the 3×4 (+,+) store must
   print `flat_states=7`, `flat_diag_max=72` and `flat_flat_couplings=0`, as it did for 3×3 (54 and
   0). Without P0 there is no verdict.

## 3. What t = 60M measures (and why it is not a gap verdict)

At t = 60 J_E, the hosted control and the spec's 137-column production measure
`N₊₊(60)`. On 3×3 the cluster sits near 52.5 J_E at r = 9. Scaled by links (24/18) it is
expected near 70 J_E on 3×4, so `N₊₊(60) = 0` is expected (CONJECTURE). A clean `0`
would certify **E₁(+,+) ≥ 60 J_E**, a vacuum-energy lower bound, not a gap. It is still
worth running: it is the cheapest production and it tests the whole pipeline.
Registered as `GAP_RULE_THRESHOLD|t_milli=60000000|role=vacuum_lower_bound_not_gap|`. This is the
**only** threshold line in this rule. 60M and the later gap certification are separate
deliverables.
`ambiguous > 0` or `negative > 0` at 60M is recorded as measured. It is not a FAIL: the 60
J_E expectation is a scaling estimate, not a registered bound.

## 4. Stage V1 rule: sector (+,+) only

- **Threshold ladder, fixed in advance:** `tB ∈ {76, 80, 84, 88}` J_E, run in increasing order.
- **Not admitted yet (review, 2026-11-01).** The ladder thresholds are written here
  **without** `GAP_RULE_THRESHOLD` lines, so the workflow cannot admit them. They become
  admissible only in a later revision of this rule, after the spec and workflow size the job
  matrix, memory admission and merge checks (core size, core fingerprint) from a measurement at
  that threshold, and that revision is verified.
- **At each ladder point** the merged `SHELL_SCHUR` row gives `negative` and `ambiguous`.
  - `negative = 7, ambiguous = 0`: the 8th (+,+) level is ≥ tB. Go to the next point.
  - `negative > 7, ambiguous = 0`: the 8th (+,+) level is < tB, so record that **upper** bound
    and stop the ladder.
  - `ambiguous > 0`: rerun the point with TOL = 100 (the spec's stage 2). If still ambiguous,
    the point is INCONCLUSIVE and the ladder stops.
  - `negative < 7`: contradicts E₇(+,+) ≤ 72 < tB and P0. **FAIL**, with no verdict.
- **V1 verdict.** With tB* = the largest ladder point that gave `7, 0`, and every lower
  ladder point also `7, 0`:
  **E₈(+,+) − E₇(+,+) ≥ tB* − 72 J_E** at r = 9. The inequality is non-strict: the count gives
  E₈(+,+) ≥ tB* and the flat bound gives E₇(+,+) ≤ 72. This is the gap above the (+,+) cluster in that
  one symmetry sector only. It is not the zero-momentum E₉ − E₈, and not the full-space gap.
- **Expected values (CONJECTURE, not used by the rule).** The gap law at r = 9 gives
  E₉ − E₈ ≈ 3r − 21/r ≈ 24.7 J_E. The 3×3 point value is 23.94. If the 3×4 cluster is near
  70, E₉ is near 94. Then every ladder point should give `7, 0`, and tB* = 88 would certify a
  sector gap ≥ 16 J_E.

## 5. Stage V2 rule: the zero-momentum gap E₉ − E₈ (needs three more stores)

As in 3×3, summed over the four C2v sectors: `N(tB) = 8`, with (+,+) = 7, (−,−) = 1,
(+,−) = 0 and (−,+) = 0, and `ambiguous = 0` in every sector. With E₈ ≤ 72, which needs the
eighth trial state (the (−,−) flat state, `flatcomp` on that store: `flat_states=1`,
`flat_diag_max=72`), this gives **E₉ − E₈ ≥ tB − 72** in the zero-momentum sector. It needs the (−,−), (+,−) and (−,+)
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

1. Control C1–C3 (running, run 41294035019). Production is admitted only against a
   **committed control receipt** with `C1=PASS`, `C2=PASS` and `C3=PASS`, pinned by run ID and SHA-256.
   Enforced by the workflow in PR #69, not yet on `main`. Until #69 is merged, the gate is
   **not enforced** and this rule must not be registered. The receipt is
   `native/ym/results/3x4_stream/control/CONTROL.hbp` plus `CONTROL-RECEIPT.hbp`
   (`CONTROL_RUN|run_id=<id>|…` and `CONTROL_SHA256|<sha256 of CONTROL.hbp>|`), with a
   `CONTROL-RECEIPT.sha256` sidecar. The run must contain the passed step "Control C1/C2 against the
   local pilot", and the committed `CONTROL.hbp` must be byte-identical to that run's own
   `fanout-control-0` artifact. On registration this
   rule gains one line, `CONTROL_RECEIPT_SHA256|<sha256 of CONTROL-RECEIPT.hbp>|`, which chains the
   receipt to the rule's own sha. GitHub must report that run as `success`. A control that is
   running or failed has no receipt, so it cannot satisfy the gate.
2. Production at t = 60M (137 columns, current spec). Expect `N = 0`.
3. P0 (`flatcomp` on the 3×4 (+,+) store).
4. A spec revision for core-sized job matrices, with the core size measured at 76M first.
5. Ladder V1, in increasing order.
6. V2 only after the three other sector stores exist.

Production HOLD is unchanged by this draft. There is no 3×4 gap verdict.
