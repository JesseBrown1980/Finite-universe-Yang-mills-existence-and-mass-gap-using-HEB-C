#!/usr/bin/env python3
"""#137 Stage E: authentic four-moment Schur interval into exact W-normalization gate.

This is a new calculation based on already accepted Stage C/D rational moments.
It retains the *certified three-moment energy windows* as a conservative input;
it does not infer an eigenvector-angle reduction from the four-moment trace width.

All arithmetic is integer and exact rational, with outward rounded roots.
Original #180 Wilson positive fixed-sample and #187 full-state transfer premises
remain source-conditional. A prospective gate crossing still requires review.
"""
import os
import sys
from math import gcd, isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
INDEP = os.path.dirname(HERE)
for name in ("y137-mu3-real-20261115", "y137-mu3-acceptance-20261115",
             "y137-moment-radau-20261114", "y137-radau-recentred-angle-20261114",
             "y137-radau-fullstate-windows-20261115"):
    sys.path.insert(0, os.path.join(INDEP, name))
import d_real_four_moment as source
import mu3_acceptance as exact
import moment_radau as mr
import recentred_angle as ra
import fullstate_windows as fw

UNIT, DEN, N, WF, FLOOR = ra.UNIT, ra.DEN, ra.N, ra.WF, ra.FLOOR
EXPECTED_OLD_BEST = 14153976076
EXPECTED_WIDTH_RATIO = (600184, 600451)
EXPECTED_WINDOWS = ((69909429421, 69909586556),
                    (69949264147, 69949433884))


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def as_pair(matrix):
    """Reduced common-denominator integral representation of a rational matrix."""
    den = exact.common_den(matrix)
    num = [[int(x * den) for x in row] for row in matrix]
    common = den
    for row in num:
        for val in row:
            common = gcd(common, abs(val))
    need(common > 0, "invalid_matrix_common_factor")
    return [[x // common for x in row] for row in num], den // common


def cross_pair(a, ad, b, bd, negative=False):
    bn = -1 if negative else 1
    num = mr.add(mr.scale(a, bd), mr.scale(b, bn * ad))
    den = ad * bd
    common = den
    for row in num:
        for val in row:
            common = gcd(common, abs(val))
    need(common > 0, "invalid_cross_pair_factor")
    return [[x // common for x in row] for row in num], den // common


def all_refs(lo, hi):
    ln, ld = as_pair(lo)
    hn, hd = as_pair(hi)
    wn, wd = cross_pair(hn, hd, ln, ld, negative=True)
    mn, md = cross_pair(hn, hd, ln, ld)
    return {"UPPER": (hn, hd, wn, wd),
            "LOWER": (ln, ld, wn, wd),
            "CENTRE": (mn, 2 * md, wn, 2 * wd)}


def flat_distance(v0, v1):
    dot = sum(WF[k] * v0[k] * v1[k] for k in range(N))
    need(dot > 0, "moved_vector_bad_orientation")
    n0, n1 = ra.wnorm(v0), ra.wnorm(v1)
    need(dot * dot <= n0 * n1, "invalid_weighted_cauchy")
    lower_cos = isqrt((dot * dot * UNIT * UNIT) // (n0 * n1))
    return fw.sqrt_ceil(2 * UNIT * (UNIT - lower_cos))


def three_moment_windows():
    src = mr.read(mr.CACHE, "source", "Y137_CACHE_POINT")
    m1 = mr.read(mr.MU1, "mu1", "Y137_MU1_COMPLETE_POINT")
    m2 = mr.read(mr.MU2, "mu2", "Y137_D11_MU2_POINT")
    windows = []
    for i in range(2):
        z, lo, hi = ra.ROWS[i][:3]
        hn, hd, ln, ld = fw.bracket(i, src[i], m1[i], m2[i])
        k = i + 1
        tlo, thi = fw.threshold(ln, ld, k)[0], fw.threshold(hn, hd, k)[1]
        need(tlo < thi < 0, "missing_three_moment_inertia_bracket")
        gz = FLOOR - z
        wlo = max(lo, z + (tlo // (UNIT // DEN)))
        whi = min(hi, z - ((-thi) * gz * gz) //
                   ((gz * gz + 72 * DEN * DEN) * (UNIT // DEN)))
        need(lo <= wlo < whi <= hi, "invalid_three_moment_energy_window")
        windows.append((wlo, whi))
    need(tuple(windows) == EXPECTED_WINDOWS, "historical_three_moment_window_regression")
    return windows


def cell(refs, windows, i, way, moved):
    z, lo, hi, accepted = ra.ROWS[i][:4]
    cn, cd, wn, wd = refs[way]
    v = list(accepted)
    qlo, qhi = fw.Q_NORMS[i]
    add, dist = 0, 0
    if moved:
        v = ra.recentre(cn, v)
        dist = flat_distance(list(accepted), v)
        gz = FLOOR - z
        spread = ra.ceil_div(fw.B_NORM_UP * dist * DEN, UNIT * gz)
        qlo, qhi = max(0, qlo - spread), qhi + spread
        add = fw.sqrt_ceil(dist * dist + spread * spread)
    gap1 = (windows[1][0] - windows[0][1]) * (UNIT // DEN)
    gap2 = min(windows[1][0] - windows[0][1],
               ra.E3_LO - windows[1][1]) * (UNIT // DEN)
    angle = ra.angle(cn, cd, wn, wd, v, z, lo, hi, ra.ROWS[i][5])
    drift = max(z - lo, hi - z)
    mu0 = angle["mu"] - angle["extra"] - ra.ceil_div(drift * UNIT, DEN)
    result = fw.compose(angle["Hcenter"] + angle["action"], mu0, (gap1, gap2)[i],
                        z, windows[i][0], windows[i][1], qlo, qhi)
    return {"error": result["error"] + add, "sin": result["sin"],
            "residual": angle["Hcenter"], "action": angle["action"],
            "moved_distance": dist, "energy_extra": result["extra"]}


def main():
    with open(source.MU3_FILE, encoding="ascii") as f:
        authentic = source.parse_pinned_mu3(f.read())
    windows = three_moment_windows()
    levels = []
    for i, z in enumerate(source.FROZEN):
        u, m0, m1, m2 = source.accepted_old_moments(i)
        m3 = exact.F(authentic[z])
        lo3, hi3 = exact.bracket3(u, m0, m1, m2, FLOOR - z, 468000000000 - z)
        lo4, hi4 = exact.bracket4(u, m0, m1, m2, m3, FLOOR - z, 468000000000 - z)
        need(exact.pd(exact.sub(lo4, lo3)) and
             exact.pd(exact.sub(hi3, hi4)) and
             exact.pd(exact.sub(hi4, lo4)), "real_four_moment_strict_nesting")
        # Deliberately reversed bracket must fail the positive-definiteness test.
        need(not exact.pd(exact.sub(lo4, hi4)), "reversed_bracket_false_control")
        ratio = exact.ppm(exact.trace(exact.sub(hi4, lo4)),
                          exact.trace(exact.sub(hi3, lo3)))
        need(ratio == EXPECTED_WIDTH_RATIO[i], "frozen_stage_D_width_regression")
        levels.append((all_refs(lo3, hi3), all_refs(lo4, hi4)))
        mr.emit("Y137_E_SOURCE", sample_num=z, authentic_mu3_six_sha256=
                source.EXPECTED_MU3_SIX_SHA[z], exact_width_ratio_per_million=ratio,
                frozen_three_window_lo=windows[i][0],
                frozen_three_window_hi=windows[i][1],
                reversed_bracket="REFUSED")
    old, now = {}, {}
    for way, moved in (("UPPER", False), ("LOWER", False),
                       ("CENTRE", False), ("CENTRE", True)):
        tag = way + ("_MOVED" if moved else "_KEPT")
        a, b = [], []
        for i in range(2):
            a.append(cell(levels[i][0], windows, i, way, moved))
            b.append(cell(levels[i][1], windows, i, way, moved))
        old[tag] = sum(x["error"] for x in a)
        now[tag] = sum(x["error"] for x in b)
        mr.emit("Y137_E_CELL", case=tag,
                three_moment_combined_per_trillion=old[tag],
                four_moment_combined_per_trillion=now[tag],
                four_E1_error=b[0]["error"], four_E2_error=b[1]["error"],
                four_E1_residual=b[0]["residual"], four_E2_residual=b[1]["residual"],
                four_E1_width_action=b[0]["action"],
                four_E2_width_action=b[1]["action"],
                four_E1_moved_distance=b[0]["moved_distance"],
                four_E2_moved_distance=b[1]["moved_distance"])
    need(old["CENTRE_KEPT"] == 15173455813,
         "accepted_three_moment_centre_kept_not_reproduced")
    need(old["CENTRE_MOVED"] == EXPECTED_OLD_BEST,
         "accepted_three_moment_best_not_reproduced")
    best = min(now.values())
    selected = min(now, key=now.get)
    mr.emit("Y137_E_VERDICT", energies="2_OF_2_AUTHENTIC",
            three_moment_best_regression="PASS",
            stage_D_width_regression="PASS", negative_controls="PASS",
            best_case=selected,
            actual_four_moment_combined_per_trillion=best,
            previous_accepted_best_per_trillion=EXPECTED_OLD_BEST,
            strict_gate_numerator=1, strict_gate_denominator=700,
            sufficient_gate=int(700 * best < UNIT),
            first_Wilson_weight=("CANDIDATE_REQUIRES_INDEPENDENT_REVIEW"
                                 if 700 * best < UNIT else "HOLD"),
            issue_137="OPEN")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, ZeroDivisionError) as exc:
        print("Y137_E_REFUSE|reason={}|json=0".format(exc), flush=True)
        raise SystemExit(1) from None
