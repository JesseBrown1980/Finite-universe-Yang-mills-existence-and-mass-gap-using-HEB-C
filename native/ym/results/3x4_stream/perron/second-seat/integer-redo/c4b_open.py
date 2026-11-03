# Integer copy of the output of make_integer_redo.py for c4b_open.py, written by native/scripts/make_integer_pairs.py: 2 divisions moved to qdiv and 0 text pairs. The original stays as evidence.
# Integer-only copy of second-seat/c4b_open.py, made on the operator's word that floating point is to be redone in integers. The original stays beside it as evidence.
# C4 part 2: gammas printed OPEN. d2 - d1 is negative on some rows, so x is not positive until gamma is large enough.
# The tool's count of nonpositive rows, and perroncert's refusal, are compared at each gamma. Also 5 thresholds with coprime gaps, where `combine` can wrap.
import os, random, struct, subprocess, sys
sys.path.insert(0, "C:/tmp/opus55/ym-two-sided")
from ownlib import *

R = "C:/tmp/opus55/ym-two-sided"
GRID, CHECK = f"{R}/bin/perronritz-grid.exe", f"{R}/bin/perroncert.exe"
tmp = f"{R}/tmpopen"
os.makedirs(tmp, exist_ok=True)


def wv(path, v):
    with open(path, "wb") as f:
        f.write(b"".join(struct.pack("<q", x) for x in v))


def fields(line):
    return dict(x.split("=", 1) for x in line.strip().split("|")[1:] if "=" in x)


rng = random.Random(27)
stats = dict(sets=0, open_rows=0, value_rows=0, open_count_bad=0, check_should_refuse_bad=0, value_bad=0, negative=0)
for which in ("22", "23"):
    DEV = f"{R}/dev{which}.bin"
    fld, rows, ok, _ = read_store(DEV)
    n = len(rows)
    flat = [r[1] == 0 for r in rows]
    for trial in range(10):
        base = [0 if flat[h] else rng.randint(10**6, 10**10) for h in range(n)]
        d2 = [0 if flat[h] else base[h] + (rng.randint(1, 10**7) if rng.randrange(10) < 9 else -rng.randint(1, 10**5)) for h in range(n)]
        a, b = f"{tmp}/a.bin", f"{tmp}/b.bin"
        wv(a, base)
        wv(b, d2)
        jb = rng.choice((9000, 4000, 777, 0))
        out = f"{tmp}/o.bin"
        t1, t2 = 1000000 + rng.randint(0, 999), 2000000 + rng.randint(0, 999)
        r = subprocess.run([GRID, "grid", DEV, "0", "1000", str(jb), out, str(t1), a, str(t2), b], capture_output=True, text=True)
        lines = r.stdout.strip().splitlines()
        best = [fields(l) for l in lines if l.startswith("PERRONRITZ_BEST")]
        if not best:
            print("NO_BEST", lines[-1:])
            continue
        stats["sets"] += 1
        gb = int(best[0]["gamma"])
        y = read_vec(out)
        x = [p - gb * q for p, q in zip(y, d2)]
        for l in lines:
            if not l.startswith("PERRONRITZ_GRID"):
                continue
            g = fields(l)
            gm = int(g["gamma"])
            yy = [p + gm * q for p, q in zip(x, d2)]
            nonpos = sum(1 for h in range(n) if not flat[h] and yy[h] <= 0)
            p = f"{tmp}/y.bin"
            wv(p, yy)
            c = subprocess.run([CHECK, "check", DEV, "0", "1000", str(jb), p], capture_output=True, text=True)
            if "result" in g:
                stats["open_rows"] += 1
                if int(g["nonpositive_rows"]) != nonpos or nonpos == 0:
                    stats["open_count_bad"] += 1
                    print("OPEN_BAD", g, nonpos)
                if c.returncode == 0:
                    stats["check_should_refuse_bad"] += 1
                    print("CHECK_ACCEPTED", g, c.stdout[:200])
            else:
                stats["value_rows"] += 1
                f = fields(c.stdout.strip().splitlines()[-1])
                if (int(f["t_cert_milli"]), int(f["min_row"]), int(f["min_mag"])) != (int(g["t_cert_milli"]), int(g["min_row"]), int(g["min_mag"])):
                    stats["value_bad"] += 1
                    print("VALUE_BAD", g, f)
                if int(g["t_cert_milli"]) < 0:
                    stats["negative"] += 1
print(f"C4B|{stats}|json=0")

