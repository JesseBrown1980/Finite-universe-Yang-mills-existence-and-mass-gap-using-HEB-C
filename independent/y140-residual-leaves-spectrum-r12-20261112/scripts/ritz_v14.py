#!/usr/bin/env python3
"""ritz_v14.py -- EXACT Rayleigh-Ritz upper bounds on the first three levels from three zero-extended class vectors.
min-max: if the 3x3 pencil (A - u B) has at least k negative eigenvalues then level k of H_Q is below u.
A_ij = sum_a W_a x_ai (H_CC x_j)_a, B_ij = sum_a W_a x_ai x_aj, H_CC = (72 + r M) - core move counts (the verifier's
own Ritz form). Exact integers/Fractions; the trial vectors are read as integers (any vectors are admissible).
  python ritz_v14.py <rows.txt> <header.txt> <leaf.hbp> <modes.npz> <u1,u2,u3 as a/b>"""
import hashlib, sys
from fractions import Fraction as Fr
import numpy as np
rows_txt = open(sys.argv[1]).read(); hdr = open(sys.argv[2]).read()
meta = dict(w.split("=", 1) for w in hdr.split() if "=" in w)
rn, rd = map(int, meta["r"].split("/")); r = Fr(rn, rd)
assert hashlib.sha256(rows_txt.encode()).hexdigest() == meta["rowhash"]
W = {}
for line in open(sys.argv[3]):
    if line.startswith("LEAF|"):
        d = dict(w.split("=", 1) for w in line.strip().split("|")[1:] if "=" in w)
        W[int(d["key"])] = int(d["w"])
z = np.load(sys.argv[4]); keys = [int(k) for k in z["keys"]]
sw = np.sqrt(np.array([W[k] for k in keys], float))
X = [[int(v) for v in np.rint(z["Q"][:, j] / sw / np.abs(z["Q"][:, j] / sw).max() * 2.0**40)] for j in range(3)]   # integer trial vectors
idx = {k: i for i, k in enumerate(keys)}
HX = [[Fr(0)] * len(keys) for _ in range(3)]
for line in rows_txt.split("\n"):
    p = line.split()
    if p and p[0] == "C":
        a = idx[int(p[1])]; dg = 72 + r * int(p[2])
        for j in range(3):
            s = dg * X[j][a]
            for w in p[4:]:
                k, c = w.split(":"); s -= int(c) * X[j][idx[int(k)]]
            HX[j][a] = s
Wl = [W[k] for k in keys]
A = [[sum(Wl[a] * X[i][a] * HX[j][a] for a in range(len(keys))) for j in range(3)] for i in range(3)]
B = [[sum(Wl[a] * X[i][a] * X[j][a] for a in range(len(keys))) for j in range(3)] for i in range(3)]
assert all(A[i][j] == A[j][i] for i in range(3) for j in range(3)), "A not symmetric"
def negatives(M):
    m1 = M[0][0]; m2 = M[0][0] * M[1][1] - M[0][1] * M[1][0]
    m3 = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0]) + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    assert m1 != 0 and m2 != 0 and m3 != 0
    sg = [1, 1 if m1 > 0 else -1, 1 if m2 > 0 else -1, 1 if m3 > 0 else -1]
    return sum(1 for k in range(1, 4) if sg[k] != sg[k - 1])
Af = np.array([[float(x) for x in row] for row in A]); Bf = np.array([[float(x) for x in row] for row in B])
th = np.sort(np.linalg.eigvals(np.linalg.solve(Bf, Af)).real)
print("RITZ_FLOAT_GUIDE|theta=%.6f_%.6f_%.6f|json=0" % tuple(th))
for k, us in enumerate(sys.argv[5].split(","), start=1):
    u = Fr(us)
    nneg = negatives([[A[i][j] - u * B[i][j] for j in range(3)] for i in range(3)])
    print("RITZ|m0=%s|f=%s|u=%s|negative_eigenvalues_of_A_minus_uB=%d|therefore_level_%d_is_below_u=%s|exact=1|json=0"
          % (meta["m0"], meta["f"], us, nneg, k, "YES" if nneg >= k else "NOT_SHOWN"))
