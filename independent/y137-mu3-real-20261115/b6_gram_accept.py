#!/usr/bin/env python3
"""#137 B6: independent SHA-256 of archived physical-Q5 Gram matrix text.

Consumes Rust's exact source-derived matrices and compares the encoded 8x8 text
against all sixteen *previously frozen* SHA fingerprints. Integer/ASCII only.
"""
import hashlib
import os
import sys

SAMPLES=(69909875505, 69949729820)
ROWS=(435324,4439918,988399,2812763,822474,3973928,1612450,3512784)

def need(ok, why):
    if not ok:
        raise ValueError(why)

def fields(line, prefix):
    name, *parts = line.rstrip("\n\r").split("|")
    need(name == prefix, "B6_wrong_prefix")
    ans={}
    for part in parts:
        key, sep, value = part.partition("=")
        need(bool(sep) and key not in ans, "B6_bad_or_duplicate_key")
        ans[key]=value
    need(ans.get("json")=="0", "B6_noncanonical_json_marker")
    return ans

def original(manifest):
    rows={}
    with open(manifest, encoding="ascii") as src:
        for line in src:
            if line.startswith("Y137_D11_V1_ALL_GROUP|"):
                r=fields(line,"Y137_D11_V1_ALL_GROUP")
                group=int(r["group"])
                need(group in range(8) and group not in rows, "B6_duplicate_group")
                rows[group]=r
    need(set(rows)==set(range(8)), "B6_missing_frozen_source_group")
    return rows

def matrix_encoding(text):
    rows=text.split(";")
    need(len(rows)==8, "B6_not_eight_rows")
    for i,row in enumerate(rows):
        values=row.split(",")
        need(len(values)==8, "B6_not_eight_columns")
        for j,value in enumerate(values):
            need(bool(value) and not (value.startswith("0") and value!="0") and
                 all(c in "0123456789" for c in value), "B6_noncanonical_integer")
            if j<i:
                need(value==rows[j].split(",")[i], "B6_nonsymmetric_gram")
    return text.encode("ascii")

def validate(manifest, group, receipt):
    expected=original(manifest)[group]
    records={}
    with open(receipt, encoding="ascii") as src:
        for line in src:
            if line.startswith("Y137_B6_GRAM|"):
                r=fields(line,"Y137_B6_GRAM")
                z=int(r["sample_num"])
                need(z in SAMPLES and z not in records and int(r["group"])==group,
                     "B6_wrong_or_duplicate_energy")
                need(r["quantity"]=="Q5_mu2_six", "B6_wrong_Gram_scale")
                records[z]=r
    need(set(records)==set(SAMPLES), "B6_missing_sample")
    outputs=[]
    for index,z in enumerate(SAMPLES):
        encoded=matrix_encoding(records[z]["encoding"])
        digest=hashlib.sha256(encoded).hexdigest()
        wanted=expected["sample_E"+str(index+1)+"_sha256"]
        need(digest==wanted,"B6_frozen_historic_Gram_sha_mismatch")
        outputs.append("Y137_B6_ACCEPT|group="+str(group)+
                       "|sample_num="+str(z)+"|sha256="+digest+
                       "|frozen_Gram=EXACT|json=0")
    return "\n".join(outputs)+"\n"

def aggregate(manifest, folder):
    accepted=original(manifest)
    total=0
    for group in range(8):
        file=os.path.join(folder, "GROUP-"+str(group)+".hbp")
        with open(file, encoding="ascii") as src:
            lines=src.read().splitlines()
        need(len(lines)==2, "B6_missing_or_extra_group_receipt")
        for index,line in enumerate(lines):
            r=fields(line,"Y137_B6_ACCEPT")
            z=SAMPLES[index]
            need(int(r["group"])==group and int(r["sample_num"])==z,
                 "B6_wrong_group_or_energy_order")
            need(r["frozen_Gram"]=="EXACT" and
                 r["sha256"]==accepted[group]["sample_E"+str(index+1)+"_sha256"],
                 "B6_forged_or_stale_Gram_receipt")
            total+=1
    need(total==16,"B6_incomplete_16_fingerprints")
    return ("Y137_B6_VERDICT|source_groups=8|energy_samples=2"+
            "|frozen_Gram_fingerprints=16|matches=16|mismatches=0"+
            "|preregistered_B6=PASS|whole_mu3=NOT_COMPUTED"+
            "|Wilson_weight=HOLD|json=0\n")

def toy():
    q=[1,2,3,4,5,6,7,8]
    w=2
    b=1_000_000_000
    mat=";".join(",".join(str(6*w*b*b*q[i]*q[j])
                     for j in range(8)) for i in range(8))
    canonical=matrix_encoding(mat)
    need(hashlib.sha256(canonical).hexdigest()==
         hashlib.sha256(mat.encode("ascii")).hexdigest(),"B6_toy_exact_encoding")
    altered=mat.replace(str(6*w*b*b*q[0]*q[0]),str(36*w*b*b*q[0]*q[0]),1)
    refused=0
    try:
        need(hashlib.sha256(matrix_encoding(altered)).hexdigest()==
             hashlib.sha256(canonical).hexdigest(),
             "B6_wrong_factor_six_accepted")
    except ValueError:
        refused+=1
    noncanonical=mat.replace(str(6*w*b*b*q[0]*q[0]),"0"+str(6*w*b*b*q[0]*q[0]),1)
    try:
        matrix_encoding(noncanonical)
    except ValueError:
        refused+=1
    need(refused==2,"B6_toy_mutated_Gram_accepted")
    print("Y137_B6_TOY|unsigned_8x8_symmetric=PASS|double_factor_six=REFUSED"+
          "|noncanonical_integer=REFUSED|frozen_real_Grams=NOT_COMPUTED|json=0")

def main(argv):
    try:
        if argv==["toy"]:
            toy()
        elif len(argv)==5 and argv[0]=="verify":
            _,manifest,group,source,out=argv
            g=int(group)
            need(g in range(8),"B6_bad_group")
            result=validate(manifest,g,source)
            with open(out,"w",encoding="ascii",newline="\n") as f:f.write(result)
            print(result,end="")
        elif len(argv)==3 and argv[0]=="aggregate":
            _,manifest,folder=argv
            print(aggregate(manifest,folder),end="")
        else:
            raise ValueError("B6_usage")
    except (ValueError, OSError, UnicodeError, KeyError) as exc:
        print("Y137_B6_REFUSE|reason="+str(exc)+"|json=0",flush=True)
        raise SystemExit(1) from None

if __name__=="__main__":
    main(sys.argv[1:])
