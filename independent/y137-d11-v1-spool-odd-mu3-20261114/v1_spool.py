#!/usr/bin/env python3
"""Replay accepted K3 Q5 sources into durable exact V1 amplitudes.

Reads archived immutable run 43606393196 eight-way Q4 source buckets.
For each destination, combines ALL source-shard edges before multiplying
in W; reconstructs the accepted mu2 Q5 Gram byte-for-byte. Emits an
address-keyed binary V1=XR spool (stored as V1/b nonnegative packed lanes)
for later on-support odd mu3, with no new 142.9M Q4 move enumeration.
"""
import hashlib
import heapq
import os
import struct
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
sys.path.insert(0,os.path.join(ROOT,"independent",
                              "y137-d11-shell5-spill-20261114"))
ARGS=sys.argv[:]
sys.argv=sys.argv[:1]
import reduce_full_mu2 as old
sys.argv=ARGS

GROUP=old.GROUP
SHARDS=old.SHARDS
BUCKETS=old.BUCKETS
GROUPS=old.GROUPS
COLS=old.COLS
B=old.B
HEADER=struct.Struct("<Q B H H")
OUT_DIR=os.environ.get("Y137_D11_V1_OUTPUT",
                       os.path.join(ROOT,"build","y137-d11-v1"))
OLD_GROUP_DIR=os.environ.get("Y137_D11_V1_OLD_GROUP",
                            os.path.join(ROOT,"build","y137-d11-mu2-previous-group"))
MAX_SPOOL_BYTES=3*1024*1024*1024


def need(ok,why):
    if not ok:
        print("Y137_D11_V1_REFUSE|group="+str(GROUP)+
              "|reason="+why+"|json=0",flush=True)
        raise SystemExit(1)


def emit(label,**fields):
    print(label+"|"+"|".join(str(k)+"="+str(v)
                           for k,v in fields.items())+"|json=0",flush=True)


def old_group_grams():
    path=os.path.join(OLD_GROUP_DIR,"GROUP-"+str(GROUP)+".hbp")
    need(os.path.isfile(path),"missing_previous_frozen_group_receipt")
    result={}
    with open(path,encoding="utf-8") as f:
        for line in f:
            if not line.startswith("Y137_D11_MU2_Q5_PART|"):
                continue
            pieces=dict(x.split("=",1) for x in line.strip().split("|")[1:])
            key=int(pieces["sample_num"])
            need(key not in result and int(pieces["group"])==GROUP,
                 "wrong_old_Q5_group")
            result[key]=pieces["Q5_mu2_six"]
    need(len(result)==2,"expected_two_old_Q5_samples")
    return result


def spool_record(target,w,packed0,packed1,width):
    need(0<=target<(1<<64) and w in (1,2,3,6),
         "bad_v1_target_or_weight")
    limit=1<<(width*COLS)
    need(0<=packed0<limit and 0<=packed1<limit,
         "packed_lane_overflow")
    size0=(packed0.bit_length()+7)//8
    size1=(packed1.bit_length()+7)//8
    need(size0<=65535 and size1<=65535,"spool_u16_length_overflow")
    return (HEADER.pack(target,w,size0,size1)+
            packed0.to_bytes(size0,"little")+
            packed1.to_bytes(size1,"little"))


def decode_record(record):
    need(len(record)>=HEADER.size,"short_v1_record")
    target,w,n0,n1=HEADER.unpack_from(record)
    need(HEADER.size+n0+n1==len(record),"truncated_v1_record")
    p0=int.from_bytes(record[HEADER.size:HEADER.size+n0],"little")
    p1=int.from_bytes(record[HEADER.size+n0:],"little")
    return target,w,p0,p1


def toy():
    width=16
    p0=sum((j+1)<<(width*j) for j in range(COLS))
    p1=sum((j+3)<<(width*j) for j in range(COLS))
    rec=spool_record(12345,6,p0,p1,width)
    need(decode_record(rec)==(12345,6,p0,p1),
         "toy_roundtrip")
    refused=False
    try:
        decode_record(rec[:-1])
    except SystemExit:
        refused=True
    need(refused,"truncation_not_refused")
    refused=False
    try:
        spool_record(12345,6,1<<(width*COLS),p1,width)
    except SystemExit:
        refused=True
    need(refused,"invalid_lane_overflow_not_refused")
    # All two origin source-shard values MUST be added before Gram.
    a=p0
    b=p0
    one=old.empty()
    old.add_upper(one,a+b,6,width,(1<<width)-1)
    wrong=old.empty()
    old.add_upper(wrong,a,6,width,(1<<width)-1)
    old.add_upper(wrong,b,6,width,(1<<width)-1)
    need(one!=wrong,"dropped_cross_shard_terms")
    emit("Y137_D11_V1_TOY",complete_target_packed_record="PASS",
         tampered_length="REFUSED",oversized_lane="REFUSED",
         premerge_outer_product="REJECTED",real_V1="NOT_COMPUTED")


