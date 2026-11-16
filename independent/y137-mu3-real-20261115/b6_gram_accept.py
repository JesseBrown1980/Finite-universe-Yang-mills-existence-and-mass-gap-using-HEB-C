#!/usr/bin/env python3
"""#137 B6: independent SHA-256 of archived physical-Q5 Gram matrix text.

Consumes Rust's exact source-derived matrices and compares the encoded 8x8 text
against all sixteen *previously frozen* SHA fingerprints. Integer/ASCII only.
"""
import hashlib
import os
import sys
import tempfile

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
    source_manifest_bytes=open(manifest,"rb").read()
    manifest_sha=hashlib.sha256(source_manifest_bytes).hexdigest()
    total=0
    for group in range(8):
        file=os.path.join(folder, "GROUP-"+str(group)+".hbp")
        gram=os.path.join(folder, "GRAM-"+str(group)+".hbp")
        source_receipt=os.path.join(folder,"SOURCE-"+str(group)+".hbp")
        with open(file, encoding="ascii") as src:
            recorded=src.read()
        # Reconstruct each claim from full numeric 8x8 matrix text, not
        # from an untrusted self-reported PASS or hash claim.
        independently_calculated=validate(manifest,group,gram)
        need(recorded==independently_calculated,
             "B6_forged_or_stale_PASS_receipt_numeric_matrix")
        with open(source_receipt,encoding="ascii") as src:
            source_lines=src.read().splitlines()
        need(len(source_lines)==2,"B6_missing_or_extra_source_provenance")
        orig=accepted[group]
        actual=fields(source_lines[0],"Y137_STAGE_B_SOURCE_GROUP")
        pin=fields(source_lines[1],"Y137_STAGE_B_GROUP_INPUT")
        need(int(actual["group"])==group and
             int(actual["targets"])==int(orig["targets"]) and
             int(actual["bytes"])==int(orig["bytes"]) and
             actual["sha256"]==orig["sha256"] and
             actual["packed_vectors"]=="PASS" and
             actual["canonical_and_orbit_weights"]=="PASS" and
             actual["address_partition"]=="PASS" and
             pin["manifest_sha256"]==manifest_sha,
             "B6_wrong_source_provenance_or_forged_PASS")
        total+=2
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


