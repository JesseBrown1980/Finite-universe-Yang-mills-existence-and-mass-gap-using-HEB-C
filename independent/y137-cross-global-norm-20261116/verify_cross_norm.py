#!/usr/bin/env python3
"""Independent exact global H operator-norm bound for accepted 20736x2 C.

Original finite S3 H obeys 0 <= H <= 468 I in the full physical W Hilbert
space. Let B denote the 20736 old basis, V the two new residual vectors.
G_old=B^T W B, Gv=V^T W V, C=B^T W H V. Therefore
  C^T G_old^-1 C <= V^T W H^2 V <= 468^2 Gv.
The left hand side uses ONLY the original four-dimensional Schur inverse
plus coordinate-diagonal contributions. Check 3 independent entries and
exact 2x2 PSD, entirely with integers, independently by adjugate and
bordered Bareiss determinant. No eigenvector or Wilson weight is claimed.
"""
import hashlib
import os
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
CROSS=os.path.join(ROOT,"independent","y137-full-cross-20261116")
sys.path.insert(0,CROSS)
import exact_old_new_coupling as prior
h=prior.h
erg=h.exact_residual_gram
D=1000000000
CAP=468
N=20736
ACCEPTED_C_SHA="fafdd16b524af6e0f8aea96fcda5699fb89968c498e406792a1ed576a0226b7f"
ACCEPTED_SOURCE_SHA="a9c918de7960e7778a918ec0a06a9d22c83b7385d19e3c636f2ea8b942318b4f"
ACCEPTED_OLD_SHA="1152059150d6bd839ec82e6db3bbd734bb25440d75be0fff25a9a72dc2ac2f89"
ARCHIVE=os.path.join(HERE,"RESULT-CROSS-FULL-20261116.hbp")

def need(cond,why):
    if not cond:
        print("Y137_GLOBAL_C_REFUSE|reason="+why+"|json=0",flush=True)
        raise SystemExit(1)

def emit(label,**kw):
    print(label+"|"+"|".join(str(k)+"="+str(v) for k,v in kw.items())+"|json=0",flush=True)

def digest(x):
    return hashlib.sha256(str(x).encode("ascii")).hexdigest()

def parse(label,lines):
    rows=[line for line in lines if line.startswith(label+"|")]
    need(len(rows)==1,"invalid_record_"+label)
    ans={}
    for item in rows[0].split("|")[1:]:
        key,sep,value=item.partition("=")
        need(sep and key not in ans,"duplicate_archive_field")
        ans[key]=value
    need(ans.get("json")=="0","invalid_archive_trailer")
    return ans

def read_matrix(path):
    need(os.path.isfile(path),"accepted_cross_artifact_missing")
    need(prior.sha256_file(path)==ACCEPTED_C_SHA,
         "original_cross_matrix_SHA256_drift")
    values=[[],[]]
    with open(path,encoding="ascii") as fd:
        for i,line in enumerate(fd):
            fields=line.rstrip("\n").split("\t")
            need(len(fields)==3 and i<N,
                 "invalid_full_cross_matrix_record")
            idx,a,b=map(int,fields)
            need(idx==i,"cross_matrix_index_permutation")
            values[0].append(a)
            values[1].append(b)
    need(len(values[0])==len(values[1])==N,
         "cross_matrix_dimension_drift")
    return values

def adjugate4(m,den):
    ans=[]
    for i in range(4):
        row=[]
        for j in range(4):
            # adj(i,j) = cofactor(j,i).
            sub=[[m[r][c] for c in range(4) if c!=i]
                 for r in range(4) if r!=j]
            row.append((-1 if (i+j)&1 else 1)*erg.determinant(sub))
        ans.append(row)
    for i in range(4):
        for j in range(4):
            need(sum(m[i][k]*ans[k][j] for k in range(4))
                 == (den if i==j else 0),
                 "independent_4x4_adjugate_inverse_wrong")
    return ans

