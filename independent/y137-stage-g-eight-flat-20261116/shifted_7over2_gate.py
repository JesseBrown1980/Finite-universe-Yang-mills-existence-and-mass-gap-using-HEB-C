#!/usr/bin/env python3
"""Stage G second small gate: exact previously certified O-7/2 shift.

Use only the original #180 dual-centre plus absolute residual enclosure to
obtain a sample-amplitude UPPER bound, and exact eight-flat/Q-norm source
lower bounds for each shifted sample action. This is a necessary obstruction
to the existing Stage E/F sufficient inequality, not a physical zero theorem.
"""
import os
import sys
from math import isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import flat_action_gate as g


def ceil_div(n, d):
    g.need(n >= 0 and d > 0, "invalid_upper_ratio")
    return (n + d - 1) // d


def main():
    vectors, qup = g.exact_original_inputs()
    weights, observable = g.independently_build_flat()
    g.negative_tests(weights, observable, vectors)
    expected = g.source_blob("independent/y137-q-dual-weight-20261113/RESULT-WILSON-Q-DUAL.hbp")
    budgets = g.records(expected, "Y137_QDUAL_BUDGET")
    shifted_weight = g.records(expected, "Y137_QDUAL_FIXED_SAMPLE_WEIGHT")
    raw_overlap = g.records(expected, "Y137_QDUAL_UNSHIFTED")
    g.need(len(budgets) == len(shifted_weight) == len(raw_overlap) == 1,
           "missing_original_Wilson_dual_or_overlap_budget")
    b = budgets[0]
    g.need(b["fixed_sample_sign_certified"] == "1" and
           b["exact_E1E2_projectors"] == "NOT_ENCLOSED" and
           int(b["center_den"]) == 1000000000 and
           int(shifted_weight[0]["lower_ppb_floor"]) == 1059210 and
           shifted_weight[0]["evidence"] ==
               "RIGOROUS_FOR_SHIFTED_WILSON_FIXED_SAMPLES_ONLY",
           "wrong_original_shifted_amplitude_provenance")
    pnorms = []
    floors = []
    for i in range(2):
        pnorm = sum(w * v * v for w, v in zip(weights, vectors[i]))
        score2 = sum(w * (2 * o - 7) ** 2 * v * v
                     for w, o, v in zip(weights, observable, vectors[i]))
        # O_shift = (2O-7)/2; use exact Q norm upper from #185.
        num = score2 * g.UNIT * g.UNIT
        den = 4 * pnorm * (g.UNIT * g.UNIT + qup[i] * qup[i])
        minimum_integer = (5, 2)[i]
        g.need(num > minimum_integer * minimum_integer * den,
               "shifted_flat_action_not_above_conservative_lower")
        floor = isqrt((num * g.UNIT * g.UNIT) // den)
        pnorms.append(pnorm)
        floors.append(floor)
        g.emit("Y137_G_SHIFT_POINT", level=i + 1, alpha_num=7, alpha_den=2,
               shift_action_squared_lower_num=num,
               shift_action_squared_lower_den=den,
               shift_action_lower_floor_per_trillion=floor,
               conservative_integer_lower=minimum_integer)
    centre = abs(int(b["center_num"]))
    err = int(b["total_error_upper_scaled"])
    g.need(centre > err and err > 0, "original_shifted_dual_margin")
    # Original #180 source: centred O2=2O-7 raw transition has numerator
    # centre/den and absolute error err/den. The original samples have flat
    # raw components UNIT*v, hence full norms >= UNIT*sqrt(Pnorm), each.
    # Round the denominator DOWN and the resulting UPPER amplitude UP.
    product_flat_norm_lower = isqrt(pnorms[0] * pnorms[1])
    g.need(product_flat_norm_lower > 0, "zero_original_sample_norm")
    amplitude_upper_per_trillion = ceil_div(
        (centre + err) * g.UNIT,
        2 * int(b["center_den"]) * g.UNIT * g.UNIT *
        product_flat_norm_lower)
    # Even omitting the strictly nonnegative second-order term in the
    # shifted transfer uncertainty, the conservative linear term is larger
    # than the source-conditional UPPER on its actual shifted amplitude.
    linear_lower_per_trillion = 5 * g.D2 + 2 * g.D1
    g.need(linear_lower_per_trillion > amplitude_upper_per_trillion,
           "shifted_seven_over_two_no_go_not_proved")
    # The same exact #180 receipt also bounds the *original unshifted*
    # fixed sample amplitude. Since O = (2O-7)/2 + (7/2)I,
    # add seven times the rigorous #180 full-Q sample overlap upper in the
    # identical integer scale *before* dividing by 2 and normalizing.
    g.need(raw_overlap[0]["fixed_sample_unshifted_sign_certified"] == "1" and
           raw_overlap[0]["exact_E1E2_projectors"] == "NOT_ENCLOSED",
           "original_raw_sample_overlap_missing")
    overlap_abs_upper = int(raw_overlap[0]["overlap_abs_upper_scaled"])
    g.need(overlap_abs_upper > 0 and
           int(raw_overlap[0]["raw_margin_scaled"]) > 0,
           "original_overlap_bound_invalid")
    raw_amplitude_upper_per_trillion = ceil_div(
        (centre + err + 7 * overlap_abs_upper) * g.UNIT,
        2 * int(b["center_den"]) * g.UNIT * g.UNIT *
        product_flat_norm_lower)
    raw_linear_lower_per_trillion = 8 * g.D2 + 4 * g.D1
    g.need(raw_linear_lower_per_trillion > raw_amplitude_upper_per_trillion,
           "raw_amplitude_upper_not_enough_for_no_go")
    g.emit("Y137_G_SHIFT_VERDICT",
           shift_num=7, shift_den=2,
           source_fixed_sample_amplitude_upper_per_trillion=
               amplitude_upper_per_trillion,
           source_shifted_sample_weight_lower_ppb=1059210,
           conservative_linear_error_lower_per_trillion=
               linear_lower_per_trillion,
           raw_sample_amplitude_upper_per_trillion=
               raw_amplitude_upper_per_trillion,
           raw_conservative_linear_error_lower_per_trillion=
               raw_linear_lower_per_trillion,
           raw_original_amplitude_transfer="NO_GO_EVEN_WITH_ACTUAL_SAMPLE_AMP",
           shifted_second_order_cost="OMITTED_FOR_STRONGER_OBSTRUCTION",
           original_full_E1_E2_sample_identity="PASS",
           original_dual_source_SHA="PASS",
           raw_shifted_sufficient_inequality="NO_GO_WITH_ACCEPTED_D1_D2",
           arbitrary_shift="NOT_TESTED",
           first_Wilson_weight="HOLD", issue_137="OPEN")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, IndexError, ZeroDivisionError) as exc:
        print("Y137_G_SHIFT_REFUSE|reason=" + str(exc) + "|json=0", flush=True)
        raise SystemExit(1) from None
