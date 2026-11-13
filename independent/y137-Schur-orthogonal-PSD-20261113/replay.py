#!/usr/bin/env python3
"""#137 source-certified Schur correction action on flat directions orthogonal
to the frozen trial eigendirection. Exact 7x7 weighted PSD, rational only.

Given 0<=X<=Lambda, the orthogonally projected error obeys
||Pperp X x||^2 <= max_{w perp x,||w||=1} <w,Lambda w> <x,Lambda x>.
Do not promote source-flat projector angles to true normalized Wilson weight.
"""
import os
import sys
from math import isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
INDEP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(INDEP, "y137-liftfree-k3-20261113"))
import k3_common as source
import y137_k3_sector_isolation as mod

DEN = 1000000000
UNIT = 1000000000000
SCALE = 1000000000000
PS = 1000000
FLOOR = 94068200
STEPS = 20
CENTERED = os.path.join(
    INDEP, "y137-centered-schur-transfer-20261113",
    "RESULT-CENTERED-PROJECTOR.hbp")
ROWS = (
    (69909875505,
     (1000000000,997935625,996905915,38054797,37920545,2788116,51160,51160),
     "0752df3c1941c67316cc6834795182fdaccdaba0ca5fc711221e7217d0dbaa1c",
     "83efba692ef3a8451a68049ee996451877ac4d646ae2f357fc0b604b48db0b0f",
     108258863901),
    (69949729820,
     (111045317,-38181375,-112233220,1000000000,979217930,216249666,4169404,4169404),
     "9229dfad058157d80287cb1ab188c1034bdbb16394dec045b540890d8bb05109",
     "e42df65b4b269095177fc609d06b4576917901c598f8ebd477eaa58b61b90d8d",
     253465115951),
)


def emit(label, **fields):
    print(label + "|" + "|".join(str(name) + "=" + str(val)
                                for name, val in fields.items()) + "|json=0", flush=True)


def refuse(label):
    emit("Y137_ORTHO_REFUSE", reason=label)
    raise SystemExit(1)


def ceil_div(n, d):
    if n < 0 or d <= 0:
        refuse("fraction_sign")
    return (n + d - 1) // d


def ceil_sqrt(n):
    if n < 0:
        refuse("sqrt_sign")
    y = isqrt(n)
    return y if y * y == n else y + 1


def sqrtfrac_up(n, d):
    return ceil_sqrt(ceil_div(n * UNIT * UNIT, d))


def psd(A, size):
    if len(A) != size or any(len(row) != size for row in A):
        refuse("PSD_matrix_size")
    if any(A[i][j] != A[j][i] for i in range(size) for j in range(size)):
        refuse("PSD_matrix_nonsymmetric")
    for mask in range(1, 1 << size):
        keep = [i for i in range(size) if mask & (1 << i)]
        minor = [[A[i][j] for j in keep] for i in keep]
        if mod.c.det(minor) < 0:
            return False
    return True


def records(path, tag):
    result = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line.startswith(tag + "|"):
            pairs = {}
            for token in line.split("|")[1:]:
                if "=" not in token:
                    refuse("malformed_accepted_receipt")
                key, val = token.split("=", 1)
                if key in pairs:
                    refuse("duplicate_accepted_receipt")
                pairs[key] = val
            result.append(pairs)
    return result


def source_freeze():
    raw = open(os.path.join(HERE, "PREDICTION.hbp"), "rb").read()
    if b"status=FROZEN_BEFORE_ORTHOGONAL_SOURCE_PSD_RUN" not in raw:
        refuse("prediction_not_sealed")
    if b"orthogonal_action2_le_max_eigen_Lambda_perp_times_xLambda_x=1" not in raw:
        refuse("new_inequality_not_frozen")
    if (source.SCRIPT_SHA != "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff"
            or source.NEW_G != FLOOR or source.PS != PS):
        refuse("source_floors")
    emit("Y137_ORTHO_FREEZE", status="PASS", source="accepted_exact_K3",
         floor="94068200/1000000", prediction_pre_result=1)


