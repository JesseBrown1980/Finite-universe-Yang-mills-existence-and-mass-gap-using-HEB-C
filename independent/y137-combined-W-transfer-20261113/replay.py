#!/usr/bin/env python3
"""#137 independent integer composition of accepted #184/#185/#186 source proofs.

Apply exact B*B=72I to Schur energy drift, retain the new 7D orthogonal
Schur residual, then recompute true-vs-fixed complete normalized W-state
bounds and fail closed on the actual raw Wilson E1-E2 sign-transfer gate.
"""
import os
from math import isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
INDEP = os.path.dirname(HERE)
UNIT = 1000000000000
DEN = 1000000000
FLOOR_ENERGY = 94068200000
B_NORM_UP = 8485281374239
PTH = (
    ("y137-centered-schur-transfer-20261113", "RESULT-CENTERED-PROJECTOR.hbp"),
    ("y137-fullstate-Q-normalization-20261113", "RESULT-FULL-W-NORM.hbp"),
    ("y137-Schur-orthogonal-PSD-20261113", "RESULT-ORTHOGONAL-SCHUR.hbp"),
)
SAMPLES = (69909875505, 69949729820)
PREHOST = ((43364646417, 44731270536),
           (95928035901, 99359189983))


def emit(tag, **items):
    print(tag + "|" + "|".join(str(name) + "=" + str(val)
                               for name, val in items.items()) + "|json=0", flush=True)


def fail(msg):
    emit("Y137_COMBINED_REFUSE", reason=msg)
    raise SystemExit(1)


def updiv(n, d):
    if n < 0 or d <= 0:
        fail("positive_fraction")
    return (n + d - 1) // d


def sqrt_ceil(n):
    if n < 0:
        fail("negative_root")
    r = isqrt(n)
    return r if r * r == n else r + 1


def input_records(d, fn, tag):
    path = os.path.join(INDEP, d, fn)
    rows = []
    for line in open(path, encoding="utf-8"):
        if not line.startswith(tag + "|"):
            continue
        obj = {}
        for item in line.strip().split("|")[1:]:
            if "=" not in item:
                fail("malformed_source_receipt")
            key, val = item.split("=", 1)
            if key in obj:
                fail("duplicated_record_key")
            obj[key] = val
        rows.append(obj)
    if len(rows) != 2:
        fail("source_pair_missing")
    if [int(rec["sample_num"]) for rec in rows] != list(SAMPLES):
        fail("source_order_mismatch")
    return rows


def freeze():
    pred = open(os.path.join(HERE, "PREDICTION.hbp"), "rb").read()
    if b"FROZEN_BEFORE_INDEPENDENT_COMBINED_HOSTED_REPLAY" not in pred:
        fail("not_frozen")
    if b"BstarB_equals_72I=1|Bnorm_ceil_per_trillion=8485281374239" not in pred:
        fail("B_norm_prediction_pin")
    if b"E1_flat_sin=43364646417|E2_flat_sin=95928035901" not in pred:
        fail("sealed_numeric_predictions_changed")
    if B_NORM_UP * B_NORM_UP < 72 * UNIT * UNIT:
        fail("Bnorm_not_outward")
    if (B_NORM_UP - 1) * (B_NORM_UP - 1) >= 72 * UNIT * UNIT:
        fail("Bnorm_not_minimal_integer_ceiling")
    emit("Y137_COMBINED_FREEZE", status="PASS",
         source="MERGED_184_185_186", prediction_pre_hosted=1,
         original_Wilson_amplitude_gt="1/50")


