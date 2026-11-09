#!/usr/bin/env python3
# Strong-coupling (large r) effective Hamiltonian on the 8 flats, computed EXACTLY from the
# #136 orbit graph (exact Fractions). H = 72 + r M - Lmoves in orbit coordinates.
# Unperturbed H0 = 72 + r M (diagonal), V = -c (every electric move, orbit coordinates).
# Bloch expansion with PVP = 0 (no flat-flat move):
#   order 2: P V R V P            = -D2 / r
#   order 3: P V R V R V P        = -C1 / r^2       (verifies GPT-6's C1 normalization)
#   order 4: P V R V R V R V P - 1/2{P V R^2 V P, P V R V P}  -> off-diagonal part -C2 / r^3
# R = Q/(72 - H0) = -Q/(r M). Then first-order (in 1/r) eigenvector perturbation of
# -C1 by -C2/r gives the leading Wilson-sum amplitude ground -> even second level.
# Exact rationals only; decimals printed via exact integer rounding. json=0.
import sys
from fractions import Fraction as Fr
sys.path.insert(0, '/mnt/c/tmp/opus55/ym137-fable5-20261109/d2-feshbach-r9')
import fe_common as fc

d, cache_sha, _ = fc.load()
w, m, adj, qflat, O, flat_out = d['w'], d['m'], d['adj'], d['qflat'], d['O'], d['flat_out']
n = len(adj)
mq = m[8:]


def dec(x, digits=12):
    x = Fr(x)
    s = '-' if x < 0 else ''
    x = abs(x)
    q = (x.numerator * 10 ** digits * 2 + x.denominator) // (2 * x.denominator)
    ip, fp = divmod(q, 10 ** digits)
    return '%s%d.%0*d' % (s, ip, digits, fp)


def prop(vec, den_power=1):
    """vec: dict Q-index -> Fraction (already divided by M of that state); apply c_{j1 j2}"""
    out = {}
    for j, v in vec.items():
        for j2, cc in adj[j]:
            out[j2] = out.get(j2, 0) + v * cc
    return out


def divM(vec):
    return {j: v / mq[j] for j, v in vec.items()}


D2 = [Fr(0)] * 8
C1 = [[Fr(0)] * 8 for _ in range(8)]
C2raw = [[Fr(0)] * 8 for _ in range(8)]
SQ = [[Fr(0)] * 8 for _ in range(8)]   # P V R^2 V P coefficient: sum c c / M^2
for k in range(8):
    v1 = {j: Fr(cc) for j, cc in flat_out[k].items()}
    assert all(mq[j] == 4 for j in v1)
    v1m = divM(v1)
    for l in range(8):
        s2 = sum(v1m[j] * qflat[j][l] for j in v1m)
        s2sq = sum(v1m[j] * qflat[j][l] / mq[j] for j in v1m)
        if l == k:
            D2[k] = s2
        else:
            assert s2 == 0, 'two-move flat-flat path exists'
        SQ[k][l] = s2sq
    v2 = divM(prop(v1m))
    for l in range(8):
        C1[k][l] = sum(v2[j] * qflat[j][l] for j in v2)
    v3 = divM(prop(v2))
    for l in range(8):
        C2raw[k][l] = sum(v3[j] * qflat[j][l] for j in v3)

# H_eff r-expansion coefficients (H_eff = 72 - D2/r - C1/r^2 - C4/r^3 + ...)
# 4th-order Bloch symmetric correction: -1/2 (SQ D2 + D2 SQ) with the sign bookkeeping below.
# PVRVRVRVP = (-c)^4 (-1/(rM))^3 = -C2raw/r^3 ; PVR^2VP = (+c^2)(1/(rM))^2 = SQ/r^2 ;
# PVRVP = -D2/r  ->  -1/2{SQ/r^2, -D2/r} = + (SQ D2 + D2 SQ)/(2 r^3)  (D2 diagonal here)
C4 = [[C2raw[k][l] - (SQ[k][l] * D2[l] + D2[k] * SQ[k][l]) / 2 for l in range(8)] for k in range(8)]

lab = d['lab']
print('PERT_INPUT|cache_sha256=%s|json=0' % cache_sha)
print('PERT_D2|' + '|'.join('f%d=%s' % (k, D2[k]) for k in range(8)) + '|all_equal=%d|json=0' % int(len(set(D2)) == 1))
for k in range(8):
    print('PERT_C1_ROW|k=%d|row=%s|json=0' % (k, ','.join(str(x) for x in C1[k])))
GPT6 = [[Fr(0)] * 8 for _ in range(8)]
GPT6[0][1] = Fr(9, 2); GPT6[1][0] = Fr(3, 2); GPT6[1][2] = Fr(3); GPT6[2][1] = Fr(9, 2)
GPT6[3][4] = Fr(3, 2); GPT6[4][3] = Fr(3, 2)
print('PERT_C1_VS_GPT6|equal=%d|weighted_symmetric=%d|tag=MEASURED|json=0' % (
    int(C1 == GPT6), int(all(w[k] * C1[k][l] == w[l] * C1[l][k] for k in range(8) for l in range(8)))))
