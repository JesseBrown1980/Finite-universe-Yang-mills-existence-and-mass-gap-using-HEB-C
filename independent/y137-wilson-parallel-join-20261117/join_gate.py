#!/usr/bin/env python3
"""#137: exact join of two INDEPENDENT original Wilson source lanes.

Input A: hosted #276 (run 44112781443) strict source-certified lower
squared ORIGINAL unshifted Wilson transition for the two exact-Q-dressed
fixed flat vectors uniformly over true physical E1/E2 energy windows.
Input B: hosted #277 (stacked on #275) Stage E source-conditional true
flat eigendirection sine bounds, and #273 full original 64-entry signed
Wilson matrix interval to bound the deflated action on two samples.

The directional-dual source lower bound is for NORMALIZED full states
with the fixed flat vectors and exact Q resolvents. Because the actual
Feshbach bilinear matrix acts on the unit FLAT components and full state
norm >= flat norm, the absolute flat-normalized sample amplitude is
at least the square root of the certified squared normalized full-sample
weight. This avoids the vacuous independent-entry signal bound.

Triangle/Cauchy on true flat eigendirections gives
 |<x2,M(E2,E1)x1>| >= c1*c2*source_amp_lower
  -s1*(zstar2+delta_M)-s2*(z1+delta_M)-s1*s2*||M||.

All arithmetic is exact integers, no float. A positive margin would be
a conditional research candidate pending independent review, never
automatically an accepted physical Wilson theorem.
"""
import os
import sys
from math import isqrt

HERE=os.path.dirname(os.path.abspath(__file__))
INDEP=os.path.dirname(HERE)
sys.path.insert(0,os.path.join(INDEP,"y137-parallel-flat-angle-fourmoment-20261117"))
import angle_transfer as stage_e
old=stage_e.old
U=1000000000000
T=1000000000000
B=1000000000
DUAL=os.path.join(HERE,"INPUT-DUAL-TRUE-WINDOW.hbp")

def need(ok,reason):
    if not ok:
        print("Y137_WILSON_JOIN_REFUSE|reason="+reason+"|json=0",flush=True)
        raise SystemExit(1)

def emit(tag,**items):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in items.items())+
          "|json=0",flush=True)

def dual_input():
    rows=open(DUAL,encoding="ascii").read().splitlines()
    need(len(rows)==4,"hosted_original_dual_receipt_rowcount")
    meta=old.parse(rows[0])
    need(rows[0].startswith("Y137_WILSON_PARALLEL_JOIN_SOURCE|")
         and meta["original_pr"]=="276"
         and meta["hosted_run"]=="44112781443"
         and meta["hosted_job"]=="134142584820"
         and meta["original_head"]=="650b915e526c2ab5cac5ad9d4043f43aeff99ae5",
         "hosted_original_Q_dual_provenance")
    one=old.parse(rows[1])
    two=old.parse(rows[2])
    three=old.parse(rows[3])
    need(rows[1].startswith("Y137_DUAL_WINDOW_SOURCE|")
         and rows[2].startswith("Y137_DUAL_WINDOW_SIGNED|")
         and rows[3].startswith("Y137_DUAL_WINDOW_VERDICT|"),
         "original_signed_dual_receipt_labels")
    need(one["original_Wilson"]=="UNSHIFTED_SEVEN_LOOP_ORBIT_MULTIPLICATION"
         and one["source_Q"]=="155378"
         and one["source_exterior"]=="1985218"
         and one["original_fixed_flat_vectors"]=="PR180_TWO_EVEN_SAMPLES"
         and one["true_window_E1_lo"]=="69909429421"
         and one["true_window_E1_hi"]=="69909586556"
         and one["true_window_E2_lo"]=="69949264147"
         and one["true_window_E2_hi"]=="69949433884"
         and one["Q_residuals"]=="ORIGINAL_S3_COMPLETE_SHELL4"
         and one["BstarB"]=="EXACT_72_IDENTITY",
         "different_original_source_or_physical_energy_windows")
    need(int(two["all_true_energy_window_signed_margin_scaled"])>0
         and two["original_directional_positive"]=="1",
         "dual_margin_nonpositive")
    need(three["fixed_flat_two_true_energy_windows"]=="POSITIVE"
         and three["actual_first_excitation_Wilson_weight"]=="HOLD"
         and three["issue_137"]=="OPEN"
         and three["original_fixed_flat_not_exact_eigenprojector"]=="ENFORCED",
         "dual_attempt_to_promote_true_Wilson")
    weight=int(three["original_Wilson_fixed_flat_full_Q_weight_ppb_lower"])
    need(weight==1027970 and 0<weight<14*14*1000000000,
         "source_certified_fixed_flat_weight_regression")
    return weight

def source_data():
    stage_e.source()
    A,R,old1,old2=old.freeze()
    s1,fac1,gap1=stage_e.transfer(stage_e.STAGE_E_PER_TRILLION[0],0)
    s2,fac2,gap2=stage_e.transfer(stage_e.STAGE_E_PER_TRILLION[1],1)
    need(s1<old1 and s2<old2 and s1>0 and s2>0,
         "Stage_E_flat_angle_not_improved")
    return A,R,s1,s2,fac1,fac2

