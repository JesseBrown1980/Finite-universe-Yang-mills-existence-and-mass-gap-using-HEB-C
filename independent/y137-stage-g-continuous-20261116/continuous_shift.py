#!/usr/bin/env python3
"""Exact continuous-rational interval exclusion for Stage G Wilson shifts.

For every real alpha in [0,14], screen the EXISTING sufficient inequality
with the ORIGINAL certified upper state-error constants d1,d2. This does not
lower-bound the actual physical eigenstate error and proves no physical zero.

A cell [a/b,c/b] is excluded only when:
 d2 * min_cell ||(O-alpha)U1||_flat_lower
 + d1 * min_cell ||(O-alpha)U2||_flat_lower
   > max_cell |<U2,(O-alpha)U1>|_source_upper.
Quadratic flat scores minimized EXACTLY at their rational vertices or
endpoints. The sample upper is a convex, piecewise-linear function of alpha,
so its maximum on a closed interval is at one of its endpoints.
Every square-root lower is rounded DOWN, and every amplitude upper UP.
All arithmetic is integer-only. A middle interval is left INCONCLUSIVE.
"""
import hashlib
import os
import sys
from math import gcd, isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GATE = os.path.join(ROOT, "independent", "y137-stage-g-eight-flat-20261116")
sys.path.insert(0, GATE)
import flat_action_gate as g

GRID_REL = "independent/y137-stage-g-eight-flat-20261116/RESULT-STAGE-G-SHIFT-GRID-20261116.hbp"
GRID_BLOB = "903cbe1e9dd01e0052f60b6b350094368d58d67f"
GATE_BLOB = "3856180144eeb69b1361bc9ae341d5a6b45b80dd"
DEN = 1000000000
MAX_ALPHA = 14
DEPTH = 13


def need(ok, why):
    g.need(ok, why)


def ceildiv(n, d):
    need(n >= 0 and d > 0, "invalid_ceil_ratio")
    return (n + d - 1) // d


def blob(path):
    raw = open(path, "rb").read()
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii")
                        + b"\x00" + raw).hexdigest()


def simplified(n, d):
    need(d > 0, "bad_rational_denominator")
    z = gcd(n, d)
    return n // z, d // z


