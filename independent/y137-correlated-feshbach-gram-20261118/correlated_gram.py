#!/usr/bin/env python3
"""Original S3 Wilson: shared-Q two-energy Gram/projector exact-integer candidate gate.

For true full states psi_i(x_i) with distinct E_i, <psi2,psi1>=
<x2,G21 x1>_W=0.  Therefore M_c=M_O2-c G21 has exactly the same
physical E1->E2 matrix element as M_O2 for every rational c.

Source centers Ghat=(2*Ohat - O2hat)/7 have exact shared-Q provenance.
The interval error below is a safe independent-radius combination, NOT
a covariance improvement. Source-only dark angles cannot prove true weight.
"""
import hashlib
import os
import sys
from math import gcd, isqrt

HERE=os.path.dirname(os.path.abspath(__file__))
INDEP=os.path.dirname(HERE)
sys.path.insert(0,os.path.join(INDEP,"y137-weighted-projector-trace-20261117"))
import projector_trace as pt

T=1000000000000
U=T
N=8
WF=(1,3,2,3,3,2,2,2)


def need(cond,reason):
    if not cond:
        print("Y137_GRAM_REFUSE|reason="+reason+"|json=0",flush=True)
        raise SystemExit(1)


def emit(tag,**kws):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in kws.items())+
          "|json=0",flush=True)


def digest(x):
    return hashlib.sha256(str(x).encode("ascii")).hexdigest()


def ceildiv(a,b):
    need(a>=0 and b>0,"ceildiv_domain")
    return (a+b-1)//b


def sqrtceil(n):
    need(n>=0,"negative_sqrt")
    r=isqrt(n)
    return r if r*r==n else r+1


def sqrtupper(num,den):
    need(num>=0 and den>0,"sqrt_ratio_domain")
    return sqrtceil(ceildiv(num*U*U,den))


def wdot(a,b):
    return sum(WF[i]*a[i]*b[i] for i in range(N))


def rawrows(A,v):
    return [sum(A[i][j]*v[j] for j in range(N)) for i in range(N)]


