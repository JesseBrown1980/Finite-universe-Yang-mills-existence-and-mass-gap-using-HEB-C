#!/usr/bin/env python3
"""Does the perturbation series in the electric term converge to the exact gap as r grows?
For 1x1, 2x1, 3x1 and r = 9, 90, 900: exact gap (exact integer inertia), first- and second-order gaps.
If the reading is right, the first-order error falls like 1/r and the second-order error like 1/r^2.
Integers only."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import open_grid as og  # noqa: E402
import pt_check as pt  # noqa: E402

S = og.S


def gaps(a, b, r):
    g = og.Grid(a, b)
    H, W = g.matrix(r)
    n = len(W)
    Hm, _ = g.matrix(1, electric=0)
    M = [Hm[i].get(i, 0) for i in range(n)]
    f = M.index(0)
    man = [i for i in range(n) if M[i] == 2]
    den = 1
    for i in range(n):
        for q in (M[i], abs(2 - M[i])):
            if q:
                den = den * q // pt.gcd(den, q)
    den *= r
    e0_1 = (H[f][f] - r * M[f]) * den
    e0_2 = e0_1 - sum(H[f][k] * H[k].get(f, 0) * (den // (r * M[k])) for k in H[f] if k != f)
    idx = {i: t for t, i in enumerate(man)}
    first = [[H[i].get(j, 0) * den for j in man] for i in man]
    second = [row[:] for row in first]
    for i in man:
        for k, v in H[i].items():
            if k in idx:
                continue
            w = den // (r * (2 - M[k]))
            for j, v2 in H[k].items():
                if j in idx:
                    second[idx[i]][idx[j]] += v * v2 * w
    pt1 = pt.lowest(first, den)[0] - (e0_1 * S) // den
    pt2 = pt.lowest(second, den)[0] - (e0_2 * S) // den
    top = (6 * len(g.links) + 3 * r * a * b + 1) * S
    e0 = og.level(H, W, 1, -S, top, 100)
    e1 = og.level(H, W, 2, e0[0], top, 100)
    return e1[0] - e0[0], pt1, pt2


def main():
    ok1 = ok2 = True
    for a, b in ((1, 1), (2, 1), (3, 1)):
        errs = []
        for r in (9, 90, 900):
            ex, p1, p2 = gaps(a, b, r)
            errs.append((abs(p1 - ex), abs(p2 - ex)))
            og.emit("PT_SCALE", a=a, b=b, r=r, units="1e-9", exact_gap=ex, first_order_gap=p1, second_order_gap=p2,
                    first_order_error=abs(p1 - ex), second_order_error=abs(p2 - ex))
        # from r = 90 to r = 900: first-order error falls by 5 to 20, second-order error by 50 to 200
        f1 = errs[1][0] * 1000 // max(errs[2][0], 1)
        f2 = errs[1][1] * 1000 // max(errs[2][1], 1)
        ok1 &= 5000 <= f1 <= 20000
        ok2 &= 50000 <= f2 <= 200000
        og.emit("PT_SCALE_RATIO", a=a, b=b, first_order_error_r90_over_r900_per_thousand=f1,
                second_order_error_r90_over_r900_per_thousand=f2)
    og.emit("PT_SCALE_VERDICT", S1_first_order_error_falls_like_1_over_r=int(ok1),
            S2_second_order_error_falls_like_1_over_r_squared=int(ok2))


if __name__ == "__main__":
    main()
