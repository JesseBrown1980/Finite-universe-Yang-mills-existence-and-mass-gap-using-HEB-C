#!/usr/bin/env python3
# Sector-resolved #136 Schur sandwich: split the 8x8 flat block into the reflection-even (A1, 7 flats)
# and reflection-odd (1 flat combination) sectors, verify the graph's reflection symmetry, and count
# levels below z per sector. Integer only. Reuses the #136 checker unchanged (blob 36ee647b). json=0.
import sys
ARGS = sys.argv[1:]
sys.argv = ['checker136.py']
sys.path.insert(0, '/mnt/c/tmp/opus55/ym137-fable5-20261109/independent')
import checker136 as c


def reflect(U, axis):
    """lattice reflection of a raw configuration: axis 'x' maps x->-x, 'y' maps y->-y"""
    V, LX, LY, pos, INV = c.V, c.LX, c.LY, c.pos, c.INV
    Z = [0] * (2 * V)
    for x in range(LX):
        for y in range(LY):
            h = U[pos(x, y)]; v = U[V + pos(x, y)]
            if axis == 'x':
                # horizontal link (x,y)->(x+1,y) becomes (-x,y)->(-x-1,y) = reversed link starting at (-x-1,y)
                Z[pos(-x - 1, y)] = INV[h]
                Z[V + pos(-x, y)] = v
            else:
                Z[pos(x, -y)] = h
                Z[V + pos(x, -y - 1)] = INV[v]
    return Z

def main(steps):
    src, floor_num = c.source_floor()
    w, m, adj, qflat, outer = c.graph()
    # rebuild the state list in the checker's order to map reflections
    flat = {}
    for a in range(6):
        for b in range(6):
            if c.MUL[a][b] != c.MUL[b][a]: continue
            U = [0] * (2 * c.V)
            for y in range(c.LY): U[c.pos(c.LX - 1, y)] = a
            for x in range(c.LX): U[c.V + c.pos(x, c.LY - 1)] = b
            flat.setdefault(c.canonical(U), (a, b))
    layers = [sorted(flat)]; seen = set(layers[0])
    for _ in range(2):
        new = set()
        for key in layers[-1]: new.update(c.neighbors(key))
        new.difference_update(seen); seen.update(new); layers.append(sorted(new))
    states = [k for L in layers for k in L]; where = {k: i for i, k in enumerate(states)}
    names = {0: 'e', 1: 'x'}
    def cls(g):
        return 'e' if g == 0 else ('t' if g in c.TRANS else 'c')
    lab = []
    for k in layers[0]:
        a, b = flat[k]; lab.append((a, b))
    perm = {}
    for axis in ('x', 'y'):
        p = []
        for k in states:
            j = where.get(c.canonical(reflect(c.from_key(k), axis)))
            assert j is not None, 'reflection_leaves_K2'
            p.append(j)
        assert sorted(p) == list(range(len(states))), 'reflection_is_a_permutation'
        assert all(w[p[i]] == w[i] and m[p[i]] == m[i] for i in range(len(states))), 'reflection_keeps_weight_and_potential'
        for i, row in enumerate(adj):
            A = dict(row); B = dict(adj[p[8 + i] - 8])
            assert all(B.get(p[8 + j] - 8, 0) == cc for j, cc in A.items()), 'reflection_commutes_with_QQ'
        for i, row in enumerate(qflat):
            assert all(qflat[p[8 + i] - 8][p[k]] == row[k] for k in range(8)), 'reflection_commutes_with_QP'
        perm[axis] = p
        print('REFLECT|axis=%s|states=%d|flat_perm=%s|json=0' % (axis, len(states), ','.join(str(p[k]) for k in range(8))))
    flat_txt = ','.join('%d:(%s,%s)w%d' % (k, cls(a), cls(b), w[k]) for k, (a, b) in enumerate(lab))
    print('FLATS|order=%s|json=0' % flat_txt)
    px, py = perm['x'][:8], perm['y'][:8]
    moved = [k for k in range(8) if px[k] != k]
    assert px == py and len(moved) == 2, ('flat_perms', px, py)
    i, j = moved
    print('ODD_PAIR|i=%d|j=%d|labels=(%s,%s),(%s,%s)|json=0' % (i, j, cls(lab[i][0]), cls(lab[i][1]), cls(lab[j][0]), cls(lab[j][1])))
    return src, floor_num, w, m, adj, qflat, outer, i, j

