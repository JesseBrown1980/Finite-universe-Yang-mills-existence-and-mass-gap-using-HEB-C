#!/usr/bin/env python3
"""Exact integer Schur/inertia and triadic Neumann certificate (small matrices).

Standalone demonstrator, not a 3x4 calculation. A 12-state graph Hamiltonian
(8 P vacua and 4 Q states) is checked with an exact M-matrix positive
witness, 3^k-term resolvent, rigorous remainder bound, and independent
full-matrix inertia. Dense products do not scale to a 3x4 Hamiltonian.
No floats, JSON, or third-party dependencies.
"""
from __future__ import annotations
from math import gcd


def mm(a, b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]


def eye(n):
    return [[int(i==j) for j in range(n)] for i in range(n)]


def det(a):
    """Integer determinant via fraction-free Bareiss and row swaps."""
    n=len(a)
    if n==0:
        return 1
    m=[row[:] for row in a]
    sign,prev=1,1
    for k in range(n-1):
        if m[k][k]==0:
            pivot=next((j for j in range(k+1,n) if m[j][k]),None)
            if pivot is None:
                return 0
            m[k],m[pivot]=m[pivot],m[k]
            sign=-sign
        pk=m[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                z=m[i][j]*pk-m[i][k]*m[k][j]
                assert z%prev==0
                m[i][j]=z//prev
        for i in range(k+1,n):
            m[i][k]=0
        prev=pk
    return sign*m[-1][-1]


def inertia(a):
    if any(a[i][j]!=a[j][i] for i in range(len(a)) for j in range(len(a))):
        raise ValueError('NON_SYMMETRIC')
    neg,signprev=0,1
    for k in range(1,len(a)+1):
        z=det([row[:k] for row in a[:k]])
        if z==0:
            raise ValueError('ZERO_PIVOT_UNCERTIFIED')
        sign=1 if z>0 else -1
        neg+=sign!=signprev
        signprev=sign
    return int(neg)


def adj_row_norm(a):
    n=len(a)
    sums=[]
    for i in range(n):
        s=0
        for j in range(n):
            # adj[i,j] is the cofactor of a[j,i], up to a sign.
            minor=[[a[r][c] for c in range(n) if c!=i]
                   for r in range(n) if r!=j]
            s+=abs(det(minor))
        sums.append(s)
    return max(sums,default=0)


def triadic_sum(cnum, a, k):
    """Return (S,T): sum_(n=0..T-1)(cnum/a)^n = S/a^(T-1), T=3^k."""
    n=len(cnum)
    s=eye(n)
    v=[row[:] for row in cnum]
    t=1
    for _ in range(k):
        vv=mm(v,v)
        factor=[[pow(a,2*t)*int(i==j)+pow(a,t)*v[i][j]+vv[i][j]
                 for j in range(n)] for i in range(n)]
        s=mm(s,factor)
        v=mm(vv,v)
        t*=3
    return s,t


def schur_cert(h, p, znum, zden, d, k):
    """Certify eigenvalue count below znum/zden, or fail closed."""
    n=len(h)
    if not(1<=p<n and zden>0 and k>=0 and len(d)==n-p
           and all(x>0 for x in d)):
        raise ValueError('INVALID_ARGUMENTS')
    if any(len(row)!=n for row in h):
        raise ValueError('NON_SQUARE')
    if any(h[i][j]!=h[j][i] for i in range(n) for j in range(n)):
        raise ValueError('NON_SYMMETRIC')
    K=[[zden*h[i][j]-znum*int(i==j) for j in range(n)]
       for i in range(n)]
    q=n-p
    A=[row[p:] for row in K[p:]]
    B=[row[p:] for row in K[:p]]
    a=max(A[i][i] for i in range(q))
    if a<=0:
        raise ValueError('NON_POSITIVE_A')
    cn=[[a*int(i==j)-A[i][j] for j in range(q)] for i in range(q)]
    if any(x<0 for row in cn for x in row):
        raise ValueError('NOT_M_MATRIX_UNCERTIFIED')
    ad=[sum(x*y for x,y in zip(row,d)) for row in A]
    if any(x<=0 for x in ad):
        raise ValueError('NON_POSITIVE_PERRON_RESIDUAL')
    j=0
    for i in range(q):
        if ad[i]*d[j]<ad[j]*d[i]:
            j=i
    dn,dd=ad[j],d[j]
    common=gcd(dn,dd)
    dn//=common
    dd//=common
    alnum=a*dd-dn
    if not(0<=alnum<a*dd):
        raise ValueError('CONTRACTION_UNCERTIFIED')
    sn,T=triadic_sum(cn,a,k)
    bb=mm(mm(B,sn),[list(row) for row in zip(*B)])
    apow=pow(a,T)
    Z=[[apow*K[i][j]-bb[i][j] for j in range(p)] for i in range(p)]
    determinant=det(Z)
    if determinant==0:
        raise ValueError('SINGULAR_APPROX_UNCERTIFIED')
    adj=adj_row_norm(Z)
    left=max(sum(abs(bij)*di for bij,di in zip(row,d)) for row in B)
    right=sum(sum(abs(x) for x in row) for row in B)
    # Integer rearrangement of ||S_T^-1||_inf ||S-S_T||_inf < 1:
    lhs=adj*left*right*pow(alnum,T)*dd
    rhs=abs(determinant)*pow(dd,T)*dn
    if not lhs<rhs:
        raise ValueError('REMAINDER_TOO_LARGE_UNCERTIFIED')
    return dict(count=inertia(Z), steps=T, denom_power=T,
                upper_residual_num=alnum,upper_residual_den=a*dd,
                inertia_margin_pass=1, full_dim=n, p_dim=p,q_dim=q)


def toy():
    n=12
    h=[[0]*n for _ in range(n)]
    def edge(i,j):
        h[i][i]+=1
        h[j][j]+=1
        h[i][j]-=1
        h[j][i]-=1
    for i in range(8):
        edge(i,8+i%4)
    for i in range(4):
        edge(8+i,8+(i+1)%4)
    for i in range(8,12):
        h[i][i]+=20
    return h


def main():
    # Rebuild 3^k-term sums independently, without the ternary recursion.
    cn=[[1,1],[0,1]]
    a0=3
    for k0 in range(4):
        got,T=triadic_sum(cn,a0,k0)
        summ=[[0,0],[0,0]]
        power=eye(2)
        for step in range(T):
            scale=pow(a0,T-1-step)
            for i in range(2):
                for j in range(2):
                    summ[i][j]+=power[i][j]*scale
            power=mm(power,cn)
        assert got==summ
        print('TRIADIC_IDENTITY|k='+str(k0)+'|T='+str(T)+'|exact=PASS|json=0')
    h=toy()
    for z in (904,906,912,914,922):
        predicted=schur_cert(h,8,z,1000,[1]*4,2)
        truth=inertia([[1000*h[i][j]-z*int(i==j) for j in range(12)]
                       for i in range(12)])
        assert truth==predicted['count']
        print('SCHUR_TOY|threshold_milli='+str(z)+'|'+
              '|'.join(f'{x}={y}' for x,y in predicted.items())+
              '|independent_direct_inertia='+str(truth)+'|json=0')
    a=schur_cert(h,8,906,1000,[1]*4,2)['count']
    b=schur_cert(h,8,912,1000,[1]*4,2)['count']
    assert (a,b)==(1,1)
    print('SCHUR_TOY_GAP|first_gap_gt=6/1000|count_at_906=1|count_at_912=1|scope=12_state_toy_not_S3|json=0')
    for mut in ('bad_witness','bad_sign','insufficient_steps'):
        try:
            if mut=='bad_witness':
                schur_cert(h,8,906,1000,[0]*4,2)
            elif mut=='bad_sign':
                bad=[row[:] for row in h]
                bad[8][9]=1
                bad[9][8]=1
                schur_cert(bad,8,906,1000,[1]*4,2)
            else:
                schur_cert(h,8,906,1000,[1]*4,0)
        except ValueError as e:
            print(f'SCHUR_RED|control={mut}|result=REFUSED|reason={e}|json=0')
        else:
            raise AssertionError('mutation accepted: '+mut)


if __name__=='__main__':
    main()
