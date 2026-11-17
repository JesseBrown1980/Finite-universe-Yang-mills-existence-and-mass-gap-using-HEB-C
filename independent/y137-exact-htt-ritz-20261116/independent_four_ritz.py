#!/usr/bin/env python3
"""Y137: independent two-route, exact integer 4-vector generalized Ritz.

Consumes source-frozen 8-shard exact physical H_tt receipt and original
PR249 2-residual Gram / old source 2x2 matrices. Represents
span{u1,u2,t1,t2} (FOUR vectors) as a subspace of authenticated 20,738D:
  u Gram=G, u H=K; t=(I-P_old)(D H-z_seed)u; E=den*Gram(t).
Take physical v=den*t, thus Gram(v)=den*E, H(v)=computed H_tt,
and D*<u,Hv>=E. The integer energy-numerator pencil is:
 [ D K-zG,                 E                  ]
 [ E,      D H_tt - z*den*E                  ].
Two independent inertia routes:
 (i) pivoted full 4x4 Bareiss leading principal minors, with all 24
     symmetric permutations available for zero minor detection;
 (ii) 2x2 Schur complement eliminating the EXACT positive lower block
     throughout 0<=z<=72D, proved by its exact positivity at 72D.
Exact bisection yields two consecutive 10^-9 Ritz brackets. These are
precise eigenvalues of the FOUR-dimensional projected pencil; only their
upper endpoints bound the first two full 20,738D Ritz values.

NO claim of full physical eigenstate distance or Wilson spectral weight.
"""
import hashlib
import itertools
import os
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
D=1000000000
UPPER_Z=72*D
SOURCE_H20738=os.path.join(ROOT,"independent",
    "y137-two-residual-krylov-20261116",
    "RESULT-TWO-RESIDUAL-AND-FOUR-ENVELOPE-20261116.hbp")
SOURCE_HTT=os.path.join(HERE,"RESULT-HTT-FULL-20261116.hbp")
ORIGINAL_RANK2_GITBLOB="90f9c002f6fe8df2ecd4b5e725de3f9153fbab10"
ORIGINAL_S3_GITBLOB="91bd1e80cbfcfb76198966aa177d097ecfbe8143"
EXPECTED_RITZ=((69913037769,69913037770),
               (69952639134,69952639135))
OLD_UPPER=(69919854414,69959079472)


def need(ok,reason):
    if not ok:
        print("Y137_HTT_RITZ_REFUSE|reason="+reason+"|json=0",
              flush=True)
        raise SystemExit(1)


def gitblob(path):
    raw=open(path,"rb").read()
    return hashlib.sha1(
        b"blob "+str(len(raw)).encode("ascii")+b"\x00"+raw).hexdigest()


def digest(v):
    return hashlib.sha256(str(v).encode("ascii")).hexdigest()


def emit(label,**kw):
    print(label+"|"+"|".join(str(k)+"="+str(v)
          for k,v in kw.items())+"|json=0",flush=True)


def parse(path,label):
    text=open(path,encoding="ascii").read().splitlines()
    rows=[x for x in text if x.startswith(label+"|")]
    need(len(rows)==1,"missing_or_duplicate_"+label)
    fields={}
    for item in rows[0].split("|")[1:]:
        k,sep,v=item.partition("=")
        need(sep and k not in fields,
             "duplicate_or_invalid_source_field")
        fields[k]=v
    need(fields.get("json")=="0","bad_original_receipt_trailer")
    return fields


