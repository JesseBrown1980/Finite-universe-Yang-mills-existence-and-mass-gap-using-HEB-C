#!/usr/bin/env python3
"""Fail-closed composite verification of two independent hosted Perron receipts.

Original run 44749925095 rebuilt all 45,508,080 physical S3 rows and checked
33 complete sector SHA256 hashes. Its final FIFO consumer stopped after
474,451,863 bytes in sector 374, although the immutable complete file is
800,000,000 bytes. The independent source probe verified the full file.

Re-hash the full immutable final file AND its exact FIFO-consumed prefix on
a new host. Source digest equality joins all 34 original files to the
independently checked physical rows without inventing a same-run 34/34 event.
"""
import hashlib
import pathlib
import sys
import urllib.request

ROOT_URL=("https://huggingface.co/datasets/Jessedbrown/"
          "ym-3x4-room-store/resolve/160726aaaf87386090b2b0b9ecf2815ca2634009")
MANIFEST_SHA="9213927b3b60cfbeae8efef10730e8c7df2ad52f56159017b048539377886ce3"
LAST_SHA="abc3ee22e5f736eba608bd98c93010b600f477e830fb8ce93f580ece41f2a55f"
LAST_PREFIX_SHA="2142b2efa9723611786e02100500435e333f154e1e3f50590d01cadc132fcff1"
LAST_PREFIX_BYTES=474451863
SECTOR_BYTES=800000000
N=45508080
PINNED={
    "PREFLIGHT.hbp":"3b0b4f472ff0b8d06798f6169cc9cd5d159f3fad5ad50daa1112315446140aba",
    "FULLREBUILD-SECOND-MACHINE.out":"6beb78668c5ce71915ee62dde094b995f0430ae540fbe9204ba399cf0ea360bb",
    "FULLREBUILD-SECOND-MACHINE.err":"d848d8e1d130c3f56f4f13f21db1e491bce145019f6def809f0947c962050513",
    "ORIGINAL-34-SECTORS-SHA.hbp":"7d09f5a96d43871f1f39f220a003cdd02dfb3d8fc7d398cc3c1b4976eff74f23",
    "STREAM-ORIGINAL-SHA.log":"5fd94d4ad6d383fd5d67fbb13e1c1197c42645cedcf891f0e383a4515413934a",
    "probe/RESULT-LAST-SECTOR.hbp":"74e1f4db2b4e05dec693791d3d52ab5d276c431ae6e9830e7fce402879cc1f60",
}
class Hold(Exception):
    pass

def need(condition,why):
    if not condition:raise Hold(why)

def digest(contents):
    return hashlib.sha256(contents).hexdigest()

def read_pinned(root):
    result={}
    for relative,expected in PINNED.items():
        raw=root.joinpath(*relative.split("/")).read_bytes()
        need(digest(raw)==expected,"pinned_hosted_receipt_SHA_"+relative.replace("/","_"))
        result[relative]=raw.decode("ascii")
    return result

def rec(line,tag):
    need(line.startswith(tag+"|"),"expected_exact_HBP_tag_"+tag)
    fields={}
    for entry in line.rstrip("\n").split("|")[1:]:
        key,sep,value=entry.partition("=")
        need(bool(sep) and bool(key) and key not in fields,
             "duplicate_or_bad_HBP_field")
        fields[key]=value
    need(fields.pop("json",None)=="0","HBP_json_terminator_missing")
    return fields

def one(source,tag):
    found=[line for line in source.splitlines() if line.startswith(tag+"|")]
    need(len(found)==1,"unique_receipt_"+tag)
    return rec(found[0],tag)

def parse_manifest(raw):
    need(digest(raw)==MANIFEST_SHA,"immutable_full_sector_manifest_SHA")
    result={}
    for line in raw.decode("ascii").splitlines():
        cells=line.split()
        need(len(cells)==2,"manifest_pair_row")
        sha,name=cells
        name=name.removeprefix("*").removeprefix("./")
        need(len(sha)==64 and all(ch in "0123456789abcdef" for ch in sha),
             "original_manifest_sha_format")
        need(name not in result,"duplicate_source_sector_manifest")
        result[name]=sha
    need(len(result)==34 and
         set(result)==set("sector-"+str(i)+".rooms" for i in range(341,375)),
         "all_34_original_source_files_present_in_manifest")
    need(result["sector-374.rooms"]==LAST_SHA,"original_last_sector_SHA_pin")
    return result

