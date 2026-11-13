#!/usr/bin/env python3
"""Issue #137: rational Q-resolvent Wilson transition at two frozen sample energies.

These are sample flat vectors/energies, not the exact E1/E2 eigenspaces.
All full-space Q residuals, shell-4 exterior terms, dual residuals and W norms
are counted exactly. Positive output at the samples does not close #137.
"""
import os
import sys
from math import gcd, isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
INDEP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(INDEP, "y137-liftfree-k3-20261113"))
import k3_common as k
import y137_k3_sector_isolation as mod

sys.path.insert(0, os.path.join(INDEP, "y137-wilson-effective-20261113"))
import check as observed

A1 = 69909875505
A2 = 69949729820
DEN = 1000000000
SCALE = 10 ** 12
FLOOR = 94068200
PS = 1000000
ITER = 20
DUAL_ITER = 20
TOP = 10 ** 9


def fail(reason):
    print("Y137_QDUAL_REFUSE|reason=" + reason + "|json=0", flush=True)
    raise SystemExit(1)


def emit(label, **fields):
    print(label + "|" + "|".join(str(x) + "=" + str(y) for x, y in fields.items())
          + "|json=0", flush=True)


def ceildiv(n, d):
    assert n >= 0 and d > 0
    return (n + d - 1) // d


def sqceil(n):
    assert n >= 0
    z = isqrt(n)
    return z if z * z == n else z + 1


def scale_vector(v):
    m = max(abs(a) for a in v)
    if not m:
        fail("zero_vector")
    out = [(a * TOP * 2 + m) // (2 * m) if a >= 0
           else -ceildiv((-a) * TOP * 2, 2 * m) for a in v]
    if not any(out):
        fail("rounded_zero_vector")
    return out


def inverse_step(M, rhs):
    detM = mod.c.det(M)
    if detM == 0:
        fail("trial_matrix_singular")
    nums = []
    for col in range(len(rhs)):
        B = [row[:] for row in M]
        for row in range(len(rhs)):
            B[row][col] = rhs[row]
        nums.append(mod.c.det(B))
    return scale_vector(nums)


def even_trial(U, start):
    E, odd = mod.sector_bases(mod.ODD_PAIR, -1)
    M = mod.congr(U, E)
    v = list(start)
    for _ in range(4):
        v = inverse_step(M, v)
    full = [0] * 8
    for i in range(8):
        full[i] = sum(E[i][j] * v[j] for j in range(7))
    if full[6] != full[7]:
        fail("reflection_even")
    return full


def obs_from_checker(key):
    c = mod.c
    raw = c.from_key(key)
    mapped = [0] * (2 * c.V)
    for x in range(c.LX):
        for y in range(c.LY):
            mapped[observed.pos(x, y)] = raw[c.pos(x, y)]
            mapped[c.V + observed.pos(x, y)] = raw[c.V + c.pos(x, y)]
    return observed.wilson_sum(mapped)


def build():
    c = mod.c
    if c.MUL != observed.MUL or c.CHAR != observed.CHAR:
        fail("independent_S3_group_disagrees")
    w, m, adj, qflat, outer = c.graph()
    states, flat, sizes = mod.rebuild_states()
    if len(states) != 8042 or sizes != [8, 264, 7770]:
        fail("source_K2")
    where = {key: i for i, key in enumerate(states)}
    C2 = mod.ball_from_checker(w, m, adj, qflat, outer)["C"]
    ball, ex = mod.build_k3(states, where, w, m, adj, outer, C2)
    if ball["n"] != 155378 or ball["nf"] != 1985218:
        fail("K3_census")
    keys = states + ex["ext_keys"]
    if len(keys) != 155386:
        fail("K3_state_keys")
    O = [obs_from_checker(key) for key in keys]
    if min(O) < -7 or max(O) > 14:
        fail("Wilson_range")
    if O[6] != O[7]:
        fail("reflection_observable")
    for i in range(8):
        aa, bb = flat[states[i]]
        if O[i] != 4 * c.CHAR[aa] + 3 * c.CHAR[bb]:
            fail("flat_Wilson_holonomy")
    # False controls were already tested in #178's independent raw-link source.
    fake = [0] * (2 * c.V)
    fake[0] = 1
    if obs_from_checker(c.canonical(fake)) == 7 * 2:
        # A single transposition cannot make all seven faithful characters 2.
        fail("changed_link_control")
    emit("Y137_QDUAL_GRAPH", flats=8, q=ball["n"], shell4=ball["nf"],
         O_min=min(O), O_max=max(O), independent_raw_observable="PASS")
    return ball, O


