#!/usr/bin/env python3
"""#137: full-state composition with the three-moment bracket, then energy windows from the
bracket itself. Integers only. See PREDICTION.hbp."""
import os
import sys
from math import isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
INDEP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(INDEP, "y137-moment-radau-20261114"))
sys.path.insert(0, os.path.join(INDEP, "y137-radau-recentred-angle-20261114"))
import moment_radau as mr  # noqa: E402
import recentred_angle as ra  # noqa: E402

N, WF, DEN, UNIT, D, FLOOR = ra.N, ra.WF, ra.DEN, ra.UNIT, ra.D, ra.FLOOR
B_NORM_UP = 8485281374239
E3_LO = ra.E3_LO
Q_NORMS = ((245203944133, 259788930946), (240019603536, 254910334285))
ACCEPTED_187 = ((43364646417, 44731270536), (95928035901, 99359189983))
INPUT_187 = ((283, 1411276469, 2785767511 - 125511135, 38224495000),
             (0, 0, 0, 0))
need, emit, ceil_div = mr.need, mr.emit, ra.ceil_div


def sqrt_ceil(n):
    r = isqrt(n)
    return r if r * r == n else r + 1


def compose(residual_plus_action, mu_without_energy, gap, z, lo, hi, q_lo, q_up):
    """#187's composition: directional energy term, sine, full normalised state error."""
    delta_E = max(z - lo, hi - z)
    gamma_hi = FLOOR - hi
    extra = ceil_div(delta_E * B_NORM_UP * q_up, UNIT * gamma_hi)
    mu = mu_without_energy + ceil_div(delta_E * UNIT, DEN) + extra
    need(0 < mu < gap, "null_branch_mu_not_strict")
    sin = ceil_div((residual_plus_action + extra) * UNIT, gap - mu)
    need(sin < UNIT, "vacuous_sine")
    cos_lower = isqrt(UNIT * UNIT - sin * sin)
    dflat = sqrt_ceil(2 * UNIT * (UNIT - cos_lower))
    q_rot = ceil_div(B_NORM_UP * dflat * DEN, UNIT * gamma_hi)
    q_en = ceil_div(delta_E * q_up, gamma_hi)
    q_diff = q_rot + q_en
    total = sqrt_ceil(dflat * dflat + q_diff * q_diff)
    nz = isqrt(UNIT * UNIT + q_lo * q_lo)
    nt = isqrt(UNIT * UNIT + max(0, q_lo - q_diff) ** 2)
    return dict(sin=sin, error=ceil_div(total * UNIT, isqrt(nz * nt)), extra=extra, mu=mu)


