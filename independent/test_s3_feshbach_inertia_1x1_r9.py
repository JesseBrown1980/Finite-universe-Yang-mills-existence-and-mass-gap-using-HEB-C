#!/usr/bin/env python3
"""Finite S3 1x1, r=9, exact integer full vs eight-flat Schur inertia.
For issue #133 as a method control only: NOT the 3x4 numerical first gap.
Post-exploration; no floats, fractions, JSON, or uncertified large solve.
"""
from itertools import permutations
import sys

RED=("incorrect_orbits","wrong_magnetic","unweighted_schur",
     "omit_nonflat","false_gap","wrong_count")
red=""
if len(sys.argv)>2 or (len(sys.argv)==2 and
  (not sys.argv[1].startswith("sabotage=") or sys.argv[1][9:] not in RED)):
    raise SystemExit("usage: test_s3_feshbach_inertia.py [sabotage=NAME]")
if len(sys.argv)==2:
    red=sys.argv[1][9:]

def check(cond,name):
    if not cond:
        print("FAILED|"+name+"|json=0")
        raise SystemExit(1)

def emit(label,**kw):
    print(label+"|"+"|".join(str(k)+"="+str(v) for k,v in kw.items())+"|json=0")

def mult(a,b):
    return tuple(a[b[i]] for i in range(3))
def inv(a):
    return tuple(a.index(i) for i in range(3))
def conj(g,a):
    return mult(mult(g,a),inv(g))
def chi(a):
    return sum(int(a[i]==i) for i in range(3))-1
def comm(a,b):
    return mult(mult(mult(a,b),inv(a)),inv(b))

def build():
    G=tuple(permutations(range(3)))
    order={x:i for i,x in enumerate(G)}
    key=lambda ab:6*order[ab[0]]+order[ab[1]]
    classes=sorted({frozenset((conj(g,a),conj(g,b)) for g in G)
                    for a in G for b in G},key=lambda o:min(key(v) for v in o))
    where={v:i for i,o in enumerate(classes) for v in o}
    w=[len(o) for o in classes]
    n=len(classes)
    if red=="incorrect_orbits":
        check(n==12,"RED_incorrect_orbits")
    check(n==11 and sum(w)==36,"eleven_physical_orbits")
    trans=[g for g in G if chi(g)==0]
    check(len(trans)==3,"three_electric_moves")
    H=[[0]*n for _ in range(n)]
    M=[]
    for i,o in enumerate(classes):
        a,b=min(o,key=key)
        H[i][i]+=6
        for t in trans:
            H[i][where[(mult(t,a),b)]]-=1
            H[i][where[(a,mult(t,b))]]-=1
        m=2-chi(comm(a,b))
        M.append(m)
        H[i][i]+=9*m
    if red=="wrong_magnetic":
        check(set(M)=={0,2},"RED_wrong_magnetic")
    check(set(M)=={0,3} and M.count(0)==8 and M.count(3)==3,
          "eight_flat_three_nonflat")
    check(all(w[i]*H[i][j]==w[j]*H[j][i]
              for i in range(n) for j in range(n)),"weighted_self_adjoint")
    return H,w,M

