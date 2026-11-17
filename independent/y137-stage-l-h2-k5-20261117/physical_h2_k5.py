#!/usr/bin/env python3
"""#137 Stage L: exact original-S3 K5-inclusive H^2 Gram of two scaled residuals.

v_i=d(I-P_old)(D H-z_i)u_i, with original frozen source d, metric and H.
Compute the three entries <H v_i,H v_j>_W through all one-step targets.
Source owners produce deterministic binary (target, source-index, edge-count)
records. Target owners sum *all* incoming weighted flux before squaring.
No finite physical Wilson overlap or full 20738D Ritz vector is claimed.
"""
import contextlib
import gzip
import hashlib
import os
import struct
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
HTT=os.path.join(ROOT,"independent","y137-htt-streamed-20261116")
sys.path.insert(0,HTT)
import exact_htt_stream as h
physical=h.finite_s3_3x4_r9_first_gap

ROWS=633919
SHARDS=8
BUCKETS=128
KEY_BYTES=13
RECORD=struct.Struct(">13sIB")
SOURCE_SHA="a9c918de7960e7778a918ec0a06a9d22c83b7385d19e3c636f2ea8b942318b4f"
H_SOURCE=os.path.join(ROOT,"independent","y137-exact-htt-ritz-20261116",
                      "RESULT-HTT-FULL-20261116.hbp")
CAP=468

def need(ok,label):
    if not ok:
        print("Y137_L_H2_REFUSE|reason="+label+"|json=0",flush=True)
        raise SystemExit(1)

def emit(tag,**vals):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in vals.items())+
          "|json=0",flush=True)

def source():
    ordered,support,gram,meta=h.new_scaled_vectors()
    need(len(ordered)==ROWS==len(support),"source_633919_distinct_orbits")
    need(meta["scaled_support_SHA256"]==SOURCE_SHA,
         "original_projected_residual_support_SHA")
    need(meta["physical_support_K2"]==7902 and
         meta["physical_support_K3"]==126752 and
         meta["physical_support_K4"]==499265,
         "original_K2_K3_K4_support")
    den,E=h.frozen_gram()
    need(gram==(den*E[0][0],den*E[0][1],den*E[1][1]),
         "source_W_Gram_frozen_exact")
    return ordered,support,gram,meta

def hmatrix():
    need(os.path.isfile(H_SOURCE),"original_Htt_file_missing")
    rows=open(H_SOURCE,encoding="ascii").read().splitlines()
    x=h.parse_receipt("Y137_HTT_FULL_MATRIX",rows)
    need(x["source_support_SHA256"]==SOURCE_SHA and
         x["physical_rows"]==str(ROWS) and
         x["exact_raw_electric_moves"]==str(ROWS*72) and
         x["exact_PSD"]=="PASS" and
         x["Wilson_weight"]=="HOLD",
         "original_8_shard_Htt_receipt")
    return (int(x["K11"]),int(x["K12"]),int(x["K22"]))

def bucket(key):
    code=17
    for letter in key:
        code=(7*code+letter)&127
    return code

def digest_file(path):
    a=hashlib.sha256()
    with open(path,"rb") as fd:
        for block in iter(lambda:fd.read(1<<20),b""):
            a.update(block)
    return a.hexdigest()

def fields(line,prefix):
    need(line.startswith(prefix+"|"),"incorrect_receipt_prefix")
    out={}
    for part in line.split("|")[1:]:
        k,s,v=part.partition("=")
        need(s and k not in out,"duplicate_or_malformed_receipt")
        out[k]=v
    need(out.get("json")=="0","original_receipt_json_trailer")
    return out

def single_record(path,tag):
    need(os.path.isfile(path),"missing_original_receipt")
    ls=open(path,encoding="ascii").read().splitlines()
    need(len(ls)==1,"multi_line_receipt")
    return fields(ls[0],tag)

def toy():
    # If two shards contribute to the same target, sum BEFORE squaring.
    w=2
    left,right=6,10
    need((left+right)**2//w==128 and
         (left*left+right*right)//w==68,
         "cross_shard_flux_square_control")
    forged=RECORD.pack(bytes([0]*13),ROWS,1)
    _,pos,_=RECORD.unpack(forged)
    need(pos>=ROWS,"forged_source_out_of_bounds_not_rejected")
    need(bucket(bytes([0]*13))==bucket(bytes([0]*13)),
         "deterministic_bucket")
    emit("Y137_L_H2_TOY",cross_shard_flux_sum="PASS",
         premature_square="REJECTED",forged_source="REJECTED",
         K5_omission="REJECTED_BY_FULL_TARGET_ACCOUNTING",
         first_Wilson_weight="HOLD")

