#!/usr/bin/env python3
"""mode_v5.py -- is the residual leaf field of a certificate a picture of the next mode? See SPEC-MODE-V5.hbp.

Rebuilds the reduced matrix G(t) = D - A of one certificate from the verifier's own canonical row text (the text
whose sha256 is the certificate's rowhash), then compares the exact local ratio q_a = (G v)_a / v_a, which is
slack_a / (rd*td*v_a), with e1/e0 row by row. The eigen-decomposition is a FLOAT DIAGNOSTIC (numpy); the leaves,
the matrix entries and the rebuild check are exact.
  python mode_v5.py <rows.txt> <header.txt> <leaf.hbp>
"""
import hashlib, re, sys
from fractions import Fraction as Fr
import numpy as np

rows_txt = open(sys.argv[1]).read()
hdr = open(sys.argv[2]).read()
meta = dict(w.split("=", 1) for w in hdr.split() if "=" in w)
m0 = int(meta["m0"]); rn, rd = map(int, meta["r"].split("/")); tn, td = map(int, meta["t"].split("/"))
fvals = [int(x) for x in meta["f"].split(",")]
assert hashlib.sha256(rows_txt.encode()).hexdigest() == meta["rowhash"], "row text does not hash to the certificate rowhash"
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
    if not p:
        continue
    if p[0] == "C":
        cur = int(p[1]); keys.append(cur); Mof[cur] = int(p[2]); ent[cur] = {}
        for w in p[4:]:
            k, c = w.split(":")
            ent[cur][int(k)] = ent[cur].get(int(k), Fr(0)) + int(c)
    elif p[0] == "T":
        m1 = int(p[1]); hist = [int(x) for x in p[2].split(",")]
        fk = f_of(m1)
        sf = sum(h * f_of(m1 + i - 4) for i, h in enumerate(hist) if h)
        N = fk * (72 + r * m1 - t) - sf
        assert N > 0
        w = Fr(fk) / N
        for b in p[3:]:
            ent[cur][int(b)] = ent[cur].get(int(b), Fr(0)) + w
n = len(keys)
idx = {k: i for i, k in enumerate(keys)}
# exact rebuild check: (G v)_a must equal slack_a/(rd*td) up to the verifier's per-tail ceilings (each < 1 unit of slack)
worst = Fr(0)
ntail_of = {}
for k in keys:
    v, s, _ = leaf[k]
    gv = (72 + r * Mof[k] - t) * v - sum(w * leaf[j][0] for j, w in ent[k].items())
    worst = max(worst, abs(gv * rd * td - s) / max(abs(s), 1))
print("REBUILD|rows=%d|rowhash_ok=1|max_relative_difference_between_rebuilt_(Gv)_and_the_leaf_slack=%.3e|note=the_verifier_rounds_each_tail_term_up|json=0" % (n, float(worst)))

G = np.zeros((n, n))
for k in keys:
    a = idx[k]
    G[a, a] += float(72 + r * Mof[k] - t)
    for j, w in ent[k].items():
        G[a, idx[j]] -= float(w)
ev, V = np.linalg.eig(G)
order = np.argsort(ev.real)
mu = ev.real[order]
print("SPECTRUM|imag_max=%.2e|mu0=%.9f|mu1=%.9f|mu2=%.9f|mu3=%.9f|gap_mu1_minus_mu0=%.9f|json=0"
      % (float(np.abs(ev.imag).max()), mu[0], mu[1], mu[2], mu[3], mu[1] - mu[0]))
E = [V[:, order[i]].real for i in range(6)]
e0 = E[0] * (1 if E[0].sum() > 0 else -1)
print("E0|positive_entries=%d|of=%d|json=0" % (int((e0 > 0).sum()), n))
v = np.array([leaf[k][0] for k in keys], float)
q = np.array([leaf[k][1] / (rd * td * leaf[k][0]) for k in keys], float)
print("FIELD|q=local_ratio_slack/(rd*td*v)|min=%.9f|max=%.9f|mean=%.9f|json=0" % (q.min(), q.max(), q.mean()))
cos0 = abs(float(v @ e0) / (np.linalg.norm(v) * np.linalg.norm(e0)))
print("VECTOR_VS_E0|cosine=%.12f|json=0" % cos0)
def corr(x, y):
    x = x - x.mean(); y = y - y.mean()
    return float((x @ y) / (np.linalg.norm(x) * np.linalg.norm(y) or 1))
ratios = [E[i] / e0 for i in range(1, 6)]
cs = [corr(q, x) for x in ratios]
print("CORR|q_with_e1/e0=%.6f|e2/e0=%.6f|e3/e0=%.6f|e4/e0=%.6f|e5/e0=%.6f|json=0" % tuple(cs))
print("CORR_ALT|q_with_row_position=%.6f|q_with_magnetic_number=%.6f|q_with_log_v=%.6f|json=0"
      % (corr(q, np.arange(n, dtype=float)), corr(q, np.array([Mof[k] for k in keys], float)), corr(q, np.log(v))))
for kk in (1, 2, 3, 5):
    X = np.column_stack([np.ones(n)] + ratios[:kk])
    res = q - X @ np.linalg.lstsq(X, q, rcond=None)[0]
    print("FIT|modes_used=%d|share_of_the_field_variance_explained=%.6f|json=0" % (kk, 1 - float(res @ res) / float(((q - q.mean()) ** 2).sum())))
# shuffle null for the correlation with e1/e0
rng = np.random.default_rng(12345)
null = sorted(abs(corr(rng.permutation(q), ratios[0])) for _ in range(999))
print("NULL|statistic=abs_corr_q_with_e1/e0|shuffles=999|null_max=%.6f|null_95th=%.6f|real=%.6f|json=0" % (null[-1], null[949], abs(cs[0])))
