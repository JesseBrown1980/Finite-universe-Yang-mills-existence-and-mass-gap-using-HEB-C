# Integer copy of native/ym/results/3x4_stream/perron/second-seat/c5_coupling.py, written by native/scripts/make_integer_pairs.py: 0 divisions moved to qdiv and 3 text pairs. The original stays as evidence.
# C5: the coupling table min_M (e_M + 1000 JB M) against perroncert check at that JB, for many JB, including the JB where the tightest M
# changes. Also runs the old binary that printed the 3x4 upper side next to the new one, on the same small inputs.
# usage: c5_coupling.py 22|23|33 [n_random_jb]
import random, subprocess, sys, time
sys.path.insert(0, "C:/tmp/opus55/ym-two-sided")
from ownlib import *
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "..", "scripts"))
from intpair import IntPair as F, integer_sample

R = "C:/tmp/opus55/ym-two-sided"
NEW, OLD, CHECK = f"{R}/bin/perronritz-grid.exe", f"{R}/bin/perronritz.exe", f"{R}/bin/perroncert.exe"
which = sys.argv[1]
nr = int(sys.argv[2]) if len(sys.argv) > 2 else 12
rng = random.Random(27)
DEV = {"22": f"{R}/dev22.bin", "23": f"{R}/dev23.bin", "33": f"{R}/dev33.bin"}[which]
if which == "22":
    vecs = [f"{R}/vec/2x2-{t}.bin" for t in (45000000, 46000000, 46400000)] + [f"{R}/vec/2x2-g.bin"]
elif which == "23":
    vecs = [f"{R}/vec/2x3-{t}.bin" for t in (57000000, 58000000, 58400000)] + [f"{R}/vec/2x3-g.bin"]
else:
    vecs = [f"{R}/vec33/w33-76200000-12_200.bin", f"{R}/vec33/w33-76430000-12_200.bin", f"{R}/vec33/33-x3a.bin", f"{R}/vec33/33-r5000.bin", f"{R}/vec33/33-r4000.bin"]
own = None
if which != "33":
    fld, rows, ok, _ = read_store(DEV)
    keep, W, M, Z = build(rows)
    own = (keep, W, M, Z)


def fields(line):
    return dict(x.split("=", 1) for x in line.strip().split("|")[1:] if "=" in x)


def run(exe, *a):
    return subprocess.run([exe, *map(str, a)], capture_output=True, text=True)


