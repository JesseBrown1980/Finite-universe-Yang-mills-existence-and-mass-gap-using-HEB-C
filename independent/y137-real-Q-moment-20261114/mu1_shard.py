#!/usr/bin/env python3
"""Sharded exact accepted-K3 mu_1 from all shell4 raw 72-move rows.

Each shard independently rebuilds the accepted K3 source vectors from frozen
Y, accounts for every shell4 outgoing move (including Q shell5), and emits
complete exact outer partial mu0 and mu1 matrices for both frozen energies.
No shell5 values are needed for mu1 because the old residual is exactly
zero on shell5. Shell5 IS required for mu2 and later moments.
"""
import hashlib
import os
import sys
from collections import Counter

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
CACHE_DIR=os.path.join(ROOT,"independent","y137-shell4-diagonal-cache-20261114")
sys.path.insert(0,CACHE_DIR)
import source_cache as source

old=source.old
m=old.m
c=m.c
B=old.B
SCALE=old.SCALE
SHARDS=8
SHARD=int(os.environ.get("Y137_MU1_SHARD","0"))
HARD_ROW_LIMIT=280000
ZERO=(0,)*8


def need(ok,reason):
    if not ok:
        print("Y137_MU1_REFUSE|shard="+str(SHARD)+"|reason="+reason+
              "|json=0",flush=True)
        raise SystemExit(1)


def emit(label,**fields):
    print(label+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())+
          "|json=0",flush=True)


def mat():
    return [[0]*8 for _ in range(8)]


def add_gram(out,a,b,w):
    for i in range(8):
        p=w*a[i]
        if p:
            for j in range(8):
                out[i][j]+=p*b[j]


def mat_add(a,b):
    return [[a[i][j]+b[i][j] for j in range(8)] for i in range(8)]


def encode(a):
    return ";".join(",".join(str(v) for v in row) for row in a)


def sha(a):
    return hashlib.sha256("|".join(str(v) for row in a for v in row)
                          .encode("ascii")).hexdigest()


def inner_residuals(ball,z,Y):
    rs,oj,oc,CI=ball["rs"],ball["oj"],ball["oc"],ball["C"]
    rows=[]
    for i in range(ball["n"]):
        t=[0]*8
        for p in range(rs[i],rs[i+1]):
            dest=Y[oj[p]]
            coeff=oc[p]
            for k in range(8):
                t[k]+=coeff*dest[k]
        yi=Y[i]
        ci=CI[i]
        d=B*ball["dbase"][i]-z
        rows.append(tuple(d*yi[k]-B*t[k]-
                          (B*SCALE*ci[k] if ci is not None else 0)
                          for k in range(8)))
    return rows


