# C1: exact inertia of W (H' - theta) on a small store, by fraction-free elimination on the rows read by my own reader.
# usage: c1_inertia.py DEV JB THETA [THETA ...]
import sys, time
sys.path.insert(0, "C:/tmp/opus55/ym-two-sided")
from ownlib import *

dev, jb = sys.argv[1], int(sys.argv[2])
fld, rows, merkle_ok, tail0 = read_store(dev)
keep, W, M, Z = build(rows)
H = hp_rows(Z, M, 1000, jb)
n = len(H)
for th in map(int, sys.argv[3:]):
    t = time.time()
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j, v in H[i].items():
            A[i][j] = W[i] * v
        A[i][i] -= W[i] * th
    neg, last, reached = inertia_bareiss(A)
    print(f"INERTIA|L={fld['L']}|JB={jb}|theta={th}|n={n}|negative={neg}|det_sign={last}|reached={reached}|secs_wall={time.time() - t:.1f}|json=0", flush=True)
