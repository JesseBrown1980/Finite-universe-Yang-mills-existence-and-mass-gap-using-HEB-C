#!/usr/bin/env python3
"""Issue 137: directional dual original-seven-loop Wilson action at true windows.

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

def actual():
    toy()
    pinned_source()
    ball,O=source.build()
    need(tuple(ball["wf"])==WFLAT and ball["n"]==155378
         and ball["nf"]==1985218 and len(O)==155386,
         "original_K3_full_S3_source_census")
    need(min(O)==-7 and max(O)==14,"original_Wilson_diagonal_values")
    t1=source.trial(ball,E1_HI,list(V1))
    t2=source.trial(ball,E2_HI,list(V2))
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
    gap1=B*FLOOR-E1_HI*PS
    gap2=B*FLOOR-E2_HI*PS
    need(gap1>0 and gap2>0,"original_true_window_undercuts_floor")
    err21=ceildiv(sqrtceil(g2sq*d21sq)*PS,gap2)
    err12=ceildiv(sqrtceil(g1sq*d12sq)*PS,gap1)
    errcross=ceildiv(B*OMAX*sqrtceil(g1sq*g2sq)*PS*PS,gap1*gap2)
    dual_err=err21+err12+errcross
    margin_upper_endpoint=abs(center)-dual_err

    # True physical unknown E_i is in [Ei_low,Ei_hi], with P fixed
    # to the frozen original eight-flat directions v_i. The original
    # exact B*B=72I and ||O||<=14 imply a rigorous energy drift.
    n1=sum(WFLAT[i]*V1[i]*V1[i] for i in range(8))
    n2=sum(WFLAT[i]*V2[i]*V2[i] for i in range(8))
    wf_prod=sqrtceil(n1*n2)*T*T
    width1=E1_HI-E1_LO
    width2=E2_HI-E2_LO
    coef=72*OMAX*wf_prod*B*B*PS*PS*PS
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
    emit("Y137_DUAL_WINDOW_SOURCE",
         original_Wilson="UNSHIFTED_SEVEN_LOOP_ORBIT_MULTIPLICATION",
         source_Q=ball["n"],source_exterior=ball["nf"],
         original_fixed_flat_vectors="PR180_TWO_EVEN_SAMPLES",
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
         dual_pair21_sha256=sha(pair21),dual_pair12_sha256=sha(pair12),
         error21_sha256=sha(err21),error12_sha256=sha(err12),
         errorcross_sha256=sha(errcross))
    emit("Y137_DUAL_WINDOW_VERDICT",
         original_Wilson_fixed_flat_full_Q_weight_ppb_lower=weight_ppb,
         fixed_flat_two_true_energy_windows=
              "POSITIVE" if margin_all>0 else "HOLD",
         original_fixed_flat_not_exact_eigenprojector="ENFORCED",
         true_E1E2_flat_eigendirections="NOT_CERTIFIED",
         actual_first_excitation_Wilson_weight="HOLD",
         issue_137="OPEN")

if __name__=="__main__":
    if sys.argv[1:]==["toy"]:toy()
    elif sys.argv[1:]==["real"]:actual()
    else:need(False,"usage_toy_or_real")
