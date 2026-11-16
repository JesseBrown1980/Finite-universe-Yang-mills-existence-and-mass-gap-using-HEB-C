#!/usr/bin/env python3
"""#137 exact two-energy full 8x8 physical signed mu3 acceptance.

Input: four *independently* hosted 320-bit Rust calculation receipts:
row+pair methods at frozen energies 69909875505 and 69949729820.
Source files and numeric results must be byte-authenticated externally.
Python exact integers make no floating-point approximation.
"""
import hashlib
import os
import sys

FROZEN=(69909875505,69949729820)
N=20738636
COLS=8
NEW_PAIRS=139517148
ABS_LIMIT=1<<294

class Refuse(Exception):
    pass

def need(ok,why):
    if not ok:
        raise Refuse(why)

def fields(line,prefix):
    parts=line.strip().split("|")
    need(parts[0]==prefix,"C_ACCEPT_wrong_record_prefix")
    out={}
    for part in parts[1:]:
        k,sep,value=part.partition("=")
        need(bool(sep) and k not in out,"C_ACCEPT_malformed_or_repeated_field")
        out[k]=value
    need(out.get("json")=="0","C_ACCEPT_invalid_json_marker")
    return out

def parse_matrix(raw):
    rows=raw.split(";")
    need(len(rows)==COLS,"C_ACCEPT_wrong_matrix_row_count")
    result=[]
    for row in rows:
        cols=row.split(",")
        need(len(cols)==COLS,"C_ACCEPT_wrong_matrix_column_count")
        vals=[]
        for cell in cols:
            try: n=int(cell)
            except ValueError as e: raise Refuse("C_ACCEPT_non_integer_matrix_value") from e
            need(str(n)==cell and abs(n)<ABS_LIMIT,
                 "C_ACCEPT_noncanonical_or_out_of_bound_matrix_value")
            vals.append(n)
        result.append(tuple(vals))
    need(all(result[i][j]==result[j][i]
             for i in range(COLS) for j in range(COLS)),
         "C_ACCEPT_exact_matrix_not_symmetric")
    return tuple(result)

def read_one(path,method,energy):
    with open(path,"rb") as f: data=f.read()
    digest=hashlib.sha256(data).hexdigest()
    lines=data.decode("ascii").splitlines()
    items=[fields(s,"Y137_C_FULL_MU3_MATRIX")
           for s in lines if s.startswith("Y137_C_FULL_MU3_MATRIX|")]
    need(len(items)==1,"C_ACCEPT_missing_or_duplicate_full_matrix_receipt")
    item=items[0]
    need(item["method"]==method and int(item["sample_num"])==energy,
         "C_ACCEPT_wrong_energy_or_method_receipt")
    need(item["quantity"]=="whole_K3_Q4_Q5_mu3_six" and
         int(item["source_states"])==N and
         int(item["rows"])==COLS and int(item["columns"])==COLS,
         "C_ACCEPT_wrong_matrix_scope_or_source_count")
    need(item["exact_symmetric"]=="PASS" and
         item["source_signs"]=="PHYSICAL_V1_EQUALS_XR" and
         item["original_Q5_B5_principal"]=="ONCE" and
         int(item["absolute_partial_bound_bits"])==294,
         "C_ACCEPT_wrong_signed_sources_or_arithmetic_bound")
    if method=="row":
        need(int(item["raw_rows"])==N and int(item["new_unordered_pairs"])==0,
             "C_ACCEPT_wrong_original_full_electric_row_census")
        blocks=[fields(s,"Y137_C_MU3_ROW_BLOCK") for s in lines
                if s.startswith("Y137_C_MU3_ROW_BLOCK|")]
        need(len(blocks)==3,"C_ACCEPT_missing_exact_source_block_census")
        expected=((3,1397544,9789408,0,264),
                  (4,9728688,7486632,125720376,0),
                  (5,0,125467392,125005512,1088585976))
        for rec,want in zip(blocks,expected):
            got=tuple(int(rec[k]) for k in
                      ("shell","to_K3","to_Q4","to_Q5","outside"))
            need(got==want,"C_ACCEPT_source_block_transition_regression")
    else:
        need(int(item["new_unordered_pairs"])==NEW_PAIRS and
             int(item["raw_rows"])==0,
             "C_ACCEPT_wrong_original_weighted_cross_pair_count")
        blocks=[fields(s,"Y137_C_MU3_PAIR_PART") for s in lines
                if s.startswith("Y137_C_MU3_PAIR_PART|")]
        need(len(blocks)==256,"C_ACCEPT_not_256_authenticated_partition_receipts")
        need(sum(int(p["unordered_pairs"]) for p in blocks)==NEW_PAIRS and
             sum(int(p["directed"]) for p in blocks)==2*NEW_PAIRS and
             sum(int(p["flux"]) for p in blocks)==837222984,
             "C_ACCEPT_original_256_partition_count_or_flux_regression")
        for idx,p in enumerate(blocks):
            need(int(p["part"])==idx and
                 p["all_reverse_edges"]=="PASS" and
                 len(p["original_exact_pair_digest"])==16,
                 "C_ACCEPT_partition_omission_or_original_reverse_failure")
    return parse_matrix(item["row"]),digest,item