stats = dict(vectors=0, jb_tested=0, value_mismatch=0, label_mismatch=0, lower_row_mismatch=0, own_mismatch=0, ties_at_integer_jb=0, envelope_breaks=0)
t0 = time.monotonic_ns()
for vi, v in enumerate(vecs):
    r = run(NEW, "pass", DEV, 0, 1000, 9000, v)
    rows_ = [l for l in r.stdout.strip().splitlines()]
    mag = {}
    for l in rows_:
        if l.startswith("PERRONRITZ_MAG|"):
            f = fields(l)
            mag[int(f["M"])] = (int(f["e_milli"]), int(f["row"]))
    if not mag:
        print("NO_TABLE", v, rows_[-1:], flush=True)
        continue
    stats["vectors"] += 1

    def table(jb):
        best = None
        for m in sorted(mag):
            val = mag[m][0] + 1000 * jb * m
            if best is None or val < best[0]:
                best = (val, mag[m][1], m)
        return best

    # JB where the lower envelope changes hands
    ms = sorted(mag)
    crossings = set()
    for a in ms:
        for b in ms:
            if a < b:
                num, den = mag[a][0] - mag[b][0], 1000 * (b - a)
                if num >= 0:
                    jbx = num // den
                    va = mag[a][0] + 1000 * jbx * a
                    for j in (jbx - 1, jbx, jbx + 1, jbx + 2):
                        if j >= 0 and j < 400000:
                            tb = table(j)
                            if tb[2] in (a, b) or table(j + 1)[2] in (a, b):
                                crossings.add(j)
                    if num % den == 0 and table(jbx)[0] == va:
                        stats["ties_at_integer_jb"] += 1
                        print(f"TIE|vector={v.split('/')[-1]}|JB={jbx}|M_a={a}|row_a={mag[a][1]}|M_b={b}|row_b={mag[b][1]}|value={va}|json=0", flush=True)
    # keep only true envelope breaks plus neighbours, then random couplings
    keepers = set()
    prev = None
    grid_probe = sorted(crossings)
    for j in grid_probe:
        m = table(j)[2]
        if m != prev:
            keepers.update(x for x in (j - 1, j, j + 1) if x >= 0)
            stats["envelope_breaks"] += 1
        prev = m
    # The exact breaks by a scan of the envelope, by bisection between probes
    lo_scan = 0
    for hi_scan in (1000, 3000, 5000, 7000, 9000, 12000, 27000, 81000, 243000):
        a, b = lo_scan, hi_scan
        def rec(a, b, depth=0):
            if table(a)[2] == table(b)[2]:
                return
            if b - a <= 1:
                keepers.update((a, b))
                return
            mid = (a + b) // 2
            rec(a, mid)
            rec(mid, b)
        rec(a, b)
        lo_scan = hi_scan
    keepers.update(rng.randint(0, 300000) for _ in range(nr))
    keepers.update((0, 1, 4000, 5000, 6000, 6500, 7000, 8000, 9000, 12000, 27000))
    jbs = sorted(keepers)
    if which == "33":
        jbs = sorted(integer_sample(rng, jbs, min(len(jbs), 28)))
    # One pass with the whole list: LOWER rows of the tool itself
    r2 = run(NEW, "pass", DEV, 0, 1000, ",".join(map(str, jbs)), v)
    lowers = {}
    for l in r2.stdout.strip().splitlines():
        if l.startswith("PERRONRITZ_LOWER|"):
            f = fields(l)
            lowers[int(f["JB"])] = (int(f["t_cert_milli"]), int(f["min_row"]), int(f["min_mag"]))
    # Old binary on the same list, byte for byte
    r3 = run(OLD, "pass", DEV, 0, 1000, ",".join(map(str, jbs)), v)
    strip_ms = lambda s: [l for l in s.strip().splitlines() if not l.startswith("PERRONRITZ|")]
    if strip_ms(r2.stdout) != strip_ms(r3.stdout):
        print("OLD_NEW_DIFFER", v, flush=True)
        stats["old_new_differ"] = stats.get("old_new_differ", 0) + 1
    for jb in jbs:
        c = run(CHECK, "check", DEV, 0, 1000, jb, v)
        f = fields(c.stdout.strip().splitlines()[-1])
        tc = (int(f["t_cert_milli"]), int(f["min_row"]), int(f["min_mag"]))
        tb = table(jb)
        stats["jb_tested"] += 1
        if tb[0] != tc[0]:
            stats["value_mismatch"] += 1
            print("VALUE_MISMATCH", v, jb, tb, tc, flush=True)
        elif tb != tc:
            stats["label_mismatch"] += 1
            print("LABEL_MISMATCH", v.split("/")[-1], jb, tb, tc, flush=True)
        if lowers.get(jb) != tb:
            stats["lower_row_mismatch"] += 1
            print("LOWER_ROW_MISMATCH", v, jb, lowers.get(jb), tb, flush=True)
        if own is not None:
            keep, W, Mm, Z = own
            x = read_vec(v)
            H = hp_rows(Z, Mm, 1000, jb)
            q, i = barta(H, [x[h] for h in keep])
            if (q, keep[i], Mm[i]) != tc:
                stats["own_mismatch"] += 1
                print("OWN_MISMATCH", v, jb, (q, keep[i], Mm[i]), tc, flush=True)
    print(f"VECTOR_DONE|{v.split('/')[-1]}|jbs={len(jbs)}|secs_wall={(time.monotonic_ns()-t0)//10**9}|json=0", flush=True)
print(f"C5|store={which}|{stats}|json=0")
