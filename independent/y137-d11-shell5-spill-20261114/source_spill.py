#!/usr/bin/env python3
"""Bounded true 3x4 accepted-K3 shell5 frontier spool for degree-11 mu2.

Real pilot uses the same frozen original accepted-K3 vectors as PR #193,
but constructs every outgoing electric move from a bounded subset of Q4
sources. Raw edge stream is recoverable, sorted and independently replayed.
A subset of source rows is NEVER represented as a whole-Q moment.
"""
import hashlib
import os
import struct
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
sys.path.insert(0,os.path.join(ROOT,"independent",
                              "y137-real-Q-moment-20261114"))
import mu1_shard as orig

m=orig.m
c=orig.c
B=orig.B
COLS=8
RECORD=struct.Struct("<QIBB")
MAX_REAL_SOURCES=1024
MAX_REAL_EVENTS=100000
MAX_REAL_TARGETS=100000
OUTPATH=os.path.join(ROOT,"build","y137-d11-shell5",
                     "REAL-SHELL5-PILOT.bin")


def need(condition,why):
    if not condition:
        print("Y137_D11_S5_REFUSE|reason="+why+"|json=0",flush=True)
        raise SystemExit(1)


def emit(name,**fields):
    print(name+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())+
          "|json=0",flush=True)


def bytehash(data):
    return hashlib.sha256(data).hexdigest()


def pairgram(pairs,source,weights):
    """6W-weighted complete 8x8 Gram on represented *subset* of targets."""
    M=[[0]*COLS for _ in range(COLS)]
    for key,value in pairs.items():
        w=weights[key]
        vals=[(value>>(source["width"]*i))&source["mask"]
              for i in range(COLS)]
        for i,vi in enumerate(vals):
            for j,vj in enumerate(vals):
                M[i][j]+=6*w*vi*vj
    return M


def fmt(M):
    return ";".join(",".join(str(v) for v in row) for row in M)


def fixedwidth_verify(pack,width,limit):
    mask=(1<<width)-1
    values=[(pack>>(width*i))&mask for i in range(COLS)]
    need(max(values)<=limit,"lane_width_overflow")
    need(orig.m.pack([values],width)[0]==pack,
         "lane_roundtrip_mismatch")
    return values


def replay(records,source0,source1,width):
    """Read unsigned fixed records independently from source-driven map.

    This is exact sparse reduction; in full production, each bucket will
    collect records from all eight source shards before weighted squaring.
    """
    need(len(records)%RECORD.size==0,"incomplete_binary_record")
    mask=(1<<width)-1
    A={}
    Bmap={}
    weights={}
    maxterm=0
    for offset in range(0,len(records),RECORD.size):
        key,f,reverse,wg=RECORD.unpack_from(records,offset)
        need(0<=f<len(source0) and 1<=reverse<=72 and
             wg in (1,2,3,6),"bad_record_field")
        need(weights.get(key,wg)==wg,"inconsistent_orbit_weight")
        weights[key]=wg
        A[key]=A.get(key,0)+reverse*source0[f]
        Bmap[key]=Bmap.get(key,0)+reverse*source1[f]
        maxterm+=reverse
    for dic in (A,Bmap):
        for value in dic.values():
            need(len(fixedwidth_verify(value,width,mask))==COLS,
                 "decoded_lane_count")
    return A,Bmap,weights,maxterm


