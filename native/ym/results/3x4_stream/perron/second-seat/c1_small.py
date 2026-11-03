# C1: lambda_1(H') on 2x2 and 2x3 from my own reader, own elimination, own exact Barta and Rayleigh. usage: c1_small.py DEV JB T0 ITER [X_BITS]
import sys, time
sys.path.insert(0, "C:/tmp/opus55/ym-two-sided")
from ownlib import *

dev, jb, t0, iters = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
XB = int(sys.argv[5]) if len(sys.argv) > 5 else 600
tick = time.time()
fld, rows, merkle_ok, tail0 = read_store(dev)
print(f"STORE|L={fld['L']}|n={fld['n']}|merkle_own={merkle_ok}|padding_zero={tail0}|json=0")
print("AUDIT", {k: (v if k != 'flats' else v) for k, v in audit(rows).items()})
keep, W, M, Z = build(rows)
H = hp_rows(Z, M, 1000, jb)
n = len(H)
# A = W (H' - t0), symmetric integer.
A = []
for i in range(n):
    r = {j: W[i] * v for j, v in H[i].items()}
    r[i] = r.get(i, 0) - W[i] * t0
    A.append(r)
sym_bad = sum(1 for i in range(n) for j, v in A[i].items() if A[j].get(i, 0) != v)
print(f"SYMMETRIC_A|bad={sym_bad}|json=0")
fact = own_sparse_ldl(A, 160)
print(f"LDL|ops={fact[3]}|secs={time.time() - tick:.1f}|json=0".replace("secs=", "secs_wall="))
one = 1 << XB
x = [one for _ in range(n)]
for it in range(iters):
    b = [W[i] * x[i] for i in range(n)]
    # iterative refinement of the solve, exact residual, to carry far more bits than the factors hold
    z = own_solve(fact, b, 0)
    for _ in range(4):
        res = [b[i] - sum(v * z[j] for j, v in A[i].items()) for i in range(n)]
        dz = own_solve(fact, res, 0)
        z = [z[i] + dz[i] for i in range(n)]
    big = max(z)
    # renormalise so the largest entry is about 2^XB
    sh = big.bit_length() - XB
    x = [(v >> sh) if sh > 0 else (v << -sh) for v in z]
    if min(x) <= 0:
        print(f"ITER|{it}|min_x_nonpositive|json=0")
        continue
    lo = barta(H, x)
    a, g = rayleigh(H, W, x)
    print(f"ITER|{it}|barta_floor={lo[0]}|barta_row={keep[lo[1]]}|rayleigh_ceil={ceil_div(a, g)}|width={ceil_div(a, g) - lo[0]}|min_x_bits={min(x).bit_length()}|secs_wall={time.time() - tick:.1f}|json=0", flush=True)
print(f"RESULT|L={fld['L']}|JB={jb}|lambda1_ge={lo[0]}|lambda1_le={ceil_div(a, g)}|json=0")
