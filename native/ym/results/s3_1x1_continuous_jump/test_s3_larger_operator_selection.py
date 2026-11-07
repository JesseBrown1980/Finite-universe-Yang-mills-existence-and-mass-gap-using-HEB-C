#!/usr/bin/env python3
"""Exact S3 gauge-invariant odd-operator selection on 2x2 and 2x3 periodic lattices.

Integer-only local symmetry certificate (no spectrum or first-gap claim).
"""
from collections import Counter
from itertools import permutations
from random import Random

G=list(permutations(range(3)))
I=(0,1,2)
TRANS=[g for g in G if sum(g[j]==j for j in range(3))==1]
assert len(TRANS)==3

def mul(a,b):return tuple(a[b[i]] for i in range(3))
def inv(a):return tuple(a.index(i) for i in range(3))
def chi(a):return sum(int(a[i]==i) for i in range(3))-1

def sites(Lx,Ly):return [(x,y) for y in range(Ly) for x in range(Lx)]
def links(Lx,Ly):return [(x,y,d) for x,y in sites(Lx,Ly) for d in (0,1)]
def end(x,y,d,Lx,Ly):
    return ((x+1)%Lx,y) if d==0 else (x,(y+1)%Ly)

def gauge(c,Lx,Ly,h):
    return {k:mul(mul(h[(x,y)],v),inv(h[end(x,y,d,Lx,Ly)]))
            for k,v in c.items() for x,y,d in (k,)}

def symmetry(c,Lx,kind):
    if kind=="swap":
        return {(y,x,1-d):v for (x,y,d),v in c.items()}
    return {((x+1)%Lx,y,d):v for (x,y,d),v in c.items()}

def plaquette(c,x,y,Lx,Ly):
    xp=(x+1)%Lx
    yp=(y+1)%Ly
    return mul(mul(mul(c[(x,y,0)],c[(xp,y,1)]),
                   inv(c[(x,yp,0)])),inv(c[(x,y,1)]))

def magnetic(c,Lx,Ly):
    return sum(2-chi(plaquette(c,x,y,Lx,Ly))
               for x,y in sites(Lx,Ly))

def winding(c,L,d):
    acc=I
    for z in range(L):
        acc=mul(acc,c[(z,0,0)] if d==0 else c[(0,z,1)])
    return chi(acc)

def observable(c,Lx,Ly,kind):
    if kind=="swap":
        return winding(c,Lx,0)-winding(c,Ly,1)
    return chi(plaquette(c,0,0,Lx,Ly))-chi(plaquette(c,1,0,Lx,Ly))

def steps(c,Lx,Ly,kind=None):
    ks=links(Lx,Ly)
    images=Counter()
    for key in ks:
        for g in TRANS:
            v=c.copy()
            v[key]=mul(g,v[key])
            if kind is not None:
                v=symmetry(v,Lx,kind)
            images[tuple(v[k] for k in ks)]+=1
    return images

def run(Lx,Ly,kind):
    rng=Random(776666+100*Lx+Ly)
    gauge_count=0;nonzero=0;open_red=0;even_red=0
    for trial in range(96):
        ks=links(Lx,Ly)
        c={k:G[rng.randrange(6)] for k in ks}
        if trial==0:
            c={k:I for k in ks}
            c[(0,0,0)]=(1,0,2)
        O=observable(c,Lx,Ly,kind)
        transformed=symmetry(c,Lx,kind)
        assert symmetry(transformed,Lx,kind)==c
        assert observable(transformed,Lx,Ly,kind)==-O
        assert magnetic(transformed,Lx,Ly)==magnetic(c,Lx,Ly)
        assert steps(c,Lx,Ly,kind)==steps(transformed,Lx,Ly)
        nonzero+=int(O!=0)
        for _ in range(6):
            h={site:G[rng.randrange(6)] for site in sites(Lx,Ly)}
            gc=gauge(c,Lx,Ly,h)
            assert observable(gc,Lx,Ly,kind)==O
            assert magnetic(gc,Lx,Ly)==magnetic(c,Lx,Ly)
            open_red+=int(chi(gc[(0,0,0)])-chi(gc[(0,0,1)]) !=
                          chi(c[(0,0,0)])-chi(c[(0,0,1)]))
            gauge_count+=1
        if kind=="swap":
            even=winding(c,Lx,0)+winding(c,Ly,1)
            t_even=winding(transformed,Lx,0)+winding(transformed,Ly,1)
        else:
            even=chi(plaquette(c,0,0,Lx,Ly))+chi(plaquette(c,1,0,Lx,Ly))
            t_even=chi(plaquette(transformed,0,0,Lx,Ly))+chi(plaquette(transformed,1,0,Lx,Ly))
        even_red+=int(even!=0 and t_even!=-even)
    assert nonzero>0 and open_red>0 and even_red>0
    print("LARGER_SELECTION|lattice="+str(Lx)+"x"+str(Ly)+
          "|symmetry="+kind+"|configs=96|gauge_transforms="+str(gauge_count)+
          "|nonzero_operator_cases="+str(nonzero)+
          "|gauge_invariance=PASS|electric_covariance=PASS|magnetic_covariance=PASS"+
          "|operator_parity=ODD|open_link_control=REJECT|even_channel_control=REJECT"+
          "|first_excitation_overlap=NOT_MEASURED|json=0")

if __name__=="__main__":
    run(2,2,"swap")
    run(2,3,"tx")
    print("LARGER_SELECTION_VERIFY|result=PASS|lattices=2|spectral_gap=OPEN|json=0")