def validate(values,manifest):
    prep=one(values["PREFLIGHT.hbp"],"Y137_PERRON_STREAM_PREPARE")
    need(prep.get("original_sector_manifest_sha256")==MANIFEST_SHA and
         prep.get("original_passA_sha256")==
             "eefd7752031cf6e1cbfd53dd47128805d1a98bb41de0a9e269222d0e2c6e3cbc" and
         prep.get("passA_rows")==str(N) and
         prep.get("named_pipe_sectors")=="34" and
         prep.get("original_store")=="IMMUTABLE_HF_COMMIT",
         "original_passA_and_manifest_source_preflight")
    physical=one(values["FULLREBUILD-SECOND-MACHINE.out"],"FULLREBUILD")
    need(physical.get("L")=="3x4" and
         physical.get("V")=="12" and
         physical.get("n")==str(N) and
         physical.get("rows_read")==str(N) and
         physical.get("rows_rebuilt")==str(N) and
         all(physical.get(k)=="0" for k in
             ("canonical_key_mismatch","weight_mismatch","M_mismatch","entries_mismatch"))
         and physical.get("merkle")=="PASS",
         "entire_original_physical_row_rebuild_and_merkle")
    need("Exit status: 0" in values["FULLREBUILD-SECOND-MACHINE.err"],
         "original_physical_rebuilder_nonzero_exit")
    first=values["ORIGINAL-34-SECTORS-SHA.hbp"]
    stream=values["STREAM-ORIGINAL-SHA.log"]
    first_lines=[x for x in first.splitlines()
                 if x.startswith("Y137_PERRON_SECTOR_SHA|")]
    stream_lines=[x for x in stream.splitlines()
                  if x.startswith("Y137_PERRON_SECTOR_SHA|")]
    need(len(first_lines)==len(stream_lines)==33 and
         first_lines==stream_lines,"33_original_full_sector_receipts_same_run")
    for i,line in enumerate(first_lines):
        original=rec(line,"Y137_PERRON_SECTOR_SHA")
        idx=341+i
        need(original.get("sector")==str(idx) and
             original.get("bytes")==str(SECTOR_BYTES) and
             original.get("sha256")==manifest["sector-"+str(idx)+".rooms"] and
             original.get("original_manifest")=="EXACT",
             "original_full_SHA_verified_sector_"+str(idx))
    missing=one(stream,"Y137_PERRON_SECTOR_MISMATCH")
    hold=one(stream,"Y137_PERRON_STREAM_HOLD")
    need(missing.get("sector")=="374" and
         missing.get("actual_bytes")==str(LAST_PREFIX_BYTES) and
         missing.get("original_sha256")==LAST_SHA and
         missing.get("streamed_sha256")==LAST_PREFIX_SHA and
         hold.get("reason")=="immutable_original_sector_SHA_374" and
         hold.get("complete_independent_rebuild")=="HOLD",
         "known_last_FIFO_consumer_prefix_discrepancy")
    probe=one(values["probe/RESULT-LAST-SECTOR.hbp"],
              "Y137_PERRON_LAST_SOURCE_PROBE")
    need(probe.get("sector")=="374" and
         probe.get("source")=="IMMUTABLE_HF_COMMIT" and
         probe.get("http_status")=="200" and
         probe.get("content_length")==str(SECTOR_BYTES) and
         probe.get("bytes")==str(SECTOR_BYTES) and
         probe.get("original_manifest_sha256")==LAST_SHA and
         probe.get("downloaded_original_sha256")==LAST_SHA and
         probe.get("sha_match")=="TRUE",
         "standalone_same_host_complete_sector374_source_SHA")
    need(not any("all_sector_hashes=34_OF_34_PASS" in x
                 for x in stream.splitlines()),
         "refuse_false_single_run_34_stream_SHA_claim")
    return LAST_PREFIX_BYTES,LAST_PREFIX_SHA,LAST_SHA