def run():
    need(0<=GROUP<GROUPS,"bad_group")
    ball,ex,inner,flat,width,mask,items=old.src.build_inputs()
    need(ball["nf"]==1985218 and len(items)==2,
         "accepted_source_changed")
    frozen=old_group_grams()
    expected=(items[0][0][0],items[1][0][0])
    need(set(frozen)==set(expected),"original_two_sample_energies")
    P0=items[0][3]
    P1=items[1][3]
    gram=[old.empty(),old.empty()]
    rows=0
    records=0
    byte_count=0
    h=hashlib.sha256()
    os.makedirs(OUT_DIR,exist_ok=True)
    path=os.path.join(OUT_DIR,"GROUP-"+str(GROUP)+".v1")
    with open(path,"wb") as f:
        for bucket in range(GROUP,BUCKETS,GROUPS):
            arrays=[old.inputs(sh,bucket) for sh in range(SHARDS)]
            n=sum(len(x) for x in arrays)
            need(n>0,"empty_bucket")
            records+=n
            target=None
            w=0
            p0=0
            p1=0
            reverse_count=0
            previous_f=-1
            bucket_targets=0
            def flush():
                nonlocal rows,byte_count,bucket_targets
                if target is None:
                    return
                need(1<=reverse_count<=72,"wrong_incoming_degree")
                item=spool_record(target,w,p0,p1,width)
                need(decode_record(item)==(target,w,p0,p1),
                     "spool_roundtrip")
                byte_count+=len(item)
                need(byte_count<=MAX_SPOOL_BYTES,"bounded_spool_limit")
                f.write(item)
                h.update(item)
                old.add_upper(gram[0],p0,w,width,mask)
                old.add_upper(gram[1],p1,w,width,mask)
                rows+=1
                bucket_targets+=1
            for code,ix,rev,weight,shard in heapq.merge(
                    *(iter(x) for x in arrays)):
                if code!=target:
                    flush()
                    target=code
                    w=weight
                    p0=0
                    p1=0
                    reverse_count=0
                    previous_f=-1
                    if bucket_targets<8:
                        need(old.c.weight(old.m.decode(code))==w,
                             "independent_target_weight")
                need(weight==w and ix!=previous_f,
                     "target_weight_or_duplicate_source")
                previous_f=ix
                reverse_count+=rev
                p0+=rev*P0[ix]
                p1+=rev*P1[ix]
            flush()
            emit("Y137_D11_V1_BUCKET",group=GROUP,bucket=bucket,
                 edge_records=n,destinations=bucket_targets,
                 W_target_merge="PASS")
            del arrays
    need(os.path.getsize(path)==byte_count,
         "spooled_byte_count_mismatch")
    for i,z in enumerate(expected):
        matrix=old.encode(old.make_symmetric(gram[i]))
        need(matrix==frozen[z],
             "new_V1_spool_gram_not_equal_accepted_mu2_Q5")
        emit("Y137_D11_V1_POINT",group=GROUP,sample_num=z,
             exact_spooled_shell5_mu2_gram="MATCHES_ACCEPTED",
             inherited_mu2_Q5_sha256=hashlib.sha256(
                 matrix.encode("ascii")).hexdigest(),
             usable_for_next_odd_quadratic=1)
    emit("Y137_D11_V1_VERDICT",group=GROUP,
         source="ACCEPTED_K3_W_WEIGHTED",
         original_mu2_run="43606393196",
         total_Q4_edge_records=records,
         exact_shell5_targets=rows,
         v1_over_b_storage="UNSIGNED_PACKED_EIGHT_LANES_BOTH_SAMPLES",
         physical_V1_scaling="MULTIPLY_BY_1E9",
         packed_lane_width=width,
         output_bytes=byte_count,output_sha256=h.hexdigest(),
         all_target_Grams_match_original_mu2="PASS",
         outward_operator_passes_completed=1,
         degree11_total_outward_passes=10,
         real_mu3="NOT_COMPUTED",
         actual_first_Wilson_weight="HOLD",issue_137="OPEN")


if __name__=="__main__":
    if len(sys.argv)==2 and sys.argv[1]=="--toy":
        toy()
    elif len(sys.argv)==1:
        run()
    else:
        need(False,"bad_mode")
