#!/usr/bin/env python3
"""Whole-Q accepted K3 μ2: eight exact Q4 source shards, radix64 shell5 spill.

Outputs complete Q4 partial μ0/μ1/μ2 for two samples and sorted-by-
target-address bucket streams. Each bucket must be merged across ALL
eight source shards before its shell5 μ2 contribution can be squared.
"""
import hashlib
import os
import struct
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
sys.path.insert(0,os.path.join(ROOT,"independent","y137-real-Q-moment-20261114"))
sys.path.insert(0,HERE)
import mu1_shard as src
import independent_move_rule as independent

m=src.m
c=src.c
B=src.B
COLS=8
SHARDS=8
SHARD=int(os.environ.get("Y137_D11_MU2_SHARD","0"))
BUCKETS=64
RECORD=struct.Struct("<QIBB")
MAX_ROWS=280000
MAX_EVENTS=15500000
MAX_BYTES=RECORD.size*MAX_EVENTS
OUT=os.path.join(ROOT,"build","y137-d11-mu2-full")


def need(ok,why):
    if not ok:
        print("Y137_D11_MU2_REFUSE|shard="+str(SHARD)+
              "|reason="+why+"|json=0",flush=True)
        raise SystemExit(1)


def emit(name,**d):
    print(name+"|"+"|".join(str(k)+"="+str(v) for k,v in d.items())+
          "|json=0",flush=True)


def empty():
    return [[0]*COLS for _ in range(COLS)]


def enc(A):
    return ";".join(",".join(str(v) for v in row) for row in A)


def blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+bytes((0,))+data).hexdigest()


def original_shard_rows():
    p=os.path.join(ROOT,"independent","y137-real-Q-moment-20261114",
                   "RESULT-MU1-SHARD-EVIDENCE.hbp")
    raw=open(p,"rb").read()
    need(blob(raw)=="ab6493016ee3201f61fa54746878ee3890f26f34",
         "old_eight_shards_source_receipt_changed")
    current=None
    rows={}
    for line in raw.decode("utf-8").splitlines():
        if line.startswith("BEGIN_PART|"):
            current=int(line.split("shard=",1)[1].split("|",1)[0])
        if current==SHARD and (line.startswith("Y137_MU1_PART|") or
                               line.startswith("Y137_MU1_INNER|")):
            bits=line.split("|")
            d=dict(x.split("=",1) for x in bits[1:])
            key=(bits[0],int(d["sample_num"]))
            need(key not in rows,"duplicate_old_shard_source")
            rows[key]=d
        if line.startswith("END_PART|"):
            current=None
    need(len(rows)==(4 if SHARD==0 else 2),"old_shard_missing")
    return rows


