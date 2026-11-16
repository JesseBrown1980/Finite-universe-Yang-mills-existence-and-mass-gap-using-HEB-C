#!/usr/bin/env python3
"""Stage F: source-pinned four-moment full-state error decomposition and trial line search.

The accepted Stage E mu3 / 4-moment matrices and 3-moment energy windows are unchanged.
Only fixed, predeclared integer interpolants of accepted versus centered E1/E2 flat
vectors are tested. A result may be sharper than Stage E; this is a NEW research
certificate requiring external review, never an automatic Wilson positivity PASS.

All arithmetic is exact integer/rational with outward integer square roots.
"""
import os
import sys
from math import isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
INDEP = os.path.dirname(HERE)
for name in ("y137-four-moment-fullstate-20261116",
             "y137-mu3-real-20261115", "y137-mu3-acceptance-20261115",
             "y137-moment-radau-20261114",
             "y137-radau-recentred-angle-20261114",
             "y137-radau-fullstate-windows-20261115"):
    sys.path.insert(0, os.path.join(INDEP, name))
import four_moment_transfer as stge
import d_real_four_moment as src
import mu3_acceptance as exact
import moment_radau as mr
import recentred_angle as ra
import fullstate_windows as fw

UNIT, DEN, FLOOR = ra.UNIT, ra.DEN, ra.FLOOR
STAGE_E_BASE = (3235251105, 8676646901)
STAGE_E_TOTAL = 11911898006
FRACTIONS = (0, 1, 2, 3, 4, 5, 6, 7, 8)
SCALE = 8


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def pinned_stage_e_receipt():
    path = os.path.join(INDEP, "y137-four-moment-fullstate-20261116",
                        "RESULT-CLOUD-STAGE-E-20261116.hbp")
    with open(path, encoding="ascii") as handle:
        rows = handle.read().splitlines()
    verdict = [r for r in rows if r.startswith("Y137_E_VERDICT|")]
    moved = [r for r in rows if r.startswith("Y137_E_CELL|case=CENTRE_MOVED|")]
    need(len(verdict) == len(moved) == 1, "unsealed_or_duplicate_stage_E_result")
    need(("actual_four_moment_combined_per_trillion=" + str(STAGE_E_TOTAL)) in verdict[0]
         and "three_moment_best_regression=PASS" in verdict[0]
         and "first_Wilson_weight=HOLD" in verdict[0],
         "accepted_stage_E_verdict_changed")
    need(("four_E1_error=" + str(STAGE_E_BASE[0])) in moved[0]
         and ("four_E2_error=" + str(STAGE_E_BASE[1])) in moved[0],
         "accepted_stage_E_components_changed")


def exact_matrices():
    with open(src.MU3_FILE, encoding="ascii") as handle:
        authentic = src.parse_pinned_mu3(handle.read())
    windows = stge.three_moment_windows()
    result = []
    for i, z in enumerate(src.FROZEN):
        u, m0, m1, m2 = src.accepted_old_moments(i)
        m3 = exact.F(authentic[z])
        lo3, hi3 = exact.bracket3(u, m0, m1, m2, FLOOR - z, 468000000000 - z)
        lo4, hi4 = exact.bracket4(u, m0, m1, m2, m3, FLOOR - z, 468000000000 - z)
        need(exact.pd(exact.sub(lo4, lo3)) and exact.pd(exact.sub(hi3, hi4))
             and exact.pd(exact.sub(hi4, lo4)), "authentic_four_moment_nesting")
        ratio = exact.ppm(exact.trace(exact.sub(hi4, lo4)),
                          exact.trace(exact.sub(hi3, lo3)))
        need(ratio == stge.EXPECTED_WIDTH_RATIO[i], "authentic_width_ratio_changed")
        result.append(stge.all_refs(lo4, hi4)["CENTRE"])
    return windows, result


