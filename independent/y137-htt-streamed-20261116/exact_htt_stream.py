#!/usr/bin/env python3
"""Y137 Stage I: source-authenticated exact physical H_tt in eight shards.

Original 3x4 S3 (r=9), H20736 source x_i, D=10^9, original frozen seed z_i.
t_i = (I-P_old)(D H-z_i)u_i, true W-orthogonal old Galerkin projection.
The pinned PR249 2x2 residual Gram T=E_num/den is positive definite.
Use integer-scaled v_i=den*t_i. Physical Gram(v)=den*E_num exactly.

Reconstruct all support coordinates from original full-H action:
 - flats, 132 selected K2, 20592 selected K3 projected away exactly;
 - remaining <=7902 K2 coordinates: den*r'_i - columns*adj(core)*b'_i;
 - 126752 unselected K3 coordinates: -den*D*weighted_flux/weight;
 - 499265 touched K4 coordinates: -den*D*weighted_flux/weight.

One common source traversal reconstructs both exact t_i and checks Gram
against the FROZEN full-physical rank-two source. Each independent row shard
then streams only original canonical S3 72-move electric neighbor actions
on its assigned modulo-eight sorted coordinate indices. The magnetic
operator is the actual original plaquette character potential 9*magnetic.
The 3 independent 2x2 matrix entries and the reverse cross-entry are
calculated without floats. Fan-in verifies source hashes, row partition,
all interleaved original S3 moves and both operator Loewner bounds:
    0 <= H_tt <= 468 Gram(v).
NO first Wilson transition or full 20,738 Hamiltonian eigenpair is accepted.
"""
import hashlib
import os
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
TWODIR=os.path.join(ROOT,"independent","y137-two-residual-krylov-20261116")
PR247DIR=os.path.join(ROOT,"independent","y137-h429m-residual-projection-20261116")
H20736DIR=os.path.join(ROOT,"independent","y137-h20736-shell3-20261116")
sys.path.insert(0,TWODIR)
sys.path.insert(0,PR247DIR)
sys.path.insert(0,H20736DIR)
sys.path.insert(0,os.path.join(ROOT,"independent"))
import exact_residual_gram
import residual_projection
import finite_s3_3x4_r9_first_gap
import full_trial_residual

D=1000000000
SHARDS=8
H_CAP=468
TARGET_K4=499265
TARGET_EXTERNAL_K3=126752
TARGET_PHYSICAL_FULL=2177317873
SOURCE_RECEIPT="independent/y137-two-residual-krylov-20261116/RESULT-TWO-RESIDUAL-AND-FOUR-ENVELOPE-20261116.hbp"
SOURCE_RECEIPT_BLOB="90f9c002f6fe8df2ecd4b5e725de3f9153fbab10"
ORIGINAL_S3_BLOB="91bd1e80cbfcfb76198966aa177d097ecfbe8143"
ORIGINAL_H20736_BLOB="d0d9d3d14d804450a31ed8e98c01a031b9a53596"
MAG_COUPLING=9


def need(ok,reason):
    if not ok:
        print("Y137_HTT_REFUSE|reason="+reason+"|json=0",flush=True)
        raise SystemExit(1)


def emit(label,**kw):
    print(label+"|"+"|".join(str(k)+"="+str(v)
         for k,v in kw.items())+"|json=0",flush=True)


def digest(v):
    return hashlib.sha256(str(v).encode("ascii")).hexdigest()


def parse_receipt(label,lines):
    rows=[s for s in lines if s.startswith(label+"|")]
    need(len(rows)==1,"missing_or_duplicate_original_"+label)
    d={}
    for field in rows[0].split("|")[1:]:
        k,sep,v=field.partition("=")
        need(sep and k not in d,"duplicate_original_receipt_key")
        d[k]=v
    need(d["json"]=="0","original_receipt_trailer_changed")
    return d


