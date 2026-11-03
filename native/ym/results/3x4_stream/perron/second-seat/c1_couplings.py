# C1 at other couplings on 2x2: own exact bracket for lambda_1(H'(r)) against every LOWER and UPPER row the pinned tool prints from the stored vectors at that r.
import subprocess, sys
sys.path.insert(0, "C:/tmp/opus55/ym-two-sided")
from ownlib import *

R = "C:/tmp/opus55/ym-two-sided"
T = f"{R}/bin/perronritz-grid.exe"
DEV = f"{R}/dev22.bin"
fld, rows, ok, _ = read_store(DEV)
keep, W, M, Z = build(rows)
vecs = [f"{R}/vec/2x2-{t}.bin" for t in (45000000, 46000000, 46400000)] + [f"{R}/vec/2x2-g.bin"]
JBS = [0, 1, 250, 500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 12000, 27000, 81000, 243000]
out = subprocess.run([T, "pass", DEV, "0", "1000", ",".join(map(str, JBS))] + vecs[:3], capture_output=True, text=True).stdout.strip().splitlines()


def fields(line):
    return dict(x.split("=", 1) for x in line.strip().split("|")[1:] if "=" in x)


low = {}
up = {}
for l in out:
    if l.startswith("PERRONRITZ_LOWER"):
        f = fields(l)
        low.setdefault(int(f["JB"]), []).append(int(f["t_cert_milli"]))
    if l.startswith("PERRONRITZ_UPPER") and "upper_milli" in l:
        f = fields(l)
        up.setdefault(int(f["JB"]), []).append(int(f["upper_milli"]))
bad = 0
for jb in JBS:
    H = hp_rows(Z, M, 1000, jb)
    n = len(H)
    t0 = max(low[jb]) - 50000
    A = []
    for i in range(n):
        r = {j: W[i] * v for j, v in H[i].items()}
        r[i] = r.get(i, 0) - W[i] * t0
        A.append(r)
    try:
        fact = own_sparse_ldl(A, 160)
    except ArithmeticError as e:
        print("LDL_FAIL", jb, e)
        continue
    x = [1 << 600] * n
    for it in range(60):
        b = [W[i] * x[i] for i in range(n)]
        z = own_solve(fact, b, 0)
        for _ in range(3):
            res = [b[i] - sum(v * z[j] for j, v in A[i].items()) for i in range(n)]
            dz = own_solve(fact, res, 0)
            z = [z[i] + dz[i] for i in range(n)]
        sh = max(z).bit_length() - 600
        x = [(v >> sh) if sh > 0 else (v << -sh) for v in z]
        if it % 5 == 4 and min(x) > 0:
            lo = barta(H, x)[0]
            a, g = rayleigh(H, W, x)
            hi = ceil_div(a, g)
            if hi - lo <= 1:
                break
    bad_low = sum(1 for v in low[jb] if v > hi)
    bad_up = sum(1 for v in up[jb] if v < lo + 1 and v < hi)
    bad += bad_low + bad_up
    print(f"L2x2|JB={jb}|lambda1_ge={lo}|lambda1_le={hi}|tool_best_lower={max(low[jb])}|tool_best_upper={min(up[jb])}|upper_minus_ceil={min(up[jb]) - hi}|bad_lower={bad_low}|bad_upper={bad_up}|json=0", flush=True)
print(f"C1_COUPLINGS|bad={bad}|json=0")