def determinant(A):
    n=len(A)
    if n==0:
        return 1
    z=[row[:] for row in A]
    last=1
    sign=1
    for k in range(n-1):
        if z[k][k]==0:
            pivot=next((i for i in range(k+1,n) if z[i][k]),None)
            if pivot is None:
                return 0
            z[k],z[pivot]=z[pivot],z[k]
            sign=-sign
        p=z[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                a=z[i][j]*p-z[i][k]*z[k][j]
                check(a%last==0,"Bareiss_integral")
                z[i][j]=a//last
        for i in range(k+1,n):
            z[i][k]=0
        last=p
    return sign*z[n-1][n-1]

def inertia(A):
    n=len(A)
    check(all(A[i][j]==A[j][i] for i in range(n) for j in range(n)),
          "exact_symmetric_pencil")
    prev=1
    negative=0
    for k in range(1,n+1):
        v=determinant([row[:k] for row in A[:k]])
        check(v!=0,"inertia_nonzero_leading_minor")
        negative+=int((v<0)!=(prev<0))
        prev=v
    return negative

def schur_and_full(H,w,M,a,b):
    flat=[i for i,m in enumerate(M) if m==0]
    high=[i for i,m in enumerate(M) if m!=0]
    order=flat+high
    full=[[w[order[i]]*(b*H[order[i]][order[j]]-a*int(i==j))
           for j in range(11)] for i in range(11)]
    D=[row[8:] for row in full[8:]]
    C=[row[:8] for row in full[:8]]
    F=[row[8:] for row in full[:8]]
    den=determinant(D)
    check(den>0 and inertia(D)==0,"nonflat_positive")
    def cof(i,j):
        x=[[D[u][v] for v in range(3) if v!=j]
           for u in range(3) if u!=i]
        return x[0][0]*x[1][1]-x[0][1]*x[1][0]
    adj=[[(-1 if (i+j)%2 else 1)*cof(j,i)
          for j in range(3)] for i in range(3)]
    check(all(sum(D[i][k]*adj[k][j] for k in range(3))
              ==den*int(i==j) for i in range(3) for j in range(3)),
          "exact_noflat_adjugate")
    if red=="unweighted_schur":
        F[0][0]+=1
    T=[[den*C[i][j]-sum(F[i][u]*adj[u][v]*F[j][v]
          for u in range(3) for v in range(3)) for j in range(8)]
          for i in range(8)]
    if red=="omit_nonflat":
        T=[[den*C[i][j] for j in range(8)] for i in range(8)]
    if red=="unweighted_schur":
        check(T==[[den*C[i][j] for j in range(8)]
                      for i in range(8)],"RED_unweighted_schur")
    got=inertia(T)
    truth=inertia(full)
    check(got==truth,"exact_Schur_matches_full_inertia")
    return got

def residual_count(H,w,M,a,b):
    ix=[i for i,m in enumerate(M) if m==0]+[i for i,m in enumerate(M) if m!=0]
    A0=[[w[ix[i]]*(b*H[ix[i]][ix[j]]-a*int(i==j))
         for j in range(11)] for i in range(11)]
    P=[row[:8] for row in A0[:8]]
    A=[row[8:] for row in A0[8:]]
    F=[row[:8] for row in A0[8:]]
    alpha=min(A[i][i]-sum(abs(A[i][j]) for j in range(3) if j!=i)
              for i in range(3))
    check(alpha>0,"Gershgorin_positive")
    den=A[0][0]*A[1][1]*A[2][2]
    check(den>0,"positive_diagonal_inverse")
    X=[[F[i][j]*(den//A[i][i]) for j in range(8)] for i in range(3)]
    R=[[den*F[i][j]-sum(A[i][k]*X[k][j] for k in range(3))
        for j in range(8)] for i in range(3)]
    check(any(v!=0 for row in R for v in row),"nonzero_residual_test")
    upper=[[den*den*P[i][j]-
            den*sum(F[k][i]*X[k][j]+X[k][i]*F[k][j] for k in range(3))+
            sum(X[k][i]*A[k][t]*X[t][j] for k in range(3) for t in range(3))
            for j in range(8)] for i in range(8)]
    lower=[[alpha*upper[i][j]-sum(R[k][i]*R[k][j] for k in range(3))
            for j in range(8)] for i in range(8)]
    got=inertia(upper)
    check(got==inertia(lower)==inertia(A0),
          "rigorous_Schur_residual_sandwich")
    return alpha,got

def main():
    H,w,M=build()
    emit("FESHBACH_SOURCE",gauge_group="S3",lattice="1x1",JE=1,r=9,
         physical_orbits=11,flat=8,nonflat=3,
         approach="WEIGHTED_SYMMETRIC_INTEGER_SCHUR")
    thresholds=((2,1,0),(2112,1000,0),(2113,1000,1),
      (3499,1000,1),(3500,1000,2),(5440,1000,2),
      (5441,1000,3),(8389,1000,6),(8390,1000,7),
      (9606,1000,7),(9607,1000,8),(20,1,8))
    for a,b,expected in thresholds:
        c=schur_and_full(H,w,M,a,b)
        if red=="wrong_count" and a==3500:
            check(c==1,"RED_wrong_count")
        check(c==expected,"frozen_12_count")
        emit("FESHBACH_COUNT",threshold=str(a)+"/"+str(b),
             below=c,full_inertia="MATCH_8X8_SCHUR")
    for a,b,expected in ((2,1,0),(5,2,1),(29,10,1),(7,2,2),(4,1,2)):
        alpha,c=residual_count(H,w,M,a,b)
        check(c==expected,"frozen_5_residual_count")
        emit("FESHBACH_RESIDUAL",threshold=str(a)+"/"+str(b),
             below=c,Gershgorin_lower=alpha,
             upper_lower_inertia="MATCH_WITH_NONZERO_RESIDUAL")
    if red=="false_gap":
        check(1000==1386,"RED_false_gap")
    emit("FESHBACH_GAP",lattice="1x1",r=9,
         first_gap_lower="1386/1000",first_gap_upper="1388/1000",
         E1_in="[2112,2113]/1000",E2_in="[3499,3500]/1000")
    emit("FESHBACH_SCOPE",method="READY_FOR_3X4_INTERVAL_RESOLVENT",
         original_3x4_E2_minus_E1="OPEN",original_3x4_Perron="UNCHANGED",
         physical_volume="FINITE",continuum="OPEN")

if __name__=="__main__":
    main()
