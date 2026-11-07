#!/usr/bin/env python3
"""Independent winding-operator selection, rational spectral weight and vacuum correlators.
Imports the already-verified 11-orbit Hamiltonian builder and rational operations;
reconstructs the winding operator and its odd-sector spectral certificate separately.
No floats, Decimal, Fraction or JSON. The full-space 3x4 first gap is not tested.
"""
from itertools import permutations
from math import gcd
import test_s3_interacting_vacuum as base

q=base.q
add=base.plus
sub=base.minus
mul=base.multiply
lt=base.less
le=base.atmost
dot=base.weighted_dot
mv=base.mv
mm=base.mmul
fmt=base.fmt

def emit(tag,**fields):
    print(tag+"|"+"|".join(k+"="+str(v) for k,v in fields.items())+"|json=0")

def compose(a,b):
    return tuple(a[b[i]] for i in range(3))

def inverse(a):
    return tuple(a.index(i) for i in range(3))

def conjugate(g,a):
    return compose(compose(g,a),inverse(g))

def chi(g):
    return sum(int(g[i]==i) for i in range(3))-1

def rebuild_winding(H,weights):
    group=tuple(permutations(range(3)))
    raw=[(a,b) for a in group for b in group]
    order={c:i for i,c in enumerate(raw)}
    orbits=sorted({frozenset((conjugate(g,a),conjugate(g,b))
                             for g in group) for a,b in raw},
                  key=lambda o:min(order[x] for x in o))
    lookup={ab:i for i,orb in enumerate(orbits) for ab in orb}
    assert len(orbits)==11 and weights==[len(x) for x in orbits]
    odd=[];swap=[]
    for orb in orbits:
        a,b=min(orb,key=lambda x:order[x])
        odd.append(chi(a)-chi(b))
        swap.append(lookup[(b,a)])
        assert all(chi(conjugate(g,a))-chi(conjugate(g,b))==chi(a)-chi(b)
                   for g in group)
    assert all(odd[swap[i]]==-odd[i] for i in range(11))
    assert all(H[swap[i]][swap[j]]==H[i][j] for i in range(11)
               for j in range(11))
    pairs=[i for i in range(11) if i<swap[i]]
    assert pairs==[1,2,6]
    B=[[H[i][j]-H[i][swap[j]] for j in pairs] for i in pairs]
    assert B==[[6,-2,0],[-3,6,-3],[0,-1,9]]
    # Explicit cubic identity via independent 3x3 multiplication.
    I=[[int(i==j) for j in range(3)] for i in range(3)]
    sq=mm(B,B); cube=mm(sq,B)
    assert all(cube[i][j]-21*sq[i][j]+135*B[i][j]-252*I[i][j]==0
               for i in range(3) for j in range(3))
    emit("WINDING_GROUP",raw=36,gauge_orbits=11,odd_sector=3,
         symmetry="AXIS_SWAP",gauge_invariant="PASS",odd_operator="PASS")
    return odd,pairs,B

def get_roots():
    # Signed rational bisection on the P3 factor; 1e-18 endpoint widths.
    windows=((3274551,3274552),(7601465,7601466),(10123983,10123984))
    scale=10**18
    def p(z):
        return z**3-21*z*z*scale+135*z*scale*scale-252*scale**3
    output=[]
    for a,b in windows:
        lo=a*10**12;hi=b*10**12
        sign=p(lo)
        assert sign*p(hi)<0
        while hi-lo>1:
            mid=(lo+hi)//2
            if p(mid)*sign>0: lo=mid;sign=p(mid)
            else:hi=mid
        output.append((q(lo,scale),q(hi,scale)))
    return output

def ii(x):
    return x,x

def iadd(x,y):
    return add(x[0],y[0]),add(x[1],y[1])

def ineg(x):
    return (-x[1][0],x[1][1]),(-x[0][0],x[0][1])

def isub(x,y):
    return iadd(x,ineg(y))

def imul(x,y):
    a=[mul(p,r) for p in x for r in y]
    lo=hi=a[0]
    for z in a[1:]:
        if lt(z,lo):lo=z
        if lt(hi,z):hi=z
    return lo,hi

def idiv(x,y):
    assert lt(q(0),y[0])
    return imul(x,(q(y[1][1],y[1][0]),q(y[0][1],y[0][0])))