def bracket(i, S, M1s, M2s):
    z = ra.ROWS[i][0]
    U0, G0 = mr.matrix(S["U0"]), mr.matrix(S["G0"])
    need(mr.sha(U0) == S["U_sha256"] and mr.sha(G0) == S["G_sha256"], "U_G_hash")
    M0 = [[x // 6 for x in row] for row in G0]
    M1, M2 = mr.matrix(M1s["exact_mu1_8x8"]), mr.matrix(M2s["actual_K3_mu2_8x8"])
    g, h = FLOOR - z, 468000000000 - z
    C, Dm = mr.sub(M2, mr.scale(M1, g)), mr.sub(M1, mr.scale(M0, g))
    G, E = mr.sub(mr.scale(M1, h), M2), mr.sub(mr.scale(M0, h), M1)
    detC, adjC = mr.inverse_parts(C, "C")
    detG, adjG = mr.inverse_parts(G, "G")
    Ln = mr.add(mr.sub(mr.scale(U0, g * detC), mr.scale(M0, detC)), mr.mul(mr.mul(Dm, adjC), Dm))
    Hn = mr.sub(mr.sub(mr.scale(U0, h * detG), mr.scale(M0, detG)), mr.mul(mr.mul(E, adjG), E))
    return Hn, h * detG, Ln, g * detC


def below(Mn, Md, t):
    """Number of flat-metric eigenvalues of Mn/(Md*D) below t/UNIT."""
    A = [[Mn[i][j] * UNIT - (t * Md * D * WF[i] if i == j else 0) for j in range(N)] for i in range(N)]
    return mr.inertia(A)


def threshold(Mn, Md, k):
    """Smallest integer t with at least k eigenvalues below t/UNIT (so lambda_k < t/UNIT <= ... )."""
    a, b = -100000000000, 0
    need(below(Mn, Md, a) < k <= below(Mn, Md, b), "threshold_range")
    while b - a > 1:
        m = (a + b) // 2
        if below(Mn, Md, m) >= k:
            b = m
        else:
            a = m
    need(below(Mn, Md, b) >= k > below(Mn, Md, a), "threshold_neighbours")
    return a, b


def main():
    # K1: the composition routine reproduces #187 from #187's own inputs
    r = compose(1536787887 - 125511135, 2785767511 - 125511135 - 1375505000, 38224495000,
                69909875505, ra.E1_LO, ra.E1_HI, *Q_NORMS[0])
    r2 = compose(1521085197 - 146165063, 3112956068 - 146165063 - 1629820000, 18969480000,
                 69949729820, ra.E2_LO, ra.E2_HI, *Q_NORMS[1])
    need((r["sin"], r["error"]) == ACCEPTED_187[0] and (r2["sin"], r2["error"]) == ACCEPTED_187[1],
         "composition_of_187_not_reproduced")
    emit("Y137_FSW_CHECK", composition_reproduces_187=1)
    S = mr.read(mr.CACHE, "source", "Y137_CACHE_POINT")
    M1 = mr.read(mr.MU1, "mu1", "Y137_MU1_COMPLETE_POINT")
    M2 = mr.read(mr.MU2, "mu2", "Y137_D11_MU2_POINT")
    parts, windows = [], []
    for i in range(2):
        z, lo, hi, v0, _, gap, _ = ra.ROWS[i]
        Hn, Hd, Ln, Ld = bracket(i, S[i], M1[i], M2[i])
        Wn, Wd = mr.sub(mr.scale(Hn, Ld), mr.scale(Ln, Hd)), Hd * Ld
        a = ra.angle(Hn, Hd, Wn, Wd, list(v0), z, lo, hi, gap)
        drift = max(z - lo, hi - z)
        mu0 = a["mu"] - a["extra"] - ceil_div(drift * UNIT, DEN)
        parts.append((a["Hcenter"] + a["action"], mu0))
        k = i + 1
        tL = threshold(Ln, Ld, k)[0]
        tH = threshold(Hn, Hd, k)[1]
        need(tL < tH < 0, "eigenvalue_bounds_order")
        gz = FLOOR - z
        new_lo = z + (tL // (UNIT // DEN))
        shrink = ((-tH) * gz * gz) // ((gz * gz + 72 * DEN * DEN) * (UNIT // DEN))
        new_hi = z - shrink
        new_lo, new_hi = max(lo, new_lo), min(hi, new_hi)
        need(lo <= new_lo < new_hi <= hi and new_hi <= z, "new_window_inside_accepted")
        windows.append((new_lo, new_hi))
        emit("Y137_FSW_WINDOW", sample_num=z, level=k, lambda_lower_per_trillion=tL, lambda_upper_per_trillion=tH,
             accepted_lo=lo, accepted_hi=hi, new_lo=new_lo, new_hi=new_hi,
             accepted_width=hi - lo, new_width=new_hi - new_lo)
    out = {}
    for name, win in (("accepted_windows", [(ra.ROWS[i][1], ra.ROWS[i][2]) for i in range(2)]), ("bracket_windows", windows)):
        gap1 = (win[1][0] - win[0][1]) * (UNIT // DEN)
        gap2 = min(win[1][0] - win[0][1], E3_LO - win[1][1]) * (UNIT // DEN)
        res = [compose(parts[i][0], parts[i][1], (gap1, gap2)[i], ra.ROWS[i][0], win[i][0], win[i][1], *Q_NORMS[i])
               for i in range(2)]
        total = res[0]["error"] + res[1]["error"]
        out[name] = total
        emit("Y137_FSW_TRANSFER", windows=name, gap1_per_trillion=gap1, gap2_per_trillion=gap2,
             E1_sin=res[0]["sin"], E2_sin=res[1]["sin"], E1_energy_term=res[0]["extra"], E2_energy_term=res[1]["extra"],
             E1_error=res[0]["error"], E2_error=res[1]["error"], combined_fullstate_error_per_trillion=total,
             gate_per_trillion=1428571429, strict_positive_Wilson_first_weight_proved=int(700 * total < UNIT))
    t1, t2 = out["accepted_windows"], out["bracket_windows"]
    emit("Y137_FSW_VERDICT", B1=int(28000000000 <= t1 <= 33000000000),
         B2=int(all(w[1] - w[0] <= 250000 for w in windows)),
         B3=int(14000000000 <= t2 <= 23000000000), B4=int(min(t1, t2) > 1428571429),
         accepted_187_combined=144090460519, Wilson_weight="HOLD" if 700 * min(t1, t2) >= UNIT else "CERTIFIED_POSITIVE",
         issue_137="OPEN")


if __name__ == "__main__":
    main()