# 5 thresholds with coprime gaps: the weights approach 2^120, so c * d in `combine` wraps. Is the printed number still the value of the written vector?
DEV = f"{R}/dev22.bin"
fld, rows, ok, _ = read_store(DEV)
names = [f"{R}/vec/2x2-{t}.bin" for t in (45000000, 46000000, 46400000)] + [f"{R}/vec/2x2-g.bin", f"{R}/vec/2x2-46400000.bin"]
ts = [10000019, 19000037, 31000079, 43000103, 46400021]
a = [GRID, "grid", DEV, "0", "1000", "9000", f"{tmp}/w.bin"]
for t, p in zip(ts, names):
    a += [str(t), p]
r = subprocess.run(a, capture_output=True, text=True)
print("FIVE_THRESHOLDS", r.returncode, r.stdout.strip().splitlines()[-1][:230])
if r.returncode == 0:
    c = subprocess.run([CHECK, "check", DEV, "0", "1000", "9000", f"{tmp}/w.bin"], capture_output=True, text=True)
    print("FIVE_CHECK", c.stdout.strip()[:230])
    # exact divided difference from my own weights, against what was written
    import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "..", "scripts"))
    from intpair import IntPair as F, qdiv
    ds = [read_vec(p) for p in names]
    x = read_vec(f"{tmp}/w.bin")
    cf = []
    for i in range(5):
        den = F(1)
        for j in range(5):
            if j != i:
                den *= ts[i] - ts[j]
        cf.append(qdiv(1 , den))
    gm = int(fields(r.stdout.strip().splitlines()[-1])["gamma"])
    X = [sum(c_ * d[h] for c_, d in zip(cf, ds)) for h in range(len(x))]
    pure = [x[h] - gm * ds[-1][h] for h in range(len(x))]
    ref = max(range(len(x)), key=lambda h: abs(X[h]))
    kappa = qdiv(F(pure[ref]) , X[ref]) if X[ref] else None
    bad = sum(1 for h in range(len(x)) if kappa is not None and F(pure[h]) != kappa * X[h])
    print(f"FIVE_LABEL|rows_differing_from_the_named_divided_difference={bad}|max_abs_true_integer_weight_bits={max(int(abs(c_) * F(1, 1) * 10**0).bit_length() for c_ in cf)}|json=0")

# A row whose d is small but whose column is large: the table's u * ed wraps with exit 0, while the forms stay exact.
import hashlib
LEAF_ = 16 * 1048576
def write_store(path, rows_):
    payload = bytearray()
    for w, mag, ent in rows_:
        payload += struct.pack("<IHH", w, mag, len(ent))
        for j, z in ent:
            payload += struct.pack("<Ii", j, z)
    shas = "".join(hashlib.sha256(bytes(payload[i : i + LEAF_])).hexdigest() for i in range(0, len(payload), LEAF_))
    line = f"YMROOMHDR|L=1x{len(rows_)}|sector=Sx+Sy+|n={len(rows_)}|nl=1|rooms=0|entries=0|payload_bytes={len(payload)}|payload_merkle={hashlib.sha256(shas.encode()).hexdigest()}|w_self_adjoint=PASS|json=0\n"
    b_ = line.encode()
    with open(path, "wb") as f:
        f.write(b_ + bytes(4096 - len(b_)) + bytes(payload))


rw = [(1, 1, [(0, 1)] + [(1, -(2**31))] * 9000), (1, 1, [(1, 1)])]
sp = f"{tmp}/wrap.bin"
write_store(sp, rw)
dv = [1, 2**62]
dp = f"{tmp}/wrap-d.bin"
wv(dp, dv)
r = subprocess.run([GRID, "pass", sp, "0", "1000", "9000", dp], capture_output=True, text=True)
print("WRAP_PASS", r.returncode, [l for l in r.stdout.strip().splitlines() if "LOWER" in l or "ERROR" in l or "UPPER" in l])
ex = None
for h, (w, mag, ent) in enumerate(rw):
    t = 1000 * 9000 * mag * dv[h] + 10**6 * sum(z * dv[j] for j, z in ent)
    q = t // dv[h]
    ex = q if ex is None else min(ex, q)
print("WRAP_EXACT_MIN_RATIO", ex, "bits", ex.bit_length())
c = subprocess.run([CHECK, "check", sp, "0", "1000", "9000", dp], capture_output=True, text=True)
print("WRAP_CHECK", c.returncode, c.stdout.strip()[:220])
