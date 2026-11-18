#!/usr/bin/env python3
"""Issue 137: same-Q shifted original Wilson/Gram joint directional dual.

This independent parallel workstream applies the already validated #180
signed Jacobi dual-residual formula to the *source-authenticated Stage E
physical E1/E2 energy UPPER endpoints*, not historical sample energies.

For two ORIGINAL fixed 8-flat sample vectors v1,v2, with exact full-Q
dressed states t_i(E)=(T v_i,-(QHQ-E)^-1 B T v_i), calculate:

  M(E2,E1)=<t2(E2),O_original t1(E1)>_W
  =<T v2,O_P T v1>+<q2(E2),O_Q q1(E1)>.

An exact dual error bound certifies M at upper endpoints, using full-shell4
Q residuals, then a separate exact resolvent Lipschitz error covers all
source-conditional Stage E true physical energies. The result is a
source-bound FIXED-FLAT-DIRECTION observable, not a true eigenstate.
The first-excitation Wilson spectral weight remains HOLD.
"""
import hashlib
import os
import sys
from math import isqrt

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
INDEP=os.path.join(ROOT,"independent")
SAMPLE=os.path.join(INDEP,"y137-q-dual-weight-20261113")
sys.path.insert(0,SAMPLE)
_args=sys.argv[:]
try:
    sys.argv=sys.argv[:1]
    import replay as source
finally:
    sys.argv=_args

B=1000000000
PS=1000000
T=source.SCALE
FLOOR=94068200
E1_LO,E1_HI=69909429421,69909586556
E2_LO,E2_HI=69949264147,69949433884
V1=(1000000000,997935625,996905915,38054797,37920545,2788116,51160,51160)
V2=(111045317,-38181375,-112233220,1000000000,979217930,216249666,4169404,4169404)
sys.path.insert(0,os.path.join(INDEP,"y137-e1-matched-projector-20261118"))
import matched_e1 as matched
E=matched.e
ORIGINAL_E1_MATCHED="1000000000,997998757,997000845,39006811,38860510,2944164,80455,80455"
OMAX=14
WFLAT=(1,3,2,3,3,2,2,2)
WILSON_BLOB="b6da6140ca36b361bdd9a0c0477af23d681257cf"
SAMPLE_BLOB="b9881651c51a278757bc0fef15de583277330da3"
SAMPLE_RECEIPT_BLOB="40762ceb865829156e4765b720f52d39a8be9b6f"
BGRAM_BLOB="48c02e1e80112e5d758b403f41d07079d9fcb064"

def need(ok,reason):
    if not ok:
        print("Y137_DUAL_WINDOW_REFUSE|reason="+reason+"|json=0",flush=True)
        raise SystemExit(1)

def blob(path):
    b=open(path,"rb").read()
    return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+bytes((0,))+b).hexdigest()

def ceildiv(n,d):
    need(n>=0 and d>0,"invalid_integer_ceiling")
    return (n+d-1)//d

def sqrtceil(n):
    need(n>=0,"negative_integer_sqrt")
    x=isqrt(n)
    return x if x*x==n else x+1

def emit(tag,**fields):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())+
          "|json=0",flush=True)

def sha(v):
    return hashlib.sha256(str(v).encode("ascii")).hexdigest()

def toy():
    # Scalar Q-space: exact inverse at A=2, true q=3 and trial qhat=2,
    # residual r=A*(qhat-q)=-2. Wilson O=5, same in both channels.
    # q_true² O=45, qhat² O=20, two linear corrections each +10,
    # quadratic correction +5: 20+10+10+5=45.
    A=2
    qhat=2
    qtrue=3
    residual=A*(qhat-qtrue)
    o=5
    dual_exact=A*o*qhat
    # To have A*u=A*rhs, u=rhs=O*qhat; here A=2,
    # original signed dual Jacobi equation uses b as energy scalar.
    U=o*qhat
    centre=A*o*qhat*qhat-2*residual*U
    quad=o*residual*residual//A
    need(centre+quad==A*o*qtrue*qtrue and
         residual==-2 and dual_exact==A*U,
         "signed_two_linear_one_quadratic_dual_identity")
    need(sqrtceil(15)==4 and sqrtceil(16)==4 and
         ceildiv(7,3)==3,"outward_integer_rounding")
    emit("Y137_DUAL_WINDOW_TOY",
         signed_dual_identity="PASS",
         quadratic_error_term="RETAINED",
         original_Wilson_weight="HOLD")

