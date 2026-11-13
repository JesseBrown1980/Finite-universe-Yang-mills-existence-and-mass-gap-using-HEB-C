#!/usr/bin/env python3
"""#137: certified centered Schur projector residual with a fail-closed null-branch gate.

Inputs: pre-frozen true-energy windows from the independent #182 K3 inertia
receipt, and old exact sample 8-flat vectors/U/G hashes from #180.
No eigenstate positivity is asserted by this directional diagnostic.
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
FLOOR = 94068200
PS = 1000000
FLOOR_ENERGY_NUM = 94068200000
B_FROB = 24
STEPS = 20
E3_LO = 69968699300
E1_LO, E1_HI = 69908500000, 69909875505
E2_LO, E2_HI = 69948100000, 69949729820
GAP1 = (E2_LO - E1_HI) * (UNIT // DEN)
GAP2 = min(E2_LO - E1_HI, E3_LO - E2_HI) * (UNIT // DEN)
ROWS = (
    (69909875505, E1_LO, E1_HI,
     (1000000000,997935625,996905915,38054797,37920545,2788116,51160,51160),
     "0752df3c1941c67316cc6834795182fdaccdaba0ca5fc711221e7217d0dbaa1c",
     "83efba692ef3a8451a68049ee996451877ac4d646ae2f357fc0b604b48db0b0f",
     GAP1),
    (69949729820, E2_LO, E2_HI,
     (111045317,-38181375,-112233220,1000000000,979217930,216249666,4169404,4169404),
     "9229dfad058157d80287cb1ab188c1034bdbb16394dec045b540890d8bb05109",
     "e42df65b4b269095177fc609d06b4576917901c598f8ebd477eaa58b61b90d8d",
     GAP2),
)


def emit(label, **fields):
    print(label + "|" + "|".join(str(name) + "=" + str(value)
                                 for name, value in fields.items()) + "|json=0", flush=True)


def refuse(reason):
    emit("Y137_CENTER_REFUSE", reason=reason)
    raise SystemExit(1)


def ceil_div(n, d):
    if n < 0 or d <= 0:
        refuse("invalid_positive_fraction")
    return (n + d - 1) // d


def sqrt_up(n, d):
    if n < 0 or d <= 0:
        refuse("sqrt_fraction")
    x = ceil_div(n * UNIT * UNIT, d)
    z = isqrt(x)
    return z if z * z == x else z + 1


def quad(M, v):
    return sum(v[i] * M[i][j] * v[j] for i in range(8) for j in range(8))


def freeze():
    raw = open(os.path.join(HERE, "PREDICTION.hbp"), "rb").read()
    if b"status=SEALED_BEFORE_CENTERED_PROJECTOR_RUN" not in raw:
        refuse("no_prediction")
    for label, row in (("E1", ROWS[0]), ("E2", ROWS[1])):
        sample, lo, hi = row[:3]
        want = (b"Y137_CENTER_" + label.encode("ascii") +
                ("|z=" + str(sample) + "|lo=" + str(lo) + "|hi=" +
                 str(hi) + "|").encode("ascii"))
        if want not in raw:
            refuse("frozen_windows_changed")
    if b"E2-E1_gt_num=38224495|E3-E2_gt_num=18969480" not in raw:
        refuse("frozen_gap")
    if source.SCRIPT_SHA != "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff":
        refuse("source_script")
    if (source.NEW_G, source.PS) != (FLOOR, PS):
        refuse("source_floor")
    emit("Y137_CENTER_FREEZE", version=1, status="PASS", floor="94068200/1000000",
         source_microbrackets="PR182_14_point_exact_inertia_receipt",
         sample_vectors="from_accepted_PR180", prediction_pre_result=1)


def coupling_B2x6(ball):
    s = 0
    for i, row in enumerate(ball["C"]):
        if row is not None:
            for j, cval in enumerate(row):
                s += (6 // ball["wf"][j]) * ball["wq"][i] * cval * cval
    if s != 3456:
        refuse("B_Frobenius_count")
    return s


def inspect(ball, a, lo, hi, v, uhash, ghash, gap):
    if not (lo < a <= hi and hi < E3_LO):
        refuse("sample_outside_certified_interval")
    if (E1_HI >= E2_LO or E2_HI >= E3_LO or
            GAP1 != 38224495000 or GAP2 != 18969480000):
        refuse("source_level_order")
    gammaz = FLOOR_ENERGY_NUM - a
    gammahi = FLOOR_ENERGY_NUM - hi
    if min(gammaz, gammahi) <= 0:
        refuse("source_gamma")
    wf = ball["wf"]
    vnorm = sum(wf[i] * v[i] * v[i] for i in range(8))
    if vnorm <= 0 or v[6] != v[7]:
        refuse("sector_and_norm")
    res = mod.threshold_ball(a, DEN, STEPS, SCALE, ball, FLOOR, keep_y=True)
    if (res["hu"], res["hg"]) != (uhash, ghash):
        refuse("U_G_frozen_hashes_changed")
    U, G = res["U"], res["G"]
    uv = [sum(U[i][j] * v[j] for j in range(8)) for i in range(8)]
    uvq = sum(uv[i] * v[i] for i in range(8))
    abs_mu_U = ceil_div(abs(uvq) * UNIT, DEN * SCALE * SCALE * vnorm)

    # New EXACT W-weighted centered residual of U: subtract its Rayleigh
    # quotient (a scalar identity term, which cannot rotate eigenvectors).
    centered_numer = [
        vnorm * uv[i] - uvq * wf[i] * v[i] for i in range(8)]
    centered_sq6 = sum(
        (6 // wf[i]) * centered_numer[i] * centered_numer[i]
        for i in range(8))
    Ucenter_up = sqrt_up(centered_sq6, 6 * DEN * DEN * SCALE ** 4 * vnorm ** 3)
    Unormal_sq6 = sum((6 // wf[i]) * uv[i] * uv[i] for i in range(8))
    Unormal_up = sqrt_up(Unormal_sq6, 6 * DEN * DEN * SCALE ** 4 * vnorm)
    if Ucenter_up > Unormal_up:
        refuse("centered_variational_norm_inverted")

    gv = quad(G, v)
    if gv < 0:
        refuse("negative_residual_gram")
    gn = DEN * FLOOR - a * PS
    dir_num = PS * gv
    dir_den = 6 * gn * DEN * SCALE * SCALE * vnorm
    tr6 = sum((6 // wf[i]) * G[i][i] for i in range(8))
    tr_num = PS * tr6
    tr_den = 36 * gn * DEN * SCALE * SCALE
    delta_rayleigh_up = ceil_div(dir_num * UNIT, dir_den)
    delta_action_up = sqrt_up(dir_num * tr_num, dir_den * tr_den)

    Y = res["Y"]
    q_squared = sum(
        ball["wq"][i] * sum(Y[i][j] * v[j] for j in range(8)) ** 2
        for i in range(ball["n"]))
    qhat_up = sqrt_up(q_squared, SCALE * SCALE * vnorm)
    full_Qres_up = sqrt_up(gv, 6 * DEN * DEN * SCALE * SCALE * vnorm)
    bx_num = sum(
        ball["wq"][i] * sum(row[j] * v[j] for j in range(8)) ** 2
        for i, row in enumerate(ball["C"]) if row is not None)
    Bx_up = sqrt_up(bx_num, vnorm)
    via_B = ceil_div(Bx_up * DEN, gammaz)
    via_Q = qhat_up + ceil_div(full_Qres_up * DEN, gammaz)
    RzBx_up = min(via_B, via_Q)
    if RzBx_up <= 0:
        refuse("zero_RzBx")

    B2x6 = coupling_B2x6(ball)
    drift = max(a-lo, hi-a)
    bare_drift_up = ceil_div(drift * UNIT, DEN)
    old_extra = ceil_div(drift * B2x6 * DEN * UNIT,
                         6 * gammahi * gammaz)
    new_extra = ceil_div(drift * B_FROB * RzBx_up, gammahi)
    best_extra = min(old_extra, new_extra)

    # Full residual for S(E)x at the true E, including the scalar drift.
    full_up = Unormal_up + delta_action_up + bare_drift_up + best_extra
    full_sin_up = ceil_div(full_up * UNIT, gap)

    # Rayleigh estimate mu=<x,S(E)x>, BEFORE using the centered residual.
    # Mu must lie strictly inside the isolated Schur null gap: otherwise a
    # zero centered residual could correspond to a DIFFERENT eigenvector.
    mu_up = abs_mu_U + delta_rayleigh_up + bare_drift_up + best_extra
    centered_up = Ucenter_up + delta_action_up + best_extra
    null_identified = int(mu_up < gap)
    if null_identified:
        centered_sin_up = ceil_div(centered_up * UNIT, gap - mu_up)
        selected = min(full_sin_up, centered_sin_up)
    else:
        centered_sin_up = -1
        selected = full_sin_up
    if selected > full_sin_up:
        refuse("centered_cannot_weaken_certified_bound")

    emit("Y137_CENTER_POINT", sample_num=a, den=DEN,
         E_lo_num=lo, E_hi_num=hi, microbracket_source="PR182",
         U_sha256=uhash, G_sha256=ghash, flat_W_norm2=vnorm,
         B_Frobenius_norm2=B2x6 // 6,
         Bx_upper_per_trillion=Bx_up,
         Qhat_upper_per_trillion=qhat_up,
         full_Qres_upper_per_trillion=full_Qres_up,
         RzBx_via_B_upper_per_trillion=via_B,
         RzBx_via_Q_upper_per_trillion=via_Q,
         U_normal_upper_per_trillion=Unormal_up,
         U_centered_upper_per_trillion=Ucenter_up,
         U_Rayleigh_abs_upper_per_trillion=abs_mu_U,
         Schur_PSD_action_upper_per_trillion=delta_action_up,
         Schur_PSD_Rayleigh_upper_per_trillion=delta_rayleigh_up,
         energy_scalar_drift_upper_per_trillion=bare_drift_up,
         energy_global_extra_upper_per_trillion=old_extra,
         energy_directional_extra_upper_per_trillion=new_extra,
         energy_selected_extra_upper_per_trillion=best_extra,
         Schur_null_gap_lower_per_trillion=gap,
         Rayleigh_mu_abs_upper_per_trillion=mu_up,
         mu_strictly_inside_null_gap=null_identified,
         centered_residual_upper_per_trillion=centered_up,
         full_residual_upper_per_trillion=full_up,
         full_sin_upper_per_trillion=full_sin_up,
         centered_sin_upper_per_trillion=centered_sin_up,
         selected_sin_upper_per_trillion=selected,
         nonvacuous=int(selected < UNIT),
         normalized_state_transfer_below_1_over_700="NOT_PROVED",
         true_Wilson_E1_E2_weight="OPEN")
    return (int(selected < UNIT), null_identified)


def main():
    freeze()
    ball = source.build_k3()
    if (ball["n"], ball["nf"]) != (155378, 1985218):
        refuse("graph_census")
    out = [inspect(ball, *row) for row in ROWS]
    emit("Y137_CENTER_VERDICT", samples=len(out),
         nonvacuous=sum(z[0] for z in out),
         null_branch_identified=sum(z[1] for z in out),
         source_energy_windows="PR182_14_point_count_certified",
         actual_Wilson_first_weight="OPEN",
         method="W_exact_centered_residual_directional_Q_dual_gate")


if __name__ == "__main__":
    main()
