#!/usr/bin/env python3
"""Independent full 3x4 S3 first-shell electric-neighbor enumeration.

This checker does NOT rely on the commuting-holonomy short-string coefficient
in finite_3x4_s3_highr_check.py; it reconstructs exact gauged configurations,
24-link transposition moves and weighted reverse counts. Integer/rational only.
"""
from collections import Counter
# Pure integer rational pairs; the repository forbids the fractions module.
def _gcd(a,b):
    a=abs(a)
    b=abs(b)
    while b:
        a,b=b,a%b
    return a

class F:
    __slots__=("numerator","denominator")
    def __init__(self,n,d=1):
        if isinstance(n,F):
            assert d==1
            n,d=n.numerator,n.denominator
        assert isinstance(n,int) and isinstance(d,int) and d>0
        g=_gcd(n,d)
        self.numerator=n//g
        self.denominator=d//g
    def __add__(self,other):
        b=F(other)
        return F(self.numerator*b.denominator+b.numerator*self.denominator,
                 self.denominator*b.denominator)
    __radd__=__add__
    def __neg__(self):
        return F(-self.numerator,self.denominator)
    def __sub__(self,other):
        return self+(-F(other))
    def __rsub__(self,other):
        return F(other)+(-self)
    def __mul__(self,other):
        b=F(other)
        return F(self.numerator*b.numerator,self.denominator*b.denominator)
    __rmul__=__mul__
    def __eq__(self,other):
        if not isinstance(other,(int,F)):
            return False
        b=F(other)
        return self.numerator==b.numerator and self.denominator==b.denominator
    def __lt__(self,other):
        b=F(other)
        return self.numerator*b.denominator < b.numerator*self.denominator
    def __gt__(self,other):
        b=F(other)
        return self.numerator*b.denominator > b.numerator*self.denominator
    def __le__(self,other):
        return self<other or self==other
    def __ge__(self,other):
        return self>other or self==other
    def __repr__(self):
        return str(self.numerator)+"/"+str(self.denominator)

from itertools import permutations

LX,LY=3,4
V=LX*LY
G=tuple(permutations(range(3)))
ids={x:i for i,x in enumerate(G)}
T=tuple(tuple(ids[tuple(G[a][G[b][i]] for i in range(3))]
              for b in range(6)) for a in range(6))
I=tuple(next(b for b in range(6) if T[a][b]==T[b][a]==0)
        for a in range(6))
TRANS=tuple(i for i in range(1,6) if T[i][i]==0)
CHI=tuple(sum(G[a][i]==i for i in range(3))-1 for a in range(6))
assert len(TRANS)==3

def pos(x,y):
    return (x%LX)*LY+(y%LY)

TREE=[(pos(0,y),pos(0,y+1),V+pos(0,y)) for y in range(LY-1)]
TREE += [(pos(x,y),pos(x+1,y),pos(x,y))
         for y in range(LY) for x in range(LX-1)]
TREESET={k for u,v,k in TREE}
KEEP=tuple(j for j in range(2*V) if j not in TREESET)
assert len(KEEP)==13
CONJ=tuple(tuple(T[T[g][a]][I[g]] for a in range(6))
           for g in range(6))

def gauge_fixed(U):
    h=[-1]*V
    h[pos(0,0)]=0
    for u,v,k in TREE:
        assert h[u]>=0
        h[v]=T[h[u]][U[k]]
    assert all(z>=0 for z in h)
    f=[0]*(2*V)
    for x in range(LX):
        for y in range(LY):
            k=pos(x,y)
            f[k]=T[T[h[k]][U[k]]][I[h[pos(x+1,y)]]]
            f[V+k]=T[T[h[k]][U[V+k]]][I[h[pos(x,y+1)]]]
    assert all(f[k]==0 for k in TREESET)
    return tuple(f[k] for k in KEEP)

def canonical(U):
    x=gauge_fixed(U)
    return min(tuple(CONJ[g][a] for a in x) for g in range(6))

def from_key(key):
    U=[0]*(2*V)
    for k,x in zip(KEEP,key):
        U[k]=x
    return U

def weight(key):
    return len({tuple(CONJ[g][x] for x in key) for g in range(6)})

def magnetic(U):
    ans=0
    for x in range(LX):
        for y in range(LY):
            p=pos(x,y)
            right=pos(x+1,y)
            up=pos(x,y+1)
            plaquette=T[T[T[U[p]][U[V+right]]][I[U[up]]]][I[U[V+p]]]
            ans+=2-CHI[plaquette]
    return ans

def moved(U,k,t):
    out=U.copy()
    out[k]=T[t][out[k]]
    return out

flat={}
for a in range(6):
    for b in range(6):
        if T[a][b]!=T[b][a]:
            continue
        U=[0]*(2*V)
        for y in range(LY):
            U[pos(LX-1,y)]=a
        for x in range(LX):
            U[V+pos(x,LY-1)]=b
        assert magnetic(U)==0
        flat[canonical(U)]=(a,b)
FKEYS=sorted(flat)
assert len(FKEYS)==8
W={key:weight(key) for key in FKEYS}
assert sum(W.values())==18

first={}
shell=set()
for key in FKEYS:
    U=from_key(key)
    nbr=Counter(canonical(moved(U,k,t))
                for k in range(2*V) for t in TRANS)
    assert sum(nbr.values())==72
    assert set(nbr).isdisjoint(flat)
    first[key]=nbr
    shell.update(nbr)
assert len(shell)==264
MS={key:magnetic(from_key(key)) for key in shell}
assert set(MS.values())=={4}

reverse={}
shell_adj={}
SW={key:weight(key) for key in shell}
for key in shell:
    U=from_key(key)
    nbr=Counter(canonical(moved(U,k,t))
                for k in range(2*V) for t in TRANS)
    assert sum(nbr.values())==72
    reverse[key]={k:n for k,n in nbr.items() if k in flat}
    shell_adj[key]={k:n for k,n in nbr.items() if k in shell}
for k in FKEYS:
    for s,z in first[k].items():
        assert W[k]*z==SW[s]*reverse[s].get(k,0)
for k,neighbors in shell_adj.items():
    for s,z in neighbors.items():
        assert SW[k]*z==SW[s]*shell_adj[s].get(k,0)

C0=[[F(0) for j in range(8)] for i in range(8)]
C1=[[F(0) for j in range(8)] for i in range(8)]
for i,fi in enumerate(FKEYS):
    for u,zi in first[fi].items():
        for j,fj in enumerate(FKEYS):
            if w:=reverse[u].get(fj,0):
                C0[i][j]+=F(zi*w,MS[u])
        for v,zuv in shell_adj[u].items():
            for j,fj in enumerate(FKEYS):
                if w:=reverse[v].get(fj,0):
                    C1[i][j]+=F(zi*zuv*w,MS[u]*MS[v])
for C in (C0,C1):
    for i,fi in enumerate(FKEYS):
        for j,fj in enumerate(FKEYS):
            assert W[fi]*C[i][j]==W[fj]*C[j][i]
assert C0==[[F(18) if i==j else F(0) for j in range(8)]
           for i in range(8)]
want=[[F(0) for j in range(8)] for i in range(8)]
for i,j,x in ((0,1,F(9,2)),(1,0,F(3,2)),(1,2,F(3)),
              (2,1,F(9,2)),(3,4,F(3,2)),(4,3,F(3,2))):
    want[i][j]=x
assert C1==want
print("FINITE34_FULL_SHELL|flat=8|first_neighbors=264|potential=4"
      "|C0=18I8|C1_MATCH_INDEPENDENT|weight_adjoint=PASS|json=0")
