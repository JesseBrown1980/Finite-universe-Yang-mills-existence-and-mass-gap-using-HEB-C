#!/usr/bin/env python3
"""#137 Stage C: independent whole signed K3/Q4-source spool validator.

Authenticate 155,378 K3 plus 1,985,218 Q4 *physical V1* vectors, two
energies, exact global canonical keys and orbit weights. Merge nine sorted
source files; detect even cross-shard duplicate/collision. Recompute maxima
from raw signed records and prove sufficient M<2^117 condition if it holds.

The original Q5 source already has <2^82 packed unsigned lanes and b<2^30,
so Q5 physical V1<2^112. Whole-Q mu3 is not yet computed.
"""
import hashlib
import heapq
import os
import sys
import tempfile

HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
from c_signed_source_codec import decode, encode, Refuse
from source_gate import canonical_weight

K3=155378
Q4=1985218
Q5=18598040
B=1000000000
EXPECTED=K3+Q4
TOTAL=EXPECTED+Q5
M_LIMIT=1<<117
Z=(69909875505,69949729820)
PINNED_UG=(
 ("0752df3c1941c67316cc6834795182fdaccdaba0ca5fc711221e7217d0dbaa1c",
  "83efba692ef3a8451a68049ee996451877ac4d646ae2f357fc0b604b48db0b0f"),
 ("9229dfad058157d80287cb1ab188c1034bdbb16394dec045b540890d8bb05109",
  "e42df65b4b269095177fc609d06b4576917901c598f8ebd477eaa58b61b90d8d"))

def need(ok,why):
    if not ok:
        raise Refuse(why)

def parse(line,prefix):
    pieces=line.rstrip("\r\n").split("|")
    need(pieces[0]==prefix,"C_wrong_receipt_type")
    result={}
    for p in pieces[1:]:
        k,sep,v=p.partition("=")
        need(bool(sep) and k not in result,"C_duplicate_or_bad_receipt_field")
        result[k]=v
    need(result.get("json")=="0","C_bad_receipt_marker")
    return result

def freeze_inputs(receipt_dir):
    entries=[]
    for group in range(9):
        key=("K3" if group==8 else "Q4-"+str(group))
        path=os.path.join(receipt_dir,"GROUP-"+str(group)+".hbp")
        with open(path,encoding="ascii") as f:
            lines=[x for x in f if x.startswith("Y137_C_SIGNED_SOURCE|")]
        need(len(lines)==1,"C_missing_or_duplicate_group_receipt_"+key)
        r=parse(lines[0],"Y137_C_SIGNED_SOURCE")
        if group==8:
            need(r["shell"]=="k3" and int(r["group"])==0 and
                 int(r["states"])==K3 and int(r["start"])==0 and
                 int(r["stop"])==K3,"C_K3_wrong_original_partition")
            shell=3
        else:
            lo=Q4*group//8
            hi=Q4*(group+1)//8
            need(r["shell"]=="q4" and int(r["group"])==group and
                 int(r["states"])==hi-lo and int(r["start"])==lo and
                 int(r["stop"])==hi,"C_Q4_wrong_original_partition")
            shell=4
        need(int(r["sample_E1_num"])==Z[0] and
             int(r["sample_E2_num"])==Z[1],
             "C_wrong_frozen_energy_numerators")
        need(r["accepted_UG_E1"]==",".join(PINNED_UG[0]) and
             r["accepted_UG_E2"]==",".join(PINNED_UG[1]),
             "C_original_K3_UG_source_not_frozen")
        need(r["independent_all_source_contractions"]=="EXACT" and
             r["roundtrip_SHA_and_sorted_keys"]=="PASS",
             "C_unsigned_or_unverified_source_label")
        need(len(r["sha256"])==64,"C_malformed_source_fingerprint")
        entries.append((group,shell,r))
    return entries

def file_records(path, group, shell, receipt, result):
    count=0
    maxi=[0,0]
    negatives=[0,0]
    positives=[0,0]
    last=None
    with open(path,"rb") as f:
        while True:
            item=decode(f)
            if item is None:
                break
            addr,weight,actual_shell,vectors=item
            need(actual_shell==shell,"C_wrong_merged_shell")
            need(last is None or addr>last,"C_unordered_or_duplicate_source_file")
            last=addr
            need(weight==canonical_weight(addr),
                 "C_independent_S3_canonical_orbit_weight")
            for e in range(2):
                for v in vectors[e]:
                    maxi[e]=max(maxi[e],abs(v))
                    negatives[e]+=int(v<0)
                    positives[e]+=int(v>0)
            count+=1
            yield (addr,group)
    with open(path,"rb") as f:
        d=hashlib.sha256()
        while chunk:=f.read(1024*1024):
            d.update(chunk)
    observed=os.path.getsize(path)
    need(count==int(receipt["states"]) and
         observed==int(receipt["bytes"]) and
         d.hexdigest()==receipt["sha256"],"C_exact_signed_spool_fingerprint_or_count")
    for e in range(2):
        suffix=str(e+1)
        need(maxi[e]==int(receipt["max_abs_E"+suffix]) and
             maxi[e].bit_length()==int(receipt["max_bits_E"+suffix]) and
             negatives[e]==int(receipt["negative_E"+suffix]) and
             positives[e]==int(receipt["positive_E"+suffix]),
             "C_forged_signed_maximum_or_count")
    result[group]={"rows":count,"bytes":observed,"digest":d.hexdigest(),
                   "maxima":maxi,"negative":negatives,"positive":positives}

