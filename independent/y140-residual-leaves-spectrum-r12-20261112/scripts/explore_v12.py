#!/usr/bin/env python3
"""explore_v12.py -- FLOAT exploration only (no claim): how tight is the second, inner comparison
K(t) = G_LL - G_LR diag(g/(G_RR g)) G_RL, with L = classes of magnetic number <= Lmax, against G(t) itself?
  python explore_v12.py <rows.txt> <header.txt> <leaf.hbp> <Lmax> <t1,t2,...>"""
import hashlib, sys
import numpy as np

rows_txt = open(sys.argv[1]).read(); hdr = open(sys.argv[2]).read()
meta = dict(w.split("=", 1) for w in hdr.split() if "=" in w)
m0 = int(meta["m0"]); rn, rd = map(int, meta["r"].split("/"))
fvals = [int(x) for x in meta["f"].split(",")]
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
diag0 = np.array([72 + r * Mof[k] for k in keys]); Marr = np.array([Mof[k] for k in keys])
w = np.array([W[k] for k in keys], float); sw = np.sqrt(w)
Lmax = int(sys.argv[4]); Lm = Marr <= Lmax; Rm = ~Lm
for ts_ in sys.argv[5].split(","):
    t = float(ts_)
    N = S_fk * (S_d - t) - S_sf
    G = np.zeros((n, n)); G[np.arange(n), np.arange(n)] = diag0 - t
    np.subtract.at(G, (ca, cb), cc); np.subtract.at(G, (ta, tb), (S_fk / N)[ts])
    S = (sw[:, None] * G) / sw[None, :]
    mu, Q = np.linalg.eigh((S + S.T) / 2)
    x0 = np.abs(Q[:, 0] / sw)                                   # lowest mode as a class vector
    GRR = G[np.ix_(Rm, Rm)]; GRL = G[np.ix_(Rm, Lm)]; GLR = G[np.ix_(Lm, Rm)]; GLL = G[np.ix_(Lm, Lm)]
    b = -GRL @ x0[Lm]
    b = b + 1e-6 * max(b.max(), 1e-30)
    g = np.linalg.solve(GRR, b)
    d = GRR @ g
    K = GLL - GLR @ ((g / d)[:, None] * GRL)
    if len(sys.argv) > 6:
        gi = np.maximum(np.rint(g / g.max() * 2.0**60), 1)
        with open("%s-t%s-L%d.txt" % (sys.argv[6], ts_, Lmax), "w") as fh:
            for k, v in zip(np.array(keys)[Rm], gi):
                fh.write("%d %d\n" % (k, int(v)))
    swL = sw[Lm]; KS = (swL[:, None] * K) / swL[None, :]
    kap = np.linalg.eigvalsh((KS + KS.T) / 2)
    print("EXPLORE|m0=%d|f=%s|Lmax=%d|L=%d|R=%d|t=%s|g_min=%.3e|d_min=%.3e|G_low=%s|G_negatives=%d|K_low=%s|K_negatives=%d|json=0"
          % (m0, meta["f"], Lmax, int(Lm.sum()), int(Rm.sum()), ts_, g.min(), d.min(), "_".join("%.5f" % x for x in mu[:4]), int((mu < 0).sum()),
             "_".join("%.5f" % x for x in kap[:4]), int((kap < 0).sum())))
