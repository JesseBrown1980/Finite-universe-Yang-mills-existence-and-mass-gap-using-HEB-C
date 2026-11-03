# C2: forms whose sums pass 2^127 and 2^128 in both directions, so the 256-bit accumulator must carry. Exact comparison with Python integers.
import hashlib, os, random, struct, subprocess, sys
R = "C:/tmp/opus55/ym-two-sided"
T = f"{R}/bin/perronritz-grid.exe"
tmp = f"{R}/tmpacc"
os.makedirs(tmp, exist_ok=True)
rng = random.Random(27)
LEAF = 16 * 1048576


def write_store(path, rows):
    payload = bytearray()
    for w, mag, ent in rows:
        payload += struct.pack("<IHH", w, mag, len(ent))
        for j, z in ent:
            payload += struct.pack("<Ii", j, z)
    shas = "".join(hashlib.sha256(bytes(payload[i : i + LEAF])).hexdigest() for i in range(0, len(payload), LEAF))
    line = f"YMROOMHDR|L=1x{len(rows)}|sector=Sx+Sy+|n={len(rows)}|payload_bytes={len(payload)}|payload_merkle={hashlib.sha256(shas.encode()).hexdigest()}|w_self_adjoint=PASS|json=0\n"
    b = line.encode()
    with open(path, "wb") as f:
        f.write(b + bytes(4096 - len(b)) + bytes(payload))


stats = dict(cases=0, refused=0, form_rows=0, mismatch=0, over_2e127=0, over_2e128=0, negative_big=0, upper_rows=0)
for trial in range(250):
    n = rng.randint(8, 40)
    z = [dict() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < 0.3:
                z[i][j] = z[j][i] = -1
    for i in range(n):
        z[i][i] = -sum(z[i].values())
    M = [rng.randint(1, 3) for _ in range(n)]
    rows = [(1, M[i], sorted(z[i].items())) for i in range(n)]
    k = rng.randint(1, 3)
    mode = rng.choice(["pos", "mixed"])
    ds = []
    for a in range(k):
        v = []
        for i in range(n):
            x = rng.randint(2**59, 2**61)
            v.append(x if mode == "pos" or rng.random() < 0.5 else -x)
        ds.append(v)
    p = f"{tmp}/s.bin"
    write_store(p, rows)
    paths = []
    for a, v in enumerate(ds):
        q = f"{tmp}/d{a}.bin"
        with open(q, "wb") as f:
            f.write(b"".join(struct.pack("<q", x) for x in v))
        paths.append(q)
    r = subprocess.run([T, "pass", p, "0", "1000", "9000"] + paths, capture_output=True, text=True)
    out = r.stdout.strip().splitlines()
    stats["cases"] += 1
    if not out or "ERROR" in out[-1]:
        stats["refused"] += 1
        continue
    for l in out:
        if l.startswith("PERRONRITZ_FORM|"):
            f = dict(x.split("=", 1) for x in l.split("|")[1:] if "=" in x)
            a, b = int(f["a"]), int(f["b"])
            G = sum(ds[a][h] * ds[b][h] for h in range(n))
            E = sum(ds[a][h] * sum(c * ds[b][j] for j, c in z[h].items()) for h in range(n))
            Mf = sum(M[h] * ds[a][h] * ds[b][h] for h in range(n))
            stats["form_rows"] += 1
            for v in (G, E, Mf):
                if abs(v) >= 2**127:
                    stats["over_2e127"] += 1
                if abs(v) >= 2**128:
                    stats["over_2e128"] += 1
                if v <= -(2**127):
                    stats["negative_big"] += 1
            if (int(f["G"]), int(f["E"]), int(f["M"])) != (G, E, Mf):
                stats["mismatch"] += 1
                print("MISMATCH", trial, f)
        if l.startswith("PERRONRITZ_UPPER") and "upper_milli" in l:
            stats["upper_rows"] += 1
print(f"C2_ACC|{stats}|json=0")
