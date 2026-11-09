#!/usr/bin/env python3
# Odd-sector lower bound with a deeper trial: the #136 Schur sandwich restricted to the reflection-odd
# flat vector w = flat6 - flat7, with a trial resolvent supported on every orbit within RADIUS moves of
# flats 6 and 7 (exterior = one further move). Same identities and Perron floor as checker136.threshold:
#   6*gamma_num*L^2*w'S(z)w >= 6*gamma_num*U_w - 10^6*G_w ;  U_w >= L^2*w'S(z)w.
# U_w > ... : LOWER_w > 0  =>  no odd level below z ;  U_w < 0  =>  an odd level below z. Integer only. json=0.
import sys
ARGS = sys.argv[1:]
sys.argv = ['checker136.py']
sys.path.insert(0, '/mnt/c/tmp/opus55/ym137-fable5-20261109/independent')
import checker136 as c

RADIUS = int(ARGS[0]); STEPS = int(ARGS[1]); GRID = [int(a) for a in ARGS[2].split(',')]; BDEN = int(ARGS[3])
SCALE = c.SCALE; PS = c.PERRON_SCALE

def flats():
    flat = {}
    for a in range(6):
        for b in range(6):
            if c.MUL[a][b] != c.MUL[b][a]: continue
            U = [0] * (2 * c.V)
            for y in range(c.LY): U[c.pos(c.LX - 1, y)] = a
            for x in range(c.LX): U[c.V + c.pos(x, c.LY - 1)] = b
            flat.setdefault(c.canonical(U), (a, b))
    return sorted(flat)

src, floor_num = c.source_floor()
F8 = flats(); assert len(F8) == 8
FLATSET = set(F8)
f6, f7 = F8[6], F8[7]
assert c.weight(f6) == c.weight(f7) == 2
# ball of radius RADIUS around flats 6,7 inside Q (flats excluded from Q)
layers = [[f6, f7]]; seen = {f6, f7}
for d in range(RADIUS):
    new = set()
    for k in layers[-1]: new.update(c.neighbors(k))
    new -= seen; new -= FLATSET; seen |= new
    layers.append(sorted(new))
    print('BALL_LAYER|d=%d|states=%d|json=0' % (d + 1, len(new)), flush=True)
Q = [k for L in layers[1:] for k in L]; where = {k: i for i, k in enumerate(Q)}
n = len(Q)
w = [c.weight(k) for k in Q]; m = [c.magnetic(c.from_key(k)) for k in Q]
adj = []; tof = []; ext = {}
for i, k in enumerate(Q):
    nb = c.neighbors(k)
    row = []; t6 = t7 = 0; flat_other = 0
    for dst, cnt in nb.items():
        if dst in FLATSET:
            if dst == f6: t6 += cnt
            elif dst == f7: t7 += cnt
            else: flat_other += cnt
            continue
        j = where.get(dst)
        if j is None:
            ext.setdefault(dst, []).append((i, w[i] * cnt))
        else:
            row.append((j, cnt))
    adj.append(row); tof.append((t6, t7))
    if i % 20000 == 0: print('BUILD|i=%d|of=%d|ext=%d|json=0' % (i, n, len(ext)), flush=True)
# weighted adjointness inside the ball and P-Q detailed balance for flats 6,7
for i, row in enumerate(adj):
    d = dict(row)
    for j, cnt in row:
        assert w[i] * cnt == w[j] * dict(adj[j]).get(i, 0), 'QQ_adjoint'
nb6 = c.neighbors(f6); nb7 = c.neighbors(f7)
for i, k in enumerate(Q):
    assert w[i] * tof[i][0] == 2 * nb6.get(k, 0) and w[i] * tof[i][1] == 2 * nb7.get(k, 0), 'PQ_adjoint'
outer = [(c.weight(k), e) for k, e in ext.items()]
print('BALL|radius=%d|Q_states=%d|exterior=%d|json=0' % (RADIUS, n, len(outer)), flush=True)

def det(A): return c.det(A)

for a in GRID:
    b = BDEN
    diag = [b * (72 + 9 * m[i] - dict(adj[i]).get(i, 0)) - a for i in range(n)]
    assert min(diag) > 0
    off = [[(j, cc) for j, cc in row if j != i] for i, row in enumerate(adj)]
    # f = F w : F[i][k] = -b * count(Q_i -> flat k) ; w = e6 - e7
    f = [-b * (t6 - t7) for (t6, t7) in tof]
    x = [0] * n
    for _ in range(STEPS):
        y = []
        for i in range(n):
            s = SCALE * f[i]
            for j, cc in off[i]: s += b * cc * x[j]
            y.append(s // diag[i])
        x = y
    r = []
    for i in range(n):
        s = SCALE * f[i] - diag[i] * x[i]
        for j, cc in off[i]: s += b * cc * x[j]
        r.append(w[i] * s)
    G = 0
    for i in range(n):
        assert 6 % w[i] == 0
        G += (6 // w[i]) * r[i] * r[i]
    for W, edges in outer:
        R = 0
        for i, cc in edges: R += b * cc * x[i]
        G += (6 // W) * R * R
    # U_w = L^2 w'Cw - L f'Wx - x'r ; w'Cw = (w6+w7)(b*72 - a) = 4(b*72 - a)
    U = SCALE * SCALE * 4 * (b * 72 - a)
    for i in range(n):
        U -= SCALE * w[i] * f[i] * x[i] + x[i] * r[i]
    gamma_num = b * floor_num - a * PS
    assert gamma_num > 0
    LOW = 6 * gamma_num * U - PS * G
    print('ODD_BALL|radius=%d|steps=%d|z=%d/%d|U_sign=%d|LOWER_sign=%d|odd_levels_below_z=%s|json=0' % (
        RADIUS, STEPS, a, b, (U > 0) - (U < 0), (LOW > 0) - (LOW < 0),
        '0' if LOW > 0 else ('>=1' if U < 0 else 'UNRESOLVED')), flush=True)
