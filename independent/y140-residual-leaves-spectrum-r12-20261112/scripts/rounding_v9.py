#!/usr/bin/env python3
"""rounding_v9.py -- is the residual field the writer's fixed-point rounding? See SPEC-ROUNDING-V9.hbp.
Exact rationals for q, S and the exact per-entry rounding sum R; correlation and fit are float diagnostics.
  python rounding_v9.py <rows.txt> <header.txt> <leaf.hbp>"""
import hashlib, sys
from fractions import Fraction as Fr
import numpy as np
rows_txt = open(sys.argv[1]).read(); hdr = open(sys.argv[2]).read()
meta = dict(w.split("=", 1) for w in hdr.split() if "=" in w)
m0 = int(meta["m0"]); rn, rd = map(int, meta["r"].split("/")); tn, td = map(int, meta["t"].split("/"))
fvals = [int(x) for x in meta["f"].split(",")]
assert hashlib.sha256(rows_txt.encode()).hexdigest() == meta["rowhash"]
r, t = Fr(rn, rd), Fr(tn, td); E = 1 << 20
f_of = lambda M: fvals[min(M - m0, len(fvals)) - 1]
leaf = {}
for line in open(sys.argv[3]):
    if line.startswith("LEAF|"):
        d = dict(w.split("=", 1) for w in line.strip().split("|")[1:] if "=" in w)
        leaf[int(d["key"])] = (int(d["v"]), int(d["slack"]))
keys, S, R, cur = [], {}, {}, None
for line in rows_txt.split("\n"):
    p = line.split()
    if not p: continue
    if p[0] == "C":
        cur = int(p[1]); keys.append(cur); S[cur] = 0; R[cur] = Fr(0)
        M = int(p[2]); dg = 72 + r * M - t
        R[cur] += (dg - Fr((dg * E).__floor__(), E)) * leaf[cur][0]            # diagonal rounded down
    elif p[0] == "T":
        m1 = int(p[1]); hist = [int(x) for x in p[2].split(",")]; fk = f_of(m1)
        N = fk * (72 + r * m1 - t) - sum(h * f_of(m1 + i - 4) for i, h in enumerate(hist) if h)
        w = Fr(fk) / N; dw = w - Fr((w * E).__floor__(), E)                   # this back weight rounded down
        sb = sum(leaf[int(b)][0] for b in p[3:])
        S[cur] += sb; R[cur] -= dw * sb                                        # exact matrix has MORE coupling: lowers (Gv)
q = np.array([float(Fr(leaf[k][1], rd * td * leaf[k][0])) for k in keys])
s = np.array([S[k] / leaf[k][0] for k in keys], float)
rr = np.array([float(R[k] / leaf[k][0]) for k in keys])
def corr(a, b):
    a = a - a.mean(); b = b - b.mean(); return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
A = np.column_stack([np.ones(len(s)), s]); (c0, slope), *_ = np.linalg.lstsq(A, q, rcond=None)
B = np.column_stack([np.ones(len(s)), rr]); (b0, b1), *_ = np.linalg.lstsq(B, q, rcond=None)
resB = q - B @ np.array([b0, b1])
print("ROUNDING|cert_f=%s|rows=%d|S_min=%.2f|S_max=%.2f|corr_q_with_S=%.6f|slope=%.4e|predicted_slope=-4.77e-07|corr_q_with_exact_rounding_sum_R=%.6f|slope_on_R=%.4f|share_of_variance_explained_by_R=%.6f|json=0"
      % (meta["f"], len(keys), s.min(), s.max(), corr(q, s), slope, corr(q, rr), b1, 1 - float(resB @ resB) / float(((q - q.mean()) ** 2).sum())))
