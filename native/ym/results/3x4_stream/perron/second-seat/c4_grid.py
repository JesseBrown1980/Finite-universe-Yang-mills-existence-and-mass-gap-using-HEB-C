# C4: grid value against perroncert check and against my own exact Barta, for every gamma, on small stores.
# usage: c4_grid.py 22|23|33 [seed]
import os, random, struct, subprocess, sys, time
sys.path.insert(0, "C:/tmp/opus55/ym-two-sided")
from ownlib import *
from fractions import Fraction as F

R = "C:/tmp/opus55/ym-two-sided"
GRID = f"{R}/bin/perronritz-grid.exe"
CHECK = f"{R}/bin/perroncert.exe"
which = sys.argv[1]
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 27
rng = random.Random(seed)
DEV = {"22": f"{R}/dev22.bin", "23": f"{R}/dev23.bin", "33": f"{R}/dev33.bin"}[which]
fld, rows, ok, _ = read_store(DEV)
n = len(rows)
keep, W, M, Z = build(rows)
flat = [r[1] == 0 for r in rows]
tmp = f"{R}/tmp{which}"
os.makedirs(tmp, exist_ok=True)


def wv(path, v):
    with open(path, "wb") as f:
        f.write(b"".join(struct.pack("<q", x) for x in v))


def fields(line):
    return dict(x.split("=", 1) for x in line.strip().split("|")[1:] if "=" in x)


def own_value(y, jb):
    H = hp_rows(Z, M, 1000, jb)
    sub = [y[h] for h in keep]
    v, i = barta(H, sub)
    return v, keep[i], M[i]


stats = dict(sets=0, gammas=0, open_rows=0, value_rows=0, negative_values=0, mismatch_check=0, mismatch_own=0, open_mismatch=0, dd_scale_fail=0)
sets = []
if which == "22":
    Vs = [(45000000, f"{R}/vec/2x2-45000000.bin"), (46000000, f"{R}/vec/2x2-46000000.bin"), (46400000, f"{R}/vec/2x2-46400000.bin")]
elif which == "23":
    Vs = [(57000000, f"{R}/vec/2x3-57000000.bin"), (58000000, f"{R}/vec/2x3-58000000.bin"), (58400000, f"{R}/vec/2x3-58400000.bin")]
else:
    Vs = [(75000000, f"{R}/vec33/d75000000.bin"), (76200000, f"{R}/vec33/w33-76200000-12_200.bin"), (76300000, f"{R}/vec33/w33-76300000-12_200.bin"), (76400000, f"{R}/vec33/w33-76400000-12_200.bin"), (76430000, f"{R}/vec33/w33-76430000-12_200.bin")]
if which == "33":
    sets = [(9000, Vs[1:4]), (9000, [Vs[0], Vs[1], Vs[3]]), (9000, [Vs[1], Vs[3]]), (6000, Vs[1:4])]
else:
    for jb in (9000, 6000, 4000, 1000, 0):
        sets += [(jb, Vs), (jb, Vs[:2]), (jb, Vs[1:])]
    # Vectors that have nothing to do with a solve: random positive integers, so the numerators go negative at many rows.
    for trial in range(6):
        vv = []
        base = [0 if flat[h] else rng.randint(10**6, 10**9) for h in range(n)]
        for k in range(rng.randint(2, 3)):
            v = [0 if flat[h] else base[h] + (k + 1) * rng.randint(-5, 10**6) for h in range(n)]
            p = f"{tmp}/rnd{trial}-{k}.bin"
            wv(p, v)
            vv.append((1000000 * (k + 1) + rng.randint(0, 999) * 7, p))
        sets.append((rng.choice((9000, 4000, 777, 0)), vv))

t0 = time.time()
for jb, vs in sets:
    stats["sets"] += 1
    out = f"{tmp}/out.bin"
    if os.path.exists(out):
        os.remove(out)
    args = [GRID, "grid", DEV, "0", "1000", str(jb), out]
    for t, p in vs:
        args += [str(t), p]
    r = subprocess.run(args, capture_output=True, text=True)
    lines = r.stdout.strip().splitlines()
    grows = [fields(l) for l in lines if l.startswith("PERRONRITZ_GRID|")]
    best = [fields(l) for l in lines if l.startswith("PERRONRITZ_BEST|")]
    if not best:
        print("NO_BEST", jb, [t for t, _ in vs], lines[-1:], flush=True)
        # Every gamma was OPEN: rebuild x from the weights to still compare the OPEN counts.
        continue
    gb = int(best[0]["gamma"])
    y = read_vec(out)
    ds = [read_vec(p) for _, p in vs]
    dk = ds[-1]
    x = [a - gb * b for a, b in zip(y, dk)]
    # x must be the divided difference, on one exact scale, with no rounding.
    ts = [t for t, _ in vs]
    coeff = []
    for i in range(len(ts)):
        den = F(1)
        for j in range(len(ts)):
            if j != i:
                den *= ts[i] - ts[j]
        coeff.append(1 / den)
    X = [sum(c * d[h] for c, d in zip(coeff, ds)) for h in range(n)]
    ref = max(range(n), key=lambda h: abs(X[h]))
    kappa = F(x[ref]) / X[ref]
    if any(F(x[h]) != kappa * X[h] for h in range(n)):
        stats["dd_scale_fail"] += 1
        print("DD_SCALE_FAIL", jb, ts, flush=True)
    for g in grows:
        gm = int(g["gamma"])
        yy = [a + gm * b for a, b in zip(x, dk)]
        nonpos = sum(1 for h in range(n) if not flat[h] and yy[h] <= 0)
        stats["gammas"] += 1
        if "result" in g:
            stats["open_rows"] += 1
            if int(g["nonpositive_rows"]) != nonpos or nonpos == 0:
                stats["open_mismatch"] += 1
                print("OPEN_COUNT_MISMATCH", jb, ts, gm, g, nonpos, flush=True)
            continue
        stats["value_rows"] += 1
        if nonpos:
            stats["open_mismatch"] += 1
            print("VALUE_ON_NONPOSITIVE", jb, ts, gm, nonpos, flush=True)
        p = f"{tmp}/y.bin"
        wv(p, yy)
        c = subprocess.run([CHECK, "check", DEV, "0", "1000", str(jb), p], capture_output=True, text=True)
        cf = fields(c.stdout.strip().splitlines()[-1])
        tg = (int(g["t_cert_milli"]), int(g["min_row"]), int(g["min_mag"]))
        tc = (int(cf["t_cert_milli"]), int(cf["min_row"]), int(cf["min_mag"]))
        if tg[0] < 0:
            stats["negative_values"] += 1
        if tg != tc:
            stats["mismatch_check"] += 1
            print("MISMATCH_CHECK", jb, ts, gm, tg, tc, flush=True)
        if which != "33":
            to = own_value(yy, jb)
            if to != tg:
                stats["mismatch_own"] += 1
                print("MISMATCH_OWN", jb, ts, gm, tg, to, flush=True)
    print(f"SET_DONE|JB={jb}|ts={ts}|best_gamma={gb}|best={best[0]['t_cert_milli']}|gammas={len(grows)}|secs_wall={time.time()-t0:.0f}|json=0", flush=True)
print(f"C4|store={which}|{stats}|json=0")
