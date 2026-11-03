# Integer copy of native/ym/results/3x4_stream/perron/vector/product_bound.py, written by native/scripts/make_integer_pairs.py: 10 divisions moved to qdiv and 0 text pairs. The original stays as evidence.
# The two-number vector d = eps^a eta^b as a formula, for an S3 torus of any size, with no table and no store.
#
# Only eps^2 enters, since a changes by 0 or 2. With e = eps^2 and h = eta, the local rule of local_table.py gives, per link of each pattern:
#   w_ee = 3(1 - e),  w_eT = 2(1 - h),  w_eC = 3(1 - e/h),  w_TC = 1 - 1/h,  w_CC = 3(1 - e/h^2),
#   w_TT_same = (1 - 1/e) + 2(1 - h^2/e),  w_TT_diff = 2(1 - h/e) + (1 - h^2/e),
# and at (a, b) = (2, 0) a same pair's first move leads to a flat state, so there w_TT_same = 1 + 2(1 - h^2/e).
# Writing x, y, z for the numbers of T-T, T-C and C-C links, the ratio at a configuration is
#   3 nl (1 - e) + a A + b B + x D_TT + y D_TC + z D_CC,
#   A = 2r + 4(w_eT - w_ee),  B = 3r + 4(w_eC - w_ee),  D_TT = min(w_TT_same, w_TT_diff) + w_ee - 2 w_eT,  D_TC = w_TC + w_ee - w_eT - w_eC,  D_CC = w_CC + w_ee - 2 w_eC.
# Over each lump the constraints on (x, y, z) are those of local_table.py: x <= adj(a), z <= adj(b), x + y + z <= adj(a + b), 2x + y <= 4a, y + 2z <= 4b, with x, y, z >= 0, relaxed to real values.
# Its minimum over those is reached at a vertex, and every vertex is tried in exact rationals. So the minimum over all lumps is a lower bound on the ratio over the whole space of orbits.
# E9 - E8 >= that minimum - 3 nl, by PERRON-BOUND.md, in units of J_E.
#
# usage: product_bound.py check LX LY R_NUM R_DEN        the fit at one coupling
#        product_bound.py scan LMAX                       E9 - E8 at r = 9, 12, 16, 24, and the least r in steps of 1/8 with a positive bound, for L x L, L = 3 .. LMAX
# Exact rationals, no float, json=0.
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "..", "scripts"))
from intpair import IntPair as Fr, qdiv
import itertools, sys


def ceil2sqrt(n):
    v = 0
    while v * v < 4 * n:
        v += 1
    return v


def adj_max(s, lx, ly):
    p = lx * ly
    if s == 0:
        return 0
    if s == p:
        return 2 * s
    return 2 * s - min(ceil2sqrt(s), min(lx, ly), ceil2sqrt(p - s))


def vertices(a, b, lx, ly):
    """Vertices (x, y, z) of the polytope of one lump."""
    X, Z, I = adj_max(a, lx, ly), adj_max(b, lx, ly), adj_max(a + b, lx, ly)
    # Each row: coefficients of x, y, z and the bound, as c.v <= d.
    rows = [(-1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, 0), (1, 0, 0, X), (0, 0, 1, Z), (1, 1, 1, I), (2, 1, 0, 4 * a), (0, 1, 2, 4 * b)]
    out = set()
    for r1, r2, r3 in itertools.combinations(rows, 3):
        det = r1[0] * (r2[1] * r3[2] - r2[2] * r3[1]) - r1[1] * (r2[0] * r3[2] - r2[2] * r3[0]) + r1[2] * (r2[0] * r3[1] - r2[1] * r3[0])
        if det == 0:
            continue
        dx = r1[3] * (r2[1] * r3[2] - r2[2] * r3[1]) - r1[1] * (r2[3] * r3[2] - r2[2] * r3[3]) + r1[2] * (r2[3] * r3[1] - r2[1] * r3[3])
        dy = r1[0] * (r2[3] * r3[2] - r2[2] * r3[3]) - r1[3] * (r2[0] * r3[2] - r2[2] * r3[0]) + r1[2] * (r2[0] * r3[3] - r2[3] * r3[0])
        dz = r1[0] * (r2[1] * r3[3] - r2[3] * r3[1]) - r1[1] * (r2[0] * r3[3] - r2[3] * r3[0]) + r1[3] * (r2[0] * r3[1] - r2[1] * r3[0])
        v = (Fr(dx, det), Fr(dy, det), Fr(dz, det))
        if all(c[0] * v[0] + c[1] * v[1] + c[2] * v[2] <= c[3] for c in rows):
            out.add(v)
    return out


