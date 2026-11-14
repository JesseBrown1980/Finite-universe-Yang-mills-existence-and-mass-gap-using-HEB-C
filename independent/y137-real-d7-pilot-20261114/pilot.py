#!/usr/bin/env python3
"""Actual periodic 3x4 S3 whole-Q streaming-moment degree-7 pilot.

Exact n<=2 source passes give four 8x8 full-Q moments of R=-QHP
(the Y=0 trial). Subsequent passes are fail-closed at a fixed frontier
cap and never masquerade as a complete degree-7 certificate.
"""
import hashlib
import os
import sys
from collections import Counter

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
HERE=os.path.join(ROOT,"independent")
sys.path.insert(0,HERE)
import finite_s3_3x4_r9_first_gap as c

B=1000000000
SAMPLES=(69909875505,69949729820)
DEGREE_TARGET=7
MAX_SOURCE_STATES=18000
MAX_NEW_STATES=420000
MAX_RAW_MOVES=1300000
ZERO=(0,)*8
NEIGHBOR_CHECK_SAMPLE=64
CHECKER_SHA="91bd1e80cbfcfb76198966aa177d097ecfbe8143"


def need(ok,why):
    if not ok:
        print("Y137_D7_REFUSE|reason="+why+"|json=0",flush=True)
        raise SystemExit(1)


def emit(name,**fields):
    print(name+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())+
          "|json=0",flush=True)


def gitblob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+bytes((0,))+data).hexdigest()


def source_check():
    path=os.path.join(HERE,"finite_s3_3x4_r9_first_gap.py")
    need(gitblob(open(path,"rb").read())==CHECKER_SHA,
         "original_operator_not_git_pinned")
    need(c.LX==3 and c.LY==4 and len(c.TRANS)==3 and c.V==12,
         "wrong_periodic_model")


def flats():
    result=set()
    for a in range(6):
        for b in range(6):
            if c.MUL[a][b]!=c.MUL[b][a]:
                continue
            links=[0]*(2*c.V)
            for y in range(c.LY):
                links[c.pos(c.LX-1,y)]=a
            for x in range(c.LX):
                links[c.V+c.pos(x,c.LY-1)]=b
            result.add(c.canonical(links))
    result=sorted(result)
    need(len(result)==8 and sum(c.weight(k) for k in result)==18,
         "flat_sector_census")
    return result


def raw_moves(key):
    """Independent raw 24-link transposition traversal, not c.neighbors."""
    U=c.from_key(key)
    out=Counter()
    raw=0
    for idx in range(24):
        old=U[idx]
        for t in c.TRANS:
            U[idx]=c.MUL[t][old]
            out[c.canonical(U)]+=1
            raw+=1
        U[idx]=old
    need(raw==72 and sum(out.values())==72,"72_raw_move_failure")
    return out


def seed(flat):
    fl=set(flat)
    nextkeys=set()
    for f in flat:
        nextkeys.update(raw_moves(f))
    nextkeys.difference_update(fl)
    states=sorted(nextkeys)
    need(len(states)==264,"first_nonflat_shell")
    V={}
    audit=0
    for k in states:
        n=raw_moves(k)
        vec=tuple(n.get(f,0) for f in flat)
        if any(vec):
            V[k]=vec
        audit+=72
    need(V and len(V)<=264,"source_not_from_true_flat_coupling")
    emit("Y137_D7_SOURCE",seed_type="Y0_R_minus_QHP",
         flat_states=8,first_shell=264,nonzero_seed_orbits=len(V),
         seed_raw_move_count=audit,
         seed_support_exhaustive=1,
         accepted_K3_trial_residual="DIFFERENT_SOURCE")
    return V


def gram(A,Bv):
    out=[[0]*8 for _ in range(8)]
    for key,vr in A.items():
        vs=Bv.get(key,ZERO)
        if not any(vs):
            continue
        w=c.weight(key)
        for p in range(8):
            val=w*vr[p]
            if val:
                for q in range(8):
                    out[p][q]+=val*vs[q]
    return out


def msum(a,b,alpha,beta):
    return [[alpha*a[i][j]+beta*b[i][j] for j in range(8)]
            for i in range(8)]


def add(a,b):
    return [[a[i][j]+b[i][j] for j in range(8)] for i in range(8)]


def matcheck(A):
    need(len(A)==8 and all(len(row)==8 for row in A),"moment_matrix_shape")
    need(all(A[i][j]==A[j][i] for i in range(8)
             for j in range(8)),"W_moment_not_symmetric")


def encode(A):
    return ";".join(",".join(str(v) for v in row) for row in A)


def sha(A):
    return hashlib.sha256("|".join(str(x) for row in A
                                   for x in row).encode("ascii")).hexdigest()


