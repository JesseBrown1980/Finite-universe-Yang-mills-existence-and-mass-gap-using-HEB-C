#!/usr/bin/env python3
"""Exact moment formula for Schur center of full-Q polynomial Chebyshev trial.

Uses independent binomial Chebyshev coefficients, not the source's
three-term polynomial recurrence. Verifies moments 0..31 on an exact toy Q
and rejects deletion of the shell4->shell5 adjacency edge.
"""
from itertools import combinations
from math import comb

A=((4,-1,0,0),(-1,5,-2,0),(0,-2,6,-1),(0,0,-1,7))
R=((0,0),(0,0),(3,1),(0,0))
F=((5,1),(1,8))
GLOW=1
HIGH=10


def need(ok,why):
    if not ok:
        raise SystemExit("Y137_MOMENT_REFUSE|reason="+why+"|json=0")


def intpower(x,n):
    need(n>=0,"negative_power")
    y=1
    while n:
        if n%2:
            y*=x
        x*=x
        n//=2
    return y


def plus(a,b):
    return tuple(tuple(x+y for x,y in zip(rx,ry)) for rx,ry in zip(a,b))


def minus(a,b):
    return tuple(tuple(x-y for x,y in zip(rx,ry)) for rx,ry in zip(a,b))


def times(a,k):
    return tuple(tuple(k*x for x in row) for row in a)


def multiply(a,b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(len(b)))
                       for j in range(len(b[0]))) for i in range(len(a)))


def transpose(a):
    return tuple(tuple(a[i][j] for i in range(len(a)))
                 for j in range(len(a[0])))