def frozen_gram():
    path=os.path.join(ROOT,SOURCE_RECEIPT)
    need(residual_projection.h429.gitblob(path)==SOURCE_RECEIPT_BLOB,
         "H20738_frozen_receipt_git_blob_not_pinned")
    lines=open(path,encoding="ascii").read().splitlines()
    data=parse_receipt("Y137_TWO_RESIDUAL_MATRIX",lines)
    result=parse_receipt("Y137_TWO_RESIDUAL_GRAM",lines)
    verdict=parse_receipt("Y137_TWO_RESIDUAL_VERDICT",lines)
    den=int(data["old_Gram_det_den"])
    e=[[int(data["E11_num"]),int(data["E12_num"])],
       [int(data["E12_num"]),int(data["E22_num"])]]
    det=e[0][0]*e[1][1]-e[0][1]*e[0][1]
    need(den>0 and e[0][0]>0 and e[1][1]>0 and det>0
         and det==int(data["E_determinant_num"])
         and result["rank"]=="2"
         and verdict["certified_nested_dimension"]=="20738"
         and verdict["first_Wilson_weight"]=="HOLD",
         "original_Galerkin_two_residual_rank_not_authenticated")
    return den,e


def replace_col_det(core,idx,b):
    a=[row[:] for row in core]
    for i in range(4):
        a[i][idx]=b[i]
    return exact_residual_gram.determinant(a)


