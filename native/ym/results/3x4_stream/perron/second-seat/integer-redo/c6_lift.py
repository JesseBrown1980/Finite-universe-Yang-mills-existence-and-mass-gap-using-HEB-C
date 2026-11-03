# Integer copy of native/ym/results/3x4_stream/perron/second-seat/c6_lift.py, written by native/scripts/make_integer_pairs.py: 0 divisions moved to qdiv and 2 text pairs. The original stays as evidence.
# C6: the statement E9(r) - E8(r) >= t_cert(r0) - 3 nl + 3 (r - r0), tested at many r0 and r, on my own whole-space rows.
# Steps: own solve at r0 on the store's sector rows, lift by my own class map, exact Barta on the whole-space H' at every r, exact equality with the sector ratio
# at every orbit. Then E8 and E9 of the whole space, by inertia counts from own integer elimination.
# usage: c6_lift.py LX LY
import pickle, random, sys, time
sys.path.insert(0, "C:/tmp/opus55/ym-two-sided")
from ownlib import *
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "..", "scripts"))
from intpair import IntPair as F

LX, LY = int(sys.argv[1]), int(sys.argv[2])
R = "C:/tmp/opus55/ym-two-sided"
t0 = time.monotonic_ns()
with open(f"{R}/whole{LX}{LY}.pkl", "rb") as f:
    w = pickle.load(f)
Wh, Mw, rowsw, cls, row_of_cl, flats, nl = w["W"], w["Mw"], w["rows"], w["cls"], w["row_of_cl"], w["flats"], w["nl"]
n = len(Wh)
fld, srows, ok, _ = read_store(f"{R}/dev{LX}{LY}.bin")
keep, Ws, Ms, Zs = build(srows)
flatset = set(flats)
s_row_of_whole = [row_of_cl[cls[i]] for i in range(n)]
nonflat = [i for i in range(n) if i not in flatset]
pos = {h: i for i, h in enumerate(keep)}
SRC = 1000 * 1000 * 2**30


def own_solve_sector(jb, t, iters=3):
    # Inverse iteration from uniform, from my own sparse elimination (at most 3 steps), giving a positive vector. Only proposes; the verdict is the exact evaluation.
    H = hp_rows(Zs, Ms, 1000, jb)
    A = []
    for i in range(len(H)):
        r = {j: Ws[i] * v for j, v in H[i].items()}
        r[i] = r.get(i, 0) - Ws[i] * t
        A.append(r)
    fact = own_sparse_ldl(A, 120)
    x = [1 << 300 for _ in A]
    for _ in range(iters):
        b = [Ws[i] * x[i] for i in range(len(A))]
        z = own_solve(fact, b, 0)
        sh = max(z).bit_length() - 300
        x = [(v >> sh) if sh > 0 else (v << -sh) for v in z]
    return H, x


def whole_h(jb):
    u, v = 10**6, 1000 * jb
    out = {}
    for i in nonflat:
        r = {j: u * z for j, z in rowsw[i].items() if j not in flatset}
        r[i] = r.get(i, 0) + v * Mw[i]
        out[i] = r
    return out



