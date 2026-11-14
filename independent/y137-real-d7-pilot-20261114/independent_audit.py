#!/usr/bin/env python3
"""Independent full-Q moments 0..3 for Y=0 actual S3 3x4 source.

This audit uses the *original merged K2 checker graph()* and its Q rows,
not the pilot's source-driven raw neighbor expansion. It proves that the
one-step V1 has zero K2 exterior so the first four moments need only
K2 internal row products. Both 8x8 source sample hashes are compared.
"""
import hashlib
import os
import sys
from itertools import combinations
from math import comb

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
sys.path.insert(0,os.path.join(ROOT,"independent"))
import finite_s3_3x4_r9_first_gap as c

HERE=os.path.dirname(os.path.abspath(__file__))
RESULT=os.path.join(HERE,"RESULT-D7-PILOT.hbp")
B=1000000000
SAMPLES=(69909875505,69949729820)
ORDERS=4


def need(ok,why):
    if not ok:
        print("Y137_D7_INDEPENDENT_REFUSE|reason="+why+"|json=0",flush=True)
        raise SystemExit(1)


def emit(label,**fields):
    print(label+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())+
          "|json=0",flush=True)


def sha(a):
    return hashlib.sha256("|".join(str(v) for row in a for v in row)
                          .encode("ascii")).hexdigest()


def enc(a):
    return ";".join(",".join(str(v) for v in row) for row in a)


def parse():
    rows=[]
    for line in open(RESULT,encoding="utf-8"):
        if line.startswith("Y137_D7_MOMENT|"):
            d={}
            for f in line.strip().split("|")[1:]:
                k,v=f.split("=",1)
                need(k not in d,"duplicate_key")
                d[k]=v
            rows.append(d)
    need(len(rows)==8,"source_moment_count")
    return rows


def gram(a,b,w):
    M=[[0]*8 for _ in range(8)]
    for i,va in enumerate(a):
        vb=b[i]
        wi=w[i]
        for p in range(8):
            for q in range(8):
                M[p][q]+=wi*va[p]*vb[q]
    return M


def symmetric(M):
    need(all(M[i][j]==M[j][i] for i in range(8)
             for j in range(8)),"weighted_symmetry")
    return M


def ipow(a,n):
    need(n>=0,"bad_exact_power")
    out=1
    while n:
        if n%2:
            out*=a
        a*=a
        n//=2
    return out


def linear_combo(moment,z,k):
    out=[[0]*8 for _ in range(8)]
    for j in range(k+1):
        fac=comb(k,j)*ipow(B,j)*ipow(-z,k-j)
        for p in range(8):
            for q in range(8):
                out[p][q]+=fac*moment[j][p][q]
    return out


def apply(A,diag,vec):
    out=[]
    for i,row in enumerate(A):
        val=[diag[i]*vec[i][k] for k in range(8)]
        for j,cc in row:
            for k in range(8):
                val[k]-=cc*vec[j][k]
        out.append(tuple(val))
    return out


def main():
    source=parse()
    w,mag,adj,flat,outer=c.graph()
    wq=w[8:]
    need(len(adj)==8034 and len(flat)==8034 and len(wq)==8034,
         "checker_Q_source_census")
    for i,row in enumerate(adj):
        for j,cc in row:
            need(wq[i]*cc==wq[j]*dict(adj[j]).get(i,0),
                 "every_K2_weighted_edge")
    R=[tuple(v) for v in flat]
    need(sum(int(any(vec)) for vec in R)==264,
         "Y0_Q_P_residual_support")
    for wf,edges in outer:
        for i,weighted in edges:
            need(all(x==0 for x in R[i]),"first_operator_pass_reaches_K3")
    D=[72+9*mag[8+i] for i in range(len(adj))]
    V1=apply(adj,D,R)
    V2=apply(adj,D,V1)
    moments=[symmetric(gram(R,R,wq)),symmetric(gram(R,V1,wq)),
             symmetric(gram(V1,V1,wq)),symmetric(gram(V1,V2,wq))]
    for zi,z in enumerate(SAMPLES):
        for k in range(ORDERS):
            expected=source[zi*ORDERS+k]
            M=linear_combo(moments,z,k)
            need(expected["source"]=="Y0_R_minus_QHP" and
                 int(expected["sample_num"])==z and
                 int(expected["order"])==k,"wrong_source_or_order")
            need(expected["W_weighted_8x8_sha256"]==sha(M) and
                 expected["W_weighted_8x8"]==enc(M),
                 "independent_K2_vs_raw_move_moment")
            emit("Y137_D7_INDEPENDENT_POINT",sample_num=z,
                 moment_order=k,source="K2_CHECKER_INDEPENDENT_ROWS",
                 exact_W_8x8_sha256=sha(M),
                 independent_fullQ_agreement=1)
    emit("Y137_D7_INDEPENDENT_VERDICT",
         real_3x4_source="Y0_MINUS_QHP",
         accepted_K3_source="DIFFERENT",
         moments_checked=8,K2_Q_states=8034,
         K2_exterior_V1="EXACT_ZERO",
         independent_source_builder="MERGED_K2_CHECKER",
         raw_move_pilot_rows="EXACTLY_MATCHED",
         degree7_real_trial="HOLD",
         actual_Wilson_weight="HOLD",issue_137="OPEN")


if __name__=="__main__":
    main()