def floor_flat_cell(state, lo, hi, den, data):
    """Proven lower bound for minimum flat-action norm over the WHOLE cell."""
    p, s1, s2, q = data[state]
    # The minimum of p*alpha^2 - 2*s1*alpha + s2 is attained
    # at rational s1/p, clamped to the exact cell endpoints.
    if den * s1 < p * lo:
        a, b = lo, den
        score = p * a * a - 2 * s1 * a * b + s2 * b * b
        n = score * g.UNIT**4
        d = b * b * p * (g.UNIT**2 + q * q)
    elif den * s1 > p * hi:
        a, b = hi, den
        score = p * a * a - 2 * s1 * a * b + s2 * b * b
        n = score * g.UNIT**4
        d = b * b * p * (g.UNIT**2 + q * q)
    else:
        # score at its vertex = (p*s2 - s1*s1)/p.
        n = (p * s2 - s1 * s1) * g.UNIT**4
        d = p * p * (g.UNIT**2 + q * q)
    need(n >= 0 and d > 0, "invalid_exact_quadratic_cell")
    return isqrt(n // d)


def sample_upper(a, b, budget):
    """Directed upper bound on normalized signed sample amplitude, /10^12.

    Original #180 O2=2O-7 centred dual:
    C/DEN +/- E/DEN, signed original overlap V, error Eov/DEN.
    For O-alpha I use (O2+(7-2alpha) I)/2.
    Normalization denominator is reduced to original flat norms, as in #237.
    """
    C, E, V, Eov, flat_norm_product_floor = budget
    t = 7 * b - 2 * a
    numerator = abs(b * C + t * DEN * V) + b * E + abs(t) * Eov
    denominator = 2 * b * DEN * g.UNIT * g.UNIT * flat_norm_product_floor
    return ceildiv(numerator * g.UNIT, denominator)


def criterion(lo, hi, den, data, budget):
    low1 = floor_flat_cell(0, lo, hi, den, data)
    low2 = floor_flat_cell(1, lo, hi, den, data)
    # U(alpha) is convex (sum of absolute affine terms) / positive constant:
    # its supremum over the closed cell is at a boundary.
    upper = max(sample_upper(lo, den, budget),
                sample_upper(hi, den, budget))
    cost_num = g.D2 * low1 + g.D1 * low2
    strict_margin_num = cost_num - upper * g.UNIT
    return strict_margin_num > 0, (low1, low2, cost_num, upper, strict_margin_num)


def adjacent(left, right):
    return left[1] * right[2] == right[0] * left[2]


def main():
    vi, q_up = g.exact_original_inputs()
    wf, obs = g.independently_build_flat()
    need(tuple(wf) == g.FROZEN_W and tuple(obs) == g.FROZEN_O,
         "unverified_original_8flat_observable")
    g.negative_tests(wf, obs, vi)
    gate_path = os.path.join(GATE, "flat_action_gate.py")
    need(blob(gate_path) == GATE_BLOB, "Stage_G_source_code_not_original")
    grid_path = os.path.join(g.ROOT, GRID_REL)
    need(blob(grid_path) == GRID_BLOB, "Stage_G_29_grid_SHA_changed")
    grid = g.records(open(grid_path, encoding="ascii").read(), "Y137_G_ALPHA")
    verdict = g.records(open(grid_path, encoding="ascii").read(),
                        "Y137_G_GRID_VERDICT")
    need(len(grid) == 29 and len(verdict) == 1
         and verdict[0]["excluded_count"] == "17"
         and verdict[0]["not_excluded_count"] == "12",
         "original_29_grid_acceptance_changed")

    original = g.source_blob("independent/y137-q-dual-weight-20261113/RESULT-WILSON-Q-DUAL.hbp")
    budgets = g.records(original, "Y137_QDUAL_BUDGET")
    overlaps = g.records(original, "Y137_QDUAL_UNSHIFTED")
    need(len(budgets) == len(overlaps) == 1, "missing_original_dual")
    b, o = budgets[0], overlaps[0]
    need(b["fixed_sample_sign_certified"] == "1"
         and o["fixed_sample_unshifted_sign_certified"] == "1"
         and int(b["center_den"]) == DEN
         and o["exact_E1E2_projectors"] == "NOT_ENCLOSED",
         "incorrect_original_source_proof_scope")

    pdata = []
    pn = []
    for v, q in zip(vi, q_up):
        p = sum(w * x * x for w, x in zip(wf, v))
        s1 = sum(w * k * x * x for w, k, x in zip(wf, obs, v))
        s2 = sum(w * k * k * x * x for w, k, x in zip(wf, obs, v))
        need(p > 0 and p * s2 >= s1 * s1, "invalid_flat_variance")
        pdata.append((p, s1, s2, q))
        pn.append(p)

    Eov = (int(o["overlap_error_21_scaled"])
           + int(o["overlap_error_12_scaled"])
           + int(o["overlap_error_cross_scaled"]))
    overlap = int(o["trial_overlap_W"])
    need(int(o["overlap_abs_upper_scaled"]) >=
         DEN * abs(overlap) + Eov, "overlap_upper_not_rigorous")
    budget = (int(b["center_num"]), int(b["total_error_upper_scaled"]),
              overlap, Eov, isqrt(pn[0] * pn[1]))
    need(budget[0] > budget[1] > 0 and budget[4] > 0,
         "wrong_center_error_or_flat_norm")

    # Reproduce the accepted 29-point screen independently using no
    # speculative fractional normalizations.
    kept, excluded = [], []
    for row in grid:
        aa = int(row["alpha_num"])
        need(0 <= aa <= 28 and int(row["alpha_den"]) == 2,
             "original_invalid_grid_row")
        ok, dat = criterion(aa, aa, 2, pdata, budget)
        ref = row["screening_result"] == "EXCLUDED_BY_FLAT_LOWER"
        need(not ref or ok, "new_upper_not_at_least_as_sharp_as_original")
        (excluded if ok else kept).append(aa)
    need(len(excluded) + len(kept) == 29
         and len(set(excluded + kept)) == 29, "grid_not_reproduced")

    intervals = []
    def visit(lo, hi, den, depth):
        yes, proof = criterion(lo, hi, den, pdata, budget)
        if yes:
            intervals.append(("EXCLUDED", lo, hi, den, proof))
            return
        if depth == 0:
            intervals.append(("UNRESOLVED", lo, hi, den, proof))
            return
        mid = lo + hi
        visit(2 * lo, mid, 2 * den, depth - 1)
        visit(mid, 2 * hi, 2 * den, depth - 1)

    visit(0, MAX_ALPHA, 1, DEPTH)
    need(intervals and intervals[0][1] == 0
         and intervals[-1][2] == MAX_ALPHA * intervals[-1][3],
         "continuous_domain_not_covered")
    for i in range(1, len(intervals)):
        previous, current = intervals[i - 1], intervals[i]
        need(previous[2] * current[3] == current[1] * previous[3],
             "continuous_partition_has_gap_or_overlap")

    ex = [row for row in intervals if row[0] == "EXCLUDED"]
    un = [row for row in intervals if row[0] == "UNRESOLVED"]
    need(ex and un, "expected_mixed_classification")
    # Confirm there is exactly one connected undecided band (no speculative
    # inclusion of rejected intervals between undecided pieces).
    need(all(un[i - 1][2] * un[i][3] == un[i][1] * un[i - 1][3]
             for i in range(1, len(un))), "unresolved_split_by_exclusions")

    emit = g.emit
    emit("Y137_G_CONT_SOURCE",
         model="3x4_S3_r9", alpha_min=0, alpha_max=MAX_ALPHA,
         original_grid_points=29, original_grid_corroborated=29,
         source_Git_blob=GRID_BLOB,
         original_dual_SHA=g.EXPECTED_BLOBS[
             "independent/y137-q-dual-weight-20261113/RESULT-WILSON-Q-DUAL.hbp"],
         floor_Qnorm_Source_SHA=g.EXPECTED_BLOBS[
             "independent/y137-fullstate-Q-normalization-20261113/RESULT-FULL-W-NORM.hbp"],
         original_trial_identity="PASS", arithmetic="INTEGER_ONLY",
         scientific_gate="NECESSARY_SCREEN_FOR_EXISTING_SUFFICIENT_TEST",
         Wilson_weight="HOLD")

    for i, (p, s1, s2, q) in enumerate(pdata):
        mu_num, mu_den = simplified(s1, p)
        emit("Y137_G_CONT_VERTEX", level=i + 1,
             alpha_opt_num=mu_num, alpha_opt_den=mu_den,
             alpha_opt_floor_per_billion=s1 * DEN // p,
             exact_variance_num=p * s2 - s1 * s1,
             original_Qnorm_upper_per_trillion=q)

    for label, lo, hi, den, (v1, v2, lhs, upper, margin) in ex:
        a, b2 = simplified(lo, den)
        c, d = simplified(hi, den)
        need(margin > 0, "emitted_false_exclusion")
        emit("Y137_G_CONT_CERT", lo_num=a, lo_den=b2,
             hi_num=c, hi_den=d,
             action1_min_lower_per_trillion=v1,
             action2_min_lower_per_trillion=v2,
             linear_min_cost_num=lhs,
             linear_min_cost_den=g.UNIT * g.UNIT,
             shifted_sample_abs_max_upper_per_trillion=upper,
             strict_margin_scaled_num=margin,
             classification="EXCLUDED_ENTIRE_CONTINUOUS_INTERVAL")

    low_un = simplified(un[0][1], un[0][3])
    high_un = simplified(un[-1][2], un[-1][3])
    emit("Y137_G_CONT_VERDICT",
         search_domain="0_TO_14_CLOSED",
         dyadic_depth=DEPTH,
         exact_excluded_cells=len(ex),
         exact_unresolved_leaves=len(un),
         excluded_left_hi_num=low_un[0],
         excluded_left_hi_den=low_un[1],
         unresolved_lo_num=low_un[0],
         unresolved_lo_den=low_un[1],
         unresolved_hi_num=high_un[0],
         unresolved_hi_den=high_un[1],
         excluded_right_lo_num=high_un[0],
         excluded_right_lo_den=high_un[1],
         outside_intervals="EXCLUDED_FOR_FROZEN_SUFFICIENT_TEST",
         middle_interval="INCONCLUSIVE_NOT_CERTIFIED_POSITIVE",
         arbitrary_real_shifts="PARTIALLY_CLASSIFIED",
         new_actual_first_Wilson_weight="HOLD",
         issue_137="OPEN")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, ZeroDivisionError) as e:
        print("Y137_G_CONT_REFUSE|reason=" + str(e) + "|json=0", flush=True)
        raise SystemExit(1) from None
