#!/usr/bin/env python3
"""Independent exact aggregation of 8 real accepted-K3 full-Q mu1 shards.

Acceptance requires all source rows, immutable G0 pins, exact 8x8 symmetry,
and all 255 principal minors for the whole-Q spectral localizers.
No degree-seven Schur center or Wilson conclusion is made from mu0/mu1.
"""
import hashlib
import os
import sys
from itertools import combinations

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
CACHE=os.path.join(ROOT,"independent","y137-shell4-diagonal-cache-20261114",
                   "RESULT-MAGNETIC-CACHE.hbp")
SOURCE_BLOB="6454216973b8e59d65174c7cadc4f22c7dcf0354"
Z=(69909875505,69949729820)
SAMPLES=2
N=8


def require(ok,why):
    if not ok:
        print("Y137_MU1_ASSEMBLE_REFUSE|reason="+why+"|json=0",flush=True)
        raise SystemExit(1)


def emit(name,**fields):
    print(name+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())+
          "|json=0",flush=True)


def gitblob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+bytes((0,))+data).hexdigest()


def parse(lines):
    out=[]
    for line in lines:
        if not line or not line.startswith("Y137_MU1_"):
            continue
        parts=line.split("|")
        d={}
        for k in parts[1:]:
            require("=" in k,"malformed_row")
            a,b=k.split("=",1)
            require(a not in d,"duplicate_field")
            d[a]=b
        out.append((parts[0],d))
    return out


def matrix(raw):
    a=[[int(x) for x in row.split(",")] for row in raw.split(";")]
    require(len(a)==8 and all(len(row)==8 for row in a),"not_eight_by_eight")
    return a


def encode(a):
    return ";".join(",".join(str(x) for x in row) for row in a)


def sha(a):
    return hashlib.sha256("|".join(str(x) for r in a for x in r)
                          .encode("ascii")).hexdigest()


def plus(a,b):
    return [[a[i][j]+b[i][j] for j in range(8)] for i in range(8)]


def scale(a,n):
    return [[n*x for x in row] for row in a]


def sub(a,b):
    return [[a[i][j]-b[i][j] for j in range(8)] for i in range(8)]