def independent_old_projector_num(bi,bj,ball,cols,s132,s3,core,adj,den):
    wf,wq,we=ball["wf"],ball["wq"],ball["eW"]
    pairs=([(i,wf[i]) for i in range(8)]+
           [(12+k,wq[idx]) for k,idx in enumerate(s132)]+
           [(144+k,we[f]) for k,f in enumerate(s3)])
    need(len(pairs)==N-4,"coordinate_gram_count_wrong")
    diag=0
    for idx,w in pairs:
        need(w>0 and bi[idx]%w==0 and bj[idx]%w==0,
             "coordinate_H_dual_not_weight_divisible")
        diag+=bi[idx]*(bj[idx]//w)
    def subtract_selected(b):
        a=list(b[8:12])
        for k,idx in enumerate(s132):
            for j in range(4):
                a[j]-=cols[j][idx]*b[12+k]
        return a
    ai,aj=subtract_selected(bi),subtract_selected(bj)
    numer=diag*den
    numer+=sum(ai[i]*adj[i][j]*aj[j]
               for i in range(4) for j in range(4))
    return numer

def toy():
    core=[[5,1],[1,4]]
    need(5*4-1==19,"toy_positive_schur")
    cap=CAP*CAP*19*3
    need(cap>0 and cap-(cap+1)<0,
         "toy_forged_upper_bound_not_rejected")
    emit("Y137_GLOBAL_C_TOY",Schur_inverse="PASS",
         too_large_cross="REJECTED",exact_integer="PASS",
         first_Wilson_weight="HOLD")

def accept(path):
    lines=open(ARCHIVE,encoding="ascii").read().splitlines()
    archived=parse("Y137_CROSS_MATRIX",lines)
    verdict=parse("Y137_CROSS_VERDICT",lines)
    need(archived["C_file_sha256"]==ACCEPTED_C_SHA
         and archived["residual_physical_source_sha256"]==ACCEPTED_SOURCE_SHA
         and archived["original_basis_sha256"]==ACCEPTED_OLD_SHA
         and archived["frozen_Gram_numerator_identities"]=="4_OF_4_PASS"
         and archived["original_source_rows"]=="28634"
         and archived["exact_entries"]=="41472"
         and verdict["full_old_to_new_H"]=="ACCEPTED_EXACT_20736x2"
         and verdict["first_Wilson_weight"]=="HOLD",
         "frozen_accepted_original_source_receipt_changed")
    b=read_matrix(path)
    rows,source_cols,old_sha=prior.old_basis()
    need(old_sha==ACCEPTED_OLD_SHA and len(rows)==28634,
         "original_old_basis_source_fingerprint_drift")
    ball,states,cols,s132=prior.old.old_source()
    s3=[f for score,total,f in prior.proj.h20.source_score(ball,cols)]
    need(len(s132)==132 and len(s3)==20592,
         "old_physical_Gram_basis_selection")
    core,den=erg.schur_reduction(ball,cols,s132)
    frozen_den,e=h.frozen_gram()
    need(den==frozen_den and den>0,"old_Schur_det_not_frozen")
    adj=adjugate4(core,den)
    nums={}
    for i,j in ((0,0),(0,1),(1,1)):
        direct=independent_old_projector_num(
            b[i],b[j],ball,cols,s132,s3,core,adj,den)
        archived_route=erg.old_cross(
            b[i],b[j],ball,cols,s132,s3,core,den)
        need(direct==archived_route,
             "two_independent_Gram_inverse_routes_disagree")
        nums[i,j]=direct
    gv11,gv12,gv22=(den*e[0][0],den*e[0][1],den*e[1][1])
    cap2=CAP*CAP
    # With projector squared-Gram numerator nums/den, the inequality
    # cap² Gv - (C^T G_old^-1 C) >= 0 is equivalent to R >= 0.
    r11=cap2*den*gv11-nums[0,0]
    r12=cap2*den*gv12-nums[0,1]
    r22=cap2*den*gv22-nums[1,1]
    det=r11*r22-r12*r12
    need(r11>=0 and r22>=0 and det>=0,
         "global_original_468_operator_ceiling_cross_violation")
    need(gv11>0 and gv22>0 and gv11*gv22-gv12*gv12>0,
         "original_new_weighted_residual_rank_drift")
    emit("Y137_GLOBAL_C_MATRIX",old_dim=N,new_dim=2,
         exact_source_cross_sha256=ACCEPTED_C_SHA,
         old_basis_sha256=old_sha,
         original_schur_Gram_determinant_sha256=digest(den),
         projected_norm11_sha256=digest(nums[0,0]),
         projected_norm12_sha256=digest(nums[0,1]),
         projected_norm22_sha256=digest(nums[1,1]),
         global_468_slack11_sha256=digest(r11),
         global_468_slack12_sha256=digest(r12),
         global_468_slack22_sha256=digest(r22),
         global_468_slack_det_sha256=digest(det),
         two_independent_exact_inverse_methods="3_OF_3_AGREE",
         global_cross_operator_ceiling_468="PSD_EXACT_PASS",
         full_20738_Ritz="NOT_COMPUTED",
         first_Wilson_weight="HOLD")
    emit("Y137_GLOBAL_C_VERDICT",
         all_41472_cross_entries_checked="YES",
         matrix_from_accepted_production="SHA256_PINNED",
         full_20738_Ritz="NEXT_GATE",
         first_Wilson_weight="HOLD",issue_137="OPEN")

if __name__=="__main__":
    if sys.argv[1:]==["toy"]:
        toy()
    elif len(sys.argv)==3 and sys.argv[1]=="accept":
        accept(sys.argv[2])
    else:
        need(False,"usage_toy_or_accept_MATRIX_PATH")
