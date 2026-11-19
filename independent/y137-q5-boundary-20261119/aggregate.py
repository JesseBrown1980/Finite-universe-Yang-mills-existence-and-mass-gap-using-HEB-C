#!/usr/bin/env python3
"""Independent integer fan-in for eight immutable original Q5 boundary audits."""
import hashlib
import os
import sys

GROUPS=8
ROWS=(435324,4439918,988399,2812763,822474,3973928,1612450,3512784)
BYTES=(72717336,750840749,166069410,476041564,137545818,672121828,270439868,595123535)
SHA=(
"3f561c26f3cf5b355ab769ae96e9da8ceaa141186fb5ecb80cc1ec4227e4c589",
"aaf435dcac9fad331ee0a0391dde0e66852426372aa7c34fac2416492485f5fc",
"f09edac5b00ab67f1c3189a4d98e6300529787bba81caf0c345cd05613985856",
"5c4017c73f869ec9187e1a1e80f6cfb1ac318521bd2c728cafb4ccbda9dba477",
"68eba145b904f6d9b792f8530420d5854ff8775239e2091aba12cc2952f15164",
"c3db5e2e6c70c4852df5bdeff5b1bcf9ec4983fd5f6288e0dc2a774652ceb59b",
"8ec64a5ba49040ba0dd835e95357ccc220785a1012850c200f81604ac7ee079a",
"98eec0d6972078dcf07c9ca36ee932f62b2dd2022725f7f91d88894e592b0ef0",
)

class Refuse(Exception):pass
def need(ok,msg):
    if not ok:raise Refuse(msg)
def parse(s):
    lines=[x for x in s.splitlines() if x.startswith("Y137_INDEPENDENT_Q5_BOUNDARY|")]
    need(len(lines)==1,"unique_original_Q5_record")
    rec={}
    for part in lines[0].split("|")[1:]:
        k,sep,v=part.partition("=")
        need(sep and k and k not in rec,"canonical_record_column")
        rec[k]=v
    need(rec.pop("json",None)=="0","receipt_tail")
    return rec
def number(a,key):
    s=a[key];n=int(s)
    need(str(n)==s,"noncanonical_"+key)
    return n
def check(g,a):
    need(number(a,"group")==g,"group")
    need(number(a,"actual_Q5_states")==27 and
         number(a,"independent_raw_moves")==1944 and
         number(a,"exact_original_two_energy_lanes")==432,
         "Q5_three_way_source_counts")
    need(27<=number(a,"Q5_Q4_reverse_edge_types")<=1944,
         "Q5_Q4_reciprocal_count")
    need(number(a,"magnetic_sum")>=0,"magnetic")
    need(number(a,"original_all_group_rows")==ROWS[g] and
         number(a,"original_all_group_bytes")==BYTES[g] and
         a["original_Q5_full_sha256"]==SHA[g],"original_Q5_archive_identity")
    need(a["original_Q5_archive_identity"]=="PASS" and
         a["independent_S3_and_Q4_boundary"]=="PASS" and
         a["two_original_Q5_packed_amplitudes"]=="EXACT",
         "source_boundary_original_acceptance")
    need(a["whole_Q_mu3"]=="RECONSTRUCTION_OPEN" and
         a["Wilson_weight"]=="CONDITIONAL_FORMAL_HOLD","status_boundary")
    token=a["challenged_source_sha256"]
    need(len(token)==64 and all(c in "0123456789abcdef" for c in token),
         "sample_challenge_digest")
    return token
