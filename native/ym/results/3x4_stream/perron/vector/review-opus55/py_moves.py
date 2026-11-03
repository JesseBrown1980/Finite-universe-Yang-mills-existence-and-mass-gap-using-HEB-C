# Own derivation check, written from the definition of H. S3 is Z3 semidirect Z2: (k,f) acts on Z3 by x -> k + (-1)^f x.
# Prints the empirical (da,db)xcount table per class pattern from the group alone, and asserts homomorphism and class data.
# Integer only, json=0.
import sys
from itertools import product
G=[(k,f) for f in (0,1) for k in (0,1,2)]
def mul(g,h):
    return ((g[0]+(h[0] if g[1]==0 else -h[0]))%3, g[1]^h[1])
def act(g,x):
    return (g[0]+(x if g[1]==0 else -x))%3
def fixed(g):
    return sum(1 for x in range(3) if act(g,x)==x)
for g,h in product(G,G):
    for x in range(3):
        assert act(mul(g,h),x)==act(g,act(h,x))
E=(0,0)
assert all(mul(E,g)==g and mul(g,E)==g for g in G)
assert len({tuple(act(g,x) for x in range(3)) for g in G})==6
def cost(g):
    return 2-(fixed(g)-1)
cl={g:('e' if fixed(g)==3 else 't' if fixed(g)==1 else 'c') for g in G}
assert sorted(cost(g) for g in G)==[0,2,2,2,3,3]
T=[g for g in G if fixed(g)==1]
assert len(T)==3
def lump_delta(x,y,s):
    bef=[cl[x],cl[y]]; aft=[cl[mul(s,x)],cl[mul(s,y)]]
    da=aft.count('t')-bef.count('t'); db=aft.count('c')-bef.count('c')
    return (da,db)
tab={}
n=0
for x,y in product(G,G):
    cx,cy=cl[x],cl[y]
    key=''.join(sorted([cx,cy]))
    if key=='tt':
        key='tt_same' if x==y else 'tt_diff'
    d={}
    for s in T:
        n+=1
        dl=lump_delta(x,y,s)
        d[dl]=d.get(dl,0)+1
    frozen=tuple(sorted(d.items()))
    tab.setdefault(key,set()).add(frozen)
print("FRAME_TRIPLES|n=%d|json=0"%n)
for k in sorted(tab):
    assert len(tab[k])==1, (k,tab[k])
    print("PATTERN|%s|moves=%s|json=0"%(k,sorted(next(iter(tab[k])))))
expected={'ee':[((2,0),3)],'et':[((0,0),1),((0,1),2)],'ce':[((2,-1),3)],'tt_same':[((-2,0),1),((-2,2),2)],'tt_diff':[((-2,1),2),((-2,2),1)],'ct':[((0,-1),1),((0,0),2)],'cc':[((2,-2),3)]}
for k,v in expected.items():
    assert sorted(next(iter(tab[k])))==sorted(v),(k,tab[k],v)
print("MOVE_TABLE_MATCH|patterns=%d|triples=%d|verdict=PASS|json=0"%(len(tab),n))
# flat classes from the definition: commuting pairs modulo simultaneous conjugation
def inv(g):
    return next(h for h in G if mul(g,h)==E)
pairs=[(x,y) for x,y in product(G,G) if mul(x,y)==mul(y,x)]
orbs=set()
for x,y in pairs:
    orbs.add(min((mul(mul(c,x),inv(c)),mul(mul(c,y),inv(c))) for c in G))
print("FLAT_ALGEBRA|commuting_pairs=%d|conj_orbits=%d|json=0"%(len(pairs),len(orbs)))
assert len(pairs)==18 and len(orbs)==8
if len(sys.argv)>1 and sys.argv[1]=='--sabotage':
    # A wrong claimed table for TT same: the comparison above must not pass on it.
    wrong=dict(expected); wrong['tt_same']=[((-2,0),2),((-2,2),1)]
    same=all(sorted(next(iter(tab[k])))==sorted(v) for k,v in wrong.items())
    print("MOVE_TABLE_SABOTAGE|same=%d|verdict=%s|json=0"%(1 if same else 0,'PASS' if same else 'FAIL'))
    sys.exit(0 if same else 1)
