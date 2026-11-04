# Integer copy of native/ym/results/3x4_stream/perron/second-seat/own34_post.py, written by native/scripts/make_integer_pairs.py: 1 divisions moved to qdiv and 3 text pairs. The original stays as evidence.
# Post-process of own34.exe: compare the store-free forms with pass1.out, and test E from the solved equations.
import re, sys
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "..", "scripts"))
from intpair import IntPair as F, qdiv

HERE = os.path.dirname(os.path.abspath(__file__))
rows = [l.strip() for l in open(os.path.join(HERE, "..", "..", "..", "..", "integer-pairs-2026-11-03", "inputs", "own34.out"), newline="").read().replace("\r", "").splitlines() if l.strip()]


def big(s):
    hi, lo = s.split(":")
    return (int(hi) << 128) + int(lo)


D = {}
G = {}
M = {}
for l in rows:
    f = dict(x.split("=", 1) for x in l.split("|")[1:] if "=" in x)
    tag = l.split("|")[0]
    if tag == "OWN34_D":
        D[int(f["i"])] = f
    elif tag == "OWN34_FORM":
        a, b = int(f["a"]), int(f["b"])
        G[(a, b)] = G[(b, a)] = big(f["G"])
        M[(a, b)] = M[(b, a)] = big(f["M"])
    elif tag in ("OWN34", "OWN34_REBUILD", "OWN34_PREDICT", "OWN34_HIST"):
        print(l)
txt = open(os.path.join(HERE, "..", "..", "PASS1-3x4.out"), newline="").read().replace("\r", "")
E_ = {}
mis = 0
for l in txt.splitlines():
    if l.startswith("PERRONRITZ_FORM|"):
        f = dict(x.split("=", 1) for x in l.split("|")[1:] if "=" in x)
        a, b = int(f["a"]), int(f["b"])
        E_[(a, b)] = E_[(b, a)] = int(f["E"])
        if int(f["G"]) != G[(a, b)] or int(f["M"]) != M[(a, b)]:
            mis += 1
            print("FORM_MISMATCH", a, b)
    if l.startswith("PERRONRITZ_D|"):
        f = dict(x.split("=", 1) for x in l.split("|")[1:] if "=" in x)
        i = int(f["i"])
        if f["d_sha256"] != D[i]["sha256"] or int(f["d_min"]) != int(D[i]["d_min"]) or int(f["d_max"]) != int(D[i]["d_max"]):
            print("D_MISMATCH", i, f, D[i])
print(f"PASS1_G_M_AGAINST_OWN|pairs_checked=10|mismatch={mis}|json=0")
for i in sorted(D):
    print({k: D[i][k] for k in ("i", "file", "sha256", "d_min", "d_max", "argmax_row", "nonpositive", "flat_nonzero", "extra_rows")})

# E from the solved equations, with no room read: (H' - t_b) d_b = s + r_b gives A_ab = t_b G_ab + s L_a + <d_a, r_b>_W.
s = 10**6 * 2**30
ts = {0: 93000000, 1: 93700000, 2: 93950000}
L = {i: big(D[i]["L"]) for i in D}
for a in range(3):
    for b in range(3):
        A = 10**6 * E_[(a, b)] + 9 * 10**6 * M[(a, b)]
        pred = ts[b] * G[(a, b)] + s * L[a]
        dev = A - pred
        print(f"E_FROM_SOLVE|a={a}|b={b}|relative_dev_e12={F(dev, A) * 10**12 // 1}|dev_over_G_milli={F(dev, G[(a, b)]) // 1}|json=0")


def pd(mat):
    n = len(mat)
    m = [[F(x) for x in r] for r in mat]
    for c in range(n):
        if m[c][c] <= 0:
            return False
        for i in range(c + 1, n):
            f = qdiv(m[i][c] , m[c][c])
            if f:
                m[i] = [x - f * y for x, y in zip(m[i], m[c])]
    return True


def upper(Am, Gm):
    lo, hi = 0, -((-Am[0][0]) // Gm[0][0])
    k = len(Am)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if pd([[Am[i][j] - mid * Gm[i][j] for j in range(k)] for i in range(k)]):
            lo = mid
        else:
            hi = mid
    return hi


# Ritz from the vectors and weights alone: A_ab = symmetrised t_b G_ab + s L_a. The E of pass1 plays no part.
for pick in ([0, 1], [0, 2], [1, 2], [0, 1, 2]):
    Am = [[(ts[y] * G[(x, y)] + s * L[x] + ts[x] * G[(x, y)] + s * L[y]) // 2 for y in pick] for x in pick]
    Gm = [[G[(x, y)] for y in pick] for x in pick]
    print(f"RITZ_STORE_FREE|vectors={pick}|upper={upper(Am, Gm)}|json=0")
# The converged vector in place of 3-pass one, on the span with 93 and 93.7. There is no E row for it, so this is the store-free estimate.
ts2 = {0: 93000000, 1: 93700000, 4: 93950000}
for pick in ([0, 4], [1, 4], [0, 1, 4]):
    Am = [[(ts2[y] * G[(x, y)] + s * L[x] + ts2[x] * G[(x, y)] + s * L[y]) // 2 for y in pick] for x in pick]
    Gm = [[G[(x, y)] for y in pick] for x in pick]
    print(f"RITZ_STORE_FREE|vectors={pick}|upper={upper(Am, Gm)}|json=0")
