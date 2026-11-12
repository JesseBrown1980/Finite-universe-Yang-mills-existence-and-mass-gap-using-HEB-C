#!/usr/bin/env python3
"""crossing_v11.py -- where does each low value of the reduced matrix G(t) cross zero as t rises?
The certificate proves lambda_min >= t when the lowest value of G(t) is >= 0; the crossing of the k-th value is the
same comparison read for the k-th level. DESCRIPTIVE float diagnostic on the exactly rebuilt matrix; no prediction
was sealed; not a certified bound.
  python crossing_v11.py <rows.txt> <header.txt> <leaf.hbp>
"""
import hashlib, sys
from fractions import Fraction as Fr
import numpy as np

rows_txt = open(sys.argv[1]).read(); hdr = open(sys.argv[2]).read()
meta = dict(w.split("=", 1) for w in hdr.split() if "=" in w)
m0 = int(meta["m0"]); rn, rd = map(int, meta["r"].split("/")); tn, td = map(int, meta["t"].split("/"))
fvals = [int(x) for x in meta["f"].split(",")]; capn, capd = map(int, meta["cap"].split("/"))
assert hashlib.sha256(rows_txt.encode()).hexdigest() == meta["rowhash"]
r = rn / rd
f_of = lambda M: fvals[min(M - m0, len(fvals)) - 1]
W = {}
for line in open(sys.argv[3]):
    if line.startswith("LEAF|"):
        d = dict(w.split("=", 1) for w in line.strip().split("|")[1:] if "=" in w)
        W[int(d["key"])] = int(d["w"])
keys, Mof, core, tails, sigs, cur = [], {}, [], [], {}, None
for line in rows_txt.split("\n"):
    p = line.split()
    if not p:
        continue
    if p[0] == "C":
        cur = int(p[1]); keys.append(cur); Mof[cur] = int(p[2])
        for w in p[4:]:
            k, c = w.split(":"); core.append((cur, int(k), int(c)))
    elif p[0] == "T":
        sg = (p[1], p[2])
        if sg not in sigs:
            m1 = int(p[1]); hist = [int(x) for x in p[2].split(",")]; fk = f_of(m1)
            sigs[sg] = (len(sigs), fk, 72 + r * m1, float(sum(h * f_of(m1 + i - 4) for i, h in enumerate(hist) if h)))
        for b in p[3:]:
            tails.append((cur, int(b), sigs[sg][0]))
n = len(keys); idx = {k: i for i, k in enumerate(keys)}
ca = np.array([idx[a] for a, _, _ in core]); cb = np.array([idx[b] for _, b, _ in core]); cc = np.array([c for _, _, c in core], float)
ta = np.array([idx[a] for a, _, _ in tails]); tb = np.array([idx[b] for _, b, _ in tails]); ts = np.array([s for _, _, s in tails])
S_fk = np.zeros(len(sigs)); S_d = np.zeros(len(sigs)); S_sf = np.zeros(len(sigs))
for (i, fk, dd, sf) in sigs.values():
    S_fk[i], S_d[i], S_sf[i] = fk, dd, sf
diag0 = np.array([72 + r * Mof[k] for k in keys])
sw = np.sqrt(np.array([W[k] for k in keys], float))


def low(t, k=6):
    N = S_fk * (S_d - t) - S_sf
    if N.min() <= 0:
        return None
    G = np.zeros((n, n))
    G[np.arange(n), np.arange(n)] = diag0 - t
    np.subtract.at(G, (ca, cb), cc)
    np.subtract.at(G, (ta, tb), (S_fk / N)[ts])
    S = (sw[:, None] * G) / sw[None, :]
    return np.linalg.eigvalsh((S + S.T) / 2)[:k]


t0 = tn / td
tmax = min(capn / capd, min(S_d - S_sf / S_fk)) - 1e-6
out = []
for k in range(4):
    lo, hi = t0 - 1.0, tmax
    vlo, vhi = low(lo), low(hi)
    if vhi is None or vhi[k] > 0:
        out.append(None); continue
    for _ in range(40):
        mid = (lo + hi) / 2
        if low(mid)[k] > 0:
            lo = mid
        else:
            hi = mid
    out.append((lo + hi) / 2)
print("CROSSING|m0=%d|r=%s|f=%s|certified_floor=%.4f|largest_admissible_t=%.4f|zero_crossings_of_the_lowest_4_values=%s|json=0"
      % (m0, meta["r"], meta["f"], t0, tmax, "_".join(("%.6f" % x) if x is not None else "NOT_REACHED_BELOW_THE_ADMISSIBLE_LIMIT" for x in out)))
got = [x for x in out if x is not None]
if len(got) >= 2:
    print("CROSSING_GAPS|m0=%d|f=%s|differences_between_consecutive_crossings=%s|json=0" % (m0, meta["f"], "_".join("%.6f" % (b - a) for a, b in zip(got, got[1:]))))
