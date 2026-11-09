#!/usr/bin/env python3
# d2-feshbach-r9 K3 extension: the 147344 exterior targets of #136 become trial (Q) states,
# so the trial resolvent lives on K3 = 8 flats + 264 + 7770 + 147344 orbits and the residual
# moves to shell 4 (every shell-4 orbit is generated and its weight computed exactly).
# Same integer Jacobi / variational Schur form / Illinois root / exact-rational lift as fe_main.
# Integer / exact rational only. json=0.
import sys, os, time, pickle, hashlib
from array import array
from collections import Counter
from fractions import Fraction as Fr
sys.path.insert(0, '/mnt/c/tmp/opus55/ym137-fable5-20261109/d2-feshbach-r9')
import fe_main as fm
c = fm.c
HERE = fm.fc.HERE
K3CACHE = HERE + '/k3-graph-cache.pkl'
KNOWN = None


def code(key):
    v = 0
    for x in reversed(key):
        v = v * 6 + x
    return v


def decode(v):
    out = []
    for _ in range(13):
        v, r = divmod(v, 6)
        out.append(r)
    return tuple(out)


def build_k3():
    t0 = time.time()
    d = fm.d
    states, w = d['states'], d['w']
    where = {k: i for i, k in enumerate(states)}
    # rebuild the exterior keys in graph()'s exact order and verify against the cached outer
    outside = {}
    for i, key in enumerate(states):
        if i < 8:
            continue
        for dst, cc in c.neighbors(key).items():
            if dst not in where:
                outside.setdefault(dst, []).append((i - 8, w[i] * cc))
    ext_keys = list(outside)
    assert [(c.weight(k), e) for k, e in outside.items()] == d['outer'], 'exterior_order_rebuild'
    ext_index = {k: t for t, k in enumerate(ext_keys)}
    nE = len(ext_keys)
    wE = array('b', [c.weight(k) for k in ext_keys])
    mE = array('b', [c.magnetic(c.from_key(k)) for k in ext_keys])
    rowsK2 = []       # per exterior state: K2-Q neighbours (index into Q2, count)
    rowsE_idx = []; rowsE_cnt = []
    s4_idx = []; s4_cnt = []
    s4_weight = {}
    for t, key in enumerate(ext_keys):
        a2 = []; ei = array('l'); ec = array('b'); fi = array('q'); fcn = array('b')
        for dst, cc in c.neighbors(key).items():
            j = where.get(dst)
            if j is not None:
                assert j >= 8 + 264, 'exterior_touches_shell1_or_flat'
                a2.append((j - 8, cc))
            else:
                u = ext_index.get(dst)
                if u is not None:
                    ei.append(u); ec.append(cc)
                else:
                    cd = code(dst)
                    if cd not in s4_weight:
                        s4_weight[cd] = c.weight(dst)
                    fi.append(cd); fcn.append(cc)
        rowsK2.append(a2); rowsE_idx.append(ei); rowsE_cnt.append(ec)
        s4_idx.append(fi); s4_cnt.append(fcn)
        if t % 20000 == 0:
            print('K3_BUILD|t=%d|s4=%d|sec=%d|json=0' % (t, len(s4_weight), time.time() - t0), flush=True)
    # detailed balance K2 <-> exterior
    for t, (W, edges) in enumerate(d['outer']):
        back = dict(rowsK2[t])
        assert len(back) == len(edges)
        for i, wc in edges:
            assert W * back[i] == wc, 'weighted_K2_exterior_adjoint'
    data = dict(nE=nE, ext_codes=array('q', [code(k) for k in ext_keys]), wE=wE, mE=mE, rowsK2=rowsK2, rowsE_idx=rowsE_idx, rowsE_cnt=rowsE_cnt,
                s4_idx=s4_idx, s4_cnt=s4_cnt, s4_weight=s4_weight)
    return data, time.time() - t0


def load_k3():
    if os.path.exists(K3CACHE):
        raw = open(K3CACHE, 'rb').read()
        return pickle.loads(raw), hashlib.sha256(raw).hexdigest(), 0
    data, dt = build_k3()
    raw = pickle.dumps(data, protocol=4)
    open(K3CACHE, 'wb').write(raw)
    return data, hashlib.sha256(raw).hexdigest(), dt


