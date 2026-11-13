#!/usr/bin/env python3
"""#137 full W-state normalization and Q-tail certificate from accepted receipts.

Source-pinned exact 8x8 P-to-Q Gram, trial and full-Q residual norms,
energy-dependent R_E B dressing and normalized vector Lipschitz error.
Every numerical claim is rational/integer outward-enclosed. A failed true
E1/E2 Wilson transition target records HOLD, never fabricated positivity.
"""
import os
import sys
from math import gcd, isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
INDEP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(INDEP, "y137-liftfree-k3-20261113"))
import k3_common as source
import y137_k3_sector_isolation as mod

DEN = 1000000000
UNIT = 1000000000000
SCALE = 1000000000000
FLOOR_NUM = 94068200
FLOOR_ENERGY_NUM = 94068200000
K3_N = 155378
SHELL4_N = 1985218
FULLSOURCE = os.path.join(INDEP, "y137-q-dual-weight-20261113",
                          "RESULT-WILSON-Q-DUAL.hbp")
CENTERED = os.path.join(INDEP, "y137-centered-schur-transfer-20261113",
                        "RESULT-CENTERED-PROJECTOR.hbp")
SAMPLES = (
    (69909875505, 69908500000, 69909875505, 108258863901,
     "0752df3c1941c67316cc6834795182fdaccdaba0ca5fc711221e7217d0dbaa1c",
     "83efba692ef3a8451a68049ee996451877ac4d646ae2f357fc0b604b48db0b0f"),
    (69949729820, 69948100000, 69949729820, 253465115951,
     "9229dfad058157d80287cb1ab188c1034bdbb16394dec045b540890d8bb05109",
     "e42df65b4b269095177fc609d06b4576917901c598f8ebd477eaa58b61b90d8d"),
)


def emit(label, **fields):
    print(label + "|" + "|".join(str(name) + "=" + str(value)
                                for name, value in fields.items()) + "|json=0", flush=True)


def refuse(reason):
    emit("Y137_FULLN_REFUSE", reason=reason)
    raise SystemExit(1)


def ceil_div(n, d):
    if n < 0 or d <= 0:
        refuse("integer_ceil_sign")
    return (n + d - 1) // d


def root_ceil(num):
    if num < 0:
        refuse("integer_square_root_sign")
    t = isqrt(num)
    return t if t * t == num else t + 1


