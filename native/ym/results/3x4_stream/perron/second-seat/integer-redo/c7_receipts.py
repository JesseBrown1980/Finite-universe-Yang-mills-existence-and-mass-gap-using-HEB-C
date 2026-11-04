# Integer copy of native/ym/results/3x4_stream/perron/second-seat/c7_receipts.py, written by native/scripts/make_integer_pairs.py: 3 divisions moved to qdiv and 4 text pairs. The original stays as evidence.
# C7 / part of C1,C2: recompute everything that pass1.out and grid1.out determine, from their own form and table rows.
# Exact rationals only. Shares no code with perronritz. Reads only the receipt text.
import re, sys, itertools
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "..", "scripts"))
from intpair import IntPair as F, qdiv

J = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..") + os.sep
txt = open(J + "PASS1-3x4.out", newline="").read().replace("\r", "")
rows = [dict(x.split("=", 1) for x in ln.split("|")[1:] if "=" in x) | {"_tag": ln.split("|")[0]} for ln in txt.splitlines() if ln]
k = 1 + max(int(r["i"]) for r in rows if r["_tag"] == "PERRONRITZ_D")
G = [[0] * k for _ in range(k)]
E = [[0] * k for _ in range(k)]
M = [[0] * k for _ in range(k)]
for r in rows:
    if r["_tag"] == "PERRONRITZ_FORM":
        a, b = int(r["a"]), int(r["b"])
        for name, mat in (("G", G), ("E", E), ("M", M)):
            mat[a][b] = mat[b][a] = int(r[name])
print("VECTORS", k)

def pd(mat):
    # Sylvester by exact rational elimination; returns True when all pivots positive.
    n = len(mat)
    m = [[F(x) for x in row] for row in mat]
    for c in range(n):
        p = m[c][c]
        if p <= 0:
            return False
        for i in range(c + 1, n):
            f = qdiv(m[i][c] , p)
            if f:
                for j in range(c, n):
                    m[i][j] -= f * m[c][j]
    return True

