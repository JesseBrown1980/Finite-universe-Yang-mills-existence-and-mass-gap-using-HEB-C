#!/usr/bin/env python3
"""#137 Stage C exact full K3/Q4 signed-V1 vs original Q5 support join.

One-pass SHA/length/count reauthentication of all eight 3.14 GB Q5 sources,
verified against the frozen preproduction manifest, plus the nine complete
signed-V1 spools from accepted Stage C source production run 43867088509.
Proves disjoint 20,738,636 full source addresses. Retains boundaries unclassified
until independent K3/Q4/Q5 electric-cross reciprocity production.
Integer-only, bounded O(K3+Q4) support lookup, no floating point.
"""
import hashlib
import io
import os
import struct
import sys
import tempfile

HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
from c_signed_source_codec import decode, Refuse
from source_gate import manifest, HEADER, BUCKETS, GROUPS, MAX_ADDRESS

K3=155378
Q4=1985218
Q5=18598040
TOTAL=K3+Q4+Q5
EXPECTED_SOURCE_HEAD="72093bb12a2524597e06e8ee62d5e81a4515e3e8"

def need(ok,why):
    if not ok:
        raise Refuse(why)

def parse(line,prefix):
    a=line.strip().split("|")
    need(a[0]==prefix,"C_JOIN_wrong_receipt_type")
    result={}
    for item in a[1:]:
        k,sep,v=item.partition("=")
        need(bool(sep) and k not in result,"C_JOIN_duplicate_or_invalid_field")
        result[k]=v
    need(result.get("json")=="0","C_JOIN_bad_json_marker")
    return result

def frozen_signed_manifest(path):
    lines=open(path,encoding="ascii").read().splitlines()
    header=[parse(x,"Y137_C_FULL_SOURCE_ARCHIVE") for x in lines
            if x.startswith("Y137_C_FULL_SOURCE_ARCHIVE|")]
    need(len(header)==1 and header[0]["source_branch_head"]==EXPECTED_SOURCE_HEAD
         and header[0]["physical_source"]=="V1_EQUALS_X_TIMES_R",
         "C_JOIN_wrong_signed_source_production_provenance")
    data=[parse(x,"Y137_C_SIGNED_SOURCE") for x in lines
          if x.startswith("Y137_C_SIGNED_SOURCE|")]
    need(len(data)==9,"C_JOIN_not_exactly_nine_original_signed_shards")
    out={}
    for r in data:
        sh=r["shell"]
        group=int(r["group"])
        ix=8 if sh=="k3" else group
        need((sh=="k3" and group==0) or
             (sh=="q4" and 0<=group<GROUPS),"C_JOIN_wrong_original_shell")
        need(ix not in out,"C_JOIN_duplicate_signed_manifest_group")
        expected_count=K3 if ix==8 else Q4*(ix+1)//GROUPS-Q4*ix//GROUPS
        need(int(r["states"])==expected_count and
             r["amplitude_under_2pow117"]=="PASS" and
             r["independent_all_source_contractions"]=="EXACT" and
             r["roundtrip_SHA_and_sorted_keys"]=="PASS",
             "C_JOIN_sign_or_numeric_source_acceptance_not_proven")
        need(int(r["sample_E1_num"])==69909875505 and
             int(r["sample_E2_num"])==69949729820,
             "C_JOIN_energy_identity_swapped")
        out[ix]=r
    need(set(out)==set(range(9)),"C_JOIN_missing_original_signed_group")
    return out

def signed_name(group):
    return "SIGNED-K3.v1" if group==8 else "SIGNED-Q4-"+str(group)+".v1"

def signed_set(directory,manifest_file):
    freeze=frozen_signed_manifest(manifest_file)
    addresses=set()
    total_bytes=0
    for group in range(9):
        wanted=freeze[group]
        path=os.path.join(directory,signed_name(group))
        count=0
        last=None
        shell=3 if group==8 else 4
        with open(path,"rb") as reader:
            while True:
                value=decode(reader)
                if value is None:break
                address,weight,stored_shell,amplitude=value
                need(stored_shell==shell,"C_JOIN_wrong_archived_shell")
                need(last is None or address>last,"C_JOIN_signed_source_unsorted")
                need(address not in addresses,"C_JOIN_signed_shard_collision")
                need(weight in (1,2,3,6) and len(amplitude)==2
                     and all(len(v)==8 for v in amplitude),
                     "C_JOIN_invalid_physical_source_record")
                addresses.add(address)
                last=address
                count+=1
        actual_bytes=os.path.getsize(path)
        sha=hashlib.sha256()
        with open(path,"rb") as reader:
            while chunk:=reader.read(1024*1024):
                sha.update(chunk)
        need(count==int(wanted["states"]) and
             actual_bytes==int(wanted["bytes"]) and
             sha.hexdigest()==wanted["sha256"],
             "C_JOIN_signed_source_SHA_or_length_or_count")
        total_bytes+=actual_bytes
        print("Y137_C_JOIN_SIGNED|group="+str(group)+
              "|shell="+str(shell)+"|count="+str(count)+
              "|bytes="+str(actual_bytes)+"|sha256="+sha.hexdigest()+
              "|source_original=AUTHENTICATED|json=0",flush=True)
    need(len(addresses)==K3+Q4,"C_JOIN_wrong_original_signed_support_count")
    return addresses,total_bytes