def det(a):
    n=len(a)
    if not n:
        return 1
    b=[list(row) for row in a]
    sign=1
    prev=1
    for k in range(n-1):
        if not b[k][k]:
            ix=next((j for j in range(k+1,n) if b[j][k]),None)
            if ix is None:
                return 0
            b[k],b[ix]=b[ix],b[k]
            sign=-sign
        pivot=b[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                v=pivot*b[i][j]-b[i][k]*b[k][j]
                need(v%prev==0,"bad_Bareiss")
                b[i][j]=v//prev
        for i in range(k+1,n):
            b[i][k]=0
        prev=pivot
    return sign*b[-1][-1]


def psd(a):
    n=len(a)
    need(all(a[i][j]==a[j][i] for i in range(n) for j in range(n)),
         "non_symmetric_matrix")
    for k in range(1,n+1):
        for ix in combinations(range(n),k):
            if det([[a[i][j] for j in ix] for i in ix])<0:
                return False
    return True


def adj(a):
    n=len(a)
    co=tuple(tuple((1 if (i+j)%2==0 else -1)*det(
             [[a[ii][jj] for jj in range(n) if jj!=j]
              for ii in range(n) if ii!=i])
             for j in range(n)) for i in range(n))
    return transpose(co)


def polynomial(n,g,h):
    """Independent closed-form T_n/binomial expansion in the variable X."""
    need(n>0 and 0<g<h,"invalid_Cheb")
    s=g+h
    d=h-g
    out=[0]*(n+1)
    for k in range((n//2)+1):
        m=n-2*k
        if m==0:
            ct=-1 if k%2 else 1
        else:
            num=n*comb(n-k,k)*(1<<(m-1))
            need(num%(n-k)==0,"binomial_coefficient_exact")
            ct=num//(n-k)
            if k%2:
                ct=-ct
        for j in range(m+1):
            out[j]+=ct*intpower(d,n-m)*comb(m,j)*intpower(s,m-j)*intpower(-2,j)
    need(out[0]>0 and len(out)==n+1,"bad_Cheb_coeff")
    return out


def poly_square(p):
    out=[0]*(2*len(p)-1)
    for i,a in enumerate(p):
        for j,b in enumerate(p):
            out[i+j]+=a*b
    return out


def moment_table(n,a,r):
    # R* A^k R, k=0..2n-1, exactly 2n small Gram matrices.
    powers=[r]
    for _ in range(2*n):
        powers.append(multiply(a,powers[-1]))
    moments=[multiply(transpose(r),powers[k]) for k in range(2*n)]
    return moments,powers


def weighted_sum(mats,coeff):
    need(len(mats)>=len(coeff),"moment_count")
    z=times(mats[0],0)
    for c,mat in zip(coeff,mats):
        z=plus(z,times(mat,c))
    return z


def certify(n):
    g,h=GLOW,HIGH
    need(psd(minus(A,times(((1,0,0,0),(0,1,0,0),
                            (0,0,1,0),(0,0,0,1)),g))),
         "toy_lower_operator")
    need(psd(minus(times(((1,0,0,0),(0,1,0,0),
                            (0,0,1,0),(0,0,0,1)),h),A)),
         "toy_upper_operator")
    p=polynomial(n,g,h)
    k=p[0]
    q=[-val for val in p[1:]]
    squared=poly_square(p)
    need(squared[0]==k*k,"bad_Cheb_normalization")
    c=[-val for val in squared[1:]]   # (K²-P(X)²)/X
    need(len(c)==2*n,"exact_center_polynomial_degree")
    moments,powers=moment_table(n,A,R)
    corr=weighted_sum(moments,c)
    center=minus(times(F,k*k),corr)
    # Independent direct variational evaluation via explicitly constructed
    # polynomial trial Y_n=-Q(A)R/K (original Y=0, B=-R).
    qvec=weighted_sum(powers,q)
    direct=plus(minus(times(F,k*k),
                      times(multiply(transpose(R),qvec),2*k)),
                multiply(transpose(qvec),multiply(A,qvec)))
    need(center==direct,"moment_center_vs_direct_variation")
    Pvec=weighted_sum(powers,p)
    need(minus(times(R,k),multiply(A,qvec))==Pvec,
         "fullQ_polynomial_residual")
    da=det(A)
    need(da>0,"Q_inverse_sign")
    snum=minus(times(F,da),multiply(multiply(transpose(R),adj(A)),R))
    # U_n - S = R_n* A^-1 R_n is PSD and <= delta²/g * original Gram.
    above=minus(times(center,da),times(snum,k*k))
    base=multiply(transpose(R),R)
    below=minus(times(base,intpower(h-g,2*n)*da),
                times(above,g))
    need(psd(above) and psd(below),"wholeQ_Cheb_residual_sandwich")
    return len(moments),k


def missing_shell5_negative_control():
    # R starts in coordinate 2. Its second moment sees the edge
    # (2,3) to the exterior site, whereas the first moment does not.
    deleted=[list(row) for row in A]
    deleted[2][3]=0
    deleted[3][2]=0
    def second(a):
        return multiply(transpose(R),multiply(a,multiply(a,R)))
    need(second(A)!=second(tuple(tuple(row) for row in deleted)),
         "omitted_outer_edge_did_not_change_operator_moment")


def flat_reentry_projection_negative_control():
    """Full H powers may visit the removed flat sector and return to Q.

    Thus Q H^2 Q is generally NOT (Q H Q)^2. The exact moments for
    the #137 resolvent must apply Q after every operator multiplication.
    """
    coupling=(0,0,1,0)
    H=((5,)+coupling,)+tuple((coupling[i],)+A[i] for i in range(4))
    raw= multiply(H,H)
    raw_Q_H2_Q=tuple(tuple(raw[i+1][j+1] for j in range(4))
                    for i in range(4))
    true_Q_H_Q_squared=multiply(A,A)
    need(raw_Q_H2_Q!=true_Q_H_Q_squared,
         "flat_sector_reentry_undetected")
    direct=multiply(transpose(R),multiply(true_Q_H_Q_squared,R))
    wrong=multiply(transpose(R),multiply(raw_Q_H2_Q,R))
    need(direct!=wrong,"raw_full_operator_moments_wrongly_accepted")


def main():
    missing_shell5_negative_control()
    flat_reentry_projection_negative_control()
    for n in (1,4,8,16):
        count,k=certify(n)
        print("Y137_MOMENT_POINT|degree="+str(n)+
              "|complete_operator_moments="+str(count)+
              "|exact_center_matches_direct=1"+
              "|fullQ_Schur_Loewner_bounds=1|json=0",flush=True)
    print("Y137_MOMENT_VERDICT|degree16_moments=32"+
          "|Chebyshev_coefficients=INDEPENDENT_BINOMIAL_FORM"+
          "|shell5_edge_omission=REJECTED"+
          "|actual_3x4_fullQ_moments=NOT_COMPUTED"+
          "|actual_Wilson_weight=HOLD|json=0",flush=True)


if __name__=="__main__":
    main()
