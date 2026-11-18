#!/usr/bin/env python3
"""Second construction of real signed-mu3 original 8x8 Schur brackets.

Uses four immutable raw HBP files, integer-only fraction-free linear solves,
a separate rational matrix implementation, and exact SHA comparison with the
original Stage D four-moment result. Does not import any original project
source, Schur machinery, acceptance checker, or producer modules.
"""
import hashlib
import os
import sys
from math import gcd

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
SOURCE=(
 ("source","independent/y137-shell4-diagonal-cache-20261114/RESULT-MAGNETIC-CACHE.hbp",
  "6454216973b8e59d65174c7cadc4f22c7dcf0354","Y137_CACHE_POINT"),
 ("mu1","independent/y137-real-Q-moment-20261114/RESULT-MU1.hbp",
  "86abf9611f8b9df5e03e796e81f513cba826c085","Y137_MU1_COMPLETE_POINT"),
 ("mu2","independent/y137-d11-shell5-spill-20261114/RESULT-MU2.hbp",
  "31de869725d0e760e650365d4c386b4b2fd722e6","Y137_D11_MU2_POINT"),
 ("mu3","independent/y137-mu3-real-20261115/RESULT-WORKER1-C-FULL-SIGNED-MU3-TWO-ENERGY-20261116.hbp",
  "1b7afcda7a6f1afe34cb22afcfc8dccde1196e04","Y137_C_MU3_ACCEPT_MATRIX")
)
ZZ=(69909875505,69949729820)
M3_SHA=("62787ba280050e598323eddcc67e0cd6234b8e2cfcb7b7bc65e6275fdfae4763",
        "481f2c6b96cb7a7b756e15e96eb8734538a2b74fcb309ac2103a3e8f0284644d")


def check(c,msg):
    if not c:raise ValueError(msg)


def sha_blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+bytes((0,))+data).hexdigest()


def read_sources():
    out=[]
    for name,path,sha,tag in SOURCE:
        data=open(os.path.join(ROOT,path),"rb").read()
        check(sha_blob(data)==sha,"historical_immutable_"+name)
        records=[]
        for line in data.decode("ascii").splitlines():
            if not line.startswith(tag+"|"):continue
            row={}
            for entry in line.split("|")[1:]:
                k,sep,v=entry.partition("=")
                check(k and sep and k not in row,"bad_source_hbp")
                row[k]=v
            check(row.get("json")=="0","source_hbp_terminator")
            records.append(row)
        check(len(records)==2,"two_frozen_source_rows_"+name)
        check(tuple(int(x["sample_num"]) for x in records)==ZZ,
              "original_two_frozen_energy_order_"+name)
        out.append(records)
    return out


def mat(text):
    rows=[[int(x) for x in row.split(",")] for row in text.split(";")]
    check(len(rows)==8 and all(len(row)==8 for row in rows),"8x8_original_source")
    check(all(rows[i][j]==rows[j][i] for i in range(8) for j in range(8)),
          "original_W_bilinear_symmetry")
    return rows


def digest_matrix(M):
    return hashlib.sha256("|".join(str(x) for row in M for x in row).encode("ascii")).hexdigest()


class Rational:
    __slots__=("n","d")
    def __init__(self,n,d=1):
        check(d!=0,"zero_rational_denominator")
        if d<0:n,d=-n,-d
        k=gcd(abs(n),d)
        self.n=n//k
        self.d=d//k

    def __add__(self,other):
        if not isinstance(other,Rational):other=Rational(other)
        return Rational(self.n*other.d+other.n*self.d,self.d*other.d)

    def __sub__(self,other):
        if not isinstance(other,Rational):other=Rational(other)
        return Rational(self.n*other.d-other.n*self.d,self.d*other.d)

    def __mul__(self,other):
        if not isinstance(other,Rational):other=Rational(other)
        return Rational(self.n*other.n,self.d*other.d)

    def div(self,other):
        if not isinstance(other,Rational):other=Rational(other)
        return Rational(self.n*other.d,self.d*other.n)

    def __neg__(self):
        return Rational(-self.n,self.d)


def asr(x):
    return x if isinstance(x,Rational) else Rational(x)


def Rmat(M):
    return [[asr(x) for x in row] for row in M]


def mm(A,B):
    n=len(A);k=len(B);m=len(B[0])
    check(all(len(row)==k for row in A) and
          all(len(row)==m for row in B),"matrix_multiply_dimension")
    return [[sum((A[i][t]*B[t][j] for t in range(k)),Rational(0))
             for j in range(m)] for i in range(n)]


def sub(A,B):
    return [[asr(A[i][j])-asr(B[i][j]) for j in range(len(A[i]))]
            for i in range(len(A))]