def inner_three_moments(ball,ex,Rs,Pext,z,width,mask):
    """Independent K3 quadratic response over COMPLETE inner source."""
    out=empty()
    cross=[[] for _ in range(ball["n"])]
    for f,srcidx,wc in zip(ex["e4f"],ex["e4s"],ex["e4c"]):
        wi=ball["wq"][srcidx]
        need(wc%wi==0,"inner_boundary_reverse_noninteger")
        cross[srcidx].append((f,wc//wi))
    rs,oj,oc=ball["rs"],ball["oj"],ball["oc"]
    for i,Ri in enumerate(Rs):
        sumr=[0]*COLS
        for e in range(rs[i],rs[i+1]):
            Rj=Rs[oj[e]]
            cc=oc[e]
            for k in range(COLS):
                sumr[k]+=cc*Rj[k]
        for f,cc in cross[i]:
            pf=src.unpack(Pext[f],width,mask)
            for k in range(COLS):
                sumr[k]-=cc*pf[k]
        D=B*ball["dbase"][i]-z
        V=[D*Ri[k]-B*sumr[k] for k in range(COLS)]
        src.add_gram(out,V,V,6*ball["wq"][i])
    return out


def run():
    need(0<=SHARD<SHARDS,"invalid_shard")
    ball,ex,inner,flat,width,mask,items=src.build_inputs()
    oldrows=original_shard_rows()
    n=ball["nf"]
    lo=n*SHARD//SHARDS
    hi=n*(SHARD+1)//SHARDS
    need(hi-lo<=MAX_ROWS,"full_shard_row_resource_limit")
    folder=os.path.join(OUT,"PART-"+str(SHARD))
    bins=os.path.join(folder,"bins")
    os.makedirs(bins,exist_ok=True)
    paths=[os.path.join(bins,"bucket-"+str(i).zfill(2)+".bin")
           for i in range(BUCKETS)]
    writers=[open(p,"wb") for p in paths]
    hashes=[hashlib.sha256() for _ in range(BUCKETS)]
    counts=[0]*BUCKETS
    result=[(empty(),empty(),empty()) for _ in items]
    raw=0
    to5=0
    to3=0
    to4=0
    back=0
    checked=0
    bucket_bytes=0
    total_events=0
    indep_positions={lo,lo+1,lo+3,lo+7,lo+15,lo+127,lo+511,hi-1}
    for f in range(lo,hi):
        key=m.decode(ex["code4"][f])
        wf=ball["eW"][f]
        need(c.weight(key)==wf,"Q4_source_weight")
        near=c.neighbors(key)
        need(sum(near.values())==72,"source_missing_one_of_72_moves")
        if f in indep_positions:
            try:
                independent.audit_original(
                    key,near,wf,c.magnetic(c.from_key(key)),
                    c.KEPT,c.TRANS)
            except ValueError:
                need(False,"independent_raw_move_source_mismatch")
            checked+=1
        raw+=72
        insums=[[0]*COLS for _ in items]
        outer_sums=[0]*len(items)
        expected={}
        for e in range(ball["es"][f],ball["es"][f+1]):
            wc=ball["ewc"][e]
            need(wc%wf==0,"original_Q3_reverse_integrality")
            j=ball["esrc"][e]
            expected[j]=expected.get(j,0)+wc//wf
        found={}
        for dst,cc in near.items():
            need(dst not in flat,"unexpected_Q4_to_flat")
            j=inner.get(dst)
            if j is not None:
                found[j]=cc
                to3+=cc
                for t,(_,_,Rs,_) in enumerate(items):
                    Ri=Rs[j]
                    for k in range(COLS):
                        insums[t][k]+=cc*Ri[k]
                continue
            g=ex["s4"].get(m.code(dst))
            if g is not None:
                to4+=cc
                wg=ball["eW"][g]
                need(wf*cc%wg==0,"Q4_Q4_flux")
                for t,(_,_,_,Qp) in enumerate(items):
                    outer_sums[t]+=cc*Qp[g]
                continue
            code=m.code(dst)
            wg=c.weight(dst)
            need(wg in (1,2,3,6) and wf*cc%wg==0,
                 "Q4_Q5_flux")
            reverse=wf*cc//wg
            need(1<=reverse<=72,"reverse_degree")
            bit=code%BUCKETS
            data=RECORD.pack(code,f,reverse,wg)
            writers[bit].write(data)
            hashes[bit].update(data)
            counts[bit]+=1
            total_events+=1
            to5+=cc
            bucket_bytes+=RECORD.size
            need(total_events<=MAX_EVENTS and
                 bucket_bytes<=MAX_BYTES,"hard_disk_event_budget")
        need(found==expected,"Q4_to_Q3_original_edge_integrity")
        back+=len(found)
        mag=c.magnetic(c.from_key(key))
        need(4<=mag<=16,"real_shell4_magnetic_range")
        for t,(row,record,Rs,Qp) in enumerate(items):
            z=row[0]
            pf=src.unpack(Qp[f],width,mask)
            s4=src.unpack(outer_sums[t],width,mask)
            D=B*(72+9*mag)-z
            # R_Q4=-pf; V_Q4=-(D pf-B sum_Q4 pf+B sum_inner R).
            # Sign on both factors cancels for μ2; for μ1 source
            # uses pf with the same positive response.
            resp=[D*pf[k]-B*s4[k]+B*insums[t][k]
                  for k in range(COLS)]
            gram0,gram1,gram2=result[t]
            wt=6*wf
            src.add_gram(gram0,pf,pf,wt)
            src.add_gram(gram1,pf,resp,wt)
            src.add_gram(gram2,resp,resp,wt)
        if (f-lo)%50000==0:
            emit("Y137_D11_MU2_PROGRESS",shard=SHARD,
                 source_rows_done=f-lo,total=hi-lo,
                 raw_electric_moves=raw,
                 shell5_edges=total_events)
    for w in writers:
        w.close()
    need(raw==(hi-lo)*72 and raw==to3+to4+to5,
         "all_72_moves_partitioned")
    need(total_events==sum(counts) and
         bucket_bytes==total_events*RECORD.size,
         "bin_length_census")
    with open(os.path.join(folder,"BUCKETS.hbp"),"w",encoding="utf-8") as f:
        for i,p in enumerate(paths):
            need(os.path.getsize(p)==counts[i]*RECORD.size,
                 "source_spool_size")
            row=("Y137_D11_MU2_BUCKET|shard="+str(SHARD)+
                 "|bucket="+str(i)+"|records="+str(counts[i])+
                 "|bytes="+str(counts[i]*RECORD.size)+
                 "|sha256="+hashes[i].hexdigest()+"|json=0")
            f.write(row+"\n")
    with open(os.path.join(folder,"PART.hbp"),"w",encoding="utf-8") as f:
        def publish(label,**row):
            bits=(label+"|"+"|".join(str(k)+"="+str(v)
                                  for k,v in row.items())+"|json=0")
            print(bits,flush=True)
            f.write(bits+"\n")
        publish("Y137_D11_MU2_SHARD",shard=SHARD,shards=SHARDS,
                source_start=lo,source_stop=hi,
                source_rows=hi-lo,all_raw_electric_moves=raw,
                outgoing_to_K3_moves=to3,
                within_Q4_moves=to4,
                outgoing_to_Q5_moves=to5,
                recorded_Q5_edges=total_events,
                spool_bytes=bucket_bytes,
                exact_weighted_reverse_edges=back,
                independently_authored_Q4_row_checks=checked,
                bucket_count=BUCKETS,
                total_8x8_samples=2,
                real_mu2="NOT_CERTIFIED_UNTIL_EIGHT_WHOLE_SHARDS_MERGED")
        for t,(row,record,Rs,Qp) in enumerate(items):
            z=row[0]
            g0,g1,g2=result[t]
            oldsource=oldrows[("Y137_MU1_PART",z)]
            need(enc(g0)==oldsource["complete_Q4_mu0_six"] and
                 enc(g1)==oldsource["complete_Q4_mu1_six"],
                 "full_shard_mu0_mu1_must_equal_previously_certified_source")
            publish("Y137_D11_MU2_PART",
                    shard=SHARD,sample_num=z,
                    Q4_mu0_six=enc(g0),
                    Q4_mu1_six=enc(g1),
                    Q4_mu2_six=enc(g2),
                    exact_prior_mu0_mu1_shard_match=1)
            if SHARD==0:
                inner0,inner1=src.inner_mu1(ball,ex,Rs,Qp,z,width,mask)
                oldinner=oldrows[("Y137_MU1_INNER",z)]
                need(enc(inner0)==oldinner["complete_K3_mu0_six"] and
                     enc(inner1)==oldinner["complete_K3_mu1_six"],
                     "K3_source_uptake_changed")
                inner2=inner_three_moments(ball,ex,Rs,Qp,z,width,mask)
                publish("Y137_D11_MU2_INNER",shard=0,sample_num=z,
                        K3_mu0_six=enc(inner0),
                        K3_mu1_six=enc(inner1),
                        K3_mu2_six=enc(inner2),
                        exact_prior_K3_mu0_mu1_match=1)
        publish("Y137_D11_MU2_VERDICT",shard=SHARD,
                source="ACTUAL_ACCEPTED_K3",
                complete_Q4_partition="PASS",
                shell5_spill="FROZEN_BUCKETED",
                actual_mu2="HOLD_ALL_EIGHT_SHARDS_AND_GLOBAL_TARGET_REDUCTION",
                target_degree=11,remaining_moments_per_sample=20,
                original_Wilson_weight="HOLD",issue_137="OPEN")


if __name__=="__main__":
    run()
