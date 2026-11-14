#!/usr/bin/env python3
"""Compute actual 3x4 full-Q accepted-K3 8x8 mu_0 at both frozen energies.

The complete K3+shell4 residual Gram was measured against all 1,985,218
shell4 targets in accepted source; G0 = 6*(R*W R).
This file does not claim that higher moments or degree7 are complete.
"""
import hashlib
import os
from itertools import combinations

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
CACHE=os.path.join(ROOT,"independent","y137-shell4-diagonal-cache-20261114",
                   "RESULT-MAGNETIC-CACHE.hbp")
FREEZE=os.path.join(ROOT,"independent","y137-shell4-diagonal-cache-20261114",
                    "PREDICTION.hbp")
SRC=os.path.join(ROOT,"independent","y137-shell4-diagonal-cache-20261114",
                 "source_cache.py")
SOURCE=os.path.join(ROOT,"independent","finite_s3_3x4_r9_first_gap.py")

GIT_CACHE="6454216973b8e59d65174c7cadc4f22c7dcf0354"
GIT_SRC="42cea9b111330d948ca40ef34185e0785e63aa3c"
GIT_MODEL="91bd1e80cbfcfb76198966aa177d097ecfbe8143"
SAMPLES=(69909875505,69949729820)
U_SHA=("0752df3c1941c67316cc6834795182fdaccdaba0ca5fc711221e7217d0dbaa1c",
       "9229dfad058157d80287cb1ab188c1034bdbb16394dec045b540890d8bb05109")
G_SHA=("83efba692ef3a8451a68049ee996451877ac4d646ae2f357fc0b604b48db0b0f",
       "e42df65b4b269095177fc609d06b4576917901c598f8ebd477eaa58b61b90d8d")
B=1000000000
QFLOOR=94068200000
HMAX=468000000000
REQUIRED_MOMENTS_DEG7=14


def need(ok,reason):
    if not ok:
        print("Y137_REAL_MOMENT_REFUSE|reason="+reason+"|json=0",flush=True)
        raise SystemExit(1)


def emit(label,**fields):
    print(label+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())+
          "|json=0",flush=True)


def blob(path):
    raw=open(path,"rb").read()
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+bytes((0,))+raw).hexdigest()


def parse_rows(raw):
    rows=[]
    for line in raw.decode("utf-8").splitlines():
        if not line:
            continue
        parts=line.split("|")
        fields={}
        for part in parts[1:]:
            need("=" in part,"bad_cache_field")
            k,v=part.split("=",1)
            need(k not in fields,"duplicated_cache_field")
            fields[k]=v
        rows.append((parts[0],fields))
    return rows


def matrix(raw):
    a=[[int(x) for x in row.split(",")] for row in raw.split(";")]
    need(len(a)==8 and all(len(row)==8 for row in a),"matrix_shape")
    need(all(a[i][j]==a[j][i] for i in range(8) for j in range(8)),
         "matrix_symmetry")
    return a


def encode(a):
    return ";".join(",".join(str(x) for x in row) for row in a)


def sha(a):
    return hashlib.sha256("|".join(str(x) for row in a
                                   for x in row).encode("ascii")).hexdigest()


