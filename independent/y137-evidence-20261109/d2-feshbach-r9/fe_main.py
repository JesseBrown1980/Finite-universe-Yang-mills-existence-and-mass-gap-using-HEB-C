#!/usr/bin/env python3
# d2-feshbach-r9: Wilson-sum transition ESTIMATE, ground -> reflection-even second level, r=9,
# with #136's own Feshbach machinery on K2 (8 flats + 264 shell-1 + 7770 shell-2 orbits).
# Integer / exact-rational only. No float anywhere. json=0.
#
# Conventions (checker136 threshold(), sign-flipped Q block):
#   z = a/b.  D_i = 72 + 9 m_i - c_ii on Q-states of K2, den_i = b D_i - a.
#   C_ik = number of electric moves from Q-state i into flat k (checker q_flat).
#   Y ~= SCALE (Q(H-z)Q)^-1 C  (n x 8, Y = -X of the checker; Q block truncated to K2).
#   Integer Jacobi from Y=0:  Y_ik <- floor( b (SCALE C_ik + sum_{j!=i} c_ij Y_jk) / den_i ).
#   Trial vectors psi(v) = v on flats + (Y v)/SCALE on Q-states of K2, 0 outside K2.
#   U8 = SCALE^2 b <psi, (H - z) psi>_W as an exact integer 8x8 form (checker's "upper" witness);
#   even sector Ue = E^T U8 E (E = flats 0..5, flat6+flat7), odd Uo = O^T U8 O (flat6-flat7).
#   Approximate Schur complement on the even sector := Ue(z) (variational / Galerkin form).
import sys, time, hashlib
from fractions import Fraction as Fr
from math import isqrt
sys.path.insert(0, '/mnt/c/tmp/opus55/ym137-fable5-20261109/d2-feshbach-r9')
import fe_common as fc
c = fc.c

d, CACHE_SHA, _ = fc.load()
w, m, adj, qflat, outer, O, flat_out = (d['w'], d['m'], d['adj'], d['qflat'], d['outer'],
                                        d['O'], d['flat_out'])
n = len(adj)
wq = w[8:]
Oq = O[8:]
selfc = [dict(adj[i]).get(i, 0) for i in range(n)]
off = [[(j, cc) for j, cc in adj[i] if j != i] for i in range(n)]
D = [72 + 9 * m[8 + i] - selfc[i] for i in range(n)]
C = qflat
maxC = max(max(r) for r in C)
maxrow = max(sum(cc for _, cc in r) for r in off)
WD = 128
MASK = (1 << WD) - 1
SH = [WD * k for k in range(8)]


