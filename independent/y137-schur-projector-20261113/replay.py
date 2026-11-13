#!/usr/bin/env python3
"""Issue #137: 8-flat source-certified Schur null projector residual envelope.

This is a conservative upper-bound test, not a declaration of Wilson weight.
All terms are integer/rational with directed integer square-root ceilings.
"""
import os
import sys
from math import isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "y137-liftfree-k3-20261113"))
import k3_common as k
import y137_k3_sector_isolation as mod

DEN = 1000000000
DIGITS = 1000000000000
FLOOR_SCALED = 94068200000
PS = 1000000
FLOOR = 94068200
SCALE = 1000000000000
STEPS = 20
# Energy bounds 1/10^7, sample energies 1/10^9.
ROWS = (
    (69909875505, 699080000, 699200000,
     (1000000000, 997935625, 996905915, 38054797, 37920545, 2788116, 51160, 51160),
     "0752df3c1941c67316cc6834795182fdaccdaba0ca5fc711221e7217d0dbaa1c",
     "83efba692ef3a8451a68049ee996451877ac4d646ae2f357fc0b604b48db0b0f",
     28000000000),
    (69949729820, 699480000, 699567503,
     (111045317, -38181375, -112233220, 1000000000,
      979217930, 216249666, 4169404, 4169404),
     "9229dfad058157d80287cb1ab188c1034bdbb16394dec045b540890d8bb05109",
     "e42df65b4b269095177fc609d06b4576917901c598f8ebd477eaa58b61b90d8d",
     11949000000),
)


def emit(label, **fields):
    print(label + "|" + "|".join(str(a) + "=" + str(b) for a, b in fields.items())
          + "|json=0", flush=True)


def refuse(label):
    emit("Y137_PROJ_REFUSE", reason=label)
    raise SystemExit(1)


def ceil_div(a, b):
    if a < 0 or b <= 0:
        refuse("ceil_sign")
    return (a + b - 1) // b


def ceil_isqrt(n):
    if n < 0:
        refuse("sqrt_sign")
    a = isqrt(n)
    return a if a * a == n else a + 1


def sqrt_frac_ceil(n, d):
    if n < 0 or d <= 0:
        refuse("sqrt_fraction_sign")
    return ceil_isqrt(ceil_div(n * DIGITS * DIGITS, d))


def quad(M, v):
    return sum(v[i] * M[i][j] * v[j] for i in range(8) for j in range(8))


