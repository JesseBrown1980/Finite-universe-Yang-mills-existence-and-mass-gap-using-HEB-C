#!/usr/bin/env python3
"""Global-lock measurement: certified two-sided enclosures of E1, E8 and E9 for the
finite S3 gauge Hamiltonian H = J_E(E + rM) on the full gauge-invariant space of a
periodic LX x LY torus.  Integer only.  See gl_core.py for the model and the method.

usage: gl_measure.py LXxLY r[,r...] [kf=2] [k3=1] [k3plus=0|1] [sabotage=NAME]
  kf: trial-resolvent ball radius around the 8 flat orbits
  k3: trial-resolvent ball radius around the M=3 orbits
Rows go to stdout as TAG|k=v|...|json=0.
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gl_core import Lattice, check, emit, dec_floor, dec_ceil, inertia, sha, CONJ  # noqa: E402

SABOTAGES = ("wrong_r", "drop_flat", "flip_electric", "truncate_exterior", "drop_m3", "wrong_dim_onfile")
D = 10 ** 12          # trial-resolvent denominator
BDEN = 10 ** 12       # threshold grid: lambda = a / BDEN
FD = 10 ** 6          # floor grid
ONFILE_DIM = {(3, 3): 10097891, (3, 4): 2177317873}
# on-file 3x3 zero-momentum shell certificates (native/ym/reference/ym3x3_frozen_8fd12e6.hbp)
ONFILE_3X3 = {27: dict(E8=(53504999, 53505037), E1_lo=53493347, E9=(133667000, 133668324)),
              243: dict(E8=(53944352, 53944779), E1_lo=53944110, E9=(782856000, 782857538))}
ONFILE_3X4_K2 = (264, 7770, 147344)   # merged #136 checker census


def peak_kb():
    try:
        for line in open("/proc/self/status"):
            if line.startswith("VmHWM:"):
                return int(line.split()[1])
    except OSError:
        return -1
    return -1


def parse():
    args = sys.argv[1:]
    check(len(args) >= 2, "usage")
    lx, ly = args[0].split("x")
    rs = [int(v) for v in args[1].split(",")]
    opt = dict(kf=2, k3=1, k3plus=0, sabotage="")
    for a in args[2:]:
        k, v = a.split("=", 1)
        check(k in opt, "usage_option")
        opt[k] = v if k == "sabotage" else int(v)
    check(opt["sabotage"] in ("",) + SABOTAGES, "usage_sabotage")
    return int(lx), int(ly), rs, opt


class Model:
    def __init__(self, lat, sab):
        self.lat = lat
        self.sab = sab
        self.sE = -1 if sab == "flip_electric" else 1
        self.N3 = lat.N3
        self.nbc = {}
        self.wc = {}
        self.mc = {}

    def nbr(self, key):
        v = self.nbc.get(key)
        if v is None:
            v = tuple(self.lat.neighbors(key).items())
            self.nbc[key] = v
        return v

    def w(self, key):
        v = self.wc.get(key)
        if v is None:
            v = self.lat.weight(key)
            self.wc[key] = v
        return v

    def m(self, key):
        v = self.mc.get(key)
        if v is None:
            v = self.lat.mag_key(key)
            self.mc[key] = v
        return v


def census(md):
    lat = md.lat
    F = lat.F
    t0 = time.monotonic_ns()
    dim = lat.burnside_dimension()
    onfile = ONFILE_DIM.get((lat.LX, lat.LY))
    if md.sab == "wrong_dim_onfile":
        onfile = onfile - 1
    check(onfile is None or dim == onfile, "burnside_dimension_onfile")
    raw = lat.enumerate_low(4)
    by = {0: {}, 3: {}, 4: {}}
    rawc = {0: 0, 3: 0, 4: 0}
    for cfg, m in raw:
        check(m in by, "magnetic_parity_low")
        rawc[m] += 1
        key = min(tuple(c[a] for a in cfg) for c in CONJ)
        by[m][key] = by[m].get(key, 0) + 1
    pairs = F * (F - 1) // 2
    flats = sorted(by[0])
    m3 = sorted(by[3])
    m4 = sorted(by[4])
    if md.sab == "drop_flat":
        flats = flats[1:]
    if md.sab == "drop_m3":
        m3 = m3[1:]
    # Hom(pi_1(torus minus punctures), S3)/conjugation counts (NAMED derivation, checked here)
    check(rawc[0] == 18 and rawc[3] == 18 * F and rawc[4] == 108 * pairs, "raw_low_configuration_counts")
    check(len(flats) == 8 and sum(md.w(k) for k in flats) == 18, "all_eight_flat_orbits")
    check(len(m3) == 3 * F and all(md.w(k) == 6 for k in m3), "m3_orbit_count")
    check(len(m4) == 20 * pairs and sum(md.w(k) for k in m4) == 108 * pairs, "m4_orbit_count")
    for k in flats:
        check(md.m(k) == 0, "flat_magnetic")
    for k in m3:
        check(md.m(k) == 3, "m3_magnetic")
    for k in m4:
        check(md.m(k) == 4, "m4_magnetic")
    emit("CENSUS", lattice=str(lat.LX) + "x" + str(lat.LY), links=lat.NL, plaquettes=F,
         orbit_dimension_burnside=dim, orbit_dimension_onfile=onfile,
         flat_orbits=len(flats), flat_raw=rawc[0], m3_orbits=len(m3), m3_raw=rawc[3],
         m4_orbits=len(m4), m4_raw=rawc[4], ms=(time.monotonic_ns() - t0) // 1000000)
    return flats, m3, m4


def floor_inputs(md, m4, Pset):
    """rho44 and P2max over the complete M=4 census; E>=0 by Gershgorin on every state touched."""
    t0 = time.monotonic_ns()
    m4set = set(m4)
    rho = 0
    p2 = 0
    cx4 = {}
    lat = md.lat
    for h in m4:
        nb = md.nbr(h)
        cself = sum(c for x, c in nb if x == h)
        check(md.sE * (md.N3 - cself) - (md.N3 - cself) >= 0, "electric_term_psd_gershgorin")
        r44 = 0
        q = 0
        for x, c in nb:
            mx = md.m(x)
            check(mx in (0, 3, 4) or mx >= 6, "magnetic_parity_neighbour")
            if x in m4set:
                r44 += c
            elif mx >= 6:
                v = cx4.get(x)
                if v is None:
                    v = sum(cc for y, cc in lat.neighbors(x).items() if y in m4set)
                    cx4[x] = v
                q += c * v
            else:
                check(x in Pset or md.sab in ("drop_flat", "drop_m3"), "low_neighbour_in_Pprime")
        rho = max(rho, r44)
        p2 = max(p2, q)
    emit("FLOOR_INPUTS", m4_orbits=len(m4), rho44=rho, P2max=p2, m6_neighbours=len(cx4),
         ms=(time.monotonic_ns() - t0) // 1000000)
    return rho, p2


def floor_value(md, r, rho, p2):
    """Largest n/FD with (FD(N3+4r-rho)-n)(6r FD-n) >= p2 FD^2, n < 6r FD."""
    check(md.sE == 1, "electric_term_psd_gershgorin")
    A0 = FD * (md.N3 + 4 * r - rho)
    B0 = FD * 6 * r
    lo, hi = 0, min(A0, B0)
    def ok(n):
        return A0 - n > 0 and B0 - n > 0 and (A0 - n) * (B0 - n) >= p2 * FD * FD
    check(ok(lo), "floor_positive")
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ok(mid):
            lo = mid
        else:
            hi = mid
    return lo  # fl = lo / FD


def build_ball(md, seeds, K, Pset):
    seen = set(seeds) | Pset
    frontier = list(seeds)
    layers = []
    for _ in range(K):
        new = set()
        for s in frontier:
            for x, _c in md.nbr(s):
                if x not in seen:
                    new.add(x)
        seen |= new
        layers.append(sorted(new))
        frontier = layers[-1]
    ball = [k for L in layers for k in L]
    return ball, layers


def gs_solve(md, r, ball, cols, Pidx, a0, b0, cap):
    """Gauss-Seidel trial for Y ~ (H_bb - lambda0)^-1 H_bP on the ball, integer, scaled by D.
    Converges (H_CC - lambda0 positive definite for lambda0 < floor); accuracy is never assumed."""
    sE = md.sE
    N3 = md.N3
    li = {k: i for i, k in enumerate(ball)}
    nc = len(cols)
    colpos = {p: j for j, p in enumerate(cols)}
    diag = []
    off = []
    Fv = []
    for k in ball:
        cself = 0
        o = []
        f = [0] * nc
        for x, c in md.nbr(k):
            if x == k:
                cself += c
            elif x in li:
                o.append((li[x], c))
            else:
                p = Pidx.get(x)
                if p is not None and p in colpos:
                    f[colpos[p]] += -sE * c * D * b0
        dg = b0 * (sE * (N3 - cself) + r * md.m(k)) - a0
        check(dg > 0, "positive_GS_diagonal")
        diag.append(dg)
        off.append([(j, sE * c * b0) for j, c in o])
        Fv.append(f)
    Y = [[0] * nc for _ in ball]
    steps = 0
    while steps < cap:
        steps += 1
        changed = 0
        for i in range(len(ball)):
            s = Fv[i][:]
            for j, c in off[i]:
                yj = Y[j]
                for t in range(nc):
                    s[t] += c * yj[t]
            dg = diag[i]
            yi = Y[i]
            for t in range(nc):
                v = (2 * s[t] + dg) // (2 * dg)
                if v != yi[t]:
                    changed += 1
                    yi[t] = v
        if changed == 0:
            break
    return Y, steps, changed


def assemble(md, r, P, Pidx, groups, lam0, cap):
    """groups: list of (ball, cols).  Returns the integer forms A_U, B_U, G0, G1, G2."""
    sE = md.sE
    N3 = md.N3
    n = len(P)
    a0, b0 = lam0
    Yn = {}
    gsinfo = []
    for ball, cols in groups:
        if not ball or not cols:
            continue
        Y, steps, changed = gs_solve(md, r, ball, cols, Pidx, a0, b0, cap)
        gsinfo.append((len(ball), len(cols), steps, changed))
        for k, y in zip(ball, Y):
            v = Yn.get(k)
            if v is None:
                v = [0] * n
                Yn[k] = v
            for t, p in enumerate(cols):
                v[p] = y[t]
    # residual numerators R0_x = D K_xP - (K0 Yn)_x over every C state touched
    T = {}
    tally = {}
    out_moves = 0
    for j, y in Yn.items():
        wj = md.w(j)
        nz = [(c, v) for c, v in enumerate(y) if v]
        for x, c in md.nbr(j):
            if x in Pidx:
                continue
            if x not in Yn:
                out_moves += c
                tally[x] = tally.get(x, 0) + c
            t = T.get(x)
            if t is None:
                t = {}
                T[x] = t
            f = sE * wj * c
            for col, v in nz:
                t[col] = t.get(col, 0) + f * v
    Ppart = {}
    for p, key in enumerate(P):
        wp = md.w(key)
        for x, c in md.nbr(key):
            check(x not in Pidx, "no_direct_Pprime_moves")
            t = T.get(x)
            if t is None:
                t = {}
                T[x] = t
            t[p] = t.get(p, 0) - D * sE * wp * c
            pp = Ppart.get(x)
            if pp is None:
                pp = {}
                Ppart[x] = pp
            pp[p] = pp.get(p, 0) - D * sE * wp * c
            if x not in Yn:
                tally[x] = tally.get(x, 0) + c
                out_moves += c
    if md.sab == "truncate_exterior":
        ext = [x for x in T if x not in Yn]
        drop = ext[len(ext) // 2]
        del T[drop]
    # exterior completeness: every move leaving P' and the ball lands in T, counted two ways
    landed = sum(tally[x] for x in T if x not in Yn)
    check(landed == out_moves and all(x in T for x in tally), "exterior_move_conservation")
    for x in T:
        check(md.m(x) >= 4, "C_states_magnetic_ge_4")
    KY = {}
    for x, y in Yn.items():
        t = T[x]
        dgx = md.w(x) * (sE * N3 + r * md.m(x))
        for col in range(n):
            if y[col]:
                t[col] = t.get(col, 0) - dgx * y[col]
        pp = Ppart.get(x, {})
        KY[x] = [pp.get(col, 0) - t.get(col, 0) for col in range(n)]
    AU = [[0] * n for _ in range(n)]
    BU = [[0] * n for _ in range(n)]
    for p, key in enumerate(P):
        wp = md.w(key)
        AU[p][p] += D * D * wp * (sE * N3 + r * md.m(key))
        BU[p][p] += D * D * wp
        for x, c in md.nbr(key):
            y = Yn.get(x)
            if y is None:
                continue
            f = -sE * wp * c * D
            for q in range(n):
                if y[q]:
                    AU[p][q] -= f * y[q]
                    AU[q][p] -= f * y[q]
    G0 = [[0] * n for _ in range(n)]
    G1 = [[0] * n for _ in range(n)]
    G2 = [[0] * n for _ in range(n)]
    for x, y in Yn.items():
        wx = md.w(x)
        ky = KY[x]
        nzy = [(c, v) for c, v in enumerate(y) if v]
        r0 = T[x]
        for i, yi in nzy:
            Ai = AU[i]
            Bi = BU[i]
            G2i = G2[i]
            for j in range(n):
                if ky[j]:
                    Ai[j] += yi * ky[j]
            for j, yj in nzy:
                Bi[j] += wx * yi * yj
                G2i[j] += 6 * wx * yi * yj
            for j, rv in r0.items():
                G1[i][j] += 6 * yi * rv
                G1[j][i] += 6 * yi * rv
    for x, r0 in T.items():
        fac = 6 // md.w(x)
        items = [(c, v) for c, v in r0.items() if v]
        for i, vi in items:
            Gi = G0[i]
            f = fac * vi
            for j, vj in items:
                Gi[j] += f * vj
    for M, name in ((AU, "AU"), (BU, "BU"), (G0, "G0"), (G1, "G1"), (G2, "G2")):
        check(all(M[i][j] == M[j][i] for i in range(n) for j in range(i)), "exact_symmetric_" + name)
    nball = len(Yn)
    next_ = sum(1 for x in T if x not in Yn)
    return dict(AU=AU, BU=BU, G0=G0, G1=G1, G2=G2, gs=gsinfo, ball=nball, ext=next_)


class Evaluator:
    def __init__(self, forms, fl_num):
        self.f = forms
        self.fn = fl_num
        self.cacheU = {}
        self.cacheL = {}

    def negU(self, a):
        v = self.cacheU.get(a)
        if v is None:
            AU, BU = self.f["AU"], self.f["BU"]
            n = len(AU)
            Un = [[BDEN * AU[i][j] - a * BU[i][j] for j in range(n)] for i in range(n)]
            v = inertia(Un)
            self.cacheU[a] = v
        return v

    def negL(self, a):
        if a * FD >= BDEN * self.fn:
            return None
        v = self.cacheL.get(a)
        if v is None:
            AU, BU, G0, G1, G2 = (self.f[k] for k in ("AU", "BU", "G0", "G1", "G2"))
            n = len(AU)
            gam = 6 * (BDEN * self.fn - a * FD)
            b2 = BDEN * BDEN
            ab = a * BDEN
            a2 = a * a
            Ln = [[gam * (BDEN * AU[i][j] - a * BU[i][j]) - FD * (b2 * G0[i][j] + ab * G1[i][j] + a2 * G2[i][j])
                   for j in range(n)] for i in range(n)]
            v = inertia(Ln)
            self.cacheL[a] = v
        return v


def bisect_upper(ev, j, lo, hi, tol):
    """smallest grid a (to tol) with negU(a) >= j: E_j < a/BDEN."""
    vh = ev.negU(hi)
    check(vh is not None and vh >= j, "upper_bracket_hi")
    vl = ev.negU(lo)
    check(vl is not None and vl < j, "upper_bracket_lo")
    while hi - lo > tol:
        mid = (lo + hi) // 2
        v = ev.negU(mid)
        if v is not None and v >= j:
            hi = mid
        else:
            lo = mid
    return hi


def bisect_lower(ev, j, lo, hi, tol):
    """largest grid a (to tol) with negL(a) <= j-1: E_j >= a/BDEN.  None if lo fails."""
    vl = ev.negL(lo)
    if vl is None or vl > j - 1:
        return None
    while hi - lo > tol:
        mid = (lo + hi) // 2
        v = ev.negL(mid)
        if v is not None and v <= j - 1:
            lo = mid
        else:
            hi = mid
    return lo


def anchor_checks(lat, r_label, E, sab):
    rows = []
    if (lat.LX, lat.LY) == (3, 3) and r_label in ONFILE_3X3:
        o = ONFILE_3X3[r_label]
        e8lo, e8hi = E["E8"]
        # on-file values are /10^6; ours are /BDEN
        s = BDEN // 1000000
        ok8 = e8lo is not None and e8lo < o["E8"][1] * s and e8hi >= o["E8"][0] * s
        rows.append(("onfile_E8_anchor_3x3", ok8))
        ok1 = E["E1"][1] >= o["E1_lo"] * s
        rows.append(("onfile_E1_floor_anchor_3x3", ok1))
        if "E9" in E and E["E9"][0] is not None:
            ok9 = E["E9"][0] <= o["E9"][1] * s
            rows.append(("onfile_E9_zero_momentum_anchor_3x3", ok9))
    if (lat.LX, lat.LY) == (3, 4) and r_label > 24:
        # #136-era draft analytic bound (FINITE_3X4_S3_FIRST_GAP_LARGE_R_20261108.md):
        # E_j within eta(r) of 72 - 18/r - mu_j/r^2, mu_1 = 9/2, mu_8 = -9/2, d = 3r,
        # eta = 5184/(d-72)^3 + 373248/(d^2 (d-72)).  Rational check in integers.
        d = 3 * r_label
        r2 = r_label * r_label
        # common denominator Q = 2 r^2 (d-72)^3 d^2
        Q = 2 * r2 * (d - 72) * (d - 72) * (d - 72) * d * d
        eta = 2 * r2 * (5184 * d * d + 373248 * (d - 72) * (d - 72))
        for lvl, mu2 in (("E1", 9), ("E8", -9)):
            centre = (72 * 2 * r2 - 36 * r_label - mu2) * (d - 72) * (d - 72) * (d - 72) * d * d
            lo_q, hi_q = centre - eta, centre + eta
            elo, ehi = E[lvl]
            ok = elo is not None and elo * Q <= hi_q * BDEN and ehi * Q >= lo_q * BDEN
            rows.append(("analytic_second_order_anchor_3x4_" + lvl, ok))
    for name, ok in rows:
        emit("ANCHOR", lattice=str(lat.LX) + "x" + str(lat.LY), r=r_label, check=name,
             result="PASS" if ok else "FAIL")
    for name, ok in rows:
        check(ok, name)


def main():
    LX, LY, rs, opt = parse()
    sab = opt["sabotage"]
    lat = Lattice(LX, LY)
    md = Model(lat, sab)
    emit("GL_MEASURE_BEGIN", lattice=str(LX) + "x" + str(LY), r_list=",".join(str(r) for r in rs),
         kf=opt["kf"], k3=opt["k3"], k3plus=opt["k3plus"], sabotage=sab if sab else "none", D=D, BDEN=BDEN, FD=FD,
         float_used=0, script_sha256=sha(Path(__file__).read_text()),
         core_sha256=sha((HERE / "gl_core.py").read_text()))
    flats, m3, m4 = census(md)
    P = flats + m3
    Pidx = {k: i for i, k in enumerate(P)}
    Pset = set(P)
    for k in P:
        check(all(x not in Pset for x, _ in md.nbr(k)), "no_direct_Pprime_moves")
    rho, p2 = floor_inputs(md, m4, Pset)
    t0 = time.monotonic_ns()
    ball_f, layers_f = build_ball(md, flats, opt["kf"], Pset)
    ball_3, layers_3 = build_ball(md, m3, opt["k3"], Pset)
    nplus = 0
    if opt["k3plus"]:
        # adaptive extension: add every neighbour of the outermost M3-ball layer's M=4 states
        # (the largest trial amplitudes, energy denominator ~ r).  Any ball is valid; only
        # tightness changes, since the residual is recomputed exactly on the new exterior.
        inb = set(ball_3) | Pset
        extra = set()
        for k in layers_3[-1]:
            if md.m(k) == 4:
                for x, _ in md.nbr(k):
                    if x not in inb:
                        extra.add(x)
        nplus = len(extra)
        ball_3 = ball_3 + sorted(extra)
    emit("BALLS", flats_layers=",".join(str(len(L)) for L in layers_f),
         m3_layers=",".join(str(len(L)) for L in layers_3), m3_plus=nplus, ball_f=len(ball_f), ball_3=len(ball_3),
         ms=(time.monotonic_ns() - t0) // 1000000)
    if (LX, LY) == (3, 4) and opt["kf"] == 2:
        # equivalence with the merged #136 checker's census (its BFS does not exclude M=3)
        d3 = set()
        inK2 = set(flats) | set(ball_f)
        for k in layers_f[1]:
            for x, _ in md.nbr(k):
                if x not in inK2:
                    d3.add(x)
        got = (len(layers_f[0]), len(layers_f[1]), len(d3))
        emit("CHECKER_136_EQUIVALENCE", shell1=got[0], shell2=got[1], distance3=got[2],
             onfile="264,7770,147344")
        check(got == ONFILE_3X4_K2, "checker_136_census_equivalence")
    nP = len(P)
    cols_f = list(range(8 if sab != "drop_flat" else 7))
    cols_3 = list(range(len(cols_f), nP))
    N3 = lat.N3
    for r_label in rs:
        r = r_label + 27 if sab == "wrong_r" else r_label
        tr = time.monotonic_ns()
        fln = floor_value(md, r, rho, p2)
        emit("FLOOR", lattice=str(LX) + "x" + str(LY), r=r_label, floor_num=fln, floor_den=FD,
             floor_dec=dec_floor(fln, FD, 6), rule="(3N+4r-rho44-l)(6r-l)>=P2max")
        groups = [(ball_f, cols_f), (ball_3, cols_3)]
        # pass A: trial at lambda0 = 3N (flats) and 3N+3r (M3); U-only estimates
        fA = assemble(md, r, P, Pidx, [(ball_f, cols_f)], (N3, 1), 400)
        fA3 = assemble(md, r, P, Pidx, [(ball_3, cols_3)], (N3 + 3 * r, 1), 400)
        for f in (fA, fA3):
            emit("ASSEMBLY", lattice=str(LX) + "x" + str(LY), r=r_label, stage="A", ball=f["ball"],
                 exterior=f["ext"], gs=";".join(",".join(str(v) for v in g) for g in f["gs"]))
        tolA = 10 ** 5
        evA = Evaluator(fA, fln)
        e1u = bisect_upper(evA, 1, 0, (N3 + 1) * BDEN, tolA)
        e8u = bisect_upper(evA, 8, 0, (N3 + 1) * BDEN, tolA)
        evA3 = Evaluator(fA3, fln)
        e9u = bisect_upper(evA3, 9, (N3 + 1) * BDEN, (N3 + 3 * r + 1) * BDEN, tolA)
        E = {}
        # pass B: band centre
        lamB = ((e1u + e8u) // 2, BDEN)
        fB = assemble(md, r, P, Pidx, groups, lamB, 400)
        emit("ASSEMBLY", lattice=str(LX) + "x" + str(LY), r=r_label, stage="B", ball=fB["ball"],
             exterior=fB["ext"], lambda0_num=lamB[0], gs=";".join(",".join(str(v) for v in g) for g in fB["gs"]))
        evB = Evaluator(fB, fln)
        for lvl, j in (("E1", 1), ("E8", 8)):
            hi = bisect_upper(evB, j, 0, (N3 + 1) * BDEN, 1)
            lo = bisect_lower(evB, j, 0, hi, 1)
            E[lvl] = (lo, hi)
        # pass C: E9
        lamC = (e9u, BDEN)
        fC = assemble(md, r, P, Pidx, groups, lamC, 400)
        emit("ASSEMBLY", lattice=str(LX) + "x" + str(LY), r=r_label, stage="C", ball=fC["ball"],
             exterior=fC["ext"], lambda0_num=lamC[0], gs=";".join(",".join(str(v) for v in g) for g in fC["gs"]))
        evC = Evaluator(fC, fln)
        hi9 = bisect_upper(evC, 9, (N3 + 1) * BDEN, (N3 + 3 * r + 1) * BDEN, 1)
        top = min(hi9, (fln * BDEN) // FD - 1)
        lo9 = bisect_lower(evC, 9, (N3 + 1) * BDEN, top, 1)
        E["E9"] = (lo9, hi9)
        for lvl in ("E1", "E8", "E9"):
            lo, hi = E[lvl]
            emit("LEVEL", lattice=str(LX) + "x" + str(LY), r=r_label, level=lvl,
                 lo_num="NONE" if lo is None else lo, hi_num=hi, den=BDEN,
                 lo_dec="NONE" if lo is None else dec_floor(lo, BDEN, 12), hi_dec=dec_ceil(hi, BDEN, 12),
                 width_dec="NONE" if lo is None else dec_ceil(hi - lo, BDEN, 12),
                 lower_side="CERTIFIED" if lo is not None else "NOT_CERTIFIED",
                 floor_num=fln, floor_den=FD)
        emit("RUN_STATS", lattice=str(LX) + "x" + str(LY), r=r_label,
             ms=(time.monotonic_ns() - tr) // 1000000, peak_kb=peak_kb())
        anchor_checks(lat, r_label, E, sab)
    emit("GL_MEASURE_END", lattice=str(LX) + "x" + str(LY), result="PASS", peak_kb=peak_kb())


if __name__ == "__main__":
    main()
