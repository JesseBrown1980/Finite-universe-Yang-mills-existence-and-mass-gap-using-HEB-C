#!/usr/bin/env python3
# d2-feshbach-r9: #136 one-sided sandwich per reflection sector with the trial resolvent on K3
# (8 flats + 264 + 7770 + 147344 orbits) and the residual Gram over K3 Q-rows AND every shell-4
# target (exact weights). Lower witness L8 = 6 gamma_num U8 - 10^6 G8 (gamma_num = b*94070673 - a*10^6):
#   neg(L_sector(z)) >= #sector levels below z   (CONDITIONAL on the #131 Perron floor)
#   neg(U_sector(z)) <= #sector levels below z   (unconditional min-max)
# Point tests at given z, then bisection for the E1_odd and E3_even lower bounds. Integer only. json=0.
import sys, time
from fractions import Fraction as Fr
sys.path.insert(0, '/mnt/c/tmp/opus55/ym137-fable5-20261109/d2-feshbach-r9')
import fe_k3 as K
fm = K.fm
c = K.c
PS = 10 ** 6
CROSS = False


def main(steps, SCALE_EXP, B_EXP, ztests, out, nbis):
    fh = open(out, 'w')
    t0 = time.time()
    S = K.setup()
    k3, n2, nE, N, wQ, off, D, C = S['k3'], S['n2'], S['nE'], S['N'], S['wQ'], S['off'], S['D'], S['C']
    w = fm.d['w']
    floor_num = fm.d['floor_num']
    SCALE = 10 ** SCALE_EXP
    b = 10 ** B_EXP
    s4w = k3['s4_weight']
    maxC = max(max(r) for r in C)
    maxrow = max(sum(cc for _, cc in r) for r in off)
    fm.emit(fh, 'K3L_BEGIN', steps=steps, SCALE='10^%d' % SCALE_EXP, z_den='10^%d' % B_EXP, q_states=N,
            shell4_targets=len(s4w), k3_cache_sha256=S['k3sha'], perron_floor_num=floor_num,
            source=fm.d['src'], tag='SANDWICH_AT_K3')

    def forms(a):
        dmin = min(b * x - a for x in D)
        assert dmin > 0
        Yb = 0; need = 0
        for _ in range(steps + 1):
            fieldmax = SCALE * maxC + maxrow * Yb
            need = max(need, fieldmax.bit_length())
            Yb = (b * fieldmax) // dmin + 1
        WD = max(128, 32 * ((need + 2 + 31) // 32))
        MASK = (1 << WD) - 1
        SH = [WD * k for k in range(8)]
        den = [b * x - a for x in D]
        SC = [SCALE * sum(C[i][k] << SH[k] for k in range(8)) for i in range(N)]
        P = [0] * N
        for _ in range(steps):
            NP = [0] * N
            for i in range(N):
                v = SC[i]
                for j, cc in off[i]:
                    v += cc * P[j]
                di = den[i]
                p = 0
                for k in range(8):
                    p |= ((b * ((v >> SH[k]) & MASK)) // di) << SH[k]
                NP[i] = p
            P = NP
        Y = [[(p >> SH[k]) & MASK for k in range(8)] for p in P]
        U = [[0] * 8 for _ in range(8)]
        G = [[0] * 8 for _ in range(8)]
        sb = SCALE * b
        for i in range(N):
            T = 0
            for j, cc in off[i]:
                T += cc * P[j]
            y = Y[i]; ci = C[i]; wi = wQ[i]
            ay = [den[i] * y[k] - b * ((T >> SH[k]) & MASK) for k in range(8)]
            r = [sb * ci[k] - ay[k] for k in range(8)]
            for p in range(8):
                yp = wi * y[p]; cp = wi * ci[p]; rp = 6 * wi * r[p]
                if yp == 0 and cp == 0 and rp == 0:
                    continue
                Ur = U[p]; Gr = G[p]
                for q in range(8):
                    Ur[q] += yp * ay[q] - sb * (cp * y[q] + yp * ci[q])
                    Gr[q] += rp * r[q]
        for k in range(8):
            U[k][k] += SCALE * SCALE * w[k] * (b * 72 - a)
        # shell-4 residual: S_f = sum_e (w_e c_ef) Y_e (nonneg, packed per target)
        W4 = WD + 16
        M4 = (1 << W4) - 1
        agg = {}
        for t in range(nE):
            ye = Y[n2 + t]
            if not any(ye):
                continue
            pe = wQ[n2 + t] * sum(ye[k] << (W4 * k) for k in range(8))
            for cd, cc in zip(k3['s4_idx'][t], k3['s4_cnt'][t]):
                agg[cd] = agg.get(cd, 0) + cc * pe
        bound = 6 * 72 * max(max(y) for y in Y[n2:])  # S_f <= W_f * sum_e c_fe * Ymax <= 6*72*Ymax
        assert bound < (1 << W4), 'shell4_packing_guard'
        for cd, pk in agg.items():
            f = 6 // s4w[cd]
            sv = [b * ((pk >> (W4 * k)) & M4) for k in range(8)]
            for p in range(8):
                if sv[p]:
                    fp = f * sv[p]
                    Gr = G[p]
                    for q in range(8):
                        Gr[q] += fp * sv[q]
        del agg
        assert all(U[p][q] == U[q][p] and G[p][q] == G[q][p] for p in range(8) for q in range(8))
        gam = b * floor_num - a * PS
        assert gam > 0
        L = [[6 * gam * U[i][j] - PS * G[i][j] for j in range(8)] for i in range(8)]
        Le = fm.congr(L, fm.EB); Ue = fm.congr(U, fm.EB)
        Lo = sum(fm.OB[x] * L[x][y] * fm.OB[y] for x in range(8) for y in range(8))
        Uo = sum(fm.OB[x] * U[x][y] * fm.OB[y] for x in range(8) for y in range(8))
        assert all(sum(fm.EB[x][p] * L[x][y] * fm.OB[y] for x in range(8) for y in range(8)) == 0 for p in range(7))
        res = dict(Le=fm.inertia(Le), Ue=fm.inertia(Ue), Lo=int(Lo < 0), Uo=int(Uo < 0))
        if CROSS:
            # exact cross-check: v^T G8 v == direct 6*sum w (Q(bH-a)Psi)^2 over K3 Q-rows + shell 4
            v8 = [1, 2, 3, 4, 5, 6, 7, 8]
            Pf = [SCALE * x for x in v8]
            Pq = [sum(Y[i][k] * v8[k] for k in range(8)) for i in range(N)]
            dq = 0
            for i in range(N):
                t = 0
                for j, cc in off[i]:
                    t += cc * Pq[j]
                for k in range(8):
                    if C[i][k]:
                        t += C[i][k] * Pf[k]
                dq += 6 * wQ[i] * ((b * D[i] - a) * Pq[i] - b * t) ** 2
            ag = {}
            for t in range(nE):
                p = Pq[n2 + t]
                if p:
                    wp = wQ[n2 + t] * p
                    for cd, cc in zip(k3['s4_idx'][t], k3['s4_cnt'][t]):
                        ag[cd] = ag.get(cd, 0) + cc * wp
            d4 = sum((6 // s4w[cd]) * (b * S_) ** 2 for cd, S_ in ag.items())
            del ag
            vGv = sum(v8[p] * G[p][q] * v8[q] for p in range(8) for q in range(8))
            fm.emit(fh, 'K3L_CROSSCHECK', z='%d/%d' % (a, b), v8='1..8', vGv_equals_direct=int(vGv == dq + d4),
                    shell4_share=fm.dec(Fr(d4, dq + d4), 9), tag='MEASURED')
            assert vGv == dq + d4, 'gram_crosscheck'
        fm.emit(fh, 'K3L_EVAL', z='%d/%d' % (a, b), z_dec=fm.dec(Fr(a, b), 7), even_lower_count=res['Le'],
                even_upper_count=res['Ue'], odd_lower_count=res['Lo'], odd_upper_count=res['Uo'],
                sec=int(time.time() - t0))
        return res

    cache = {}

    def ev(a):
        if a not in cache:
            cache[a] = forms(a)
        return cache[a]
    for z in ztests:
        num, den_ = z.split('/')
        a = int(num) * b // int(den_)
        r = ev(a)
        fm.emit(fh, 'K3L_TEST', z=z, odd_level_below_z_possible=r['Lo'],
                even_levels_below_z_at_most=r['Le'], even_levels_below_z_at_least=r['Ue'],
                tag='CONDITIONAL_ON_PERRON_FLOOR_FOR_LOWER')
    # bisection for lower bounds: E1_odd (Lo crosses 0->1) and E3_even (Le reaches 3)
    for key, k, name in (('Lo', 1, 'E1_odd'), ('Le', 3, 'E3_even')):
        lo = int(ztests[0].split('/')[0]) * b // int(ztests[0].split('/')[1])
        hi = 69990 * b // 1000
        if ev(lo)[key] >= k:
            fm.emit(fh, 'K3L_BOUND', level=name, bound='below_first_test_point'); continue
        if ev(hi)[key] < k:
            fm.emit(fh, 'K3L_BOUND', level=name, bound='>=69.99'); continue
        for _ in range(nbis):
            mid = (lo + hi) // 2
            if ev(mid)[key] >= k:
                hi = mid
            else:
                lo = mid
        fm.emit(fh, 'K3L_BOUND', level=name, lower_bound='%d/%d' % (lo, b), lower_bound_dec=fm.dec(Fr(lo, b), 7),
                bracket_hi='%d/%d' % (hi, b), meaning='certified_lower_bound_CONDITIONAL_on_Perron_floor')
    fm.emit(fh, 'K3L_END', evaluations=len(cache), seconds=int(time.time() - t0))


if __name__ == '__main__':
    CROSS = len(sys.argv) > 7 and sys.argv[7] == 'cross'
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4].split(','), sys.argv[5], int(sys.argv[6]))
