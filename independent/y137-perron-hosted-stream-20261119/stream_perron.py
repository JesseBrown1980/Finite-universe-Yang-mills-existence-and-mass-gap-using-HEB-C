#!/usr/bin/env python3
"""Read-only independent-machine 34-sector Perron full-row streaming replay.

Streams original pinned HF full sector bytes through named pipes into the
separately written 2026-11-02 Rust fullrebuild program. Never stores all
sectors together, never edits a source, and independently SHA-authenticates
all original sector files, the manifest and the passA row/key table.
No external Python packages, no floating point, and no unpinned sources.

Usage:
  stream_perron.py toy
  stream_perron.py prepare ROOT
  stream_perron.py serve ROOT
"""
import hashlib
import os
import pathlib
import sys
import urllib.request

DATASET="https://huggingface.co/datasets/Jessedbrown/ym-3x4-room-store/resolve"
ORIGINAL_STORE=DATASET+"/160726aaaf87386090b2b0b9ecf2815ca2634009"
ORIGINAL_PERRON=DATASET+"/d2630edf882f3d9fa125f25680fd9b6a04c98d31/perron"
MANIFEST_SHA="9213927b3b60cfbeae8efef10730e8c7df2ad52f56159017b048539377886ce3"
PASSA_SHA="eefd7752031cf6e1cbfd53dd47128805d1a98bb41de0a9e269222d0e2c6e3cbc"
PASSA_BYTES=728129280
N=45508080
FIRST=341
COUNT=34
SEGMENT_BYTES=800000000
CHUNK=1<<20

class Refuse(Exception):
    pass

def need(ok,why):
    if not ok:raise Refuse(why)

def hash_hex(data):
    return hashlib.sha256(data).hexdigest()

def manifest_parse(content):
    lines=content.decode("ascii").splitlines()
    result=[]
    for row in lines:
        fields=row.split()
        need(len(fields)==2,"source_manifest_two_columns")
        sha,name=fields
        need(len(sha)==64 and all(x in "0123456789abcdef" for x in sha),
             "source_manifest_sha_hex")
        name=name.removeprefix("*").removeprefix("./")
        result.append((sha,name))
    need(len(result)==COUNT and
         sorted(result)==sorted(set(result)),
         "original_34_segment_unique_manifest")
    expected=["sector-"+str(i)+".rooms" for i in range(FIRST,FIRST+COUNT)]
    need(set(name for _,name in result)==set(expected),
         "exact_34_original_pinned_sector_names")
    return {name:sha for sha,name in result}

def load_manifest(root):
    raw=(root.joinpath("SECTORS-341-374.sha256")).read_bytes()
    need(hash_hex(raw)==MANIFEST_SHA,"original_sector_manifest_SHA_mismatch")
    return manifest_parse(raw)

def download(url,target,expected_sha,expected_bytes):
    target.parent.mkdir(parents=True,exist_ok=True)
    h=hashlib.sha256()
    size=0
    tmp=target.with_suffix(target.suffix+".part")
    try:
        with urllib.request.urlopen(url,timeout=120) as src,open(tmp,"wb") as out:
            while True:
                b=src.read(CHUNK)
                if not b:break
                out.write(b)
                h.update(b)
                size+=len(b)
        need(size==expected_bytes and h.hexdigest()==expected_sha,
             "immutable_download_byte_length_or_SHA_"+target.name)
        os.replace(tmp,target)
    finally:
        if tmp.exists():tmp.unlink()
    return h.hexdigest()

def prepare(root):
    root.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(ORIGINAL_STORE+"/SECTORS-341-374.sha256",timeout=120) as inp:
        data=inp.read(1<<20)
    need(hash_hex(data)==MANIFEST_SHA,"remote_manifest_SHA256")
    manifest_parse(data)
    (root.joinpath("SECTORS-341-374.sha256")).write_bytes(data)
    download(ORIGINAL_PERRON+"/passA.bin",root.joinpath("passA.bin"),PASSA_SHA,PASSA_BYTES)
    for i in range(FIRST,FIRST+COUNT):
        fifo=root.joinpath("sector-"+str(i)+".rooms")
        need(not fifo.exists(),"refuse_overwrite_input_sector")
        os.mkfifo(fifo,0o600)
    print("Y137_PERRON_STREAM_PREPARE|original_sector_manifest_sha256="+MANIFEST_SHA+
          "|original_passA_sha256="+PASSA_SHA+
          "|passA_rows="+str(N)+
          "|named_pipe_sectors=34|original_store=IMMUTABLE_HF_COMMIT"+
          "|original_fullrebuild=SEPARATE_SOURCE_CHECK|json=0",flush=True)