if (LX, LY) == (2, 3):
    stats = dict(pairs=0, row_eq_fail=0, min_fail=0, bound_fail=0)
    rng = random.Random(27)
    vecs = {"58400000": read_vec(f"{R}/vec/2x3-58400000.bin"), "g": read_vec(f"{R}/vec/2x3-g.bin")}
    vecs["random"] = [0 if srows[h][1] == 0 else rng.randint(1, 10**15) for h in range(len(srows))]
    for name, d in vecs.items():
        x = [d[h] for h in keep]
        dt = {i: x[pos[s_row_of_whole[i]]] for i in nonflat}
        for jb0 in (1000, 4000, 9000):
            tc0 = barta(hp_rows(Zs, Ms, 1000, jb0), x)[0]
            for jb in (jb0, jb0 + 777, 9000, 12000, 27000, 243000):
                if jb < jb0:
                    continue
                u, v = 10**6, 1000 * jb
                Hs = hp_rows(Zs, Ms, 1000, jb)
                ts = [sum(c * x[j] for j, c in Hs[sh].items()) for sh in range(len(Hs))]
                wmin = None
                for i in nonflat:
                    tw = v * Mw[i] * dt[i] + u * sum(z * dt[j] for j, z in rowsw[i].items() if j not in flatset)
                    if tw != ts[pos[s_row_of_whole[i]]]:
                        stats["row_eq_fail"] += 1
                    q = tw // dt[i]
                    wmin = q if wmin is None or q < wmin else wmin
                smin = min(ts[sh] // x[sh] for sh in range(len(ts)))
                stats["pairs"] += 1
                if wmin != smin:
                    stats["min_fail"] += 1
                if wmin < tc0 + 3000 * (jb - jb0):
                    stats["bound_fail"] += 1
        print(f"VECTOR_DONE|{name}|secs_wall={(time.monotonic_ns()-t0)//10**9}|json=0", flush=True)
    print(f"C6_LIFT|L={LX}x{LY}|{stats}|json=0")
    sys.exit(0)

JB0S = {(2, 2): [500, 1000, 2000, 3000, 4000, 5000, 6000, 9000], (2, 3): [1000, 2000, 3000, 4000, 5000, 6000, 9000]}[(LX, LY)]
# t just below the sector level at r0: find by own bisection on the pivots of the fixed point elimination
stats = dict(r0=0, r_pairs=0, row_eq_fail=0, min_fail=0, bound_fail=0)
for jb0 in JB0S:
    H0 = hp_rows(Zs, Ms, 1000, jb0)
    lo, hi = 0, 200_000_000
    # lowest diagonal gives an upper bound on the level
    hi = min(H0[i][i] for i in range(len(H0)))
    while hi - lo > 2000:
        mid = (lo + hi) // 2
        A = []
        for i in range(len(H0)):
            r = {j: Ws[i] * v for j, v in H0[i].items()}
            r[i] = r.get(i, 0) - Ws[i] * mid
            A.append(r)
        try:
            own_sparse_ldl(A, 40)
            lo = mid
        except ArithmeticError:
            hi = mid
    t_solve = lo - 20000
    H0, x = own_solve_sector(jb0, t_solve)
    if min(x) <= 0:
        print("NONPOS", jb0)
        continue
    tc0 = barta(H0, x)[0]
    stats["r0"] += 1
    # The lifted vector
    dt = {i: x[pos[s_row_of_whole[i]]] for i in nonflat}
    for jb in sorted(set(JB0S + [jb0 + 1, jb0 + 777, 12000, 27000, 81000, 243000])):
        if jb < jb0:
            continue
        Hw = whole_h(jb)
        Hs = hp_rows(Zs, Ms, 1000, jb)
        stats["r_pairs"] += 1
        # exact equality of the ratio at every orbit, with its sector row
        ratios_s = {}
        wmin = None
        smin = None
        for i in nonflat:
            sh = pos[s_row_of_whole[i]]
            tw = sum(v * dt[j] for j, v in Hw[i].items())
            if sh not in ratios_s:
                ratios_s[sh] = sum(v * x[j] for j, v in Hs[sh].items())
            if tw != ratios_s[sh]:
                stats["row_eq_fail"] += 1
            q = tw // dt[i]
            wmin = q if wmin is None or q < wmin else wmin
        for sh in range(len(Hs)):
            t = ratios_s.get(sh)
            if t is None:
                t = sum(v * x[j] for j, v in Hs[sh].items())
            q = t // x[sh]
            smin = q if smin is None or q < smin else smin
        if wmin != smin:
            stats["min_fail"] += 1
        # 1000 JB units: r - r0 = (jb - jb0)/1000; 3 (r - r0) J_E = 3000 (jb - jb0) in t_milli
        if wmin < tc0 + 3000 * (jb - jb0):
            stats["bound_fail"] += 1
            print("BOUND_FAIL", jb0, jb, wmin, tc0)
        if jb == jb0 or jb in (9000, 27000):
            print(f"ROW|L={LX}x{LY}|JB0={jb0}|t_cert_r0={tc0}|JB={jb}|whole_min_ratio={wmin}|sector_min_ratio={smin}|claimed_floor={tc0 + 3000 * (jb - jb0)}|json=0", flush=True)
    print(f"R0_DONE|JB0={jb0}|t_solve={t_solve}|t_cert={tc0}|flat_bound={3 * nl * 10**6}|above_flat={tc0 > 3 * nl * 10**6}|secs_wall={(time.monotonic_ns()-t0)//10**9}|json=0", flush=True)
print(f"C6_LIFT|L={LX}x{LY}|{stats}|json=0")
