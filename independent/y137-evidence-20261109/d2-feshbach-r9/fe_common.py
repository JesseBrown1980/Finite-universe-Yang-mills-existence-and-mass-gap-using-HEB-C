#!/usr/bin/env python3
# d2-feshbach-r9 common layer: imports the merged #136 checker UNCHANGED (git blob 91bd1e80),
# rebuilds its 8042-state K2 graph, the state keys in the checker's order, the flat labels,
# the Wilson-sum observable O_sum on every K2 state, and caches the integer data in a local
# pickle (cold cache only, never an authority; sha256 recorded). Integer only, no float.
import sys, os, pickle, hashlib, time
_saved = sys.argv
sys.argv = ['checker136.py']
sys.path.insert(0, '/mnt/c/tmp/opus55/ym137-fable5-20261109/independent')
import checker136 as c
sys.argv = _saved

HERE = '/mnt/c/tmp/opus55/ym137-fable5-20261109/d2-feshbach-r9'
CACHE = HERE + '/k2-graph-cache.pkl'


def cls(g):
    return 'e' if g == 0 else ('t' if g in c.TRANS else 'c')


def osum(U):
    """O_sum(U) = sum_y CHAR(W_x(y)) + sum_x CHAR(W_y(x)) on a raw configuration."""
    V, LX, LY, pos, MUL, CHAR = c.V, c.LX, c.LY, c.pos, c.MUL, c.CHAR
    s = 0
    for y in range(LY):           # four horizontal length-3 loops
        h = 0
        for x in range(LX):
            h = MUL[h][U[pos(x, y)]]
        s += CHAR[h]
    for x in range(LX):           # three vertical length-4 loops
        h = 0
        for y in range(LY):
            h = MUL[h][U[V + pos(x, y)]]
        s += CHAR[h]
    return s


def build():
    t0 = time.time()
    src, floor_num = c.source_floor()
    w, m, adj, qflat, outer = c.graph()
    # rebuild state keys exactly as graph() orders them
    flat = {}
    for a in range(6):
        for b in range(6):
            if c.MUL[a][b] != c.MUL[b][a]:
                continue
            U = [0] * (2 * c.V)
            for y in range(c.LY):
                U[c.pos(c.LX - 1, y)] = a
            for x in range(c.LX):
                U[c.V + c.pos(x, c.LY - 1)] = b
            flat.setdefault(c.canonical(U), (a, b))
    layers = [sorted(flat)]
    seen = set(layers[0])
    for _ in range(2):
        new = set()
        for key in layers[-1]:
            new.update(c.neighbors(key))
        new.difference_update(seen)
        seen.update(new)
        layers.append(sorted(new))
    states = [k for L in layers for k in L]
    assert len(states) == 8042 == len(w)
    assert [c.weight(k) for k in states] == w
    lab = [flat[k] for k in layers[0]]
    O = [osum(c.from_key(k)) for k in states]
    # O on flats must equal 4 CHAR(a) + 3 CHAR(b)
    for k, (a, b) in enumerate(lab):
        assert O[k] == 4 * c.CHAR[a] + 3 * c.CHAR[b], ('O_flat', k, O[k])
    # flat -> Q counts directly from the checker's neighbors() (independent of detailed balance)
    where = {k: i for i, k in enumerate(states)}
    flat_out = []
    for k in range(8):
        row = {}
        for dst, cc in c.neighbors(states[k]).items():
            j = where[dst]
            assert j >= 8
            row[j - 8] = cc
        flat_out.append(row)
    data = dict(src=src, floor_num=floor_num, w=w, m=m, adj=adj, qflat=qflat, outer=outer,
                states=states, lab=lab, O=O, flat_out=flat_out)
    return data, time.time() - t0


def load():
    if os.path.exists(CACHE):
        raw = open(CACHE, 'rb').read()
        return pickle.loads(raw), hashlib.sha256(raw).hexdigest(), 0
    data, dt = build()
    raw = pickle.dumps(data, protocol=4)
    open(CACHE, 'wb').write(raw)
    return data, hashlib.sha256(raw).hexdigest(), dt


if __name__ == '__main__':
    d, h, dt = load()
    nnz = sum(len(r) for r in d['adj'])
    nself = sum(1 for i, r in enumerate(d['adj']) for j, cc in r if j == i)
    print('FE_GRAPH|states=%d|qq_nnz=%d|qq_self=%d|exterior=%d|ext_edges=%d|build_s=%d|cache_sha256=%s|json=0' % (
        len(d['w']), nnz, nself, len(d['outer']), sum(len(e) for _, e in d['outer']), dt, h))
    lab = d['lab']
    print('FE_FLATS|' + '|'.join('f%d=(%s,%s)w%d,O=%d' % (k, cls(a), cls(b), d['w'][k], d['O'][k])
                                 for k, (a, b) in enumerate(lab)) + '|json=0')
    from collections import Counter
    print('FE_OSUM_HIST|' + ','.join('%d:%d' % kv for kv in sorted(Counter(d['O']).items())) + '|json=0')