def perp_basis(wf, v):
    # Integer basis orthogonal to v in the weighted P Hilbert metric.
    pivot = max(range(8), key=lambda idx: abs(wf[idx] * v[idx]))
    if v[pivot] == 0:
        refuse("zero_trial_direction")
    cols = []
    for j in range(8):
        if j == pivot:
            continue
        vec = [0] * 8
        vec[j] = wf[pivot] * v[pivot]
        vec[pivot] = -wf[j] * v[j]
        if sum(wf[i] * vec[i] * v[i] for i in range(8)) != 0:
            refuse("weighted_perp_basis_failure")
        cols.append(vec)
    if len(cols) != 7:
        refuse("wrong_perp_dimension")
    # False control: changing one integer component must break orthogonality.
    false = cols[0][:]
    false[pivot] += 1
    if sum(wf[i] * false[i] * v[i] for i in range(8)) == 0:
        refuse("perp_negative_control_not_detected")
    return cols, pivot


def inspect(ball, row, accepted):
    a, v, hu, hg, old_sin = row
    wf = ball["wf"]
    if accepted["sample_num"] != str(a) or accepted["U_sha256"] != hu or accepted["G_sha256"] != hg:
        refuse("accepted_source_hash_mismatch")
    if int(accepted["selected_sin_upper_per_trillion"]) != old_sin:
        refuse("source_old_projector_angle")
    if accepted["mu_strictly_inside_null_gap"] != "1":
        refuse("accepted_null_branch_not_identified")
    result = mod.threshold_ball(a, DEN, STEPS, SCALE, ball, FLOOR)
    if (result["hu"], result["hg"]) != (hu, hg):
        refuse("source_recomputed_U_G_SHA_mismatch")
    G = result["G"]
    if not psd(G, 8):
        refuse("accepted_full_Q_residual_G_not_PSD")
    q = sum(wf[i] * v[i] * v[i] for i in range(8))
    gv = sum(v[i] * G[i][j] * v[j] for i in range(8) for j in range(8))
    if q <= 0 or gv <= 0:
        refuse("direction_Q_residual_norm")
    gamma_num = DEN * FLOOR - a * PS
    if gamma_num <= 0:
        refuse("Q_floor")
    # Raw weighted Lambda = PS*G/(T), T=6*gamma_num*b*SCALE^2.
    T = 6 * gamma_num * DEN * SCALE * SCALE
    dir_num, dir_den = PS * gv, T * q
    trace6 = sum((6 // wf[i]) * G[i][i] for i in range(8))
    tr_num = PS * trace6
    tr_den = 6 * T
    if min(dir_num, tr_num) <= 0 or any(6 % w for w in wf):
        refuse("source_positive_trace_and_weights")
    old_action = sqrtfrac_up(tr_num * dir_num, tr_den * dir_den)
    if old_action != int(accepted["Schur_PSD_action_upper_per_trillion"]):
        refuse("original_source_trace_action_not_reproduced")
    trace_up = ceil_div(tr_num * UNIT, tr_den)
    cols, pivot = perp_basis(wf, v)
    # Generalized 7D metric and residual Gram in the exact W-orthogonal
    # subspace; no metric square roots or guessed eigenvectors.
    W7 = [[sum(wf[i] * cols[j][i] * cols[k][i] for i in range(8))
           for k in range(7)] for j in range(7)]
    G7 = [[sum(cols[j][i] * G[i][l] * cols[k][l]
               for i in range(8) for l in range(8))
           for k in range(7)] for j in range(7)]
    # Lambda<=K/UNIT on v^perp iff
    # K*T*W7 - PS*UNIT*G7 PSD, by 127 exact principal minors.
    def candidate(K):
        return [[K * T * W7[i][j] - PS * UNIT * G7[i][j]
                 for j in range(7)] for i in range(7)]
    if not psd(candidate(trace_up), 7):
        refuse("trace_upper_does_not_dominate_restricted_operator")
    low, high = 0, trace_up
    while low < high:
        mid = (low + high) // 2
        if psd(candidate(mid), 7):
            high = mid
        else:
            low = mid + 1
    K = low
    if not psd(candidate(K), 7):
        refuse("restricted_PSD_K_failed")
    if K > 0 and psd(candidate(K - 1), 7):
        refuse("restricted_PSD_minimality_failed")
    new_action = sqrtfrac_up(K * dir_num, UNIT * dir_den)
    selected_action = min(old_action, new_action)
    U_center = int(accepted["U_centered_upper_per_trillion"])
    energy = int(accepted["energy_selected_extra_upper_per_trillion"])
    mu = int(accepted["Rayleigh_mu_abs_upper_per_trillion"])
    gap = int(accepted["Schur_null_gap_lower_per_trillion"])
    if not 0 <= mu < gap:
        refuse("null_identification_gate")
    old_center = U_center + old_action + energy
    old_center_sin = ceil_div(old_center * UNIT, gap - mu)
    if old_center_sin != int(accepted["centered_sin_upper_per_trillion"]):
        refuse("accepted_centered_rayleigh_replay_mismatch")
    new_center = U_center + selected_action + energy
    new_center_sin = ceil_div(new_center * UNIT, gap - mu)
    new_selected = min(new_center_sin, old_sin)
    if new_selected > old_sin:
        refuse("new_bound_regressed")
    emit("Y137_ORTHO_POINT", sample_num=a, den=DEN,
         source_U_sha256=hu, source_G_sha256=hg,
         flat_metric_norm2=q, weighted_perp_dimension=7,
         pivot_index=pivot, G_all_255_PSD=1,
         trace_Lambda_upper_per_trillion=trace_up,
         max_Lambda_perp_integer_upper_per_trillion=K,
         lambda_perp_127_PSD=1, lambda_Kminus1_not_PSD=int(K>0),
         Rayleigh_Lambda_up_num=dir_num, Rayleigh_Lambda_up_den=dir_den,
         old_trace_source_action_upper_per_trillion=old_action,
         new_perp_source_action_upper_per_trillion=new_action,
         selected_source_action_upper_per_trillion=selected_action,
         centered_variational_U_upper_per_trillion=U_center,
         energy_directional_extra_upper_per_trillion=energy,
         Rayleigh_mu_upper_per_trillion=mu,
         Schur_null_gap_lower_per_trillion=gap,
         old_centered_sin_upper_per_trillion=old_center_sin,
         new_centered_sin_upper_per_trillion=new_center_sin,
         accepted_old_sin_upper_per_trillion=old_sin,
         selected_sin_upper_per_trillion=new_selected,
         strict_improvement=int(new_selected<old_sin),
         nonvacuous=int(new_selected<UNIT),
         orthogonal_basis_negative_control="PASS",
         actual_Wilson_first_weight="OPEN")
    return int(new_selected < old_sin), new_selected


def main():
    source_freeze()
    accepted = records(CENTERED, "Y137_CENTER_POINT")
    if len(accepted) != 2:
        refuse("accepted_centered_receipt_missing")
    accepted_by_sample = {int(item["sample_num"]): item for item in accepted}
    if set(accepted_by_sample) != set(row[0] for row in ROWS):
        refuse("sample_pair_not_frozen")
    ball = source.build_k3()
    if (ball["n"], ball["nf"]) != (155378, 1985218):
        refuse("K3_census")
    outcomes = [inspect(ball, row, accepted_by_sample[row[0]]) for row in ROWS]
    emit("Y137_ORTHO_VERDICT", tested=2,
         improvement_count=sum(item[0] for item in outcomes),
         E1_sin_upper_per_trillion=outcomes[0][1],
         E2_sin_upper_per_trillion=outcomes[1][1],
         exact_source="full_Q_K3_8x8_PSD_and_weighted_perp_7x7",
         true_E1_E2_Wilson_weight="OPEN",
         next="update_full_normalized_state_error_then_test_rational_Wilson_sign")


if __name__ == "__main__":
    main()
