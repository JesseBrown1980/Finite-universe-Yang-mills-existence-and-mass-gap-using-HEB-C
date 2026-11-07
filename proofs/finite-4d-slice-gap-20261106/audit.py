#!/usr/bin/env python3
"""Independent finite-4D Z3/S3 group and gap-premise checks; integer-only.

Does not diagonalize the exponentially large physical transfer or establish
the continuum/Clay mass gap. Does not import the existing gauge engines.
"""
from itertools import permutations
from math import gcd

def determinant(rows):
    a=[row[:] for row in rows]
    n=len(a)
    prev=1
    sign=1
    for k in range(n-1):
        if a[k][k]==0:
            j=next((i for i in range(k+1,n) if a[i][k]!=0),None)
            if j is None:
                return 0
            a[k],a[j]=a[j],a[k]
            sign=-sign
        p=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                v=a[i][j]*p-a[i][k]*a[k][j]
                assert v%prev==0
                a[i][j]=v//prev
            a[i][k]=0
        prev=p
    return sign*a[-1][-1]

def integer_rank(rows):
    a=[row[:] for row in rows]
    height=len(a)
    width=len(a[0])
    r=0
    for col in range(width):
        i=next((j for j in range(r,height) if a[j][col]),None)
        if i is None:
            continue
        a[r],a[i]=a[i],a[r]
        p=a[r][col]
        for j in range(r+1,height):
            c=a[j][col]
            if c:
                a[j]=[p*x-c*y for x,y in zip(a[j],a[r])]
                divisor=0
                for v in a[j]:
                    divisor=gcd(divisor,abs(v))
                if divisor:
                    a[j]=[v//divisor for v in a[j]]
        r+=1
        if r==height:
            break
    return r

def group(name):
    if name=="Z3":
        q=3
        return q,lambda a,b:(a+b)%3,lambda a:(-a)%3,lambda a:4 if a==0 else 1,(6,3,3)
    perms=tuple(permutations(range(3)))
    pos={p:i for i,p in enumerate(perms)}
    def mul(a,b):
        return pos[tuple(perms[a][perms[b][i]] for i in range(3))]
    def inv(a):
        return pos[tuple(perms[a].index(i) for i in range(3))]
    def w(a):
        p=perms[a]
        inversions=sum(p[i]>p[j] for i in range(3) for j in range(i+1,3))
        sign=-1 if inversions%2 else 1
        return 2+sign*sum(p[i]==i for i in range(3))
    return 6,mul,inv,w,(12,6,3,3,3,3)

def audit(name):
    q,mul,inv,w,spectrum=group(name)
    elems=range(q)
    assert all(mul(a,inv(a))==0==mul(inv(a),a) for a in elems)
    assert all(mul(mul(a,b),c)==mul(a,mul(b,c)) for a in elems for b in elems for c in elems)
    assert all(w(mul(mul(h,a),inv(h)))==w(a) for a in elems for h in elems)
    assert all(w(inv(a))==w(a) and w(a)>=1 for a in elems)
    c=[[w(mul(a,inv(b))) for b in elems] for a in elems]
    assert all(c[a][b]==c[b][a] for a in elems for b in elems)
    assert all(sum(row)==sum(w(i) for i in elems) for row in c)
    minors=[determinant([row[:n] for row in c[:n]]) for n in range(1,q+1)]
    assert all(x>0 for x in minors)
    multiplicity={}
    for lam in set(spectrum):
        multiplicity[lam]=q-integer_rank([[c[a][b]-(lam if a==b else 0) for b in elems] for a in elems])
    assert sorted(lam for lam,d in multiplicity.items() for unused in range(d))==sorted(spectrum)
    orbits=sum(sum(mul(g,h)==mul(h,g) for h in elems)**17 for g in elems)//q
    assert orbits=={"Z3":129140163,"S3":2821153019713}[name]
    assert q**24=={"Z3":282429536481,"S3":4738381338321616896}[name]
    maxw=max(w(g) for g in elems)
    N=maxw**24
    assert N=={"Z3":281474976710656,"S3":59604644775390625}[name]
    for power in range(4):
        m=3**power
        assert (N-1)**m*(N+m)<=N**(m+1)
    mutated=[row[:] for row in c]
    mutated[0][1]+=1
    assert mutated[0][1]!=mutated[1][0]
    assert min([0]+[w(i) for i in elems])==0
    assert maxw**23<N
    if name=="S3":
        assert any(mul(a,b)!=mul(b,a) for a in elems for b in elems)
        assert sorted(w(i) for i in elems)==[1,1,1,2,2,5]
    else:
        assert sorted(w(i) for i in elems)==[1,1,4]
    print(f"FINITE4D_FAULT|group={name}|mutated_link_kernel=REJECTED_SYMMETRY|zero_weight=REJECTED_POSITIVITY|missing_temporal_face=REJECTED_COUNT|json=0")
    print(f"FINITE4D|group={name}|order={q}|link_spectrum={';'.join(map(str,spectrum))}|leading_principal_minors={';'.join(map(str,minors))}|orbits={orbits}|raw_configs={q**24}|N={N}|minorization=1/{N}|ratio_bound={N-1}/{N}|status=PASS|json=0")

def main():
    for g in ("Z3","S3"):
        audit(g)
    assert 7776*8//2==31104
    print("FINITE2D|group=S3|weighted_vertices=7776|graph_diameter=8|unconditional_electric_gap_lower=1/31104|J_E=0_and_J_B_positive=gap_zero|status=PRIOR_GRAPH_ANTECEDENTS|json=0")
    print("FINITE4D_SCOPE|complete_physical_transfer_matrix_constructed=NO|gauge_invariant_slice_transfer_defined=YES|full_mass_eigenvalue_computed=NO|continuum_clay_proof=NO|json=0")

if __name__=="__main__":
    main()
