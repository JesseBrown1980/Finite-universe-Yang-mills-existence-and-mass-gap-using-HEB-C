"""Pre-freeze structure check (not a measurement of the predicted gap): on a torus the ordered product of all plaquette
holonomies equals a commutator [a,b] of the two cycle holonomies. So the plaquette fluxes of a gauge-invariant state are
classes C_1..C_k with representatives whose product is a commutator. Minimal nonflat magnetic cost = min sum (2 - chi(C_i)).
Integers only: S3 as permutations with chi_std = fixed points - 1; 2T as quaternions with doubled integer coordinates."""
import itertools, hashlib
def s3():
    G=list(itertools.permutations(range(3)))
    mul=lambda a,b: tuple(a[b[i]] for i in range(3))
    inv=lambda a: tuple(sorted(range(3), key=lambda i:a[i]))
    chi2=lambda a: 2*(sum(1 for i in range(3) if a[i]==i)-1)   # 2*chi_std, integer
    return G,mul,inv,chi2,(0,1,2)
def t2():   # binary tetrahedral: quaternions with coordinates doubled (integers), norm 4
    G=set()
    for s in itertools.product((-2,2),repeat=1):
        for pos in range(4):
            v=[0,0,0,0]; v[pos]=s[0]; G.add(tuple(v))
    for s in itertools.product((-1,1),repeat=4): G.add(tuple(s))
    G=sorted(G)
    def mul(p,q):
        a1,b1,c1,d1=p; a2,b2,c2,d2=q
        r=(a1*a2-b1*b2-c1*c2-d1*d2, a1*b2+b1*a2+c1*d2-d1*c2, a1*c2-b1*d2+c1*a2+d1*b2, a1*d2+b1*c2-c1*b2+d1*a2)
        return tuple(x//2 for x in r)
    inv=lambda p:(p[0],-p[1],-p[2],-p[3])
    chi2=lambda p: 2*p[0]   # trace = 2*Re(q) = p[0] (doubled coords) ; return 2*trace for a common scale
    return G,mul,inv,chi2,(2,0,0,0)
def run(name,grp):
    G,mul,inv,chi2,e=grp
    assert len({mul(a,b) for a in G for b in G})==len(G)
    comm={mul(mul(a,b),mul(inv(a),inv(b))) for a in G for b in G}
    cls={}
    for g in G: cls.setdefault(frozenset(mul(mul(h,g),inv(h)) for h in G),g)
    classes=[c for c in cls if e not in c]
    cost=lambda c: 2*chi2(e)-2*chi2(next(iter(c)))   # 4*(2 - chi) scale-free integer
    best=None
    for k in (1,2,3):
        for tup in itertools.combinations_with_replacement(classes,k):
            ok=any(x in comm for x in [functools_prod(mul,reps,e) for reps in itertools.product(*[list(c) for c in tup])])
            if ok:
                c=sum(cost(x) for x in tup)
                if best is None or c<best[0]: best=(c,k,[sorted(x)[0] for x in tup])
    print("FLUX_COST|group=%s|order=%d|commutator_set=%d|nontrivial_classes=%d|min_cost_x4=%d|plaquettes=%d|json=0"%(name,len(G),len(comm),len(classes),best[0],best[1]))
def functools_prod(mul,xs,e):
    r=e
    for x in xs: r=mul(r,x)
    return r
run("S3_chi_std",s3()); run("2T_fund",t2())
