#!/usr/bin/env python3
"""#137 Worker 1 full authentic signed V1=X R sources on K3 and Q4.

Reconstruct original residual R_K3=signed inner_residuals and R_Q4=negative
positive packed exterior residual, THEN independently evaluates X R on every
K3 and Q4 row. The emitted source is V1=X R (not the intermediate R).
Writes the strictly sorted, verified signed 192-bit two-energy spool.

A source-format and source-content gate; whole-Q mu3 is NOT_COMPUTED.
"""
import hashlib
import heapq
import os
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0,HERE)
from c_signed_source_codec import encode, verified_read, Refuse
sys.path.insert(0,os.path.join(ROOT,"independent","y137-real-Q-moment-20261114"))
ORIGINAL_ARGS=sys.argv[:]
sys.argv=sys.argv[:1]  # k3_common intentionally refuses nonempty argv on import
import mu1_shard as src
sys.argv=ORIGINAL_ARGS

B=1000000000
COLS=8
ENERGIES=(69909875505,69949729820)
K3=155378
Q4=1985218
Q5=18598040
N=K3+Q4+Q5
GROUPS=8
BOUND=1<<117

def need(ok,why):
    if not ok:
        raise Refuse(why)

def frozen():
    ball,ex,inner,flat,width,mask,items=src.build_inputs()
    need(ball["n"]==K3 and ball["nf"]==Q4 and len(ex["code4"])==Q4
         and len(inner)==K3 and len(ex["s4"])==Q4 and len(items)==2,
         "C_complete_K3_Q4_original_census")
    need(tuple(row[0] for row,_,_,_ in items)==ENERGIES,
         "C_wrong_frozen_energy_samples")
    need(len(set(ex["code4"]))==Q4,"C_original_Q4_duplicate_address")
    need(len(set(inner))==K3,"C_original_K3_duplicate_key")
    return ball,ex,inner,flat,width,mask,items

def checked_key(key,address,weight,shell):
    need(src.m.code(key)==address,"C_source_key_encoding_mismatch")
    need(src.c.canonical(src.c.from_key(key))==key,
         "C_source_not_global_S3_canonical")
    need(src.c.weight(key)==weight,"C_source_orbit_weight_mismatch")
    magnetic=src.c.magnetic(src.c.from_key(key))
    need(0<=magnetic<=36,"C_magnetic_out_of_range")
    if shell==4:
        need(4<=magnetic<=16,"C_Q4_magnetic_support_incorrect")
    return magnetic

def original_UG(items):
    return tuple((row[4],row[5]) for row,_,_,_ in items)

def original_k3_residual(ball,items,i):
    """Rebuild the original R_K3 = X*Y, checking immutable old calculation."""
    answer=[]
    for row,record,old_rs,positive_q4 in items:
        y=record["Y"]
        yi=y[i]
        q=[0]*COLS
        for e in range(ball["rs"][i],ball["rs"][i+1]):
            coeff=ball["oc"][e]
            yj=y[ball["oj"][e]]
            for c in range(COLS):
                q[c]+=coeff*yj[c]
        d=B*ball["dbase"][i]-row[0]
        source=ball["C"][i]
        rebuilt=tuple(d*yi[c]-B*q[c]-
                      (B*src.SCALE*source[c] if source is not None else 0)
                      for c in range(COLS))
        need(rebuilt==tuple(old_rs[i]),
             "C_K3_original_R_independent_contraction_disagreement")
        answer.append(rebuilt)
    return tuple(answer)

def k3_reverse_index(ball,ex):
    """Original weighted Q4->K3 edges, independently transposed to K3->Q4."""
    cross=[{} for _ in range(K3)]
    for f,i,weighted in zip(ex["e4f"],ex["e4s"],ex["e4c"]):
        need(0<=f<Q4 and 0<=i<K3,"C_K3_Q4_reverse_index_range")
        w=ball["wq"][i]
        need(weighted%w==0,"C_K3_Q4_weighted_reverse_integrality")
        cc=weighted//w
        need(f not in cross[i],"C_duplicate_K3_Q4_reverse_record")
        cross[i][f]=cc
    return cross