def congr(M, T):
    n = len(T[0])
    return [[sum(T[a][p] * M[a][b] * T[b][q] for a in range(8) for b in range(8)) for q in range(n)] for p in range(n)]

def inertia_n(A):
    n = len(A); neg = 0; prev = 1
    for k in range(1, n + 1):
        D = c.det([row[:k] for row in A[:k]])
        if D == 0: return None
        neg += int((D < 0) != (prev < 0)); prev = D
    return neg

if __name__ == '__main__':
    steps = int(ARGS[0]) if ARGS else 4
    grid = [int(a) for a in ARGS[1].split(',')] if len(ARGS) > 1 else [6989, 6992, 6993, 6994, 6995, 6996, 6997, 6998, 6999, 7000, 7002, 7005]
    src, floor_num, w, m, adj, qflat, outer, i, j = main(steps)
    c.STEPS = steps
    cap = []
    orig = c.inertia
    def grab(A):
        cap.append([row[:] for row in A]); return orig(A)
    c.inertia = grab
    # even basis: the 6 fixed flats and e_i+e_j; odd vector e_i-e_j (integer congruence, det +-2)
    E = [[0] * 7 for _ in range(8)]; col = 0
    for k in range(8):
        if k in (i, j): continue
        E[k][col] = 1; col += 1
    E[i][6] = 1; E[j][6] = 1
    O = [[0] for _ in range(8)]; O[i][0] = 1; O[j][0] = -1
    import inspect
    BDEN = int(ARGS[2]) if len(ARGS) > 2 else 100
    src_t = inspect.getsource(c.threshold)
    assert src_t.count('    b=100\n') == 1
    ns = c.__dict__
    exec(src_t.replace('def threshold(a,w,m,adj,q_flat,outer,source_floor_num):', 'def threshold_b(a,w,m,adj,q_flat,outer,source_floor_num):').replace('    b=100\n', '    b=%d\n' % BDEN), ns)
    thr = ns['threshold_b']
    print('RUN|steps=%d|den=%d|grid=%s|checker_threshold_source_reused=1|json=0' % (steps, BDEN, ','.join(str(a) for a in grid)))
    for a in grid:
        cap.clear()
        nlo, nhi = thr(a, w, m, adj, qflat, outer, floor_num)[:2]
        Lm, Um = cap[0], cap[1]
        # exact reflection symmetry of the witnesses: swapping i and j leaves them unchanged
        sw = list(range(8)); sw[i], sw[j] = j, i
        for M, nm in ((Lm, 'LOWER'), (Um, 'UPPER')):
            assert all(M[sw[x]][sw[y]] == M[x][y] for x in range(8) for y in range(8)), nm + '_not_reflection_symmetric'
            assert all(congr(M, [[E[r][q] for q in range(7)] + [O[r][0]] for r in range(8)])[p][7] == 0 for p in range(7)), nm + '_not_block_diagonal'
        eL, eU = congr(Lm, E), congr(Um, E)
        oL, oU = congr(Lm, O)[0][0], congr(Um, O)[0][0]
        neL, neU = inertia_n(eL), inertia_n(eU)
        odd_lo = int(oL < 0); odd_hi = int(oU < 0)
        print(('SECTOR|z=%d/'+str(BDEN)+'|total_lower=%d|total_upper=%d|A1_lower=%s|A1_upper=%s|odd_LOWER_form_sign=%d|odd_UPPER_form_sign=%d|odd_count_bounds=%d..%d|json=0') % (
            a, nlo, nhi, neL, neU, (oL > 0) - (oL < 0), (oU > 0) - (oU < 0), odd_hi, odd_lo))
