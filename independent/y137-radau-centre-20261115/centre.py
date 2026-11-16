#!/usr/bin/env python3
"""#137: centre plus two half-widths in place of a one-sided bracket. Integers only. See PREDICTION.hbp."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INDEP = os.path.dirname(HERE)
for d in ("y137-moment-radau-20261114", "y137-radau-recentred-angle-20261114", "y137-radau-fullstate-windows-20261115"):
    sys.path.insert(0, os.path.join(INDEP, d))
import moment_radau as mr  # noqa: E402
import recentred_angle as ra  # noqa: E402
import fullstate_windows as fw  # noqa: E402

UNIT, DEN, FLOOR = ra.UNIT, ra.DEN, ra.FLOOR
ONE_SIDED = 19880853054


def main():
    S = mr.read(mr.CACHE, "source", "Y137_CACHE_POINT")
    M1 = mr.read(mr.MU1, "mu1", "Y137_MU1_COMPLETE_POINT")
    M2 = mr.read(mr.MU2, "mu2", "Y137_D11_MU2_POINT")
    parts, windows, ratios = [], [], []
    for i in range(2):
        z, lo, hi, v0, _, gap, _ = ra.ROWS[i]
        Hn, Hd, Ln, Ld = fw.bracket(i, S[i], M1[i], M2[i])
        Wn, Wd = mr.sub(mr.scale(Hn, Ld), mr.scale(Ln, Hd)), Hd * Ld
        Mn, Md = mr.add(mr.scale(Hn, Ld), mr.scale(Ln, Hd)), 2 * Hd * Ld
        one = ra.angle(Hn, Hd, Wn, Wd, list(v0), z, lo, hi, gap)
        cen = ra.angle(Mn, Md, Wn, 2 * Wd, list(v0), z, lo, hi, gap)
        drift = max(z - lo, hi - z)
        mu0 = cen["mu"] - cen["extra"] - ra.ceil_div(drift * UNIT, DEN)
        parts.append((cen["Hcenter"] + cen["action"], mu0))
        ratios.append((1000000 * cen["action"]) // one["action"])
        k = i + 1
        tL, tH = fw.threshold(Ln, Ld, k)[0], fw.threshold(Hn, Hd, k)[1]
        gz = FLOOR - z
        new_lo = max(lo, z + (tL // (UNIT // DEN)))
        new_hi = min(hi, z - ((-tH) * gz * gz) // ((gz * gz + 72 * DEN * DEN) * (UNIT // DEN)))
        windows.append((new_lo, new_hi))
        mr.emit("Y137_CENTRE_POINT", sample_num=z, centred_residual_about_centre=cen["Hcenter"],
                centred_residual_about_upper=one["Hcenter"], half_width_action=cen["action"],
                one_sided_width_action=one["action"], action_per_million_of_one_sided=ratios[-1],
                new_lo=new_lo, new_hi=new_hi)
    gap1 = (windows[1][0] - windows[0][1]) * (UNIT // DEN)
    gap2 = min(windows[1][0] - windows[0][1], ra.E3_LO - windows[1][1]) * (UNIT // DEN)
    res = [fw.compose(parts[i][0], parts[i][1], (gap1, gap2)[i], ra.ROWS[i][0], windows[i][0], windows[i][1], *fw.Q_NORMS[i])
           for i in range(2)]
    total = res[0]["error"] + res[1]["error"]
    mr.emit("Y137_CENTRE_TRANSFER", E1_sin=res[0]["sin"], E2_sin=res[1]["sin"], E1_error=res[0]["error"],
            E2_error=res[1]["error"], combined_fullstate_error_per_trillion=total, one_sided=ONE_SIDED,
            gate_per_trillion=1428571429)
    mr.emit("Y137_CENTRE_VERDICT", C1=int(all(490000 <= r <= 510000 for r in ratios)),
            C2=int(12000000000 <= total <= 16500000000), C3=int(total > 1428571429),
            Wilson_weight="HOLD" if 700 * total >= UNIT else "CERTIFIED_POSITIVE", issue_137="OPEN")


if __name__ == "__main__":
    main()