def dot_w(a, b, weights):
    return sum(weights[i] * a[i] * b[i] for i in range(len(weights)))


def qsquared_from_G(G, v):
    return sum(v[i] * G[i][j] * v[j] for i in range(8) for j in range(8))


def trial(ball, a, v):
    r = mod.threshold_ball(a, DEN, ITER, SCALE, ball, FLOOR, keep_y=True)
    Y = r["Y"]
    q = [sum(Y[i][j] * v[j] for j in range(8)) for i in range(ball["n"])]
    p = [SCALE * vv for vv in v]
    norm = dot_w(p, p, ball["wf"]) + dot_w(q, q, ball["wq"])
    g = qsquared_from_G(r["G"], v)
    if norm <= 0 or g <= 0:
        fail("trial_norm_or_residual")
    emit("Y137_QDUAL_TRIAL", z=str(a) + "/" + str(DEN), iterations=ITER,
         q_residual_G=g, norm_W=norm,
         normalized_Q_residual_ppm_upper=sqceil(ceildiv(g * 10 ** 12, 6 * DEN * DEN * norm)),
         U_sha256=r["hu"], G_sha256=r["hg"])
    return dict(a=a, v=v, p=p, q=q, norm=norm, G=g)


def residual_scaled(ball, t):
    """b*[(QHQ-z)q+Bx] on K3 Q and shell 4; completely independent of G."""
    a, v, q = t["a"], t["v"], t["q"]
    n = ball["n"]
    s = [0] * n
    for i in range(n):
        coupling = sum(ball["oc"][j] * q[ball["oj"][j]]
                       for j in range(ball["rs"][i], ball["rs"][i + 1]))
        ci = ball["C"][i]
        if ci is not None:
            coupling += SCALE * sum(ci[j] * v[j] for j in range(8))
        s[i] = (DEN * ball["dbase"][i] - a) * q[i] - DEN * coupling
    # Shell4 residual is -b*sum_{i in K3} c_fi q_i, with c_fi=wc_fi/w_f.
    s4norm = 0
    for f in range(ball["nf"]):
        acc = sum(ball["ewc"][j] * q[ball["esrc"][j]]
                  for j in range(ball["es"][f], ball["es"][f + 1]))
        wf = ball["eW"][f]
        if acc % wf:
            fail("weighted_exterior_balance")
        sf = -DEN * (acc // wf)
        s4norm += wf * sf * sf
    squared = dot_w(s, s, ball["wq"]) + s4norm
    if 6 * squared != t["G"]:
        fail("independent_complete_Q_residual_not_equal_Gram")
    emit("Y137_QDUAL_RESIDUAL", z=str(a) + "/" + str(DEN),
         shell4_norm2_scaled=s4norm, whole_Q_norm2_scaled=squared,
         exact_agree_G=1)
    return s, squared


def dual_solve(ball, a, rhs):
    """Signed integer Jacobi on K3 Q. Complete exterior residual computed exactly."""
    n = ball["n"]
    diag = [DEN * d - a for d in ball["dbase"]]
    if min(diag) <= 0:
        fail("dual_diagonal")
    u = [0] * n
    for step in range(DUAL_ITER):
        nxt = []
        for i in range(n):
            cou = sum(ball["oc"][j] * u[ball["oj"][j]]
                      for j in range(ball["rs"][i], ball["rs"][i + 1]))
            nxt.append((DEN * (rhs[i] + cou)) // diag[i])
        u = nxt
    d = []
    for i in range(n):
        cou = sum(ball["oc"][j] * u[ball["oj"][j]]
                  for j in range(ball["rs"][i], ball["rs"][i + 1]))
        d.append(DEN * (rhs[i] + cou) - diag[i] * u[i])
    interior_norm = dot_w(d, d, ball["wq"])
    exterior_norm = 0
    for f in range(ball["nf"]):
        acc = sum(ball["ewc"][j] * u[ball["esrc"][j]]
                  for j in range(ball["es"][f], ball["es"][f + 1]))
        wf = ball["eW"][f]
        if acc % wf:
            fail("dual_weighted_balance")
        dext = DEN * (acc // wf)
        exterior_norm += wf * dext * dext
    return u, interior_norm + exterior_norm


def main():
    raw = open(os.path.join(HERE, "PREDICTION.hbp"), "rb").read()
    if b"FROZEN_BEFORE_NEW_R9_QAMPLITUDE" not in raw:
        fail("prediction_seal")
    if b"E1_a=69909875505|E2_a=69949729820|b=1000000000" not in raw:
        fail("sample_pair_moved")
    if k.SCRIPT_SHA != "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff":
        fail("source_script_changed")
    ball, O = build()
    # Selection of the nearest-to-null even direction is integer inverse iteration.
    r1 = mod.threshold_ball(A1, DEN, ITER, SCALE, ball, FLOOR)
    r2 = mod.threshold_ball(A2, DEN, ITER, SCALE, ball, FLOOR)
    v1 = even_trial(r1["U"], [1, 2, 3, 4, 5, 6, 7])
    v2 = even_trial(r2["U"], [7, 6, 5, 4, 3, 2, 1])
    emit("Y137_QDUAL_FLATS", v1=",".join(str(v) for v in v1),
         v2=",".join(str(v) for v in v2), sector="even", certification="trial_only")
    del r1, r2
    t1 = trial(ball, A1, v1)
    t2 = trial(ball, A2, v2)
    overlap = dot_w(t1["p"], t2["p"], ball["wf"]) + dot_w(t1["q"], t2["q"], ball["wq"])
    oamp = sum(ball["wf"][i] * O[i] * t1["p"][i] * t2["p"][i] for i in range(8))
    oamp += sum(ball["wq"][i] * O[i + 8] * t1["q"][i] * t2["q"][i]
                for i in range(ball["n"]))
    wnum = oamp * oamp
    wden = t1["norm"] * t2["norm"]
    emit("Y137_QDUAL_RITZ", raw_amplitude_sign=(oamp > 0) - (oamp < 0),
         raw_trial_weight_ppb_floor=wnum * 1000000000 // wden,
         raw_trial_weight_ppb_ceil=ceildiv(wnum * 1000000000, wden),
         shifted_trial_amplitude2=2 * oamp - 7 * overlap,
         raw_trial_amplitude=oamp, overlap_W=overlap,
         status="ESTIMATE_ONLY")
    s1, qres1 = residual_scaled(ball, t1)
    s2, qres2 = residual_scaled(ball, t2)
    shifted_Q = [2 * O[i + 8] - 7 for i in range(ball["n"])]
    # Cross duals have different resolvent energies.
    u21, d21sq = dual_solve(ball, A2,
                           [shifted_Q[i] * t1["q"][i] for i in range(ball["n"])])
    u12, d12sq = dual_solve(ball, A1,
                           [shifted_Q[i] * t2["q"][i] for i in range(ball["n"])])
    pair21 = dot_w(s2, u21, ball["wq"])
    pair12 = dot_w(s1, u12, ball["wq"])
    free = sum(ball["wf"][i] * (2 * O[i] - 7) * t1["p"][i] * t2["p"][i]
               for i in range(8))
    qtrial = sum(ball["wq"][i] * shifted_Q[i] * t1["q"][i] * t2["q"][i]
                 for i in range(ball["n"]))
    # Exact O2=2O-7 fixed-flat Wilson transition has center=center_num/b.
    center_num = DEN * (free + qtrial) - pair21 - pair12
    g1 = DEN * FLOOR - A1 * PS
    g2 = DEN * FLOOR - A2 * PS
    if min(g1, g2) <= 0:
        fail("source_floor_gap")
    # Directed integer upper error on b*amplitude for the two dual terms
    # and the quadratic e2*O_Q*e1 term, with ||2O-7|| <= 21.
    err21 = ceildiv(sqceil(qres2 * d21sq) * PS, g2)
    err12 = ceildiv(sqceil(qres1 * d12sq) * PS, g1)
    errcross = ceildiv(
        DEN * 21 * sqceil(qres1 * qres2) * PS * PS, g1 * g2)
    error_scaled = err21 + err12 + errcross
    margin = abs(center_num) - error_scaled
    emit("Y137_QDUAL_BUDGET",
         free_O2=free, Qtrial_O2=qtrial,
         center_num=center_num, center_den=DEN,
         qdual_pair21_num=pair21, qdual_pair12_num=pair12,
         d21_norm2_scaled=d21sq, d12_norm2_scaled=d12sq,
         err21_upper_scaled=err21, err12_upper_scaled=err12,
         errcross_upper_scaled=errcross, total_error_upper_scaled=error_scaled,
         signed_margin_scaled=margin, fixed_sample_sign_certified=int(margin > 0),
         exact_E1E2_projectors="NOT_ENCLOSED",
         full_first_spectral_weight="OPEN")
    if margin > 0:
        # The exact resolvent-dressed sample pair has a strict transition.
        # Give a conservative rational lower weight via full-Q norm upper
        # using the Q residual bound, but NOT as an E1/E2 spectral weight.
        ep1 = ceildiv(sqceil(qres1) * PS, g1)
        ep2 = ceildiv(sqceil(qres2) * PS, g2)
        maxn1 = (sqceil(t1["norm"]) + ep1) ** 2
        maxn2 = (sqceil(t2["norm"]) + ep2) ** 2
        lo_num = margin * margin
        lo_den = 4 * DEN * DEN * maxn1 * maxn2
        common = gcd(lo_num, lo_den)
        emit("Y137_QDUAL_FIXED_SAMPLE_WEIGHT", lower_num=lo_num // common,
             lower_den=lo_den // common,
             lower_ppb_floor=lo_num * 1000000000 // lo_den,
             evidence="RIGOROUS_FOR_SHIFTED_WILSON_FIXED_SAMPLES_ONLY",
             full_first_spectral_weight="OPEN")

        # A scalar shift O2=2O-7 leaves exact E1-E2 transitions invariant
        # only after exact orthogonality has been established. The frozen
        # sample vectors are not certified orthogonal, so bound the full-Q
        # overlap separately before claiming anything about unshifted O.
        qn1 = dot_w(t1["q"], t1["q"], ball["wq"])
        qn2 = dot_w(t2["q"], t2["q"], ball["wq"])
        overlap_err21 = ceildiv(DEN * sqceil(qres2 * qn1) * PS, g2)
        overlap_err12 = ceildiv(DEN * sqceil(qres1 * qn2) * PS, g1)
        overlap_errcross = ceildiv(
            DEN * sqceil(qres1 * qres2) * PS * PS, g1 * g2)
        overlap_abs_scaled = (DEN * abs(overlap) + overlap_err21
                              + overlap_err12 + overlap_errcross)
        # 2<psi2,O psi1> = <psi2,O2 psi1> + 7<psi2,psi1>.
        # Both quantities are in integer units 1/DEN.
        raw_margin_scaled = margin - 7 * overlap_abs_scaled
        emit("Y137_QDUAL_UNSHIFTED", trial_overlap_W=overlap,
             overlap_abs_upper_scaled=overlap_abs_scaled,
             overlap_error_21_scaled=overlap_err21,
             overlap_error_12_scaled=overlap_err12,
             overlap_error_cross_scaled=overlap_errcross,
             raw_margin_scaled=raw_margin_scaled,
             fixed_sample_unshifted_sign_certified=int(raw_margin_scaled > 0),
             exact_E1E2_projectors="NOT_ENCLOSED")
        if raw_margin_scaled > 0:
            raw_num = raw_margin_scaled * raw_margin_scaled
            raw_den = 4 * DEN * DEN * maxn1 * maxn2
            common = gcd(raw_num, raw_den)
            emit("Y137_QDUAL_RAW_WILSON_FIXED_WEIGHT",
                 lower_num=raw_num // common,
                 lower_den=raw_den // common,
                 lower_ppb_floor=raw_num * 1000000000 // raw_den,
                 evidence="RIGOROUS_FOR_UNSHIFTED_WILSON_FIXED_SAMPLES_ONLY",
                 actual_E1E2_weight="OPEN")
    emit("Y137_QDUAL_VERDICT", source_floor="94068200/1000000",
         complete_exterior=1, duals=2, normalized_actual_E1E2_weight="NOT_COMPUTED",
         issue_137="OPEN")


if __name__ == "__main__":
    main()
