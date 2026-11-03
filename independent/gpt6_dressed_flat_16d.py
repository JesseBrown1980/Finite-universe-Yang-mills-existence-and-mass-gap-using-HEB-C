#!/usr/bin/env python3
"""Fresh integer-only local S3 dressed-flat 16D trial-space audit.

Builds 8 flat commuting-holonomy classes, their one-link electric shells,
shell weights and all shell-to-shell electric transitions, from the lattice
definition; no hybrid vector, production store or original E8 checker.
"""
from itertools import permutations
from collections import defaultdict

GROUP = list(permutations(range(3)))
INDEX = {p:i for i,p in enumerate(GROUP)}
MUL = [[INDEX[tuple(GROUP[a][GROUP[b][k]] for k in range(3))]
        for b in range(6)] for a in range(6)]
INV = [next(b for b in range(6) if MUL[a][b]==MUL[b][a]==0)
       for a in range(6)]
TRANS = [g for g in range(6) if g!=0 and MUL[g][g]==0]
CONJ = [[MUL[MUL[g][u]][INV[g]] for u in range(6)] for g in range(6)]
assert len(TRANS)==3

class Lattice:
    def __init__(self,lx,ly):
        self.lx,self.ly=lx,ly
        self.plaquettes=lx*ly
        self.links=2*self.plaquettes
        self.steps=3*self.links
        def site(x,y):return (x%lx)+lx*(y%ly)
        def link(x,y,d):return 2*site(x,y)+d
        self.site,self.link=site,link
        tree=[]
        for x in range(lx-1):
            tree.append((link(x,0,0),site(x,0),site(x+1,0)))
        for x in range(lx):
            for y in range(ly-1):
                tree.append((link(x,y,1),site(x,y),site(x,y+1)))
        assert len(tree)==self.plaquettes-1
        self.tree=tree
        owned={e for e,_,_ in tree}
        self.free=[e for e in range(self.links) if e not in owned]
        self.src=[0]*self.links
        self.dst=[0]*self.links
        self.pl=[]
        for y in range(ly):
            for x in range(lx):
                h,v=link(x,y,0),link(x,y,1)
                self.src[h],self.dst[h]=site(x,y),site(x+1,y)
                self.src[v],self.dst[v]=site(x,y),site(x,y+1)
                self.pl.append((h,link(x+1,y,1),link(x,y+1,0),v))

    def gauge_free(self,U):
        frames=[0]*self.plaquettes
        for e,a,b in self.tree:
            frames[b]=MUL[frames[a]][U[e]]
        return tuple(MUL[MUL[frames[self.src[e]]][U[e]]][INV[frames[self.dst[e]]]]
                     for e in self.free)

    def class_key(self,U):
        values=self.gauge_free(U)
        return min(tuple(CONJ[g][v] for v in values) for g in range(6))

    def weight(self,U):
        values=self.gauge_free(U)
        return len({tuple(CONJ[g][v] for v in values) for g in range(6)})

    def flat(self,a,b):
        U=[0]*self.links
        for y in range(self.ly):
            for x in range(self.lx):
                if x==self.lx-1:
                    U[self.link(x,y,0)]=a
                if y==self.ly-1:
                    U[self.link(x,y,1)]=b
        return U

    def magnetic(self,U):
        n=0
        for a,b,c,d in self.pl:
            z=MUL[MUL[MUL[U[a]][U[b]]][INV[U[c]]]][INV[U[d]]]
            n+=0 if z==0 else 2 if z in TRANS else 3
        return n

    def neighbors(self,U):
        for e in range(self.links):
            for t in TRANS:
                v=U.copy()
                v[e]=MUL[t][v[e]]
                yield self.class_key(v),v

def check(lx,ly,expect_edges):
    lattice=Lattice(lx,ly)
    flat={}
    for a in range(6):
        for b in range(6):
            if MUL[a][b]==MUL[b][a]:
                U=lattice.flat(a,b)
                assert lattice.magnetic(U)==0
                flat.setdefault(lattice.class_key(U),U)
    assert len(flat)==8
    assert sum(lattice.weight(U) for U in flat.values())==18
    shells={}
    owner={}
    for f,U in flat.items():
        count={}
        example={}
        for k,V in lattice.neighbors(U):
            assert k not in flat
            count[k]=count.get(k,0)+1
            example[k]=V
        assert sum(count.values())==lattice.steps
        wf=lattice.weight(U)
        norm=0
        for k,V in example.items():
            assert lattice.magnetic(V)==4
            assert k not in owner or owner[k]==f
            owner[k]=f
            shells[k]=V
            wk=lattice.weight(V)
            assert wf*count[k] % wk==0
            coefficient=wf*count[k]//wk
            norm+=wk*coefficient*coefficient
        assert norm==lattice.steps*wf
    count_edges=0
    for U in shells.values():
        for k,_ in lattice.neighbors(U):
            if k in owner:
                count_edges+=1
    assert count_edges==expect_edges,(lx,ly,count_edges,expect_edges)
    assert len(flat)==8 and len(shells)>0
    print("GPT6_DRESSED_FLAT|Lx=%d|Ly=%d|flat_classes=8|flat_configs=18|"
          "shell_classes=%d|shell_shell_moves=%d|norm=3NL|"
          "truncated_block=%s|result=PASS|json=0" %
          (lx,ly,len(shells),count_edges,
           "VALID" if count_edges==0 else "INVALID"))

def main():
    check(3,3,216)  # negative geometry control: length-three winding loops.
    check(4,4,0)
    check(4,5,0)
    check(5,5,0)
    print("GPT6_DRESSED_FLAT_SCOPE|"
          "16D_trial_matrix=CHECKED_FOR_4X4_4X5_5X5|"
          "full_hybrid_E9_certificate=OPEN|json=0")

if __name__=="__main__":
    main()