def inspect(old, norm, perp, index):
    sample = SAMPLES[index]
    if any(int(rec["sample_num"]) != sample for rec in (old, norm, perp)):
        fail("sample_labels_disagree")
    if (old["U_sha256"] != perp["source_U_sha256"] or
            old["G_sha256"] != perp["source_G_sha256"] or
            old["sample_num"] != norm["sample_num"]):
        fail("matrix_source_SHA_mismatch")
    if (old["mu_strictly_inside_null_gap"] != "1" or
            perp["lambda_perp_127_PSD"] != "1" or
            perp["G_all_255_PSD"] != "1" or
            int(perp["selected_sin_upper_per_trillion"]) >=
            int(old["selected_sin_upper_per_trillion"])):
        fail("source_Rayleigh_or_PSD_gates")
    q_up = int(norm["Q_Rz_Bx_upper_per_trillion"])
    q_lo = int(norm["Q_Rz_Bx_lower_per_trillion"])
    if not (0 < q_lo <= q_up < UNIT):
        fail("Q_norm_range")
    a = sample
    lo, hi = int(old["E_lo_num"]), int(old["E_hi_num"])
    if not (lo < a <= hi < FLOOR_ENERGY):
        fail("source_energy_interval")
    if (str(lo) != norm["true_E_lo_num"] or
            str(hi) != norm["true_E_hi_num"]):
        fail("energy_interval_changed")
    delta_E = max(a - lo, hi - a)
    if delta_E != int(norm["energy_variation_num"]):
        fail("source_energy_variation_disagrees")
    gamma_hi = FLOOR_ENERGY - hi
    old_extra = int(perp["energy_directional_extra_upper_per_trillion"])
    if old_extra != int(old["energy_directional_extra_upper_per_trillion"]):
        fail("old_24_bound_disagrees")
    # Source #183/#184 used ||B||_F=24; accepted #185 proves ||B||=sqrt72.
    new_extra = updiv(delta_E * B_NORM_UP * q_up,
                      UNIT * gamma_hi)
    if new_extra >= old_extra:
        fail("exact_B_improvement_did_not_pass")
    old_mu = int(perp["Rayleigh_mu_upper_per_trillion"])
    mu = old_mu - old_extra + new_extra
    gap = int(perp["Schur_null_gap_lower_per_trillion"])
    if not (0 < mu < gap):
        fail("null_branch_mu_not_strict")
    center = (int(perp["centered_variational_U_upper_per_trillion"])
              + int(perp["selected_source_action_upper_per_trillion"])
              + new_extra)
    flat_sin = updiv(center * UNIT, gap - mu)
    if flat_sin >= int(perp["selected_sin_upper_per_trillion"]):
        fail("combined_flat_projector_not_improved")
    # Exact sharp upper on phase-aligned unit P-flat distance.
    cos_lower = isqrt(UNIT * UNIT - flat_sin * flat_sin)
    dflat = sqrt_ceil(2 * UNIT * (UNIT - cos_lower))
    if not 0 < dflat < UNIT:
        fail("flat_rotation_is_vacuous")
    # True Q has -R_E Bx; fixed sample Q has -R_z Bv.
    q_rotation = updiv(B_NORM_UP * dflat * DEN,
                       UNIT * gamma_hi)
    q_energy = updiv(delta_E * q_up, gamma_hi)
    q_difference = q_rotation + q_energy
    total_un = sqrt_ceil(dflat * dflat + q_difference * q_difference)
    # The accepted #185 exact whole-Q sample interval gives positive
    # sample and true full-state norm lower endpoints after the update.
    q_true_lower = max(0, q_lo - q_difference)
    norm_z_lower = isqrt(UNIT * UNIT + q_lo * q_lo)
    norm_true_lower = isqrt(UNIT * UNIT + q_true_lower * q_true_lower)
    norm_geometric_lower = isqrt(norm_z_lower * norm_true_lower)
    normalized_error = updiv(total_un * UNIT, norm_geometric_lower)
    if normalized_error > int(norm["full_normalized_state_distance_upper_per_trillion"]):
        fail("new_total_state_error_regressed")
    if (flat_sin, normalized_error) != PREHOST[index]:
        fail("prediction_not_reproduced")
    emit("Y137_COMBINED_POINT", sample_num=a, den=DEN,
         true_E_lo_num=lo, true_E_hi_num=hi,
         original_fullstate_distance_upper_per_trillion=
             norm["full_normalized_state_distance_upper_per_trillion"],
         source_7D_orthogonal_sin_upper_per_trillion=
             perp["selected_sin_upper_per_trillion"],
         old_B24_energy_extra_upper_per_trillion=old_extra,
         exact_Bsqrt72_energy_extra_upper_per_trillion=new_extra,
         Rayleigh_mu_refined_upper_per_trillion=mu,
         centered_source_residual_refined_upper_per_trillion=center,
         refined_flat_sin_upper_per_trillion=flat_sin,
         phase_aligned_flat_distance_upper_per_trillion=dflat,
         whole_Q_sample_lower_per_trillion=q_lo,
         whole_Q_sample_upper_per_trillion=q_up,
         Q_rotation_upper_per_trillion=q_rotation,
         Q_energy_change_upper_per_trillion=q_energy,
         Q_difference_upper_per_trillion=q_difference,
         sample_full_norm_lower_per_trillion=norm_z_lower,
         true_full_norm_lower_per_trillion=norm_true_lower,
         normalization_geometric_lower_per_trillion=norm_geometric_lower,
         full_normalized_state_error_upper_per_trillion=normalized_error,
         source_Gamma_floor="94068200/1000000",
         actual_E1_E2_Wilson_weight="OPEN")
    return normalized_error


def main():
    freeze()
    A = input_records(*PTH[0], "Y137_CENTER_POINT")
    B = input_records(*PTH[1], "Y137_FULLN_POINT")
    C = input_records(*PTH[2], "Y137_ORTHO_POINT")
    norms = [inspect(A[i], B[i], C[i], i) for i in range(2)]
    total = sum(norms)
    old_total = sum(int(obj["full_normalized_state_distance_upper_per_trillion"])
                    for obj in B)
    if total >= old_total or total != 144090460519:
        fail("combined_total_prediction_or_improvement")
    positive = int(700 * total < UNIT)
    emit("Y137_COMBINED_TRANSFER", E1_error_upper_per_trillion=norms[0],
         E2_error_upper_per_trillion=norms[1],
         combined_fullstate_error_upper_per_trillion=total,
         previously_accepted_fullstate_error_upper_per_trillion=old_total,
         source_fixed_sample_weight_lower_ppb=416300,
         original_unshifted_Wilson_norm_upper=14,
         sufficient_error_target="1/700",
         strict_positive_Wilson_first_weight_proved=positive)
    emit("Y137_COMBINED_VERDICT", exact_integers=1,
         source_conditional=1, first_Wilson_weight="CERTIFIED_POSITIVE" if positive
         else "HOLD", next="IMPROVE_SHELL4_Q_RESOLVENT_BOUND" if not positive
         else "INDEPENDENT_SECOND_SOURCE_REPLAY")


if __name__ == "__main__":
    main()
