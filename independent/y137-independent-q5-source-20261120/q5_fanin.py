#!/usr/bin/env python3
"""Strict independent exact 8-way original-Q5 V1/b and source geometry fan-in.

Streaming 8-way sorted merge against independent Q4->Q5 complete boundary
sources; O(8) key memory, original u64 byte-equality, no floating arithmetic.
"""
import hashlib
import heapq
import pathlib
import struct
import sys

N=18_598_040
GROUP_ROWS=(435324,4439918,988399,2812763,822474,3973928,1612450,3512784)
GROUPS=len(GROUP_ROWS)
LANES=16
MOVES=72

class Refuse(Exception):
    pass

def need(ok,why):
    if not ok:raise Refuse(why)

def row(line,prefix):
    need(line.startswith(prefix+"|"),"missing_receipt_"+prefix)
    out={}
    for part in line.split("|")[1:]:
        k,sep,v=part.partition("=")
        need(sep=="=" and k not in out,"duplicate_or_bad_receipt_field")
        out[k]=v
    need(out.get("json")=="0","bad_receipt_termination")
    return out

def iter_u64(path,expected):
    need(path.stat().st_size==8*expected,"original_Q5_key_file_byte_count_"+path.name)
    with open(path,"rb") as src:
        last=None
        for _ in range(expected):
            block=src.read(8)
            need(len(block)==8,"Q5_short_key_file")
            addr=struct.unpack("<Q",block)[0]
            if last is not None:
                need(addr>last,"Q5_duplicate_or_unsorted_keys_"+path.name)
            last=addr
            yield addr
        need(not src.read(1),"extra_Q5_address_bytes")

def check_exact_group_union(groups,independent,expected):
    original=heapq.merge(*groups)
    h=hashlib.sha256()
    prev=None
    total=0
    for source_key in independent:
        try:old_key=next(original)
        except StopIteration:raise Refuse("Q5_missing_original_archive_target")
        need(old_key==source_key,"original_Q5_source_not_independent_Q4_boundary")
        if prev is not None:need(old_key>prev,"duplicate_original_Q5_group_address")
        prev=old_key
        h.update(struct.pack("<Q",old_key))
        total+=1
    try:next(original)
    except StopIteration:pass
    else:raise Refuse("extra_original_Q5_archived_target")
    need(total==expected,"complete_independent_Q5_18598040_target_census")
    return h.hexdigest()

def real(root):
    source=root.joinpath("ALL-INDEPENDENT-Q5-KEYS.bin")
    independent=iter_u64(source,N)
    groups=[]
    for group,count in enumerate(GROUP_ROWS):
        record=root.joinpath("RESULT-Q5-SHARD-"+str(group)+".hbp")
        lines=record.read_text(encoding="ascii").splitlines()
        matches=[l for l in lines if l.startswith("Y137_INDEPENDENT_Q5_SOURCE_SHARD|")]
        need(len(matches)==1,"missing_real_Q5_group_verdict_"+str(group))
        f=row(matches[0],"Y137_INDEPENDENT_Q5_SOURCE_SHARD")
        need(int(f["group"])==group and
             int(f["original_Q5_targets"])==count and
             int(f["exact_unsigned_V1_over_b_components"])==16*count and
             int(f["physical_72_moves"])==72*count and
             f["original_archive_source"]=="SHA256_PINNED" and
             f["original_K3_Q4_R"]=="FIRST_PRINCIPLES" and
             f["original_packed_V1_over_b"]=="EXACT_ALL_LANES",
             "Q5_source_group_failed_acceptance_"+str(group))
        groups.append(iter_u64(root.joinpath("ORIGINAL-Q5-KEYS-"+str(group)+".bin"),count))
    receipt=root.joinpath("RESULT-Q5-TARGET-SUPPORT.hbp")
    support=[l for l in receipt.read_text(encoding="ascii").splitlines()
             if l.startswith("Y137_INDEPENDENT_Q5_TARGET_SUPPORT|")]
    need(len(support)==1,"missing_new_independent_S3_Q5_target_support")
    p=row(support[0],"Y137_INDEPENDENT_Q5_TARGET_SUPPORT")
    need(int(p["first_principles_Q4_sources"])==1_985_218 and
         int(p["complete_Q5_destinations"])==N and
         int(p["original_Q4_72_raw_moves"])==1_985_218*72,
         "original_Q5_target_reconstruction_provenance")
    digest=check_exact_group_union(groups,independent,N)
    print("Y137_INDEPENDENT_Q5_FIRST_PRINCIPLES_ACCEPT|hosted_source_groups=8_OF_8"+
          "|original_Q5_destinations=18598040_OF_18598040_EXACT"+
          "|physical_source_72move_rows=18598040"+
          "|original_Q5_V1_over_b_two_energy_components=297568640_OF_297568640_EXACT"+
          "|physical_Q5_raw_moves=1339058880"+
          "|independent_target_source=FULL_Q4_S3_PHYSICAL_BOUNDARY"+
          "|original_and_rebuilt_Q5_address_set_SHA256="+digest+
          "|source_K3_Q4=FIRST_PRINCIPLES_PASS"+
          "|first_Wilson=SOURCE_CONDITIONAL_FORMAL_HOLD|json=0")

def toy():
    rows=list(range(17))
    chunks=[rows[17*g//8:17*(g+1)//8] for g in range(8)]
    need(len(check_exact_group_union([iter(x) for x in chunks],iter(rows),17))==64,
         "Q5_fanin_toy_unique_exact_set")
    rejected=0
    bad=[x[:] for x in chunks]
    bad[2]=bad[2][:-1]+[bad[1][-1]]
    try:check_exact_group_union([iter(x) for x in bad],iter(rows),17)
    except Refuse:rejected+=1
    bad=[x[:] for x in chunks]
    bad[0]=bad[0][:-1]
    try:check_exact_group_union([iter(x) for x in bad],iter(rows),17)
    except Refuse:rejected+=1
    bad=list(rows)
    bad[6]=18
    bad.sort()
    try:check_exact_group_union([iter(x) for x in chunks],iter(bad),17)
    except Refuse:rejected+=1
    need(rejected==3,"Q5_fanin_negative_controls_not_rejected")
    print("Y137_Q5_FANIN_TOY|exact_8way_u64_merge=PASS"+
          "|missing_duplicate_replaced_key_controls=3_REJECTED"+
          "|original_Q5=NOT_COMPUTED|json=0")

def main(argv):
    try:
        if argv==["toy"]:toy()
        elif len(argv)==2 and argv[0]=="real":real(pathlib.Path(argv[1]))
        else:raise Refuse("usage")
    except (Refuse,OSError,KeyError,ValueError,UnicodeError) as e:
        print("Y137_INDEPENDENT_Q5_FANIN_HOLD|reason="+str(e)+
              "|original_Q5_source=HOLD|Wilson=FORMAL_HOLD|json=0")
        raise SystemExit(2) from None

if __name__=="__main__":
    main(sys.argv[1:])
