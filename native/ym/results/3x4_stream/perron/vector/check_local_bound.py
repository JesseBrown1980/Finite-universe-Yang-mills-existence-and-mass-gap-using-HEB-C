# Two checks of a store-free bound, separate from prodvec and from the table's generator.
#
# 1. Exact value. Reads a table and a vector g, and evaluates the ratio of `perroncert check` on every signature in Python integers:
#    ratio = 1000 (JB M + JE diag) - ceil(1000 JE sum(c g_k) / g_L). Prints the minimum. Fails if it differs from the value given.
# 2. The rule on real configurations. On an Lx x Ly torus it builds S3 link configurations, computes the moves of H from the definition, by recomputing every plaquette after each move,
#    and requires the signature of each configuration to be in the table, and its ratio to be at least the minimum. Configurations, in turn: uniform random, walks of 1 to WALK random moves
#    from a random flat configuration, and descents from a random configuration that take a move lowering M until a random number of steps or none is left, so that the lowest M are reached.
#
# usage: check_local_bound.py TABLE G JE JB T_MILLI LX LY SAMPLES SEED
# Integer only, json=0. Exits 1 on any failure.
import random, sys

TABLE, G, JE, JB, T_MILLI, LX, LY, SAMPLES, SEED = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8]), int(sys.argv[9])
WALK = 14
names, sigs = {}, []
for line in open(TABLE, encoding="utf-8"):
    f = dict(x.split("=", 1) for x in line.strip().split("|")[1:] if "=" in x)
    if line.startswith("LUMP|"):
        names[int(f["id"])] = (int(f["a"]), int(f["b"]))
    elif line.startswith("SIG|"):
        near = {}
        if f["n"]:
            for p in f["n"].split(","):
                i, c = p.split(":")
                near[names[int(i)]] = int(c)
        sigs.append((names[int(f["lump"])], int(f["diag"]), int(f["flat"]), near))
g = {}
for line in open(G, encoding="utf-8"):
    f = dict(x.split("=", 1) for x in line.strip().split("|")[1:] if "=" in x)
    g[(int(f["a"]), int(f["b"]))] = int(f["g"])
UNIT = 1000 * JE


def ratio(lump, diag, near):
    a, b = lump
    m = 2 * a + 3 * b
    total = sum(c * g[k] for k, c in near.items())
    # ceil(u s / g) by floor division of the negative.
    return 1000 * (JB * m + JE * diag) + (-UNIT * total) // g[lump]


low = min(ratio(s[0], s[1], s[3]) for s in sigs)
print("LOCAL_EXACT|signatures=%d|t_milli=%d|given=%d|same=%d|json=0" % (len(sigs), low, T_MILLI, 1 if low == T_MILLI else 0))
bad = 0 if low == T_MILLI else 1
table = {(s[0], s[2], tuple(sorted(s[3].items()))) for s in sigs}
P = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
MUL = [[P.index(tuple(p[q[i]] for i in range(3))) for q in P] for p in P]
INV = [next(j for j in range(6) if MUL[i][j] == 0) for i in range(6)]
FIXED = [sum(1 for i in range(3) if P[g_][i] == i) for g_ in range(6)]
TRANSP = [i for i in range(6) if FIXED[i] == 1]
v = LX * LY
site = lambda x, y: (x % LX) * LY + y % LY
xl = lambda x, y: site(x, y)
yl = lambda x, y: v + site(x, y)
nl = 2 * v
PLAQ = [(xl(x, y), yl(x + 1, y), xl(x, y + 1), yl(x, y)) for x in range(LX) for y in range(LY)]
ENDS = [None] * nl
for x in range(LX):
    for y in range(LY):
        ENDS[xl(x, y)] = (site(x, y), site(x + 1, y))
        ENDS[yl(x, y)] = (site(x, y), site(x, y + 1))


def lump_of(u):
    a = b = 0
    for p in PLAQ:
        z = MUL[MUL[MUL[u[p[0]]][u[p[1]]]][INV[u[p[2]]]]][INV[u[p[3]]]]
        if FIXED[z] == 1:
            a += 1
        elif FIXED[z] == 0:
            b += 1
    return a, b


def random_flat(rng):
    # A commuting pair on the two cycles, then a random gauge transformation.
    while True:
        s, t = rng.randrange(6), rng.randrange(6)
        if MUL[s][t] == MUL[t][s]:
            break
    def power(w, k):
        r = 0
        for _ in range(k):
            r = MUL[r][w]
        return r
    h = [rng.randrange(6) for _ in range(v)]
    u = [0] * nl
    for x in range(LX):
        for y in range(LY):
            xlink = s if x == LX - 1 else 0
            ylink = t if y == LY - 1 else 0
            a, b = site(x, y), site(x + 1, y)
            u[xl(x, y)] = MUL[MUL[h[a]][xlink]][INV[h[b]]]
            a, b = site(x, y), site(x, y + 1)
            u[yl(x, y)] = MUL[MUL[h[a]][ylink]][INV[h[b]]]
    return u


rng = random.Random(SEED)
seen, missing, under, best = {}, 0, 0, None
for k in range(SAMPLES):
    if k % 3 == 0:
        u = [rng.randrange(6) for _ in range(nl)]
    elif k % 3 == 1:
        u = random_flat(rng)
        for _ in range(1 + k % WALK):
            l = rng.randrange(nl)
            u[l] = MUL[rng.choice(TRANSP)][u[l]]
    else:
        u = [rng.randrange(6) for _ in range(nl)]
        for _ in range(rng.randrange(1, 3 * LX * LY)):
            a0, b0 = lump_of(u)
            m0 = 2 * a0 + 3 * b0
            lower = []
            for l in range(nl):
                keep = u[l]
                for s in TRANSP:
                    u[l] = MUL[s][keep]
                    a1, b1 = lump_of(u)
                    if 2 * a1 + 3 * b1 < m0 and (a1, b1) != (0, 0):
                        lower.append((l, s))
                u[l] = keep
            if not lower:
                break
            l, s = rng.choice(lower)
            u[l] = MUL[s][u[l]]
    lump = lump_of(u)
    if lump == (0, 0):
        continue
    near, flat = {}, 0
    for l in range(nl):
        keep = u[l]
        for s in TRANSP:
            u[l] = MUL[s][keep]
            t = lump_of(u)
            if t == (0, 0):
                flat += 1
            else:
                near[t] = near.get(t, 0) + 1
        u[l] = keep
    key = (lump, flat, tuple(sorted(near.items())))
    seen[lump] = seen.get(lump, 0) + 1
    if key not in table:
        missing += 1
        if missing <= 6:
            print("LOCAL_SAMPLE_MISSING|lump=%s|flat=%d|near=%s|json=0" % (lump, flat, sorted(near.items())))
    r = ratio(lump, 3 * nl, near)
    best = r if best is None or r < best else best
    if r < T_MILLI:
        under += 1
low_lumps = sorted(seen, key=lambda t: 2 * t[0] + 3 * t[1])[:8]
print("LOCAL_SAMPLE|Lx=%d|Ly=%d|samples=%d|lumps_reached=%d|lowest_lumps=%s|not_in_table=%d|ratio_below_t=%d|lowest_ratio_milli=%s|bound_milli=%d|json=0" % (LX, LY, SAMPLES, len(seen), ";".join("%d,%d" % t for t in low_lumps), missing, under, best, T_MILLI))
print("LOCAL_CHECK_DONE|failed=%d|json=0" % (bad + (1 if missing else 0) + (1 if under else 0)))
sys.exit(1 if bad or missing or under else 0)