def add(A,B):
    return [[asr(A[i][j])+asr(B[i][j]) for j in range(len(A[i]))]
            for i in range(len(A))]


def multiply(A,s):
    return [[asr(v)*asr(s) for v in row] for row in A]


def plain_mul(A,s):
    return [[v*s for v in row] for row in A]


def plain_sub(A,B):
    return [[a-b for a,b in zip(x,y)] for x,y in zip(A,B)]


def plain_add(A,B):
    return [[a+b for a,b in zip(x,y)] for x,y in zip(A,B)]


def block(A,B,C,D):
    n=len(A)
    check(len(B)==len(C)==len(D)==n,"block_count")
    return [A[i]+B[i] for i in range(n)]+[C[i]+D[i] for i in range(n)]


def solve_fraction_free(A,B):
    # Separate Bareiss elimination with eight simultaneous RHS columns.
    n=len(A);m=len(B[0])
    check(len(B)==n and all(len(x)==n for x in A),"square_system")
    T=[A[i][:]+B[i][:] for i in range(n)]
    prev=1
    for k in range(n-1):
        piv=T[k][k]
        check(piv!=0,"singular_fraction_free_pivot")
        for i in range(k+1,n):
            old=T[i][k]
            for j in range(k+1,n+m):
                v=piv*T[i][j]-old*T[k][j]
                check(v%prev==0,"fraction_free_divisibility")
                T[i][j]=v//prev
            T[i][k]=0
        prev=piv
    check(T[-1][-m-1]!=0,"singular_fraction_free_determinant")
    X=[[Rational(0) for _ in range(m)] for _ in range(n)]
    for i in range(n-1,-1,-1):
        for j in range(m):
            res=Rational(T[i][n+j])
            for k in range(i+1,n):
                res=res-Rational(T[i][k])*X[k][j]
            X[i][j]=res.div(Rational(T[i][i]))
    # Direct exact integer/rational witness of every solved equation.
    for i in range(n):
        for j in range(m):
            lhs=sum((Rational(A[i][k])*X[k][j] for k in range(n)),Rational(0))
            check(lhs.n==B[i][j]*lhs.d,"source_linear_system_replay")
    return X


