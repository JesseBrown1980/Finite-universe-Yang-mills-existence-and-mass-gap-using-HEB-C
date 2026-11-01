# Writes a permuted integer midpoint matrix for the separately written minors kernel. Integers only.
import sys, random
out, seed, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
R = {}
m = None
for fn in files:
    with open(fn, "rb") as f:
        for ln in f:
            if not ln.startswith(b"SCOL|"):
                continue
            d = {}
            for x in ln.decode().split("|"):
                if "=" in x:
                    k, v = x.split("=", 1)
                    d[k] = v
            m = int(d["core"])
            R[(int(d["ca"]), int(d["cb"]))] = (int(d["lo"]), int(d["hi"]))
assert len(R) == m * m
Q = 20
M = [[0] * m for _ in range(m)]
for i in range(m):
    for j in range(m):
        a, b = R[(i, j)], R[(j, i)]
        l, h = max(a[0], b[0]), min(a[1], b[1])
        assert l <= h
        sl, sh = l >> Q, -((-h) >> Q)
        M[i][j] = (sl + sh) >> 1
del R
perm = list(range(m))
random.Random(seed).shuffle(perm)
with open(out, "w", newline="\n") as f:
    f.write(f"{m}\n")
    for i in perm:
        row = M[i]
        f.write(" ".join(str(row[j]) for j in perm) + "\n")
print(f"MID_DUMP|m={m}|seed={seed}|json=0")
