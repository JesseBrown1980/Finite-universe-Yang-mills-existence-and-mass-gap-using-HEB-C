#!/usr/bin/env python3
"""Independently reconstruct original physical Q5 V1 sources from Q4 residuals.

The Q5 spool is fully authenticated against frozen B-stage SHA, then 27
SHA-selected actual Q5 rows per group are rebuilt using independently authored
S3 canonical gauge and all 72 raw moves. Q5 residual R=0 and Q4 R=-P,
therefore V1_Q5=(D-b*C)R=b*sum_Q4 c*P_Q4. Both original energies and all
eight exact integer lanes are compared with the original frozen Q5 physical
source. Original K3 trial Y / Q4 packed P remain frozen premises.

Source sample ≠ full independent 20,738,636-state mu3 production.
"""
import hashlib
import os
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0,os.path.join(ROOT,"independent","y137-real-Q-moment-20261114"))
import mu1_shard as src
sys.path.insert(0,os.path.join(ROOT,"independent","y137-d11-shell5-spill-20261114"))
import independent_move_rule as rule

B=1000000000
Q5_ROWS=(435324,4439918,988399,2812763,822474,3973928,1612450,3512784)
Q5_BYTES=(72717336,750840749,166069410,476041564,137545818,672121828,270439868,595123535)
Q5_SHA=(
"3f561c26f3cf5b355ab769ae96e9da8ceaa141186fb5ecb80cc1ec4227e4c589",
"aaf435dcac9fad331ee0a0391dde0e66852426372aa7c34fac2416492485f5fc",
"f09edac5b00ab67f1c3189a4d98e6300529787bba81caf0c345cd05613985856",
"5c4017c73f869ec9187e1a1e80f6cfb1ac318521bd2c728cafb4ccbda9dba477",
"68eba145b904f6d9b792f8530420d5854ff8775239e2091aba12cc2952f15164",
"c3db5e2e6c70c4852df5bdeff5b1bcf9ec4983fd5f6288e0dc2a774652ceb59b",
"8ec64a5ba49040ba0dd835e95357ccc220785a1012850c200f81604ac7ee079a",
"98eec0d6972078dcf07c9ca36ee932f62b2dd2022725f7f91d88894e592b0ef0",
)
BITS=82
MASK=(1<<BITS)-1
N=27
ADDR_MAX=6**13

class Refuse(Exception):
    pass

def need(ok,reason):
    if not ok:raise Refuse(reason)

def key_address(key):
    total=0
    for x in reversed(key):
        total=total*6+x
    return total

def selected(group):
    need(0<=group<8,"group_bounds")
    seed=("Y137-INDEPENDENT-Q5-PHYSICAL-SOURCE-20261119|"+
          str(group)+"|"+Q5_SHA[group]).encode("ascii")
    indexes=set()
    ctr=0
    while len(indexes)<N:
        h=hashlib.sha256(seed+ctr.to_bytes(8,"little")).digest()
        indexes.add(int.from_bytes(h,"little")%Q5_ROWS[group])
        ctr+=1
    return indexes

def stream_selected(path,group):
    # One pass both verifies original full Q5 SHA and selects challenge rows.
    picks=selected(group)
    h=hashlib.sha256()
    found={}
    rows=0
    byte_count=0
    bucket_seq=0
    prior=-1
    with open(path,"rb") as f:
        while True:
            header=f.read(13)
            if not header:break
            need(len(header)==13,"truncated_Q5_header")
            address=int.from_bytes(header[:8],"little")
            weight=header[8]
            a=int.from_bytes(header[9:11],"little")
            b=int.from_bytes(header[11:13],"little")
            need(0<=address<ADDR_MAX and weight in (1,2,3,6),
                 "invalid_Q5_address_weight")
            need(0<=a<=82 and 0<=b<=82,"invalid_Q5_packed_lengths")
            content=f.read(a+b)
            need(len(content)==a+b,"truncated_Q5_packed_amplitude")
            need((a==0 or content[a-1]!=0) and
                 (b==0 or content[-1]!=0),"nonminimal_Q5_packed_samples")
            bucket=address%64
            need(bucket%8==group,"incorrect_Q5_group")
            if bucket==group+bucket_seq*8:
                need(address>prior,"unsorted_original_Q5_bucket")
            else:
                need(bucket_seq<7 and bucket==group+(bucket_seq+1)*8,
                     "missing_or_reordered_Q5_bucket")
                bucket_seq+=1
                prior=-1
            prior=address
            h.update(header);h.update(content)
            byte_count+=13+a+b
            if rows in picks:
                p0=int.from_bytes(content[:a],"little")
                p1=int.from_bytes(content[a:],"little")
                need((p0>>(BITS*8))==0 and (p1>>(BITS*8))==0,
                     "Q5_eight_lane_capacity")
                v0=tuple((p0>>(BITS*k))&MASK for k in range(8))
                v1=tuple((p1>>(BITS*k))&MASK for k in range(8))
                need(address not in found,"duplicate_selected_Q5_address")
                found[address]=(weight,(v0,v1))
            rows+=1
    need(rows==Q5_ROWS[group] and byte_count==Q5_BYTES[group],
         "original_Q5_complete_group_count_or_bytes")
    need(bucket_seq==7,"missing_last_Q5_bucket")
    need(h.hexdigest()==Q5_SHA[group],"original_Q5_full_SHA_mismatch")
    need(len(found)==N,"selected_Q5_rows_missing")
    return found

def q4_positive(source,idx,width,mask):
    packed=source[idx]
    need(packed>=0 and mask==(1<<width)-1,"original_Q4_packed_domain")
    return tuple((packed>>(width*k))&mask for k in range(8))

