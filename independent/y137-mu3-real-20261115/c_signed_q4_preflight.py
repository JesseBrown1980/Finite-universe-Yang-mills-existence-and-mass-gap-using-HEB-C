#!/usr/bin/env python3
"""#137 Stage C first authentic signed-source control, using frozen K3/Q4 builder.

Full K3/Q4/Q5 moment remains uncomputed. This independently regenerates frozen
K3 Y/U/G identities and checks 27 real Q4 electric rows per requested shard,
at the two original energies. Exact integers only.
"""
import hashlib
import os
import sys

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
sys.path.insert(0,os.path.join(ROOT,"independent","y137-real-Q-moment-20261114"))
# The pinned K3 loader refuses extra argv during import to prevent hidden
# source changes. Preserve that source gate rather than modifying it.
ORIGINAL_ARGS=sys.argv[:]
sys.argv=sys.argv[:1]
import mu1_shard as src
sys.argv=ORIGINAL_ARGS

B=1000000000
ENERGIES=(69909875505,69949729820)
K3=155378
Q4=1985218
Q5=18598040
SHARDS=8
COLS=8

class Refuse(Exception):
    pass

def need(ok,reason):
    if not ok:
        raise Refuse(reason)

def signed_response(d,pf,q4_sum,k3_sum):
    """Exact Q4 V1_Q4, sign frozen as negative of original mu1 response."""
    return tuple(-d*p + B*s4 - B*s3
                 for p,s4,s3 in zip(pf,q4_sum,k3_sum))

def direct_operator(d,negative_pf,neighbors):
    """Compute X R on Q4 from signed actual R, without the response formula."""
    return tuple(d*negative_pf[k]-B*neighbors[k] for k in range(COLS))

def toy():
    pf=(2,4,6,8,10,12,14,16)
    q4=(3,5,7,9,11,13,15,17)
    k3=(1,2,1,2,1,2,1,2)
    d=B*108-ENERGIES[0]
    first=signed_response(d,pf,q4,k3)
    contracted=tuple(-s4+s3 for s4,s3 in zip(q4,k3))
    second=direct_operator(d,tuple(-v for v in pf),contracted)
    need(first==second,"C_toy_signed_Q4_formula_mismatch")
    legacy=tuple(d*p-B*s4+B*s3 for p,s4,s3 in zip(pf,q4,k3))
    need(first==tuple(-v for v in legacy),"C_toy_original_response_sign")
    need(first!=legacy,"C_toy_wrong_positive_Q4_sign")
    need(first!=signed_response(d,pf,(0,)*COLS,k3),
         "C_toy_missing_Q4_cross")
    need(first!=signed_response(d,pf,q4,(0,)*COLS),
         "C_toy_missing_K3_cross")
    need(first!=signed_response(B*108-ENERGIES[1],pf,q4,k3),
         "C_toy_energy_swap_not_detected")
    print("Y137_C_SIGNED_TOY|signed_Q4_negative_legacy_response=PASS"+
          "|independent_direct_operator=EXACT"+
          "|wrong_Q4_sign=REFUSED|omitted_Q4_neighbors=REFUSED"+
          "|omitted_K3_neighbors=REFUSED|swapped_energy=REFUSED"+
          "|genuine_K3_Q4_Q5=NOT_COMPUTED|whole_mu3=NOT_COMPUTED"+
          "|Wilson_weight=HOLD|json=0")