def inspect(ball, a, lo, hi, v, expect_u, expect_g, gap_lower):
    q = sum(ball["wf"][i] * v[i] * v[i] for i in range(8))
    if q <= 0 or v[6] != v[7]:
        refuse("non_even_normalized_trial")
    zlo = lo * 100
    zhi = hi * 100
    if not (zlo < a < zhi):
        refuse("z_outside_energy_bracket")
    gamma_z_num = FLOOR_SCALED - a
    gamma_u_num = FLOOR_SCALED - zhi
    if min(gamma_z_num, gamma_u_num) <= 0:
        refuse("Q_floor")
    x = mod.threshold_ball(a, DEN, STEPS, SCALE, ball, FLOOR)
    if (x["hu"], x["hg"]) != (expect_u, expect_g):
        refuse("source_U_G_hash_mismatch")
    U, G = x["U"], x["G"]
    uv = [sum(U[i][j] * v[j] for j in range(8)) for i in range(8)]
    # Euclidean W-normalized residual of U/(b*scale^2):
    # || Wp^-1/2 Uv || / (b*scale^2 sqrt(v^T Wp v)).
    # Sum 1/w_i represented by integer numerator with denominator 6.
    numer_u = sum((6 // ball["wf"][i]) * uv[i] * uv[i] for i in range(8))
    denom_u = 6 * DEN * DEN * SCALE * SCALE * SCALE * SCALE * q
    U_norm_up = sqrt_frac_ceil(numer_u, denom_u)

    vvG = quad(G, v)
    if vvG < 0:
        refuse("negative_PSD_direction")
    weighted_trace = sum((6 // ball["wf"][i]) * G[i][i] for i in range(8))
    if weighted_trace < 0:
        refuse("negative_PSD_trace")
    gamma_num = DEN * FLOOR - a * PS
    if gamma_num <= 0:
        refuse("floor_gamma")
    # width direction = PS*vGv / (6*gamma_num*b*scale^2*q).
    # trace width = PS*(weighted_trace/6) / (6*gamma_num*b*scale^2).
    deltav_num = PS * vvG
    deltav_den = 6 * gamma_num * DEN * SCALE * SCALE * q
    trace_num = PS * weighted_trace
    trace_den = 36 * gamma_num * DEN * SCALE * SCALE
    delta_direction_up = sqrt_frac_ceil(deltav_num * trace_num,
                                       deltav_den * trace_den)
    trace_up = ceil_div(trace_num * DIGITS, trace_den)

    # M2 = ||B||_F^2 = sum_i,k (wq_i/wf_k)*C_ik^2,
    # with six as common orbit-weight denominator.
    M2x6 = 0
    for i, ci in enumerate(ball["C"]):
        if ci is None:
            continue
        wi = ball["wq"][i]
        for j, edge in enumerate(ci):
            M2x6 += (6 // ball["wf"][j]) * wi * edge * edge
    if M2x6 <= 0:
        refuse("zero_flat_coupling")

    # ||S(E)-S(z)|| <= |E-z| [1 + M2/((gamma-E)(gamma-z))]
    # for E anywhere in the certified bracket; M2 <= M2x6/6.
    drift = max(a - zlo, zhi - a)
    direct_up = ceil_div(drift * DIGITS, DEN)
    indirect_up = ceil_div(
        drift * M2x6 * DEN * DIGITS,
        6 * gamma_u_num * gamma_z_num)
    total_up = U_norm_up + delta_direction_up + direct_up + indirect_up
    # Gap strict > gap_lower/DIGITS implies sin(angle)
    # < total_up / gap_lower as an interval-conservative upper bound.
    sin_up = ceil_div(total_up * DIGITS, gap_lower)
    # Unit flat vectors, with phase optimally chosen: |x-v| <= sqrt(2)*sin(angle)
    # sqrt2 rational upwards as 1414213562374/10^12.
    phase_distance_up = ceil_div(sin_up * 1414213562374, DIGITS)
    emit("Y137_PROJ_POINT", sample=str(a) + "/" + str(DEN),
         energy_lo=str(lo) + "/10000000", energy_hi=str(hi) + "/10000000",
         source_U_sha256=expect_u, source_G_sha256=expect_g,
         flat_W_norm2=q,
         U_residual_upper_per_trillion=U_norm_up,
         Schur_trace_upper_per_trillion=trace_up,
         PSD_direction_upper_per_trillion=delta_direction_up,
         energy_drift_direct_upper_per_trillion=direct_up,
         energy_drift_B_bound_upper_per_trillion=indirect_up,
         B_Frobenius_norm2_times6=M2x6,
         full_Schur_null_residual_upper_per_trillion=total_up,
         certified_gap_lower_per_trillion=gap_lower,
         sin_angle_upper_per_trillion=sin_up,
         phase_distance_upper_per_trillion=phase_distance_up,
         nontrivial_projector_bound=int(sin_up < DIGITS),
         exact_eigenprojector="NOT_YET_ENCLOSED")
    return int(sin_up < DIGITS)


def main():
    freeze = open(os.path.join(HERE, "PREDICTION.hbp"), "rb").read()
    if b"status=FROZEN_BEFORE_8D_PROJECTOR_REPLAY" not in freeze:
        refuse("not_frozen")
    if k.SCRIPT_SHA != "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff":
        refuse("source_script_pin")
    ball = k.build_k3()
    if ball["n"] != 155378 or ball["nf"] != 1985218:
        refuse("K3_census")
    verdicts = [inspect(ball, *row) for row in ROWS]
    emit("Y137_PROJ_VERDICT", samples=2,
         nontrivial_projector_bound_count=sum(verdicts),
         source_floor="94068200/1000000",
         Wilson_E1_E2_weight="OPEN",
         proof="rational_W_Schur_residual_plus_monotone_pencil",
         verdict="DIAGNOSTIC_BOUND_ONLY")


if __name__ == "__main__":
    main()