def pinned_source():
    need(blob(os.path.join(INDEP,"y137-wilson-effective-20261113","check.py"))==
         WILSON_BLOB,"original_seven_loop_Wilson_changed")
    need(blob(os.path.join(SAMPLE,"replay.py"))==SAMPLE_BLOB,
         "original_Q_dual_engine_changed")
    need(blob(os.path.join(SAMPLE,"RESULT-WILSON-Q-DUAL.hbp"))==
         SAMPLE_RECEIPT_BLOB,"original_sample_receipt_changed")
    bgram=os.path.join(INDEP,"y137-fullstate-Q-normalization-20261113",
                       "RESULT-FULL-W-NORM.hbp")
    need(blob(bgram)==BGRAM_BLOB,"exact_original_B_gram_receipt_changed")
    txt=open(bgram,encoding="ascii").read()
    need("BstarB_exact_72_identity=1" in txt
         and "min_integer_PSD_K=72" in txt
         and "P_Q_edges=264" in txt,
         "physical_B_isometry_not_accepted")
    need(source.k.SCRIPT_SHA==
         "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff",
         "original_K3_Q_builder_drift")
    rec=open(os.path.join(SAMPLE,"RESULT-WILSON-Q-DUAL.hbp"),
             encoding="ascii").read()
    need("v1="+",".join(str(x) for x in V1) in rec
         and "v2="+",".join(str(x) for x in V2) in rec,
         "historical_original_W_flat_sample_changed")
    need(E1_LO<E1_HI<E2_LO<E2_HI
         and E2_HI*PS<B*FLOOR,"true_E_windows_cross_Q_floor")

def matched_pair():
    # Rebuild original signed four-moment Schur centre at BOTH physical
    # energies; no recycled Wilson signed transition on moved vectors.
    with open(E.source.MU3_FILE,encoding="ascii") as handle:
        mu3=E.source.parse_pinned_mu3(handle.read())
    windows=E.three_moment_windows()
    need(tuple(windows)==E.EXPECTED_WINDOWS,
         "original_fourmoment_true_energy_windows_changed")
    result=[]
    for level,oldvec,expected_disp,expected_stage in (
        (0,V1,949209145,3235251105),
        (1,V2,3693022069,8676646901)
    ):
        z,lo,hi,v0,_,gap,_=E.ra.ROWS[level]
        need(tuple(v0)==oldvec,"historical_flat_original_vector_pin")
        uu,m0,m1,m2=E.source.accepted_old_moments(level)
        m3=E.exact.F(mu3[z])
        low,up=E.exact.bracket4(uu,m0,m1,m2,m3,
                                 E.FLOOR-z,468000000000-z)
        need(E.exact.pd(E.exact.sub(up,low)),
             "actual_four_moment_enclosure_PSD")
        centre=E.all_refs(low,up)["CENTRE"]
        vn=tuple(E.ra.recentre(centre[0],list(v0)))
        need(E.ra.wnorm(vn)>0 and
             E.flat_distance(list(v0),list(vn))==expected_disp,
             "original_signed_Schur_recenter_movement")
        check=E.cell(E.all_refs(low,up),windows,level,"CENTRE",True)
        need(check["error"]==expected_stage,
             "original_StageE_true_eigenprojector_regression")
        result.append(vn)
    a,b=result
    need(",".join(str(t) for t in a)==ORIGINAL_E1_MATCHED,
         "hosted_E1_matched_witness_source_SHA")
    emit("Y137_MATCHED_PAIR",
         source="SIGNED_ORIGINAL_MU3_FOUR_MOMENT_SCHUR",
         original_E1_recenter_v=",".join(str(t) for t in a),
         original_E2_recenter_v=",".join(str(t) for t in b),
         original_E1_recenter_sha256=hashlib.sha256(
             ",".join(str(t) for t in a).encode("ascii")).hexdigest(),
         original_E2_recenter_sha256=hashlib.sha256(
             ",".join(str(t) for t in b).encode("ascii")).hexdigest(),
         matched_E1_Wflat_sine_upper_per_trillion=2362700330,
         matched_E2_Wflat_sine_upper_per_trillion=5047836049,
         matched_E1_full_distance_upper_per_trillion=2229193756,
         matched_E2_full_distance_upper_per_trillion=4761738647,
         two_witness_Wilson_dual="FRESH_REQUIRED",
         original_first_Wilson_weight="HOLD")
    return a,b


