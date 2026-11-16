#!/usr/bin/env python3
"""#137: eigendirection sine bound with the three-moment bracket of #198 and a re-centred trial.
Integers only. See PREDICTION.hbp."""
import os
import sys
from itertools import combinations
from math import isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "y137-moment-radau-20261114"))
import moment_radau as mr  # noqa: E402

N = 8
WF = (1, 3, 2, 3, 3, 2, 2, 2)
DEN = 1000000000
UNIT = 1000000000000
D = DEN * UNIT * UNIT
FLOOR = 94068200000
E3_LO = 69968699300
E1_LO, E1_HI = 69908500000, 69909875505
E2_LO, E2_HI = 69948100000, 69949729820
GAP1 = (E2_LO - E1_HI) * (UNIT // DEN)
GAP2 = min(E2_LO - E1_HI, E3_LO - E2_HI) * (UNIT // DEN)
ROWS = (
    (69909875505, E1_LO, E1_HI, (1000000000, 997935625, 996905915, 38054797, 37920545, 2788116, 51160, 51160),
     5983943305230862339, GAP1, 43364646417),
    (69949729820, E2_LO, E2_HI, (111045317, -38181375, -112233220, 1000000000, 979217930, 216249666, 4169404, 4169404),
     6012097741070977840, GAP2, 95928035901),
)
need, emit = mr.need, mr.emit


def ceil_div(n, d):
    need(n >= 0 and d > 0, "invalid_positive_fraction")
    return (n + d - 1) // d


def sqrt_up(n, d):
    x = ceil_div(n * UNIT * UNIT, d)
    z = isqrt(x)
    return z if z * z == x else z + 1


def wnorm(v):
    return sum(WF[i] * v[i] * v[i] for i in range(N))


def apply(M, v):
    return [sum(M[i][j] * v[j] for j in range(N)) for i in range(N)]


def psd7(A):
    for k in range(1, 8):
        for ix in combinations(range(7), k):
            if mr.determinant([[A[i][j] for j in ix] for i in ix]) < 0:
                return False
    return True


def perp_basis(v):
    pivot = max(range(N), key=lambda i: abs(WF[i] * v[i]))
    need(v[pivot] != 0, "zero_trial")
    cols = []
    for j in range(N):
        if j == pivot:
            continue
        vec = [0] * N
        vec[j] = WF[pivot] * v[pivot]
        vec[pivot] = -WF[j] * v[j]
        need(sum(WF[i] * vec[i] * v[i] for i in range(N)) == 0, "perp_basis")
        cols.append(vec)
    return cols


def recentre(Hn, v):
    adj = mr.adjugate(Hn)
    for _ in range(3):
        y = apply(adj, [WF[i] * v[i] for i in range(N)])
        top = max(abs(t) for t in y)
        need(top > 0, "inverse_iteration_zero")
        sign = 1 if y[max(range(N), key=lambda i: abs(y[i]))] > 0 else -1
        v = [sign * ((2 * t * DEN + top) // (2 * top)) for t in y]
    return v


def angle(Hn, Hd, Wn, Wd, v, z, lo, hi, gap):
    vn = wnorm(v)
    hv = apply(Hn, v)
    hq = sum(hv[i] * v[i] for i in range(N))
    abs_mu_H = ceil_div(abs(hq) * UNIT, Hd * D * vn)
    cen = [vn * hv[i] - hq * WF[i] * v[i] for i in range(N)]
    Hcenter = sqrt_up(sum((6 // WF[i]) * cen[i] * cen[i] for i in range(N)), 6 * Hd * Hd * D * D * vn ** 3)
    wv = sum(v[i] * Wn[i][j] * v[j] for i in range(N) for j in range(N))
    need(wv >= 0, "width_form_negative")
    w_ray = ceil_div(wv * UNIT, Wd * D * vn)
    cols = perp_basis(v)
    W7 = [[sum(WF[i] * cols[a][i] * cols[b][i] for i in range(N)) for b in range(7)] for a in range(7)]
    G7 = [[sum(cols[a][i] * Wn[i][l] * cols[b][l] for i in range(N) for l in range(N)) for b in range(7)] for a in range(7)]

    def cand(K):
        return [[K * Wd * D * W7[i][j] - UNIT * G7[i][j] for j in range(7)] for i in range(7)]

    top = ceil_div(sum((6 // WF[i]) * Wn[i][i] for i in range(N)) * UNIT, 6 * Wd * D)
    need(psd7(cand(top)), "trace_bound_does_not_dominate")
    a, b = 0, top
    while a < b:
        m = (a + b) // 2
        if psd7(cand(m)):
            b = m
        else:
            a = m + 1
    K = a
    need(psd7(cand(K)) and (K == 0 or not psd7(cand(K - 1))), "lambda_perp_minimality")
    action = sqrt_up(K * wv, UNIT * Wd * D * vn)
    gz, gh = FLOOR - z, FLOOR - hi
    drift = max(z - lo, hi - z)
    bare = ceil_div(drift * UNIT, DEN)
    extra = ceil_div(drift * 72 * DEN * UNIT, gh * gz)
    mu = abs_mu_H + w_ray + bare + extra
    need(mu < gap, "null_branch_not_identified")
    centred = Hcenter + action + extra
    return dict(sin=ceil_div(centred * UNIT, gap - mu), Hcenter=Hcenter, action=action, extra=extra, mu=mu,
                lambda_perp=K, trace_width=top, width_rayleigh=w_ray)


def point(i, S, M1s, M2s, radau):
    z, lo, hi, v0, vnorm0, gap, accepted = ROWS[i]
    need(int(S["sample_num"]) == z == int(radau["sample_num"]), "sample_alignment")
    need(wnorm(v0) == vnorm0, "flat_norm_of_184_not_reproduced")
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
    Ld = g * detC
    Hn = mr.sub(mr.sub(mr.scale(U0, h * detG), mr.scale(M0, detG)), mr.mul(mr.mul(E, adjG), E))
    Hd = h * detG
    need(mr.sha(Hn) == radau["upper3_sha256"] and mr.sha(Ln) == radau["lower3_sha256"]
         and str(Hd) == radau["upper3_den"] and str(Ld) == radau["lower3_den"], "bracket_of_198_not_reproduced")
    Wn, Wd = mr.sub(mr.scale(Hn, Ld), mr.scale(Ln, Hd)), Hd * Ld
    v1 = recentre(Hn, list(v0))
    dot = sum(WF[k] * v0[k] * v1[k] for k in range(N))
    n0, n1 = wnorm(v0), wnorm(v1)
    turn = sqrt_up(n0 * n1 - dot * dot, n0 * n1)
    new = angle(Hn, Hd, Wn, Wd, v1, z, lo, hi, gap)
    old = angle(Hn, Hd, Wn, Wd, list(v0), z, lo, hi, gap)
    emit("Y137_RECENTRE_POINT", sample_num=z, recentred_vector=",".join(map(str, v1)),
         flat_sine_accepted_to_recentred_per_trillion=turn,
         accepted_187_sin_per_trillion=accepted,
         recentred_sin_per_trillion=new["sin"], recentred_centred_residual=new["Hcenter"],
         recentred_width_action=new["action"], energy_global_extra=new["extra"], recentred_mu=new["mu"],
         recentred_lambda_perp=new["lambda_perp"], width_trace=new["trace_width"],
         kept_vector_sin_per_trillion=old["sin"], kept_vector_centred_residual=old["Hcenter"],
         kept_vector_width_action=old["action"], kept_vector_mu=old["mu"], gap_per_trillion=gap)
    return new["sin"], old["sin"], turn


def main():
    S = mr.read(mr.CACHE, "source", "Y137_CACHE_POINT")
    M1 = mr.read(mr.MU1, "mu1", "Y137_MU1_COMPLETE_POINT")
    M2 = mr.read(mr.MU2, "mu2", "Y137_D11_MU2_POINT")
    R = mr.read(os.path.join(os.path.dirname(mr.__file__), "RESULT-RADAU.hbp"), None, "Y137_RADAU_POINT")
    out = [point(i, S[i], M1[i], M2[i], R[i]) for i in range(2)]
    total = out[0][0] + out[1][0]
    emit("Y137_RECENTRE_VERDICT",
         A1=int(out[0][0] <= 12000000000), A2=int(out[1][0] <= 30000000000),
         A3=int(1428571429 < total < 40000000000),
         A4=int(all(o[1] >= 2 * o[0] for o in out)),
         A5=int(all(5000000000 <= o[2] <= 120000000000 for o in out)),
         sine_sum_per_trillion=total, accepted_187_sine_sum_per_trillion=43364646417 + 95928035901,
         gate_per_trillion=1428571429, Wilson_amplitude_for_recentred_vector="NOT_COMPUTED",
         Wilson_weight="HOLD", issue_137="OPEN")


if __name__ == "__main__":
    main()