def toy():
    """Independent small weighted Q4->Q5 many-to-one coalescence.

    Two source rows with different orbit weights both lead to one Q5
    orbit. Separate-shard Gram squaring must FAIL to reproduce the
    globally reduced Gram, and a changed binary edge must be rejected.
    """
    width=32
    left=[orig.m.pack([[2,3,5,7,11,13,17,19]],width)[0],
          orig.m.pack([[23,29,31,37,41,43,47,53]],width)[0]]
    right=[orig.m.pack([[59,61,67,71,73,79,83,89]],width)[0],
           orig.m.pack([[97,101,103,107,109,113,127,131]],width)[0]]
    # w0=3, w1=6, common target w5=6, edges multiplicities 2 and 3;
    # reverse flux (3*2)/6=1 and (6*3)/6=3.
    a=RECORD.pack(12345,0,1,6)
    b=RECORD.pack(12345,1,3,6)
    raw=a+b
    x,y,w,_=replay(raw,left,right,width)
    want0=left[0]+3*left[1]
    want1=right[0]+3*right[1]
    need(x=={12345:want0} and y=={12345:want1},
         "toy_target_coalescence")
    A=pairgram(x,{"width":width,"mask":(1<<width)-1},w)
    AA,_,wa,_=replay(a,left,right,width)
    AB,_,wb,_=replay(b,left,right,width)
    separate=[[pairgram(AA,{"width":width,"mask":(1<<width)-1},wa)[i][j]+
               pairgram(AB,{"width":width,"mask":(1<<width)-1},wb)[i][j]
               for j in range(COLS)] for i in range(COLS)]
    need(A!=separate and all(A[i][i]>separate[i][i]
                             for i in range(COLS)),
         "cross_shard_target_overlap_not_detected")
    corrupt=bytearray(raw)
    corrupt[-2]=2
    x_bad,_,_,_=replay(bytes(corrupt),left,right,width)
    need(x_bad!=x and bytehash(bytes(corrupt))!=bytehash(raw),
         "corrupted_edge_not_detected")
    # Dropped exterior destination and a zero reverse coefficient MUST
    # fail the independent event census and field validator.
    need(len(raw)!=len(raw[:-RECORD.size]),
         "lost_edge_not_detected")
    bad=RECORD.pack(12345,1,0,6)
    refused=False
    try:
        replay(bad,left,right,width)
    except SystemExit:
        refused=True
    need(refused,"missing_reverse_weight_not_rejected")
    emit("Y137_D11_S5_TOY",source_rows=2,
         shared_shell5_target=1,
         W_nonidentity=1,
         packed_8_lane_exact="PASS",
         cross_partition_square_before_reduction="REJECTED",
         corrupted_edge="REJECTED",
         missing_outgoing_move="DETECTED_BY_CENSUS",
         zero_reverse="REJECTED",
         fullQ_moment="NOT_COMPUTED")


