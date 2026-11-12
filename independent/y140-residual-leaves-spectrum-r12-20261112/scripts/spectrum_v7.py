#!/usr/bin/env python3
"""spectrum_v7.py -- where in the spectrum of G(t) does a certificate's residual live? Float diagnostic on the exact
rebuilt matrix (same rebuild as mode_v5.py). Descriptive; no prediction was sealed for this one.
  python spectrum_v7.py <rows.txt> <header.txt> <leaf.hbp> <out.npy>"""
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
        leaf[int(d["key"])] = (int(d["v"]), int(d["slack"]), int(d["w"]))
keys, Mof, ent, cur = [], {}, {}, None
for line in rows_txt.split("\n"):
    p = line.split()
    if not p: continue
    if p[0] == "C":
        cur = int(p[1]); keys.append(cur); Mof[cur] = int(p[2]); ent[cur] = {}
        for w in p[4:]:
            k, c = w.split(":"); ent[cur][int(k)] = ent[cur].get(int(k), 0.0) + int(c)
    elif p[0] == "T":
        m1 = int(p[1]); hist = [int(x) for x in p[2].split(",")]; fk = f_of(m1)
        N = fk * (72 + r * m1 - t) - sum(h * f_of(m1 + i - 4) for i, h in enumerate(hist) if h)
        w = float(Fr(fk) / N)
        for b in p[3:]: ent[cur][int(b)] = ent[cur].get(int(b), 0.0) + w
n = len(keys); idx = {k: i for i, k in enumerate(keys)}
G = np.zeros((n, n))
for k in keys:
    a = idx[k]; G[a, a] += float(72 + r * Mof[k] - t)
    for j, w in ent[k].items(): G[a, idx[j]] -= w
# symmetrise with the class weights W: S = W^(1/2) G W^(-1/2)
W = np.array([leaf[k][2] for k in keys], float); sw = np.sqrt(W)
S = (sw[:, None] * G) / sw[None, :]
asym = float(np.abs(S - S.T).max())
mu, Q = np.linalg.eigh((S + S.T) / 2)
v = np.array([leaf[k][0] for k in keys], float)
res = np.array([leaf[k][1] / (rd * td) for k in keys], float)          # (G v)_a, exact numerators
c = Q.T @ (sw * res)                                                     # residual in the orthonormal eigenbasis
e = c * c; tot = e.sum()
cum = np.cumsum(e) / tot
half = int(np.searchsorted(cum, 0.5)); p90 = int(np.searchsorted(cum, 0.9))
print("SPECTRUM7|cert_f=%s|rows=%d|symmetry_defect=%.2e|mu_min=%.6f|mu_max=%.6f|residual_energy_in_mode_0=%.6f|in_modes_1_to_5=%.6f|in_the_top_half_of_the_spectrum=%.6f|median_mode_index=%d|mu_at_median=%.4f|mode_index_at_90pct=%d|json=0"
      % (meta["f"], n, asym, mu[0], mu[-1], e[0] / tot, e[1:6].sum() / tot, e[n // 2:].sum() / tot, half, mu[half], p90))
np.save(sys.argv[4], np.vstack([mu, c]))
