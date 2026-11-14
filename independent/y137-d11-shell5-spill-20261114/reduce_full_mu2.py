#!/usr/bin/env python3
"""Full-Q μ2 shell5 W-Gram: externally merge 8 Q4 shards by target key.

One reducer handles 8 of the 64 disjoint radix buckets, reading all
eight source shards for each bucket. No shell5 target is squared before
every incoming Q4 source has been reduced. Exact integer arithmetic.
"""
import hashlib
import heapq
import os
import struct
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
sys.path.insert(0,os.path.join(ROOT,"independent","y137-real-Q-moment-20261114"))
import mu1_shard as src

m=src.m
c=src.c
B=src.B
COLS=8
SHARDS=8
GROUPS=8
BUCKETS=64
SH4=1985218
RECORD=struct.Struct("<QIBB")
GROUP=int(os.environ.get("Y137_D11_MU2_GROUP","0"))
PART_ROOT=os.environ.get(
    "Y137_D11_MU2_PART_ROOT",
    os.path.join(ROOT,"build","y137-d11-mu2-download"))
OUT=os.path.join(ROOT,"build","y137-d11-mu2-reduced")


def need(ok,why):
    if not ok:
        print("Y137_D11_MU2_REDUCER_REFUSE|group="+str(GROUP)+
              "|reason="+why+"|json=0",flush=True)
        raise SystemExit(1)


def emit(label,**fields):
    print(label+"|"+"|".join(str(k)+"="+str(v)
                           for k,v in fields.items())+"|json=0",flush=True)


def empty():
    return [[0]*COLS for _ in range(COLS)]


def encode(A):
    return ";".join(",".join(str(v) for v in row) for row in A)


def bucket_path(shard,bucket):
    folder=("y137-mu2-shard-"+str(shard)+"-group-"+str(GROUP))
    base=os.path.join(PART_ROOT,folder)
    return (os.path.join(base,"bucket-"+str(bucket).zfill(2)+".bin"),
            os.path.join(base,"BUCKETS.hbp"))


def bucket_receipt(path,bucket,shard):
    expected=None
    need(os.path.isfile(path),"missing_bucket_manifest")
    with open(path,encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("Y137_D11_MU2_BUCKET|"):
                bits=dict(x.split("=",1) for x in line.strip().split("|")[1:])
                if int(bits["bucket"])==bucket:
                    need(int(bits["shard"])==shard,"wrong_manifest_shard")
                    need(expected is None,"duplicate_bucket_manifest_row")
                    expected=bits
    need(expected is not None,"missing_bucket_manifest_row")
    return expected


def inputs(shard,bucket):
    path,manifest=bucket_path(shard,bucket)
    wanted=bucket_receipt(manifest,bucket,shard)
    raw=open(path,"rb").read()
    need(len(raw)%RECORD.size==0 and
         len(raw)==int(wanted["bytes"]) and
         len(raw)//RECORD.size==int(wanted["records"]) and
         hashlib.sha256(raw).hexdigest()==wanted["sha256"],
         "bucket_source_hash_or_length")
    rows=[]
    lo=SH4*shard//SHARDS
    hi=SH4*(shard+1)//SHARDS
    for key,f,rev,wg in RECORD.iter_unpack(raw):
        need(key%BUCKETS==bucket and lo<=f<hi and
             1<=rev<=72 and wg in (1,2,3,6),
             "invalid_bucket_record")
        rows.append((key,f,rev,wg,shard))
    rows.sort()
    return rows


def add_upper(M,packed,w,width,mask):
    digits=[(packed>>(width*j))&mask for j in range(COLS)]
    need(packed < (1<<(width*COLS)),"integer_lane_carry_overflow")
    prefactor=6*w*B*B
    for i in range(COLS):
        v=prefactor*digits[i]
        for j in range(i,COLS):
            M[i][j]+=v*digits[j]


def make_symmetric(M):
    for i in range(COLS):
        for j in range(i):
            M[i][j]=M[j][i]
    return M


def run():
    need(0<=GROUP<GROUPS,"invalid_group")
    ball,ex,inner,flat,width,mask,items=src.build_inputs()
    need(ball["nf"]==SH4 and len(items)==2,"wrong_accepted_source")
    P0=items[0][3]
    P1=items[1][3]
    M0,M1=empty(),empty()
    total_records=0
    total_targets=0
    raw_reverse=0
    independently_checked_weights=0
    max_group_sources=0
    for bucket in range(GROUP,BUCKETS,GROUPS):
        arrays=[inputs(shard,bucket) for shard in range(SHARDS)]
        count=sum(len(rows) for rows in arrays)
        need(count>0,"empty_expected_shell5_bucket")
        total_records+=count
        stream=heapq.merge(*(iter(rows) for rows in arrays))
        active_key=None
        active_weight=0
        active0=0
        active1=0
        active_reverse=0
        preceding_f=-1
        bucket_targets=0
        def finalize():
            nonlocal total_targets,bucket_targets
            if active_key is not None:
                need(active_reverse<=72,"more_than_72_incoming_reverse_moves")
                add_upper(M0,active0,active_weight,width,mask)
                add_upper(M1,active1,active_weight,width,mask)
                total_targets+=1
                bucket_targets+=1
        for key,f,reverse,wg,shard in stream:
            if key!=active_key:
                finalize()
                active_key=key
                active_weight=wg
                active0=0
                active1=0
                active_reverse=0
                preceding_f=-1
                if bucket_targets<8:
                    # Independent target-weight spot check per bucket.
                    need(c.weight(m.decode(key))==wg,
                         "canonical_shell5_target_weight")
                    independently_checked_weights+=1
            need(wg==active_weight and f!=preceding_f,
                 "wrong_weight_or_duplicate_source_edge")
            preceding_f=f
            active_reverse+=reverse
            raw_reverse+=reverse
            active0+=reverse*P0[f]
            active1+=reverse*P1[f]
            max_group_sources=max(max_group_sources,active_reverse)
        finalize()
        emit("Y137_D11_MU2_BUCKET_PASS",group=GROUP,
             bucket=bucket,source_records=count,
             distinct_shell5_targets=bucket_targets,
             every_Q4_shard_present=1,
             no_premature_square="PASS")
        del arrays
    os.makedirs(OUT,exist_ok=True)
    emit("Y137_D11_MU2_GROUP",group=GROUP,groups=GROUPS,
         buckets=8,source_shards=SHARDS,
         total_Q4_edge_records=total_records,
         unique_shell5_targets=total_targets,
         total_reverse_moves=raw_reverse,
         maximum_incoming_reverse_moves=max_group_sources,
         independent_target_weights_spotcheck=independently_checked_weights,
         exact_target_merge_before_square="PASS",
         accepted_K3_mu2="PARTIAL_Q5_ONLY")
    for t,(z,G) in enumerate(((items[0][0][0],M0),
                             (items[1][0][0],M1))):
        G=make_symmetric(G)
        emit("Y137_D11_MU2_Q5_PART",group=GROUP,
             sample_num=z,
             Q5_mu2_six=encode(G),
             complete_bucket_groups=1,
             actual_full_mu2="NOT_UNTIL_ALL_EIGHT_GROUPS")
    emit("Y137_D11_MU2_GROUP_VERDICT",group=GROUP,
         total_groups_required=GROUPS,
         exact_Q5_reduction="PASS_FOR_GROUP",
         real_mu2="HOLD_UNTIL_GROUP_SUM_AND_K3_Q4",
         original_Wilson_weight="HOLD",issue_137="OPEN")


if __name__=="__main__":
    run()