def root_frac_floor(num, den):
    if num < 0 or den <= 0:
        refuse("sqrt_fraction_floor_sign")
    return isqrt(num * UNIT * UNIT // den)


def root_frac_ceil(num, den):
    if num < 0 or den <= 0:
        refuse("sqrt_fraction_ceil_sign")
    return root_ceil(ceil_div(num * UNIT * UNIT, den))


def parse_rows(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    if not lines:
        refuse("missing_source_receipt")
    out = []
    for row in lines:
        fields = row.split("|")
        if not fields[-1] == "json=0":
            refuse("record_not_exact_integer_schema")
        item = {"tag": fields[0]}
        for field in fields[1:]:
            if "=" not in field:
                refuse("receipt_bad_field")
            name, value = field.split("=", 1)
            if name in item:
                refuse("duplicate_receipt_field")
            item[name] = value
        out.append(item)
    return out


def psd_integer(M):
    n = len(M)
    if any(M[i][j] != M[j][i] for i in range(n) for j in range(n)):
        refuse("non_symmetric_PSD_input")
    for mask in range(1, 1 << n):
        idx = [i for i in range(n) if mask & (1 << i)]
        principal = [[M[i][j] for j in idx] for i in idx]
        if mod.c.det(principal) < 0:
            return False
    return True


def exact_coupling(ball):
    # The full 8x8 weighted M = C^t W_Q C, whose metric operator
    # W_P^-1/2 M W_P^-1/2 is B*B. This is a source matrix, not a guess.
    wf, wq, CC = ball["wf"], ball["wq"], ball["C"]
    if not (len(wf) == 8 and len(wq) == len(CC) == K3_N):
        refuse("source_dimension")
    M = [[0] * 8 for _ in range(8)]
    used = 0
    edge = None
    for i, row in enumerate(CC):
        if row is None:
            continue
        for j in range(8):
            if not row[j]:
                continue
            used += 1
            if edge is None:
                edge = (wq[i], row[j], j)
            for k in range(8):
                if row[k]:
                    M[j][k] += wq[i] * row[j] * row[k]
    if edge is None or used <= 0:
        refuse("no_P_Q_edges")
    if any(M[i][j] != M[j][i] for i in range(8) for j in range(8)):
        refuse("B_gram_not_symmetric")
    if not all(6 % w == 0 for w in wf):
        refuse("flat_orbit_W_not_dividing_six")
    trace_times_six = sum((6 // wf[i]) * M[i][i] for i in range(8))
    if trace_times_six != 3456:
        refuse("previous_B_frobenius_trace_mismatch")
    # Missing-edge negative control: deleting one nonzero source C edge
    # must change the diagonal Gram exactly.
    wi, coeff, jj = edge
    dropped_delta = wi * (2 * coeff - 1)
    if dropped_delta == 0 or M[jj][jj] - dropped_delta == M[jj][jj]:
        refuse("dropped_C_edge_not_detected")
    # The sharpest INTEGER PSD scalar bound K with M <= K W_P.
    def upper_gram(kval):
        return [[kval * wf[i] * int(i == j) - M[i][j]
                 for j in range(8)] for i in range(8)]
    if not psd_integer(upper_gram(576)):
        refuse("trace_bound_not_PSD")
    low, high = 0, 576
    while low < high:
        mid = (low + high) // 2
        if psd_integer(upper_gram(mid)):
            high = mid
        else:
            low = mid + 1
    K = low
    if K <= 0 or not psd_integer(upper_gram(K)) or psd_integer(upper_gram(K - 1)):
        refuse("integer_minimal_operator_norm_bound")
    gram_72_identity = int(all(
        M[i][j] == 72 * wf[i] * int(i == j)
        for i in range(8) for j in range(8)))
    Bnorm_up = root_ceil(K * UNIT * UNIT)
    emit("Y137_FULLN_GRAM", dimension=8, K3_q=K3_N,
         shell4=SHELL4_N, P_Q_edges=used,
         wf=",".join(str(x) for x in wf),
         source_M_rows=";".join(",".join(str(x) for x in row) for row in M),
         weighted_trace6=trace_times_six, min_integer_PSD_K=K,
         B_norm_upper_per_trillion=Bnorm_up,
         BstarB_exact_72_identity=gram_72_identity,
         principal_minors_K_upper=255, principal_minors_K_minus1_has_negative=1,
         dropped_C_edge_negative_control="PASS")
    return K, Bnorm_up, gram_72_identity


def select(tag, rows):
    matches = [row for row in rows if row["tag"] == tag]
    return matches


def full_state_sample(accept, obs, a, lo, hi, sin, uhash, ghash, Bnorm_up):
    c = accept
    t = obs
    if (c["sample_num"] != str(a) or c["E_lo_num"] != str(lo)
            or c["E_hi_num"] != str(hi)
            or c["U_sha256"] != uhash or c["G_sha256"] != ghash
            or int(c["selected_sin_upper_per_trillion"]) != sin
            or c["mu_strictly_inside_null_gap"] != "1"):
        refuse("centered_projector_source_pin")
    if (t["z"] != str(a) + "/" + str(DEN)
            or t["U_sha256"] != uhash or t["G_sha256"] != ghash):
        refuse("fixed_sample_K3_trial_source_pin")
    if not (lo < a <= hi < FLOOR_ENERGY_NUM):
        refuse("invalid_E_bracket")
    flat_q = int(c["flat_W_norm2"])
    trial_sq = int(t["norm_W"])
    Gq = int(t["q_residual_G"])
    if flat_q <= 0 or Gq <= 0:
        refuse("source_Q_norm_sign")
    rawflat = SCALE * SCALE * flat_q
    if trial_sq <= rawflat:
        refuse("source_trial_missing_Q")
    qhat2_num = trial_sq - rawflat
    qhat2_den = rawflat
    qhat_lo = root_frac_floor(qhat2_num, qhat2_den)
    qhat_hi = root_frac_ceil(qhat2_num, qhat2_den)
    qres_up = root_frac_ceil(Gq, 6 * DEN * DEN * rawflat)
    if (qhat_hi != int(c["Qhat_upper_per_trillion"])
            or qres_up != int(c["full_Qres_upper_per_trillion"])):
        refuse("independent_receipt_Q_norm_or_residual_disagrees")
    gamma_z = FLOOR_ENERGY_NUM - a
    gamma_hi = FLOOR_ENERGY_NUM - hi
    correction = ceil_div(qres_up * DEN, gamma_z)
    rzbx_hi = min(int(c["RzBx_via_B_upper_per_trillion"]),
                   int(c["RzBx_via_Q_upper_per_trillion"]))
    if rzbx_hi != int(c["RzBx_via_Q_upper_per_trillion"]):
        refuse("Q_trial_not_preferred_check")
    if rzbx_hi != qhat_hi + correction:
        refuse("source_Q_resolvent_upper_disagrees")
    q_z_lo = max(0, qhat_lo - correction)
    q_z_hi = qhat_hi + correction
    if q_z_hi != rzbx_hi:
        refuse("Q_upper_anomalous")

    # Choosing the correct sign/phase, ||x_true-x_trial|| has the
    # sharp exact upper d=sqrt(2(1-cos(theta))) with
    # cos(theta)>=sqrt(1-sin(theta)^2), not the loose sqrt(2)*sin.
    if not (0 <= sin < UNIT):
        refuse("flat_projector_angle_vacuous")
    cos_lo = isqrt(UNIT * UNIT - sin * sin)
    flat_distance = root_ceil(2 * UNIT * (UNIT - cos_lo))
    if flat_distance <= 0 or flat_distance >= UNIT:
        refuse("flat_direction_distance_not_small")

    # True full state has Q part -R_E B x_true. Reference fixed sample
    # is -R_z B x_trial. Positivity of D-E supplies two terms:
    # (i) angular B contribution, (ii) change in resolvent energy.
    Q_flat_err = ceil_div(Bnorm_up * flat_distance * DEN,
                          UNIT * gamma_hi)
    delta_energy = max(a - lo, hi - a)
    Q_energy_err = ceil_div(delta_energy * rzbx_hi, gamma_hi)
    Q_err = Q_flat_err + Q_energy_err
    total_difference = root_ceil(flat_distance ** 2 + Q_err ** 2)

    # Norms of [x,-R Bx] where flat ||x||=1. Both can be
    # lower bounded from the source-Q profile and the Q error.
    q_true_lo = max(0, q_z_lo - Q_err)
    norm_z_lo = isqrt(UNIT * UNIT + q_z_lo * q_z_lo)
    norm_true_lo = isqrt(UNIT * UNIT + q_true_lo * q_true_lo)
    # Unit-normalization Lipschitz:
    # ||u/||u||-v/||v|||| <= ||u-v|| / sqrt(||u||||v||).
    norm_geom_lo = isqrt(norm_z_lo * norm_true_lo)
    if norm_geom_lo < UNIT:
        refuse("normalization_lower_below_one")
    dist_norm_up = ceil_div(total_difference * UNIT, norm_geom_lo)
    q_true_hi = q_z_hi + Q_err
    norm_z_hi = root_ceil(UNIT * UNIT + q_z_hi * q_z_hi)
    norm_true_hi = root_ceil(UNIT * UNIT + q_true_hi * q_true_hi)
    if not (UNIT <= norm_true_lo <= norm_true_hi
            and UNIT <= norm_z_lo <= norm_z_hi):
        refuse("invalid_norm_intervals")
    if dist_norm_up > 2 * UNIT:
        dist_norm_up = 2 * UNIT
    emit("Y137_FULLN_POINT", sample_num=a, sample_den=DEN,
         true_E_lo_num=lo, true_E_hi_num=hi, flat_sin_upper_per_trillion=sin,
         flat_phase_distance_upper_per_trillion=flat_distance,
         source_Gq=Gq, source_trial_norm2=trial_sq,
         Qhat_norm_lower_per_trillion=qhat_lo,
         Qhat_norm_upper_per_trillion=qhat_hi,
         whole_Q_residual_upper_per_trillion=qres_up,
         Q_Rz_Bx_lower_per_trillion=q_z_lo,
         Q_Rz_Bx_upper_per_trillion=q_z_hi,
         sample_state_norm_lower_per_trillion=norm_z_lo,
         sample_state_norm_upper_per_trillion=norm_z_hi,
         true_state_norm_lower_per_trillion=norm_true_lo,
         true_state_norm_upper_per_trillion=norm_true_hi,
         energy_variation_num=delta_energy, energy_variation_den=DEN,
         Q_flat_rotation_upper_per_trillion=Q_flat_err,
         Q_energy_change_upper_per_trillion=Q_energy_err,
         Q_total_difference_upper_per_trillion=Q_err,
         P_plus_Q_difference_upper_per_trillion=total_difference,
         norm_geometric_mean_lower_per_trillion=norm_geom_lo,
         full_normalized_state_distance_upper_per_trillion=dist_norm_up,
         projector_source="PR184_ACCEPTED_CENTERED_RAYLEIGH",
         actual_E1_E2_weight="OPEN")
    return dist_norm_up


def main():
    raw = open(os.path.join(HERE, "PREDICTION.hbp"), "rb").read()
    if b"FROZEN_BEFORE_FULL_STATE_GRAM_AND_NORM_REPLAY" not in raw:
        refuse("prediction_not_pre_result")
    if (source.SCRIPT_SHA != "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff"
            or source.NEW_G != FLOOR_NUM or source.PS != 1000000):
        refuse("source_floor_or_code_pin_changed")
    accepted = parse_rows(CENTERED)
    samples = parse_rows(FULLSOURCE)
    cs = select("Y137_CENTER_POINT", accepted)
    ts = select("Y137_QDUAL_TRIAL", samples)
    positives = select("Y137_QDUAL_RAW_WILSON_FIXED_WEIGHT", samples)
    if len(cs) != 2 or len(ts) != 2 or len(positives) != 1:
        refuse("accepted_source_receipts_incomplete")
    if int(positives[0]["lower_ppb_floor"]) != 416300:
        refuse("source_original_Wilson_fixed_sample_pin")
    # 416300 ppb > 1/2500 squared amplitude = 400000 ppb.
    if int(positives[0]["lower_ppb_floor"]) <= 400000:
        refuse("source_amplitude_less_than_one_fiftieth")
    emit("Y137_FULLN_FREEZE", status="PASS", source_floor="94068200/1000000",
         reference="MERGED_PR180_AND_PR184_FROZEN_EXACT_RECEIPTS",
         samples=2, original_Wilson_amplitude_gt="1/50")
    ball = source.build_k3()
    if ball["n"] != K3_N or ball["nf"] != SHELL4_N:
        refuse("whole_K3_census")
    K, Bnorm_up, exact_72 = exact_coupling(ball)
    by_center = {int(c["sample_num"]): c for c in cs}
    by_trial = {int(t["z"].split("/")[0]): t for t in ts}
    bounds = []
    for a, lo, hi, sin, uhash, ghash in SAMPLES:
        if a not in by_center or a not in by_trial:
            refuse("sample_pair_mismatch")
        bounds.append(full_state_sample(
            by_center[a], by_trial[a], a, lo, hi,
            sin, uhash, ghash, Bnorm_up))
    total = sum(bounds)
    # ||O_original|| <=14, and original fixed-sample amplitude >1/50.
    # Full normalized state transfer requires 14*(e1+e2)<1/50.
    positive = int(700 * total < UNIT)
    emit("Y137_FULLN_TRANSFER", sample_weight_lower_ppb=416300,
         original_Wilson_operator_norm_upper=14,
         fixed_sample_amplitude_gt="1/50",
         certified_fullstate_error1_upper_per_trillion=bounds[0],
         certified_fullstate_error2_upper_per_trillion=bounds[1],
         certified_total_fullstate_error_upper_per_trillion=total,
         target_total_error_num=1, target_total_error_den=700,
         transfer_sufficient_gate=int(positive),
         BstarB_exact_72_identity=exact_72, B_operator_norm2_integer_upper=K,
         true_E1_E2_positive_Wilson_weight=int(positive))
    if positive:
        # A >= (UNIT-700total)/(50 UNIT)>0 by triangle inequality.
        margin = UNIT - 700 * total
        numer = margin * margin
        denom = (50 * UNIT) ** 2
        common = gcd(numer, denom)
        emit("Y137_FULLN_TRUE_WEIGHT", strict_lower_num=numer // common,
             strict_lower_den=denom // common, source="ALL_Q_NORMALIZATION_GATES_PASS")
    emit("Y137_FULLN_VERDICT", source_conditional_exact_Gram=1,
         full_state_normalization_enclosed=1,
         actual_E1_E2_weight="CERTIFIED_POSITIVE" if positive else "HOLD",
         next="REDUCE_SCHUR_Q_PROJECTOR_ERROR_AND_RECALCULATE" if not positive
             else "INDEPENDENT_SECOND_SOURCE_VERIFICATION")


if __name__ == "__main__":
    main()