def derived(A,R,s1,s2,ppb):
    n1,n2=old.wnorm(old.V1),old.wnorm(old.V2)
    need(n1>0 and n2>0,"original_W_flat_sample_norm")
    rows1=[sum(A[i][j]*old.V1[j] for j in range(8))
           for i in range(8)]
    cols2=[sum(A[i][j]*old.V2[i] for i in range(8))
           for j in range(8)]
    amp=sum(old.V2[i]*rows1[i] for i in range(8))
    z1_num=n2*sum((6//old.WF[i])*rows1[i]*rows1[i]
                 for i in range(8))-6*amp*amp
    z2_num=n1*sum((6//old.WF[j])*cols2[j]*cols2[j]
                 for j in range(8))-6*amp*amp
    den=6*n1*n2*T*T*T*T
    need(z1_num>=0 and z2_num>=0,
         "source_W_flat_projected_action_PSD")
    z1=old.sqrt_upper_scaled(z1_num,den)
    z2=old.sqrt_upper_scaled(z2_num,den)
    raw=sum((36//(old.WF[i]*old.WF[j]))*R[i][j]*R[i][j]
            for i in range(8) for j in range(8))
    err=old.sqrt_upper_scaled(raw,36*T*T*T*T)
    gamma1=old.FLOOR-old.E1_HI
    gamma2=old.FLOOR-old.E2_HI
    need(gamma1>0 and gamma2>0,"whole_Q_floor_energy_order")
    op=14*U+old.ceildiv(14*72*B*B*U,gamma1*gamma2)
    c1=isqrt(U*U-s1*s1)
    c2=isqrt(U*U-s2*s2)
    need(c1>0 and c2>0,"flat_cosine_nonpositive")
    # Guaranteed source lower for fixed flat vectors at true windows:
    # |<v2,Mv1>| /(||v1|| ||v2||) >=
    # |<full2,O full1>| /(||full1|| ||full2||) > sqrt(ppb/10^9).
    sample_lo=isqrt(ppb*U*U//1000000000)
    need(sample_lo>0,"source_fixed_direction_amplitude_not_positive")
    signal=sample_lo*c1*c2//(U*U)
    C=old.ceildiv(s1*(z2+err),U)
    C+=old.ceildiv(s2*(z1+err),U)
    C+=old.ceildiv(s1*s2*op,U*U)
    margin=signal-C
    need(C>=0 and signal>0 and sample_lo<=14*U,
         "strict_original_Wilson_sample_source_bound_invalid")
    # The signed margin must decrease if the E2 angular upper bound
    # increases while all fixed source terms are unchanged.
    s2_big=s2+1
    c2_big=isqrt(U*U-s2_big*s2_big)
    test_sig=sample_lo*c1*c2_big//(U*U)
    test_C=old.ceildiv(s1*(z2+err),U)
    test_C+=old.ceildiv(s2_big*(z1+err),U)
    test_C+=old.ceildiv(s1*s2_big*op,U*U)
    need(test_sig-test_C<=margin,
         "false_control_larger_eigen_angle_improves_result")
    emit("Y137_WILSON_JOIN_INPUT",
         original_source_dual="PR276_HOSTED_ACCEPTED_FIXED_FLAT_TRUE_WINDOWS",
         original_full_Q_dual_weight_ppb_floor=ppb,
         source_stage_E="PR234_SOURCE_CONDITIONAL_SIGNED_MU3",
         source_flat_angle="PR277_STAGE_E_PROJECTION",
         source_original_M="PR273_HOSTED_64_ENTRIES",
         E1_sine_per_trillion=s1,E2_sine_per_trillion=s2,
         sample_positive_amplitude_lower_per_trillion=sample_lo)
    emit("Y137_WILSON_JOIN_BUDGET",
         deflated_Mu1_upper_per_trillion=z1,
         deflated_Mstaru2_upper_per_trillion=z2,
         full_Q_matrix_entry_inflation_per_trillion=err,
         effective_operator_norm_upper_per_trillion=op,
         signal_lower_per_trillion=signal,
         full_contamination_upper_per_trillion=C,
         strict_signed_margin_per_trillion=margin,
         angular_false_control="PASS")
    emit("Y137_WILSON_JOIN_VERDICT",
         original_fixed_flat_transition="POSITIVE_SOURCE_CONDITIONAL",
         projector_transfer=
           "CANDIDATE_FOR_INDEPENDENT_REVIEW" if margin>0 else "HOLD",
         physical_full_state_normalization="NEEDS_INDEPENDENT_ACCEPTANCE",
         actual_first_excitation_Wilson_weight="HOLD",
         issue_137="OPEN")
    return margin

def toy():
    U0=U
    s1=U0//100
    s2=U0//100
    m=isqrt(U0*U0-s1*s1)
    sig=(U0//20)*m*m//(U0*U0)
    penalty=2*(U0//100)*(U0//100)//U0
    need(sig>penalty and isqrt(1027970*U0*U0//1000000000)>0,
         "positive_source_min_with_small_angles_toy")
    need(old.sqrtceil(15)==4 and old.ceildiv(7,3)==3,
         "integer_outward_toy")
    emit("Y137_WILSON_JOIN_TOY",
         positive_small_angle="PASS",
         false_positive_at_real_source="NOT_ASSUMED",
         integer_only="PASS",actual_Wilson_weight="HOLD")

if __name__=="__main__":
    if sys.argv[1:]==["toy"]:
        toy()
    elif sys.argv[1:]==["real"]:
        toy()
        ppb=dual_input()
        A,R,s1,s2,f1,f2=source_data()
        derived(A,R,s1,s2,ppb)
    else:need(False,"usage_toy_or_real")