offdiag4 = [(k, l, C4[k][l]) for k in range(8) for l in range(8) if k != l and C4[k][l] != 0]
print('PERT_C4_DIAG|' + '|'.join('f%d=%s' % (k, C4[k][k]) for k in range(8)) + '|all_equal=%d|json=0' % int(len(set(C4[k][k] for k in range(8))) == 1))
for k in range(8):
    print('PERT_C4_ROW|k=%d|row=%s|json=0' % (k, ','.join(str(x) for x in C4[k])))
print('PERT_C4_WSYM|weighted_symmetric=%d|nonzero_offdiag=%d|json=0' % (
    int(all(w[k] * C4[k][l] == w[l] * C4[l][k] for k in range(8) for l in range(8))), len(offdiag4)))

# ---- first-order (1/r) eigenvector perturbation of K0 = -C1 by K1 = -C4offdiag / r ----
def wdot(a, b):
    return sum(w[k] * a[k] * b[k] for k in range(8))

def matvec(M, v):
    return [sum(M[k][l] * v[l] for l in range(8)) for k in range(8)]

# exact C1 eigenvectors (function coordinates) -- verified below
vecs = {
    'g': (Fr(9, 2), [1, 1, 1, 0, 0, 0, 0, 0]),
    'z012': (Fr(0), [2, 0, -1, 0, 0, 0, 0, 0]),
    'm012': (Fr(-9, 2), [1, -1, 1, 0, 0, 0, 0, 0]),
    'e': (Fr(3, 2), [0, 0, 0, 1, 1, 0, 0, 0]),
    'm34': (Fr(-3, 2), [0, 0, 0, 1, -1, 0, 0, 0]),
    'f5': (Fr(0), [0, 0, 0, 0, 0, 1, 0, 0]),
    'f6p7': (Fr(0), [0, 0, 0, 0, 0, 0, 1, 1]),
    'f6m7': (Fr(0), [0, 0, 0, 0, 0, 0, 1, -1]),
}
for name, (lam, v) in vecs.items():
    v = [Fr(x) for x in v]
    assert matvec(C1, v) == [lam * x for x in v], name
names = list(vecs)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        assert wdot(vecs[names[i]][1], vecs[names[j]][1]) == 0
K1 = [[-(C4[k][l] - (C4[0][0] if k == l else 0)) for l in range(8)] for k in range(8)]  # times 1/r ; scalar part removed


def first_order(target):
    lam_t, vt = vecs[target]
    Et = -lam_t
    Kv = matvec(K1, [Fr(x) for x in vt])
    corr = [Fr(0)] * 8
    for name, (lam, v) in vecs.items():
        if name == target:
            continue
        En = -lam
        coef = wdot(v, Kv) / wdot(v, v) / (Et - En)
        corr = [corr[k] + coef * v[k] for k in range(8)]
    return [Fr(x) for x in vt], corr

g0, g1 = first_order('g')
e0, e1 = first_order('e')
Ov = lambda v: [O[k] * v[k] for k in range(8)]
A0 = wdot(e0, Ov(g0))
A1 = wdot(e0, Ov(g1)) + wdot(e1, Ov(g0))
N0 = wdot(g0, g0) * wdot(e0, e0)
# amplitude ~ kappa / r with kappa = A1/sqrt(N0)
kappa2 = A1 * A1 / N0
r = 9
amp2_r9 = kappa2 / (r * r)
print('PERT_AMP|A0=%s|A1_coef_of_1_over_r=%s|norm0=%s|kappa2=%s|kappa2_dec=%s|amp2_at_r9=%s|amp2_r9_dec=%s|tag=LEADING_ORDER_1_over_r|json=0' % (
    A0, A1, N0, kappa2, dec(kappa2), amp2_r9, dec(amp2_r9)))
# leading-order (r -> infinity) split of the connected O_sum variance in the ground mode g
gg = wdot(g0, g0)
meanO = wdot(g0, Ov(g0)) / gg
varO = wdot(g0, Ov(Ov(g0))) / gg - meanO ** 2
split = []
for name, (lam, v) in vecs.items():
    if name == 'g':
        continue
    a2 = wdot(v, Ov(g0)) ** 2 / (wdot(v, v) * gg)
    split.append('%s:%s' % (name, a2))
print('PERT_VAR_SPLIT|mean_O_g=%s|var_O_g=%s|amp2_by_mode=%s|tag=LEADING_ORDER_r_infinity|json=0' % (
    meanO, varO, ','.join(split)))
# eigenvalue prediction through 1/r^3 (scalar 4th-order diagonal included)
for t in ('g', 'e', 'f6m7'):
    lam, v = vecs[t]
    E = 72 - D2[0] / r - lam / r ** 2 - C4[0][0] / r ** 3
    print('PERT_LEVEL|mode=%s|C1_eig=%s|E_through_1_over_r3_at_r9=%s|dec=%s|note=first_order_K1_shift_zero_if_offdiag|json=0' % (t, lam, E, dec(E, 9)))
