#!/usr/bin/env python3
"""#137 source-pinned K3: new r9 Schur inertia points and a rational matrix envelope.

Eight points were sealed in PREDICTION.hbp before this script existed.
The module uses the accepted K3 source through k3_common, not a new graph.
It performs only exact integer arithmetic and keeps Wilson weight OPEN.
"""
import os
import sys
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
K3_DIR = os.path.join(PARENT, "y137-liftfree-k3-20261113")
sys.path.insert(0, K3_DIR)
import k3_common as k
import y137_k3_sector_isolation as mod
import check_k3 as independent

DEN = 10000000
SCALE = 10 ** 12
PS = 1000000
GAMMA = 94068200
POINTS = (
    699000000, 699050000, 699080000, 699090000,
    699400000, 699450000, 699480000, 699490000,
)
PRED = os.path.join(HERE, "PREDICTION.hbp")
BASE_LO_E1 = 698900000
BASE_HI_E1 = 69909875505
BASE_LO_E2 = 699346057
BASE_HI_E2 = 69949729820
# The old E2 lower point 69.9346057 has denominator 10^7.
BASE_LO_E2 = 699346057
E3_LO = 699686993


def emit(label, **fields):
    print(label + "|" + "|".join(str(key) + "=" + str(val)
                                for key, val in fields.items()) + "|json=0", flush=True)


def refuse(reason):
    emit("Y137_SCHUR_REFUSE", reason=reason)
    raise SystemExit(1)


def verify_freeze():
    raw = open(PRED, "rb").read()
    if b"status=FROZEN_BEFORE_NEW_K3_EVALUATIONS" not in raw:
        refuse("not_frozen")
    expected = ",".join(str(a) for a in POINTS).encode("ascii")
    if expected not in raw:
        refuse("changed_point_grid")
    if b"floor=94068200/1000000" not in raw:
        refuse("floor")
    if k.NEW_G != GAMMA or k.PS != PS or k.K3_B != DEN:
        refuse("source_or_denominator")
    if k.SCRIPT_SHA != "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff":
        refuse("source_pin")
    emit("Y137_SCHUR_FREEZE", status="PASS", points=len(POINTS),
         floor=str(GAMMA) + "/" + str(PS))


def psd_principal_minors(M):
    """All 255 principal minors >= 0 is an exact PSD criterion for real symmetric M."""
    n = len(M)
    if any(M[i][j] != M[j][i] for i in range(n) for j in range(n)):
        refuse("non_symmetric_gram")
    for mask in range(1, 1 << n):
        idx = [i for i in range(n) if mask & (1 << i)]
        sub = [[M[i][j] for j in idx] for i in idx]
        if mod.c.det(sub) < 0:
            refuse("Gram_not_positive_semidefinite")
    return (1 << n) - 1


def independent_counts(r):
    L, U = r["L"], r["U"]
    if independent.negative_count(L) != r["nlo"]:
        refuse("charpoly_disagrees_on_lower")
    if independent.negative_count(U) != r["nhi"]:
        refuse("charpoly_disagrees_on_upper")
    le, lo = independent.split(L)
    ue, uo = independent.split(U)
    ans = (independent.negative_count(le), independent.negative_count(ue),
           int(lo < 0), int(uo < 0))
    s = mod.sectors(r)
    exp = tuple(s[name] for name in ("even_lower", "even_upper", "odd_lower", "odd_upper"))
    if ans != exp:
        refuse("independent_sector_inertia")
    return ans


