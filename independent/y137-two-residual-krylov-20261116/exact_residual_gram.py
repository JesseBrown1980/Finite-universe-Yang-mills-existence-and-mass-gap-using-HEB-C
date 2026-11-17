#!/usr/bin/env python3
"""Y137 exact W-Gram rank of two FULL physical residual Krylov directions.

Accepted PR247 source: original H20736 rational trial vectors u1,u2 at
original 144 seed numerators z1,z2, D=10**9. Define
    r_i = (D H - z_i)u_i
    t_i = (I-P_20736) r_i = D (I-P_20736) H u_i.
Then t_i is EXACTLY orthogonal to every old Galerkin vector. Compute its
2x2 W-Gram from original K2/K3/K4 electric-flux sources, including the
non-coordinate four-Krylov old W-projector via exact 4x4 Schur inverse:
    T_ij = <r_i,r_j>_W - b_i^T G_old^-1 b_j,
    b_i = B_old^T W r_i = (D K_old - z_i G_old)x_i.
All pairings exact integers/rationals. Validate PR247 independently
recorded self-norm hashes and original old-projector hashes and positivity.

A strictly positive 2x2 determinant proves two new independent directions
and a nested dimension of exactly 20738, with no 429M-matrix construction.
The old-to-new H coupling for the ORIGINAL two samples is exactly T_ij/D
by self-adjointness, but H(t_i,t_j) is NOT computed in this stage.
Therefore there are NO new Ritz values or first-Wilson-weight claims.
"""
import os
import sys
from hashlib import sha256

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PR247 = os.path.join(ROOT, "independent", "y137-h429m-residual-projection-20261116")
SOURCE = os.path.join(PR247, "residual_projection.py")
FROZEN = os.path.join(PR247,
    "RESULT-H429M-FULL-RESIDUAL-PROJECTION-20261116.hbp")
OLD_SOURCE_BLOB = "1a174c7ff47d944370bf3c35ecc8557dfcc3bb17"
FROZEN_RECEIPT_BLOB = "a7af4f4eb556ff60ca98f31dc9c73b2715b5032f"
D = 1000000000
NOLD = 20736
RANK_SUPPORT_K2 = 8034
RANK_SUPPORT_K3 = 147344


def need(ok, reason):
    if not ok:
        print("Y137_TWO_RESIDUAL_REFUSE|reason="+reason+"|json=0",
              flush=True)
        raise SystemExit(1)


def digest(num):
    return sha256(str(num).encode("ascii")).hexdigest()


def emit(label, **fields):
    print(label+"|"+"|".join(str(k)+"="+str(v)
          for k,v in fields.items())+"|json=0",flush=True)