def determinant(a):
    n=len(a)
    need(n>0 and all(len(row)==n for row in a),
         "bad_square_matrix_Bareiss")
    m=[row[:] for row in a]
    sign=1
    prev=1
    for k in range(n-1):
        if m[k][k]==0:
            row=next((j for j in range(k+1,n)
                      if m[j][k]!=0),None)
            if row is None:
                return 0
            m[k],m[row]=m[row],m[k]
            sign=-sign
        pivot=m[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                v=pivot*m[i][j]-m[i][k]*m[k][j]
                need(v%prev==0,"fraction_free_division_not_exact")
                m[i][j]=v//prev
            m[i][k]=0
        prev=pivot
    return sign*m[-1][-1]


def original():
    need(gitblob(SOURCE_H20738)==ORIGINAL_RANK2_GITBLOB,
         "original_PR249_exact_Gram_receipt_sha_drift")
    m=parse(SOURCE_H20738,"Y137_TWO_RESIDUAL_MATRIX")
    gram=parse(SOURCE_H20738,"Y137_TWO_RESIDUAL_GRAM")
    need(gram["rank"]=="2" and
         gram["nested_dimension"]=="20738"
         and m["new_to_new_H"]=="NOT_COMPUTED",
         "rank2_source_replaced_by_unaccepted_new_Ritz")
    archive=parse(SOURCE_HTT,"Y137_HTT_ARCHIVE")
    proof=parse(SOURCE_HTT,"Y137_HTT_FULL_MATRIX")
    verdict=parse(SOURCE_HTT,"Y137_HTT_VERDICT")
    need(archive["original_run"]=="43992456055"
         and archive["original_fanin_job"]=="133739257030"
         and archive["original_source_commit"]
             =="45b17f68dfb3ebaffaa7a3eeba54932951b90898"
         and archive["original_rank2_receipt_gitblob"]
             ==ORIGINAL_RANK2_GITBLOB
         and archive["original_S3_physical_H_gitblob"]
             ==ORIGINAL_S3_GITBLOB
         and proof["physical_rows"]=="633919"
         and proof["exact_raw_electric_moves"]=="45642168"
         and proof["source_support_SHA256"]
             =="a9c918de7960e7778a918ec0a06a9d22c83b7385d19e3c636f2ea8b942318b4f"
         and proof["exact_PSD"]=="PASS"
         and proof["exact_global_468_Loewner_ceiling"]=="PASS"
         and verdict["source_shards"]=="8_OF_8_EXACT"
         and verdict["first_Wilson_weight"]=="HOLD",
         "full_original_Htt_source_or_scope_not_accepted")

    den=int(m["old_Gram_det_den"])
    E=[[int(m["E11_num"]),int(m["E12_num"])],
       [int(m["E12_num"]),int(m["E22_num"])]]
    G=[[int(m["old_source_G11"]),int(m["old_source_G12"])],
       [int(m["old_source_G12"]),int(m["old_source_G22"])]]
    K=[[int(m["old_source_H11"]),int(m["old_source_H12"])],
       [int(m["old_source_H12"]),int(m["old_source_H22"])]]
    H=[[int(proof["K11"]),int(proof["K12"])],
       [int(proof["K12"]),int(proof["K22"])]]
    need(den>0
         and E[0][0]>0 and E[0][0]*E[1][1]>E[0][1]*E[1][0]
         and G[0][0]>0 and G[0][0]*G[1][1]>G[0][1]*G[1][0],
         "old_four_vector_Gram_not_positive_definite")
    g11,g12,g22=(den*E[0][0],den*E[0][1],den*E[1][1])
    need(H[0][0]>=0 and H[1][1]>=0
         and H[0][0]*H[1][1]>=H[0][1]**2,
         "original_Htt_not_PSD")
    c11=468*g11-H[0][0]
    c12=468*g12-H[0][1]
    c22=468*g22-H[1][1]
    need(c11>=0 and c22>=0 and c11*c22>=c12*c12,
         "original_Htt_violates_S3_operator_cap")
    return den,E,G,K,H


def full4(z,den,E,G,K,H):
    a=[[0]*4 for i in range(4)]
    for i in range(2):
        for j in range(2):
            a[i][j]=D*K[i][j]-z*G[i][j]
            a[i][2+j]=E[i][j]
            a[2+i][j]=E[i][j]
            a[2+i][2+j]=D*H[i][j]-z*den*E[i][j]
    need(all(a[i][j]==a[j][i] for i in range(4)
             for j in range(4)),
         "four_vector_exact_pencil_not_symmetric")
    return a


def inertia_bareiss(z,den,E,G,K,H):
    matrix=full4(z,den,E,G,K,H)
    for perm in itertools.permutations(range(4)):
        last=1
        negative=0
        valid=True
        for size in range(1,5):
            selected=perm[:size]
            det=determinant([
                [matrix[i][j] for j in selected] for i in selected])
            if det==0:
                valid=False
                break
            negative+=int((det<0)!=(last<0))
            last=det
        if valid:
            return negative
    need(False,"all_4x4_exact_symmetric_pivots_zero")


def two_by_two_inertia(a,b,c):
    det=a*c-b*b
    need(det!=0,"integer_end_point_exact_eigenvalue")
    if a==0:
        need(b!=0,"singular_integer_2x2")
        return 1
    return int(a<0)+int((det<0)!=(a<0))


def inertia_schur(z,den,E,G,K,H):
    # Prove B(z) positive for all 0<=z<=72D using B(72D)>0.
    b11=D*H[0][0]-z*den*E[0][0]
    b12=D*H[0][1]-z*den*E[0][1]
    b22=D*H[1][1]-z*den*E[1][1]
    det=b11*b22-b12*b12
    need(b11>0 and b22>0 and det>0,
         "new_residual_energy_block_not_positive_at_sampled_z")
    a11=D*K[0][0]-z*G[0][0]
    a12=D*K[0][1]-z*G[0][1]
    a22=D*K[1][1]-z*G[1][1]
    e11,e12,e22=E[0][0],E[0][1],E[1][1]
    # E * adj(B) * E:
    q11=b22*e11*e11-2*b12*e11*e12+b11*e12*e12
    q12=b22*e11*e12-b12*(e11*e22+e12*e12)+b11*e12*e22
    q22=b22*e12*e12-2*b12*e12*e22+b11*e22*e22
    return two_by_two_inertia(
        det*a11-q11,det*a12-q12,det*a22-q22)


def exact_bracket(level,den,E,G,K,H):
    lo=0
    hi=72*D
    def two(z):
        n=inertia_schur(z,den,E,G,K,H)
        need(n==inertia_bareiss(z,den,E,G,K,H),
             "four_vector_inertia_two_exact_algorithms_disagree")
        return n
    need(two(lo)<level and two(hi)>=level,
         "four_vector_first_two_levels_outside_0_72")
    while hi-lo>1:
        mid=(lo+hi)//2
        if two(mid)>=level:
            hi=mid
        else:
            lo=mid
    need(two(lo)==level-1 and two(hi)==level,
         "four_vector_1e9_exact_sturm_endpoints_wrong")
    return lo,hi


def toys():
    need(determinant([[5,2],[2,3]])==11
         and determinant([[0,1],[1,0]])==-1,
         "toy_exact_Bareiss_pivot_bad")
    need(two_by_two_inertia(5,2,3)==0
         and two_by_two_inertia(-5,2,3)==1
         and two_by_two_inertia(-5,2,-3)==2,
         "toy_2x2_Schur_inertia_bad")
    need(5*3-2*2>0 and 5*3-6*6<0,
         "toy_sign_forgery_not_detected")
    emit("Y137_HTT_RITZ_TOY",
         bareiss_pivot="PASS",
         independent_2x2_schur="PASS",
         forged_offdiagonal="REJECTED",
         residual_full_state="NOT_COMPUTED",
         Wilson_weight="HOLD")


def real():
    den,E,G,K,H=original()
    cap=72*D
    need(inertia_schur(cap,den,E,G,K,H)==
         inertia_bareiss(cap,den,E,G,K,H),
         "positive_lower_2x2_new_energy_block_not_verified")
    results=[]
    for level in (1,2):
        lo,hi=exact_bracket(level,den,E,G,K,H)
        need((lo,hi)==EXPECTED_RITZ[level-1],
             "frozen_4vector_Ritz_1e9_bracket_drift")
        need(hi<=OLD_UPPER[level-1],
             "new_exact_4vector_Ritz_does_not_improve_envelope")
        results.append((lo,hi))
        emit("Y137_HTT_FOUR_RITZ",
             level=level,lower_z=lo,upper_z=hi,energy_den=D,
             old_468_envelope_upper_z=OLD_UPPER[level-1],
             strict_upper_improvement=OLD_UPPER[level-1]-hi,
             exact_2x2_schur_inertia="PASS",
             independent_4x4_Bareiss_inertia="PASS",
             source_Htt="8_SHARD_ORIGINAL_H",
             spectral_scope="FOUR_VECTOR_ONLY",
             full_20738_Ritz="NOT_COMPUTED",
             Wilson_weight="HOLD")
    low=results[1][0]-results[0][1]
    high=results[1][1]-results[0][0]
    need(low>0 and high>=low,
         "FOUR_only_reduced_Ritz_separation_not_positive")
    emit("Y137_HTT_FOUR_RITZ_VERDICT",
         physical_support="633919_ORIGINAL_S3_ORBITS",
         original_electric_moves=45642168,
         strict_2x2_new_Gram="POSITIVE",
         exact_Htt_3_entries="ACCEPTED_SOURCE",
         two_independent_inertia_routes="2_OF_2_PASS",
         four_vector_projected_gap_lower_num=low,
         four_vector_projected_gap_upper_num=high,
         gap_energy_denom=D,
         physical_full_gap="NOT_CERTIFIED_BY_RITZ_SEPARATION",
         full_20738_Galerkin_eigenpairs="NOT_COMPUTED",
         first_Wilson_spectral_weight="HOLD",
         issue_137="OPEN")


if __name__=="__main__":
    if sys.argv[1:]==["toy"]:
        toys()
    elif sys.argv[1:]==["real"]:
        real()
    else:
        need(False,"usage_toy_real")
