#!/usr/bin/env python3
"""Independent, source-pinned 3x4 S3 signed-V1 physical row challenges.

Checks original Stage C archived K3/Q4 spools against a fresh reconstruction
using the historical frozen Y/residual source and the separately implemented
S3 gauge-fixing, 72-move graph, weight and magnetic functions from
independent_move_rule.py. No Stage C source builder/codec is imported.
No floating point, JSON, Fraction, external solver, or true division.

This samples a stated 864 of 2,140,596 K3/Q4 source states across eight
disjoint partitions. It is evidence about *challenged source rows*, not a
replacement for independent full-state signed-mu3 or Perron reconstruction.
"""
import hashlib
import os
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0,os.path.join(ROOT,"independent","y137-real-Q-moment-20261114"))
old_argv=sys.argv[:]
sys.argv=sys.argv[:1]
import mu1_shard as frozen_source
sys.argv=old_argv
sys.path.insert(0,os.path.join(ROOT,"independent","y137-d11-shell5-spill-20261114"))
import independent_move_rule as rule

K3=155378
Q4=1985218
B=1000000000
COLS=8
GROUPS=8
N_K3=27
N_Q4=81
SAMPLES=(69909875505,69949729820)
K3_SHA="36e22e87ed5d5af87f00c3712fb4020ff189325862a449d4899281a2f104de45"
Q4_SHA=(
"4065b826ab9319bb1815db2cebd37d6906eefa0fd360d403b00170f7db95b88b",
"dcdf3b37416d70545eab7628af358ccb61c50d33c891c1424a395614f5e3c1ce",
"8ed217f59afb7808da51234bb246ec37703f7a49e96bb874261eaaa10233b67b",
"1d238882127dda84e755ed44c5754462aadb4d785a269caa4f8421a83c5f89d3",
"266d452170b3a9d7a51acee8482a519d482fc17ccae0a2267137a72fac0abf9e",
"47174192ce7315c9aed74edb710dd00c20b85bdc2403b8b8e6c8a48eeb1e2651",
"1acfe077a80ff8710af30480393b51c708d5ae3f37727fae9dd114dd35213794",
"cb5240e6d3cb4a85c639be56cdd83d3acc5ae2e786abde9ca5769599dd6ff461",
)
POW6=[1]
for _ in range(12):
    POW6.append(6*POW6[-1])
ADDR_LIMIT=6*POW6[-1]

class Refuse(Exception):
    pass

def need(ok,why):
    if not ok:raise Refuse(why)

def encode_key(key):
    need(len(key)==13 and all(0<=x<6 for x in key),"key_domain")
    return sum(t*POW6[i] for i,t in enumerate(key))

def chosen(lo,hi,n,group,tag):
    need(0<=lo<hi and 0<n<=hi-lo,"challenge_partition")
    seed=("Y137-SOURCE-CHALLENGE-20261119|"+str(group)+"|"+tag+
          "|"+K3_SHA+"|"+Q4_SHA[group]).encode("ascii")
    result=set()
    ctr=0
    while len(result)<n:
        h=hashlib.sha256(seed+ctr.to_bytes(8,"little")).digest()
        result.add(lo+int.from_bytes(h,"little")%(hi-lo))
        ctr+=1
    return sorted(result)

def file_digest(path,sha):
    h=hashlib.sha256()
    with open(path,"rb") as inp:
        while True:
            b=inp.read(1<<20)
            if not b:break
            h.update(b)
    need(h.hexdigest()==sha,"immutable_signed_archive_SHA_mismatch")

def records(path,sha,shell,count,wanted):
    # Decode independently of Stage C's c_signed_source_codec, verifying
    # the *entire* archived canonical header sequence and all lane encodings.
    file_digest(path,sha)
    found={}
    last=-1
    n=0
    with open(path,"rb") as inp:
        while True:
            h=inp.read(11)
            if not h:break
            need(len(h)==11,"short_signed_header")
            address=int.from_bytes(h[:8],"little")
            weight,kind,samples=h[8],h[9],h[10]
            need(last<address<ADDR_LIMIT,"noncanonical_order_or_address")
            need(kind==shell and weight in (1,2,3,6) and samples==2,
                 "incorrect_signed_shell_weight_samples")
            last=address
            vectors=[]
            for _ in range(2):
                values=[]
                for _ in range(8):
                    b=inp.read(1)
                    need(len(b)==1,"short_signed_lane_header")
                    length=b[0]&127
                    negative=bool(b[0]&128)
                    need(0<=length<=24,"invalid_signed_lane_width")
                    payload=inp.read(length)
                    need(len(payload)==length,"short_signed_lane_payload")
                    need(length==0 or payload[-1]!=0,"nonminimal_magnitude")
                    need(not negative or length>0,"negative_zero")
                    value=int.from_bytes(payload,"little")
                    need(value.bit_length()<=192,"signed_lane_overflow")
                    values.append(-value if negative else value)
                vectors.append(tuple(values))
            if address in wanted:
                need(address not in found,"duplicate_challenge_address")
                found[address]=(weight,tuple(vectors))
            n+=1
    need(n==count,"signed_source_record_count")
    need(len(found)==len(wanted),"missing_challenged_signed_sources")
    return found