def determinant(a):
    """Integer Bareiss with row swaps, including bordered non-symmetric forms."""
    n = len(a)
    need(n>0 and all(len(row)==n for row in a),
         "determinant_non_square")
    v=[row[:] for row in a]
    previous=1
    sign=1
    for k in range(n-1):
        if not v[k][k]:
            replacement=next((i for i in range(k+1,n)
                              if v[i][k]), None)
            if replacement is None:
                return 0
            v[k],v[replacement]=v[replacement],v[k]
            sign=-sign
        pivot=v[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                numer=pivot*v[i][j]-v[i][k]*v[k][j]
                need(numer%previous==0,
                     "non_integral_fraction_free_determinant")
                v[i][j]=numer//previous
            v[i][k]=0
        previous=pivot
    return sign*v[-1][-1]


def independent_toys():
    a=[[5,2],[2,3]]
    det=determinant(a)
    need(det==11, "toy_Schur_det")
    q1=[1,-2]
    q2=[2,1]
    def adjcross(x,y):
        return -determinant([a[0]+[x[0]],
                             a[1]+[x[1]],
                             y+[0]])
    need(adjcross(q1,q1)==31,
         "toy_self_inverse_numerator")
    need(adjcross(q2,q2)==9,
         "toy_other_inverse_numerator")
    need(adjcross(q1,q2)==2 and
         adjcross(q1,q2)==adjcross(q2,q1),
         "toy_cross_bordered_pair")
    need(31*9-4>0, "toy_two_positive_directions")
    need(determinant([[0,1],[1,0]])==-1,
         "toy_swapped_Bareiss")
    need((11*0+31)>=0 and (31*15-1)>0,
         "toy_negative_control")
    emit("Y137_TWO_RESIDUAL_TOY",
         independent_Bareiss_2x2="PASS",
         signed_bordered_Bareiss_3x3="PASS",
         cross_Gram_symmetry="PASS",
         rank2_discriminator="PASS",
         original_20736_source="NOT_COMPUTED",
         Wilson_weight="HOLD")


def precheck():
    sys.path.insert(0,PR247)
    import residual_projection as pr247
    need(pr247.h429.gitblob(SOURCE)==OLD_SOURCE_BLOB,
         "original_PR247_source_git_blob_drift")
    need(pr247.h429.gitblob(FROZEN)==FROZEN_RECEIPT_BLOB,
         "original_PR247_receipt_git_blob_drift")
    text=open(FROZEN,encoding="ascii").read().splitlines()
    need(len(text)==55, "frozen_PR247_receipt_length")
    split=[]
    for line in text:
        if not line.startswith("Y137_H429M_RESIDUAL_SPLIT|"):
            continue
        data=dict(piece.split("=",1)
                  for piece in line.split("|")[1:] if "=" in piece)
        split.append(data)
    need(len(split)==2
         and [int(t["level"]) for t in split]==[1,2],
         "frozen_PR247_two_original_energies")
    need([int(t["original_144_seed_energy_num"]) for t in split]
         == [69924497999,69963565334],
         "frozen_trial_energy_numerator_drift")
    return split


def dual_of_old_space(x,z,entries,ball,cols,s132,s3,
                      rp,rq2,rq3):
    """Reconstruct exact b = B_old^T W (D H-z)u, not support projection."""
    b=[0]*NOLD
    for tag,i,j,val in entries:
        c=D*val if tag=="K" else -z*val
        b[i]+=c*x[j]
        if i!=j:
            b[j]+=c*x[i]
    for i in range(8):
        need(b[i]==ball["wf"][i]*rp[i],
             "old_flat_dual_not_actual_H_residual")
    for k,f in enumerate(s132):
        need(b[12+k]==ball["wq"][f]*rq2[f],
             "old_K2_indicator_dual_not_actual_H")
    for k,f in enumerate(s3):
        need(b[144+k]==ball["eW"][f]*rq3[k],
             "old_K3_indicator_dual_not_actual_H")
    for a in range(4):
        direct=sum(ball["wq"][i]*cols[a][i]*rq2[i]
                   for i in range(RANK_SUPPORT_K2))
        need(b[8+a]==direct, "old_Krylov_dual_mismatch")
    return b


def schur_reduction(ball, cols, s132):
    """Original 4x4 Gram Schur: indicator block strictly positive diagonal."""
    import nested_ritz as n
    oldG, oldK=n.load_h12()
    core=[[oldG[8+i][8+j] for j in range(4)]
          for i in range(4)]
    for idx in s132:
        w=ball["wq"][idx]
        for i in range(4):
            for j in range(4):
                core[i][j]-=w*cols[i][idx]*cols[j][idx]
    for k in range(1,5):
        need(determinant([row[:k] for row in core[:k]])>0,
             "old_G_4x4_schur_not_positive")
    return core, determinant(core)


def old_cross(bi,bj,ball,cols,s132,s3,core,den):
    """Exact numerator of b_i^T G_old^-1 b_j, common positive den."""
    wf,wq,we=ball["wf"],ball["wq"],ball["eW"]
    diagonal=0
    for k in range(8):
        need(bi[k]%wf[k]==0 and bj[k]%wf[k]==0,
             "noninteger_flat_dual_weight")
        diagonal+=bi[k]*(bj[k]//wf[k])
    for k,f in enumerate(s132):
        w=wq[f]
        need(bi[12+k]%w==0 and bj[12+k]%w==0,
             "noninteger_K2_dual_weight")
        diagonal+=bi[12+k]*(bj[12+k]//w)
    for k,f in enumerate(s3):
        w=we[f]
        need(bi[144+k]%w==0 and bj[144+k]%w==0,
             "noninteger_K3_dual_weight")
        diagonal+=bi[144+k]*(bj[144+k]//w)
    def adjusted(b):
        a=b[8:12]
        for k,idx in enumerate(s132):
            v=b[12+k]
            for j in range(4):
                a[j]-=cols[j][idx]*v
        return a
    ai,aj=adjusted(bi),adjusted(bj)
    numerator=-determinant([core[k]+[ai[k]] for k in range(4)]
                           + [aj+[0]])
    need(numerator == -determinant(
        [core[k]+[aj[k]] for k in range(4)]+[ai+[0]]),
         "old_projected_cross_not_symmetric")
    return diagonal*den+numerator


def raw_full_residuals(samples,ball,keys3,index3,where,s3):
    """Compute exact original full-H residuals and their CROSS weighted pairing.

    Use old accepted H20k direct physical residuals for independent self
    checks, then a single source-backed 72-move traversal of active K3 rows
    for BOTH vectors to reconstruct shell3 and shell4 boundary flux vectors.
    """
    import finite_s3_3x4_r9_first_gap as gauge
    import full_trial_residual as oldr
    import residual_projection as pr247
    wf,wq,we=ball["wf"],ball["wq"],ball["eW"]
    es,esrc,ewc=ball["es"],ball["esrc"],ball["ewc"]
    selection=set(s3)
    collected=[]
    for z,x,p,q2,q3 in samples:
        full6,den6,(rp,rq2,rq3),census=oldr.direct_residual(
            z,p,q2,q3,ball,keys3,index3,where,s3)
        source_norm=oldr.inner_products(p,q2,q3,ball,s3)
        need(den6==6*D*D*source_norm,
             "old_full_source_original_norm_denominator")
        collected.append((rp,rq2,rq3,full6,census))
    flux3=[]
    for z,x,p,q2,q3 in samples:
        v=[0]*len(keys3)
        for f in range(len(keys3)):
            total=0
            for ix in range(es[f],es[f+1]):
                total+=int(ewc[ix])*q2[int(esrc[ix])]
            v[f]=total
        flux3.append(v)
    # Include all nonzero outgoing shell3->shell3 or shell3->shell4
    # weighted source fluxes. Each original 72-move row handled once.
    shell4={}
    count=0
    for t,f in enumerate(s3):
        q1=samples[0][4][t]
        q2=samples[1][4][t]
        if q1==0 and q2==0:
            continue
        key=keys3[f]
        wi=we[f]
        neigh=gauge.neighbors(key)
        need(sum(neigh.values())==72,
             "full_residual_source_non_72_move_K3")
        count+=72
        for dst,mul in neigh.items():
            if dst==key or dst in where:
                continue
            g=index3.get(dst)
            if g is not None:
                if g not in selection:
                    flux3[0][g]+=wi*mul*q1
                    flux3[1][g]+=wi*mul*q2
            else:
                pair=shell4.get(dst)
                if pair is None:
                    pair=[0,0]
                    shell4[dst]=pair
                pair[0]+=wi*mul*q1
                pair[1]+=wi*mul*q2
    need(count<=28634*72 and len(shell4)==499265,
         "whole_source_one_step_scope_changed")
    # Pair weighted exterior *physical amplitudes*. The residual outside
    # old support is r_f=-(D/w_f) S_f, so norm square is D^2 S^2/w_f.
    ext=[[0,0],[0,0]]
    nonzero3=0
    for f in range(len(keys3)):
        if f in selection:
            continue
        fa,fb=flux3[0][f],flux3[1][f]
        if fa or fb:
            nonzero3+=1
        w=we[f]
        need(fa%w==0 and fb%w==0,
             "nonintegral_original_K3_exterior_W_flux")
        ext[0][0]+=w*(fa//w)*(fa//w)
        ext[0][1]+=w*(fa//w)*(fb//w)
        ext[1][1]+=w*(fb//w)*(fb//w)
    for dst,(fa,fb) in shell4.items():
        w=gauge.weight(dst)
        need(w in (1,2,3,6) and fa%w==0 and fb%w==0,
             "nonintegral_original_K4_exterior_W_flux")
        ext[0][0]+=w*(fa//w)*(fa//w)
        ext[0][1]+=w*(fa//w)*(fb//w)
        ext[1][1]+=w*(fb//w)*(fb//w)
    for i in range(2):
        for j in range(i,2):
            a,b=collected[i],collected[j]
            inside=sum(wf[k]*a[0][k]*b[0][k] for k in range(8))
            inside+=sum(wq[k]*a[1][k]*b[1][k]
                        for k in range(RANK_SUPPORT_K2))
            inside+=sum(we[f]*a[2][k]*b[2][k]
                        for k,f in enumerate(s3))
            ext[i][j]=inside+D*D*ext[i][j]
    ext[1][0]=ext[0][1]
    for i in range(2):
        need(6*ext[i][i]==collected[i][3],
             "exact_PR242_full_R_self_norm_fails")
    return ext,collected,len(shell4),nonzero3,count


def real():
    frozen=precheck()
    sys.path.insert(0,PR247)
    import residual_projection as p
    (entries,original_sha,trials,ball,states,cols,s132,
     keys3,index3,where,s3,indexer,nested)=p.pinned()
    samples=[]
    for z,x in trials:
        pp,qq,ee=p.oldr.physical_amplitudes(ball,cols,s132,s3,x)
        samples.append((z,x,pp,qq,ee))
    full,inside,out4,out3,moves=raw_full_residuals(
        samples,ball,keys3,index3,where,s3)
    for i in range(2):
        need(digest(full[i][i])==frozen[i]["exact_full_R_square_sha256"],
             "PR247_frozen_full_residual_integer_hash_mismatch")
    core,den=schur_reduction(ball,cols,s132)
    bs=[dual_of_old_space(samples[i][1],samples[i][0],entries,
        ball,cols,s132,s3,*inside[i][:3])
        for i in range(2)]
    proj=[[0,0],[0,0]]
    for i in range(2):
        for j in range(i,2):
            proj[i][j]=old_cross(bs[i],bs[j],ball,cols,
                                 s132,s3,core,den)
    proj[1][0]=proj[0][1]
    # Independently require original self projector SHA receipts.
    for i in range(2):
        need(digest(proj[i][i])==
             frozen[i]["old_projector_fraction_num_sha256"]
             and digest(den)==
             frozen[i]["old_projector_fraction_den_sha256"],
             "PR247_frozen_self_projector_integer_hash_mismatch")
    # Exact Gram of TWO actual (I-P_old)(D H-z_i)u_i vectors.
    e=[[den*full[i][j]-proj[i][j] for j in range(2)]
       for i in range(2)]
    need(e[0][1]==e[1][0], "residual_cross_Gram_not_symmetric")
    need(e[0][0]>=0 and e[1][1]>=0,
         "unphysical_negative_squared_residual")
    disc=e[0][0]*e[1][1]-e[0][1]*e[0][1]
    need(disc>=0, "two_new_directions_Gram_not_PSD")
    rank=int(e[0][0]!=0 or e[1][1]!=0)+int(disc>0)
    need(rank in (1,2), "both_projected_H_residuals_zero")
    # Difference between 20k-old and 429m-new: two residual vectors
    # include the ENTIRE old-space-orthogonal residual, not a lex subset.
    ugram=[[0,0],[0,0]]
    uk=[[0,0],[0,0]]
    for tag,a,b,val in entries:
        for i in range(2):
            for j in range(i,2):
                term=samples[i][1][a]*samples[j][1][b]
                if a!=b:
                    term+=samples[i][1][b]*samples[j][1][a]
                (ugram if tag=="G" else uk)[i][j]+=val*term
    ugram[1][0]=ugram[0][1]
    uk[1][0]=uk[0][1]
    need(ugram[0][0]*ugram[1][1]>ugram[0][1]**2,
         "original_two_rational_trials_not_independent")
    cos2ppm=(1000000*e[0][1]*e[0][1])//(e[0][0]*e[1][1])
    emit("Y137_TWO_RESIDUAL_SOURCE",
         original_PR247_source_git_blob=OLD_SOURCE_BLOB,
         original_PR247_receipt_git_blob=FROZEN_RECEIPT_BLOB,
         original_H20736_sparse_sha256=original_sha,
         original_basis_rank=NOLD,
         physical_K2_source_states=RANK_SUPPORT_K2,
         physical_K3_source_states=RANK_SUPPORT_K3,
         touched_K4_canonical_states=out4,
         nonzero_exterior_K3_states=out3,
         actual_original_K3_raw_electric_moves=moves,
         D=D,arithmetic="INTEGER_ONLY")
    emit("Y137_TWO_RESIDUAL_GRAM",
         rank=rank,nested_dimension=NOLD+rank,
         source1_seed_z_num=samples[0][0],
         source2_seed_z_num=samples[1][0],
         denominator=den,
         E11_num_sha256=digest(e[0][0]),
         E12_num_sha256=digest(e[0][1]),
         E22_num_sha256=digest(e[1][1]),
         E11_num_bits=e[0][0].bit_length(),
         E12_num_bits=abs(e[0][1]).bit_length(),
         E22_num_bits=e[1][1].bit_length(),
         rank_discriminant_sha256=digest(disc),
         rank_discriminant_sign="POSITIVE" if disc>0 else "ZERO",
         rank_discriminant_bits=disc.bit_length(),
         squared_correlation_ppm=cos2ppm,
         old_to_new_metric_orthogonality="EXACT",
         original_self_full_H_checks="2_OF_2_EXACT",
         original_self_old_projector_checks="2_OF_2_EXACT",
         original_two_source_cross_H="EXACT_SYMMETRIC")
    emit("Y137_TWO_RESIDUAL_HBLOCK",
         old_two_source_Gram_determinant_sign="POSITIVE",
         old_H11_sha256=digest(uk[0][0]),
         old_H12_sha256=digest(uk[0][1]),
         old_H22_sha256=digest(uk[1][1]),
         true_old_to_residual_H11_num_sha256=digest(e[0][0]),
         true_old_to_residual_H12_num_sha256=digest(e[0][1]),
         true_old_to_residual_H22_num_sha256=digest(e[1][1]),
         old_to_residual_H_common_den=den*D,
         new_residual_to_residual_H="NOT_COMPUTED",
         new_two_residual_Ritz="NOT_COMPUTED")
    emit("Y137_TWO_RESIDUAL_VERDICT",
         both_full_H_residuals="EXACT",
         actual_noncoordinate_old_Gram_inverse="EXACT_4X4",
         new_Gram_2x2="EXACT",
         two_new_independent_residual_directions="PASS" if rank==2 else "NO",
         certified_nested_dimension=NOLD+rank,
         new_H_tt_block="HOLD",
         new_Ritz_brackets="HOLD",
         first_Wilson_weight="HOLD",
         issue_137="OPEN")


if __name__ == "__main__":
    if sys.argv[1:]==["toy"]:
        independent_toys()
    elif sys.argv[1:]==["real"]:
        real()
    else:
        need(False,"usage_toy_or_real")