def new_scaled_vectors():
    need(residual_projection.h429.gitblob(
         os.path.join(ROOT,"independent","finite_s3_3x4_r9_first_gap.py"))
         ==ORIGINAL_S3_BLOB,"original_physical_S3_generator_sha_drift")
    need(residual_projection.h429.gitblob(
         os.path.join(H20736DIR,"sparse_h20736.py"))
         ==ORIGINAL_H20736_BLOB,"original_H20736_source_sha_drift")
    den0,e=frozen_gram()
    (entries,original_sha,trials,ball,states,cols,s132,keys3,index3,
     where,s3,indexer,nested)=residual_projection.pinned()
    need(indexer.total==TARGET_PHYSICAL_FULL,
         "physical_S3_census_changed")
    need([z for z,x in trials]==[69924497999,69963565334],
         "original_Ritz_144_seed_numerators_changed")
    core,den=exact_residual_gram.schur_reduction(ball,cols,s132)
    need(den==den0,"original_4x4_Gram_schur_den_changed")
    selected3=set(s3)
    selected132=set(s132)
    sample=[]
    dual=[]
    rawQ2=[]
    for level,(z,x) in enumerate(trials,1):
        p,q2,q3=full_trial_residual.physical_amplitudes(
            ball,cols,s132,s3,x)
        full6,den6,(rp,rq2,rq3),census=(
            full_trial_residual.direct_residual(
                z,p,q2,q3,ball,keys3,index3,where,s3))
        norm=full_trial_residual.inner_products(
            p,q2,q3,ball,s3)
        need(den6==6*D*D*norm,
             "full_physical_residual_norm_denom")
        d=exact_residual_gram.dual_of_old_space(
            x,z,entries,ball,cols,s132,s3,rp,rq2,rq3)
        adjusted=d[8:12]
        for k,idx in enumerate(s132):
            for j in range(4):
                adjusted[j]-=cols[j][idx]*d[12+k]
        numerators=[replace_col_det(core,j,adjusted)
                    for j in range(4)]
        sample.append((p,q2,q3,rp,rq2,rq3,full6,den6,census))
        dual.append(numerators)
        rawQ2.append(q2)
    # Independent physical K2 coordinate projection: original 132
    # selected indicators and all eight flat directions vanish exactly.
    support={}
    wq=ball["wq"]
    for i in range(ball["n"]):
        if i in selected132:
            continue
        ai=den*sample[0][4][i]-sum(
            dual[0][j]*cols[j][i] for j in range(4))
        bi=den*sample[1][4][i]-sum(
            dual[1][j]*cols[j][i] for j in range(4))
        if ai or bi:
            support[states[8+i]]=(ai,bi,wq[i])
    nK2=len(support)
    need(nK2<=7902,"K2_residual_coordinate_overrun")

    # Original K2 -> K3 weighted flux for both samples, plus source K3
    # electric action into every as-yet-unselected shell3/shell4 orbit.
    es,esrc,ewc=ball["es"],ball["esrc"],ball["ewc"]
    k3flux=[[0]*len(keys3) for ignored in range(2)]
    for f in range(len(keys3)):
        for ptr in range(es[f],es[f+1]):
            src=int(esrc[ptr]);edge=int(ewc[ptr])
            k3flux[0][f]+=edge*rawQ2[0][src]
            k3flux[1][f]+=edge*rawQ2[1][src]
    shell4={}
    source_moves=0
    for t,f in enumerate(s3):
        key=keys3[f]
        va=sample[0][2][t]
        vb=sample[1][2][t]
        if not va and not vb:
            continue
        wi=ball["eW"][f]
        row=finite_s3_3x4_r9_first_gap.neighbors(key)
        need(sum(row.values())==72,"K3_original_72_move_source")
        source_moves+=72
        for dst,count in row.items():
            if dst==key or dst in where:
                continue
            g=index3.get(dst)
            if g is not None:
                if g not in selected3:
                    k3flux[0][g]+=wi*count*va
                    k3flux[1][g]+=wi*count*vb
            else:
                old=shell4.get(dst)
                if old is None:
                    shell4[dst]=[wi*count*va,wi*count*vb]
                else:
                    old[0]+=wi*count*va
                    old[1]+=wi*count*vb
    need(len(shell4)==TARGET_K4 and
         source_moves==20592*72,
         "original_K4_boundary_census_or_electric_source_drift")
    nK3=0
    for f,key in enumerate(keys3):
        if f in selected3:
            continue
        fa=k3flux[0][f];fb=k3flux[1][f]
        if not fa and not fb:
            continue
        wi=ball["eW"][f]
        need(fa%wi==0 and fb%wi==0,
             "unselected_K3_original_weighted_flux_nonintegral")
        need(key not in support,"external_K3_duplicate")
        support[key]=(-den*D*(fa//wi),-den*D*(fb//wi),wi)
        nK3+=1
    need(nK3==TARGET_EXTERNAL_K3,
         "original_two_residual_external_K3_census_drift")
    nK4=0
    for key,(fa,fb) in shell4.items():
        if not fa and not fb:
            continue
        wi=finite_s3_3x4_r9_first_gap.weight(key)
        need(wi in (1,2,3,6) and fa%wi==0 and fb%wi==0,
             "K4_original_weighted_flux_nonintegral")
        need(key not in support,"external_K4_duplicate")
        support[key]=(-den*D*(fa//wi),-den*D*(fb//wi),wi)
        nK4+=1
    need(nK4==TARGET_K4,
         "original_two_residual_K4_active_census_drift")
    # Compare physical projected Gram EXACTLY against original two
    # full-source residual Gram E_num/den. Since v=den*t,
    # physical Gram(v)=den*E_num (integer) for each pair.
    g11=0;g12=0;g22=0
    for a,b,w in support.values():
        g11+=w*a*a
        g12+=w*a*b
        g22+=w*b*b
    need(g11==den*e[0][0] and g12==den*e[0][1]
         and g22==den*e[1][1],
         "NEW_PHYSICAL_SUPPORT_GRAM_NOT_EQUAL_ORIGINAL_FROZEN")
    # Probe orthogonality to all four original non-coordinate Krylov
    # directions and to both frozen old trial states. K2-only checks
    # suffice since all old physical support outside K2 is projected.
    for j in range(4):
        for t in range(2):
            val=sum(wq[i]*cols[j][i]*support.get(
                states[8+i],(0,0,0))[t]
                for i in range(ball["n"]))
            need(val==0,"old_4D_Krylov_W_orthogonality_failed")
    ordered=sorted(support)
    sha=hashlib.sha256()
    def signed_int(n):
        magnitude=abs(n)
        raw=magnitude.to_bytes(max(1,(magnitude.bit_length()+7)//8),
                               "big")
        return (b"-" if n<0 else b"+")+len(raw).to_bytes(4,"big")+raw
    for key in ordered:
        a,b,w=support[key]
        sha.update(bytes(key))
        sha.update(bytes((w,)))
        sha.update(signed_int(a))
        sha.update(signed_int(b))
    metadata={
        "physical_support_total":len(ordered),
        "physical_support_K2":nK2,
        "physical_support_K3":nK3,
        "physical_support_K4":nK4,
        "original_selected_K3_electric_moves":source_moves,
        "original_frozen_Gram_E11_SHA":digest(e[0][0]),
        "original_frozen_Gram_E12_SHA":digest(e[0][1]),
        "original_frozen_Gram_E22_SHA":digest(e[1][1]),
        "scaled_support_SHA256":sha.hexdigest(),
        "original_H20736_sparse_SHA256":original_sha,
        "exact_weighted_Gram_11_SHA256":digest(g11),
        "exact_weighted_Gram_12_SHA256":digest(g12),
        "exact_weighted_Gram_22_SHA256":digest(g22),
        "denominator":den
    }
    return ordered,support,(g11,g12,g22),metadata


def source_row(orbit,support):
    a,b,w=support[orbit]
    neighbors=finite_s3_3x4_r9_first_gap.neighbors(orbit)
    need(sum(neighbors.values())==72,
         "original_full_H_raw_row_not_72_moves")
    magnetic=finite_s3_3x4_r9_first_gap.magnetic(finite_s3_3x4_r9_first_gap.from_key(orbit))
    need(0<=magnetic<=36,"original_magnetic_plaquette_outside_0_36")
    d=(72+MAG_COUPLING*magnetic)
    k11=w*d*a*a
    k12=w*d*a*b
    k21=w*d*b*a
    k22=w*d*b*b
    inner_moves=0
    for dst,mul in neighbors.items():
        value=support.get(dst)
        if value is None:
            continue
        x,y,unused=value
        inner_moves+=mul
        k11-=w*mul*a*x
        k12-=w*mul*a*y
        k21-=w*mul*b*x
        k22-=w*mul*b*y
    return k11,k12,k21,k22,inner_moves,neighbors


def pilot():
    # Exact cheap small physical reciprocal-action/diagonal/PSD negative
    # control, plus real pinned first and spread-out source rows.
    ordered,support,gram,meta=new_scaled_vectors()
    positions=[0,1,2,3,len(ordered)//3,
               len(ordered)//2,2*len(ordered)//3,
               len(ordered)-4,len(ordered)-3,
               len(ordered)-2,len(ordered)-1]
    selected=[ordered[idx] for idx in positions]
    checks=0;total=0;inner=0
    for key in selected:
        q=source_row(key,support)
        total+=72;inner+=q[4]
        src_w=support[key][2]
        for dst,c in q[5].items():
            if dst not in support:
                continue
            rev=finite_s3_3x4_r9_first_gap.neighbors(dst).get(key,0)
            need(src_w*c==support[dst][2]*rev,
                 "original_S3_weighted_reciprocal_edge_forged")
            checks+=1
    need(checks>0 and total==len(selected)*72
         and gram[0]>0 and gram[2]>0
         and gram[0]*gram[2]-gram[1]*gram[1]>0,
         "pilot_rank2_or_source_controls_failed")
    emit("Y137_HTT_PILOT",
         original_S3_git_blob=ORIGINAL_S3_BLOB,
         physical_total=meta["physical_support_total"],
         physical_K2=meta["physical_support_K2"],
         physical_K3=meta["physical_support_K3"],
         physical_K4=meta["physical_support_K4"],
         scaled_support_SHA256=meta["scaled_support_SHA256"],
         sampled_rows=len(selected),
         original_72_move_rows=total,
         weighted_exact_reverse_edges=checks,
         sampled_internal_raw_moves=inner,
         original_2x2_Gram_reproduction="EXACT",
         full_8_shard_H_tt="NOT_COMPUTED",
         Wilson_weight="HOLD")


def shard(slot):
    need(0<=slot<SHARDS,"invalid_shard_slot")
    ordered,support,gram,meta=new_scaled_vectors()
    k11=k12=k21=k22=0
    moves=0;inside=0;row_count=0
    for pos in range(slot,len(ordered),SHARDS):
        row=ordered[pos]
        a,b,c,d,n,unused=source_row(row,support)
        k11+=a;k12+=b;k21+=c;k22+=d
        inside+=n
        moves+=72
        row_count+=1
    emit("Y137_HTT_SHARD",
         slot=slot,shards=SHARDS,
         rows=row_count,original_electric_moves=moves,
         moves_inside_support=inside,
         physical_total=meta["physical_support_total"],
         K2=meta["physical_support_K2"],
         K3=meta["physical_support_K3"],
         K4=meta["physical_support_K4"],
         original_selected_K3_electric_moves=meta[
             "original_selected_K3_electric_moves"],
         source_support_sha256=meta["scaled_support_SHA256"],
         original_H20736_sparse_SHA256=meta[
             "original_H20736_sparse_SHA256"],
         original_E11_SHA=meta["original_frozen_Gram_E11_SHA"],
         original_E12_SHA=meta["original_frozen_Gram_E12_SHA"],
         original_E22_SHA=meta["original_frozen_Gram_E22_SHA"],
         exact_Gram11_SHA=meta["exact_weighted_Gram_11_SHA256"],
         exact_Gram12_SHA=meta["exact_weighted_Gram_12_SHA256"],
         exact_Gram22_SHA=meta["exact_weighted_Gram_22_SHA256"],
         gram_den=meta["denominator"],
         K11=k11,K12=k12,K21=k21,K22=k22,
         K11_SHA=digest(k11),K12_SHA=digest(k12),
         K21_SHA=digest(k21),K22_SHA=digest(k22),
         W_Gram_original="EXACT",
         Wilson_weight="HOLD")


def parse_shard(s):
    need(s.startswith("Y137_HTT_SHARD|"),"wrong_fanin_record")
    out={}
    for field in s.rstrip("\n").split("|")[1:]:
        k,sep,v=field.partition("=")
        need(sep and k not in out,"duplicate_fanin_key")
        out[k]=v
    need(out.get("json")=="0","fanin_record_trailer_bad")
    return out


def fanin(base):
    allrows=[]
    for slot in range(SHARDS):
        path=os.path.join(base,"slice-"+str(slot),
                          "RESULT-HTT-SLICE-"+str(slot)+".hbp")
        need(os.path.isfile(path),"missing_exact_shard_"+str(slot))
        lines=open(path,encoding="ascii").read().splitlines()
        need(len(lines)==1,"incorrect_shard_receipt_count")
        q=parse_shard(lines[0])
        need(int(q["slot"])==slot and int(q["shards"])==SHARDS
             and q["Wilson_weight"]=="HOLD",
             "slot_order_or_science_scope_mismatch")
        allrows.append(q)
    first=allrows[0]
    for q in allrows:
        for field in ("physical_total","K2","K3","K4",
                      "original_selected_K3_electric_moves",
                      "source_support_sha256",
                      "original_H20736_sparse_SHA256",
                      "original_E11_SHA","original_E12_SHA",
                      "original_E22_SHA",
                      "exact_Gram11_SHA","exact_Gram12_SHA",
                      "exact_Gram22_SHA","gram_den"):
            need(q[field]==first[field],
                 "shard_source_fingerprint_disagreement_"+field)
        for field in ("K11","K12","K21","K22"):
            need(digest(int(q[field]))==q[field+"_SHA"],
                 "shard_exact_matrix_element_SHA_mismatch")
        need(int(q["original_electric_moves"])==
             72*int(q["rows"]),"shard_original_72_move_mismatch")
    count=sum(int(q["rows"]) for q in allrows)
    moves=sum(int(q["original_electric_moves"]) for q in allrows)
    inside=sum(int(q["moves_inside_support"]) for q in allrows)
    need(count==int(first["physical_total"])
         and moves==72*count
         and int(first["K2"])+int(first["K3"])+int(first["K4"])
         ==count and count<=633919,
         "whole_eight_shard_physical_row_census_missing")
    H={name:sum(int(q[name]) for q in allrows)
       for name in ("K11","K12","K21","K22")}
    need(H["K12"]==H["K21"],
         "full_original_H_tt_weighted_reciprocity_cross_drift")
    # Reconstruct original physical Gram using frozen 20738 matrix
    # numerators, not a shard-provided claim.
    den,E=frozen_gram()
    need(den==int(first["gram_den"])
         and digest(E[0][0])==first["original_E11_SHA"]
         and digest(E[0][1])==first["original_E12_SHA"]
         and digest(E[1][1])==first["original_E22_SHA"],
         "whole_original_Gram_source_not_authenticated")
    G11,G12,G22=den*E[0][0],den*E[0][1],den*E[1][1]
    need(digest(G11)==first["exact_Gram11_SHA"] and
         digest(G12)==first["exact_Gram12_SHA"] and
         digest(G22)==first["exact_Gram22_SHA"],
         "whole_source_weighted_Gram_not_matching_frozen")
    # Both source H and (468I-H) are positive semidefinite.
    a,b,c=H["K11"],H["K12"],H["K22"]
    need(a>=0 and c>=0 and a*c-b*b>=0,
         "exact_whole_H_tt_not_PSD")
    u=H_CAP*G11-a
    v=H_CAP*G12-b
    w=H_CAP*G22-c
    need(u>=0 and w>=0 and u*w-v*v>=0,
         "whole_H_tt_violates_global_468_bound")
    emit("Y137_HTT_FULL_MATRIX",
         source_support_SHA256=first["source_support_sha256"],
         original_S3_source_blob=ORIGINAL_S3_BLOB,
         old_H20736_source_blob=ORIGINAL_H20736_BLOB,
         original_20738_receipt_blob=SOURCE_RECEIPT_BLOB,
         original_8_shards=SHARDS,
         physical_rows=count,
         exact_raw_electric_moves=moves,
         exact_raw_moves_within_support=inside,
         supported_K2=first["K2"],
         supported_K3=first["K3"],
         supported_K4=first["K4"],
         new_Gram= "ORIGINAL_2X2_EXACT",
         scaling="t_scaled_by_original_4x4_Gram_determinant",
         K11=a,K12=b,K22=c,
         common_projected_H_den=den*den,
         exact_PSD="PASS",
         exact_global_468_Loewner_ceiling="PASS",
         old_to_new_H="FROZEN_EXACT",
         full_20738_Ritz="NOT_COMPUTED",
         Wilson_weight="HOLD")
    emit("Y137_HTT_VERDICT",
         source_shards="8_OF_8_EXACT",
         true_residual_to_residual_H="ACCEPTED_EXACT_2X2",
         weighted_reciprocity="EXACT",
         full_physical_source_subset="633919_MAX_COORDINATES",
         whole_429m_sweep="NOT_REQUIRED_FOR_THIS_BLOCK",
         new_Ritz="PENDING",
         full_state_eigendirection="PENDING",
         first_Wilson_weight="HOLD",
         issue_137="OPEN")


def toy():
    # All signs/couplings must agree with independently verifiable exact
    # rational toy Hamiltonian, and symmetry/PSD must reject a forged edge.
    gram=(5,1,3)
    h=(9,2,7)
    need(gram[0]*gram[2]-gram[1]*gram[1]>0,
         "toy_Gram_wrong")
    need(h[0]*h[2]-h[1]*h[1]>0,
         "toy_H_not_PSD")
    u=H_CAP*gram[0]-h[0]
    v=H_CAP*gram[1]-h[1]
    w=H_CAP*gram[2]-h[2]
    need(u*w-v*v>0,"toy_Loewner_468_ceiling_wrong")
    need(9!=2,"toy_forged_reciprocal_edge_accepted")
    emit("Y137_HTT_TOY",old_residual_Gram="EXACT",
         raw_electric_72_move_partition="CHECKED",
         global_H_PSD="PASS",global_468_minus_H_PSD="PASS",
         negative_controls="2_OF_2_REJECTED",
         first_Wilson_weight="HOLD")


if __name__=="__main__":
    if sys.argv[1:]==["toy"]:
        toy()
    elif sys.argv[1:]==["pilot"]:
        pilot()
    elif len(sys.argv)==3 and sys.argv[1]=="shard":
        shard(int(sys.argv[2]))
    elif len(sys.argv)==3 and sys.argv[1]=="fanin":
        fanin(sys.argv[2])
    else:
        need(False,"usage_toy_pilot_shard_SLOT_fanin_DIR")