def negative_controls(values,manifest):
    tests=[
        ("FULLREBUILD-SECOND-MACHINE.out","|merkle=PASS|","|merkle=FAIL|"),
        ("FULLREBUILD-SECOND-MACHINE.out","|rows_rebuilt=45508080|",
                                            "|rows_rebuilt=45508079|"),
        ("ORIGINAL-34-SECTORS-SHA.hbp","|sector=373|","|sector=374|"),
        ("STREAM-ORIGINAL-SHA.log","|actual_bytes=474451863|",
                                       "|actual_bytes=474451862|"),
        ("probe/RESULT-LAST-SECTOR.hbp","|sha_match=TRUE|","|sha_match=FALSE|"),
        ("PREFLIGHT.hbp","|named_pipe_sectors=34|","|named_pipe_sectors=33|"),
    ]
    for path,before,after in tests:
        need(before in values[path],"missing_negative_control_fixture")
        corrupt=dict(values)
        corrupt[path]=values[path].replace(before,after,1)
        try:validate(corrupt,manifest)
        except Hold:pass
        else:raise Hold("modified_original_Perron_certificate_accepted")
    print("Y137_PERRON_COMPOSITE_TOY|original_receipt_structure=PASS"+
          "|six_changed_sources=6_REJECTED"+
          "|same_run_34_sector_stream_verdict=NOT_CLAIMED|json=0",flush=True)

def rehash_original_last(prefix_len,expected_prefix,expected_whole):
    prefix=hashlib.sha256()
    whole=hashlib.sha256()
    count=0
    with urllib.request.urlopen(ROOT_URL+"/sector-374.rooms",timeout=120) as response:
        need(response.status==200,"original_sector_374_HTTP_status")
        need(response.headers.get("Content-Length")==str(SECTOR_BYTES),
             "original_sector_374_HTTP_complete_byte_length")
        while True:
            part=response.read(1<<20)
            if not part:break
            whole.update(part)
            if count<prefix_len:
                prefix.update(part[:max(0,prefix_len-count)])
            count+=len(part)
    need(count==SECTOR_BYTES and whole.hexdigest()==expected_whole,
         "original_frozen_complete_last_source_SHA")
    need(prefix.hexdigest()==expected_prefix,
         "original_last_source_prefix_differs_from_physical_FIFO_stream")
    return prefix.hexdigest(),whole.hexdigest()

def main(argv):
    try:
        need(len(argv)==2 and argv[0] in ("toy","real"),
             "usage_toy_or_real_ROOT")
        root=pathlib.Path(argv[1])
        values=read_pinned(root)
        with urllib.request.urlopen(ROOT_URL+"/SECTORS-341-374.sha256",
                                     timeout=120) as response:
            manifest=parse_manifest(response.read(1<<20))
        prefix_len,prefix_sha,last_sha=validate(values,manifest)
        need(len(prefix_sha)==64 and len(last_sha)==64,"original_SHA256_64hex_format")
        negative_controls(values,manifest)
        if argv[0]=="toy":return
        actual_prefix,actual_whole=rehash_original_last(
            prefix_len,prefix_sha,last_sha)
        need(actual_prefix==LAST_PREFIX_SHA and actual_whole==LAST_SHA,
             "physical_FIFO_to_immutable_complete_file_source_link")
        print("Y137_PERRON_COMPOSITE_PHYSICAL_SOURCE_ACCEPT"+
              "|independent_physical_rows=45508080_OF_45508080_PASS"+
              "|canonical_key_weight_magnetic_entries=ALL_ZERO_MISMATCH"+
              "|physical_source_merkle=PASS"+
              "|original_full_sector_stream_sha=33_OF_33_PASS"+
              "|sector374_original_complete_bytes=800000000"+
              "|sector374_original_complete_sha="+actual_whole+
              "|sector374_physical_FIFO_prefix_bytes="+str(prefix_len)+
              "|sector374_authentic_source_prefix_sha="+actual_prefix+
              "|sector374_original_prefix_match=PASS"+
              "|original_sector_files_cryptographically_authenticated=34_OF_34"+
              "|evidence_mode=COMPOSITE_TWO_HOSTED_SOURCE_JOBS"+
              "|same_run_full_34_sector_stream_SHA=NOT_CLAIMED"+
              "|original_finite_Perron_top_vector=SEPARATE_PREMISE"+
              "|first_Wilson=FORMAL_HOLD|json=0",flush=True)
    except (Hold,OSError,ValueError,UnicodeError,KeyError) as error:
        print("Y137_PERRON_COMPOSITE_HOLD|reason="+str(error)+
              "|original_first_Wilson=FORMAL_HOLD|json=0",flush=True)
        raise SystemExit(2) from None

if __name__=="__main__":
    main(sys.argv[1:])
