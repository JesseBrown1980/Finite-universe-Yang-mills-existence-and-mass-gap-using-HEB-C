#!/usr/bin/env python3
"""Certify actual accepted-K3 whole-Q μ2 at E1/E2 from all S3 shell5 buckets.

Source shards compute Q3/Q4 values; target-keyed reducers combine Q5
before Gram squaring. The exact prior μ0/μ1 must reappear unchanged.
A 16x16 moment block-Hankel Schur test is checked in integer arithmetic.
"""
import hashlib
import os
from itertools import combinations

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
PARTS=os.environ.get("Y137_D11_MU2_PART_ROOT",
                     os.path.join(ROOT,"build","y137-d11-mu2-part-metadata"))
GROUPS=os.environ.get("Y137_D11_MU2_GROUP_ROOT",
                      os.path.join(ROOT,"build","y137-d11-mu2-group-results"))
CACHED=os.path.join(ROOT,"independent",
                    "y137-shell4-diagonal-cache-20261114",
                    "RESULT-MAGNETIC-CACHE.hbp")
OLD_MU1=os.path.join(ROOT,"independent",
                     "y137-real-Q-moment-20261114","RESULT-MU1.hbp")
CACHE_BLOB="6454216973b8e59d65174c7cadc4f22c7dcf0354"
OLD_BLOB="86abf9611f8b9df5e03e796e81f513cba826c085"
Z=(69909875505,69949729820)
SH4=1985218
N=8
B=1000000000


def need(ok,reason):
    if not ok:
        print("Y137_D11_MU2_ASSEMBLE_REFUSE|reason="+reason+"|json=0",
              flush=True)
        raise SystemExit(1)


def emit(name,**fields):
    print(name+"|"+"|".join(str(k)+"="+str(v)
                           for k,v in fields.items())+"|json=0",flush=True)


def blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+bytes((0,))+data).hexdigest()


def lines(path,sha=None):
    raw=open(path,"rb").read()
    if sha is not None:
        need(blob(raw)==sha,"immutable_source_blob")
    out=[]
    for item in raw.decode("utf-8").splitlines():
        if not item.strip():
            continue
        arr=item.split("|")
        fields={}
        for bit in arr[1:]:
            need("=" in bit,"row_field_format")
            k,v=bit.split("=",1)
            need(k not in fields,"duplicate_row_field")
            fields[k]=v
        out.append((arr[0],fields))
    return out


def pick(records,label):
    return [d for tag,d in records if tag==label]


def mat(raw):
    a=[[int(x) for x in row.split(",")] for row in raw.split(";")]
    need(len(a)==N and all(len(r)==N for r in a),"8x8_matrix_shape")
    return a


def encode(a):
    return ";".join(",".join(str(v) for v in row) for row in a)


def sha(a):
    return hashlib.sha256("|".join(str(v) for row in a for v in row)
                          .encode("ascii")).hexdigest()


def zero():
    return [[0]*N for _ in range(N)]


def add(a,b):
    return [[a[i][j]+b[i][j] for j in range(N)] for i in range(N)]


def sub(a,b):
    return [[a[i][j]-b[i][j] for j in range(N)] for i in range(N)]


def scale(a,x):
    return [[x*v for v in row] for row in a]


def mul(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(N))
             for j in range(N)] for i in range(N)]


def transpose(a):
    return [[a[j][i] for j in range(N)] for i in range(N)]