def serve(root):
    manifest=load_manifest(root)
    h=hashlib.sha256()
    with open(root.joinpath("passA.bin"),"rb") as inp:
        while True:
            b=inp.read(CHUNK)
            if not b:break
            h.update(b)
    need(h.hexdigest()==PASSA_SHA,"original_passA_prechecked")
    summary=hashlib.sha256()
    matched=0
    total=0
    record=root.joinpath("ORIGINAL-34-SECTORS-SHA.hbp")
    with open(record,"w",encoding="ascii",buffering=1) as out:
        for i in range(FIRST,FIRST+COUNT):
            name="sector-"+str(i)+".rooms"
            expected=manifest[name]
            url=ORIGINAL_STORE+"/"+name
            fifo=root.joinpath(name)
            need(fifo.is_fifo(),"missing_unmodified_source_named_pipe")
            h=hashlib.sha256()
            n=0
            pipe_broken=False
            # Open blocks until fullrebuild opens the matching sequential pipe.
            with open(fifo,"wb",buffering=0) as sink,urllib.request.urlopen(url,timeout=120) as source:
                while True:
                    b=source.read(CHUNK)
                    if not b:break
                    h.update(b)
                    n+=len(b)
                    if not pipe_broken:
                        try:
                            sink.write(b)
                        except BrokenPipeError:
                            # The last segment may have archive bytes beyond
                            # the logical merkle stream. Hash the remainder
                            # without presenting it as additional store data.
                            pipe_broken=True
            actual=h.hexdigest()
            need(actual==expected,"immutable_original_sector_SHA_"+str(i))
            need(i==FIRST+COUNT-1 or n==SEGMENT_BYTES,
                 "nonterminal_original_sector_length_"+str(i))
            matched+=1
            total+=n
            summary.update((str(i)+"|"+str(n)+"|"+actual+";").encode("ascii"))
            line=("Y137_PERRON_SECTOR_SHA|sector="+str(i)+
                  "|bytes="+str(n)+"|sha256="+actual+
                  "|original_manifest=EXACT|json=0\n")
            out.write(line)
            print(line,end="",flush=True)
        out.write("Y137_PERRON_ORIGINAL_34_SECTOR_ACCEPT|all_sector_hashes=34_OF_34_PASS"+
                  "|streamed_original_bytes="+str(total)+
                  "|fingerprint="+summary.hexdigest()+
                  "|fullrebuild_rows=VERIFY_SEPARATELY|json=0\n")
        print("Y137_PERRON_ORIGINAL_34_SECTOR_ACCEPT|all_sector_hashes=34_OF_34_PASS"+
              "|streamed_original_bytes="+str(total)+
              "|fingerprint="+summary.hexdigest()+
              "|fullrebuild_rows=VERIFY_SEPARATELY|json=0",flush=True)

def toy():
    # Structural and SHA-corruption controls are independently tested
    # without fetching any remote payload.
    example="\n".join("0"*64+"  sector-"+str(i)+".rooms"
                      for i in range(FIRST,FIRST+COUNT)).encode()
    data=manifest_parse(example)
    need(len(data)==34 and data["sector-341.rooms"]=="0"*64,
         "toy_complete_sector_manifest")
    bad=example.replace(b"sector-341.rooms",b"sector-340.rooms")
    try:manifest_parse(bad)
    except Refuse:pass
    else:raise Refuse("forged_sector_manifest_accepted")
    bad2=example.replace(b"0"*64,b"0"*63+b"g",1)
    try:manifest_parse(bad2)
    except Refuse:pass
    else:raise Refuse("malformed_manifest_sha_accepted")
    need(PASSA_BYTES==16*N and FIRST+COUNT-1==374,
         "original_Perron_passA_width_and_end_sector")
    print("Y137_PERRON_STREAM_TOY|34_manifest_entries=PASS"+
          "|original_passA_row_width=16|original_nonflat_rows=45508080"+
          "|wrong_sector_and_forged_SHA=2_REJECTED"+
          "|no_full_archive_download=PASS|fullrebuild=NOT_YET_RUN|json=0")

def main():
    try:
        need(len(sys.argv) in (2,3),"usage_toy_or_prepare_or_serve_ROOT")
        if sys.argv[1:]==["toy"]:toy()
        elif len(sys.argv)==3 and sys.argv[1]=="prepare":
            prepare(pathlib.Path(sys.argv[2]))
        elif len(sys.argv)==3 and sys.argv[1]=="serve":
            serve(pathlib.Path(sys.argv[2]))
        else:raise Refuse("usage")
    except (Refuse,OSError,UnicodeError,ValueError) as e:
        print("Y137_PERRON_STREAM_HOLD|reason="+str(e)+
              "|complete_independent_rebuild=HOLD"+
              "|first_Wilson=FORMAL_HOLD|json=0",flush=True)
        raise SystemExit(2) from None

if __name__=="__main__":main()