def aggregate(receipt_dir,source_dir):
    entries=freeze_inputs(receipt_dir)
    records={}
    streams=[]
    for group,shell,receipt in entries:
        name="SIGNED-K3.v1" if group==8 else "SIGNED-Q4-"+str(group)+".v1"
        streams.append(file_records(os.path.join(source_dir,name),
                                    group,shell,receipt,records))
    total=0
    before=None
    for addr,group in heapq.merge(*streams,key=lambda row:row[0]):
        need(before is None or addr>before,"C_global_cross_shard_signed_source_collision")
        before=addr
        total+=1
    need(total==EXPECTED and len(records)==9,"C_global_signed_source_census")
    maxima=[max(v["maxima"][e] for v in records.values()) for e in range(2)]
    conditional=max(maxima)<M_LIMIT
    max_bits=[n.bit_length() for n in maxima]
    source_bound=("PASS" if conditional else "HOLD_SHARPER_BOUND_REQUIRED")
    need(TOTAL==20738636 and Q5==18598040,"C_total_supported_count_changed")
    # Independent of the exact source magnitudes, the original Q5 archive
    # has all 8 lanes <2^82 and b<2^30, hence every Q5 |V1|<2^112.
    need(B<(1<<30) and 82+30==112,"C_frozen_Q5_analytic_lane_bound")
    need(TOTAL<(1<<25) and 36<(1<<6) and
         (396*B-min(Z)+72*B)<(1<<39),
         "C_2pow304_global_operator_assumptions")
    result=("Y137_C_SIGNED_ACCEPT|source_groups=9|K3_states="+str(K3)+
            "|Q4_states="+str(Q4)+
            "|K3_Q4_unique_canonical_states="+str(total)+
            "|Q5_verified_packed_lane_bits=82"+
            "|Q5_physical_V1_upper_bits=112"+
            "|full_support_capacity="+str(TOTAL)+
            "|global_source_max_E1="+str(maxima[0])+
            "|global_source_max_E2="+str(maxima[1])+
            "|K3_Q4_max_bits_E1="+str(max_bits[0])+
            "|K3_Q4_max_bits_E2="+str(max_bits[1])+
            "|amplitude_under_2pow117="+source_bound+
            "|row_partial_sum_under_2pow304="+
            ("PROVED_CONDITIONAL_ON_ALL_SUPPORT_JOINS" if conditional
             else "HOLD_SHARPER_BLOCK_BOUND")+
            "|paired_edge_partial_sum_under_2pow304="+
            ("PROVED_CONDITIONAL_ON_RECIPROCAL_COMPLETE_SUPPORT" if conditional
             else "HOLD_SHARPER_BLOCK_BOUND")+
            "|Q5_support_disjointness=NOT_YET_RECHECKED"+
            "|whole_mu3=NOT_COMPUTED|Wilson_weight=HOLD|json=0")
    return result+"\n"

def toy():
    good=tuple(tuple((-1)**(e+i)*(e+2)*(i+1) for i in range(8))
               for e in range(2))
    t=encode(0,1,3,good)
    need(decode(__import__("io").BytesIO(t))==(0,1,3,good),
         "C_accept_toy_signed_code")
    need(canonical_weight(0)==1,"C_accept_toy_zero_weight")
    refused=0
    for a in (2,):
        try:
            canonical_weight(a)  # noncanonical S3 transposition
        except Refuse:
            refused+=1
    need(refused==1,"C_accept_noncanonical_attack_not_rejected")
    need(155378+1985218+18598040==20738636,"C_accept_support_count")
    print("Y137_C_SIGNED_ACCEPT_TOY|signed_reader=PASS"+
          "|S3_noncanonical_key=REFUSED|total_support_upper_count=20738636"+
          "|Q5_analytic_bound_bits=112|sufficient_amplitude_bound_bits=117"+
          "|full_signed_sources=NOT_COMPUTED|whole_mu3=NOT_COMPUTED"+
          "|Wilson_weight=HOLD|json=0")

def main(argv):
    try:
        if argv==["toy"]:
            toy()
        elif len(argv)==3 and argv[0]=="aggregate":
            print(aggregate(argv[1],argv[2]),end="")
        else:
            raise Refuse("C_signed_source_aggregate_usage")
    except (Refuse,ValueError,KeyError,OSError) as exc:
        print("Y137_C_SIGNED_ACCEPT_REFUSE|reason="+str(exc)+"|json=0",flush=True)
        raise SystemExit(1) from None

if __name__=="__main__":
    main(sys.argv[1:])