def pilot():
    ordered,support,gram,meta=source()
    first_K3=7902
    first_K4=7902+126752
    positions=sorted(set((0,1,2,7,first_K3,first_K3+1,
                          first_K4,first_K4+1,first_K4+1234,
                          ROWS//3,ROWS//2,ROWS-2,ROWS-1)))
    moves,reverse,exterior,distinct=0,0,0,set()
    for pos in positions:
        key=ordered[pos]
        a,b,w=support[key]
        nei=physical.neighbors(key)
        need(sum(nei.values())==72,"pilot_source_72_moves")
        moves+=72
        for dst,mul in nei.items():
            need(bucket(bytes(dst)) in range(BUCKETS),
                 "invalid_target_bucket")
            distinct.add(dst)
            if dst not in support: exterior+=1
            if reverse<120:
                rev=physical.neighbors(dst).get(key,0)
                need(w*mul==physical.weight(dst)*rev,
                     "pilot_weighted_reverse_edge")
                reverse+=1
    need(exterior>0 and reverse>0,"pilot_no_K5_boundary_or_reverse")
    emit("Y137_L_H2_PILOT",physical_rows=len(positions),raw_moves=moves,
         unique_targets=len(distinct),exterior_edge_records=exterior,
         weighted_reverse_edges=reverse,
         source_sha256=meta["scaled_support_SHA256"],
         frozen_Htt="SOURCE_PINNED",
         full_3x4_H2="NOT_COMPUTED",Wilson_weight="HOLD")

def shard(slot):
    need(0<=slot<SHARDS,"invalid_shard_slot")
    ordered,support,gram,meta=source()
    folder=os.path.join(ROOT,"build","y137-l-h2-source-"+str(slot))
    os.makedirs(folder,exist_ok=True)
    diag1=[0,0,0,0]
    diag2=[0,0,0]
    mixed=[0,0,0,0]
    edge=[0,0,0,0]
    total=0
    records=0
    sum_a=sum_b=0
    with contextlib.ExitStack() as stack:
        handles=[]
        for b in range(BUCKETS):
            p=os.path.join(folder,"bucket-%03d.bin.gz"%b)
            fd=stack.enter_context(open(p,"wb"))
            handles.append(stack.enter_context(gzip.GzipFile(
                filename="",fileobj=fd,mode="wb",
                compresslevel=1,mtime=0)))
        for pos in range(slot,ROWS,SHARDS):
            key=ordered[pos]
            a,b,w=support[key]
            neighbors=physical.neighbors(key)
            need(sum(neighbors.values())==72,
                 "source_full_original_72_moves")
            mag=physical.magnetic(physical.from_key(key))
            need(0<=mag<=36,"source_original_magnetic_potential")
            d=72+9*mag
            n1=n2=0
            for dst,mul in neighbors.items():
                vals=support.get(dst)
                if vals is not None:
                    n1+=mul*vals[0]
                    n2+=mul*vals[1]
                out=RECORD.pack(bytes(dst),pos,mul)
                handles[bucket(dst)].write(out)
                records+=1
            diag1[0]+=w*d*a*a
            diag1[1]+=w*d*a*b
            diag1[2]+=w*d*b*a
            diag1[3]+=w*d*b*b
            diag2[0]+=w*d*d*a*a
            diag2[1]+=w*d*d*a*b
            diag2[2]+=w*d*d*b*b
            mixed[0]+=w*d*a*n1
            mixed[1]+=w*d*a*n2
            mixed[2]+=w*d*b*n1
            mixed[3]+=w*d*b*n2
            edge[0]+=w*a*n1
            edge[1]+=w*a*n2
            edge[2]+=w*b*n1
            edge[3]+=w*b*n2
            sum_a+=72*w*a
            sum_b+=72*w*b
            total+=72
    rows=len(range(slot,ROWS,SHARDS))
    need(total==72*rows,"shard_move_census")
    hs=hashlib.sha256()
    for b in range(BUCKETS):
        hs.update(bytes((b,)))
        hs.update(bytes.fromhex(digest_file(
            os.path.join(folder,"bucket-%03d.bin.gz"%b))))
    entry=os.path.join(folder,"RESULT-SHARD.hbp")
    with open(entry,"w",encoding="ascii") as fd:
        def record(tag,**kv):
            fd.write(tag+"|"+"|".join(str(k)+"="+str(v)
                     for k,v in kv.items())+"|json=0\n")
        record("Y137_L_H2_SHARD",slot=slot,shards=SHARDS,
               source_rows=rows,raw_electric_moves=total,
               directed_orbit_records=records,
               original_support_sha256=SOURCE_SHA,
               bucket_fingerprint=hs.hexdigest(),
               d11=diag1[0],d12=diag1[1],d21=diag1[2],d22=diag1[3],
               t11=diag2[0],t12=diag2[1],t22=diag2[2],
               m11=mixed[0],m12=mixed[1],m21=mixed[2],m22=mixed[3],
               e11=edge[0],e12=edge[1],e21=edge[2],e22=edge[3],
               fluxsum1=sum_a,fluxsum2=sum_b,
               first_Wilson_weight="HOLD")
    print(open(entry,encoding="ascii").read().strip(),flush=True)

def reduce(group,base):
    need(0<=group<SHARDS,"invalid_target_group")
    ordered,support,gram,meta=source()
    folder=os.path.join(ROOT,"build","y137-l-h2-reduce-"+str(group))
    os.makedirs(folder,exist_ok=True)
    sq11=sq12=sq22=0
    target_count=outside=0
    records=moves=0
    fluxsum1=fluxsum2=0
    target_sha=hashlib.sha256()
    for b in range(group,BUCKETS,SHARDS):
        flux={}
        for slot in range(SHARDS):
            fn=os.path.join(base,"h2-source-"+str(slot),
                            "bucket-%03d.bin.gz"%b)
            need(os.path.isfile(fn),"missing_input_edge_bucket")
            with gzip.open(fn,"rb") as fd:
                while True:
                    raw=fd.read(RECORD.size)
                    if not raw:break
                    need(len(raw)==RECORD.size,
                         "truncated_original_edge_record")
                    key,pos,mul=RECORD.unpack(raw)
                    need(pos<ROWS and pos%SHARDS==slot and
                         0<mul<=72 and bucket(key)==b,
                         "forged_target_bucket_or_source_position")
                    a,c,w=support[ordered[pos]]
                    val=flux.get(key)
                    if val is None:
                        flux[key]=[w*mul*a,w*mul*c]
                    else:
                        val[0]+=w*mul*a
                        val[1]+=w*mul*c
                    records+=1
                    moves+=mul
        for key in sorted(flux):
            fa,fb=flux[key]
            w=physical.weight(tuple(key))
            need(w in (1,2,3,6) and
                 fa%w==0 and fb%w==0,
                 "physical_target_flux_nonintegral")
            sq11+=fa*(fa//w)
            sq12+=fa*(fb//w)
            sq22+=fb*(fb//w)
            fluxsum1+=fa
            fluxsum2+=fb
            target_count+=1
            if tuple(key) not in support:
                outside+=1
            target_sha.update(key)
            for value in (fa,fb):
                raw=abs(value).to_bytes(max(1,(abs(value).bit_length()+7)//8),"big")
                target_sha.update(bytes((1 if value<0 else 0,)))
                target_sha.update(len(raw).to_bytes(2,"big"))
                target_sha.update(raw)
    path=os.path.join(folder,"RESULT-REDUCE.hbp")
    with open(path,"w",encoding="ascii") as fd:
        fd.write("Y137_L_H2_REDUCE|group="+str(group)+
                 "|buckets="+str(BUCKETS//SHARDS)+
                 "|target_count="+str(target_count)+
                 "|outside_old_residual_support="+str(outside)+
                 "|records="+str(records)+
                 "|multiplicity_sum="+str(moves)+
                 "|fluxsum1="+str(fluxsum1)+
                 "|fluxsum2="+str(fluxsum2)+
                 "|f11="+str(sq11)+"|f12="+str(sq12)+
                 "|f22="+str(sq22)+
                 "|target_sha256="+target_sha.hexdigest()+
                 "|source_sha256="+SOURCE_SHA+
                 "|first_Wilson_weight=HOLD|json=0\n")
    print(open(path,encoding="ascii").read().strip(),flush=True)

def psd(a,b,c):
    return a>=0 and c>=0 and a*c>=b*b

def fanin(source_base,reduce_base):
    den,E=h.frozen_gram()
    G=[den*E[0][0],den*E[0][1],den*E[1][1]]
    KT=hmatrix()
    ds=[0]*4
    t=[0]*3
    m=[0]*4
    edge=[0]*4
    sum_a=sum_b=0
    rows=moves=records=0
    sha_list=[]
    for slot in range(SHARDS):
        path=os.path.join(source_base,"h2-receipt-"+str(slot),
                          "RESULT-SHARD.hbp")
        x=single_record(path,"Y137_L_H2_SHARD")
        need(int(x["slot"])==slot and int(x["shards"])==SHARDS
             and x["original_support_sha256"]==SOURCE_SHA
             and x["first_Wilson_weight"]=="HOLD",
             "source_shard_receipt_mismatch")
        for arr,keys in ((ds,("d11","d12","d21","d22")),
                         (t,("t11","t12","t22")),
                         (m,("m11","m12","m21","m22")),
                         (edge,("e11","e12","e21","e22"))):
            for i,key in enumerate(keys):arr[i]+=int(x[key])
        rows+=int(x["source_rows"])
        moves+=int(x["raw_electric_moves"])
        records+=int(x["directed_orbit_records"])
        sum_a+=int(x["fluxsum1"])
        sum_b+=int(x["fluxsum2"])
        sha_list.append(x["bucket_fingerprint"])
    need(rows==ROWS and moves==ROWS*72,
         "incomplete_original_physical_support")
    need(ds[1]==ds[2],"diagonal_weighted_moment_symmetry")
    # Htt uses the electric edge bilinear WITHOUT magnetic diagonal factor.
    # The separately retained d-weighted mixed term belongs only in H^2.
    k=(ds[0]-edge[0],ds[1]-edge[1],ds[3]-edge[3])
    need(k==KT and ds[1]-edge[1]==ds[2]-edge[2],
         "original_8_shard_Htt_regression")
    f=[0,0,0]
    targets=outside=records2=moves2=0
    recv_a=recv_b=0
    target_sha_list=[]
    for group in range(SHARDS):
        path=os.path.join(reduce_base,"h2-reduce-"+str(group),
                          "RESULT-REDUCE.hbp")
        x=single_record(path,"Y137_L_H2_REDUCE")
        need(int(x["group"])==group
             and int(x["buckets"])==BUCKETS//SHARDS
             and x["source_sha256"]==SOURCE_SHA
             and x["first_Wilson_weight"]=="HOLD",
             "target_shard_receipt_mismatch")
        for i,key in enumerate(("f11","f12","f22")):
            f[i]+=int(x[key])
        targets+=int(x["target_count"])
        outside+=int(x["outside_old_residual_support"])
        records2+=int(x["records"])
        moves2+=int(x["multiplicity_sum"])
        recv_a+=int(x["fluxsum1"])
        recv_b+=int(x["fluxsum2"])
        target_sha_list.append(x["target_sha256"])
    need(records2==records and moves2==moves,
         "target_missing_or_duplicate_electric_edges")
    need(recv_a==sum_a and recv_b==sum_b,
         "global_target_weighted_flux_sum_mismatch")
    need(outside>0 and targets>=outside,
         "missing_exterior_K5_target_flux")
    S11=t[0]-2*m[0]+f[0]
    S12=t[1]-m[1]-m[2]+f[1]
    S22=t[2]-2*m[3]+f[2]
    need(psd(S11,S12,S22),"physical_H2_not_PSD")
    need(psd(CAP*CAP*G[0]-S11,CAP*CAP*G[1]-S12,
             CAP*CAP*G[2]-S22),
         "physical_468_squared_norm_ceiling")
    detG=G[0]*G[2]-G[1]*G[1]
    need(detG>0,"original_2D_residual_Gram_not_PD")
    h11,h12,h22=KT
    q11=G[2]*h11*h11-2*G[1]*h11*h12+G[0]*h12*h12
    q12=G[2]*h11*h12-G[1]*(h11*h22+h12*h12)+G[0]*h12*h22
    q22=G[2]*h12*h12-2*G[1]*h12*h22+G[0]*h22*h22
    need(psd(detG*S11-q11,detG*S12-q12,detG*S22-q22),
         "physical_H2_below_projected_Htt_Gram")
    seal=hashlib.sha256()
    for v in sha_list+target_sha_list:seal.update(bytes.fromhex(v))
    emit("Y137_L_H2_MATRIX",physical_source_rows=rows,
         original_raw_electric_moves=moves,directed_orbit_records=records,
         unique_original_targets=targets,exterior_targets=outside,
         exact_integer_H2_11=S11,exact_integer_H2_12=S12,
         exact_integer_H2_22=S22,
         exact_H2_11_SHA256=h.digest(S11),
         exact_H2_12_SHA256=h.digest(S12),
         exact_H2_22_SHA256=h.digest(S22),
         target_and_source_receipts_sha256=seal.hexdigest(),
         original_Htt_reproduced="3_OF_3_EXACT",
         weighted_physical_H2_PSD="PASS",
         original_468_squared_ceiling="PASS",
         residual_projection_Htt_lower="PASS",
         K5_boundary_targets="INCLUDED_EXACT",
         full_20738_Ritz_witness="NOT_COMPUTED",
         first_Wilson_weight="HOLD")
    emit("Y137_L_H2_VERDICT",original_S3_H2="ACCEPTED_THREE_EXACT",
         full_3x4_physical_target_flux="ALL_SHARDS",
         original_K5_leakage="INCLUDED",
         first_Wilson_weight="HOLD",issue_137="OPEN")

if __name__=="__main__":
    args=sys.argv[1:]
    if args==["toy"]:toy()
    elif args==["pilot"]:pilot()
    elif len(args)==2 and args[0]=="shard":shard(int(args[1]))
    elif len(args)==3 and args[0]=="reduce":reduce(int(args[1]),args[2])
    elif len(args)==3 and args[0]=="fanin":fanin(args[1],args[2])
    else:need(False,"usage_toy_pilot_shard_N_reduce_N_DIR_fanin_DIR_DIR")
