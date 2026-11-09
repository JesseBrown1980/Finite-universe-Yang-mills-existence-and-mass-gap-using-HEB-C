#!/usr/bin/env python3
# d2-feshbach-r9: K2 limit of #136's one-sided sandwich per reflection sector (converged Jacobi).
# Lower witness (checker): L8 = 6 gamma_num U8 - PERRON_SCALE G8, gamma_num = b*94070673 - a*10^6,
# G8 = 6 * sum_s w_s r_s r_s^T over K2 Q-states AND all 147344 exterior targets.
# neg(L_sector(z)) >= #sector levels below z  (CONDITIONAL on #131 Perron floor);
# neg(U_sector(z)) <= #sector levels below z  (unconditional min-max on exact trial vectors).
# Bisection on integer a at denominator b; reports the crossing brackets. Integer only. json=0.
import sys, time
sys.path.insert(0, '/mnt/c/tmp/opus55/ym137-fable5-20261109/d2-feshbach-r9')
import fe_main as fm

PS = 10 ** 6


def gram8(a, b, Y, AY, SCALE):
    G = [[0] * 8 for _ in range(8)]
    sb = SCALE * b
    for i in range(fm.n):
        wi = fm.wq[i]
        r = [sb * fm.C[i][k] - AY[i][k] for k in range(8)]
        for p in range(8):
            rp = 6 * wi * r[p]
            if rp:
                row = G[p]
                for q in range(8):
                    row[q] += rp * r[q]
    for W, edges in fm.outer:
        R = [0] * 8
        for i, wc in edges:
            y = Y[i]
            for k in range(8):
                R[k] += b * wc * y[k]
        f = 6 // W
        for p in range(8):
            rp = f * R[p]
            if rp:
                row = G[p]
                for q in range(8):
                    row[q] += rp * R[q]
    return G


def sector_forms(a, b, steps, SCALE, floor_num):
    Y, P, den = fm.jacobi_packed(a, b, steps, SCALE)
    U8, AY = fm.form8(a, b, Y, P, den, SCALE)
    G8 = gram8(a, b, Y, AY, SCALE)
    gam = b * floor_num - a * PS
    assert gam > 0
    L8 = [[6 * gam * U8[i][j] - PS * G8[i][j] for j in range(8)] for i in range(8)]
    Le = fm.congr(L8, fm.EB)
    Lo = sum(fm.OB[x] * L8[x][y] * fm.OB[y] for x in range(8) for y in range(8))
    Ue = fm.congr(U8, fm.EB)
    Uo = sum(fm.OB[x] * U8[x][y] * fm.OB[y] for x in range(8) for y in range(8))
    return dict(Le=fm.inertia(Le), Lo=int(Lo < 0), Ue=fm.inertia(Ue), Uo=int(Uo < 0))


def main(steps, SCALE_EXP, B_EXP, out):
    SCALE = 10 ** SCALE_EXP
    b = 10 ** B_EXP
    floor_num = fm.d['floor_num']
    fm.set_width(steps, SCALE, b, 69990 * b // 1000)
    fh = open(out, 'w')
    t0 = time.time()
    fm.emit(fh, 'FL_BEGIN', steps=steps, SCALE='10^%d' % SCALE_EXP, z_den='10^%d' % B_EXP,
            perron_floor_num=floor_num, source=fm.d['src'], tag='SANDWICH_LIMIT_AT_K2')
    cache = {}

    def ev(a):
        if a not in cache:
            cache[a] = sector_forms(a, b, steps, SCALE, floor_num)
        return cache[a]
    grid = [69880 + 5 * t for t in range(23)]
    for z in grid:
        r = ev(z * b // 1000)
        fm.emit(fh, 'FL_GRID', steps=steps, z='%d/1000' % z, even_lower_count=r['Le'],
                even_upper_count=r['Ue'], odd_lower_count=r['Lo'], odd_upper_count=r['Uo'])

    def cross(key, k):
        """smallest grid bracket where count(key) goes from <k to >=k, then bisect"""
        seq = [z * b // 1000 for z in grid]
        lo = hi = None
        for a0, a1 in zip(seq, seq[1:]):
            if ev(a0)[key] is not None and ev(a1)[key] is not None and ev(a0)[key] < k <= ev(a1)[key]:
                lo, hi = a0, a1
                break
        if lo is None:
            return None
        while hi - lo > 1:
            mid = (lo + hi) // 2
            cm = ev(mid)[key]
            if cm is None:
                mid += 1; cm = ev(mid)[key]
            if cm >= k:
                hi = mid
            else:
                lo = mid
        return lo, hi
    meaning = {'Le': 'certified_lower_bound_CONDITIONAL', 'Lo': 'certified_lower_bound_CONDITIONAL',
               'Ue': 'rigorous_upper_bound_UNCONDITIONAL', 'Uo': 'rigorous_upper_bound_UNCONDITIONAL'}
    for key, k, name in (('Le', 1, 'E1_even'), ('Ue', 1, 'E1_even'), ('Le', 2, 'E2_even'), ('Ue', 2, 'E2_even'),
                         ('Le', 3, 'E3_even'), ('Lo', 1, 'E1_odd'), ('Uo', 1, 'E1_odd')):
        br = cross(key, k)
        if br is None:
            fm.emit(fh, 'FL_BOUND', steps=steps, level=name, form=key, bracket='not_in_grid')
            continue
        lo, hi = br
        val = lo if key in ('Le', 'Lo') else hi
        fm.emit(fh, 'FL_BOUND', steps=steps, level=name, form=key, bracket='[%d,%d]/%d' % (lo, hi, b),
                bound='%d/%d' % (val, b), bound_dec=fm.dec(fm.Fr(val, b), 7), meaning=meaning[key])
    fm.emit(fh, 'FL_END', steps=steps, evaluations=len(cache), seconds=int(time.time() - t0))


if __name__ == '__main__':
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
