#!/usr/bin/env python3
"""#137: certified directional Q-resolvent contribution to 8-flat Schur drift.

A pre-result frozen comparison with the accepted #181 global Frobenius
energy-drift bound. Source U/G and trial Q vectors are reconstructed on
the full K3 graph. All arithmetic is exact integers, with outward rounding.
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
PS = 1000000
FLOOR = 94068200
SCALE = 1000000000000
STEPS = 20
B_NORM = 24
ROWS = (
    (69909875505, 699080000, 699200000,
     (1000000000, 997935625, 996905915, 38054797, 37920545, 2788116, 51160, 51160),
     "0752df3c1941c67316cc6834795182fdaccdaba0ca5fc711221e7217d0dbaa1c",
     "83efba692ef3a8451a68049ee996451877ac4d646ae2f357fc0b604b48db0b0f",
     28000000000, 842057984250),
    (69949729820, 699480000, 699567503,
     (111045317, -38181375, -112233220, 1000000000,
      979217930, 216249666, 4169404, 4169404),
     "9229dfad058157d80287cb1ab188c1034bdbb16394dec045b540890d8bb05109",
     "e42df65b4b269095177fc609d06b4576917901c598f8ebd477eaa58b61b90d8d",
     11949000000, 1465570680225),
)


def emit(label, **fields):
    print(label + "|" + "|".join(str(name) + "=" + str(value)
                                for name, value in fields.items()) + "|json=0", flush=True)


def refuse(reason):
    emit("Y137_QDIR_REFUSE", reason=reason)
    raise SystemExit(1)


def ceil_div(n, d):
    if n < 0 or d <= 0:
        refuse("invalid_ceil_fraction")
    return (n + d - 1) // d


def ceil_isqrt(n):
    if n < 0:
        refuse("negative_root")
    z = isqrt(n)
    return z if z * z == n else z + 1


def rational_root_up(num, den):
    return ceil_isqrt(ceil_div(num * UNIT * UNIT, den))


def quad(A, v):
    return sum(v[i] * A[i][j] * v[j] for i in range(8) for j in range(8))


def check_freeze():
    raw = open(os.path.join(HERE, "PREDICTION.hbp"), "rb").read()
    if b"status=FROZEN_BEFORE_DIRECTIONAL_Q_REPLAY" not in raw:
        refuse("freeze_missing")
    if b"E1_old_sin_upper_per_trillion=842057984250|E2_old_sin_upper_per_trillion=1465570680225" not in raw:
        refuse("prior_readout_changed")
    if (source.SCRIPT_SHA != "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff"
            or source.NEW_G != FLOOR or source.PS != PS):
        refuse("source_not_pinned")
    emit("Y137_QDIR_FREEZE", checked=1, predictions_before_new_result=1,
         floor=str(FLOOR) + "/" + str(PS), source_sha256=source.SCRIPT_SHA)


def compute_B_norm2_times6(ball):
    result = 0
    for i, row in enumerate(ball["C"]):
        if row is None:
            continue
        weight = ball["wq"][i]
        for j, val in enumerate(row):
            result += (6 // ball["wf"][j]) * weight * val * val
    return result


def inspect(ball, a, lo, hi, v, uhash, ghash, null_gap, old_sin):
    zlo = lo * 100
    zhi = hi * 100
    if not (zlo < a < zhi):
        refuse("energy_window_does_not_contain_sample")
    gammaz = DEN * FLOOR - a * PS
    gammahi = DEN * FLOOR - zhi * PS
    if min(gammaz, gammahi) <= 0:
        refuse("floor_not_above_energy")
    fw = ball["wf"]
    vnorm2 = sum(fw[j] * v[j] * v[j] for j in range(8))
    if vnorm2 <= 0 or v[6] != v[7]:
        refuse("non_even_direction")
    rr = mod.threshold_ball(a, DEN, STEPS, SCALE, ball, FLOOR, keep_y=True)
    if (rr["hu"], rr["hg"]) != (uhash, ghash):
        refuse("independently_frozen_U_G_hashes")
    U, G = rr["U"], rr["G"]
    vec_U = [sum(U[i][j] * v[j] for j in range(8)) for i in range(8)]
    u_sq_6 = sum((6 // fw[i]) * val * val for i, val in enumerate(vec_U))
    u_up = rational_root_up(u_sq_6, 6 * DEN * DEN * SCALE ** 4 * vnorm2)
    gvv = quad(G, v)
    if gvv < 0:
        refuse("G_negative_quadratic")
    gamma_num = gammaz
    trace6 = sum((6 // fw[i]) * G[i][i] for i in range(8))
    direction_num = PS * gvv
    direction_den = 6 * gamma_num * DEN * SCALE * SCALE * vnorm2
    trace_num = PS * trace6
    trace_den = 36 * gamma_num * DEN * SCALE * SCALE
    schur_dir_up = rational_root_up(direction_num * trace_num, direction_den * trace_den)

    # Exact direct Bx norm in the W-orthonormalized P/Q metric.
    Bx2_numerator = 0
    for i, row in enumerate(ball["C"]):
        if row is not None:
            Bx2_numerator += ball["wq"][i] * (
                sum(row[j] * v[j] for j in range(8))) ** 2
    Bx_up = rational_root_up(Bx2_numerator, vnorm2)

    # The K3 trial Q vector (already computed for U/G) approximates
    # -R_z Bx. It is measured with all K3 W weights.
    Y = rr["Y"]
    qnorm2numer = sum(
        ball["wq"][i] * sum(Y[i][j] * v[j] for j in range(8)) ** 2
        for i in range(ball["n"]))
    Qhat_up = rational_root_up(qnorm2numer, SCALE * SCALE * vnorm2)

    # Complete Q residual: v^T G v = 6||b r_sample||_W^2
    # for the unnormalized flat part SCALE*v. Normalize by SCALE*sqrt(vWv).
    resid_up = rational_root_up(gvv, 6 * DEN * DEN * SCALE * SCALE * vnorm2)

    # Two independent certified bounds for ||R_z Bx||:
    #   ||B x|| / (gamma-z)
    #   ||yhat|| + ||r_z|| / (gamma-z).
    via_B = ceil_div(Bx_up * DEN * PS, gammaz)
    via_Q = Qhat_up + ceil_div(resid_up * DEN * PS, gammaz)
    rzbx_up = min(via_B, via_Q)
    if rzbx_up <= 0 or Bx_up <= 0:
        refuse("norm_bound_zero")

    B2_times6 = compute_B_norm2_times6(ball)
    if B2_times6 != 3456 or B_NORM * B_NORM * 6 != B2_times6:
        refuse("B_Frobenius_source_count")
    drift = max(a - zlo, zhi - a)
    direct = ceil_div(drift * UNIT, DEN)
    old_indirect = ceil_div(
        drift * B2_times6 * DEN * UNIT, 6 * gammahi * gammaz)
    # By resolvent identity, ||(S(E)-S(z))x|| <= |E-z| *
    # [ 1 + ||B||*||R_z Bx|| / (gamma-E) ].
    candidate_indirect = ceil_div(drift * B_NORM * rzbx_up * PS, gammahi)
    best_indirect = min(candidate_indirect, old_indirect)
    old_total = u_up + schur_dir_up + direct + old_indirect
    old_sin_check = ceil_div(old_total * UNIT, null_gap)
    if old_sin_check != old_sin:
        refuse("independent_prior_projector_replay_mismatch")
    new_total = u_up + schur_dir_up + direct + best_indirect
    new_sin = ceil_div(new_total * UNIT, null_gap)
    if new_sin > old_sin:
        refuse("claimed_directional_improvement_wrong")

    emit("Y137_QDIR_POINT", sample_num=a, sample_den=DEN,
         E_lo_num=zlo, E_hi_num=zhi, E_den=DEN,
         source_U_sha256=uhash, source_G_sha256=ghash,
         flat_W_norm2=vnorm2, B_Frobenius_norm2=576,
         Bx_norm_upper_per_trillion=Bx_up,
         Qhat_norm_upper_per_trillion=Qhat_up,
         full_Q_residual_norm_upper_per_trillion=resid_up,
         RzBx_via_B_upper_per_trillion=via_B,
         RzBx_via_Q_upper_per_trillion=via_Q,
         RzBx_upper_per_trillion=rzbx_up,
         U_residual_upper_per_trillion=u_up,
         Schur_direction_upper_per_trillion=schur_dir_up,
         drift_direct_upper_per_trillion=direct,
         old_global_drift_extra_upper_per_trillion=old_indirect,
         new_directional_drift_extra_upper_per_trillion=candidate_indirect,
         selected_drift_extra_upper_per_trillion=best_indirect,
         old_total_upper_per_trillion=old_total,
         new_total_upper_per_trillion=new_total,
         old_sin_upper_per_trillion=old_sin,
         new_sin_upper_per_trillion=new_sin,
         strict_improvement=int(new_sin < old_sin),
         nonvacuous=int(new_sin < UNIT), true_Wilson_E1_E2="OPEN")
    return int(new_sin < UNIT), int(new_sin < old_sin)


def main():
    check_freeze()
    ball = source.build_k3()
    if ball["n"] != 155378 or ball["nf"] != 1985218:
        refuse("graph_census")
    results = [inspect(ball, *row) for row in ROWS]
    emit("Y137_QDIR_VERDICT", samples=len(results),
         nonvacuous=sum(item[0] for item in results),
         improved=sum(item[1] for item in results),
         source_floor="94068200/1000000",
         calculation="source_pinned_integer_W_Q_directional_energy_drift",
         actual_first_Wilson_weight="OPEN",
         next="rerun_on_new_exact_microbrackets_and_certify_full_projectors")


if __name__ == "__main__":
    main()