def trace_envelope(r, weights, a):
    """Trace bound on ||W_P^-1/2 (U/b-Lscaled/b) W_P^-1/2||."""
    gamma_num = DEN * GAMMA - a * PS
    if gamma_num <= 0 or len(weights) != 8:
        refuse("source_floor")
    if any(6 % weight for weight in weights):
        refuse("non_s3_weight")
    # Delta in the W metric:
    #   S(z) in [U - PS*G/(6*gamma_num), U] / (DEN*SCALE^2).
    # Thus 0<=Delta and ||W^-1/2 Delta W^-1/2|| <= tr(...) precisely.
    # Sum_i G_ii/weight_i = [sum_i (6/weight_i)G_ii]/6.
    numer = PS * sum((6 // weights[i]) * r["G"][i][i] for i in range(8))
    denom = 36 * gamma_num * DEN * SCALE * SCALE
    common = gcd(numer, denom)
    numer //= common
    denom //= common
    # Directed upper round to 10^-9 (safe: ceil).
    up_ppb = (numer * 1000000000 + denom - 1) // denom
    # Strict Schur-null-direction gap from prior accepted E2-E1 > .01.
    # The perturbation-to-gap ratio is at most 100*trace(Delta).
    over_gap_ppm = (numer * 100000000 + denom - 1) // denom
    if numer <= 0 or denom <= 0:
        refuse("non_positive_width")
    return numer, denom, up_ppb, over_gap_ppm


def main():
    verify_freeze()
    ball = k.build_k3()
    if ball["n"] != 155378 or ball["nf"] != 1985218:
        refuse("ball_census")
    weights = ball["wf"]
    if len(weights) != 8:
        refuse("flat_weights")
    results = []
    previous = (-1, -1)
    for a in POINTS:
        if a >= E3_LO or a <= BASE_LO_E1:
            refuse("grid_outside_E3")
        # The accepted script builds the full K3 U, G and complete shell-4 residual.
        result = mod.threshold_ball(a, DEN, k.K3_STEPS, SCALE, ball, GAMMA)
        if result["nlo"] < result["nhi"]:
            refuse("sandwich_inverted")
        counts = independent_counts(result)
        if psd_principal_minors(result["G"]) != 255:
            refuse("Gram_PSD")
        lower_count = result["nhi"]
        upper_count = result["nlo"]
        if lower_count < previous[0] or upper_count < previous[1]:
            refuse("threshold_inertia_not_monotone")
        previous = (lower_count, upper_count)
        numer, denom, ppb, ppm = trace_envelope(result, weights, a)
        settled = lower_count == upper_count
        if settled and lower_count not in (0, 1, 2):
            refuse("unexpected_complete_count_below_E3")
        results.append((a, lower_count, upper_count, settled))
        emit("Y137_SCHUR_POINT", z_num=a, z_den=DEN,
             count_min=lower_count, count_max=upper_count,
             even_L=counts[0], even_U=counts[1],
             odd_L=counts[2], odd_U=counts[3], settled=int(settled),
             W_trace_width_num=numer, W_trace_width_den=denom,
             W_trace_width_upper_ppb=ppb,
             W_width_over_0p01_upper_ppm=ppm,
             Gram_principal_minors=255, independent_charpoly="PASS",
             U_sha256=result["hu"], G_sha256=result["hg"], L_sha256=result["hl"])
    # Derive bounds only from complete count sandwiches, plus old ACCEPTED
    # outer windows; never substitute Ritz root estimates for certified counts.
    lo1, hi1 = BASE_LO_E1, BASE_HI_E1
    lo2, hi2 = BASE_LO_E2, BASE_HI_E2
    for a, lower, upper, settled in results:
        if not settled:
            continue
        if lower == 0:
            lo1 = max(lo1, a)
        elif lower == 1:
            hi1 = min(hi1, a)
            lo2 = max(lo2, a)
        elif lower == 2:
            hi2 = min(hi2, a)
    # The K3 Ritz upper for E1 was historically reported at a / 10^9,
    # whereas all new points use 10^7. Normalize before comparing.
    # E1 upper 69.909875505 has numerator 69909875505 / 10^9.
    # E2 upper 69.949729820 has numerator 69949729820 / 10^9.
    # Existing upper endpoints above are in 10^9 units.
    hi1 = min(hi1 * 100, BASE_HI_E1)
    hi2 = min(hi2 * 100, BASE_HI_E2)
    # Existing lower E1 = 69.89 and lower E2 = 69.9346057.
    lo1 = max(lo1, BASE_LO_E1)
    lo2 = max(lo2, BASE_LO_E2)
    if not (lo1 * 100 < hi1 and lo2 * 100 < hi2):
        refuse("inconsistent_bracket")
    emit("Y137_SCHUR_BRACKETS", E1_lower=str(lo1) + "/10000000",
         E1_upper=str(hi1) + "/1000000000",
         E2_lower=str(lo2) + "/10000000",
         E2_upper=str(hi2) + "/1000000000",
         E3_lower=str(E3_LO) + "/10000000",
         settled_points=sum(1 for row in results if row[3]),
         points=len(results), source_floor="94068200/1000000",
         proof="conditional_on_173_176_177")
    emit("Y137_SCHUR_VERDICT", status="BRACKET_PROBE_COMPLETE",
         Wilson_weight="OPEN", projector_direction="NOT_COMPUTED",
         O_eff="NOT_COMPUTED")


if __name__ == "__main__":
    main()