def energy_gap(windows, i):
    common = windows[1][0] - windows[0][1]
    d = min(common, ra.E3_LO - windows[1][1]) if i == 1 else common
    need(d > 0, "nonpositive_spectral_gap")
    return d * (UNIT // DEN)


def outward_diagnostics(refs, windows, i, fraction):
    need(fraction in FRACTIONS, "interpolation_fraction_out_of_range")
    z, lo, hi, v0 = ra.ROWS[i][:4]
    cn, cd, wn, wd = refs
    moved = ra.recentre(cn, list(v0))
    v = [(SCALE - fraction) * a + fraction * b for a, b in zip(v0, moved)]
    need(any(v), "interpolated_trial_zero")
    dist = stge.flat_distance(list(v0), v)
    qlo, qhi = fw.Q_NORMS[i]
    if fraction == 0:
        need(dist == 0, "original_sample_has_positive_displacement")
    spread = ra.ceil_div(fw.B_NORM_UP * dist * DEN, UNIT * (FLOOR - z))
    qlo, qhi = max(0, qlo - spread), qhi + spread
    triangle = fw.sqrt_ceil(dist * dist + spread * spread)
    angle = ra.angle(cn, cd, wn, wd, v, z, lo, hi, ra.ROWS[i][5])
    drift = max(z - lo, hi - z)
    mu0 = angle["mu"] - angle["extra"] - ra.ceil_div(drift * UNIT, DEN)
    wlo, whi = windows[i]
    de = max(z - wlo, whi - z)
    gamma = FLOOR - whi
    extra = ra.ceil_div(de * fw.B_NORM_UP * qhi, UNIT * gamma)
    mu = mu0 + ra.ceil_div(de * UNIT, DEN) + extra
    gap = energy_gap(windows, i)
    need(0 < mu < gap, "spectral_separation_not_certified")
    sin = ra.ceil_div((angle["Hcenter"] + angle["action"] + extra) * UNIT, gap - mu)
    need(sin < UNIT, "angle_not_certified")
    coslower = isqrt(UNIT * UNIT - sin * sin)
    flat = fw.sqrt_ceil(2 * UNIT * (UNIT - coslower))
    qrot = ra.ceil_div(fw.B_NORM_UP * flat * DEN, UNIT * gamma)
    qen = ra.ceil_div(de * qhi, gamma)
    qdiff = qrot + qen
    full_dist = fw.sqrt_ceil(flat * flat + qdiff * qdiff)
    sample_norm = isqrt(UNIT * UNIT + qlo * qlo)
    true_norm = isqrt(UNIT * UNIT + max(0, qlo - qdiff) ** 2)
    normalized = ra.ceil_div(full_dist * UNIT, isqrt(sample_norm * true_norm))
    error = normalized + triangle
    historical = fw.compose(angle["Hcenter"] + angle["action"], mu0, gap, z,
                             wlo, whi, qlo, qhi)
    need(error == historical["error"] + triangle and sin == historical["sin"],
         "independent_error_decomposition_mismatch")
    return dict(error=error, norm_error=normalized, triangle=triangle,
                displacement=dist, Q_sample_spread=spread,
                sine=sin, centered_residual=angle["Hcenter"],
                width_action=angle["action"], energy_extra=extra,
                q_rot=qrot, q_energy=qen, q_total=qdiff,
                spectral_gap=gap, energy_window_width=whi-wlo,
                mu=mu)


def main():
    pinned_stage_e_receipt()
    windows, refs = exact_matrices()
    data = []
    for i in range(2):
        rows = []
        for alpha in FRACTIONS:
            out = outward_diagnostics(refs[i], windows, i, alpha)
            rows.append(out)
            mr.emit("Y137_F_ROW", level=i+1, alpha_eighths=alpha,
                    normalized_error=out["norm_error"],
                    triangle_cost=out["triangle"],
                    total_error=out["error"],
                    sample_displacement=out["displacement"],
                    Q_sample_spread=out["Q_sample_spread"],
                    flat_angle_sine=out["sine"],
                    centered_residual=out["centered_residual"],
                    width_action=out["width_action"],
                    energy_extra=out["energy_extra"],
                    Q_rotation=out["q_rot"], Q_energy_drift=out["q_energy"],
                    Q_total=out["q_total"],
                    effective_gap=out["spectral_gap"])
        need(rows[SCALE]["error"] == STAGE_E_BASE[i],
             "alpha_one_does_not_reproduce_accepted_stage_E")
        data.append(rows)
    # The two directions may be moved independently, but the original fixed
    # Wilson amplitude is retained and every move pays its triangle cost.
    ia = min(FRACTIONS, key=lambda j: data[0][j]["error"])
    ib = min(FRACTIONS, key=lambda j: data[1][j]["error"])
    best = data[0][ia]["error"] + data[1][ib]["error"]
    # This is a structural impossibility for the CURRENT alpha=1 Stage E route
    # when the original fixed Wilson sample remains the comparison target.
    move_floor = data[0][SCALE]["displacement"] + data[1][SCALE]["displacement"]
    need(move_floor > UNIT // 700, "expected_stage_E_moved_sample_floor_regression")
    need(700 * data[1][SCALE]["displacement"] > UNIT,
         "E2_displacement_alone_no_longer_above_gate")
    for bad in (-1, SCALE + 1):
        try:
            outward_diagnostics(refs[0], windows, 0, bad)
        except ValueError:
            pass
        else:
            raise ValueError("out_of_range_fraction_accepted")
    mr.emit("Y137_F_VERDICT",
            source_frozen="PASS", stage_E_exact_reproduction="PASS",
            independent_error_identity="PASS",
            out_of_range_controls="REFUSED",
            best_alpha_E1_eighths=ia, best_alpha_E2_eighths=ib,
            best_E1_error=data[0][ia]["error"],
            best_E2_error=data[1][ib]["error"], best_total_error=best,
            previous_stage_E_total=STAGE_E_TOTAL,
            stage_E_move_floor=move_floor,
            stage_E_move_route_alone_blocks_1_over_700="PROVED",
            sufficient_gate=int(700 * best < UNIT),
            first_Wilson_weight="HOLD_PENDING_INDEPENDENT_REVIEW",
            issue_137="OPEN")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, ZeroDivisionError) as exc:
        print("Y137_F_REFUSE|reason={}|json=0".format(exc), flush=True)
        raise SystemExit(1) from None