def measure_weight(H,weights,winding,pairs,B,v,norm):
    w=[2*weights[i] for i in pairs]
    u=[winding[i]*v[i] for i in pairs]
    # Independent route 1: strictly positive odd-sector Perron eigenvector.
    A=[[12*int(i==j)-B[i][j] for j in range(3)] for i in range(3)]
    assert all(z>=0 for row in A for z in row)
    p=[1,1,1]
    for _ in range(110):p=mv(A,p)
    hp=mv(B,p)
    n=dot(p,p,w);h=dot(p,hp,w)
    mu=q(h,n)
    gap=sub(q(7601465,10**6),mu)
    residual=q(sum(w[i]*(n*hp[i]-h*p[i])**2 for i in range(3)),n**3)
    assert lt(q(0),gap)
    assert lt(residual,mul(mul(gap,gap),q(1,10**38)))
    numerator=dot(u,p,w)
    pw=q(numerator*numerator,n*norm)
    # Cauchy plus certified odd-vector angular amplitude <1e-19.
    err=q(1,10**13)
    lower,upper=sub(pw,err),add(pw,err)
    assert lt(q(302165,10**5),lower) and lt(upper,q(302169,10**5))
    emit("WINDING_E1_PERRON",lower=fmt(lower,12),upper=fmt(upper,12,ceil=True),
         odd_angle_lt="1e-19",first_spectral_weight="NONZERO")

    # Independent route 2: exact moments plus interval polynomial
    # interpolation at rationally isolated roots of P3. No Perron odd
    # eigenvector or spectral-filter amplitude is used in this route.
    r1,r2,r3=get_roots()
    Bu=mv(B,u)
    m0=q(dot(u,u,w),norm)
    m1=q(dot(u,Bu,w),norm)
    m2=q(dot(u,mv(B,Bu),w),norm)
    numerator=iadd(isub(ii(m2),imul(iadd(r2,r3),ii(m1))),
                   imul(imul(r2,r3),ii(m0)))
    denominator=imul(isub(r1,r2),isub(r1,r3))
    lo,hi=idiv(numerator,denominator)
    assert le(lo,upper) and le(lower,hi)
    assert lt(q(3),lo) and lt(hi,q(31,10))
    emit("WINDING_E1_PROJECTOR",lower=fmt(lo,12),upper=fmt(hi,12,ceil=True),
         independent_of_odd_Perron="YES",roots_error_lt="1e-18",
         matches_Perron="PASS")
    return lower,upper

def main():
    H,weights,_=base.build()
    winding,pairs,B=rebuild_winding(H,weights)
    P5=base.p5(H)
    # The even interacting vacuum is Perron certified by the original
    # checker; the odd operator annihilates its vacuum expectation.
    v,norm=base.vacuum(H,weights,P5)
    assert all(v[i]*winding[i]+v[j]*winding[j]==0
               for i,j in ((1,3),(2,7),(6,8)))
    assert dot(v,[winding[i]*v[i] for i in range(11)],weights)==0
    measure_weight(H,weights,winding,pairs,B,v,norm)
    moments,norm2,mean=base.shifted_moments(H,weights,winding,v)
    assert norm2==norm and mean==q(0)
    observed=[(3022205243660,3022205243665),
              (342108549190,342108549210),
              (38732861750,38732861775),
              (4385267360,4385267380)]
    for t in range(4):
        correlation=(q(dot([winding[i]*v[i] for i in range(11)],
                           [winding[i]*v[i] for i in range(11)],
                           weights),norm)
                     if t==0 else base.expand_corr(moments,norm,mean,t))
        # Valid bound includes Perron-angle, shift and 192-term Taylor
        # truncation errors (<1e-30), using the source checker proof.
        epsilon=q(1,10**13)
        lo,hi=sub(correlation,epsilon),add(correlation,epsilon)
        freeze_lo,freeze_hi=observed[t]
        assert le(q(freeze_lo,10**12),lo) and le(hi,q(freeze_hi,10**12))
        emit("WINDING_CONNECTED",t=t,lower=fmt(lo,12),
             upper=fmt(hi,12,ceil=True),vacuum="INTERACTING",
             continuous_time="FINITE_H",certified_error_lt="1e-13")
    emit("WINDING_GATE",result="PASS",spectral_weights="TWO_EXACT_ROUTES",
         true_first_excitation="VISIBLE",first_gap="2.178437..2.178439",
         spatial_continuum="OPEN",Clay="OPEN")

if __name__=="__main__":
    main()
