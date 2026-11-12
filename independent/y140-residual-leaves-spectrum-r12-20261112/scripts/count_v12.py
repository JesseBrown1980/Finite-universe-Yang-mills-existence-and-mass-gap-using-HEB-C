#!/usr/bin/env python3
"""count_v12.py -- EXACT count: how many levels of the comparison matrix G(t) can lie below zero (symmetric sector).

Chain (see STEP1-BRIDGE note): N_<t(H_Q, symmetric sector) <= n_-(G(t)) <= n_-(K(t)), where, with the core classes
split into L (magnetic number <= Lmax) and R (the rest) and any positive vector g on R with d = G_RR g > 0,
    K(t) = B_LL - B_LR diag( g_a / (W_a d_a) ) B_RL ,   B = diag(W) G   (symmetric).
Everything here is exact (Python integers and Fractions). The witness g is read from a file; ANY positive integer
vector is admissible, so how it was produced (a float solve) does not enter the proof.
  python count_v12.py <rows.txt> <header.txt> <leaf.hbp> <t as a/b> <Lmax> <witness_file>
"""
import hashlib, sys
from fractions import Fraction as Fr

rows_txt = open(sys.argv[1]).read(); hdr = open(sys.argv[2]).read()
meta = dict(w.split("=", 1) for w in hdr.split() if "=" in w)
m0 = int(meta["m0"]); rn, rd = map(int, meta["r"].split("/"))
fvals = [int(x) for x in meta["f"].split(",")]
assert hashlib.sha256(rows_txt.encode()).hexdigest() == meta["rowhash"], "row text does not hash to the certificate rowhash"
r = Fr(rn, rd); t = Fr(sys.argv[4]); cap = Fr(meta["cap"]); Lmax = int(sys.argv[5])
assert t < cap, "t is not below the certified tail cap"
f_of = lambda M: fvals[min(M - m0, len(fvals)) - 1]
W = {}
for line in open(sys.argv[3]):
    if line.startswith("LEAF|"):
        d = dict(w.split("=", 1) for w in line.strip().split("|")[1:] if "=" in w)
        W[int(d["key"])] = int(d["w"])
keys, Mof, G, cur, wc = [], {}, {}, None, {}
for line in rows_txt.split("\n"):
    p = line.split()
    if not p:
        continue
    if p[0] == "C":
        cur = int(p[1]); keys.append(cur); Mof[cur] = int(p[2]); G[cur] = {cur: 72 + r * Mof[cur] - t}
        for w in p[4:]:
            k, c = w.split(":"); k = int(k)
            G[cur][k] = G[cur].get(k, Fr(0)) - int(c)
    elif p[0] == "T":
        sg = (p[1], p[2])
        if sg not in wc:
            m1 = int(p[1]); hist = [int(x) for x in p[2].split(",")]; fk = f_of(m1)
            N = fk * (72 + r * m1 - t) - sum(h * f_of(m1 + i - 4) for i, h in enumerate(hist) if h)
            assert N > 0, "a one-step tail denominator is not positive at this t"
            wc[sg] = Fr(fk) / N
        w = wc[sg]
        for b in p[3:]:
            b = int(b); G[cur][b] = G[cur].get(b, Fr(0)) - w
# exact W-self-adjointness of the whole matrix, and the sign pattern the comparison needs
nsym = nbad = 0
for a in keys:
    for b, x in G[a].items():
        if a != b:
            if x > 0:
                nbad += 1
            if W[a] * x != W[b] * G[b].get(a, Fr(0)):
                nsym += 1
L = [k for k in keys if Mof[k] <= Lmax]; R = [k for k in keys if Mof[k] > Lmax]
Rset = set(R); Lset = set(L)
g = {}
for line in open(sys.argv[6]):
    k, v = line.split(); g[int(k)] = int(v)
assert set(g) == Rset and all(v >= 1 for v in g.values()), "witness must be a positive integer vector on R"
dmin = None; coef = {}
for a in R:
    da = sum(x * g[b] for b, x in G[a].items() if b in Rset)
    if dmin is None or da < dmin:
        dmin = da
    if da > 0:
        coef[a] = Fr(g[a]) / (W[a] * da)
ok_R = dmin > 0
print("COUNTHDR|m0=%d|r=%s|f=%s|t=%s|cap=%s|classes=%d|L=%d_(M<=%d)|R=%d|offdiagonal_entries_positive=%d|W_selfadjoint_violations=%d|json=0"
      % (m0, meta["r"], meta["f"], sys.argv[4], meta["cap"], len(keys), len(L), Lmax, len(R), nbad, nsym))
print("RBLOCK|witness_positive=1|min_of_G_RR_g=%s|G_RR_positive_definite_certified=%d|json=0" % ("POSITIVE" if ok_R else "NOT_POSITIVE", int(ok_R and nbad == 0 and nsym == 0)))
if not (ok_R and nbad == 0 and nsym == 0):
    print("COUNT|result=NOT_CERTIFIED|json=0"); sys.exit(1)
li = {k: i for i, k in enumerate(L)}; n = len(L)
K = [[Fr(0)] * n for _ in range(n)]
for i_k in L:
    for b, x in G[i_k].items():
        if b in Lset:
            K[li[i_k]][li[b]] += W[i_k] * x
for a in R:
    ent = [(li[b], W[a] * x) for b, x in G[a].items() if b in Lset]
    if ent:
        c = coef[a]
        for i, bi in ent:
            for j, bj in ent:
                K[i][j] -= bi * bj * c
assert all(K[i][j] == K[j][i] for i in range(n) for j in range(i)), "K is not symmetric"
# exact inertia by symmetric elimination (LDL^T with diagonal pivoting)
neg = pos = 0; act = list(range(n))
while act:
    piv = next((i for i in act if K[i][i] != 0), None)
    assert piv is not None, "zero diagonal block met: inertia not decided by this elimination"
    dpiv = K[piv][piv]
    neg += dpiv < 0; pos += dpiv > 0
    act.remove(piv)
    rowp = K[piv]
    for i in act:
        if K[i][piv] != 0:
            fct = K[i][piv] / dpiv
            Ki = K[i]
            for j in act:
                if rowp[j] != 0:
                    Ki[j] -= fct * rowp[j]
print("COUNT|n_minus_of_K=%d|n_plus_of_K=%d|therefore_levels_of_the_symmetric_sector_strictly_below_t=AT_MOST_%d|so_level_number_%d_is_at_least_t=%s|exact=1|float_used=0|json=0"
      % (neg, pos, neg, neg + 1, sys.argv[4]))