def upper(pick, je, jb):
    u, v = 1000 * je, 1000 * jb
    A = [[u * E[x][y] + v * M[x][y] for y in pick] for x in pick]
    Gm = [[G[x][y] for y in pick] for x in pick]
    if not pd(Gm):
        return None
    lo = 0
    # hi from the first vector's Rayleigh quotient, rounded up
    hi = -((-A[0][0]) // Gm[0][0])
    t = lambda th: [[A[i][j] - th * Gm[i][j] for j in range(len(pick))] for i in range(len(pick))]
    assert pd(t(lo))
    assert not pd(t(hi))
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if pd(t(mid)):
            lo = mid
        else:
            hi = mid
    return hi

bad_upper = 0
n_upper = 0
for r in rows:
    if r["_tag"] == "PERRONRITZ_UPPER":
        jb = int(r["JB"])
        pick = [int(x) for x in r["vectors"].split("+")]
        mine = upper(pick, 1000, jb)
        n_upper += 1
        if mine != int(r["upper_milli"]):
            bad_upper += 1
            print("UPPER_MISMATCH", jb, pick, mine, r["upper_milli"])
print(f"UPPER_RECOMPUTED|rows={n_upper}|mismatch={bad_upper}|json=0")

mags = {i: {} for i in range(k)}
for r in rows:
    if r["_tag"] == "PERRONRITZ_MAG":
        mags[int(r["i"])][int(r["M"])] = (int(r["e_milli"]), int(r["row"]), int(r["rows"]))

def lower(i, jb):
    best = None
    for m in sorted(mags[i]):
        e, row, _ = mags[i][m]
        v = e + 1000 * jb * m
        if best is None or v < best[0]:
            best = (v, row, m)
    return best

bad_low = 0
n_low = 0
for r in rows:
    if r["_tag"] == "PERRONRITZ_LOWER":
        got = lower(int(r["vector"]), int(r["JB"]))
        n_low += 1
        if got != (int(r["t_cert_milli"]), int(r["min_row"]), int(r["min_mag"])):
            bad_low += 1
            print("LOWER_MISMATCH", r, got)
print(f"LOWER_RECOMPUTED|rows={n_low}|mismatch={bad_low}|json=0")

for i in range(k):
    ms = sorted(mags[i])
    print(f"MAG_LIST|i={i}|count={len(ms)}|min={ms[0]}|max={ms[-1]}|rows_sum={sum(mags[i][m][2] for m in ms)}|missing={[m for m in range(ms[0], ms[-1]+1) if m not in mags[i]]}|json=0")

# The table in section 5
print("TABLE")
for r_ in (F(12), F(9), F(8), F(7), F(13, 2), F(6)):
    jb = r_ * 1000
    assert jb.denominator == 1
    print(f"  r={str(r_)}|E9_ge={lower(0, int(jb))}")

# Exact crossing of 72 for vector 0: smallest r with min_M (e_M + r 10^6 M) >= 72 10^6.
target = 72_000_000
cross = max(F(target - mags[0][m][0], 1_000_000 * m) for m in mags[0])
tight = [m for m in mags[0] if F(target - mags[0][m][0], 1_000_000 * m) == cross]
print(f"CROSS72|r_exact={cross}|tight_M={tight}|decimal_times_1e6={cross.numerator * 10**6 // cross.denominator}|json=0")
for test in (F(6075, 1000), F(6076, 1000)):
    jb = test * 1000
    v = min(mags[0][m][0] + test * 1_000_000 * m for m in mags[0])
    print(f"  at r={test}: value_exact_milli={v}|ge_72={v >= target}")

# Per-vector crossing for the other vectors, to see that vector 0 is the right choice among the four.
for i in range(k):
    c = max(F(target - mags[i][m][0], 1_000_000 * m) for m in mags[i])
    print(f"CROSS72_VECTOR|i={i}|r={c.numerator * 10**6 // c.denominator}/10^6|json=0")

# Numbers in the doc
s = 10**6 * 2**30
for t, dmax, want in ((93950000, 192571261487, 93955575), (93700000, 58304971582, 93718415), (93000000, 17587343634, 93061051)):
    print(f"S_OVER_DMAX|t={t}|dmax={dmax}|s_over_dmax_x10={10 * s // dmax}|t_plus_floor={t + s // dmax}|row_value={want}|equal={t + s // dmax == want}|json=0")
print("GAP", F(94064904, 10**6) - F(70031, 1000), F(94064904, 10**6) - 72)
print("GAP_DEC", 94064904 - 70031000, 94064904 - 72000000)

# Bounds on the forms that any honest H' must obey on this lattice: 0 <= E <= 6 nl = 144, 3 <= M <= 36 on the span.
def psd_like(mat):
    return pd(mat)
for lo_, hi_, name, F_ in ((3, 36, "M", M), (0, 144, "E", E)):
    lo_ok = pd([[F_[a][b] - lo_ * G[a][b] for b in range(k)] for a in range(k)]) if lo_ else True
    hi_ok = pd([[hi_ * G[a][b] - F_[a][b] for b in range(k)] for a in range(k)])
    print(f"FORM_BOUND|{name}|{lo_}G_le={lo_ok}|le_{hi_}G={hi_ok}|json=0")
print("RAYLEIGH_DIAG", [(i, str(round(qdiv(E[i][i] , G[i][i]), 4)), str(round(qdiv(M[i][i] , G[i][i]), 4))) for i in range(k)] if False else "skipped")

# Lower never above upper, at each coupling in the receipt.
jbs = sorted({int(r["JB"]) for r in rows if r["_tag"] == "PERRONRITZ_UPPER"})
for jb in jbs:
    lows = [int(r["t_cert_milli"]) for r in rows if r["_tag"] == "PERRONRITZ_LOWER" and int(r["JB"]) == jb]
    ups = [int(r["upper_milli"]) for r in rows if r["_tag"] == "PERRONRITZ_UPPER" and int(r["JB"]) == jb]
    print(f"BRACKET|JB={jb}|best_lower={max(lows)}|best_upper={min(ups)}|width={min(ups) - max(lows)}|json=0")

# Concavity of lambda_1 in r: the upper values should not be read as lambda_1, but for a concave function the secant slopes fall.
pts = [(jb, min(int(r["upper_milli"]) for r in rows if r["_tag"] == "PERRONRITZ_UPPER" and int(r["JB"]) == jb)) for jb in jbs]
print("UPPER_POINTS", pts)
for (a, x), (b, y), (c, z) in zip(pts, pts[1:], pts[2:]):
    print(f"  slopes {a}-{b}: {F(y - x, b - a)!s:>18} ~ {(y-x)//(b-a)}  {b}-{c}: {(z-y)//(c-b)}")

g = open(J + "GRID1-3x4.out", newline="").read().replace("\r", "")
vals = []
for ln in g.splitlines():
    if ln.startswith("PERRONRITZ_GRID") and "t_cert_milli" in ln:
        f = dict(x.split("=", 1) for x in ln.split("|")[1:] if "=" in x)
        vals.append((int(f["t_cert_milli"]), int(f["gamma"]), int(f["min_row"]), int(f["min_mag"])))
print("GRID_BEST", max(vals), "count", len(vals))
# On the rows dominated by row 44742735 the value is a Moebius function of gamma: fit from three grid values to see what lies between grid points.
m3 = [(gm, v) for v, gm, row, mm in vals if row == 44742735]
print("GRID_M3_ROWS", m3[:6])
