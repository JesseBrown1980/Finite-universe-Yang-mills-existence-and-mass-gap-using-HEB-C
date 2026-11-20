#!/usr/bin/env python3
"""Original finite S3 E1/E2 eigenbranch endpoint count from frozen exact Schur brackets.

Independently counts 8x8 matrix inertia with congruence elimination, including
2x2 pivots when all diagonal entries vanish. The historical signed full-Q source
and conservative Perron floor remain separately accepted premises. This run can
verify *conditional* first/second branch isolation, independently of E1/E2
projector-angle bounds.
"""
import json
import os
import sys
from fractions import Fraction as F

sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import source_sample as source

e=source.e

def need(ok,reason):
    if not ok:
        raise ValueError(reason)

def swap(A,i,j):
    if i==j:return
    A[i],A[j]=A[j],A[i]
    for row in A:row[i],row[j]=row[j],row[i]

def inertia(matrix):
    A=[list(map(source.as_fraction,row)) for row in matrix]
    n=len(A)
    need(n>0 and all(len(row)==n for row in A),"square_inertia")
    need(all(A[i][j]==A[j][i] for i in range(n) for j in range(n)),"symmetric_inertia")
    neg=pos=zero=0
    while A:
        n=len(A)
        pivot=next((i for i in range(n) if A[i][i]),None)
        if pivot is not None:
            swap(A,0,pivot)
            d=A[0][0]
            neg+=int(d<0);pos+=int(d>0)
            A=[[A[i][j]-A[i][0]*A[0][j]/d for j in range(1,n)]
               for i in range(1,n)]
            continue
        pair=next(((i,j) for i in range(n) for j in range(i+1,n) if A[i][j]),None)
        if pair is None:
            zero+=n
            break
        i,j=pair
        swap(A,0,i)
        if j==0:j=i
        swap(A,1,j)
        a=A[0][1]
        need(a!=0 and A[0][0]==A[1][1]==0,"two_pivot")
        neg+=1;pos+=1
        A=[[A[x][y]-(A[x][0]*A[1][y]+A[x][1]*A[0][y])/a
            for y in range(2,n)] for x in range(2,n)]
    need(neg+pos+zero==len(matrix),"inertia_count")
    return neg,pos,zero

def endpoint(i,auth):
    z=e.ra.ROWS[i][0]
    U0,m0,m1,m2=e.source.accepted_old_moments(i)
    m3=e.exact.F(auth[z])
    L,U=e.exact.bracket4(U0,m0,m1,m2,m3,e.FLOOR-z,468000000000-z)
    need(e.exact.pd(e.exact.sub(U,L)),"Loewner_source")
    windows=e.three_moment_windows()
    a,b=windows[i]
    need(a<b<z<e.FLOOR,"endpoints_below_sample")
    W=e.WF
    physden=F(e.ra.D); energyden=F(e.DEN)
    gamma=F(e.FLOOR)/energyden
    z_phys=F(z)/energyden
    derivative_upper=1+F(72)/(gamma-z_phys)**2
    out=[]
    for t,expected in ((a,i),(b,i+1)):
        dt=F(z-t)/energyden
        lower=[[source.as_fraction(L[j][k])/physden+(dt*W[j] if j==k else 0)
                for k in range(8)] for j in range(8)]
        upper=[[source.as_fraction(U[j][k])/physden+
                (dt*derivative_upper*W[j] if j==k else 0)
                for k in range(8)] for j in range(8)]
        il=inertia(lower);iu=inertia(upper)
        need(iu[0]<=il[0],"Loewner_inertia_order")
        status="PASS" if iu[0]==il[0]==expected and il[2]==iu[2]==0 else "HOLD"
        out.append({"energy_num":t,"energy_den":e.DEN,"label":"lower" if t==a else "upper",
            "nneg_upper":iu[0],"nneg_lower":il[0],
            "nzero_upper":iu[2],"nzero_lower":il[2],
            "required_nneg":expected,"endpoint_count":status})
    return {"sample":z,"level":i+1,"endpoints":out,
            "conditional_branch":"PASS" if all(t["endpoint_count"]=="PASS" for t in out) else "HOLD",
            "original_fullQ_source":"PINNED_PREMISE",
            "original_Wilson_first_weight":"FORMAL_HOLD"}

def toy():
    need(inertia([[F(2),F(0)],[F(0),F(-3)]])==(1,1,0),"toy_diagonal")
    need(inertia([[F(0),F(2)],[F(2),F(0)]])==(1,1,0),"toy_2x2")
    need(inertia([[F(0),F(0)],[F(0),F(0)]])==(0,0,2),"toy_zero")
    print("Y137_ENDPOINT_INERTIA_TOY|cases=3/3_PASS|json=0",flush=True)

def main():
    toy()
    if sys.argv[1:]==["toy"]:return
    need(sys.argv[1:]==["real"],"usage: source_branch.py toy|real")
    with open(e.source.MU3_FILE,encoding="ascii") as h:
        auth=e.source.parse_pinned_mu3(h.read())
    for i in range(2):
        output=endpoint(i,auth)
        print("Y137_ENDPOINT_BRANCH|"+json.dumps(output,sort_keys=True),flush=True)
if __name__=="__main__":
    main()