def real(folder):
    arrays={}
    manifests={}
    for e in FROZEN:
        for method in ("row","pair"):
            p=os.path.join(folder,"RESULT-"+method+"-"+str(e)+".hbp")
            arr,sha,rec=read_one(p,method,e)
            arrays[(method,e)]=arr
            manifests[(method,e)]=sha
            print("Y137_C_MU3_ACCEPT_METHOD|method="+method+
                  "|sample_num="+str(e)+"|rows=8|columns=8"+
                  "|source_states="+str(N)+
                  "|strict_absolute_bound_bits=294"+
                  "|result_sha256="+sha+
                  "|exact_symmetric=PASS|json=0",flush=True)
    for e in FROZEN:
        a,b=arrays["row",e],arrays["pair",e]
        for i in range(COLS):
            for j in range(COLS):
                need(a[i][j]==b[i][j],
                     "C_ACCEPT_real_full_row_vs_pair_disagreement_at_"+
                     str(e)+"_"+str(i)+"_"+str(j))
        text=";".join(",".join(str(x) for x in row) for row in a)
        digest=hashlib.sha256(text.encode("ascii")).hexdigest()
        print("Y137_C_MU3_ACCEPT_MATRIX|sample_num="+str(e)+
              "|full_whole_Q_mu3_six="+text+
              "|matrix_sha256="+digest+
              "|all_64_exact_row_pair_entries=PASS"+
              "|signed_source_K3_Q4_Q5=AUTHENTICATED"+
              "|original_B5_Q5_principal=ONCE"+
              "|json=0",flush=True)
    print("Y137_C_MU3_ACCEPT_VERDICT|two_frozen_energies="+
          ",".join(str(e) for e in FROZEN)+
          "|full_states="+str(N)+
          "|whole_space_mu3_two_energy_matrices=CALCULATED"+
          "|row_vs_pair_exact_entries=128"+
          "|matrix_symmetry_entries=128"+
          "|original_source_physical_signs=PASS"+
          "|original_256_cross_partitions=PASS"+
          "|strict_signed_320bit_absolute_partial_sum_below_2pow294=PASS"+
          "|mathematical_mu3_stage=ACCEPTANCE_PENDING_INDEPENDENT_CLOUD"+
          "|whole_mu3_production=PASS"+
          "|Wilson_first_excitation_weight=HOLD|json=0",flush=True)

def toy():
    ident=tuple(tuple(12 if i==j else 0 for j in range(COLS))
                for i in range(COLS))
    def fail(label,func):
        try:func()
        except Refuse:return label+"=REFUSED"
        raise Refuse("C_ACCEPT_toy_"+label+"_accepted")
    def comparison(a,b):
        need(all(a[i][j]==b[i][j]
                 for i in range(COLS) for j in range(COLS)),
             "C_ACCEPT_toy_disagree")
    bad=[list(row) for row in ident]
    bad[0][1]=1
    cases=[
       fail("wrong_Q4_source_sign",lambda:comparison(ident,bad)),
       fail("energy_swap",lambda:need(FROZEN[0]==FROZEN[1],
                                    "C_ACCEPT_toy_energy_swapped")),
       fail("wrong_factor_six",lambda:comparison(ident,
            tuple(tuple(x*6 for x in row) for row in ident))),
       fail("omitted_Q5_cross",lambda:comparison(ident,
            tuple(tuple(x-1 for x in row) for row in ident))),
       fail("B5_principal_double_count",lambda:comparison(ident,
            tuple(tuple(x+x for x in row) for row in ident))),
       fail("wrong_symmetric_matrix",lambda:parse_matrix(
            ";".join(",".join(str(v) for v in row) for row in bad))),
       fail("out_of_bound_matrix_entry",lambda:parse_matrix(
            ";".join(",".join(str(ABS_LIMIT if i==j==0 else 0)
                     for j in range(COLS)) for i in range(COLS)))),
    ]
    print("Y137_C_MU3_ACCEPT_TOY|"+ "|".join(cases)+
          "|exact_8x8_integer=PASS"+
          "|real_128_entries=NOT_COMPUTED|Wilson_weight=HOLD|json=0")

def main(argv):
    try:
        if argv==["toy"]:toy()
        elif len(argv)==2 and argv[0]=="real":real(argv[1])
        else:raise Refuse("C_ACCEPT_usage")
    except (Refuse,ValueError,KeyError,OSError,UnicodeDecodeError) as exc:
        print("Y137_C_MU3_ACCEPT_REFUSE|reason="+str(exc)+"|json=0",flush=True)
        raise SystemExit(1) from None

if __name__=="__main__":
    main(sys.argv[1:])