def determinant(a):
    n=len(a)
    if n==0:
        return 1
    m=[row[:] for row in a]
    sign=1
    pprev=1
    for k in range(n-1):
        if m[k][k]==0:
            j=next((j for j in range(k+1,n) if m[j][k]),None)
            if j is None:
                return 0
            m[j],m[k]=m[k],m[j]
            sign=-sign
        pivot=m[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                raw=pivot*m[i][j]-m[i][k]*m[k][j]
                require(raw%pprev==0,"nonexact_Bareiss")
                m[i][j]=raw//pprev
        for i in range(k+1,n):
            m[i][k]=0
        pprev=pivot
    return sign*m[-1][-1]


def psd(a):
    require(all(a[i][j]==a[j][i] for i in range(8)
                 for j in range(8)),"nonsymmetric_localizer")
    for num in range(1,9):
        for idx in combinations(range(8),num):
            if determinant([[a[i][j] for j in idx] for i in idx])<0:
                return False
    return True


def read_source():
    data=open(CACHE,"rb").read()
    require(gitblob(data)==SOURCE_BLOB,"accepted_source_G_blob_changed")
    lines=data.decode("utf-8").splitlines()
    rs=[line for line in lines if line.startswith("Y137_CACHE_POINT|")]
    require(len(rs)==2,"source_sample_count")
    def fields(line):
        return dict(p.split("=",1) for p in line.split("|")[1:])
    return [fields(line) for line in rs]


def load_one(root,idx):
    path=os.path.join(root,"PART-"+str(idx)+".hbp")
    require(os.path.isfile(path),"missing_shard_"+str(idx))
    data=parse(open(path,encoding="utf-8").read().splitlines())
    header=[x[1] for x in data if x[0]=="Y137_MU1_SHARD"]
    parts=[x[1] for x in data if x[0]=="Y137_MU1_PART"]
    inner=[x[1] for x in data if x[0]=="Y137_MU1_INNER"]
    verdict=[x[1] for x in data if x[0]=="Y137_MU1_VERDICT"]
    require(len(header)==len(verdict)==1 and len(parts)==2 and
            len(inner)==(2 if idx==0 else 0),"shard_receipt_shape")
    h=header[0]
    require(int(h["shard"])==idx and int(h["shards"])==N and
            h["all_72_moves_per_row"]=="PASS" and
            int(h["complete_raw_moves"])==72*int(h["rows"]) and
            int(h["start"])==(1985218*idx)//N and
            int(h["stop"])==(1985218*(idx+1))//N,
            "missing_or_wrong_shard_rows")
    require(verdict[0]["real_mu1_certified"]=="NOT_UNTIL_ALL_SHARDS" and
            verdict[0]["actual_Wilson_weight"]=="HOLD",
            "bad_source_scope")
    return h,parts,inner


def main():
    root=os.environ.get("Y137_MU1_PART_DIR",
                        os.path.join(ROOT,"build","y137-all-mu1-parts"))
    source=read_source()
    allshards=[load_one(root,i) for i in range(N)]
    require(sum(int(t[0]["rows"]) for t in allshards)==1985218,
            "total_shell4_source_census")
    emit("Y137_MU1_COMPLETE_FREEZE",fullQ_model="3x4_periodic_S3_r9",
         real_accepted_K3_source=1,samples=2,shards=N,
         checked_shell4_states=1985218,
         total_raw_outgoing_moves=1985218*72,
         source_G_git_blob=SOURCE_BLOB,
         independent_second_transition_builder="PENDING")
    for si,z in enumerate(Z):
        ref=source[si]
        require(int(ref["sample_num"])==z,"source_frozen_energy")
        rawG=matrix(ref["G0"])
        require(sha(rawG)==ref["G_sha256"],"accepted_source_G_matrix")
        total0=[[0]*8 for _ in range(8)]
        total1=[[0]*8 for _ in range(8)]
        for i,(header,parts,inner) in enumerate(allshards):
            row=parts[si]
            require(int(row["shard"])==i and
                    int(row["sample_num"])==z and
                    row["source_U_sha256"]==ref["U_sha256"] and
                    row["source_G_sha256"]==ref["G_sha256"],
                    "shard_frozen_source_mismatch")
            total0=plus(total0,matrix(row["complete_Q4_mu0_six"]))
            total1=plus(total1,matrix(row["complete_Q4_mu1_six"]))
            if i==0:
                rin=inner[si]
                require(int(rin["sample_num"])==z,"inner_sample_wrong")
                total0=plus(total0,matrix(rin["complete_K3_mu0_six"]))
                total1=plus(total1,matrix(rin["complete_K3_mu1_six"]))
        require(total0==rawG,"all_8_shards_mu0_does_not_equal_original_G")
        require(all(total1[i][j]==total1[j][i]
                    for i in range(8) for j in range(8)),
                "mu1_not_W_adjoint")
        g=94068200000-z
        h=468000000000-z
        require(g>0 and h>g,"wrong_global_A_Q_bounds")
        require(psd(sub(total1,scale(total0,g))) and
                psd(sub(scale(total0,h),total1)),
                "wholeQ_mu1_spectral_localizer_PSD")
        require(all(x%6==0 for row in total1 for x in row),
                "mu1_W_metric_divisibility")
        m0=[[x//6 for x in row] for row in total0]
        m1=[[x//6 for x in row] for row in total1]
        emit("Y137_MU1_COMPLETE_POINT",sample_num=z,den=1000000000,
             wholeQ_mu0_sha256=sha(m0),
             wholeQ_mu1_sha256=sha(m1),
             exact_mu1_8x8=encode(m1),
             weighted_mu0_exact_match=1,
             wholeQ_lower_and_upper_255_PSD=1,
             complete_shell5_electric_destinations_counted=1,
             real_Wilson_weight="HOLD")
    emit("Y137_MU1_COMPLETE_VERDICT",
         real_K3_exact_moment_orders="0,1",
         real_K3_degree7_remaining_per_sample=12,
         fullQ_mu1_source="ALL_8_SHARDS_REQUIRED",
         independent_transition_source="PENDING",
         actual_Schur_center="NOT_COMPUTED",
         actual_Wilson_weight="HOLD",issue_137="OPEN")


if __name__=="__main__":
    main()