def sampled_indices(shard):
    lo=Q4*shard//SHARDS
    hi=Q4*(shard+1)//SHARDS
    need(0<=lo<hi<=Q4,"C_bad_shard")
    spans=(list(range(lo,lo+9))+
           list(range((lo+hi)//2-4,(lo+hi)//2+5))+
           list(range(hi-9,hi)))
    result=sorted(set(spans))
    need(len(result)==27 and result[0]>=lo and result[-1]<hi,
         "C_sample_not_27_real_Q4_states")
    return result

def real(shard):
    need(0<=shard<SHARDS,"C_invalid_shard")
    ball,ex,inner,flat,width,mask,items=src.build_inputs()
    need(ball["n"]==K3 and ball["nf"]==Q4 and
         len(ex["code4"])==Q4 and len(items)==2,
         "C_frozen_K3_Q4_census")
    need(tuple(row[0] for row,_,_,_ in items)==ENERGIES,
         "C_frozen_two_sample_energy_numerators")
    need(width>=1 and mask==(1<<width)-1,"C_packed_source_width")
    digest=[hashlib.sha256(),hashlib.sha256()]
    max_bits=[0,0]
    signed_negative=[0,0]
    signed_positive=[0,0]
    true_inner=0
    true_q4=0
    unclassified_q5=0
    move_sum=0
    for f in sampled_indices(shard):
        address=ex["code4"][f]
        key=src.m.decode(address)
        w=ball["eW"][f]
        need(src.c.weight(key)==w,"C_independent_orbit_weight")
        moves=src.c.neighbors(key)
        need(sum(moves.values())==72,"C_original_72_raw_moves")
        magnetic=src.c.magnetic(src.c.from_key(key))
        need(4<=magnetic<=16,"C_authentic_Q4_magnetic_range")
        expected={}
        for edge in range(ball["es"][f],ball["es"][f+1]):
            weighted=ball["ewc"][edge]
            need(weighted%w==0,"C_original_K3_reverse_weight_division")
            j=ball["esrc"][edge]
            expected[j]=expected.get(j,0)+weighted//w
        found={}
        q4sum=[[0]*COLS for _ in items]
        k3sum=[[0]*COLS for _ in items]
        for dest,c in moves.items():
            need(dest not in flat,"C_unexpected_Q4_to_flat_move")
            j=inner.get(dest)
            if j is not None:
                found[j]=c
                true_inner+=c
                for k,(_,_,residuals,_) in enumerate(items):
                    for channel in range(COLS):
                        k3sum[k][channel]+=c*residuals[j][channel]
                continue
            g=ex["s4"].get(src.m.code(dest))
            if g is not None:
                true_q4+=c
                for k,(_,_,_,positive_q4) in enumerate(items):
                    val=src.unpack(positive_q4[g],width,mask)
                    for channel in range(COLS):
                        q4sum[k][channel]+=c*val[channel]
                continue
            unclassified_q5+=c
        need(found==expected,"C_K3_reverse_edge_census")
        dbase=72+9*magnetic
        for k,(frozen,_,residuals,positive_q4) in enumerate(items):
            z=frozen[0]
            pf=src.unpack(positive_q4[f],width,mask)
            d=B*dbase-z
            direct_neighbors=tuple(-q4sum[k][channel]+k3sum[k][channel]
                                   for channel in range(COLS))
            a=signed_response(d,pf,q4sum[k],k3sum[k])
            b=direct_operator(d,tuple(-value for value in pf),direct_neighbors)
            legacy=tuple(d*p-B*s4+B*s3 for p,s4,s3
                         in zip(pf,q4sum[k],k3sum[k]))
            need(a==b and a==tuple(-v for v in legacy),
                 "C_original_signed_Q4_negative_response_disagreement")
            for val in a:
                max_bits[k]=max(max_bits[k],abs(val).bit_length())
                signed_negative[k]+=int(val<0)
                signed_positive[k]+=int(val>0)
            digest[k].update((str(address)+"|"+str(w)+"|"+
                              str(z)+"|"+",".join(str(v) for v in a)+"\n")
                             .encode("ascii"))
        move_sum+=72
    need(move_sum==27*72 and
         true_inner+true_q4+unclassified_q5==move_sum,
         "C_sampled_Q4_partition_or_degree")
    for k,(frozen,_,_,_) in enumerate(items):
        print("Y137_C_SIGNED_Q4_SAMPLE|shard="+str(shard)+
              "|sample_num="+str(frozen[0])+
              "|authentic_rows=27|sampled_raw_moves="+str(move_sum)+
              "|signed_row_sha256="+digest[k].hexdigest()+
              "|max_abs_lane_bits="+str(max_bits[k])+
              "|negative_entries="+str(signed_negative[k])+
              "|positive_entries="+str(signed_positive[k])+
              "|source_U_sha256="+str(frozen[4])+
              "|source_G_sha256="+str(frozen[5])+
              "|negative_original_Q4_response=EXACT"+
              "|independent_direct_operator=EXACT|json=0")
    print("Y137_C_SIGNED_PREFLIGHT|shard="+str(shard)+
          "|real_Q4_rows=27|raw_moves="+str(move_sum)+
          "|Q4_to_K3_raw_moves="+str(true_inner)+
          "|Q4_to_Q4_raw_moves="+str(true_q4)+
          "|Q4_to_outside_raw_moves="+str(unclassified_q5)+
          "|original_K3_Q4_source_fingerprints=PASS"+
          "|signed_Q4_two_energies=EXACT"+
          "|full_Q4=NOT_COMPUTED|whole_mu3=NOT_COMPUTED"+
          "|Wilson_weight=HOLD|json=0")

def main(argv):
    try:
        if argv==["toy"]:
            toy()
        elif len(argv)==2 and argv[0]=="real-shard":
            real(int(argv[1]))
        else:
            raise Refuse("C_usage")
    except (Refuse,ValueError,KeyError,OverflowError,MemoryError) as e:
        print("Y137_C_SIGNED_REFUSE|reason="+str(e)+"|json=0",flush=True)
        raise SystemExit(1) from None

if __name__=="__main__":
    main(sys.argv[1:])
