# C5 part 2: find a positive vector on the real 2x2 store with a tie between two magnetic numbers at an integer JB, then compare labels from the real tools.
import random, struct, subprocess, sys
sys.path.insert(0, "C:/tmp/opus55/ym-two-sided")
from ownlib import *

R = "C:/tmp/opus55/ym-two-sided"
T, C = f"{R}/bin/perronritz-grid.exe", f"{R}/bin/perroncert.exe"
DEV = f"{R}/dev22.bin"
fld, rows, ok, _ = read_store(DEV)
keep, W, M, Z = build(rows)
base = read_vec(f"{R}/vec/2x2-46000000.bin")
x0 = [base[h] for h in keep]
rng = random.Random(27)
u = 10**6
n = len(keep)
found = []
for trial in range(200000):
    x = [v + rng.randint(0, 10**5) for v in x0]
    tab = {}
    for i in range(n):
        t = u * sum(c * x[j] for j, c in Z[i].items())
        q = t // x[i]
        m = M[i]
        if m not in tab or q < tab[m][0]:
            tab[m] = (q, i)
    ms = sorted(tab)
    for a in ms:
        for b in ms:
            if a < b:
                num, den = tab[a][0] - tab[b][0], 1000 * (b - a)
                if num >= 0 and num % den == 0:
                    jb = num // den
                    va = tab[a][0] + 1000 * jb * a
                    if all(tab[m][0] + 1000 * jb * m >= va for m in ms):
                        # label differs when the higher M row comes first in row order
                        rows_tied = [keep[i] for i in range(n) if u * sum(c * x[j] for j, c in Z[i].items()) // x[i] + 1000 * jb * M[i] == va]
                        first_row = min(rows_tied)
                        low_m_row = keep[tab[a][1]]
                        if first_row != low_m_row:
                            found.append((trial, jb, a, b, list(x)))
                            break
        if found:
            break
    if found:
        break
print("TRIALS", trial + 1, "FOUND", [f[:4] for f in found])
if found:
    tr, jb, a, b, x = found[0]
    y = [0] * len(rows)
    for i, h in enumerate(keep):
        y[h] = x[i]
    p = f"{R}/tie-d.bin"
    with open(p, "wb") as f:
        f.write(b"".join(struct.pack("<q", v) for v in y))
    r = subprocess.run([T, "pass", DEV, "0", "1000", str(jb), p], capture_output=True, text=True)
    print("LOWER_ROW", [l for l in r.stdout.splitlines() if "LOWER" in l])
    c = subprocess.run([C, "check", DEV, "0", "1000", str(jb), p], capture_output=True, text=True)
    print("CHECK_ROW", c.stdout.strip()[:190])
    print("REPRO", f"perronritz pass dev22.bin 0 1000 {jb} tie-d.bin ; perroncert check dev22.bin 0 1000 {jb} tie-d.bin", "sha", __import__("hashlib").sha256(open(p, "rb").read()).hexdigest())