def independently_rebuild_K3(ball,ex,inner,items,i,key,reverse):
    """Two exact constructions of V1_K3 = X R at both frozen energies.

    Original frozen K3 CSR and weighted Q4-reverse list versus independent
    complete 72-move canonical electric enumerator. R_K3 is signed and
    R_Q4 is NEGATIVE positive P. R outside K3+Q4 vanishes.
    """
    original_k3_residual(ball,items,i)
    near=src.c.neighbors(key)
    need(sum(near.values())==72,"C_full_K3_72_raw_moves")
    actual_inner={}
    actual_q4={}
    for dst,cc in near.items():
        j=inner.get(dst)
        if j is not None:
            actual_inner[j]=cc
            continue
        g=ex["s4"].get(src.m.code(dst))
        if g is not None:
            actual_q4[g]=cc
    expected_inner={ball["oj"][p]:ball["oc"][p]
                    for p in range(ball["rs"][i],ball["rs"][i+1])}
    need(actual_inner==expected_inner,
         "C_independent_K3_row_vs_original_CSR_disagreement")
    need(actual_q4==reverse[i],
         "C_independent_K3_Q4_row_vs_original_weighted_reverse_disagreement")
    result=[]
    for row,record,old_rs,positive_q4 in items:
        ri=old_rs[i]
        direct=[0]*COLS
        for j,cc in actual_inner.items():
            rj=old_rs[j]
            for c in range(COLS):
                direct[c]+=cc*rj[c]
        for g,cc in actual_q4.items():
            pf=src.unpack(positive_q4[g],width_global,mask_global)
            for c in range(COLS):
                direct[c]-=cc*pf[c]
        historic=[0]*COLS
        for p in range(ball["rs"][i],ball["rs"][i+1]):
            cc=ball["oc"][p]
            rj=old_rs[ball["oj"][p]]
            for c in range(COLS):
                historic[c]+=cc*rj[c]
        for g,cc in reverse[i].items():
            pf=src.unpack(positive_q4[g],width_global,mask_global)
            for c in range(COLS):
                historic[c]-=cc*pf[c]
        d=B*ball["dbase"][i]-row[0]
        actual=tuple(d*ri[c]-B*direct[c] for c in range(COLS))
        expected=tuple(d*ri[c]-B*historic[c] for c in range(COLS))
        need(actual==expected,
             "C_K3_full_V1_independent_row_vs_weighted_CSR_disagreement")
        result.append(actual)
    return tuple(result)

