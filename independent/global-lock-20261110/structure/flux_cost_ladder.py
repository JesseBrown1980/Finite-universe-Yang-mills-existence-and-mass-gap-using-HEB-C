"""Pre-freeze structure check, the whole binary polyhedral ladder (2T, 2O, 2I) plus S3, integers only.
Quaternion coordinates are doubled and held as integer pairs (a, b) = a + b*w in Z[w], with w = sqrt2 (2O) or phi (2I),
phi^2 = phi + 1. Trace in the fundamental = 2 Re q = the doubled real coordinate; magnetic cost 2 - trace.
Every comparison is exact: the sign of a + b*sqrt2, or of a + b*phi = ((2a + b) + b*sqrt5)/2, by comparing squares."""
import itertools, sys
class Ring:
    def __init__(s, kind): s.kind = kind
    def mul(s, x, y):
        a, b = x; c, d = y
        if s.kind == "sqrt2": return (a*c + 2*b*d, a*d + b*c)
        if s.kind == "phi":   return (a*c + b*d, a*d + b*c + b*d)
        return (a*c, 0)
    def sign(s, x):
        a, b = x
        if s.kind == "sqrt2": p, q, D = a, b, 2
        elif s.kind == "phi": p, q, D = 2*a + b, b, 5
        else: return (a > 0) - (a < 0)
        if p >= 0 and q >= 0: return 0 if (p == 0 and q == 0) else 1
        if p <= 0 and q <= 0: return -1
        lhs, rhs = p*p, q*q*D            # p + q*sqrtD with opposite signs
        if lhs == rhs: return 0
        return (1 if p > 0 else -1) if lhs > rhs else (1 if q > 0 else -1)
def make(kind, extra):
    R = Ring(kind); z = (0, 0)
    add = lambda x, y: (x[0]+y[0], x[1]+y[1]); sub = lambda x, y: (x[0]-y[0], x[1]-y[1])
    def qmul(p, q):
        a1,b1,c1,d1 = p; a2,b2,c2,d2 = q; m = R.mul
        r = (sub(sub(sub(m(a1,a2),m(b1,b2)),m(c1,c2)),m(d1,d2)),
             add(add(m(a1,b2),m(b1,a2)),sub(m(c1,d2),m(d1,c2))),
             add(sub(m(a1,c2),m(b1,d2)),add(m(c1,a2),m(d1,b2))),
             add(sub(add(m(a1,d2),m(b1,c2)),m(c1,b2)),m(d1,a2)))
        for x in r: assert x[0] % 2 == 0 and x[1] % 2 == 0, "closure"
        return tuple((x[0]//2, x[1]//2) for x in r)
    I = lambda n: (n, 0)
    gens = [((I(1),I(1),I(1),I(1))), ((I(0),I(2),I(0),I(0))), ((I(0),I(0),I(2),I(0)))] + extra
    e = (I(2), z, z, z)
    G = {e}; frontier = [e]
    while frontier:
        nxt = []
        for g in frontier:
            for h in gens:
                p = qmul(g, h)
                if p not in G: G.add(p); nxt.append(p)
        frontier = nxt
    inv = lambda p: (p[0], (-p[1][0], -p[1][1]), (-p[2][0], -p[2][1]), (-p[3][0], -p[3][1]))
    cost = lambda p: (2 - p[0][0], -p[0][1])          # 2 - trace, in Z[w]
    return R, G, qmul, inv, cost, e
def analyse(name, kind, extra):
    R, G, mul, inv, cost, e = make(kind, extra)
    comm = {mul(mul(a, b), mul(inv(a), inv(b))) for a in G for b in G}
    classes = {}
    for g in G: classes.setdefault(frozenset(mul(mul(h, g), inv(h)) for h in G), g)
    cl = [c for c in classes if e not in c]
    cs = sorted(cl, key=lambda c: 0)  # order fixed below by exact comparison
    def less(x, y): return R.sign((x[0]-y[0], x[1]-y[1])) < 0
    cheapest = cl[0]
    for c in cl[1:]:
        if less(cost(next(iter(c))), cost(next(iter(cheapest)))): cheapest = c
    single = [c for c in cl if any(g in comm for g in c)]
    best = None
    for c in single:
        v = cost(next(iter(c)))
        if best is None or less(v, best): best = v
    k = 1
    cheapest_in_comm = any(g in comm for g in cheapest)
    if not cheapest_in_comm:      # a pair of cheaper classes could beat the cheapest single commutator class
        for c1, c2 in itertools.combinations_with_replacement(cl, 2):
            v = tuple(a + b for a, b in zip(cost(next(iter(c1))), cost(next(iter(c2)))))
            if not less(v, best): continue
            if any(mul(x, y) in comm for x in c1 for y in c2): best, k = v, 2
    tr = next(iter(cheapest))[0][0]
    print("FLUX_LADDER|group=%s|order=%d|commutator_set=%d|nontrivial_classes=%d|cheapest_class_in_commutators=%d|min_cost=%d+%d*%s|plaquettes=%d|json=0"
          % (name, len(G), len(comm), len(cl), int(cheapest_in_comm), best[0], best[1], {"sqrt2":"sqrt2","phi":"phi","int":"1"}[kind], k))
    return len(G)
I = lambda n: (n, 0)
assert analyse("2T", "int", []) == 24
assert analyse("2O", "sqrt2", [((0,1),(0,1),(0,0),(0,0))]) == 48           # (1+i)/sqrt2, doubled = sqrt2 + sqrt2 i
assert analyse("2I", "phi", [((0,1),(1,0),(-1,1),(0,0))]) == 120          # (phi + i + (phi-1) j)/2, doubled