def unpack(packed,width,mask):
    need(packed>=0 and mask==(1<<width)-1 and width>=64,
         "original_signed_residual_lane_domain")
    return tuple((packed>>(width*j))&mask for j in range(8))

def row_challenge(key,weight,source,ball,ex,inner,flat,width,mask,items):
    # Entire 72-move graph is computed via the independent permutation rule.
    need(rule.canonical_from_full(rule.expanded_links(key))==key,
         "independent_S3_canonicality")
    need(rule.canonical_weight(key)==weight,"independent_S3_orbit_weight")
    mag=rule.magnetic_of_key(key)
    need(mag==frozen_source.c.magnetic(frozen_source.c.from_key(key)),
         "independent_magnetic_row")
    neighbors=rule.neighbor_counts(key)
    need(sum(neighbors.values())==72 and
         neighbors==frozen_source.c.neighbors(key),
         "independent_72_electric_moves")
    idx=inner.get(key)
    f=ex["s4"].get(encode_key(key))
    need((idx is None)!=(f is None),"K3_Q4_support_partition")
    matches=0
    directed=0
    reciprocal=0
    boundary=0
    own_R=[]
    for t,(row,_,R_K3,P_Q4) in enumerate(items):
        need(row[0]==SAMPLES[t],"frozen_energy_order")
        R=tuple(R_K3[idx]) if idx is not None else tuple(-a for a in unpack(P_Q4[f],width,mask))
        own_R.append(R)
        near_sum=[0]*8
        for dst,c in neighbors.items():
            j=inner.get(dst)
            q=ex["s4"].get(encode_key(dst))
            if j is not None:
                r=R_K3[j]
            elif q is not None:
                r=tuple(-a for a in unpack(P_Q4[q],width,mask))
            else:
                # The residual is exactly zero off K3+Q4, including Q5.
                r=(0,)*8
            for column in range(8):
                near_sum[column]+=c*r[column]
        d=B*(72+9*mag)-row[0]
        result=tuple(d*R[col]-B*near_sum[col] for col in range(8))
        need(result==source[t],"independent_signed_V1_response_mismatch")
        need(all(abs(v)<(1<<117) for v in result),
             "signed_source_2pow117_amplitude_limit")
        matches+=8
    # Independently re-enumerate one supported reverse edge per row,
    # including the orbit-weight relation, using only the alternative rule.
    supported=[]
    for dst,c in neighbors.items():
        if dst in inner or encode_key(dst) in ex["s4"]:
            supported.append((encode_key(dst),dst,c))
        else:
            boundary+=c
        directed+=c
    need(directed==72,"challenged_72_raw_moves")
    if supported:
        _,dst,c=min(supported,key=lambda p:p[0])
        reverse=rule.neighbor_counts(dst).get(key,0)
        need(weight*c==rule.canonical_weight(dst)*reverse,
             "independent_weighted_reciprocal_edge")
        reciprocal=1
    return matches,directed,reciprocal,boundary,mag

