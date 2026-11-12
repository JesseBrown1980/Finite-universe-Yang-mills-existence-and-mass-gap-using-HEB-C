#!/usr/bin/env python3
"""cluster_v10.py -- the low end of the spectrum of the reduced matrix G(t) = D - A, rebuilt exactly from the
verifier's canonical row text. See SPEC-CLUSTER-V10.hbp. Matrix entries are exact rationals; the eigenvalues are a
FLOAT DIAGNOSTIC (numpy eigh on the class-weight symmetrised matrix).
  python cluster_v10.py <rows.txt> <header.txt> <leaf.hbp>
"""
import hashlib, sys
from fractions import Fraction as Fr
import numpy as np

rows_txt = open(sys.argv[1]).read(); hdr = open(sys.argv[2]).read()
meta = dict(w.split("=", 1) for w in hdr.split() if "=" in w)
m0 = int(meta["m0"]); rn, rd = map(int, meta["r"].split("/")); tn, td = map(int, meta["t"].split("/"))
fvals = [int(x) for x in meta["f"].split(",")]
assert hashlib.sha256(rows_txt.encode()).hexdigest() == meta["rowhash"], "row text does not hash to the certificate rowhash"
r, t = Fr(rn, rd), Fr(tn, td)
TLABEL = "certificate_floor"
if len(sys.argv) > 5:
    t = Fr(sys.argv[5]); TLABEL = "common_t_" + sys.argv[5]
f_of = lambda M: fvals[min(M - m0, len(fvals)) - 1]
W, V, SL = {}, {}, {}
for line in open(sys.argv[3]):
    if line.startswith("LEAF|"):
        d = dict(w.split("=", 1) for w in line.strip().split("|")[1:] if "=" in w)
        W[int(d["key"])] = int(d["w"]); V[int(d["key"])] = int(d["v"]); SL[int(d["key"])] = int(d["slack"])
keys, Mof, ent, cur, wcache = [], {}, {}, None, {}
for line in rows_txt.split("\n"):
    p = line.split()
    if not p:
        continue
    if p[0] == "C":
        cur = int(p[1]); keys.append(cur); Mof[cur] = int(p[2]); ent[cur] = {}
        for w in p[4:]:
            k, c = w.split(":")
            ent[cur][int(k)] = ent[cur].get(int(k), 0.0) + int(c)
    elif p[0] == "T":
        sig = (p[1], p[2])
        if sig not in wcache:
            m1 = int(p[1]); hist = [int(x) for x in p[2].split(",")]; fk = f_of(m1)
            N = fk * (72 + r * m1 - t) - sum(h * f_of(m1 + i - 4) for i, h in enumerate(hist) if h)
            assert N > 0
            wcache[sig] = float(Fr(fk) / N)
        w = wcache[sig]
        for b in p[3:]:
            ent[cur][int(b)] = ent[cur].get(int(b), 0.0) + w
n = len(keys); idx = {k: i for i, k in enumerate(keys)}
G = np.zeros((n, n))
for k in keys:
    a = idx[k]; G[a, a] += float(72 + r * Mof[k] - t)
    for j, w in ent[k].items():
        G[a, idx[j]] -= w
v = np.array([V[k] for k in keys], float)
gv = G @ v
chk = float(np.abs(gv - np.array([SL[k] / (rd * td) for k in keys])).max() / np.abs(gv).max())
if TLABEL != "certificate_floor":
    chk = float("nan")
sw = np.sqrt(np.array([W[k] for k in keys], float))
S = (sw[:, None] * G) / sw[None, :]
asym = float(np.abs(S - S.T).max())
mu, Q = np.linalg.eigh((S + S.T) / 2)
low = mu[:12]
gaps = np.diff(low)
big = int(np.argmax(gaps[:8]))
print("CLUSTER|at=" + TLABEL + "|m0=%d|r=%s|f=%s|t=%s|rows=%d|rebuild_vs_leaves=%.1e|symmetry_defect=%.1e|lowest_12=%s|json=0"
      % (m0, meta["r"], meta["f"], meta["t"], n, chk, asym, "_".join("%.4f" % x for x in low)))
print("CLUSTER_READ|at=" + TLABEL + "|m0=%d|f=%s|values_below_1=%d|values_below_2=%d|largest_gap_among_the_first_nine=%.4f|it_follows_value_number=%d|cluster_width=%.4f|ratio_gap_over_width=%.2f|json=0"
      % (m0, meta["f"], int((mu < mu[0] + 1).sum()), int((mu < mu[0] + 2).sum()), float(gaps[big]), big + 1, float(low[big] - low[0]),
         float(gaps[big] / max(low[big] - low[0], 1e-12))))
print("INTERVALS|at=%s|m0=%d|f=%s|consecutive_differences_of_the_lowest_8=%s|json=0" % (TLABEL, m0, meta["f"], "_".join("%.4f" % x for x in np.diff(mu[:8]))))
Ms = sorted(set(Mof.values()))
Marr = np.array([Mof[k] for k in keys])
for kq in range(4):
    wts = [float((Q[Marr == M, kq] ** 2).sum()) for M in Ms]
    print("MODE|at=%s|m0=%d|f=%s|mode=%d|mu=%.6f|weight_by_magnetic_number=%s|sign_changes_possible=%d|json=0"
          % (TLABEL, m0, meta["f"], kq, mu[kq], "_".join("M%d:%.4f" % (M, w) for M, w in zip(Ms, wts)), int((Q[:, kq] > 0).sum() not in (0, n))))
if len(sys.argv) > 4 and sys.argv[4] != "-":
    np.savez(sys.argv[4], keys=np.array(keys, dtype=np.int64), Q=Q[:, :4], mu=mu[:12])