def receipt_attack_selftest():
    """Attack the exact *real production verifier* with self-consistent toy files.

    All eight groups first satisfy original(), validate(), aggregate(). Then
    forge plausible PASS receipts while independently tampering numeric Gram
    source, energy identity, source provenance, and claimed digest.
    """
    refusal = {}

    def expect_refuse(label,action):
        try:
            action()
        except (ValueError, KeyError) as error:
            refusal[label] = str(error)
        else:
            raise ValueError("B8_forged_" + label + "_PASS_accepted")

    with tempfile.TemporaryDirectory() as root:
        manifest_path=os.path.join(root,"FROZEN.hbp")
        metadata=[]
        matrices={}
        for group in range(8):
            tags={}
            for index,z in enumerate(SAMPLES):
                q=[(group+1)*(c+2)+index for c in range(8)]
                gram=";".join(",".join(str(6*(group+1)*q[i]*q[j])
                                   for j in range(8)) for i in range(8))
                matrices[(group,z)]=gram
                tags["sample_E"+str(index+1)+"_sha256"]=hashlib.sha256(
                    gram.encode("ascii")).hexdigest()
            source_sha=hashlib.sha256(("B6-fixture-source-"+str(group)).encode()).hexdigest()
            metadata.append("Y137_D11_V1_ALL_GROUP|group="+str(group)+
                            "|targets=3|bytes=128|sha256="+source_sha+
                            "|sample_E1_sha256="+tags["sample_E1_sha256"]+
                            "|sample_E2_sha256="+tags["sample_E2_sha256"]+
                            "|json=0")
        with open(manifest_path,"w",encoding="ascii") as f:
            f.write("\n".join(metadata)+"\n")
        manifest_sha=hashlib.sha256(open(manifest_path,"rb").read()).hexdigest()

        for group in range(8):
            gram_lines=[]
            for z in SAMPLES:
                gram_lines.append("Y137_B6_GRAM|group="+str(group)+
                                  "|sample_num="+str(z)+
                                  "|quantity=Q5_mu2_six|encoding="+matrices[(group,z)]+
                                  "|json=0")
            with open(os.path.join(root,"GRAM-"+str(group)+".hbp"),
                      "w",encoding="ascii") as f:
                f.write("\n".join(gram_lines)+"\n")
            with open(os.path.join(root,"GROUP-"+str(group)+".hbp"),
                      "w",encoding="ascii") as f:
                f.write(validate(manifest_path,group,
                                 os.path.join(root,"GRAM-"+str(group)+".hbp")))
            orig=fields(metadata[group],"Y137_D11_V1_ALL_GROUP")
            receipt=("Y137_STAGE_B_SOURCE_GROUP|group="+str(group)+
                     "|targets=3|bytes=128|sha256="+orig["sha256"]+
                     "|packed_vectors=PASS|canonical_and_orbit_weights=PASS"+
                     "|address_partition=PASS|json=0\n"+
                     "Y137_STAGE_B_GROUP_INPUT|manifest_sha256="+manifest_sha+
                     "|json=0\n")
            with open(os.path.join(root,"SOURCE-"+str(group)+".hbp"),
                      "w",encoding="ascii") as f:f.write(receipt)
        original_verdict=aggregate(manifest_path,root)
        need("frozen_Gram_fingerprints=16|matches=16|mismatches=0" in original_verdict,
             "B8_valid_source_control_not_accepted")

        def mutate(filename,replacer,action):
            path=os.path.join(root,filename)
            with open(path,encoding="ascii") as f:
                original_content=f.read()
            corrupted=replacer(original_content)
            need(corrupted!=original_content,"B8_mutation_did_not_change_fixture")
            with open(path,"w",encoding="ascii") as f:f.write(corrupted)
            try:
                expect_refuse(action,lambda:aggregate(manifest_path,root))
            finally:
                with open(path,"w",encoding="ascii") as f:f.write(original_content)
            need(aggregate(manifest_path,root)==original_verdict,
                 "B8_verifier_restore_after_forgery")

        g=0
        z=SAMPLES[0]
        original_num=str(6*1*(2)*(2))
        mutate("GRAM-0.hbp",lambda v:v.replace(
            original_num+","+str(6*1*(2)*(3)),
            str(int(original_num)+1)+","+str(6*1*(2)*(3)),1),
            "altered_numeric_Gram")
        mutate("GROUP-0.hbp",lambda v:v.replace(
            "frozen_Gram=EXACT","frozen_Gram=PASS",1),
            "plausible_false_PASS")
        mutate("GROUP-0.hbp",lambda v:v.replace(
            "sha256=","sha256="+("0"*64),1),"forged_SHA_claim")
        mutate("SOURCE-0.hbp",lambda v:v.replace(
            "canonical_and_orbit_weights=PASS",
            "canonical_and_orbit_weights=FAIL",1),"false_canonical_source_receipt")
        mutate("SOURCE-0.hbp",lambda v:v.replace(
            "manifest_sha256="+manifest_sha,
            "manifest_sha256="+("0"*64),1),"wrong_manifest_provenance")
        mutate("GRAM-0.hbp",lambda v:v.replace(
            "sample_num="+str(z),"sample_num="+str(SAMPLES[1]),1),
            "swapped_energy_identifiers")
        need(len(refusal)==6 and all(refusal.values()),
             "B8_not_all_plausible_forgeries_refused")
        print("Y137_B8_VERIFIER_ATTACK|real_production_verifier=aggregate" +
              "|valid_8group_toy=ACCEPTED|altered_numeric_Gram=REFUSED" +
              "|plausible_false_PASS=REFUSED|forged_SHA_claim=REFUSED" +
              "|false_canonical_source_receipt=REFUSED" +
              "|wrong_manifest_provenance=REFUSED" +
              "|swapped_energy_identifiers=REFUSED|forgeries_refused=6" +
              "|live_B6_16_of_16=UNAFFECTED|json=0")


def main(argv):
    try:
        if argv==["toy"]:
            toy()
        elif argv==["attack-toy"]:
            receipt_attack_selftest()
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
