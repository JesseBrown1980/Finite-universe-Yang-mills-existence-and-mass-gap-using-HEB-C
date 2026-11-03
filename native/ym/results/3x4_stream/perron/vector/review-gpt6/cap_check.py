# The ratio at lump (0,3) on 4x4 and 4x5 at r = 9 from the pinned vector, as CC links go from 2 to 3, and the adjacency cap at 3 plaquettes, real and planar-only.
# Python integers and fractions, json=0.
import sys
from fractions import Fraction as Fr
from math import isqrt
def c2s(n): return 0 if n == 0 else isqrt(4 * n - 1) + 1
def real(s, lx, ly):
    p = lx * ly
    if s == 0: return 0
    if s == p: return 2 * s
    return 2 * s - min(c2s(s), min(lx, ly), c2s(p - s))
def planar(s): return 2 * s - c2s(s)
MOVES = {"ee": ((2, 0, 3),), "eT": ((0, 0, 1), (0, 1, 2)), "eC": ((2, -1, 3),), "TTs": ((-2, 0, 1), (-2, 2, 2)), "TTd": ((-2, 1, 2), (-2, 2, 1)), "TC": ((0, -1, 1), (0, 0, 2)), "CC": ((2, -2, 3),)}
for lx, ly, path, want in ((4, 4, sys.argv[1], 112252744), (4, 5, sys.argv[2], 134017195)):
    g = {}
    for line in open(path, encoding="utf-8"):
        f = line.strip().split("|")
        if f[0] == "G":
            d = dict(x.split("=", 1) for x in f[1:] if "=" in x)
            g[(int(d["a"]), int(d["b"]))] = int(d["g"])
    g[(0, 0)] = 0
    nl = 2 * lx * ly
    def ratio(a, b, n):
        base = g[(a, b)]
        s = Fr(0)
        for p, c in n.items():
            for da, db, m in MOVES[p]:
                s += c * m * (1 - Fr(g[(a + da, b + db)], base))
        return 9 * (2 * a + 3 * b) + s
    for cc in (0, 1, 2, 3):
        ec = 12 - 2 * cc
        ee = nl - ec - cc
        v = ratio(0, 3, {"ee": ee, "eC": ec, "CC": cc})
        print("CAP_CHECK|L=%dx%d|lump=0,3|n_ee=%d|n_eC=%d|n_CC=%d|ratio_micro=%d|real_cap=%d|planar_cap=%d|at_or_under_real_cap=%d|bound_micro=%d|json=0" % (lx, ly, ee, ec, cc, (v * 10**6).__floor__(), real(3, lx, ly), planar(3), 1 if cc <= real(3, lx, ly) else 0, want))