def det(a):
    n=len(a)
    if not n:
        return 1
    r=[row[:] for row in a]
    sign=1
    last=1
    for k in range(n-1):
        if r[k][k]==0:
            pivot=next((j for j in range(k+1,n) if r[j][k]!=0),None)
            if pivot is None:
                return 0
            r[k],r[pivot]=r[pivot],r[k]
            sign=-sign
        p=r[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                num=r[i][j]*p-r[i][k]*r[k][j]
                need(num%last==0,"exact_Bareiss")
                r[i][j]=num//last
        for i in range(k+1,n):
            r[i][k]=0
        last=p
    return sign*r[-1][-1]


def psd(a):
    for size in range(1,9):
        for ix in combinations(range(8),size):
            if det([[a[i][j] for j in ix] for i in ix])<0:
                return False
    return True


def plus(a,b):
    return [[a[i][j]+b[i][j] for j in range(8)] for i in range(8)]


def minus(a,b):
    return [[a[i][j]-b[i][j] for j in range(8)] for i in range(8)]


def scale(a,n):
    return [[n*x for x in row] for row in a]


def main():
    need(blob(CACHE)==GIT_CACHE and blob(SRC)==GIT_SRC and
         blob(SOURCE)==GIT_MODEL,"immutable_3x4_source_blobs")
    data=parse_rows(open(CACHE,"rb").read())
    need([x[0] for x in data]==["Y137_CACHE_FREEZE","Y137_CACHE_SHELL4",
                               "Y137_CACHE_POINT","Y137_CACHE_POINT",
                               "Y137_CACHE_VERDICT"],"receipt_shape")
    shell=data[1][1]
    need(int(shell["orbits"])==1985218 and
         int(shell["maximum_m"])==16,"full_shell4_source")
    need(data[-1][1]["independent_second_seat_Gram_review"]=="PENDING",
         "source_second_seat_provenance_changed")
    emit("Y137_REAL_MOMENT_FREEZE",model="3x4_periodic_S3_r9",
         source="ACCEPTED_K3_20_JACOBI_TRIAL",
         source_Gram_git_blob=GIT_CACHE,
         K3_Q_states=155378,shell4_target_states=1985218,
         whole_Q_orbit_states=2177317865,
         required_moments_per_sample=REQUIRED_MOMENTS_DEG7,
         first_Wilson_weight="HOLD")
    for index in range(2):
        fields=data[2+index][1]
        need(int(fields["sample_num"])==SAMPLES[index] and
             fields["U_sha256"]==U_SHA[index] and
             fields["G_sha256"]==G_SHA[index],"frozen_sample_source_pin")
        U=matrix(fields["U0"])
        G=matrix(fields["G0"])
        need(sha(U)==U_SHA[index] and sha(G)==G_SHA[index],
             "original_source_matrix_hash")
        grouped={}
        for entry in fields["shell4_magnetic_gram"].split("~"):
            label,contents=entry.split(":",1)
            mm=int(label)
            need(4<=mm<=16 and mm not in grouped,"magnetic_bucket_schema")
            grouped[mm]=matrix(contents)
        need(16 in grouped and len(grouped)>=5,"outer_bucket_census")
        outer=scale(G,0)
        for gm in grouped.values():
            need(psd(gm),"source_shell4_magnetic_PSD")
            outer=plus(outer,gm)
        inner=minus(G,outer)
        need(psd(inner) and psd(outer),"Q_inner_outer_PSD")
        need(all(x%6==0 for row in G for x in row),
             "source_W_Gram_divisibility")
        mu0=[[x//6 for x in row] for row in G]
        need(psd(mu0),"actual_full_Q_mu0_PSD")
        # Exact conditional global spectral interval gives rigorous
        # nontrivial 8x8 enclosures for the still-unknown mu1.
        z=SAMPLES[index]
        g=QFLOOR-z
        h=HMAX-z
        need(g>0 and h>g,"wholeQ_spectral_interval")
        lower=scale(mu0,g)
        upper=scale(mu0,h)
        need(psd(lower) and psd(upper) and
             psd(minus(upper,lower)),"mu1_Loewner_bracket_PSD")
        emit("Y137_REAL_MOMENT_POINT",sample_num=z,den=B,
             moment_order=0,
             complete_Q_residual="K3_PLUS_ALL_SHELL4",
             exact_mu0_8x8=encode(mu0),
             exact_mu0_sha256=sha(mu0),
             source_U_sha256=U_SHA[index],source_G_sha256=G_SHA[index],
             fullQ_mu1_lower_num=g,fullQ_mu1_upper_num=h,
             fullQ_mu1_enclosure="LOEWNER_MULTIPLES_OF_MU0",
             mu1_exact="NOT_COMPUTED",
             all_255_mu0_PSD=1,
             shell4_grouped_source_moments="REPLAYED_FROM_PINNED_SOURCE",
             additional_fullQ_A_passes=0,
             first_Wilson_weight="HOLD")
    emit("Y137_REAL_MOMENT_VERDICT",actual_accepted_K3_8x8_moment0_samples=2,
         actual_accepted_K3_highest_exact_moment_order=0,
         actual_K3_degree7_moments_remaining_per_sample=13,
         fullQ_operator_moment_passes_completed=0,
         independent_transition_source_check="PENDING",
         actual_degree7_Schur_center="HOLD",
         actual_Wilson_weight="HOLD",issue_137="OPEN")


if __name__=="__main__":
    main()