def det(a):
    n=len(a)
    if n==0:
        return 1
    need(all(len(row)==n for row in a),"determinant_shape")
    tmp=[list(r) for r in a]
    previous=1
    sign=1
    for k in range(n-1):
        if tmp[k][k]==0:
            j=next((i for i in range(k+1,n) if tmp[i][k]),None)
            if j is None:
                return 0
            tmp[k],tmp[j]=tmp[j],tmp[k]
            sign=-sign
        q=tmp[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                number=q*tmp[i][j]-tmp[i][k]*tmp[k][j]
                need(number%previous==0,"not_fraction_free_Bareiss")
                tmp[i][j]=number//previous
        for i in range(k+1,n):
            tmp[i][k]=0
        previous=q
    return sign*tmp[-1][-1]


def psd(a):
    need(all(a[i][j]==a[j][i] for i in range(N)
             for j in range(N)),"not_weighted_symmetric")
    for k in range(1,N+1):
        for ix in combinations(range(N),k):
            if det([[a[i][j] for j in ix] for i in ix])<0:
                return False
    return True


def adj(a):
    co=[[0]*N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            minor=[[a[p][q] for q in range(N) if q!=j]
                   for p in range(N) if p!=i]
            co[i][j]=det(minor) if (i+j)%2==0 else -det(minor)
    return transpose(co)


def hankel_psd(mu0,mu1,mu2):
    # 16x16 [[mu0,mu1],[mu1,mu2]] is PSD iff mu0 is PD and
    # det(mu0)*mu2 - mu1*adj(mu0)*mu1 is PSD.
    need(psd(mu0),"original_mu0_not_PSD")
    require_pd=all(det([row[:k] for row in mu0[:k]])>0
                   for k in range(1,N+1))
    need(require_pd,"mu0_not_strictly_PD_HOLD")
    d=det(mu0)
    a=adj(mu0)
    # Verify exact cofactor inverse before using it as a proof.
    product=mul(mu0,a)
    need(all(product[i][j]==(d if i==j else 0)
             for i in range(N) for j in range(N)),
         "adjugate_inverse_fault")
    schur=sub(scale(mu2,d),mul(mul(mu1,a),mu1))
    need(psd(schur),"moment_Hankel_not_PSD")
    return d


def reconstruct():
    historical=pick(lines(CACHED,CACHE_BLOB),"Y137_CACHE_POINT")
    accepted=pick(lines(OLD_MU1,OLD_BLOB),"Y137_MU1_COMPLETE_POINT")
    need(len(historical)==len(accepted)==2,"original_accepted_points")
    part=[]
    source_rows=0
    source_moves=0
    total_q5_events=0
    for s in range(N):
        path=os.path.join(PARTS,"y137-mu2-shard-"+str(s)+"-group-0",
                          "PART.hbp")
        rows=lines(path)
        headers=pick(rows,"Y137_D11_MU2_SHARD")
        points=pick(rows,"Y137_D11_MU2_PART")
        inner=pick(rows,"Y137_D11_MU2_INNER")
        verdict=pick(rows,"Y137_D11_MU2_VERDICT")
        need(len(headers)==len(verdict)==1 and len(points)==2
             and len(inner)==(2 if s==0 else 0),"source_shard_row_shape")
        h=headers[0]
        lo=SH4*s//N
        hi=SH4*(s+1)//N
        need(int(h["shard"])==s and int(h["shards"])==N and
             int(h["source_start"])==lo and
             int(h["source_stop"])==hi and
             int(h["source_rows"])==hi-lo and
             int(h["all_raw_electric_moves"])==(hi-lo)*72 and
             h["bucket_count"]=="64","source_completeness_rows")
        need(verdict[0]["actual_mu2"]==
             "HOLD_ALL_EIGHT_SHARDS_AND_GLOBAL_TARGET_REDUCTION",
             "source_shard_scope_changed")
        source_rows+=hi-lo
        source_moves+=72*(hi-lo)
        total_q5_events+=int(h["recorded_Q5_edges"])
        part.append((points,inner))
    need(source_rows==SH4 and source_moves==SH4*72,
         "missing_real_Q4_source_states")
    buckets=[]
    total_targets=0
    total_reduced_records=0
    for group in range(N):
        path=os.path.join(GROUPS,"GROUP-"+str(group)+".hbp")
        data=lines(path)
        head=pick(data,"Y137_D11_MU2_GROUP")
        points=pick(data,"Y137_D11_MU2_Q5_PART")
        verdict=pick(data,"Y137_D11_MU2_GROUP_VERDICT")
        bucket_rows=pick(data,"Y137_D11_MU2_BUCKET_PASS")
        need(len(head)==len(verdict)==1 and len(points)==2 and
             len(bucket_rows)==8,"reduced_bucket_group_structure")
        h=head[0]
        need(int(h["group"])==group and int(h["buckets"])==8 and
             int(h["source_shards"])==N and
             h["exact_target_merge_before_square"]=="PASS",
             "group_not_complete")
        need(verdict[0]["exact_Q5_reduction"]=="PASS_FOR_GROUP" and
             verdict[0]["original_Wilson_weight"]=="HOLD",
             "group_proof_scope")
        total_targets+=int(h["unique_shell5_targets"])
        total_reduced_records+=int(h["total_Q4_edge_records"])
        buckets.append(points)
    need(total_q5_events==total_reduced_records,
         "source_vs_target_bucket_event_loss")
    for si,z in enumerate(Z):
        href=historical[si]
        original=accepted[si]
        need(int(href["sample_num"])==z and
             int(original["sample_num"])==z,"original_sample_order")
        ref_mu0_6=mat(href["G0"])
        mu0=zero()
        mu1=zero()
        mu2=zero()
        for shard,(points,inner) in enumerate(part):
            p=points[si]
            need(int(p["sample_num"])==z and
                 int(p["shard"])==shard and
                 p["exact_prior_mu0_mu1_shard_match"]=="1",
                 "wrong_sample_or_original_mu1_regression")
            mu0=add(mu0,mat(p["Q4_mu0_six"]))
            mu1=add(mu1,mat(p["Q4_mu1_six"]))
            mu2=add(mu2,mat(p["Q4_mu2_six"]))
            if shard==0:
                q=inner[si]
                need(int(q["sample_num"])==z and
                     q["exact_prior_K3_mu0_mu1_match"]=="1",
                     "inner_source_changed")
                mu0=add(mu0,mat(q["K3_mu0_six"]))
                mu1=add(mu1,mat(q["K3_mu1_six"]))
                mu2=add(mu2,mat(q["K3_mu2_six"]))
        need(mu0==ref_mu0_6,"entire_prior_mu0_not_restored")
        ref_mu1=mat(original["exact_mu1_8x8"])
        need(mu1==scale(ref_mu1,6),"entire_prior_mu1_not_restored")
        for group,points in enumerate(buckets):
            p=points[si]
            need(int(p["group"])==group and
                 int(p["sample_num"])==z and
                 p["complete_bucket_groups"]=="1",
                 "partial_shell5_group")
            mu2=add(mu2,mat(p["Q5_mu2_six"]))
        need(all(x%6==0 for M in (mu0,mu1,mu2)
                 for row in M for x in row),"exact_W_six_divisibility")
        A0=[[v//6 for v in row] for row in mu0]
        A1=[[v//6 for v in row] for row in mu1]
        A2=[[v//6 for v in row] for row in mu2]
        g=94068200000-z
        h=468000000000-z
        need(g>0 and h>g,"source_conditional_interval")
        need(psd(sub(A1,scale(A0,g))) and
             psd(sub(scale(A0,h),A1)),
             "previous_moment_spectral_bounds_changed")
        need(psd(sub(A2,scale(A1,g))) and
             psd(sub(scale(A1,h),A2)),
             "mu2_first_spectral_localizer")
        need(psd(add(sub(A2,scale(A1,2*g)),scale(A0,g*g))) and
             psd(add(sub(A2,scale(A1,2*h)),scale(A0,h*h))),
             "mu2_square_spectral_localizers")
        hankeld= hankel_psd(A0,A1,A2)
        # Deliberately zeroing the new moment must be rejected by the
        # strictly positive lower energy spectral condition.
        need(not psd(sub(zero(),scale(A1,g))),
             "zero_new_moment_negative_control_not_refused")
        emit("Y137_D11_MU2_POINT",sample_num=z,den=B,
             actual_K3_mu0_sha256=sha(A0),
             actual_K3_mu1_sha256=sha(A1),
             actual_K3_mu2_sha256=sha(A2),
             actual_K3_mu2_8x8=encode(A2),
             exact_all_Q3_Q4_Q5_present=1,
             original_mu0_mu1_byte_reproduced=1,
             spectral_8x8_localizers="PASS",
             block_Hankel_16x16_via_adjugate="PASS",
             positive_mu0_determinant_digits=len(str(hankeld)),
             planted_zero_mu2="REJECTED",
             first_Wilson_weight="HOLD")
    emit("Y137_D11_MU2_VERDICT",full_Q4_sources=source_rows,
         full_Q4_raw_moves=source_moves,
         shell5_raw_edge_records=total_q5_events,
         unique_shell5_target_states=total_targets,
         exact_real_K3_moments_per_sample=3,
         exact_moment_orders="0,1,2",
         degree11_remaining_moments_per_sample=19,
         degree11_source_passes="ONE_COMPLETE_OF_ELEVEN",
         independent_second_seat_raw_source="PENDING",
         degree11_corrected_Schur="NOT_COMPUTED",
         original_first_Wilson_weight="HOLD",
         issue_137="OPEN")


def selftest():
    I=[[int(i==j) for j in range(N)] for i in range(N)]
    mu0=I
    mu1=scale(I,2)
    mu2=scale(I,4)
    need(hankel_psd(mu0,mu1,mu2)==1,
         "synthetic_matrix_Hankel")
    need(psd(sub(mu2,mu1)) and
         psd(sub(scale(mu1,4),mu2)),
         "synthetic_upper_lower_localizers")
    need(not psd(sub(zero(),mu1)),
         "synthetic_zero_second_moment_control")
    need(encode(I)==
         ";".join(",".join(str(int(i==j)) for j in range(N))
                  for i in range(N)),
         "independent_8x8_source_serialization")
    emit("Y137_D11_MU2_ASSEMBLER_TOY",
         exact_Bareiss_and_adjugate="PASS",
         full_16x16_block_Hankel="PASS",
         invalid_mu2_zero="REJECTED",
         real_source_moments="NOT_COMPUTED")


if __name__=="__main__":
    import sys
    if len(sys.argv)==2 and sys.argv[1]=="--self-test":
        selftest()
    elif len(sys.argv)==1:
        reconstruct()
    else:
        need(False,"invalid_mode")
