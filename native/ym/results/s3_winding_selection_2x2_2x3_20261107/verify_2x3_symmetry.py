#!/usr/bin/env python3
"""Independent exact raw-link tests for 2x3 S3 x-translation-odd Wilson operator.
This establishes symmetry selection only, not the location of the first eigenvalue.
No float, no NumPy, no JSON.
"""
from itertools import permutations
P=tuple(permutations(range(3))); IDX={p:i for i,p in enumerate(P)}
M=tuple(tuple(IDX[tuple(P[a][P[b][k]] for k in range(3))]
         for b in range(6)) for a in range(6))
I=tuple(next(b for b in range(6) if M[a][b]==M[b][a]==0) for a in range(6))
T=tuple(i for i in range(6) if M[i][i]==0 and i)
assert len(T)==3
def mul(*a):
    z=0
    for x in a:z=M[z][x]
    return z
def chi(g):return 2 if g==0 else 0 if g in T else -1
def site(x,y):return (x%2)*3+y%3
def tx(u):
    v=[0]*12
    for x in range(2):
        for y in range(3):
            s=site(x,y);t=site(x+1,y)
            v[s]=u[t];v[6+s]=u[6+t]
    return v
def gauge(u,h):
    v=[0]*12
    for x in range(2):
        for y in range(3):
            s=site(x,y);r=site(x+1,y);up=site(x,y+1)
            v[s]=mul(h[s],u[s],I[h[r]])
            v[6+s]=mul(h[s],u[6+s],I[h[up]])
    return v
def plaquette(u,x,y):
    s=site(x,y);r=site(x+1,y);up=site(x,y+1)
    return mul(u[s],u[6+r],I[u[up]],I[u[6+s]])
def observable(u):
    return chi(plaquette(u,0,0))-chi(plaquette(u,1,0))
def magnetic(u):
    return sum(2-chi(plaquette(u,x,y)) for x in range(2) for y in range(3))
def mover(u,e,t):
    v=u[:];v[e]=M[t][u[e]]
    return v
def emit(tag,**values):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in values.items())+"|json=0")
count=0;badraw=0
for sample in range(96):
    n=(sample**3*981739+sample*9973+17)%(6**12)
    u=[(n//(6**j))%6 for j in range(12)]
    assert observable(tx(u))==-observable(u)
    assert magnetic(tx(u))==magnetic(u)
    assert tx(tx(u))==u
    for e in range(12):
        for t in T:
            mapped=mover(tx(u),(e+3)%6 if e<6 else 6+(e-6+3)%6,t)
            assert tx(mover(u,e,t))==mapped
    for k in range(6):
        h=[(sample+3*s+k*s*s+2*k)%6 for s in range(6)]
        v=gauge(u,h)
        assert observable(u)==observable(v)
        assert magnetic(u)==magnetic(v)
        assert all(chi(plaquette(u,x,y))==chi(plaquette(v,x,y))
                   for x in range(2) for y in range(3))
        badraw+=int(chi(u[0])!=chi(v[0]))
        count+=1
assert count==576 and badraw>0
assert (6**7+3*2**7+2*3**7)//6==47449
emit("SELECTION_2X3",gauge_orbits=47449,raw_samples=96,
     local_gauge_checks=count,negative_raw_link_witnesses=badraw,
     x_translation_odd="EXACT",electric_covariant="EXACT",
     magnetic_covariant="EXACT",plaquette_difference_gauge_invariant="EXACT",
     first_excitation_overlap="OPEN")