def real():
    ball,ex,inner,flat,width,mask,items=orig.build_inputs()
    need(ball["n"]==155378 and ball["nf"]==1985218,
         "frozen_K3_shell4_geometry_changed")
    take=min(MAX_REAL_SOURCES,ball["nf"])
    sources=[items[0][3],items[1][3]]
    need(len(sources[0])==ball["nf"] and len(sources[1])==ball["nf"],
         "wrong_source_vector_count")
    os.makedirs(os.path.dirname(OUTPATH),exist_ok=True)
    rows=0
    moves=0
    q3=q4=q5=projected=0
    events=[]
    sample_edges=0
    for f in range(take):
        src=m.decode(ex["code4"][f])
        wf=ball["eW"][f]
        need(c.weight(src)==wf,"true_Q4_weight_changed")
        adjacent=c.neighbors(src)
        need(sum(adjacent.values())==72,"source_row_not_72")
        rows+=1
        moves+=72
        for dst,cc in adjacent.items():
            if dst in flat:
                projected+=cc
                continue
            if dst in inner:
                q3+=cc
                continue
            code=m.code(dst)
            if code in ex["s4"]:
                q4+=cc
                continue
            wg=c.weight(dst)
            need(wg in (1,2,3,6),"unexpected_orbit_weight")
            need(wf*cc%wg==0,"noninteger_weighted_reverse")
            reverse=wf*cc//wg
            need(1<=reverse<=72,"bad_reverse_multiplicity")
            if sample_edges<48:
                # Same canonicalizer, but independently reverse the raw
                # direction. A separate source implementation is still
                # mandatory for a production certificate.
                need(c.neighbors(dst).get(src,0)==reverse,
                     "explicit_reverse_electric_row")
                sample_edges+=1
            events.append(RECORD.pack(code,f,reverse,wg))
            q5+=cc
        need(len(events)<=MAX_REAL_EVENTS,"bounded_event_budget")
    need(rows==take and moves==rows*72 and
         moves==q3+q4+q5+projected,
         "complete_72_move_partition")
    raw=b"".join(events)
    need(len(raw)==len(events)*RECORD.size,"binary_event_length")
    with open(OUTPATH,"wb") as handle:
        handle.write(raw)
    need(open(OUTPATH,"rb").read()==raw,"binary_spool_roundtrip")
    reduced0,reduced1,weights,sum_reverse=replay(
        raw,sources[0],sources[1],width)
    # Producer check with a SECOND code path: sorted record reduction.
    grouped={}
    for key,f,reverse,wg in sorted(RECORD.iter_unpack(raw)):
        a,b=grouped.get(key,(0,0))
        grouped[key]=(a+reverse*sources[0][f],
                      b+reverse*sources[1][f])
        need(weights[key]==wg,"wrong_record_wg")
    need(len(grouped)==len(reduced0) and
         all(v==(reduced0[k],reduced1[k]) for k,v in grouped.items()),
         "independent_sorted_reduction_mismatch")
    limit=(72*max(max(orig.unpack(v,width,mask)) for v in sources[0][:take]))+1
    need(limit>0,"bad_positive_source")
    # We do NOT square partial blocks as if they were complete shell5
    # targets. This is a diagnostic only and may not be used as mu2.
    grams=[pairgram(v,{"width":width,"mask":mask},weights)
           for v in (reduced0,reduced1)]
    emit("Y137_D11_S5_FREEZE",model="PERIODIC_3x4_S3_r9",
         target_degree=11,total_required_moments_per_sample=22,
         accepted_K3_mu0_mu1="PRESERVED",
         real_shard_rows_max=MAX_REAL_SOURCES,
         memory_method="FIXED_WIDTH_BINARY_EVENT_STREAM",
         source_SHA_verification="INHERITED_ACCEPTED_K3",
         actual_mu2="NOT_COMPUTED")
    emit("Y137_D11_S5_PILOT",shell4_first_index=0,
         shell4_stop_index=take,actual_source_rows=rows,
         raw_electric_moves=moves,into_K3=q3,within_Q4=q4,
         into_shell5=q5,projected_P=projected,
         unique_shell5_targets=len(reduced0),
         shell5_records=len(events),
         fixed_record_bytes=RECORD.size,
         spool_bytes=len(raw),spool_sha256=bytehash(raw),
         aggregate_reverse_coefficient=sum_reverse,
         independent_row_reverse_checks=sample_edges,
         exact_72_move_accounting="PASS",
         exact_weighted_flux="PASS",
         second_sorted_reduction="PASS")
    for i,G in enumerate(grams):
        emit("Y137_D11_S5_SAMPLE",sample_num=items[i][0][0],
             source="ACCEPTED_K3",
             partial_shell5_Gram_six_sha256=bytehash(fmt(G).encode("ascii")),
             partial_shell5_Gram_six=fmt(G),
             partial_target_reduction="EXACT_FOR_BOUND_SUBSET",
             entire_mu2="NOT_COMPUTED",
             source_replay="FROZEN_TWO_SAMPLES")
    emit("Y137_D11_S5_VERDICT",real_3x4_shell5_moves="PARTIAL_SOURCE_PILOT",
         pilot_all_outgoing_moves_accounted=1,
         real_mu2="HOLD_NEEDS_ALL_EIGHT_SOURCE_SHARDS_AND_CROSS_SHARD_MERGE",
         remaining_degree11_moments_per_sample=20,
         separate_canonicalizer_review="PENDING",
         first_Wilson_weight="HOLD",issue_137="OPEN")


def main():
    mode=sys.argv[1] if len(sys.argv)>1 else "--toy"
    need(mode in ("--toy","--real"),"bad_mode")
    toy()
    if mode=="--real":
        real()


if __name__=="__main__":
    main()