def negatives(a):
    cases=(
        ("group","1"),("actual_Q5_states","26"),
        ("independent_raw_moves","1943"),
        ("exact_original_two_energy_lanes","431"),
        ("Q5_Q4_reverse_edge_types","0"),
        ("original_all_group_rows","1"),
        ("original_all_group_bytes","1"),
        ("original_Q5_full_sha256","0"*64),
        ("independent_S3_and_Q4_boundary","HOLD"),
        ("two_original_Q5_packed_amplitudes","HOLD"),
        ("Wilson_weight","PASS"))
    count=0
    for key,v in cases:
        clone=dict(a);clone[key]=v
        try:check(0,clone)
        except (Refuse,KeyError,ValueError):count+=1
        else:raise Refuse("forged_Q5_boundary_accepted_"+key)
    need(count==11,"Q5_negative_control_count")
    return count
def aggregate(path):
    digest=hashlib.sha256()
    rows=lanes=moves=edges=0
    receipts=[]
    for g in range(GROUPS):
        with open(os.path.join(path,"GROUP-"+str(g)+".hbp"),
                  encoding="ascii") as f:
            x=parse(f.read())
        token=check(g,x)
        digest.update((str(g)+"|"+token+";").encode("ascii"))
        rows+=number(x,"actual_Q5_states")
        lanes+=number(x,"exact_original_two_energy_lanes")
        moves+=number(x,"independent_raw_moves")
        edges+=number(x,"Q5_Q4_reverse_edge_types")
        receipts.append(x)
    n=negatives(receipts[0])
    need(rows==216 and lanes==3456 and moves==15552 and edges>=216,
         "all_Q5_fanin_counts")
    print("Y137_INDEPENDENT_Q5_FANIN|complete_source_groups=8"+
          "|original_Q5_archives_SHA=8_OF_8_PASS"+
          "|archived_original_Q5_rows=18598040"+
          "|archived_original_Q5_bytes=3140900108"+
          "|independent_physical_Q5_rows="+str(rows)+
          "|independent_raw_moves="+str(moves)+
          "|exact_two_energy_signed_components="+str(lanes)+
          "|Q5_Q4_weighted_reverse_edge_types="+str(edges)+
          "|independent_Q5_from_Q4_source=PASS"+
          "|corrupt_receipts="+str(n)+"_REJECTED"+
          "|group_receipt_sha256="+digest.hexdigest()+
          "|original_Wilson=SOURCE_CONDITIONAL_FORMAL_HOLD"+
          "|whole_Q_mu3=INDEPENDENT_RECONSTRUCTION_OPEN"+
          "|continuum_4D=OPEN|json=0",flush=True)
def toy():
    a={"group":"0","actual_Q5_states":"27","independent_raw_moves":"1944",
       "exact_original_two_energy_lanes":"432",
       "Q5_Q4_reverse_edge_types":"27","magnetic_sum":"500",
       "original_all_group_rows":str(ROWS[0]),
       "original_all_group_bytes":str(BYTES[0]),
       "original_Q5_full_sha256":SHA[0],
       "challenged_source_sha256":"a"*64,
       "original_Q5_archive_identity":"PASS",
       "independent_S3_and_Q4_boundary":"PASS",
       "two_original_Q5_packed_amplitudes":"EXACT",
       "whole_Q_mu3":"RECONSTRUCTION_OPEN",
       "Wilson_weight":"CONDITIONAL_FORMAL_HOLD"}
    check(0,a)
    n=negatives(a)
    print("Y137_INDEPENDENT_Q5_FANIN_TOY|positive=PASS"+
          "|bad_receipts="+str(n)+"_REJECTED"+
          "|real_Q5=NOT_RUN|json=0",flush=True)
def main():
    try:
        if sys.argv[1:]==["toy"]:toy()
        elif len(sys.argv)==3 and sys.argv[1]=="aggregate":
            aggregate(sys.argv[2])
        else:raise Refuse("usage: toy|aggregate PATH")
    except (Refuse,KeyError,ValueError,OSError) as exc:
        print("Y137_INDEPENDENT_Q5_FANIN_HOLD|reason="+str(exc)+
              "|original_Wilson=FORMAL_HOLD|json=0",flush=True)
        raise SystemExit(2) from None
if __name__=="__main__":main()