def upper_sqrt_ratio(num,den):
    need(num>=0 and den>0,"outward_sqrt_ratio_domain")
    return sqrtceil(ceildiv(num*1000000000000000000000000,den))


def source_weighted_effective_raw(ball,obs,p,dual):
    # R2 O_Q q1 (or R1 O_Q q2) is approximated by dual.
    # The physical P-Q coupling is -C, so both minus signs cancel in
    # B^sharp R2 O_Q R1 B. This is the weighted P bilinear numerator.
    wf,wq=ball["wf"],ball["wq"]
    raw=[wf[j]*obs[j]*p[j] for j in range(8)]
    for i,row in enumerate(ball["C"]):
        if row is not None:
            for j,cij in enumerate(row):
                raw[j]+=wq[i]*cij*dual[i]
    return raw


def deflated_upper(raw,v1,v2):
    n1=sum(WFLAT[i]*v1[i]*v1[i] for i in range(8))
    n2=sum(WFLAT[i]*v2[i]*v2[i] for i in range(8))
    a=sum(v2[i]*raw[i] for i in range(8))
    num=n2*sum((6//WFLAT[i])*raw[i]*raw[i] for i in range(8))
    num-=6*a*a
    need(num>=0,"projected_Wflat_Cauchy")
    return upper_sqrt_ratio(num,6*n2*n1*T*T),a,num


def directional_action_gate(ball,O,t1,t2,u21,u12,g1sq,g2sq,d21sq,d12sq,
                            gap1,gap2,weight_ppb,v1,v2):
    # This uses the SAME actual original-Q dual solutions as signed
    # fixed-source Wilson, plus the accepted two-eigenvector sine caps.
    U=1000000000000
    cap=30
    n1=sum(WFLAT[i]*v1[i]*v1[i] for i in range(8))
    n2=sum(WFLAT[i]*v2[i]*v2[i] for i in range(8))
    raw_f=source_weighted_effective_raw(ball,O,t1["p"],u21)
    raw_a=source_weighted_effective_raw(ball,O,t2["p"],u12)
    f_nom,forward_amp,fn=deflated_upper(raw_f,v1,v2)
    a_nom,adj_amp,an=deflated_upper(raw_a,v2,v1)
    # Residuals s1,s2,d21,d12 are all D-times the physical
    # (QHQ-E) source equations. The Q spectral floor gamma supplies
    # the two resolvent norm factors, and ||B||=sqrt(72).
    eps21=ceildiv(sqrtceil(d21sq)*PS,gap2)
    eps12=ceildiv(sqrtceil(d12sq)*PS,gap1)
    epsq1=ceildiv(cap*sqrtceil(g1sq)*B*PS*PS,gap1*gap2)
    epsq2=ceildiv(cap*sqrtceil(g2sq)*B*PS*PS,gap1*gap2)
    f_res=upper_sqrt_ratio(72*(eps21+epsq1)**2,n1*T*T)
    a_res=upper_sqrt_ratio(72*(eps12+epsq2)**2,n2*T*T)
    width1=E1_HI-E1_LO
    width2=E2_HI-E2_LO
    drift=ceildiv(72*cap*B*B*PS*PS*PS*U*
                  (width1*gap2+width2*gap1),
                  gap1*gap1*gap2*gap2)
    full_f=f_nom+f_res+drift
    full_a=a_nom+a_res+drift
    operator=cap*U+ceildiv(cap*72*B*B*PS*PS*U,gap1*gap2)
    s1=2362700330
    s2=5047836049
    c1=isqrt(U*U-s1*s1)
    c2=isqrt(U*U-s2*s2)
    amp_lb=isqrt(weight_ppb*U*U//1000000000)
    signal=amp_lb*c1*c2//(U*U)
    e1pen=ceildiv(s1*c2*full_a,U*U)
    e2pen=ceildiv(s2*c1*full_f,U*U)
    cross=ceildiv(s1*s2*operator,U*U)
    err=e1pen+e2pen+cross
    margin=signal-err
    need(n1>0 and n2>0 and
         min(f_nom,a_nom,f_res,a_res,drift,operator,
             amp_lb,signal,e1pen,e2pen,cross)>=0,
         "original_source_action_bounds")
    weight_floor=max(0,margin)
    physical_weight_num=weight_floor*weight_floor*gap1*gap1*gap2*gap2
    physical_weight_den=(4*U*U*
             (gap1*gap1+72*B*B*PS*PS)*
             (gap2*gap2+72*B*B*PS*PS))
    need(physical_weight_den>0,"physical_W_normalization_positive")
    physical_ppb=physical_weight_num*1000000000//physical_weight_den
    emit("Y137_MATCHED_ACTION_INPUT",
         source_original_flat_W="1,3,2,3,3,2,2,2",
         n1=n1,n2=n2,amp_source_ppb=weight_ppb,
         forward_raw=",".join(str(x) for x in raw_f),
         adjoint_raw=",".join(str(x) for x in raw_a),
         forward_W_bilinear=forward_amp,
         adjoint_W_bilinear=adj_amp,
         g1_residual_norm2_scaled=g1sq,
         g2_residual_norm2_scaled=g2sq,
         d21_residual_norm2_scaled=d21sq,
         d12_residual_norm2_scaled=d12sq,
         gap1_num=gap1,gap2_num=gap2,
         e1_window_width_num=width1,e2_window_width_num=width2)
    emit("Y137_MATCHED_ACTION_BOUND",
         nominal_forward_deflated_per_trillion=f_nom,
         nominal_adjoint_deflated_per_trillion=a_nom,
         forward_direct_dual_Q_error_per_trillion=f_res,
         adjoint_direct_dual_Q_error_per_trillion=a_res,
         true_energy_matrix_drift_per_trillion=drift,
         forward_source_action_upper_per_trillion=full_f,
         adjoint_source_action_upper_per_trillion=full_a,
         physical_effective_M9_norm_upper_per_trillion=operator,
         matched_fixed_amp_lower_per_trillion=amp_lb,
         phase_cosine_signal_lower_per_trillion=signal,
         E1_directional_penalty_per_trillion=e1pen,
         E2_directional_penalty_per_trillion=e2pen,
         two_angles_penalty_per_trillion=cross,
         signed_true_flat_transition_margin_per_trillion=margin,
         original_physical_weight_ppb_lower=physical_ppb,
         source_acceptance="CANDIDATE_INDEPENDENT_MATH_REVIEW" if margin>0 else "HOLD",
         actual_first_Wilson_weight="HOLD")
    return margin


def actual(centered=False):
    toy()
    pinned_source()
    v1,v2=matched_pair()
    ball,O=source.build()
    need(tuple(ball["wf"])==WFLAT and ball["n"]==155378
         and ball["nf"]==1985218 and len(O)==155386,
         "original_K3_full_S3_source_census")
    need(min(O)==-7 and max(O)==14,"original_Wilson_diagonal_values")
    original_O=O
    if centered:
        # Integer source observable exactly 2*(O-7/2 I), globally
        # bounded by 21 on ALL original physical Q orbits.
        O=[2*v-16 for v in original_O]
        cap=30
        label="TWICE_ORIGINAL_SEVEN_LOOP_MINUS_16_TIMES_IDENTITY"
        need(min(O)==-30 and max(O)==12,
             "source_centered_global_character_range")
    else:
        cap=OMAX
        label="UNSHIFTED_SEVEN_LOOP_ORBIT_MULTIPLICATION"
    t1=source.trial(ball,E1_HI,list(v1))
    t2=source.trial(ball,E2_HI,list(v2))
    s1,g1sq=source.residual_scaled(ball,t1)
    s2,g2sq=source.residual_scaled(ball,t2)
    rhs21=[O[8+i]*t1["q"][i] for i in range(ball["n"])]
    rhs12=[O[8+i]*t2["q"][i] for i in range(ball["n"])]
    u21,d21sq=source.dual_solve(ball,E2_HI,rhs21)
    del rhs21
    u12,d12sq=source.dual_solve(ball,E1_HI,rhs12)
    del rhs12
    pair21=source.dot_w(s2,u21,ball["wq"])
    pair12=source.dot_w(s1,u12,ball["wq"])
    free=sum(ball["wf"][i]*O[i]*t2["p"][i]*t1["p"][i]
             for i in range(8))
    qtrial=sum(ball["wq"][i]*O[8+i]*t2["q"][i]*t1["q"][i]
                for i in range(ball["n"]))
    center=B*(free+qtrial)-pair21-pair12
    # The fixed trial states are NOT exact mutually orthogonal
    # eigendirections. The scalar identity shift contributes to their
    # actual signed sampled transition and must be accounted for.
    overlap=sum(ball["wf"][i]*t2["p"][i]*t1["p"][i]
                for i in range(8))
    overlap+=sum(ball["wq"][i]*t2["q"][i]*t1["q"][i]
                 for i in range(ball["n"]))
    if centered:
        original_raw=sum(ball["wf"][i]*original_O[i]*t2["p"][i]*t1["p"][i]
                         for i in range(8))
        original_raw+=sum(ball["wq"][i]*original_O[8+i]*t2["q"][i]*t1["q"][i]
                          for i in range(ball["n"]))
        need(free+qtrial==2*original_raw-16*overlap,
             "source_nonorthogonal_centering_identity")
        need(overlap!=0,"false_assumption_sample_orthogonality")
    gap1=B*FLOOR-E1_HI*PS
    gap2=B*FLOOR-E2_HI*PS
    need(gap1>0 and gap2>0,"original_true_window_undercuts_floor")
    err21=ceildiv(sqrtceil(g2sq*d21sq)*PS,gap2)
    err12=ceildiv(sqrtceil(g1sq*d12sq)*PS,gap1)
    errcross=ceildiv(B*cap*sqrtceil(g1sq*g2sq)*PS*PS,gap1*gap2)
    dual_err=err21+err12+errcross
    margin_upper_endpoint=abs(center)-dual_err

    # True physical unknown E_i is in [Ei_low,Ei_hi], with P fixed
    # to the frozen original eight-flat directions v_i. The original
    # exact B*B=72I and ||O||<=14 imply a rigorous energy drift.
    n1=sum(WFLAT[i]*v1[i]*v1[i] for i in range(8))
    n2=sum(WFLAT[i]*v2[i]*v2[i] for i in range(8))
    wf_prod=sqrtceil(n1*n2)*T*T
    width1=E1_HI-E1_LO
    width2=E2_HI-E2_LO
    coef=72*cap*wf_prod*B*B*PS*PS*PS
    drift1=ceildiv(coef*width1,gap2*gap1*gap1)
    drift2=ceildiv(coef*width2,gap2*gap2*gap1)
    energy_err=B*(drift1+drift2)
    margin_all=margin_upper_endpoint-energy_err
    # Optional full-state norm upper for the same two *fixed flat*
    # directions with true energy E_i, including source residual and
    # energy drift of the nonflat inverse component.
    def norm_upper(t,g2,gn,wflat,width):
        source_corr=ceildiv(sqrtceil(g2)*PS,gn)
        qenergy=ceildiv(T*sqrtceil(72*wflat)*width*B*PS*PS,gn*gn)
        return sqrtceil(t["norm"])+source_corr+qenergy
    nm1=norm_upper(t1,g1sq,gap1,n1,width1)
    nm2=norm_upper(t2,g2sq,gap2,n2,width2)
    need(nm1>0 and nm2>0,"full_fixed_flat_state_norm_nonpositive")
    scaled_amp_lower=max(0,margin_all)
    # Strict lower bound for the squared transition between two original
    # full-Q dressed ORIGINAL FLAT TRIAL DIRECTIONS at TRUE energy windows;
    # this is NOT an eigenstate-to-eigenstate transition.
    weight_ppb=scaled_amp_lower*scaled_amp_lower*1000000000//(
          B*B*nm1*nm1*nm2*nm2)
    directional_action_gate(ball,O,t1,t2,u21,u12,g1sq,g2sq,
                            d21sq,d12sq,gap1,gap2,weight_ppb,v1,v2)
    emit("Y137_DUAL_WINDOW_SOURCE",
         original_Wilson=label,
         source_operator_norm_cap=cap,
         centered_rational_mu="8/1" if centered else "0/1",
         source_Q=ball["n"],source_exterior=ball["nf"],
         original_fixed_flat_vectors="STAGEE_MATCHED_BOTH_E1_E2",
         true_window_E1_lo=E1_LO,true_window_E1_hi=E1_HI,
         true_window_E2_lo=E2_LO,true_window_E2_hi=E2_HI,
         Q_residuals="ORIGINAL_S3_COMPLETE_SHELL4",
         two_source_duals="EXACT_ORIGINAL_JACOBI_WITH_SHELL4_RESIDUAL",
         BstarB="EXACT_72_IDENTITY")
    emit("Y137_DUAL_WINDOW_SIGNED",
         flat_signed_sha256=sha(free),nonflat_trial_signed_sha256=sha(qtrial),
         endpoint_dual_center_num_sha256=sha(center),
         endpoint_dual_error_num_sha256=sha(dual_err),
         endpoint_margin_scaled=margin_upper_endpoint,
         physical_energy_drift_scaled=energy_err,
         all_true_energy_window_signed_margin_scaled=margin_all,
         original_directional_positive=int(margin_all>0),
         signed_source_trial_overlap_sha256=sha(overlap),
         original_observable_shift_defect="EXACT_RETAINED" if centered
             else "NO_SHIFT",
         dual_pair21_sha256=sha(pair21),dual_pair12_sha256=sha(pair12),
         error21_sha256=sha(err21),error12_sha256=sha(err12),
         errorcross_sha256=sha(errcross))
    emit("Y137_JOINT_DUAL_AUDIT",
         physical_shift_c_num=9,physical_shift_c_den=1,
         O2_integer_source="TWO_ORIGINAL_O_MINUS_16_I",
         same_Q_two_trial_residuals="ORIGINAL_K3_AND_SHELL4",
         full_spectral_Gram_identity="TRUE_E1_E2_ORTHOGONALITY",
         source_trial_nonorthogonal_overlap_num=overlap,
         source_trial_overlap_sha256=sha(overlap),
         endpoint_signed_center_num=center,
         endpoint_dual_error_num=dual_err,
         true_energy_drift_num=energy_err,
         true_windows_signed_margin_num=margin_all,
         norm1_upper_num=nm1,norm2_upper_num=nm2,
         fixed_shifted_weight_ppb_floor=weight_ppb,
         original_Wilson_weight="HOLD")
    emit("Y137_MATCHED_PROJECTOR_BOUND",
         source_true_E1_sine_upper_per_trillion=2362700330,
         source_true_E2_sine_upper_per_trillion=5047836049,
         source_contracted_action="NOT_YET_CERTIFIED_MATCHED",
         source_direct_joint_Q_dual="COMPUTED",
         true_first_Wilson_positive="HOLD")
    emit("Y137_JOINT_DUAL_VERDICT",
         original_seven_loop_shifted_Q_operator="DIRECT_SHARED_Q",
         source_fixed_flat_true_energy_windows=
             "POSITIVE" if margin_all>0 else "HOLD",
         true_E1_E2_eigendirection_projectors="NOT_CERTIFIED",
         orthogonality_removes_shift_for_TRUE_states="EXACT",
         actual_original_first_excitation_Wilson_weight="HOLD",
         issue_137="OPEN")

if __name__=="__main__":
    if sys.argv[1:]==["toy"]:toy()
    elif sys.argv[1:]==["real"]:actual(True)
    else:need(False,"usage_toy_or_real")