def challenge(group,path3,path4):
    need(0<=group<8,"group_out_of_range")
    ball,ex,inner,flat,width,mask,items=frozen_source.build_inputs()
    need(ball["n"]==K3 and ball["nf"]==Q4 and len(items)==2,
         "original_frozen_support_census")
    need(tuple(row[0] for row,_,_,_ in items)==SAMPLES,
         "two_source_energies")
    lo3=K3*group//8;hi3=K3*(group+1)//8
    lo4=Q4*group//8;hi4=Q4*(group+1)//8
    chosen3=chosen(lo3,hi3,N_K3,group,"K3")
    chosen4=chosen(lo4,hi4,N_Q4,group,"Q4")
    inverse=[None]*K3
    for key,i in inner.items():
        need(0<=i<K3 and inverse[i] is None,"original_K3_index")
        inverse[i]=key
    need(all(k is not None for k in inverse),"missing_K3_index")
    wanted3={encode_key(inverse[i]) for i in chosen3}
    wanted4={ex["code4"][i] for i in chosen4}
    need(len(wanted3)==N_K3 and len(wanted4)==N_Q4,
         "duplicate_selected_canonical_address")
    sources3=records(path3,K3_SHA,3,K3,wanted3)
    sources4=records(path4,Q4_SHA[group],4,hi4-lo4,wanted4)
    totals=[0]*5
    digest=hashlib.sha256()
    for kind,indices,lookup in (("K3",chosen3,sources3),("Q4",chosen4,sources4)):
        for i in indices:
            key=inverse[i] if kind=="K3" else frozen_source.m.decode(ex["code4"][i])
            address=encode_key(key)
            weight,vectors=lookup[address]
            expected_weight=ball["wq"][i] if kind=="K3" else ball["eW"][i]
            need(weight==expected_weight,"challenged_source_orbit_weight")
            row=row_challenge(key,weight,vectors,ball,ex,inner,flat,width,mask,items)
            for k,x in enumerate(row):
                totals[k]+=x
            digest.update((str(address)+"|"+str(weight)+"|"+
              "|".join(",".join(str(v) for v in vector) for vector in vectors)+";").encode("ascii"))
    need(totals[0]==(N_K3+N_Q4)*16 and
         totals[1]==(N_K3+N_Q4)*72 and totals[2]>0,
         "independent_challenge_coverage")
    print("Y137_INDEPENDENT_SOURCE_CHALLENGE|group="+str(group)+
          "|K3_disjoint_range="+str(lo3)+","+str(hi3)+
          "|Q4_disjoint_range="+str(lo4)+","+str(hi4)+
          "|K3_challenged_rows="+str(N_K3)+
          "|Q4_challenged_rows="+str(N_Q4)+
          "|exact_signed_lanes="+str(totals[0])+
          "|independent_raw_moves="+str(totals[1])+
          "|weighted_reverse_edges="+str(totals[2])+
          "|off_support_moves="+str(totals[3])+
          "|magnetic_number_sum="+str(totals[4])+
          "|source_digest="+digest.hexdigest()+
          "|K3_original_archive_SHA=PASS|Q4_original_archive_SHA=PASS"+
          "|independent_S3_72moves=PASS|signed_V1_two_energies=PASS"+
          "|whole_Q_mu3=NOT_INDEPENDENTLY_RECOMPUTED"+
          "|first_Wilson_weight=FORMAL_HOLD|json=0",flush=True)

def toy():
    sample=(0,)*13
    need(rule.canonical_weight(sample)==1 and
         rule.magnetic_of_key(sample)==0 and
         sum(rule.neighbor_counts(sample).values())==72,
         "source_independent_rule_toy")
    need(K3+Q4==2140596 and K3+Q4+18598040==20738636,
         "frozen_source_census")
    a=chosen(0,1000,27,0,"K3")
    b=chosen(0,1000,27,0,"K3")
    need(a==b and len(set(a))==27,"frozen_challenge_determinism")
    for g in range(8):
        need(len(chosen(K3*g//8,K3*(g+1)//8,N_K3,g,"K3"))==N_K3,
             "K3_partition_independence")
        need(len(chosen(Q4*g//8,Q4*(g+1)//8,N_Q4,g,"Q4"))==N_Q4,
             "Q4_partition_independence")
    print("Y137_INDEPENDENT_SOURCE_CHALLENGE_TOY|independent_S3_torus=PASS"+
          "|frozen_sha_seed=DETERMINISTIC|disjoint_parts=8"+
          "|selected_K3_per_part=27|selected_Q4_per_part=81"+
          "|real_signed_sources=NOT_RUN|json=0",flush=True)

def main(args):
    try:
        if args==["toy"]:
            toy()
        elif len(args)==4 and args[0]=="real":
            challenge(int(args[1]),args[2],args[3])
        else:
            raise Refuse("usage_toy_or_real_GROUP_K3_SPOOL_Q4_SPOOL")
    except (Refuse,KeyError,ValueError,OSError,OverflowError,MemoryError) as e:
        print("Y137_INDEPENDENT_SOURCE_CHALLENGE_HOLD|reason="+str(e)+
              "|first_Wilson_weight=FORMAL_HOLD|json=0",flush=True)
        raise SystemExit(1) from None

if __name__=="__main__":
    main(sys.argv[1:])