def physical_row(address,weight,orig,inputs):
    ball,ex,inner,flat,width,mask,items=inputs
    need(len(items)==2 and (items[0][0][0],items[1][0][0])==
         (69909875505,69949729820),"frozen_original_energies")
    key=src.m.decode(address)
    need(key_address(key)==address and
         rule.canonical_from_full(rule.expanded_links(key))==key,
         "independent_Q5_canonicality")
    need(rule.canonical_weight(key)==weight,
         "independent_Q5_weight")
    need(key not in inner and address not in ex["s4"] and key not in flat,
         "Q5_not_disjoint_from_frozen_residual")
    near=rule.neighbor_counts(key)
    need(sum(near.values())==72 and
         near==src.c.neighbors(key),"independent_Q5_72_electric_moves")
    magnetic=rule.magnetic_of_key(key)
    need(magnetic==src.c.magnetic(src.c.from_key(key)),
         "independent_Q5_magnetic")
    links=[]
    for dest,mult in near.items():
        need(mult>0,"Q5_zero_move")
        target=key_address(dest)
        f=ex["s4"].get(target)
        need(dest not in inner and dest not in flat,
             "unexpected_Q5_K3_or_flat_neighbor")
        if f is not None:
            reverse=rule.neighbor_counts(dest).get(key,0)
            need(weight*mult==rule.canonical_weight(dest)*reverse,
                 "independent_Q5_Q4_weighted_reverse")
            links.append((f,mult))
    need(len(links)>0,"Q5_without_original_Q4_boundary")
    for t,(_,_,_,positive) in enumerate(items):
        expected=[0]*8
        for f,mult in links:
            p=q4_positive(positive,f,width,mask)
            for c in range(8):
                expected[c]+=mult*p[c]
        # Stage C stores Q5 V1 / b, so divide by the known positive b.
        need(tuple(expected)==orig[t],
             "original_Q5_packed_source_not_equal_independent_Q4_boundary")
        need(all(0<=v<(1<<82) for v in expected),
             "Q5_source_packed_lane_limit")
    return 72, len(links), magnetic

def real(group,path):
    found=stream_selected(path,group)
    inputs=src.build_inputs()
    need(inputs[0]["n"]==155378 and inputs[0]["nf"]==1985218,
         "historical_K3_Q4_support")
    checked=0
    connections=0
    magnets=0
    h=hashlib.sha256()
    for address,(w,samples) in sorted(found.items()):
        moves,edges,magnetic=physical_row(address,w,samples,inputs)
        checked+=moves
        connections+=edges
        magnets+=magnetic
        h.update((str(address)+"|"+str(w)+"|"+
                  "|".join(",".join(map(str,v)) for v in samples)+";").encode("ascii"))
    need(checked==72*N and connections>=N,"independent_Q5_coverage")
    print("Y137_INDEPENDENT_Q5_BOUNDARY|group="+str(group)+
          "|actual_Q5_states="+str(N)+
          "|independent_raw_moves="+str(checked)+
          "|Q5_Q4_reverse_edge_types="+str(connections)+
          "|exact_original_two_energy_lanes="+str(16*N)+
          "|magnetic_sum="+str(magnets)+
          "|original_all_group_rows="+str(Q5_ROWS[group])+
          "|original_all_group_bytes="+str(Q5_BYTES[group])+
          "|original_Q5_full_sha256="+Q5_SHA[group]+
          "|challenged_source_sha256="+h.hexdigest()+
          "|original_Q5_archive_identity=PASS"+
          "|independent_S3_and_Q4_boundary=PASS"+
          "|two_original_Q5_packed_amplitudes=EXACT"+
          "|whole_Q_mu3=RECONSTRUCTION_OPEN"+
          "|Wilson_weight=CONDITIONAL_FORMAL_HOLD|json=0",flush=True)

def toy():
    need(N==27 and sum(Q5_ROWS)==18598040 and
         sum(Q5_BYTES)==3140900108 and len(Q5_SHA)==8,
         "original_Q5_census")
    need(rule.canonical_weight((0,)*13)==1 and
         sum(rule.neighbor_counts((0,)*13).values())==72,
         "independent_S3_72_toy")
    for g in range(8):
        need(selected(g)==selected(g) and len(selected(g))==N,
             "deterministic_Q5_challenges")
    # Error in two-energy lane split and nonminimal payloads cannot pass.
    v=sum((i+1)<<(BITS*i) for i in range(8))
    packed=v.to_bytes((v.bit_length()+7)//8,"little")
    need(tuple((int.from_bytes(packed,"little")>>(BITS*i))&MASK
               for i in range(8))==tuple(range(1,9)),
         "82bit_Q5_lanes_toy")
    print("Y137_INDEPENDENT_Q5_BOUNDARY_TOY|72_S3_moves=PASS"+
          "|Q5_source_archive_count=18598040"+
          "|Q5_source_archive_bytes=3140900108"+
          "|eight_disjoint_SHA_selected_groups=PASS"+
          "|packed_eight_82bit_lanes=PASS"+
          "|real_Q5_source_rows=NOT_RUN|json=0",flush=True)

def main():
    try:
        need(len(sys.argv)==1,"no_cli_args")
        if os.environ.get("Y137_Q5_MODE","toy")=="toy":
            toy()
        else:
            need(os.environ.get("Y137_Q5_MODE")=="real","mode")
            real(int(os.environ["Y137_Q5_GROUP"]),os.environ["Y137_Q5_ARCHIVE"])
    except (Refuse,KeyError,ValueError,OSError,OverflowError,MemoryError) as e:
        print("Y137_INDEPENDENT_Q5_BOUNDARY_HOLD|reason="+str(e)+
              "|first_Wilson_weight=FORMAL_HOLD|json=0",flush=True)
        raise SystemExit(1) from None

if __name__=="__main__":
    main()