CACHE = {}


def lump_vertices(lx, ly):
    key = (lx, ly)
    if key not in CACHE:
        p = lx * ly
        CACHE[key] = [((a, b), vertices(a, b, lx, ly)) for a in range(0, min(p, 40) + 1, 2) for b in range(0, min(p - a, 40) + 1) if (a, b) != (0, 0)]
    return CACHE[key]


def excess(e, h, r, lx, ly):
    """The least of a A + b B + x D_TT + y D_TC + z D_CC over the lumps, and its lump. Lumps past the first 40 of each kind are covered by the per-plaquette values, checked here."""
    wee, weT, weC, wTC, wCC = 3 * (1 - e), 2 * (1 - h), 3 * (1 - qdiv(e , h)), 1 - qdiv(1 , h), 3 * (1 - qdiv(e , (h * h)))
    same = (1 - qdiv(1 , e)) + 2 * (1 - qdiv(h * h , e))
    same_flat = 1 + 2 * (1 - qdiv(h * h , e))
    diff = 2 * (1 - qdiv(h , e)) + (1 - qdiv(h * h , e))
    A, B = 2 * r + 4 * (weT - wee), 3 * r + 4 * (weC - wee)
    DTC, DCC = wTC + wee - weT - weC, wCC + wee - 2 * weC
    DTT = min(same, diff) + wee - 2 * weT
    DTT2 = min(same_flat, diff) + wee - 2 * weT
    KT, KC = A + 2 * min(0, DTT, DTC), B + 2 * min(0, DTC, DCC)
    best, at = None, None
    for (a, b), verts in lump_vertices(lx, ly):
        d = DTT2 if (a, b) == (2, 0) else DTT
        for x, y, z in verts:
            v = a * A + b * B + x * d + y * DTC + z * DCC
            if best is None or v < best:
                best, at = v, (a, b)
    # Past the 40 enumerated of each kind, each plaquette contributes at least KT or KC. These lumps hold a or b above 40.
    p = lx * ly
    if p > 40 and (KT < 0 or KC < 0 or 41 * min(KT, KC) < best):
        return None, None
    return best, at


def fit(r, lx, ly):
    nl = 2 * lx * ly
    # A descent on a grid of e and h in steps that shrink, from a start near the optimum.
    e, h = Fr(1, 8), Fr(3, 10)

    def value(e_, h_):
        if not (0 < e_ < 1 and 0 < h_ < 1):
            return None
        v, _ = excess(e_, h_, r, lx, ly)
        return None if v is None else v - 3 * nl * e_

    cur = value(e, h)
    if cur is None:
        e, h = Fr(1, 4), Fr(1, 2)
        cur = value(e, h)
    if cur is None:
        return None
    for shift in range(2, 12):
        moved = True
        while moved:
            moved = False
            for de, dh in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                e2 = (qdiv(e * (2 ** shift + de) , 2 ** shift)).limit_denominator(10 ** 6)
                h2 = (qdiv(h * (2 ** shift + dh) , 2 ** shift)).limit_denominator(10 ** 6)
                v = value(e2, h2)
                if v is not None and v > cur:
                    e, h, cur = e2, h2, v
                    moved = True
    return cur, e, h


def milli(v):
    return (v * 1000000).__floor__()


def main():
    if sys.argv[1] == "check":
        lx, ly, r = int(sys.argv[2]), int(sys.argv[3]), Fr(int(sys.argv[4]), int(sys.argv[5]))
        gap, e, h = fit(r, lx, ly)
        nl = 2 * lx * ly
        print("PRODUCT_BOUND|Lx=%d|Ly=%d|r=%s|t_milli=%d|flat_bound=%d|gap_milli=%d|e=%s|h=%s|json=0" % (lx, ly, r, milli(gap + 3 * nl), 3 * nl, milli(gap), e, h))
        return
    lmax = int(sys.argv[2])
    for L in range(3, lmax + 1):
        cells = []
        for r in (9, 12, 16, 24):
            res = fit(Fr(r), L, L)
            cells.append("gap_r%d_milli=%s" % (r, "-" if res is None else milli(res[0])))
        lo, hi = 8, 8 * 200
        while hi - lo > 1:
            mid = (lo + hi) // 2
            res = fit(Fr(mid, 8), L, L)
            if res is not None and res[0] > 0:
                hi = mid
            else:
                lo = mid
        print("PRODUCT_SCAN|L=%d|nl=%d|%s|least_r_in_eighths=%d/8|json=0" % (L, 2 * L * L, "|".join(cells), hi), flush=True)


main()