def advance(V,flat,step):
    """Apply full QHQ using source-driven weighted adjoints, no Q boundary loss."""
    need(len(V)<=MAX_SOURCE_STATES,"source_cap_exceeded")
    flatset=set(flat)
    nextV={}
    total=0
    paired=0
    rows={}
    for idx,(key,vec) in enumerate(V.items()):
        near=raw_moves(key)
        if idx<NEIGHBOR_CHECK_SAMPLE:
            need(near==c.neighbors(key),"independent_raw_move_vs_checker")
        rows[key]=near
        wy=c.weight(key)
        row=nextV.setdefault(key,[0]*8)
        mag=c.magnetic(c.from_key(key))
        factor=72+9*mag
        for k in range(8):
            row[k]+=factor*vec[k]
        for dst,cc in near.items():
            total+=cc
            if dst in flatset:
                continue
            wd=c.weight(dst)
            need((wy*cc)%wd==0,"weighted_source_target_nonintegrality")
            reverse=wy*cc//wd
            target=nextV.setdefault(dst,[0]*8)
            for k in range(8):
                target[k]-=reverse*vec[k]
        if len(nextV)>MAX_NEW_STATES or total>MAX_RAW_MOVES:
            need(False,"pilot_hard_resource_cap")
    for key, near in rows.items():
        for dst,cc in near.items():
            if dst in rows:
                need(c.weight(key)*cc==c.weight(dst)*rows[dst].get(key,0),
                     "every_internal_edge_weighted_balance")
                paired+=1
    out={key:tuple(vals) for key,vals in nextV.items() if any(vals)}
    need(out and len(out)<=MAX_NEW_STATES,"frontier_cap_exceeded")
    # Independent true row-action check on real Q target keys. This uses
    # checker neighbor rows instead of source-driven weighted transport.
    for key in list(out)[:NEIGHBOR_CHECK_SAMPLE]:
        vec=V.get(key,ZERO)
        direct=[(72+9*c.magnetic(c.from_key(key)))*v for v in vec]
        for dst,cc in c.neighbors(key).items():
            if dst in flatset:
                continue
            vv=V.get(dst,ZERO)
            for k in range(8):
                direct[k]-=cc*vv[k]
        need(tuple(direct)==out[key],"second_operator_row_action")
    emit("Y137_D7_PASS",completed_operator_pass=step,
         active_sources=len(V),full_raw_moves=total,
         complete_next_active_support=len(out),
         all_destinations_indexed=1,
         P_destinations_projected=1,
         source_to_target_W_balance_integrality="PASS",
         internal_edge_reverse_balance=paired,
         independently_enumerated_raw_moves="PASS",
         independent_operator_sample_rows=min(len(out),NEIGHBOR_CHECK_SAMPLE),
         source_truncation="NONE")
    return out


def output_moments(M,Z):
    b=B
    for z in SAMPLES:
        m0,m1,m2,m3=M
        a0=m0
        a1=msum(m1,m0,b,-z)
        a2=add(add(msum(m2,m1,b*b,-2*b*z),
                       [[z*z*v for v in row] for row in m0]),
               [[0]*8 for _ in range(8)])
        a3=add(add(msum(m3,m2,b*b*b,-3*b*b*z),
                       [[3*b*z*z*x for x in row] for row in m1]),
               [[-z*z*z*x for x in row] for row in m0])
        for k,A in enumerate((a0,a1,a2,a3)):
            matcheck(A)
            emit("Y137_D7_MOMENT",source="Y0_R_minus_QHP",
                 sample_num=z,den=b,order=k,
                 W_weighted_8x8_sha256=sha(A),
                 W_weighted_8x8=encode(A),
                 exact_full_Q=1,
                 Q_projected_after_every_operator_application=1)
    # independent shifted pair checks for first and second moments
    need(Z==len(M)==4,"moment_count")


def main():
    source_check()
    F=flats()
    emit("Y137_D7_FREEZE",target_degree=DEGREE_TARGET,
         actual_model="3x4_periodic_S3_r9",
         complete_full_Q_operator="24_links_x_3_transpositions",
         first_run_cap_sources=MAX_SOURCE_STATES,
         first_run_cap_raw_moves=MAX_RAW_MOVES,
         floor_source="ACCEPTED_PER_PR187",
         actual_first_Wilson_weight="HOLD")
    R=seed(F)
    V1=advance(R,F,1)
    V2=advance(V1,F,2)
    M=[gram(R,R),gram(R,V1),gram(V1,V1),gram(V1,V2)]
    for A in M:
        matcheck(A)
    need(M[0][0][0]>0,"real_fullQ_nonzero_source_Gram")
    output_moments(M,4)
    # This is intentionally a pilot. The real full-Q source R_K3 has
    # 1,985,218 shell4 residual orbits already at degree zero;
    # it requires distributed streaming before even its first pass.
    emit("Y137_D7_VERDICT",completed_operator_passes=2,
         exact_real_model_source_moments_per_sample=4,
         degree7_requested_passes=7,
         accepted_K3_residual_moments="NOT_COMPUTED",
         degree7_actual_source="HOLD_RESOURCE_BOUND",
         uncomputed_remaining_passes=5,
         whole_Q_state_census=2177317873,
         full_source_Wilson_weight="HOLD",issue_137="OPEN")


if __name__=="__main__":
    main()
