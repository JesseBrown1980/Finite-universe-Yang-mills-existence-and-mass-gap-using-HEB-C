#!/usr/bin/env python3
"""#137: pre-frozen 14-point exact K3 inertia microbrackets near E1/E2.

The independent 8x8 and 7x7 charpoly recount and all 255 PSD principal
minors are evaluated from the pinned, complete K3 source. All arithmetic
is integer; prior Ritz-root positions choose points but are not proof inputs.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INDEP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(INDEP, "y137-liftfree-k3-20261113"))
import k3_common as k
import y137_k3_sector_isolation as mod
import check_k3 as independent

DEN = 1000000000
SCALE = 10 ** 12
FLOOR = 94068200
STEPS = 20
E1_POINTS = (
    69908100000, 69908500000, 69909500000, 69909875505,
    69909880000, 69910000000, 69912000000,
)
E2_POINTS = (
    69948100000, 69948500000, 69949500000, 69949729820,
    69949740000, 69950000000, 69952000000,
)
CROSS = {
    69909875505: ("0752df3c1941c67316cc6834795182fdaccdaba0ca5fc711221e7217d0dbaa1c",
                  "83efba692ef3a8451a68049ee996451877ac4d646ae2f357fc0b604b48db0b0f"),
    69949729820: ("9229dfad058157d80287cb1ab188c1034bdbb16394dec045b540890d8bb05109",
                  "e42df65b4b269095177fc609d06b4576917901c598f8ebd477eaa58b61b90d8d"),
}
# Existing accepted mainline windows, lifted to denominator 10^9.
SOURCE_E1 = (69908000000, 69920000000)
SOURCE_E2 = (69948000000, 69956750300)
SOURCE_E3_LO = 69968699300


def emit(label, **pairs):
    print(label + "|" + "|".join(str(k) + "=" + str(v)
                                for k, v in pairs.items()) + "|json=0", flush=True)


def refuse(label):
    emit("Y137_MICRO_REFUSE", reason=label)
    raise SystemExit(1)


def pin():
    freeze = open(os.path.join(HERE, "PREDICTION.hbp"), "rb").read()
    if b"SEALED_BEFORE_MICROBRACKET_EVALUATION" not in freeze:
        refuse("freeze_missing")
    for label, points in (("E1", E1_POINTS), ("E2", E2_POINTS)):
        row = b"Y137_MICRO_" + label.encode("ascii") + b"|points=" + (
            ",".join(str(x) for x in points).encode("ascii"))
        if row + b"|json=0" not in freeze:
            refuse("freeze_grid_changed")
    if k.SCRIPT_SHA != "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff":
        refuse("source_sha_changed")
    if not (k.NEW_G == FLOOR and k.K3_SCALE == SCALE and k.K3_STEPS == 12):
        refuse("floor_source_changed")
    if len(E1_POINTS + E2_POINTS) != 14:
        refuse("grid_length")
    emit("Y137_MICRO_FREEZE", status="PASS", pre_result=1, points=14,
         floor=str(FLOOR) + "/1000000", steps=STEPS, scale=SCALE)


def psd_check(G):
    if any(G[i][j] != G[j][i] for i in range(8) for j in range(8)):
        refuse("G_nonsymmetric")
    for mask in range(1, 256):
        idx = [i for i in range(8) if mask & (1 << i)]
        sm = [[G[i][j] for j in idx] for i in idx]
        if mod.c.det(sm) < 0:
            refuse("G_not_PSD")
    return 255


def recount(result):
    U, L = result["U"], result["L"]
    nu, nl = independent.negative_count(U), independent.negative_count(L)
    le, lo = independent.split(L)
    ue, uo = independent.split(U)
    counts = (independent.negative_count(le), independent.negative_count(ue),
              int(lo < 0), int(uo < 0))
    source = mod.sectors(result)
    expected = tuple(source[k] for k in
                     ("even_lower", "even_upper", "odd_lower", "odd_upper"))
    if (nu, nl) != (result["nhi"], result["nlo"]) or counts != expected:
        refuse("independent_inertia_disagrees")
    if nu > nl or counts[0] < counts[1] or counts[2] < counts[3]:
        refuse("inertia_order_inverted")
    if counts[2] != 0 or counts[3] != 0:
        refuse("odd_level_below_old_certified_bound")
    return nu, nl, counts


def main():
    pin()
    ball = k.build_k3()
    if (ball["n"], ball["nf"]) != (155378, 1985218):
        refuse("K3_census")
    all_points = E1_POINTS + E2_POINTS
    if all_points != tuple(sorted(set(all_points))):
        refuse("points_not_unique_ordered")
    results = []
    for a in all_points:
        if not SOURCE_E1[0] < a < SOURCE_E3_LO:
            refuse("point_outside_known_levels")
        result = mod.threshold_ball(a, DEN, STEPS, SCALE, ball, FLOOR)
        expected = CROSS.get(a)
        if expected and (result["hu"], result["hg"]) != expected:
            refuse("original_source_sample_U_G_hash")
        nmin, nmax, parts = recount(result)
        if psd_check(result["G"]) != 255:
            refuse("PSD_principal_check")
        # The previous mainline E3 isolation is available at every point.
        # Below E3 no more than two full-H levels can lie below z.
        nmax = min(nmax, 2)
        if nmin > nmax:
            refuse("inconsistent_E3_cap")
        results.append((a, nmin, nmax))
        emit("Y137_MICRO_POINT", z_num=a, z_den=DEN, lower_count=nmin,
             upper_count=nmax, even_L=parts[0], even_U=parts[1],
             odd_L=parts[2], odd_U=parts[3],
             source_sha_U=result["hu"], source_sha_G=result["hg"],
             source_sha_L=result["hl"], PSD_principal=255,
             independent_charpoly="PASS", settled=int(nmin == nmax))
    # N(z) is monotone in z; the point-dependent U/L witness matrices
    # themselves need not be monotone. Use only legitimate count closure.
    closed = []
    for i, (a, _, _) in enumerate(results):
        nmin = max(x[1] for x in results[:i + 1])
        nmax = min(x[2] for x in results[i:])
        if nmin > nmax:
            refuse("count_closure_contradiction")
        closed.append((a, nmin, nmax))
        emit("Y137_MICRO_CLOSED", z_num=a, z_den=DEN, lower_count=nmin,
             upper_count=nmax, settled=int(nmin == nmax))
    lo1, hi1 = SOURCE_E1
    lo2, hi2 = SOURCE_E2
    for a, nmin, nmax in closed:
        if nmax == 0:
            lo1 = max(lo1, a)
        if nmin >= 1:
            hi1 = min(hi1, a)
        if nmax <= 1:
            lo2 = max(lo2, a)
        if nmin >= 2:
            hi2 = min(hi2, a)
    if not (lo1 < hi1 < lo2 < hi2 < SOURCE_E3_LO):
        refuse("new_windows_not_ordered")
    gap_lo = lo2 - hi1
    gap_hi = hi2 - lo1
    if gap_lo <= 0:
        refuse("gap_not_positive")
    emit("Y137_MICRO_WINDOWS", E1_lo_num=lo1, E1_hi_num=hi1,
         E2_lo_num=lo2, E2_hi_num=hi2, denominator=DEN,
         gap_lo_num=gap_lo, gap_hi_num=gap_hi,
         E3_lo_num=SOURCE_E3_LO,
         settled_points=sum(int(x[1] == x[2]) for x in closed),
         steps=STEPS, floor="94068200/1000000",
         independent="charpoly_8x8_7x7_PSD_255")
    emit("Y137_MICRO_VERDICT", energy_windows="CERTIFIED_CONDITIONAL_ON_SOURCE_FLOOR",
         actual_Wilson_first_weight="OPEN", projector_transfer="NEXT_GATE")


if __name__ == "__main__":
    main()
