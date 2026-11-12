#!/usr/bin/env python3
"""leak_v6.py -- is the residual leaf field the row's coupling into the discarded sector? See SPEC-LEAK-V6.hbp.
Exact rationals for tau and q; the correlation and the line fit are float diagnostics.
  python leak_v6.py <rows.txt> <header.txt> <leaf.hbp>"""
import hashlib, sys
from fractions import Fraction as Fr
import numpy as np
rows_txt = open(sys.argv[1]).read(); hdr = open(sys.argv[2]).read()
meta = dict(w.split("=", 1) for w in hdr.split() if "=" in w)
m0 = int(meta["m0"]); rn, rd = map(int, meta["r"].split("/")); tn, td = map(int, meta["t"].split("/"))
fvals = [int(x) for x in meta["f"].split(",")]
assert hashlib.sha256(rows_txt.encode()).hexdigest() == meta["rowhash"]
r, t = Fr(rn, rd), Fr(tn, td)
f_of = lambda M: fvals[min(M - m0, len(fvals)) - 1]
leaf = {}
for line in open(sys.argv[3]):
    if line.startswith("LEAF|"):
        d = dict(w.split("=", 1) for w in line.strip().split("|")[1:] if "=" in w)
        leaf[int(d["key"])] = (int(d["v"]), int(d["slack"]))
keys, tau, cur = [], {}, None
for line in rows_txt.split("\n"):
    p = line.split()
    if not p: continue
    if p[0] == "C":
        cur = int(p[1]); keys.append(cur); tau[cur] = Fr(0)
    elif p[0] == "T":
        m1 = int(p[1]); hist = [int(x) for x in p[2].split(",")]; fk = f_of(m1)
        N = fk * (72 + r * m1 - t) - sum(h * f_of(m1 + i - 4) for i, h in enumerate(hist) if h)
        tau[cur] += Fr(fk * fk) / (N * N) * sum(leaf[int(b)][0] for b in p[3:])
q = np.array([float(Fr(leaf[k][1], rd * td * leaf[k][0])) for k in keys])
x = np.array([float(tau[k] / leaf[k][0]) for k in keys])
def corr(a, b):
    a = a - a.mean(); b = b - b.mean(); return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
c = corr(q, x)
A = np.column_stack([np.ones(len(x)), 1 + x]); (mu0, dt), *_ = np.linalg.lstsq(A, q, rcond=None)
res = q - A @ np.array([mu0, dt])
print("LEAK|cert_f=%s|t=%s|rows=%d|tau_min=%.6f|tau_max=%.6f|corr_q_with_tau=%.9f|fit_q=mu0+dt*(1+tau)|mu0=%.9f|dt=%.9f|dt_in_units_of_1/10000=%.4f|share_of_variance_explained=%.9f|largest_misfit_over_field_range=%.3e|json=0"
      % (meta["f"], meta["t"], len(keys), x.min(), x.max(), c, mu0, dt, dt * 10000, 1 - float(res @ res) / float(((q - q.mean()) ** 2).sum()), float(np.abs(res).max() / (q.max() - q.min()))))