def setup():
    """K3 Q-space operator data (same construction as main), for fe_k3lower.py."""
    k3, k3sha, _ = load_k3()
    d = fm.d
    n2 = fm.n
    nE = k3['nE']
    N = n2 + nE
    wQ = list(fm.wq) + list(k3['wE'])
    mQ = list(d['m'][8:]) + list(k3['mE'])
    ext_keys = [decode(v) for v in k3['ext_codes']]
    assert len(ext_keys) == nE and all(c.weight(k) == W for k, (W, _) in zip(ext_keys, d['outer']))
    off = [list(r) for r in fm.off]
    for t, (W, edges) in enumerate(d['outer']):
        for i, wc in edges:
            assert wc % fm.wq[i] == 0
            off[i].append((n2 + t, wc // fm.wq[i]))
    selfE = []
    for t in range(nE):
        row = list(k3['rowsK2'][t])
        sc = 0
        for u, cc in zip(k3['rowsE_idx'][t], k3['rowsE_cnt'][t]):
            if u == t:
                sc += cc
            else:
                row.append((n2 + u, cc))
        off.append(row); selfE.append(sc)
    selfQ = list(fm.selfc) + selfE
    D = [72 + 9 * mQ[i] - selfQ[i] for i in range(N)]
    C = list(fm.C) + [[0] * 8 for _ in range(nE)]
    return dict(k3=k3, k3sha=k3sha, n2=n2, nE=nE, N=N, wQ=wQ, off=off, D=D, C=C)


def main(steps, steps_check, SCALE_EXP, B_EXP, out):
    fh = open(out, 'w')
    t0 = time.time()
    k3, k3sha, bdt = load_k3()
    d = fm.d
    n2 = fm.n
    nE = k3['nE']
    N = n2 + nE
    w = d['w']
    wQ = list(fm.wq) + list(k3['wE'])
    mQ = list(d['m'][8:]) + list(k3['mE'])
    ext_keys = [decode(v) for v in k3['ext_codes']]
    assert len(ext_keys) == nE and all(c.weight(k) == W for k, (W, _) in zip(ext_keys, d['outer']))
    OQ = list(fm.Oq) + [fm.fc.osum(c.from_key(k)) for k in ext_keys]
    # adjacency on Q3
    off = [list(r) for r in fm.off]
    for t, (W, edges) in enumerate(d['outer']):
        for i, wc in edges:
            assert wc % fm.wq[i] == 0
            off[i].append((n2 + t, wc // fm.wq[i]))
    selfE = []
    for t in range(nE):
        row = list(k3['rowsK2'][t])
        sc = 0
        for u, cc in zip(k3['rowsE_idx'][t], k3['rowsE_cnt'][t]):
            if u == t:
                sc += cc
            else:
                row.append((n2 + u, cc))
        off.append(row); selfE.append(sc)
    selfQ = list(fm.selfc) + selfE
    D = [72 + 9 * mQ[i] - selfQ[i] for i in range(N)]
    C = list(fm.C) + [[0] * 8 for _ in range(nE)]
    nnz = sum(len(r) for r in off)
    s4n = len(k3['s4_weight'])
    fm.emit(fh, 'K3_BEGIN', steps=steps, steps_check=steps_check, SCALE='10^%d' % SCALE_EXP,
            z_den='10^%d' % B_EXP, q_states=N, q_nnz=nnz, shell4_targets=s4n,
            shell4_edges=sum(len(x) for x in k3['s4_idx']), k3_cache_sha256=k3sha, build_s=int(bdt),
            tag='ESTIMATE')
    SCALE = 10 ** SCALE_EXP
    b = 10 ** B_EXP
    maxC = max(max(r) for r in C)
    maxrow = max(sum(cc for _, cc in r) for r in off)

    def width(st, a_max):
        dmin = min(b * x - a_max for x in D)
        Yb = 0; need = 0
        for _ in range(st + 1):
            fieldmax = SCALE * maxC + maxrow * Yb
            need = max(need, fieldmax.bit_length())
            Yb = (b * fieldmax) // dmin + 1
        return max(128, 32 * ((need + 2 + 31) // 32))

    def jacobi(a, st):
        WD = width(st, a)
        MASK = (1 << WD) - 1
        SH = [WD * k for k in range(8)]
        den = [b * x - a for x in D]
        assert min(den) > 0
        SC = [SCALE * sum(C[i][k] << SH[k] for k in range(8)) for i in range(N)]
        P = [0] * N
        for _ in range(st):
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
        AY = []
        for i in range(N):
            T = 0
            for j, cc in off[i]:
                T += cc * P[j]
            AY.append([den[i] * Y[i][k] - b * ((T >> SH[k]) & MASK) for k in range(8)])
        U = [[0] * 8 for _ in range(8)]
        sb = SCALE * b
        for i in range(N):
            wi = wQ[i]; y = Y[i]; ci = C[i]; ay = AY[i]
            for p in range(8):
                yp = wi * y[p]
                if yp == 0 and ci[p] == 0:
                    continue
                cp = wi * ci[p]
                row = U[p]
                for q in range(8):
                    row[q] += yp * ay[q] - sb * (cp * y[q] + yp * ci[q])
        for k in range(8):
            U[k][k] += SCALE * SCALE * w[k] * (b * 72 - a)
        assert all(U[p][q] == U[q][p] for p in range(8) for q in range(8))
        Ue = fm.congr(U, fm.EB)
        Uo = sum(fm.OB[x] * U[x][y] * fm.OB[y] for x in range(8) for y in range(8))
        assert all(sum(fm.EB[x][p] * U[x][y] * fm.OB[y] for x in range(8) for y in range(8)) == 0 for p in range(7))
        return dict(Y=Y, Ue=Ue, Uo=Uo, det=c.det(Ue), neg=fm.inertia(Ue))

    cache = {}   # small results only (neg, det, Uo); trial resolvents are NOT kept (memory)

    def ev(a):
        if a not in cache:
            r = jacobi(a, steps)
            cache[a] = dict(neg=r['neg'], det=r['det'], Uo=r['Uo'])
            fm.emit(fh, 'K3_EVAL', z='%d/%d' % (a, b), even_neg=r['neg'], det_sign=fm.sgn(r['det']),
                    odd_sign=fm.sgn(r['Uo']), sec=int(time.time() - t0))
            del r
        return cache[a]

    # K2 converged roots (fe_main steps>=32): E1 69.917141101.., E2 69.956750266..
    roots = {}
    if KNOWN:
        # brackets measured earlier by this same code (k3-amp-roots.rows); re-verify counts at both ends
        for name, k_lo, (lo, hi) in (('E1_even', 0, KNOWN[0]), ('E2_even', 1, KNOWN[1])):
            assert ev(lo)['neg'] == k_lo and ev(hi)['neg'] == k_lo + 1, ('known_bracket_counts', name)
            roots[name] = (lo, hi, ev(lo)['det'], ev(hi)['det'], 0)
    for name, k_lo, a_hi0 in (() if KNOWN else (('E1_even', 0, 69917141102 * b // 10 ** 9), ('E2_even', 1, 69956750267 * b // 10 ** 9))):
        a_hi = a_hi0
        a_lo = a_hi - 25 * b // 1000
        while ev(a_hi)['neg'] < k_lo + 1:
            a_hi += 5 * b // 1000
        while ev(a_lo)['neg'] > k_lo:
            a_lo -= 5 * b // 1000
        # tighten to a bracket with exactly one crossing
        while ev(a_hi)['neg'] - ev(a_lo)['neg'] > 1:
            mid = (a_lo + a_hi) // 2
            if ev(mid)['neg'] <= k_lo:
                a_lo = mid
            else:
                a_hi = mid
        lo, hi, flo, fhi, ne = fm.illinois(lambda a: ev(a)['det'], a_lo, a_hi, ev(a_lo)['det'], ev(a_hi)['det'])
        roots[name] = (lo, hi, flo, fhi, ne)
    # lifts and amplitudes
    s4w = k3['s4_weight']
    psi = {}
    for name in ('E1_even', 'E2_even'):
        lo, hi, flo, fhi, ne = roots[name]
        a_end = lo if abs(flo) <= abs(fhi) else hi
        for st in sorted({steps, steps_check}):
            r = jacobi(a_end, st)
            u7 = fm.null_vector(r['Ue'])
            v8 = [sum(fm.EB[k][p] * u7[p] for p in range(7)) for k in range(8)]
            Pf = [SCALE * x for x in v8]
            Pq = [sum(r['Y'][i][k] * v8[k] for k in range(8)) for i in range(N)]
            del r
            # residual (bH - a) Psi on K3 and shell 4
            rf = [(b * 72 - a_end) * Pf[k] - b * sum(cc * Pq[j] for j, cc in fm.flat_out[k].items()) for k in range(8)]
            rq = []
            for i in range(N):
                t = 0
                for j, cc in off[i]:
                    t += cc * Pq[j]
                for k in range(8):
                    if C[i][k]:
                        t += C[i][k] * Pf[k]
                rq.append((b * D[i] - a_end) * Pq[i] - b * t)
            k3res = 6 * (sum(w[k] * rf[k] ** 2 for k in range(8)) + sum(wQ[i] * rq[i] ** 2 for i in range(N)))
            agg = {}
            for t in range(nE):
                p = Pq[n2 + t]
                if p:
                    wp = wQ[n2 + t] * p
                    for cd, cc in zip(k3['s4_idx'][t], k3['s4_cnt'][t]):
                        agg[cd] = agg.get(cd, 0) + cc * wp
            s4res = 0
            for cd, S in agg.items():
                s4res += (6 // s4w[cd]) * (b * S) ** 2
            del agg
            quad = sum(w[k] * Pf[k] * rf[k] for k in range(8)) + sum(wQ[i] * Pq[i] * rq[i] for i in range(N))
            nf = sum(w[k] * Pf[k] ** 2 for k in range(8))
            n12 = sum(wQ[i] * Pq[i] ** 2 for i in range(n2))
            n3 = sum(wQ[i] * Pq[i] ** 2 for i in range(n2, N))
            nrm = nf + n12 + n3
            z = Fr(a_end, b)
            rho = z + Fr(quad, b * nrm)
            rz2 = Fr(k3res + s4res, 6 * b * b * nrm)
            rr2 = rz2 - (rho - z) ** 2
            del rf, rq
            psi[(name, st)] = dict(Pf=Pf, Pq=Pq, nrm=nrm, rho=rho, rr2=rr2)
            fm.emit(fh, 'K3_LEVEL', steps=st, which=name, z_lo='%d/%d' % (lo, b), z_hi='%d/%d' % (hi, b),
                    z_used=fm.dec(z, 9), rayleigh=fm.dec(rho, 12), rel_res2_at_rho=fm.dec(rr2, 15),
                    rel_res_at_rho=fm.sqrt_dec(max(rr2, Fr(0)), 12), shell4_share_of_res2=fm.dec(Fr(s4res, k3res + s4res), 9),
                    norm_share_flat=fm.dec(Fr(nf, nrm), 12), norm_share_shell12=fm.dec(Fr(n12, nrm), 12),
                    norm_share_shell3=fm.dec(Fr(n3, nrm), 12), tag='ESTIMATE')
    for st in sorted({steps, steps_check}):
        p1, p2 = psi[('E1_even', st)], psi[('E2_even', st)]
        s = fm.sgn(p1['Pf'][0]) * fm.sgn(p2['Pf'][3])
        Af = s * sum(w[k] * fm.O[k] * p2['Pf'][k] * p1['Pf'][k] for k in range(8))
        A12 = s * sum(wQ[i] * OQ[i] * p2['Pq'][i] * p1['Pq'][i] for i in range(n2))
        A3 = s * sum(wQ[i] * OQ[i] * p2['Pq'][i] * p1['Pq'][i] for i in range(n2, N))
        G = s * (sum(w[k] * p2['Pf'][k] * p1['Pf'][k] for k in range(8)) + sum(wQ[i] * p2['Pq'][i] * p1['Pq'][i] for i in range(N)))
        A = Af + A12 + A3
        N12 = p1['nrm'] * p2['nrm']
        amp2 = Fr(A * A, N12)
        fm.emit(fh, 'K3_AMP', steps=st, amp=('-' if A < 0 else '') + fm.sqrt_dec(amp2, 12), amp2=fm.dec(amp2, 15),
                flat_share=fm.dec(Fr(Af, A), 9), shell12_share=fm.dec(Fr(A12, A), 9), shell3_share=fm.dec(Fr(A3, A), 9),
                overlap_psi1_psi2=('-' if G < 0 else '') + fm.sqrt_dec(Fr(G * G, N12), 12),
                residual='res1=%s,res2=%s' % (fm.sqrt_dec(max(p1['rr2'], Fr(0)), 12), fm.sqrt_dec(max(p2['rr2'], Fr(0)), 12)),
                amp2_exact_sha256=hashlib.sha256(('%d/%d' % (amp2.numerator, amp2.denominator)).encode()).hexdigest(),
                tag='ESTIMATE')
    fm.emit(fh, 'K3_END', evaluations=len(cache), seconds=int(time.time() - t0))


if __name__ == '__main__':
    if sys.argv[1] == 'build':
        data, sha, dt = load_k3()
        print('K3_CACHE|sha256=%s|build_s=%d|ext=%d|shell4=%d|json=0' % (sha, dt, data['nE'], len(data['s4_weight'])))
    else:
        if len(sys.argv) > 7:   # known brackets "lo1,hi1,lo2,hi2" (integers over 10^B_EXP)
            v = [int(x) for x in sys.argv[7].split(',')]
            KNOWN = ((v[0], v[1]), (v[2], v[3]))
        main(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6])
