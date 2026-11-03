# Optional, outside the claim: how far could a one-value-per-lump vector go if the isoperimetric table is replaced by the exhaustive class walk?
# Reads CSIG rows from classes.exe (dump mode), fits a vector by my own bisection and Gauss-Seidel in Python integers, and writes it in the G row format.
# The result is then judged by classes.exe and hunt.exe, never by this fit.
# usage: py_refit_classes.py CLASSES_DUMP LX LY R T_LO_MICRO T_HI_MICRO G_OUT
# Integer only, json=0.
import sys
DUMP, LX, LY, R, T_LO, T_HI, OUT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
P = LX * LY
NL = 2 * P
RULE = {'ee': [(2, 0, 3)], 'et': [(0, 0, 1), (0, 1, 2)], 'ec': [(2, -1, 3)], 'tts': [(-2, 0, 1), (-2, 2, 2)], 'ttd': [(-2, 1, 2), (-2, 2, 1)], 'tc': [(0, -1, 1), (0, 0, 2)], 'cc': [(2, -2, 3)]}
lumps = [(a, b) for a in range(0, P + 1, 2) for b in range(0, P - a + 1) if (a, b) != (0, 0)]
index = {l: i for i, l in enumerate(lumps)}
rows = [[] for _ in lumps]
seen = set()
for line in open(DUMP, encoding='utf-8'):
    if not line.startswith('CSIG|'):
        continue
    key = int(line.split('|')[1])
    a, b = key & 63, (key >> 6) & 63
    if (a, b) == (0, 0):
        continue
    tt, tc, cc, et, ec, ee = (key >> 12) & 63, (key >> 18) & 63, (key >> 24) & 63, (key >> 30) & 63, (key >> 36) & 63, (key >> 42) & 63
    for split in (('tts', tt), ('ttd', tt)) if tt else (('tts', 0),):
        n = {'ee': ee, 'et': et, 'ec': ec, split[0]: split[1], 'tc': tc, 'cc': cc}
        near = {}
        own = 0
        for pat, c in n.items():
            if not c:
                continue
            for da, db, m in RULE[pat]:
                t = (a + da, b + db)
                if t == (a, b):
                    own += m * c
                elif t != (0, 0):
                    near[index[t]] = near.get(index[t], 0) + m * c
        sig = (index[(a, b)], own, tuple(sorted(near.items())))
        if sig not in seen:
            seen.add(sig)
            rows[index[(a, b)]].append((own, tuple(sorted(near.items()))))
order = sorted(range(len(lumps)), key=lambda i: (2 * lumps[i][0] + 3 * lumps[i][1], lumps[i]))
print("REFIT_ROWS|signature_rows=%d|lumps=%d|json=0" % (len(seen), len(lumps)), flush=True)
SCALE_BITS = 90
def diag(i):
    a, b = lumps[i]
    return R * (2 * a + 3 * b) + 3 * NL
def attempt(t_milli, g, sweeps):
    # Gauss-Seidel on g_L = max over rows (sum c g_k) * 10^6 / (10^6 diag - 10^6 own - t), t in micro units. Returns None when some denominator is not positive or the top runs away.
    for s in range(sweeps):
        change = 0
        for i in order:
            top = 0
            dd = 1000000 * diag(i)
            for own, near in rows[i]:
                den = dd - 1000000 * own - t_milli
                if den <= 0:
                    return None
                x = 0
                for k, c in near:
                    x += c * g[k]
                x = x * 1000000 // den
                if x > top:
                    top = x
            new = max(top, 1)
            if new != g[i]:
                change = max(change, abs(new - g[i]) * (1 << 24) // max(g[i], 1))
            g[i] = new
        m = max(g)
        bits = m.bit_length()
        if bits > SCALE_BITS:
            g[:] = [max(v >> (bits - SCALE_BITS), 1) for v in g]
        elif bits < SCALE_BITS:
            g[:] = [v << (SCALE_BITS - bits) for v in g]
        if change == 0:
            break
    return g
def value(g):
    best = None
    for i in order:
        dd = 1000000 * diag(i)
        for own, near in rows[i]:
            x = sum(c * g[k] for k, c in near)
            v = dd - 1000000 * own - ((1000000 * x + g[i] - 1) // g[i])
            if best is None or v < best:
                best = v
    return best
g0 = [1 << max(SCALE_BITS - 3 * (2 * lumps[i][0] + 3 * lumps[i][1]) // 2, 8) for i in range(len(lumps))]
lo, hi = T_LO, T_HI
best = None
while hi - lo > 2000:
    mid = (lo + hi) // 2
    g = attempt(mid, list(g0), 120)
    v = value(g) if g else None
    print("REFIT_TRY|t_milli=%d|value=%s|json=0" % (mid, v), flush=True)
    if v is not None and v > lo:
        if best is None or v > best[0]:
            best = (v, list(g))
        lo = max(mid if v >= mid else lo, v)
        if v < mid:
            hi = mid
    else:
        hi = mid
if best is None:
    print("REFIT_NONE|json=0")
    sys.exit(1)
v, g = best
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    f.write("G|id=0|a=0|b=0|g=1|json=0\n")
    for i, (a, b) in enumerate(lumps):
        f.write("G|id=%d|a=%d|b=%d|g=%d|json=0\n" % (i + 1, a, b, g[i]))
print("REFIT_RESULT|Lx=%d|Ly=%d|r=%d|fit_value_milli=%d|json=0" % (LX, LY, R, v))