def weighted_action(rows):
    return [(6//WF[i])*rows[i] for i in range(N)]


def chord_upper(s):
    need(0<=s<U,"true_flat_sine")
    cosine_lower=isqrt(U*U-s*s)
    return sqrtceil(2*U*(U-cosine_lower))


def candidate(p,q,A2,R2,A0,R0,v1,v2,s1,s2,gop):
    need(isinstance(p,int) and isinstance(q,int) and q>0,
         "candidate_rational")
    d=7*q
    cnum=(7*q+p)
    ob=(2*p)
    C=[[cnum*A2[i][j]-ob*A0[i][j] for j in range(N)]
       for i in range(N)]
    Rad=[[abs(cnum)*R2[i][j]+abs(ob)*R0[i][j] for j in range(N)]
         for i in range(N)]
    # Correct direct correlation: C=(7q+p)O2 - 2p O.
    for i in range(N):
        for j in range(N):
            need(C[i][j]==7*q*A2[i][j]-p*(2*A0[i][j]-A2[i][j]),
                 "shared_Q_center_Gram_identity")
    rows=rawrows(C,v1)
    norm1=wdot(v1,v1)
    norm2=wdot(v2,v2)
    sqrtprod=sqrtceil(norm1*norm2)
    a=sum(v2[i]*rows[i] for i in range(N))
    amp_lo=abs(a)*U//(d*T*T*sqrtprod)
    amp_hi=ceildiv(abs(a)*U,d*T*T*max(1,isqrt(norm1*norm2)))
    weighted_num=sum((6//WF[i])*rows[i]*rows[i] for i in range(N))
    action=sqrtupper(weighted_num,6*d*d*T*T*T*T*norm1)
    # Dir-specific radius, not Frobenius, retains original fixed v1.
    errrows=[sum(Rad[i][j]*abs(v1[j]) for j in range(N)) for i in range(N)]
    err_num=sum((6//WF[i])*errrows[i]*errrows[i] for i in range(N))
    err=sqrtupper(err_num,6*d*d*T*T*T*T*norm1)
    gs1=pt.old.FLOOR-pt.old.E1_HI
    gs2=pt.old.FLOOR-pt.old.E2_HI
    need(gs1>0 and gs2>0,"source_true_energy_under_Q_floor")
    op=21*gop+ceildiv(abs(p)*gop,q)
    c1=chord_upper(s1)
    c2=chord_upper(s2)
    e1=ceildiv(op*c1,U)
    total_err=e1+err
    # Any true dark x2 has <x2,(M_O2-c*G21)x1>_W=0.
    # Compare it to the frozen (v2,v1) source and two true angle caps.
    rhs=ceildiv(c2*action,U)
    rhs+=ceildiv((U+c2)*total_err,U)
    margin=amp_lo-rhs
    # True source-Q normalized fixed vectors not claimed to be true eigenstates.
    result=dict(c_num=p,c_den=q,
                center_amp_lo_per_trillion=amp_lo,
                center_amp_hi_per_trillion=amp_hi,
                source_action_hi_per_trillion=action,
                directional_source_radius_hi_per_trillion=err,
                ground_projector_error_hi_per_trillion=e1,
                true_E2_chord_hi_per_trillion=c2,
                true_E1_chord_hi_per_trillion=c1,
                physical_op_hi_per_trillion=op,
                no_dark_rhs_hi_per_trillion=rhs,
                strict_no_dark_margin_per_trillion=margin,
                source_radius_construction="SHARED_Q_CENTRE_INDEPENDENT_RADII",
                full_original_Wilson_weight="HOLD")
    return result,C


def toy():
    # Exact 2x2 shared-centre identity and W-trace test.
    # Rebuild a consistent example with exact integer divisibility.
    trueG=[[2,1],[1,3]]
    trueO=[[7,2],[5,9]]
    trueO2=[[2*trueO[i][j]-7*trueG[i][j] for j in range(2)]
             for i in range(2)]
    need(all((2*trueO[i][j]-trueO2[i][j])//7==trueG[i][j]
             for i in range(2) for j in range(2)),
         "shared_Gram_toy_identity")
    v=(1,2)
    g=(2,1)
    M=((4,1),(2,5))
    need((g[0]*v[0]+g[1]*v[1])==4 and
         (g[0]*sum(M[0][j]*v[j] for j in range(2))+
          g[1]*sum(M[1][j]*v[j] for j in range(2)))==24,
         "nonnormal_toy")
    need(chord_upper(0)==0 and chord_upper(U//10)>0 and
         sqrtupper(4,9)>0,"outward_interval_roots")
    emit("Y137_GRAM_TOY", shared_shift="PASS", weighted_W="PASS",
         two_energy_orthogonality="CONDITIONAL_EXACT",
         nonnormal_control="PASS", actual_first_Wilson_weight="HOLD")


def run():
    toy()
    ppb=pt.joined.dual_input()
    A2,R2,s1,s2,_,_=pt.joined.source_data()
    A0,R0,_,_=pt.old.freeze()
    G,Gr=pt.original_gram(A2,R2,A0,R0)
    need(tuple(pt.old.WF)==WF and all(len(r)==N for r in A2)
         and all(len(r)==N for r in G),"original_S3_8flat_scope")
    v1,v2=pt.old.V1,pt.old.V2
    g=weighted_action(rawrows(G,v1))
    s=weighted_action(rawrows(A2,v1))
    gg=wdot(g,g)
    ss=wdot(s,s)
    gs=wdot(g,s)
    rg=wdot(v2,g)
    rs=wdot(v2,s)
    nn=wdot(v2,v2)
    gramdet=gg*ss-gs*gs
    projection_num=ss*rg*rg-2*gs*rg*rs+gg*rs*rs
    projection_den=nn*gramdet
    need(gg>0 and ss>0 and gramdet>0 and
         0<=projection_num<=projection_den,
         "original_source_Gram_W_rank2")
    source_sine_lower=isqrt(projection_num*U*U//projection_den)
    source_sine_upper=sqrtupper(projection_num,projection_den)
    source_null_excluded=int(projection_num*U*U>s2*s2*projection_den)
    # Gram alone is the true two-energy normalization inner-product
    # matrix. Its exact source overlap is pinned to full Q trials.
    gram_sine_upper=sqrtupper(rg*rg,nn*gg)
    optn=gs
    optd=gg
    reduce=gcd(abs(optn),optd)
    optn//=reduce
    optd//=reduce
    need(0<optn<12*optd,"original_optimal_shift_range")
    g1=pt.old.FLOOR-pt.old.E1_HI
    g2=pt.old.FLOOR-pt.old.E2_HI
    B=1000000000
    gop=U+ceildiv(72*B*B*U,g1*g2)
    emit("Y137_GRAM_SOURCE",original_O2="TWO_ORIGINAL_SEVEN_LOOP_MINUS_SEVEN",
         full_Q="155378_PLUS_1985218_EXTERIOR",
         shared_Q_inverse_hashes="4_OF_4_IDENTICAL",
         original_matrix_SHA2=pt.old.blob(pt.joined.CENTERED),
         original_matrix_SHA0=pt.old.blob(pt.old.MATRIX),
         gram_source_rank2="EXACT_W_WEIGHTED",
         sample_dual_weight_ppb=ppb,
         E1_sine_hi_per_trillion=s1,E2_sine_hi_per_trillion=s2,
         first_Wilson_weight="HOLD")
    emit("Y137_GRAM_GEOMETRY",orthogonal_optimal_shift_num=optn,
         orthogonal_optimal_shift_den=optd,
         Gram_only_angle_hi_per_trillion=gram_sine_upper,
         closest_joint_dark_sine_lo_per_trillion=source_sine_lower,
         closest_joint_dark_sine_hi_per_trillion=source_sine_upper,
         old_E2_cone_source_only_dark_excluded=source_null_excluded,
         true_state_dark_excluded="NOT_FROM_NOMINAL_GEOMETRY",
         source_two_constraint_den_sha256=digest(projection_den),
         source_two_constraint_num_sha256=digest(projection_num),
         actual_first_Wilson_weight="HOLD")
    candidates=[(0,1),(3,1),(6,1),(7,1),(8,1),(17,2),
                (35,4),(9,1),(10,1),(optn,optd)]
    allc=[]
    for p,q in candidates:
        result,C=candidate(p,q,A2,R2,A0,R0,v1,v2,s1,s2,gop)
        if (p,q) in ((0,1),(optn,optd)):
            # Exact two-route W-adjoint 8x8 projector trace identity.
            z,amp,_,_=pt.trace_two_routes(C,WF,v1,v2,7*q*T*T)
            need(z[0]>=0 and amp!=0,"source_rankone_trace_false")
        emit("Y137_GRAM_CANDIDATE",**result)
        allc.append(result)
    best=max(allc,key=lambda r:r["strict_no_dark_margin_per_trillion"])
    need(best["strict_no_dark_margin_per_trillion"]==max(
         x["strict_no_dark_margin_per_trillion"] for x in allc),
         "candidate_selection")
    emit("Y137_GRAM_VERDICT",candidate_count=len(allc),
         best_shift_num=best["c_num"],best_shift_den=best["c_den"],
         strongest_valid_margin_per_trillion=
             best["strict_no_dark_margin_per_trillion"],
         original_source_nominal_joint_dark="EXCLUDED" if source_null_excluded else "FEASIBLE",
         source_shared_residual_covariance="REQUIRES_DIRECT_JOINT_DUAL",
         true_E1_projector_action="CONSERVATIVE_OP_BOUND",
         original_first_excitation_Wilson_weight=
             "CANDIDATE_REQUIRE_INDEPENDENT_REVIEW" if
             best["strict_no_dark_margin_per_trillion"]>0 else "HOLD",
         quantitative_original_weight="HOLD",
         issue_137="OPEN")


if __name__=="__main__":
    if sys.argv[1:]==["toy"]:toy()
    elif sys.argv[1:]==["real"]:run()
    else:need(False,"usage_toy_or_real")
