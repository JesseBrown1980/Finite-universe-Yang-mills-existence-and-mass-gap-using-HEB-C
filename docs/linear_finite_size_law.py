# The linear finite-size law of docs/LINEAR-FINITE-SIZE-LAW-20261115.md, checked in exact rationals.
#
# Claim checked here, for the L x L S3 torus with L >= 4 and r >= 3L/2 + 6, at the fixed parameters
#   h = 1/4,  s = 1 + 2 h^2 = 9/8,  c = s (1 + 1/L),  e = c / r        (e = eps^2 and h = eta of the two-number vector d = eps^a eta^b):
#   (1) closed form   <=  the exact minimum of the two-number bound over every lump and every vertex (the machinery of product_bound.py);
#   (2) simple form   <=  closed form, with simple form = 3r - 18 - 27 (L^2 + 9)(L + 1) / (4 L r);
#   (3) simple form   >   0.
# closed form = min(K_C', f2, 4 |D_TT|, (L^2 - 3) K_T) - 6 L^2 e, each term evaluated exactly from the weights of product_bound.py.
#
# The functions adj_max and vertices are those of native/ym/results/3x4_stream/perron/vector/product_bound.py, copied unchanged (that file runs
# its main on import). The weights are the ones in its header. Exact rationals, no float, json=0. Exits 1 on any failed inequality.
from fractions import Fraction as Fr
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
    X, Z, I = adj_max(a, lx, ly), adj_max(b, lx, ly), adj_max(a + b, lx, ly)
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


def weights(e, h, r):
    wee, weT, weC, wTC, wCC = 3 * (1 - e), 2 * (1 - h), 3 * (1 - e / h), 1 - 1 / h, 3 * (1 - e / (h * h))
    same = (1 - 1 / e) + 2 * (1 - h * h / e)
    same_flat = 1 + 2 * (1 - h * h / e)
    diff = 2 * (1 - h / e) + (1 - h * h / e)
    A, B = 2 * r + 4 * (weT - wee), 3 * r + 4 * (weC - wee)
    DTC, DCC = wTC + wee - weT - weC, wCC + wee - 2 * weC
    DTT = min(same, diff) + wee - 2 * weT
    DTT2 = min(same_flat, diff) + wee - 2 * weT
    return A, B, DTT, DTT2, DTC, DCC


def exact_min(e, h, r, L):
    """Exact minimum of a A + b B + x D_TT + y D_TC + z D_CC over every non-flat lump of the L x L torus and every vertex of its polytope."""
    A, B, DTT, DTT2, DTC, DCC = weights(e, h, r)
    P = L * L
    best, at = None, None
    for a in range(0, P + 1, 2):
        for b in range(0, P - a + 1):
            if (a, b) == (0, 0):
                continue
            d = DTT2 if (a, b) == (2, 0) else DTT
            for x, y, z in vertices(a, b, L, L):
                v = a * A + b * B + x * d + y * DTC + z * DCC
                if best is None or v < best:
                    best, at = v, (a, b)
    return best, at


def closed_form(r, L):
    h = Fr(1, 4)
    s = 1 + 2 * h * h
    c = s * (1 + Fr(1, L))
    e = c / r
    A, B, DTT, DTT2, DTC, DCC = weights(e, h, r)
    signs_ok = DTT <= 0 and DTC <= 0 and DCC <= 0 and 0 < e < Fr(1, 3)
    KC = B + 4 * min(DTC, DCC / 2)
    f2 = 2 * A + min(0, DTT2)
    KT = A + 2 * DTT
    terms = (KC, f2, 4 * (-DTT), (L * L - 3) * KT)
    return min(terms) - 6 * L * L * e, e, h, signs_ok, KT, terms


def micro(v):
    return (v * 1000000).__floor__()


def main():
    lmax_exact = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    lmax_formula = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    fails = 0
    # (1), (2), (3) with the exact minimum over every lump, on the sizes where every lump is enumerated.
    for L in range(4, lmax_exact + 1):
        r0 = Fr(3 * L, 2) + 6
        for r in (r0, r0 + Fr(1, 8), r0 + 1, Fr(2 * L) + 6, Fr(3 * L) + 6, Fr(9 * L), Fr(40 * L)):
            cf, e, h, signs_ok, KT, terms = closed_form(r, L)
            ex, at = exact_min(e, h, r, L)
            exact_gap = ex - 6 * L * L * e
            simple = 3 * r - 18 - Fr(27 * (L * L + 9) * (L + 1), 4 * L) / r
            ok = signs_ok and KT > 0 and cf <= exact_gap and simple <= cf and simple > 0
            fails += 0 if ok else 1
            print("LINEAR_LAW_EXACT|L=%d|r=%s|e=%s|h=%s|exact_gap_micro=%d|tight_lump=%d,%d|closed_form_micro=%d|simple_form_micro=%d|signs_ok=%d|ok=%d|json=0"
                  % (L, r, e, h, micro(exact_gap), at[0], at[1], micro(cf), micro(simple), int(signs_ok), int(ok)), flush=True)
    # (2), (3) and the sign conditions on every size up to lmax_formula, at the threshold and above it.
    checked = 0
    for L in range(4, lmax_formula + 1):
        r0 = Fr(3 * L, 2) + 6
        for r in (r0, r0 + Fr(1, 100), r0 + 1, Fr(2 * L) + 6, Fr(10 * L), Fr(1000 * L)):
            cf, e, h, signs_ok, KT, terms = closed_form(r, L)
            simple = 3 * r - 18 - Fr(27 * (L * L + 9) * (L + 1), 4 * L) / r
            ok = signs_ok and KT > 0 and simple <= cf and simple > 0
            checked += 1
            if not ok:
                fails += 1
                if fails < 8:
                    print("LINEAR_LAW_FAIL|L=%d|r=%s|closed_form_micro=%d|simple_form_micro=%d|signs_ok=%d|json=0" % (L, r, micro(cf), micro(simple), int(signs_ok)))
    print("LINEAR_LAW_FORMULA|sizes=4..%d|points=%d|json=0" % (lmax_formula, checked))
    # the threshold itself beside the earlier finite-size step r >= 4 L^2
    for L in (4, 5, 6, 8, 16, 32, 64):
        r0 = Fr(3 * L, 2) + 6
        simple = 3 * r0 - 18 - Fr(27 * (L * L + 9) * (L + 1), 4 * L) / r0
        print("LINEAR_LAW_THRESHOLD|L=%d|r_linear=%s|r_quadratic=%d|gap_lower_at_r_linear_micro=%d|json=0" % (L, r0, 4 * L * L, micro(simple)))
    print("LINEAR_LAW_DONE|failed=%d|json=0" % fails)
    sys.exit(1 if fails else 0)


main()