def set_width(steps, SCALE, b, a_max):
    """choose the packing field width from the a-priori monotone bound
    Yb_{s+1} = b (SCALE maxC + maxrow Yb_s)/dmin + 1 over every z <= a_max/b (exact ints)."""
    global WD, MASK, SH
    dmin = min(b * Dq - a_max for Dq in D)
    assert dmin > 0
    Yb = 0; need = 0
    for _ in range(steps + 1):
        fieldmax = SCALE * maxC + maxrow * Yb
        need = max(need, fieldmax.bit_length())
        Yb = (b * fieldmax) // dmin + 1
    WD = max(128, 32 * ((need + 2 + 31) // 32))
    MASK = (1 << WD) - 1
    SH = [WD * k for k in range(8)]
    return WD


EB = [[0] * 7 for _ in range(8)]
for k in range(6):
    EB[k][k] = 1
EB[6][6] = 1
EB[7][6] = 1
OB = [0, 0, 0, 0, 0, 0, 1, -1]


def emit(fh, label, **kv):
    s = label + '|' + '|'.join('%s=%s' % (k, v) for k, v in kv.items()) + '|json=0'
    print(s, flush=True)
    if fh:
        fh.write(s + '\n')
        fh.flush()


def dec(x, digits=12):
    x = Fr(x)
    s = '-' if x < 0 else ''
    x = abs(x)
    q = (x.numerator * 10 ** digits * 2 + x.denominator) // (2 * x.denominator)
    ip, fp = divmod(q, 10 ** digits)
    return '%s%d.%0*d' % (s, ip, digits, fp)


def sqrt_dec(x, digits=12):
    """decimal string of sqrt(x) for exact nonnegative rational x, truncated (floor)."""
    x = Fr(x)
    assert x >= 0
    v = isqrt(x.numerator * 10 ** (2 * digits) // x.denominator)
    ip, fp = divmod(v, 10 ** digits)
    return '%d.%0*d' % (ip, digits, fp)


def sgn(x):
    return (x > 0) - (x < 0)


# ---------------------------------------------------------------- Jacobi (packed, nonneg)
def jacobi_packed(a, b, steps, SCALE):
    den = [b * D[i] - a for i in range(n)]
    dmin = min(den)
    assert dmin > 0, 'positive_Q_Jacobi_diagonal'
    # a-priori field bound (monotone nonneg iterates): n_k <= SCALE*maxC + maxrow*Yb
    Yb = 0
    for _ in range(steps):
        fieldmax = SCALE * maxC + maxrow * Yb
        assert fieldmax < (1 << WD), 'packing_field_overflow'
        Yb = (b * fieldmax) // dmin + 1
    SC = [SCALE * sum(C[i][k] << SH[k] for k in range(8)) for i in range(n)]
    P = [0] * n
    s0, s1, s2, s3, s4, s5, s6, s7 = SH
    for _ in range(steps):
        NP = [0] * n
        for i in range(n):
            N = SC[i]
            for j, cc in off[i]:
                N += cc * P[j]
            di = den[i]
            NP[i] = (((b * (N & MASK)) // di)
                     | (((b * ((N >> s1) & MASK)) // di) << s1)
                     | (((b * ((N >> s2) & MASK)) // di) << s2)
                     | (((b * ((N >> s3) & MASK)) // di) << s3)
                     | (((b * ((N >> s4) & MASK)) // di) << s4)
                     | (((b * ((N >> s5) & MASK)) // di) << s5)
                     | (((b * ((N >> s6) & MASK)) // di) << s6)
                     | (((b * (N >> s7)) // di) << s7))
        P = NP
    Y = [[(p >> SH[k]) & MASK for k in range(8)] for p in P]
    return Y, P, den


def jacobi_plain_Y(a, b, steps, SCALE):
    """unpacked reference (validation only)"""
    den = [b * D[i] - a for i in range(n)]
    Y = [[0] * 8 for _ in range(n)]
    for _ in range(steps):
        NY = []
        for i in range(n):
            s = [SCALE * C[i][k] for k in range(8)]
            for j, cc in off[i]:
                y = Y[j]
                for k in range(8):
                    s[k] += cc * y[k]
            NY.append([(b * v) // den[i] for v in s])
        Y = NY
    return Y


def jacobi_checker_X(a, b, steps, SCALE):
    """the checker's literal X iteration (F = -b c, floor on negatives), validation only"""
    diag = [b * (72 + 9 * m[8 + i] - selfc[i]) - a for i in range(n)]
    F = [[-b * cc for cc in row] for row in C]
    X = [[0] * 8 for _ in range(n)]
    for _ in range(steps):
        NX = []
        for i in range(n):
            s = [SCALE * F[i][k] for k in range(8)]
            for j, cc in off[i]:
                y = X[j]
                for k in range(8):
                    s[k] += b * cc * y[k]
            NX.append([v // diag[i] for v in s])
        X = NX
    return X


def pack(Y):
    return [sum(y[k] << SH[k] for k in range(8)) for y in Y]


# ---------------------------------------------------------------- 8x8 trial form
def form8(a, b, Y, P, den, SCALE):
    AY = []
    for i in range(n):
        T = 0
        for j, cc in off[i]:
            T += cc * P[j]
        di = den[i]
        y = Y[i]
        AY.append([di * y[k] - b * ((T >> SH[k]) & MASK) for k in range(8)])
    U = [[0] * 8 for _ in range(8)]
    sb = SCALE * b
    for i in range(n):
        wi = wq[i]
        y = Y[i]; ci = C[i]; ay = AY[i]
        for p in range(8):
            yp = wi * y[p]; cp = wi * ci[p]
            row = U[p]
            for q in range(8):
                row[q] += yp * ay[q] - sb * (cp * y[q] + yp * ci[q])
    for k in range(8):
        U[k][k] += SCALE * SCALE * w[k] * (b * 72 - a)
    assert all(U[p][q] == U[q][p] for p in range(8) for q in range(8)), 'exact_symmetric_trial'
    return U, AY


def congr(M, T):
    cols = len(T[0])
    return [[sum(T[x][p] * M[x][y] * T[y][q] for x in range(8) for y in range(8))
             for q in range(cols)] for p in range(cols)]


def inertia(A):
    k = len(A)
    neg = 0; prev = 1
    for t in range(1, k + 1):
        Dt = c.det([row[:t] for row in A[:t]])
        if Dt == 0:
            return None
        neg += int((Dt < 0) != (prev < 0)); prev = Dt
    return neg


def evaluate(a, b, steps, SCALE):
    Y, P, den = jacobi_packed(a, b, steps, SCALE)
    U8, AY = form8(a, b, Y, P, den, SCALE)
    Ue = congr(U8, EB)
    Uo = sum(OB[x] * U8[x][y] * OB[y] for x in range(8) for y in range(8))
    cross = [sum(EB[x][p] * U8[x][y] * OB[y] for x in range(8) for y in range(8)) for p in range(7)]
    assert all(v == 0 for v in cross), 'even_odd_block_diagonal'
    return dict(Y=Y, P=P, den=den, U8=U8, Ue=Ue, Uo=Uo, det=c.det(Ue), neg=inertia(Ue))


# ---------------------------------------------------------------- exact rational helpers
def solve(M, rhs):
    k = len(M)
    A = [[Fr(M[i][j]) for j in range(k)] + [Fr(rhs[i])] for i in range(k)]
    for col in range(k):
        piv = max(range(col, k), key=lambda r: abs(A[r][col]))
        assert A[piv][col] != 0
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        for r in range(k):
            if r != col and A[r][col] != 0:
                f = A[r][col] / pv
                A[r] = [A[r][j] - f * A[col][j] for j in range(k + 1)]
    return [A[i][k] / A[i][i] for i in range(k)]


def null_vector(M, iters=2, top=10 ** 30):
    """exact-rational inverse iteration from the all-ones vector, then rounded to integers
    with max |entry| = 10^30 (round-half-up on exact rationals)."""
    x = [Fr(1)] * len(M)
    for _ in range(iters):
        x = solve(M, x)
        mx = max(abs(v) for v in x)
        x = [v / mx for v in x]
    u = []
    for v in x:
        t = v * top
        u.append((2 * t.numerator + t.denominator) // (2 * t.denominator))
    return u


# ---------------------------------------------------------------- lift, residual, amplitude
def lift(v8, Y, SCALE):
    Pf = [SCALE * v8[k] for k in range(8)]
    Pq = [sum(Y[i][k] * v8[k] for k in range(8)) for i in range(n)]
    return Pf, Pq


def residual6(a, b, Pf, Pq):
    """6 * sum_s w_s ((bH - a) Psi)_s^2 over K2 and every exterior target, exact integer;
    also returns <Psi,(bH-a)Psi>_W."""
    rf = []
    for k in range(8):
        s = (b * 72 - a) * Pf[k] - b * sum(cc * Pq[j] for j, cc in flat_out[k].items())
        rf.append(s)
    rq = []
    for i in range(n):
        s = (b * D[i] - a) * Pq[i]
        t = 0
        for j, cc in off[i]:
            t += cc * Pq[j]
        ci = C[i]
        for k in range(8):
            if ci[k]:
                t += ci[k] * Pf[k]
        rq.append(s - b * t)
    k2 = 6 * (sum(w[k] * rf[k] ** 2 for k in range(8)) + sum(wq[i] * rq[i] ** 2 for i in range(n)))
    ext = 0
    for W, edges in outer:
        S = 0
        for i, wc in edges:
            S += wc * Pq[i]
        if S:
            ext += (6 // W) * (b * S) ** 2
    quad = sum(w[k] * Pf[k] * rf[k] for k in range(8)) + sum(wq[i] * Pq[i] * rq[i] for i in range(n))
    return k2, ext, quad


def wdot(Af, Aq, Bf, Bq, obs=False):
    if obs:
        f = sum(w[k] * O[k] * Af[k] * Bf[k] for k in range(8))
        q = sum(wq[i] * Oq[i] * Aq[i] * Bq[i] for i in range(n))
    else:
        f = sum(w[k] * Af[k] * Bf[k] for k in range(8))
        q = sum(wq[i] * Aq[i] * Bq[i] for i in range(n))
    return f, q


def wdot_O2(Af, Aq):
    f = sum(w[k] * O[k] * O[k] * Af[k] * Af[k] for k in range(8))
    q = sum(wq[i] * Oq[i] * Oq[i] * Aq[i] * Aq[i] for i in range(n))
    return f, q


# ---------------------------------------------------------------- root finding
def illinois(fun, a_lo, a_hi, f_lo, f_hi, maxit=60):
    """sign-change root bracket of an exact integer function (Illinois regula falsi).
    returns (a_lo, a_hi, true f_lo, true f_hi, evaluations)."""
    assert sgn(f_lo) * sgn(f_hi) < 0
    t_lo, t_hi = f_lo, f_hi
    g_lo, g_hi = f_lo, f_hi
    side = 0
    ev = 0
    for _ in range(maxit):
        if a_hi - a_lo <= 1:
            break
        a_new = a_lo + (g_lo * (a_hi - a_lo)) // (g_lo - g_hi)
        a_new = min(max(a_new, a_lo + 1), a_hi - 1)
        f_new = fun(a_new); ev += 1
        if f_new == 0:
            return a_new, a_new, 0, 0, ev
        if sgn(f_new) == sgn(t_lo):
            a_lo, t_lo, g_lo = a_new, f_new, f_new
            if side == -1:
                g_hi = g_hi // 2 if g_hi > 0 else -((-g_hi) // 2)
                if g_hi == 0:
                    g_hi = sgn(t_hi)
            side = -1
        else:
            a_hi, t_hi, g_hi = a_new, f_new, f_new
            if side == 1:
                g_lo = g_lo // 2 if g_lo > 0 else -((-g_lo) // 2)
                if g_lo == 0:
                    g_lo = sgn(t_lo)
            side = 1
    return a_lo, a_hi, t_lo, t_hi, ev


# ---------------------------------------------------------------- modes
def anchor(fh):
    """(1) checker's literal X iteration at a=6992,b=100,SCALE=1e9,4 steps, Y=-X fed to
    form8 must reproduce #136 schur_trial_sha256; (2) packed Y-Jacobi == unpacked Y-Jacobi."""
    t0 = time.time()
    X = jacobi_checker_X(6992, 100, 4, 10 ** 9)
    Y = [[-v for v in row] for row in X]
    assert all(v >= 0 for row in Y for v in row)
    den = [100 * D[i] - 6992 for i in range(n)]
    U8, _ = form8(6992, 100, Y, pack(Y), den, 10 ** 9)
    hu = hashlib.sha256('|'.join(str(z) for row in U8 for z in row).encode()).hexdigest()
    want = 'c0837b71b8185b99d64f01a5f3ea9cb742890b8fa27579c8072d2283d075e43e'
    emit(fh, 'FE_ANCHOR', check='checker136_schur_trial_sha256_at_6992_over_100', got=hu,
         want=want, match=int(hu == want), tag='MEASURED')
    assert hu == want
    a, b, S, SC = 69900, 1000, 6, 10 ** 12
    Yp, _, _ = jacobi_packed(a, b, S, SC)
    Yr = jacobi_plain_Y(a, b, S, SC)
    emit(fh, 'FE_ANCHOR', check='packed_vs_unpacked_Y_jacobi', z='%d/%d' % (a, b), steps=S,
         identical=int(Yp == Yr), seconds=int(time.time() - t0), tag='MEASURED')
    assert Yp == Yr


def run(steps, SCALE_EXP, B_EXP, fh):
    SCALE = 10 ** SCALE_EXP
    b = 10 ** B_EXP
    t0 = time.time()
    wd = set_width(steps, SCALE, b, 69990 * b // 1000)
    emit(fh, 'FE_BEGIN', steps=steps, SCALE='10^%d' % SCALE_EXP, z_den='10^%d' % B_EXP, pack_bits=wd,
         cache_sha256=CACHE_SHA, perron_floor_num=d['floor_num'], source=d['src'],
         basis='even:f0..f5,f6+f7|odd:f6-f7', form='U8=SCALE^2*b*<psi,(H-z)psi>_W',
         tag='ESTIMATE')
    cache = {}

    def ev(a):
        if a not in cache:
            cache[a] = evaluate(a, b, steps, SCALE)
        return cache[a]

    # ---- grid scan
    grid = [69885 + 5 * t for t in range(22)]  # 69.885 .. 69.990
    for z in grid:
        a = z * b // 1000
        r = ev(a)
        emit(fh, 'FE_GRID', steps=steps, z='%d/1000' % z, even_neg=r['neg'],
             even_det_sign=sgn(r['det']), odd_form_sign=sgn(r['Uo']))
    # ---- brackets
    roots = {}
    seq = [(z * b // 1000) for z in grid]
    for want_lo, name in ((0, 'E1_even'), (1, 'E2_even')):
        br = None
        for a0, a1 in zip(seq, seq[1:]):
            if ev(a0)['neg'] == want_lo and ev(a1)['neg'] == want_lo + 1:
                br = (a0, a1); break
        assert br, ('no bracket', name)
        lo, hi, flo, fhi, ne = illinois(lambda a: ev(a)['det'], br[0], br[1], ev(br[0])['det'], ev(br[1])['det'])
        cnt_lo, cnt_hi = ev(lo)['neg'], ev(hi)['neg']
        roots[name] = (lo, hi, flo, fhi, cnt_lo, cnt_hi, ne)
    br = None
    for a0, a1 in zip(seq, seq[1:]):
        if ev(a0)['Uo'] > 0 and ev(a1)['Uo'] < 0:
            br = (a0, a1); break
    assert br, 'no odd bracket'
    lo, hi, flo, fhi, ne = illinois(lambda a: ev(a)['Uo'], br[0], br[1], ev(br[0])['Uo'], ev(br[1])['Uo'])
    roots['E_odd'] = (lo, hi, flo, fhi, int(ev(lo)['Uo'] < 0), int(ev(hi)['Uo'] < 0), ne)

    # ---- null vectors + lifts
    psi = {}
    for name in ('E1_even', 'E2_even', 'E_odd'):
        lo, hi, flo, fhi, cl, ch, ne = roots[name]
        a_end = lo if abs(flo) <= abs(fhi) else hi
        r = ev(a_end)
        if name == 'E_odd':
            u7 = None
            v8 = list(OB)
            nullrel = 'n/a_1x1'
        else:
            u7 = null_vector(r['Ue'])
            v8 = [sum(EB[k][p] * u7[p] for p in range(7)) for k in range(8)]
            Uu = [sum(r['Ue'][p][q] * u7[q] for q in range(7)) for p in range(7)]
            mxU = max(abs(x) for row in r['Ue'] for x in row)
            nullrel = dec(Fr(max(abs(x) for x in Uu), mxU * max(abs(x) for x in u7)), 15)
        Pf, Pq = lift(v8, r['Y'], SCALE)
        k2, ext, quad = residual6(a_end, b, Pf, Pq)
        nf, nq = wdot(Pf, Pq, Pf, Pq)
        nrm = nf + nq
        z = Fr(a_end, b)
        rho = z + Fr(quad, b * nrm)
        rz2 = Fr(k2 + ext, 6 * b * b * nrm)            # ||(H-z)psi||^2/||psi||^2
        rr2 = rz2 - (rho - z) ** 2                      # ||(H-rho)psi||^2/||psi||^2
        psi[name] = dict(Pf=Pf, Pq=Pq, nrm=nrm, nf=nf, nq=nq, z=z, rho=rho, rz2=rz2, rr2=rr2,
                         ext=Fr(ext, k2 + ext), u7=u7, v8=v8)
        emit(fh, 'FE_LEVEL', steps=steps, which=name, z_lo='%d/%d' % (lo, b), z_hi='%d/%d' % (hi, b),
             z_used=dec(z, 9), count_lo=cl, count_hi=ch, illinois_evals=ne,
             rayleigh=dec(rho, 12), rho_minus_z=dec(rho - z, 15),
             rel_res2_at_z=dec(rz2, 15), rel_res2_at_rho=dec(rr2, 15),
             rel_res_at_rho=sqrt_dec(max(rr2, Fr(0)), 12), exterior_share_of_res2=dec(psi[name]['ext'], 9),
             flat_norm_share=dec(Fr(nf, nrm), 12), null_rel=nullrel,
             v8=','.join(str(x) for x in v8) if name == 'E_odd' else 'u7_max_1e30', tag='ESTIMATE')
    # ---- amplitudes
    p1, p2, po = psi['E1_even'], psi['E2_even'], psi['E_odd']
    # phase: Perron ground positive on flat 0; second level positive on flat 3
    s1 = sgn(p1['Pf'][0]); s2 = sgn(p2['Pf'][3])
    Af, Aq = wdot(p2['Pf'], p2['Pq'], p1['Pf'], p1['Pq'], obs=True)
    Af *= s1 * s2; Aq *= s1 * s2
    A = Af + Aq
    Gf, Gq = wdot(p2['Pf'], p2['Pq'], p1['Pf'], p1['Pq'])
    G = (Gf + Gq) * s1 * s2
    N12 = p1['nrm'] * p2['nrm']
    amp2 = Fr(A * A, N12)
    ov2 = Fr(G * G, N12)
    O1f, O1q = wdot(p1['Pf'], p1['Pq'], p1['Pf'], p1['Pq'], obs=True)
    mean1 = Fr(O1f + O1q, p1['nrm'])
    Q1f, Q1q = wdot_O2(p1['Pf'], p1['Pq'])
    var1 = Fr(Q1f + Q1q, p1['nrm']) - mean1 ** 2
    # amplitude after W-orthogonalising psi2 against psi1 (shift O by <O>_1)
    Aorth = Fr(A) - Fr(G) * mean1
    n2orth = Fr(p2['nrm']) - Fr(G * G, p1['nrm'])
    amp2_orth = Aorth * Aorth / (p1['nrm'] * n2orth)
    Aodd_f, Aodd_q = wdot(po['Pf'], po['Pq'], p1['Pf'], p1['Pq'], obs=True)
    emit(fh, 'FE_AMP', steps=steps, amp=('-' if A < 0 else '') + sqrt_dec(amp2, 12), amp2=dec(amp2, 15),
         amp_orth=('-' if Aorth < 0 else '') + sqrt_dec(amp2_orth, 12), amp2_orth=dec(amp2_orth, 15),
         flat_share=dec(Fr(Af, A), 9) if A else 'undef', q_share=dec(Fr(Aq, A), 9) if A else 'undef',
         overlap_psi1_psi2=('-' if G < 0 else '') + sqrt_dec(ov2, 12),
         residual='res1=%s,res2=%s' % (sqrt_dec(max(p1['rr2'], Fr(0)), 12), sqrt_dec(max(p2['rr2'], Fr(0)), 12)),
         first_state_weight_over_var=dec(amp2 / var1, 12), var1=dec(var1, 12), mean1=dec(mean1, 12),
         odd_amp_numerator=Aodd_f + Aodd_q, tag='ESTIMATE')
    emit(fh, 'FE_AMP_EXACT', steps=steps,
         A_num='%d' % A, A_flat_num='%d' % Af, A_q_num='%d' % Aq, norm1_num=p1['nrm'], norm2_num=p2['nrm'],
         common_den='SCALE^2*u_scale^2 cancels in amp', amp2_exact='%d/%d' % (amp2.numerator, amp2.denominator),
         sha256_amp2=hashlib.sha256(('%d/%d' % (amp2.numerator, amp2.denominator)).encode()).hexdigest(),
         tag='MEASURED_ARITHMETIC_OF_ESTIMATE')
    emit(fh, 'FE_NORMS', steps=steps, norm1_flat_share=dec(Fr(p1['nf'], p1['nrm']), 12),
         norm2_flat_share=dec(Fr(p2['nf'], p2['nrm']), 12),
         u1=','.join(str(x) for x in p1['u7']), u2=','.join(str(x) for x in p2['u7']))
    emit(fh, 'FE_END', steps=steps, evaluations=len(cache), seconds=int(time.time() - t0))


if __name__ == '__main__':
    mode = sys.argv[1]
    out = sys.argv[2]
    with open(out, 'w') as fh:
        if mode == 'anchor':
            anchor(fh)
        else:
            run(int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), fh)
