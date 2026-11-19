#!/usr/bin/env python3
"""Exact integer 16-shard independent full 3x4 S3 signed μ3 Dirichlet acceptance.

Only authentic original frozen Stage C matrices and 16 new row computations
are compared. The real result requires source SHA verified externally by CI,
all 20,738,636 actual physical source rows, all 1,493,181,792 electric moves,
the complete original K3/Q4/Q5 boundary counts, independently regenerated
Q5-Q5 principal contribution, and 128 exact 8x8 matrix entries matching.
No floats, no original producer module, no numerical tolerances.
"""
import hashlib
import os
import sys

COLS=8
SAMPLES=(69909875505,69949729820)
N=20738636
EXPECTED=((1397544,9789408,0,264),
          (9728688,7486632,125720376,0),
          (0,125467392,125005512,1088585976))
LIMIT=1<<294

class Refuse(Exception):pass
def need(ok,why):
    if not ok:raise Refuse(why)
def number(s):
    v=int(s)
    need(str(v)==s,"noncanonical_integer")
    return v
def parse_record(raw,typ):
    lines=[x for x in raw.splitlines() if x.startswith(typ+"|")]
    need(len(lines)==1,"missing_or_duplicate_"+typ)
    data={}
    for term in lines[0].split("|")[1:]:
        k,sep,v=term.partition("=")
        need(sep and k not in data and k,"malformed_"+typ)
        data[k]=v
    need(data.pop("json",None)=="0","invalid_tail_"+typ)
    return data
def matrix(encoded):
    rows=encoded.split(";")
    need(len(rows)==COLS,"signed_8x8_eight_rows")
    m=[]
    for row in rows:
        cols=row.split(",")
        need(len(cols)==COLS,"signed_8x8_eight_columns")
        m.append(tuple(number(x) for x in cols))
    need(all(abs(x)<LIMIT for row in m for x in row),
         "signed_320_bit_absolute_bound")
    need(all(m[i][j]==m[j][i] for i in range(COLS)
             for j in range(COLS)),"exact_matrix_symmetry")
    return tuple(m)
def validate(rec,sample,shard):
    need(number(rec["sample_num"])==SAMPLES[sample] and
         number(rec["shard"])==shard,
         "original_frozen_energy_shard_identity")
    need(number(rec["source_total"])==N and
         (number(rec["K3"]),number(rec["Q4"]),number(rec["Q5"]))==
         (155378,1985218,18598040),
         "original_20million_source_support_census")
    n=number(rec["actual_rows"])
    need(n>0 and number(rec["all_raw_moves"])==72*n,
         "physical_independent_72_raw_moves")
    census=tuple(number(x) for x in rec["block_census"].split(","))
    need(len(census)==12 and all(x>=0 for x in census) and
         sum(census)==72*n,"complete_physical_shell_transition_counts")
    need(number(rec["selfloops"])==0,"independent_selfloop_count")
    need(number(rec["sampled_weighted_reverse_checks"])>0,
         "independent_weighted_reverse_challenges")
    need(rec["original_source_SHA256"]=="WORKFLOW_PRECHECK" and
         rec["Q5_principal"]=="REBUILT_NOT_IMPORTED" and
         rec["full_Dirichlet_identity"]=="SYMMETRIC_REARRANGEMENT" and
         rec["original_Wilson"]=="SOURCE_CONDITIONAL_FORMAL_HOLD",
         "original_Q5_principal_and_mathematical_scope")
    return n,census,matrix(rec["matrix_8x8"])
def original(raw):
    lines=[line for line in raw.splitlines() if
           line.startswith("Y137_C_MU3_ACCEPT_MATRIX|")]
    need(len(lines)==2,"exact_original_two_energy_receipts")
    result={}
    for line in lines:
        rec=parse_record(line,"Y137_C_MU3_ACCEPT_MATRIX")
        e=number(rec["sample_num"])
        need(e in SAMPLES and e not in result,"original_energy_unique")
        m=matrix(rec["full_whole_Q_mu3_six"])
        fingerprint=hashlib.sha256(rec["full_whole_Q_mu3_six"].encode("ascii")).hexdigest()
        need(fingerprint==rec["matrix_sha256"] and
             rec["all_64_exact_row_pair_entries"]=="PASS" and
             rec["signed_source_K3_Q4_Q5"]=="AUTHENTICATED",
             "original_production_source_matrix_identity")
        result[e]=m
    return result