def packed_outer(ball,Y,width):
    """R_shell4=-positive P. Return the 8-entry positive residual packed."""
    hi=max(max(row) for row in Y)
    wy=max((ball["maxwc"]*hi).bit_length()+3,8)
    py=m.pack(Y,wy)
    my=(1<<wy)-1
    es,esrc,ewc,wt=ball["es"],ball["esrc"],ball["ewc"],ball["eW"]
    arr=[0]*ball["nf"]
    for f in range(ball["nf"]):
        packed=0
        for e in range(es[f],es[f+1]):
            packed+=ewc[e]*py[esrc[e]]
        w=wt[f]
        val=0
        for k in range(8):
            digit=(packed>>(wy*k))&my
            need(digit%w==0,"weighted_exterior_residual_division")
            val+=(B*(digit//w))<<(width*k)
        arr[f]=val
    return arr


def unpack(v,width,mask):
    return [(v>>(width*k))&mask for k in range(8)]


def inner_mu1(ball,ex,Rs,Pext,z,width,mask):
    """Compute *only once* at shard0, inner Q rows of mu1 and mu0."""
    result=mat()
    gm=mat()
    rs,oj,oc=ball["rs"],ball["oj"],ball["oc"]
    cross=[[] for _ in range(ball["n"])]
    for f,src,weighted in zip(ex["e4f"],ex["e4s"],ex["e4c"]):
        wi=ball["wq"][src]
        need(weighted%wi==0,"inner_outgoing_coeff_divisibility")
        cross[src].append((f,weighted//wi))
    for i,ri in enumerate(Rs):
        acc=[0]*8
        for e in range(rs[i],rs[i+1]):
            rj=Rs[oj[e]]
            cc=oc[e]
            for k in range(8):
                acc[k]+=cc*rj[k]
        for f,cc in cross[i]:
            pq=unpack(Pext[f],width,mask)
            for k in range(8):
                acc[k]-=cc*pq[k]
        D=B*ball["dbase"][i]-z
        resp=[D*ri[k]-B*acc[k] for k in range(8)]
        w=6*ball["wq"][i]
        add_gram(gm,ri,ri,w)
        add_gram(result,ri,resp,w)
    return gm,result


def build_inputs():
    need(0<=SHARD<SHARDS,"invalid_shard_id")
    ball,ex=old.build()
    need(ball["n"]==155378 and ball["nf"]==1985218,
         "actual_K3_shell4_census")
    states,flat,sizes=m.rebuild_states()
    need(sizes==[8,264,7770],"original_small_shell_census")
    full_inner={key:i-8 for i,key in enumerate(states) if i>=8}
    full_inner.update({key:i+(len(states)-8)
                       for i,key in enumerate(ex["ext_keys"])})
    need(len(full_inner)==ball["n"],"unique_inner_orbit_lookup")
    flatset=set(states[:8])
    # Both original accepted E1/E2 source samples in one geometry build.
    inputs=[]
    maxq=0
    for row in old.FROZEN:
        z=row[0]
        t=m.threshold_ball(z,B,old.STEPS,SCALE,ball,old.FLOOR,
                           keep_y=True)
        need(t["hu"]==row[4] and t["hg"]==row[5],
             "accepted_K3_U_G_source_hashes")
        Y=t["Y"]
        hi=max(max(v) for v in Y)
        maxq=max(maxq,B*ball["maxwc"]*hi)
        inputs.append((row,t,Y))
    width=max((72*maxq).bit_length()+4,64)
    mask=(1<<width)-1
    data=[]
    for row,t,Y in inputs:
        Rs=inner_residuals(ball,row[0],Y)
        Qp=packed_outer(ball,Y,width)
        need(any(Qp),"outer_source_not_zero")
        data.append((row,t,Rs,Qp))
    return ball,ex,full_inner,flatset,width,mask,data


def run():
    ball,ex,inner,flat,width,mask,items=build_inputs()
    n=ball["nf"]
    low=n*SHARD//SHARDS
    high=n*(SHARD+1)//SHARDS
    need(high-low<=HARD_ROW_LIMIT,"shard_row_limit")
    mu0out=[mat() for _ in items]
    mu1out=[mat() for _ in items]
    move_count=0
    shell5_move_count=0
    internal_reverse_verified=0
    inner_reverses_verified=0
    raw_source_hash=hashlib.sha256()
    for f in range(low,high):
        key=m.decode(ex["code4"][f])
        w=ball["eW"][f]
        need(c.weight(key)==w,"orbit_weight_mismatch")
        near=c.neighbors(key)
        need(sum(near.values())==72,"full_72_electric_move_row")
        raw_source_hash.update(int(ex["code4"][f]).to_bytes(8,"little"))
        move_count+=72
        q4sum=[0]*len(items)
        insums=[[0]*8 for _ in items]
        expected={}
        for e in range(ball["es"][f],ball["es"][f+1]):
            wi=ball["ewc"][e]
            need(wi%w==0,"expected_Q3_reverse_integrality")
            si=ball["esrc"][e]
            expected[si]=expected.get(si,0)+wi//w
        actual={}
        for dst,cc in near.items():
            if dst in flat:
                need(False,"shell4_unexpected_flat_neighbor")
            j=inner.get(dst)
            if j is not None:
                actual[j]=cc
                for t,(_,_,Rs,_) in enumerate(items):
                    ri=Rs[j]
                    for k in range(8):
                        insums[t][k]+=cc*ri[k]
                continue
            g=ex["s4"].get(m.code(dst))
            if g is None:
                shell5_move_count+=cc
                continue
            wg=ball["eW"][g]
            need((w*cc)%wg==0,"shell4_shell4_weighted_flux")
            for t,(_,_,_,Qp) in enumerate(items):
                q4sum[t]+=cc*Qp[g]
            # Sample reciprocal edges with separately evaluated raw rows.
            if (f-low)<12 and internal_reverse_verified<1024:
                reverse=c.neighbors(dst).get(key,0)
                need(w*cc==wg*reverse,"sampled_Q4_Q4_reverse_balance")
                internal_reverse_verified+=1
        need(actual==expected,"all_Q4_Q3_reverses_exact")
        inner_reverses_verified+=len(actual)
        mag=c.magnetic(c.from_key(key))
        need(4<=mag<=16,"magnetic_shell4_support")
        for t,(row,record,Rs,Qp) in enumerate(items):
            z=row[0]
            pf=unpack(Qp[f],width,mask)
            sum4=unpack(q4sum[t],width,mask)
            D=B*(72+9*mag)-z
            response=[D*pf[k]-B*sum4[k]+B*insums[t][k]
                      for k in range(8)]
            add_gram(mu0out[t],pf,pf,6*w)
            add_gram(mu1out[t],pf,response,6*w)
        if (f-low)%40000==0:
            emit("Y137_MU1_PROGRESS",shard=SHARD,done=f-low,
                 total=high-low,raw_moves=move_count)
    emit("Y137_MU1_SHARD",shard=SHARD,shards=SHARDS,
         start=low,stop=high,rows=high-low,
         complete_raw_moves=move_count,
         outgoing_to_shell5_moves=shell5_move_count,
         Q4_Q3_reverse_edges_verified=inner_reverses_verified,
         sampled_Q4_Q4_reciprocal_edges=internal_reverse_verified,
         all_72_moves_per_row="PASS",
         exact_8x8_source_samples=2,
         source_rows_hash=raw_source_hash.hexdigest(),
         accepted_mu1="PARTIAL_SHARD_ONLY")
    for t,(row,record,Rs,Qp) in enumerate(items):
        z=row[0]
        emit("Y137_MU1_PART",shard=SHARD,sample_num=z,
             complete_Q4_mu0_six=encode(mu0out[t]),
             complete_Q4_mu1_six=encode(mu1out[t]),
             source_U_sha256=row[4],source_G_sha256=row[5],
             real_source="ACCEPTED_K3")
        if SHARD==0:
            im0,im1=inner_mu1(ball,ex,Rs,Qp,z,width,mask)
            # Exact source inner Gram reproduced from the original
            # complete-Q G, not from a differently chosen trial.
            source_gram=old.inner_gram(ball,z,record["Y"])
            need(source_gram==im0,"accepted_inner_Gram_independent_rebuild")
            emit("Y137_MU1_INNER",shard=0,sample_num=z,
                 complete_K3_mu0_six=encode(im0),
                 complete_K3_mu1_six=encode(im1),
                 source_U_sha256=row[4],source_G_sha256=row[5])
    emit("Y137_MU1_VERDICT",shard=SHARD,scope="REAL_COMPLETE_3x4_Q4_ROW_SOURCE",
         uncomputed_shards=SHARDS-1,
         next="SUM_ALL_SHARDS_AND_CHECK_COMPLETE_8x8_SYMMETRY",
         real_mu1_certified="NOT_UNTIL_ALL_SHARDS",
         actual_Wilson_weight="HOLD",issue_137="OPEN")


if __name__=="__main__":
    run()
