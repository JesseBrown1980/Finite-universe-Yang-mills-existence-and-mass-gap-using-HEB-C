#!/usr/bin/env python3
"""#137: the three-moment bracket read from the upper side, the lower side and the centre,
with the accepted vector kept and with the vector moved. Integers only. See PREDICTION.hbp."""
import os
import sys
from math import isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
INDEP = os.path.dirname(HERE)
for d in ("y137-moment-radau-20261114", "y137-radau-recentred-angle-20261114", "y137-radau-fullstate-windows-20261115"):
    sys.path.insert(0, os.path.join(INDEP, d))
import moment_radau as mr  # noqa: E402
import recentred_angle as ra  # noqa: E402
import fullstate_windows as fw  # noqa: E402

UNIT, DEN, FLOOR, N, WF = ra.UNIT, ra.DEN, ra.FLOOR, ra.N, ra.WF


def flat_distance(v0, v1):
    """Outward flat-metric distance of the two unit vectors, per trillion."""
    dot = sum(WF[k] * v0[k] * v1[k] for k in range(N))
    mr.need(dot > 0, "moved_vector_orientation")
    n0, n1 = ra.wnorm(v0), ra.wnorm(v1)
    cos_lower = isqrt((dot * dot * UNIT * UNIT) // (n0 * n1))
    return fw.sqrt_ceil(2 * UNIT * (UNIT - cos_lower))


def main():
    S = mr.read(mr.CACHE, "source", "Y137_CACHE_POINT")
    M1 = mr.read(mr.MU1, "mu1", "Y137_MU1_COMPLETE_POINT")
    M2 = mr.read(mr.MU2, "mu2", "Y137_D11_MU2_POINT")
    refs, windows = [], []
    for i in range(2):
        z, lo, hi = ra.ROWS[i][:3]
        Hn, Hd, Ln, Ld = fw.bracket(i, S[i], M1[i], M2[i])
        Wn, Wd = mr.sub(mr.scale(Hn, Ld), mr.scale(Ln, Hd)), Hd * Ld
        Mn, Md = mr.add(mr.scale(Hn, Ld), mr.scale(Ln, Hd)), 2 * Hd * Ld
        refs.append({"UPPER": (Hn, Hd, Wn, Wd), "LOWER": (Ln, Ld, Wn, Wd), "CENTRE": (Mn, Md, Wn, 2 * Wd)})
        k = i + 1
        tL, tH = fw.threshold(Ln, Ld, k)[0], fw.threshold(Hn, Hd, k)[1]
        gz = FLOOR - z
        windows.append((max(lo, z + (tL // (UNIT // DEN))),
                        min(hi, z - ((-tH) * gz * gz) // ((gz * gz + 72 * DEN * DEN) * (UNIT // DEN)))))
    gap1 = (windows[1][0] - windows[0][1]) * (UNIT // DEN)
    gaps = (gap1, min(windows[1][0] - windows[0][1], ra.E3_LO - windows[1][1]) * (UNIT // DEN))
    table = {}
    for way in ("UPPER", "CENTRE", "LOWER"):
        for vec in ("KEPT", "MOVED"):
            errs, extra_fields = [], {}
            for i in range(2):
                z, lo, hi, v0 = ra.ROWS[i][:4]
                Cn, Cd, Wn, Wd = refs[i][way]
                q_lo, q_up = fw.Q_NORMS[i]
                v, add = list(v0), 0
                if vec == "MOVED":
                    v = ra.recentre(Cn, list(v0))
                    d = flat_distance(list(v0), v)
                    gz = FLOOR - z
                    spread = ra.ceil_div(fw.B_NORM_UP * d * DEN, UNIT * gz)
                    q_lo, q_up = max(0, q_lo - spread), q_up + spread
                    add = fw.sqrt_ceil(d * d + spread * spread)
                    extra_fields["E%d_moved_flat_distance" % (i + 1)] = d
                a = ra.angle(Cn, Cd, Wn, Wd, v, z, lo, hi, ra.ROWS[i][5])
                drift = max(z - lo, hi - z)
                mu0 = a["mu"] - a["extra"] - ra.ceil_div(drift * UNIT, DEN)
                r = fw.compose(a["Hcenter"] + a["action"], mu0, gaps[i], z, windows[i][0], windows[i][1], q_lo, q_up)
                errs.append(r["error"] + add)
                extra_fields["E%d_residual" % (i + 1)] = a["Hcenter"]
                extra_fields["E%d_action" % (i + 1)] = a["action"]
                extra_fields["E%d_sin" % (i + 1)] = r["sin"]
            table[(way, vec)] = sum(errs)
            mr.emit("Y137_THREE_CELL", way=way, vector=vec, E1_error=errs[0], E2_error=errs[1],
                    combined_fullstate_error_per_trillion=sum(errs), **extra_fields)
    best = min(table.values())
    uk, lk, ck, cm = table[("UPPER", "KEPT")], table[("LOWER", "KEPT")], table[("CENTRE", "KEPT")], table[("CENTRE", "MOVED")]
    gain = (1000000 * (ck - cm)) // ck if cm <= ck else -((1000000 * (cm - ck)) // ck)
    mr.emit("Y137_THREE_VERDICT",
            T1=int(all(table[("CENTRE", v)] == min(table[(w, v)] for w in ("UPPER", "CENTRE", "LOWER")) for v in ("KEPT", "MOVED"))),
            T2=int(abs(uk - lk) * 1000000 <= 150000 * min(uk, lk)),
            T3=int(50000 <= gain <= 250000), centre_moved_gain_per_million=gain,
            T4=int(11500000000 <= best <= 15000000000 and best > 1428571429),
            T5=int(uk == 19880853054 and ck == 15173455813),
            best_cell=min(table, key=table.get)[0] + "_" + min(table, key=table.get)[1], best_per_trillion=best,
            gate_per_trillion=1428571429, Wilson_weight="HOLD" if 700 * best >= UNIT else "CERTIFIED_POSITIVE", issue_137="OPEN")


if __name__ == "__main__":
    main()
