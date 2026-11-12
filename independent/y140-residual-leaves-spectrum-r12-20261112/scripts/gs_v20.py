#!/usr/bin/env python3
"""gs_v20.py -- is the leaf pattern the trace of the writer's Gauss-Seidel sweep order?  See SPEC-GS-V20.hbp.
The writer makes the certificate vector v by inverse iteration whose inner solve is 8 Gauss-Seidel sweeps over the
rows in key order. One sweep leaves, exactly,  ((F - sigma) x)_a = v_a - sum_{j after a} A_aj (x_j_new - x_j_old).
If the last change is close to a common factor gamma, the row quotient is  q_a = const - gamma * U_a  with
    U_a = sum_{j after a} A_aj v_j / v_a      (the share of row a's coupling that points FORWARD in key order).
Diagnostic in floats (rank correlations); the matrix and leaves are read exactly.
  python gs_v20.py <rows.txt> <header.txt> <leaf.hbp>
"""
import hashlib, sys
from fractions import Fraction as Fr
rows_txt = open(sys.argv[1]).read(); hdr = open(sys.argv[2]).read()
meta = dict(w.split("=", 1) for w in hdr.split() if "=" in w)
m0 = int(meta["m0"]); r = Fr(meta["r"]); t = Fr(meta["t"]); fvals = [int(x) for x in meta["f"].split(",")]
assert hashlib.sha256(rows_txt.encode()).hexdigest() == meta["rowhash"]
f_of = lambda M: fvals[min(M - m0, len(fvals)) - 1]
V = {}; S = {}
for line in open(sys.argv[3]):
    if line.startswith("LEAF|"):
        d = dict(w.split("=", 1) for w in line.strip().split("|")[1:] if "=" in w)
        V[int(d["key"])] = int(d["v"]); S[int(d["key"])] = int(d["slack"])
keys = []; Mof = {}; A = {}; cur = None; wc = {}
for line in rows_txt.split("\n"):
    p = line.split()
    if not p: continue
    if p[0] == "C":
        cur = int(p[1]); keys.append(cur); Mof[cur] = int(p[2]); A[cur] = {}
        for w in p[4:]:
            k, c = w.split(":"); A[cur][int(k)] = A[cur].get(int(k), 0.0) + int(c)
    elif p[0] == "T":
        sg = (p[1], p[2])
        if sg not in wc:
            m1 = int(p[1]); hist = [int(x) for x in p[2].split(",")]; fk = f_of(m1)
            wc[sg] = float(Fr(fk) / (fk * (72 + r * m1 - t) - sum(h * f_of(m1 + i - 4) for i, h in enumerate(hist) if h)))
        for b in p[3:]:
            A[cur][int(b)] = A[cur].get(int(b), 0.0) + wc[sg]
pos = {k: i for i, k in enumerate(keys)}
leaf = []; U = []; B = []; Tt = []; Mm = []
for a in keys:
    va = V[a]; u = b = 0.0
    for j, w in A[a].items():
        if j == a: continue
        if pos[j] > pos[a]: u += w * V[j] / va
        else: b += w * V[j] / va
    leaf.append(S[a] / va); U.append(u); B.append(b); Tt.append(u + b); Mm.append(Mof[a])
def rank(x):
    o = sorted(range(len(x)), key=lambda i: x[i]); rk = [0.0] * len(x); i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and x[o[j + 1]] == x[o[i]]: j += 1
        for q in range(i, j + 1): rk[o[q]] = (i + j) / 2
        i = j + 1
    return rk
def sp(x, y):
    a = rank(x); b = rank(y); n = len(a); ma = sum(a) / n; mb = sum(b) / n
    c = sum((p - ma) * (q - mb) for p, q in zip(a, b)); da = sum((p - ma) ** 2 for p in a); db = sum((q - mb) ** 2 for q in b)
    return c / (da * db) ** 0.5 if da and db else 0.0
frac = [u / tt if tt else 0.0 for u, tt in zip(U, Tt)]
print("GSV20|m0=%d|f=%s|rows=%d|spearman_leaf_vs_forward_U=%.3f|vs_backward_B=%.3f|vs_total=%.3f|vs_forward_fraction=%.3f|vs_M=%.3f|vs_key_position=%.3f|float_diagnostic=1|json=0" % (
    m0, meta["f"], len(keys), sp(leaf, U), sp(leaf, B), sp(leaf, Tt), sp(leaf, frac), sp(leaf, Mm), sp(leaf, list(range(len(keys))))))
