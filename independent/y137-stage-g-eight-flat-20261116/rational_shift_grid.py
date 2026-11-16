#!/usr/bin/env python3
"""Stage G: exact 29-point half-integer shift feasibility screen.

A grid point is ruled out only when a *lower* bound on the existing state
transfer linear cost strictly exceeds the original #180 certified *upper*
bound on the matching shifted fixed-sample Wilson amplitude. Non-excluded
points are research candidates, NOT positive-weight certificates.
"""
import os
import sys
from math import isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import flat_action_gate as g
import shifted_7over2_gate as shift


def shifted_flat_norm_lower(v, weights, o, q_up, a):
    p = sum(w * t * t for w, t in zip(weights, v))
    score = sum(w * (2 * obs - a) ** 2 * t * t
                for w, obs, t in zip(weights, o, v))
    g.need(p > 0, "flat_norm_zero")
    num = score * g.UNIT * g.UNIT
    den = 4 * p * (g.UNIT * g.UNIT + q_up * q_up)
    g.need(den > 0, "no_Q_norm_bound")
    return isqrt((num * g.UNIT * g.UNIT) // den), p


def main():
    vectors, q_up = g.exact_original_inputs()
    weights, obs = g.independently_build_flat()
    g.negative_tests(weights, obs, vectors)
    original = g.source_blob("independent/y137-q-dual-weight-20261113/RESULT-WILSON-Q-DUAL.hbp")
    b = g.records(original, "Y137_QDUAL_BUDGET")
    ov = g.records(original, "Y137_QDUAL_UNSHIFTED")
    g.need(len(b) == len(ov) == 1, "original_dual_or_overlap_missing")
    g.need(b[0]["fixed_sample_sign_certified"] == "1"
           and ov[0]["fixed_sample_unshifted_sign_certified"] == "1"
           and int(b[0]["center_den"]) == 1000000000,
           "original_dual_source_mismatch")
    centre = abs(int(b[0]["center_num"]))
    err = int(b[0]["total_error_upper_scaled"])
    overlap = int(ov[0]["overlap_abs_upper_scaled"])
    p1 = sum(w * t * t for w, t in zip(weights, vectors[0]))
    p2 = sum(w * t * t for w, t in zip(weights, vectors[1]))
    prod_floor = isqrt(p1 * p2)
    g.need(centre > err > 0 and overlap > 0 and prod_floor > 0,
           "invalid_exact_dual_interval")
    denom = 2 * int(b[0]["center_den"]) * g.UNIT * g.UNIT * prod_floor

    excluded = []
    inconclusive = []
    records = {}
    # Frozen before hosted production: alpha=a/2 for a=0..28 inclusive.
    for a in range(29):
        l1, _ = shifted_flat_norm_lower(vectors[0], weights, obs, q_up[0], a)
        l2, _ = shifted_flat_norm_lower(vectors[1], weights, obs, q_up[1], a)
        sample_upper = shift.ceil_div(
            (centre + err + abs(7 - a) * overlap) * g.UNIT, denom)
        linear_lower_num = g.D2 * l1 + g.D1 * l2
        # d_i and l_i are both per 10^12; compare in an exact 10^24 unit.
        excluded_here = linear_lower_num > sample_upper * g.UNIT
        (excluded if excluded_here else inconclusive).append(a)
        records[a] = excluded_here
        g.emit("Y137_G_ALPHA", alpha_num=a, alpha_den=2,
               action1_lower_per_trillion=l1,
               action2_lower_per_trillion=l2,
               linear_error_lower_num=linear_lower_num,
               linear_error_lower_den=g.UNIT * g.UNIT,
               shifted_sample_amplitude_upper_per_trillion=sample_upper,
               screening_result="EXCLUDED_BY_FLAT_LOWER"
                   if excluded_here else "NOT_EXCLUDED_REQUIRES_FURTHER_CERTIFICATION")
    g.need(records[0] and records[7] and
           not records[12] and not records[16],
           "expected_baseline_and_nonexcluded_controls")
    g.need(len(excluded) + len(inconclusive) == 29
           and len(set(excluded + inconclusive)) == 29,
           "grid_incomplete_or_duplicated")
    g.emit("Y137_G_GRID_VERDICT",
           grid="HALF_INTEGERS_ZERO_THROUGH_FOURTEEN",
           cells=29, original_raw_alpha_zero="EXCLUDED",
           original_shift_seven_over_two="EXCLUDED",
           excluded_count=len(excluded),
           not_excluded_count=len(inconclusive),
           not_excluded_alpha_nums=",".join(map(str, inconclusive)),
           criterion="LOWER_TRANSFER_GREATER_THAN_UPPER_SAMPLE",
           result_for_not_excluded="INCONCLUSIVE_NOT_POSITIVE",
           arbitrary_real_shifts="NOT_CLASSIFIED",
           actual_first_Wilson_weight="HOLD", issue_137="OPEN")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, ZeroDivisionError) as exc:
        print("Y137_G_GRID_REFUSE|reason=" + str(exc) + "|json=0", flush=True)
        raise SystemExit(1) from None