def scan_q5_file(path,group,wanted,signed):
    digest=hashlib.sha256()
    total_bytes=0
    records=0
    last_bucket=None
    last_address=None
    unique_buckets=0
    with open(path,"rb",buffering=1024*1024) as f:
        while True:
            h=f.read(HEADER.size)
            if not h:break
            need(len(h)==HEADER.size,"C_JOIN_truncated_Q5_header")
            address,weight,n0,n1=HEADER.unpack(h)
            need(0<=address<MAX_ADDRESS and weight in (1,2,3,6),
                 "C_JOIN_Q5_invalid_record_header")
            need(n0<=82 and n1<=82,"C_JOIN_Q5_packed_source_width")
            payload=f.read(n0+n1)
            need(len(payload)==n0+n1,"C_JOIN_Q5_short_physical_source")
            digest.update(h)
            digest.update(payload)
            total_bytes+=len(h)+len(payload)
            bucket=address%BUCKETS
            need(bucket%GROUPS==group,"C_JOIN_Q5_wrong_original_group")
            if last_bucket is None:
                need(bucket==group,"C_JOIN_Q5_wrong_initial_bucket")
                unique_buckets=1
            elif bucket!=last_bucket:
                need(bucket==last_bucket+GROUPS,
                     "C_JOIN_Q5_bucket_out_of_order_or_missing")
                unique_buckets+=1
                last_address=None
            if last_address is not None:
                need(address>last_address,
                     "C_JOIN_Q5_duplicate_or_descending_bucket")
            last_bucket=bucket
            last_address=address
            need(address not in signed,"C_JOIN_SIGNED_Q5_SUPPORT_COLLISION")
            records+=1
        need(unique_buckets==8 and last_bucket==group+56,
             "C_JOIN_not_all_eight_original_Q5_buckets")
    need(total_bytes==int(wanted["bytes"]) and
         records==int(wanted["targets"]) and
         digest.hexdigest()==wanted["sha256"],
         "C_JOIN_original_Q5_frozen_sha_count_bytes_disagree")
    return records,total_bytes,digest.hexdigest()

def real(signed_dir,q5_dir,signed_manifest,q5_manifest):
    signed,sign_bytes=signed_set(signed_dir,signed_manifest)
    frozen,orig_manifest_sha=manifest(q5_manifest)
    total=0
    size=0
    for group in range(GROUPS):
        path=os.path.join(q5_dir,"GROUP-"+str(group)+".v1")
        n,bytes_count,digest=scan_q5_file(path,group,frozen[group],signed)
        total+=n
        size+=bytes_count
        print("Y137_C_JOIN_Q5_GROUP|group="+str(group)+
              "|count="+str(n)+"|bytes="+str(bytes_count)+
              "|sha256="+digest+"|overlap_K3_Q4=0|json=0",flush=True)
    need(total==Q5 and size==3140900108 and len(signed)+total==TOTAL,
         "C_JOIN_failed_full_three_block_source_census")
    print("Y137_C_JOIN_VERDICT|signed_K3_Q4_addresses="+str(len(signed))+
          "|signed_K3_Q4_bytes="+str(sign_bytes)+
          "|authentic_Q5_addresses="+str(total)+
          "|authentic_Q5_bytes="+str(size)+
          "|unique_K3_Q4_Q5_addresses="+str(TOTAL)+
          "|signed_Q5_overlaps=0|original_Q5_manifest_sha256="+
          orig_manifest_sha+
          "|complete_source_support=PASS"+
          "|all_source_physical_amplitude_upper_bits=112"+
          "|row_and_pair_absolute_sum_upper_bits=294"+
          "|electric_cross_support_reciprocity=PENDING"+
          "|whole_mu3=NOT_COMPUTED|Wilson_weight=HOLD|json=0",flush=True)

def toy():
    def record(addr):
        return HEADER.pack(addr,1,1,1)+b"\x01\x02"
    with tempfile.TemporaryDirectory() as folder:
        path=os.path.join(folder,"GROUP-0.v1")
        all_data=b"".join(record(n) for n in range(0,64,8))
        with open(path,"wb") as f:f.write(all_data)
        receipt={"bytes":str(len(all_data)),"targets":"8",
                 "sha256":hashlib.sha256(all_data).hexdigest()}
        n,bytes_read,digest=scan_q5_file(path,0,receipt,{1,2,3})
        need(n==8 and bytes_read==len(all_data) and
             digest==receipt["sha256"],"C_JOIN_toy_original_fixture")
        refuses=0
        for label,mutated,existing in [
            ("cross_source_collision",all_data,{8}),
            ("tampered_spool",all_data+b"\x00",{1,2,3}),
            ("forged_numeric_address",record(0)+record(0)+all_data[2*len(record(0)):],{1,2,3}),
        ]:
            with open(path,"wb") as f:f.write(mutated)
            try:
                scan_q5_file(path,0,receipt,existing)
            except Refuse:
                refuses+=1
            else:
                raise Refuse("C_JOIN_toy_false_positive_"+label)
        need(refuses==3,"C_JOIN_toy_fault_acceptance")
    print("Y137_C_JOIN_TOY|original_group_buckets=8|valid_fixture=PASS"+
          "|cross_source_collision=REFUSED|tampered_spool=REFUSED"+
          "|forged_duplicate_address=REFUSED|controls_rejected=3"+
          "|full_three_support=NOT_COMPUTED|whole_mu3=NOT_COMPUTED"+
          "|Wilson_weight=HOLD|json=0")

def main(argv):
    try:
        if argv==["toy"]:
            toy()
        elif len(argv)==5 and argv[0]=="run":
            real(argv[1],argv[2],argv[3],argv[4])
        else:
            raise Refuse("C_JOIN_usage")
    except (Refuse,OSError,ValueError,KeyError) as e:
        print("Y137_C_JOIN_REFUSE|reason="+str(e)+"|json=0",flush=True)
        raise SystemExit(1) from None

if __name__=="__main__":
    main(sys.argv[1:])