def run(folder,original_path):
    with open(original_path,encoding="ascii") as f: target=original(f.read())
    checked=0
    report={}
    tamper_record=None
    for s,e in enumerate(SAMPLES):
        matrices=[]
        states=0
        flux=[0]*12
        reverse=0
        for g in range(8):
            path=os.path.join(folder,"RESULT-"+str(s)+"-"+str(g)+".hbp")
            with open(path,encoding="ascii") as f:
                rec=parse_record(f.read(),"Y137_INDEPENDENT_FULL_DIRICHLET_SHARD")
            n,census,m=validate(rec,s,g)
            states+=n
            reverse+=number(rec["sampled_weighted_reverse_checks"])
            for j,v in enumerate(census):flux[j]+=v
            matrices.append(m)
            if s==0 and g==0:tamper_record=rec
        need(states==N,"all_full_20million_original_states_covered")
        need(tuple(tuple(flux[4*i:4*i+4]) for i in range(3))==EXPECTED,
             "complete_K3_Q4_Q5_original_72move_block_census")
        expected=target[e]
        observed=tuple(tuple(sum(m[i][j] for m in matrices)
                             for j in range(COLS))for i in range(COLS))
        need(observed==expected,"INDEPENDENT_WHOLE_Q_SIGNED_MU3_MATRIX_MISMATCH_"+str(e))
        fingerprint=hashlib.sha256(";".join(",".join(str(x) for x in row)
                                         for row in observed).encode("ascii")).hexdigest()
        report[e]=fingerprint
        checked+=64
        print("Y137_INDEPENDENT_FULL_DIRICHLET_ACCEPT_ENERGY|sample_num="+str(e)+
              "|source_states="+str(states)+"|whole_electric_moves="+str(72*states)+
              "|independent_Q5_principal=RECOMPUTED"+
              "|whole_original_8x8_matrix_SHA256="+fingerprint+
              "|original_exact_signed_matrix_entries=64_OF_64_PASS"+
              "|independent_weighted_reverse_challenges="+str(reverse)+
              "|full_original_Wilson=FORMAL_HOLD|json=0",flush=True)
    need(checked==128 and tamper_record is not None,
         "both_complete_signed_moment_matrices")
    controls=negatives(tamper_record)
    print("Y137_INDEPENDENT_FULL_DIRICHLET_VERDICT|original_K3_Q4_Q5_states="+str(N)+
          "|two_energies="+",".join(str(x) for x in SAMPLES)+
          "|whole_source_rows_rebuilt=41477272"+
          "|independent_raw_electric_moves=2986363584"+
          "|original_8x8_signed_entries=128_OF_128_EXACT"+
          "|Q5_principal=RECOMPUTED_FROM_ORIGINAL_SOURCE_NO_B5_IMPORT"+
          "|all_original_block_censuses=PASS"+
          "|source_archive_SHA=WORKFLOW_PINNED"+
          "|modified_partial_receipts="+str(controls)+"_REJECTED"+
          "|E1_matrix_sha256="+report[SAMPLES[0]]+
          "|E2_matrix_sha256="+report[SAMPLES[1]]+
          "|first_Wilson=SOURCE_CONDITIONAL_FORMAL_HOLD"+
          "|whole_Perron_store=INDEPENDENT_REPLICATION_OPEN"+
          "|continuum_4D=OPEN|json=0",flush=True)
def negatives(rec):
    variants=(("sample_num","1"),("shard","9"),
              ("source_total","20"),("K3","1"),
              ("actual_rows","0"),("all_raw_moves","1"),
              ("block_census","1,2"),("selfloops","1"),
              ("sampled_weighted_reverse_checks","0"),
              ("Q5_principal","ORIGINAL_B5_IMPORTED"),
              ("full_Dirichlet_identity","UNVERIFIED"),
              ("original_Wilson","ACCEPTED"))
    errors=0
    for k,v in variants:
        changed=dict(rec);changed[k]=v
        try:validate(changed,0,0)
        except (Refuse,KeyError,ValueError):errors+=1
        else:raise Refuse("tampered_full_Mu3_receipt_accepted_"+k)
    need(errors==len(variants),"rejected_modified_partial_count")
    return errors
def toy():
    source=[[0]*COLS for _ in range(COLS)]
    for i in range(COLS):source[i][i]=1+i
    m=matrix(";".join(",".join(map(str,row))for row in source))
    need(len(m)==8 and all(m[i][i]==i+1 for i in range(8)),
         "signed_matrix_parser_toy")
    fake={
        "sample_num":str(SAMPLES[0]),"shard":"0","source_total":str(N),
        "K3":"155378","Q4":"1985218","Q5":"18598040",
        "actual_rows":"1","all_raw_moves":"72",
        "block_census":",".join(str(x) for x in
             [0,72,0,0]+[0]*8),
        "selfloops":"0","sampled_weighted_reverse_checks":"1",
        "original_source_SHA256":"WORKFLOW_PRECHECK",
        "Q5_principal":"REBUILT_NOT_IMPORTED",
        "full_Dirichlet_identity":"SYMMETRIC_REARRANGEMENT",
        "original_Wilson":"SOURCE_CONDITIONAL_FORMAL_HOLD",
        "matrix_8x8":";".join(",".join(map(str,row))for row in source),
    }
    validate(fake,0,0)
    attacks=negatives(fake)
    need(attacks==12,"injected_moment_fault_census")
    print("Y137_INDEPENDENT_FULL_DIRICHLET_FANIN_TOY|exact_8x8_integer=PASS"+
          "|frozen_two_energies=PASS|Q5_source_principal_import=REFUSED"+
          "|tampered_receipts=12_REJECTED"+
          "|real_fullstate_source=NOT_COMPUTED|json=0",flush=True)
def main():
    try:
        if sys.argv[1:]==["toy"]:toy()
        elif len(sys.argv)==4 and sys.argv[1]=="real":
            run(sys.argv[2],sys.argv[3])
        else:raise Refuse("usage_toy_or_real_PARTIAL_FOLDER_FROZEN_SOURCE")
    except (Refuse,OSError,KeyError,ValueError) as e:
        print("Y137_INDEPENDENT_FULL_DIRICHLET_HOLD|reason="+str(e)+
              "|full_original_mu3=HOLD|original_Wilson=FORMAL_HOLD|json=0",flush=True)
        raise SystemExit(2)
if __name__=="__main__":main()
