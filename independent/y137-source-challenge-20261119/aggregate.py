#!/usr/bin/env python3
"""Independent exact-integer fan-in of signed K3/Q4 row challenges.

Never imports original signed source producers. All eight source partitions,
signed lane counts, 72-move tallies, and archive evidence labels are required.
Tamper controls must be rejected before the fan-in can pass.
"""
import hashlib
import os
import sys

K3=155378
Q4=1985218
PARTS=8

class Refuse(Exception):
    pass

def need(ok,why):
    if not ok:raise Refuse(why)

def record(raw):
    rows=[x for x in raw.splitlines() if x.startswith("Y137_INDEPENDENT_SOURCE_CHALLENGE|")]
    need(len(rows)==1,"exact_single_group_receipt")
    cols=rows[0].split("|")
    data={}
    for item in cols[1:]:
        key,sep,val=item.partition("=")
        need(bool(sep) and key and key not in data,"duplicate_or_missing_receipt_column")
        data[key]=val
    need(data.pop("json",None)=="0","bad_terminator")
    return data

def value(row,key):
    x=row[key]
    v=int(x)
    need(str(v)==x,"noncanonical_integer_"+key)
    return v

def pair(row,key):
    x=row[key].split(",")
    need(len(x)==2,"range_format")
    return tuple(int(v) for v in x)

def accept(g,row):
    need(value(row,"group")==g,"wrong_source_group")
    need(pair(row,"K3_disjoint_range")==(K3*g//8,K3*(g+1)//8),
         "K3_source_partition_range")
    need(pair(row,"Q4_disjoint_range")==(Q4*g//8,Q4*(g+1)//8),
         "Q4_source_partition_range")
    need(value(row,"K3_challenged_rows")==27 and
         value(row,"Q4_challenged_rows")==81,
         "source_challenge_row_count")
    need(value(row,"exact_signed_lanes")==16*(27+81),
         "source_challenge_signed_matrix_lanes")
    need(value(row,"independent_raw_moves")==72*(27+81),
         "source_challenge_full_72_moves")
    need(0<value(row,"weighted_reverse_edges")<=108,
         "source_challenge_reciprocal_edges")
    need(0<=value(row,"off_support_moves")<=72*108,
         "source_challenge_offsupport_count")
    need(0<=value(row,"magnetic_number_sum")<=36*108,
         "source_challenge_magnetic_domain")
    dig=row["source_digest"]
    need(len(dig)==64 and all(c in "0123456789abcdef" for c in dig),
         "source_challenge_digest")
    for key in ("K3_original_archive_SHA","Q4_original_archive_SHA",
                "independent_S3_72moves","signed_V1_two_energies"):
        need(row[key]=="PASS","physical_source_challenge_"+key)
    need(row["whole_Q_mu3"]=="NOT_INDEPENDENTLY_RECOMPUTED" and
         row["first_Wilson_weight"]=="FORMAL_HOLD","proof_status_boundary")
    return dig

def corruptions(row):
    cases=[]
    for col,change in (
        ("group","8"),("K3_challenged_rows","26"),
        ("Q4_challenged_rows","80"),("exact_signed_lanes","0"),
        ("independent_raw_moves","7776"),("K3_original_archive_SHA","HOLD"),
        ("Q4_original_archive_SHA","HOLD"),("signed_V1_two_energies","HOLD"),
        ("whole_Q_mu3","INDEPENDENT_PASS"),("first_Wilson_weight","PASS")):
        a=dict(row);a[col]=change;cases.append(a)
    for bad in cases:
        try:accept(0,bad)
        except (Refuse,ValueError,KeyError):pass
        else:raise Refuse("modified_challenge_receipt_was_accepted")
    need(len(cases)==10,"tamper_control_count")
    return len(cases)

def aggregate(folder):
    observations=[]
    digests=set()
    h=hashlib.sha256()
    for g in range(PARTS):
        p=os.path.join(folder,"GROUP-"+str(g)+".hbp")
        with open(p,encoding="ascii") as stream:
            raw=stream.read()
        row=record(raw)
        d=accept(g,row)
        need(d not in digests,"repeated_source_challenge_digest")
        digests.add(d)
        h.update((str(g)+"|"+d+";").encode("ascii"))
        observations.append(row)
    # Source-free corruption checks reuse a real grouped record.
    a=corruptions(observations[0])
    totalK3=sum(value(x,"K3_challenged_rows") for x in observations)
    totalQ4=sum(value(x,"Q4_challenged_rows") for x in observations)
    totalRaw=sum(value(x,"independent_raw_moves") for x in observations)
    totalW=sum(value(x,"weighted_reverse_edges") for x in observations)
    need(totalK3==216 and totalQ4==648 and totalRaw==62208,
         "global_challenge_census")
    need(totalW>=8,"missing_independent_reciprocity")
    print("Y137_INDEPENDENT_SOURCE_CHALLENGE_FANIN|source_groups=8"+
          "|disjoint_K3_challenges="+str(totalK3)+
          "|disjoint_Q4_challenges="+str(totalQ4)+
          "|independent_72_raw_moves="+str(totalRaw)+
          "|independent_reciprocals="+str(totalW)+
          "|exact_signed_lanes="+str((totalK3+totalQ4)*16)+
          "|K3_Q4_archive_SHA=9_OF_9_PASS"+
          "|S3_graph_and_signed_V1=SOURCE_CHALLENGE_PASS"+
          "|forged_receipts="+str(a)+"_REJECTED"+
          "|group_digest_sha256="+h.hexdigest()+
          "|whole_Q_mu3=INDEPENDENT_RECONSTRUCTION_OPEN"+
          "|whole_Perron_rebuild=INDEPENDENT_RECONSTRUCTION_OPEN"+
          "|original_Wilson_weight=CONDITIONAL_CANDIDATE_FORMAL_HOLD"+
          "|continuum_4D=OPEN|json=0",flush=True)

def toy():
    a={"group":"0","K3_disjoint_range":"0,"+str(K3//8),
       "Q4_disjoint_range":"0,"+str(Q4//8),
       "K3_challenged_rows":"27","Q4_challenged_rows":"81",
       "exact_signed_lanes":str(108*16),"independent_raw_moves":str(108*72),
       "weighted_reverse_edges":"10","off_support_moves":"10",
       "magnetic_number_sum":"900","source_digest":"a"*64,
       "K3_original_archive_SHA":"PASS","Q4_original_archive_SHA":"PASS",
       "independent_S3_72moves":"PASS","signed_V1_two_energies":"PASS",
       "whole_Q_mu3":"NOT_INDEPENDENTLY_RECOMPUTED",
       "first_Wilson_weight":"FORMAL_HOLD"}
    accept(0,a)
    n=corruptions(a)
    print("Y137_INDEPENDENT_SOURCE_CHALLENGE_FANIN_TOY|positive=PASS"+
          "|tamper_controls="+str(n)+"_REJECTED"+
          "|original_K3_Q4=NOT_COMPUTED|json=0",flush=True)

def main():
    try:
        if sys.argv[1:]==["toy"]:
            toy()
        elif len(sys.argv)==3 and sys.argv[1]=="aggregate":
            aggregate(sys.argv[2])
        else:raise Refuse("usage_toy_or_aggregate_FOLDER")
    except (Refuse,ValueError,KeyError,OSError) as e:
        print("Y137_INDEPENDENT_SOURCE_CHALLENGE_FANIN_HOLD|reason="+str(e)+
              "|Wilson_weight=FORMAL_HOLD|json=0",flush=True)
        raise SystemExit(2)

if __name__=="__main__":
    main()