def fingerprint(A):
    den=1
    for row in A:
        for x in row:
            den=den*x.d//gcd(den,x.d)
    entries=[[x.n*(den//x.d) for x in row] for row in A]
    data=str(den)+"|"+";".join(",".join(str(v) for v in row) for row in entries)
    return den,hashlib.sha256(data.encode("ascii")).hexdigest(),entries


def inertia_exact(A):
    # Sylvester inertia by symmetric rational LDL with nonzero pivots.
    T=[row[:] for row in A]
    n=len(T);neg=0
    for k in range(n):
        p=T[k][k]
        check(p.n!=0,"zero_pivot_in_original_Schur_inertia")
        neg+=int(p.n<0)
        for i in range(k+1,n):
            for j in range(i,n):
                x=T[i][j] - (T[i][k]*T[k][j]).div(p)
                T[i][j]=x
                T[j][i]=x
    return neg


def strict_PD(A):
    # Fraction-free determinant monotone positivity along a fixed ordering.
    n=len(A)
    D=[row[:] for row in A]
    prev=1
    for k in range(n):
        piv=D[k][k]
        check(piv>0,"actual_signed_mu3_localizer_not_strict_PD")
        if k==n-1:break
        for i in range(k+1,n):
            for j in range(k+1,n):
                v=piv*D[i][j]-D[i][k]*D[k][j]
                check(v%prev==0,"localizer_exact_Bareiss")
                D[i][j]=v//prev
            D[i][k]=0
        prev=piv
    return True


def Schur(index,rowset,auth):
    s,m1,m2,m3=(r[index] for r in rowset)
    z=ZZ[index]
    g,h=94068200000-z,468000000000-z
    check(0<g<h,"physical_Q_support_window")
    U0=mat(s["U0"])
    G=mat(s["G0"])
    check(all(v%6==0 for row in G for v in row),"original_mu0_six")
    M0=[[v//6 for v in row] for row in G]
    M1=mat(m1["exact_mu1_8x8"])
    M2=mat(m2["actual_K3_mu2_8x8"])
    M3raw=mat(m3["full_whole_Q_mu3_six"])
    check(all(v%6==0 for row in M3raw for v in row),"signed_mu3_six")
    txt=m3["full_whole_Q_mu3_six"]
    check(hashlib.sha256(txt.encode("ascii")).hexdigest()==
          M3_SHA[index]==m3["matrix_sha256"],"real_signed_mu3_matrix_SHA")
    M3=[[v//6 for v in row] for row in M3raw]
    check(digest_matrix(U0)==s["U_sha256"] and
          digest_matrix(G)==s["G_sha256"] and
          digest_matrix(M0)==m1["wholeQ_mu0_sha256"]==
             m2["actual_K3_mu0_sha256"] and
          digest_matrix(M1)==m1["wholeQ_mu1_sha256"]==
             m2["actual_K3_mu1_sha256"] and
          digest_matrix(M2)==m2["actual_K3_mu2_sha256"],
          "original_signed_8x8_matrix_source_SHA")
    lo11=plain_sub(M1,plain_mul(M0,g))
    lo12=plain_sub(M2,plain_mul(M1,g))
    lo22=plain_sub(M3,plain_mul(M2,g))
    hi11=plain_sub(plain_mul(M0,h),M1)
    hi12=plain_sub(plain_mul(M1,h),M2)
    hi22=plain_sub(plain_mul(M2,h),M3)
    strict_PD(block(lo11,lo12,lo12,lo22))
    strict_PD(block(hi11,hi12,hi12,hi22))
    # F_Gauss = [M0 M1]* [[M1 M2],[M2 M3]]^-1 * [M0 ; M1].
    K=block(M1,M2,M2,M3)
    rhs=M0+M1
    X=solve_fraction_free(K,rhs)
    left=[M0[i]+M1[i] for i in range(8)]
    gauss=mm(Rmat(left),X)
    # F_Lobatto = [(g+h)M0-M1 - b c^-1 b]/(g h).
    b=plain_sub(plain_sub(plain_mul(M1,g+h),M2),plain_mul(M0,g*h))
    c=plain_sub(plain_sub(plain_mul(M2,g+h),M3),plain_mul(M1,g*h))
    Y=solve_fraction_free(c,b)
    correction=mm(Rmat(b),Y)
    lobatto=multiply(sub(sub(plain_mul(M0,g+h),M1),correction),
                     Rational(1,g*h))
    low=sub(Rmat(U0),lobatto)
    high=sub(Rmat(U0),gauss)
    low_den,low_sha,_=fingerprint(low)
    high_den,high_sha,_=fingerprint(high)
    orig=auth[index]
    check(int(orig["sample_num"])==z and
          int(orig["lower_den"])==low_den and
          int(orig["upper_den"])==high_den and
          orig["lower_exact_sha256"]==low_sha and
          orig["upper_exact_sha256"]==high_sha,
          "independent_exact_fourmoment_Schur_matrix_not_equal")
    nlow=inertia_exact(low)
    nhigh=inertia_exact(high)
    check(nlow==nhigh==index+1 and
          nlow==int(orig["lower_negative_inertia"]) and
          nhigh==int(orig["upper_negative_inertia"]) and
          orig["four_moment_inside_three_moment"]=="PASS" and
          orig["mu3_window"]=="PASS","independent_signed_mu3_Schur_inertia")
    print("Y137_INDEPENDENT_SCHUR_MATRIX|sample_num="+str(z)+
          "|signed_mu3_localizers=2_STRICT_PD"+
          "|lower_SHA="+low_sha+"|upper_SHA="+high_sha+
          "|lower_inertia="+str(nlow)+"|upper_inertia="+str(nhigh)+
          "|source_signed_mu3=PINNED_FULL_Q"+
          "|independent_fourmoment_eigendirection_enclosure=MATRIX_REPLAY_PASS"+
          "|full_true_flat_projector_theorem=SEPARATE_REVIEW|json=0")
    return low_sha,high_sha


def main():
    check(len(sys.argv)==2,"usage_original_StageD_HBP")
    original=open(sys.argv[1],encoding="ascii").read()
    old=[]
    for line in original.splitlines():
        if line.startswith("Y137_D_REAL_FOUR_MOMENT|"):
            d={}
            for part in line.split("|")[1:]:
                k,sep,v=part.partition("=")
                check(k and sep and k not in d,"StageD_duplicate")
                d[k]=v
            old.append(d)
    check(len(old)==2,"StageD_two_original_moments")
    sources=read_sources()
    for i in range(2):
        Schur(i,sources,old)
    print("Y137_INDEPENDENT_SCHUR_VERDICT|signed_mu3_sources=2_OF_2_PINNED"+
          "|matrix_hash_replays=128_OF_128_EXACT"+
          "|fourmoment_inertias=E1_1_E2_2"+
          "|signed_Schur_formula=SECOND_IMPLEMENTATION_PASS"+
          "|first_original_Wilson_weight=CONDITIONAL_CANDIDATE_HOLD|json=0")


if __name__=="__main__":
    main()