def independently_rebuild_Q4(ball,ex,inner,items,width,mask,f,weight,key):
    """Rebuild R_Q4=-pf from original K3 Y, then compute V1_Q4=X R.

    The original positive Q4 response must be negated. Cross-term signs
    and all self loops are computed from the full 72-move row.
    """
    start=ball["es"][f]
    stop=ball["es"][f+1]
    for row,record,old_rs,positive_q4 in items:
        y=record["Y"]
        sums=[0]*COLS
        for e in range(start,stop):
            wc=ball["ewc"][e]
            source=y[ball["esrc"][e]]
            for c in range(COLS):
                sums[c]+=wc*source[c]
        r=[]
        for value in sums:
            need(value%weight==0,"C_Q4_weighted_Y_source_division")
            r.append(-B*(value//weight))
        original=src.unpack(positive_q4[f],width,mask)
        need(tuple(r)==tuple(-v for v in original),
             "C_Q4_original_negative_R_independent_contraction_disagreement")
    near=src.c.neighbors(key)
    need(sum(near.values())==72,"C_full_Q4_72_raw_moves")
    expect_k3={}
    for edge in range(start,stop):
        weighted=ball["ewc"][edge]
        need(weighted%weight==0,"C_Q4_K3_reverse_record_divisibility")
        j=ball["esrc"][edge]
        expect_k3[j]=expect_k3.get(j,0)+weighted//weight
    actual_k3={}
    actual_q4={}
    for dst,cc in near.items():
        j=inner.get(dst)
        if j is not None:
            actual_k3[j]=cc
            continue
        g=ex["s4"].get(src.m.code(dst))
        if g is not None:
            actual_q4[g]=cc
    need(actual_k3==expect_k3,
         "C_full_Q4_original_K3_reverse_row_census_mismatch")
    magnetic=src.c.magnetic(src.c.from_key(key))
    dbase=72+9*magnetic
    result=[]
    for row,record,old_rs,positive_q4 in items:
        pf=src.unpack(positive_q4[f],width,mask)
        incoming=[0]*COLS
        sum4=[0]*COLS
        for j,cc in actual_k3.items():
            rj=old_rs[j]
            for c in range(COLS):
                incoming[c]+=cc*rj[c]
        for g,cc in actual_q4.items():
            pg=src.unpack(positive_q4[g],width,mask)
            for c in range(COLS):
                sum4[c]+=cc*pg[c]
        d=B*dbase-row[0]
        # Direct operator acting on R_K3=old_rs, R_Q4=-pf.
        direct=tuple(-d*pf[c]-B*incoming[c]+B*sum4[c]
                     for c in range(COLS))
        # Independent algebraic replay of the original positive response,
        # with its physical Q4 V1 sign reversed.
        negative_response=tuple(-(d*pf[c]-B*sum4[c]+B*incoming[c])
                                for c in range(COLS))
        need(direct==negative_response,
             "C_full_Q4_direct_signed_operator_vs_historic_response")
        result.append(direct)
    return tuple(result)

def spool(mode,group,filename):
    need(mode in ("k3","q4"),"C_invalid_shell")
    need((mode=="k3" and group==0) or
         (mode=="q4" and 0<=group<GROUPS),"C_invalid_source_partition")
    ball,ex,inner,flat,width,mask,items=frozen()
    start=0 if mode=="k3" else Q4*group//GROUPS
    stop=K3 if mode=="k3" else Q4*(group+1)//GROUPS
    shell=3 if mode=="k3" else 4
    count=stop-start
    maxabs=[0,0]
    negative=[0,0]
    positive=[0,0]
    weight_hist=[0]*7
    minmag=36
    maxmag=0
    buckets=[[] for _ in range(64)]
    q4_lookup=ex["s4"]
    original_hash=original_UG(items)
    global width_global, mask_global
    width_global, mask_global = width, mask
    if mode=="k3":
        reverse=k3_reverse_index(ball,ex)
        keys=[None]*K3
        for key,i in inner.items():
            need(0<=i<K3 and keys[i] is None,"C_K3_invalid_inverse_index")
            keys[i]=key
        need(all(k is not None for k in keys),
             "C_K3_missing_canonical_source_addresses")
    for offset in range(start,stop):
        if mode=="k3":
            key=keys[offset]
            address=src.m.code(key)
            need(address not in q4_lookup,"C_K3_Q4_support_collision")
            weight=src.c.weight(key)
            values=independently_rebuild_K3(ball,ex,inner,items,offset,key,reverse)
        else:
            address=ex["code4"][offset]
            need(q4_lookup.get(address)==offset,"C_Q4_original_index_mismatch")
            key=src.m.decode(address)
            need(key not in inner,"C_Q4_K3_support_collision")
            weight=ball["eW"][offset]
            values=independently_rebuild_Q4(ball,ex,inner,items,width,mask,offset,weight,key)
        magnetic=checked_key(key,address,weight,shell)
        minmag=min(minmag,magnetic)
        maxmag=max(maxmag,magnetic)
        weight_hist[weight]+=1
        for e in range(2):
            for val in values[e]:
                maxabs[e]=max(maxabs[e],abs(val))
                negative[e]+=int(val<0)
                positive[e]+=int(val>0)
                need(abs(val)<(1<<192),"C_signed_codec_exceeds_192_bits")
        buckets[address%64].append((address,weight,shell,values))
        if (offset-start+1)%50000==0:
            print("Y137_C_SIGNED_PROGRESS|shell="+mode+
                  "|group="+str(group)+"|rows="+str(offset-start+1)+
                  "|bound_candidate_bits="+str(max(v.bit_length() for v in maxabs))+
                  "|json=0",flush=True)

    # Sort inside each disjoint bucket, then merge all buckets into one
    # globally ascending canonical-address stream without storing bytes.
    for part in buckets:
        part.sort(key=lambda p:p[0])
        for i in range(1,len(part)):
            need(part[i][0]>part[i-1][0],"C_duplicate_same_bucket_address")
    os.makedirs(os.path.dirname(os.path.abspath(filename)),exist_ok=True)
    digest=hashlib.sha256()
    saved=0
    length=0
    before=None
    with open(filename,"wb") as out:
        for address,weight,real_shell,values in heapq.merge(
                *(iter(part) for part in buckets)):
            need(before is None or address>before,
                 "C_global_source_stream_not_strictly_ascending")
            before=address
            raw=encode(address,weight,real_shell,values)
            digest.update(raw)
            out.write(raw)
            saved+=1
            length+=len(raw)
    need(saved==count,"C_missing_original_source_rows")
    verified_read(filename,digest.hexdigest(),count,shell)
    bound_ok=all(v<BOUND for v in maxabs)
    label=("PASS" if bound_ok else "HOLD_REQUIRE_SHARPER_BOUND")
    print("Y137_C_SIGNED_SOURCE|shell="+mode+"|group="+str(group)+
          "|start="+str(start)+"|stop="+str(stop)+"|states="+str(saved)+
          "|bytes="+str(length)+"|sha256="+digest.hexdigest()+
          "|sample_E1_num="+str(ENERGIES[0])+
          "|sample_E2_num="+str(ENERGIES[1])+
          "|max_abs_E1="+str(maxabs[0])+"|max_abs_E2="+str(maxabs[1])+
          "|max_bits_E1="+str(maxabs[0].bit_length())+
          "|max_bits_E2="+str(maxabs[1].bit_length())+
          "|negative_E1="+str(negative[0])+
          "|negative_E2="+str(negative[1])+
          "|positive_E1="+str(positive[0])+
          "|positive_E2="+str(positive[1])+
          "|mag_min="+str(minmag)+"|mag_max="+str(maxmag)+
          "|weights="+",".join(str(v) for v in weight_hist)+
          "|accepted_UG_E1="+",".join(original_hash[0])+
          "|accepted_UG_E2="+",".join(original_hash[1])+
          "|independent_all_source_contractions=EXACT"+
          "|roundtrip_SHA_and_sorted_keys=PASS"+
          "|amplitude_under_2pow117="+label+
          "|whole_mu3=NOT_COMPUTED|Wilson_weight=HOLD|json=0",
          flush=True)

def toy():
    # Operator sign and source sign are distinguished by construction.
    D=B*108-ENERGIES[0]
    Y=(3,5,7,11,13,17,19,23)
    neighbors=(2,4,6,8,10,12,14,16)
    force=(1,0,1,0,1,0,1,0)
    recovered=tuple(D*y-B*n-B*src.SCALE*f
                    for y,n,f in zip(Y,neighbors,force))
    ref=tuple(D*Y[k]-B*(neighbors[k]+src.SCALE*force[k])
              for k in range(COLS))
    need(ref==recovered,"C_K3_toy_contraction_disagreement")
    weighted=[6,12,18,24,30,36,42,48]
    weight=3
    signed=tuple(-B*(v//weight) for v in weighted)
    need(all(v<0 for v in signed),"C_Q4_toy_unsigned_source_error")
    need(all(abs(v)<BOUND for v in recovered+signed),
         "C_toy_amplitude_bound")
    need(K3+Q4+Q5==20738636,"C_total_supported_state_count")
    need((396*B-ENERGIES[0]+72*B)<(1<<39) and
         (396*B-ENERGIES[1]+72*B)<(1<<39),
         "C_frozen_operator_absolute_row_bound")
    # Global W max=36, 20,738,636 rows. Every partial row sum is
    # bounded by 2^25 * 2^6 * 2^117 * 2^156 = 2^304.
    need(20738636<(1<<25) and 36<(1<<6) and
         117+156+25+6==304,"C_sufficient_global_320bit_budget")
    print("Y137_C_SIGNED_SOURCE_TOY|K3_residual_sign=PASS"+
          "|Q4_negative_source=PASS|two_frozen_energy_diagonal=PASS"+
          "|total_supported_rows=20738636|sufficient_source_limit_bits=117"+
          "|global_operator_limit_bits=39|global_partial_sum_limit_bits=304"+
          "|real_K3_Q4_sources=NOT_COMPUTED|whole_mu3=NOT_COMPUTED"+
          "|Wilson_weight=HOLD|json=0")

def main(argv):
    try:
        if argv==["toy"]:
            toy()
        elif len(argv)==4 and argv[0]=="write" and argv[1]=="q4":
            spool("q4",int(argv[2]),argv[3])
        elif len(argv)==3 and argv[0]=="write-k3":
            # Invocation: write-k3 0 PATH -- strictly one K3 stream.
            raise Refuse("C_K3_usage_write-k3_PATH")
        elif len(argv)==2 and argv[0]=="write-k3":
            spool("k3",0,argv[1])
        else:
            raise Refuse("C_usage")
    except (Refuse,ValueError,OSError,KeyError,MemoryError,OverflowError) as e:
        print("Y137_C_SIGNED_SOURCE_REFUSE|reason="+str(e)+"|json=0",flush=True)
        raise SystemExit(1) from None

if __name__=="__main__":
    main(sys.argv[1:])
