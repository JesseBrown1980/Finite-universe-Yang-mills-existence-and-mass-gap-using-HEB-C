#!/usr/bin/env python3
"""Independent exact, full-address fan-in of eight first-principles Q4 V1 shards.

Input only eight hosted records and eight exact sorted u64 address lists,
plus a separately generated complete original-geometry Q4 key list.
An exact set equality is required; hashes alone cannot substitute.
"""
import hashlib
import pathlib
import struct
import sys
import tempfile

N=1_985_218
SHARDS=8
LANES=16
MOVES=72

class Refuse(Exception):
    pass

def need(ok,reason):
    if not ok:raise Refuse(reason)

def keys_from_bytes(data):
    need(len(data)%8==0,"Q4_key_list_is_not_aligned_u64")
    return [x[0] for x in struct.iter_unpack("<Q",data)]

def validate(groups,independent,total):
    need(len(groups)==SHARDS,"Q4_missing_one_of_eight_shards")
    need(len(independent)==total,"independent_Q4_geometry_census")
    need(all(a<b for a,b in zip(independent,independent[1:])),
         "independent_Q4_geometry_not_unique_sorted")
    union=[]
    for g,keys in enumerate(groups):
        start=total*g//SHARDS
        stop=total*(g+1)//SHARDS
        need(len(keys)==stop-start,"Q4_original_group_archive_census_"+str(g))
        need(all(a<b for a,b in zip(keys,keys[1:])),
             "Q4_original_group_duplicate_or_unsorted_"+str(g))
        union.extend(keys)
    need(len(union)==total,"original_Q4_union_count")
    union.sort()
    need(all(a<b for a,b in zip(union,union[1:])),
         "cross_group_duplicate_Q4_source")
    need(union==independent,
         "original_Q4_archive_union_differs_from_independent_S3_shell4")
    return hashlib.sha256(b"".join(struct.pack("<Q",x) for x in union)).hexdigest()

def fields(line,prefix):
    need(line.startswith(prefix+"|"),"Q4_missing_shard_acceptance")
    out={}
    for col in line.rstrip("\n").split("|")[1:]:
        k,sep,v=col.partition("=")
        need(sep=="=" and k not in out,"Q4_malformed_receipt")
        out[k]=v
    need(out.get("json")=="0","Q4_receipt_marker")
    return out

def real(root):
    original=[]
    for g in range(SHARDS):
        keys=keys_from_bytes(root.joinpath("ORIGINAL-Q4-KEYS-"+str(g)+".bin").read_bytes())
        record=root.joinpath("RESULT-Q4-SHARD-"+str(g)+".hbp").read_text(encoding="ascii").splitlines()
        verdict=[line for line in record if line.startswith("Y137_INDEPENDENT_Q4_V1_SHARD|")]
        need(len(verdict)==1,"Q4_missing_original_v1_shard_verdict_"+str(g))
        f=fields(verdict[0],"Y137_INDEPENDENT_Q4_V1_SHARD")
        want=N*(g+1)//SHARDS-N*g//SHARDS
        need(int(f["group"])==g and int(f["rows"])==want,
             "Q4_original_complete_shard_count_"+str(g))
        need(int(f["exact_source_components"])==LANES*want
             and int(f["raw_72_electric_moves"])==MOVES*want
             and f["all_original_signed_V1_entries"]=="EXACT_FIRST_PRINCIPLES"
             and f["original_archive_immutable"]=="SHA_PINNED"
             and int(f["independent_Q4_set"])==N,
             "Q4_physical_source_verdict_mismatch_"+str(g))
        original.append(keys)
    independent=keys_from_bytes(root.joinpath("ALL-INDEPENDENT-Q4-KEYS.bin").read_bytes())
    union_sha=validate(original,independent,N)
    print("Y137_INDEPENDENT_Q4_V1_FANIN|original_Q4_archives=8_OF_8"+
          "|physical_Q4_rows="+str(N)+
          "|original_Q4_keys=FULL_SET_EXACT_MATCH"+
          "|new_independent_Q4_keys=FULL_SET_EXACT_MATCH"+
          "|original_two_energy_signed_V1_components="+str(N*LANES)+
          "_OF_"+str(N*LANES)+"_MATCH"+
          "|physical_72_moves="+str(N*MOVES)+
          "|sorted_original_geometry_sha256="+union_sha+
          "|original_K3_Q4_source=FIRST_PRINCIPLES"+
          "|original_Wilson=SOURCE_CONDITIONAL_FORMAL_HOLD|json=0")

def toy():
    rows=list(range(17))
    parts=[rows[17*g//8:17*(g+1)//8] for g in range(8)]
    need(len(validate(parts,rows,17))==64,"independent_Q4_lexical_toy")
    rejected=0
    bad=[x[:] for x in parts]
    bad[3]=bad[3][:-1]+[bad[2][-1]]
    try:validate(bad,rows,17)
    except Refuse:rejected+=1
    bad=[x[:] for x in parts]
    bad[0]=bad[0][:-1]
    try:validate(bad,rows,17)
    except Refuse:rejected+=1
    bad=list(rows)
    bad[5]=100
    bad.sort()
    try:validate(parts,bad,17)
    except Refuse:rejected+=1
    need(rejected==3,"Q4_fault_controls_not_rejected")
    print("Y137_INDEPENDENT_Q4_FANIN_TOY|unique_complete_set=PASS"+
          "|altered_address_duplicate_and_missing=3_REJECTED"+
          "|exact_u64_sorted_lists=PASS|real_Q4=NOT_COMPUTED|json=0")

def main(argv):
    try:
        if argv==["toy"]:toy()
        elif len(argv)==2 and argv[0]=="real":
            real(pathlib.Path(argv[1]))
        else:raise Refuse("usage_toy_or_real_ROOT")
    except (Refuse,ValueError,KeyError,OSError,UnicodeError) as e:
        print("Y137_INDEPENDENT_Q4_FANIN_HOLD|reason="+str(e)+
              "|full_Q4_source=HOLD|Wilson=FORMAL_HOLD|json=0")
        raise SystemExit(2) from None

if __name__=="__main__":
    main(sys.argv[1:])
