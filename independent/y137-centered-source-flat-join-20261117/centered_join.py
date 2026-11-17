#!/usr/bin/env python3
"""#137: source-original centred Wilson dual and true-flat exact join.

Input A: hosted PR #281 (run 44119924916) strict full-Q source
lower squared transition for INTEGER O2=2*O-7I on the two
original fixed flat directions, uniformly over physical E1/E2 windows.
Input B: hosted PR #277 Stage E source-conditional true flat
eigendirection sine bounds, and PR #282's original 64-entry
CENTERED O8 signed source intervals (denominator 2*T*T).
This verifier multiplies those interval values by TWO and contracts
the integer O2 matrix with its matched O2 dual source; no mixed
unshifted/centered observable quantities are permitted.

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
DUAL=os.path.join(HERE,"INPUT-CENTERED-DUAL.hbp")
CENTERED=os.path.join(HERE,"INPUT-CENTERED-O8-64.hbp")

def need(ok,reason):
    if not ok:
        print("Y137_CENTERED_JOIN_REFUSE|reason="+reason+"|json=0",flush=True)
        raise SystemExit(1)

def emit(tag,**items):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in items.items())+
          "|json=0",flush=True)

def dual_input():
    rows=open(DUAL,encoding="ascii").read().splitlines()
    need(len(rows)==4,"frozen_centered_original_dual_rowcount")
    meta=old.parse(rows[0])
    need(rows[0].startswith("Y137_CENTERED_DUAL_JOIN_SOURCE|")
         and meta["pr"]=="281"
         and meta["run"]=="44119924916"
         and meta["job"]=="134168147605"
         and meta["source_head"]=="e0f7563eed891507d9778aa96423c2af7a04dae2",
         "original_centered_dual_source_provenance")
    one=old.parse(rows[1])
    two=old.parse(rows[2])
    verdict=old.parse(rows[3])
    need(rows[1].startswith("Y137_DUAL_WINDOW_SOURCE|")
         and rows[2].startswith("Y137_DUAL_WINDOW_SIGNED|")
         and rows[3].startswith("Y137_DUAL_WINDOW_VERDICT|"),
         "original_centered_dual_receipt_label")
    need(one["original_Wilson"]=="TWICE_ORIGINAL_CENTERED_SEVEN_LOOP_O_MINUS_7_OVER_2"
         and one["source_operator_norm_cap"]=="21"
         and one["centered_rational_mu"]=="7/2"
         and one["source_Q"]=="155378"
         and one["source_exterior"]=="1985218"
         and one["true_window_E1_lo"]=="69909429421"
         and one["true_window_E1_hi"]=="69909586556"
         and one["true_window_E2_lo"]=="69949264147"
         and one["true_window_E2_hi"]=="69949433884",
         "different_original_centered_source_or_energy_windows")
    need(two["original_directional_positive"]=="1"
         and two["original_observable_shift_defect"]=="EXACT_RETAINED"
         and int(two["all_true_energy_window_signed_margin_scaled"])>0,
         "centered_original_dual_source_margin_invalid")
    need(verdict["fixed_flat_two_true_energy_windows"]=="POSITIVE"
         and verdict["true_eigenstate_centering_invariant"]=="YES_EXACT_ORTHOGONALITY"
         and verdict["actual_first_excitation_Wilson_weight"]=="HOLD",
         "centered_source_promoted_without_true_eigenstate")
    floor=int(verdict["fixed_flat_two_times_centered_weight_ppb_lower"])
    need(floor==4232581
         and int(verdict["centered_fixed_flat_weight_ppb_lower"])==floor//4,
         "original_centered_dual_weight_regression")
    return floor

def source_data():
    stage_e.source()
    _,_,old1,old2=old.freeze()
    s1,fac1,_=stage_e.transfer(stage_e.STAGE_E_PER_TRILLION[0],0)
    s2,fac2,_=stage_e.transfer(stage_e.STAGE_E_PER_TRILLION[1],1)
    need(s1<old1 and s2<old2,"accepted_flat_angle_regression")
    rows=open(CENTERED,encoding="ascii").read().splitlines()
    need(len(rows)==68,"centered_original_full_Q_64_receipt_rowcount")
    meta=old.parse(rows[0])
    need(rows[0].startswith("Y137_CENTERED_O8_JOIN_SOURCE|")
         and meta["pr"]=="282"
         and meta["run"]=="44120602178"
         and meta["job"]=="134170606705",
         "original_centered_eight_matrix_hosted_provenance")
    centered=old.parse(rows[1])
    need(rows[1].startswith("Y137_O8_CENTERED_SOURCE|")
         and centered["rational_mu"]=="7/2"
         and centered["integer_observable"]=="TWO_ORIGINAL_O_MINUS_SEVEN_I"
         and centered["centered_Q_operator_norm_upper_num"]=="21"
         and centered["centered_Q_operator_norm_upper_den"]=="2",
         "wrong_original_Q_centering")
    matrix=old.parse(rows[2])
    need(rows[2].startswith("Y137_O8_MATRIX|")
         and matrix["original_E1_window"]=="69909429421:69909586556"
         and matrix["original_E2_window"]=="69949264147:69949433884"
         and matrix["full_original_Q_shell4_residuals"]=="INCLUDED"
         and matrix["Q_Wilson_two_times_centered_operator_cap_21"]=="PASS",
         "original_centered_matrix_source_or_Q_residual_drift")
    A=[[0]*8 for _ in range(8)]
    R=[[0]*8 for _ in range(8)]
    seen=set()
    for line in rows[3:-1]:
        need(line.startswith("Y137_O8_ENTRY|"),"missing_centered_original_matrix_entry")
        z=old.parse(line)
        i,j=int(z["i"]),int(z["j"])
        need(i in range(8) and j in range(8)
             and (i,j) not in seen and int(z["den"])==2*T*T,
             "original_centered_rational_matrix_denominator_mismatch")
        seen.add((i,j))
        a=int(z["approx_signed_num"])
        radius=int(z["Q_residual_radius_num"])+int(z["energy_band_radius_num"])
        need(radius>=0 and int(z["lower_signed_num"])==a-radius
             and int(z["upper_signed_num"])==a+radius,
             "original_centered_signed_rational_interval_mismatch")
        # Input matrix denominator 2*T² represents O-mu. This join
        # computes the TWICE-centered O2=2*(O-mu) matrix as A/T².
        A[i][j]=a
        R[i][j]=radius
    need(len(seen)==64,"source_full_64_entries_not_complete")
    verdict=old.parse(rows[-1])
    need(rows[-1].startswith("Y137_O8_VERDICT|")
         and verdict["entire_true_original_Oeff_8x8"]=="64_CENTERED_RATIONAL_ENTRY_INTERVALS"
         and verdict["true_normalized_first_Wilson_weight"]=="HOLD",
         "centered_eight_matrix_accepted_scope")
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
    op=21*U+old.ceildiv(21*72*B*B*U,gamma1*gamma2)
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
    need(C>=0 and signal>0 and sample_lo<=21*U,
         "strict_original_Wilson_sample_source_bound_invalid")
    # Exact monotone feasibility frontier at this FROZEN source matrix
    # and dual signal. It is a diagnostic of how much angle improvement
    # would make this particular sufficient inequality positive.
    def conditional_margin(x,y):
        cx=isqrt(U*U-x*x)
        cy=isqrt(U*U-y*y)
        lo=sample_lo*cx*cy//(U*U)
        penalty=old.ceildiv(x*(z2+err),U)
        penalty+=old.ceildiv(y*(z1+err),U)
        penalty+=old.ceildiv(x*y*op,U*U)
        return lo-penalty
    need(conditional_margin(s1,s2)==margin,
         "independent_monotone_margin_formula_mismatch")
    need(conditional_margin(s1,0)>0 and margin<=0,
         "finite_E2_angle_frontier_not_bracketed")
    low,high=0,s2
    while high-low>1:
        mid=(low+high)//2
        if conditional_margin(s1,mid)>0:
            low=mid
        else:
            high=mid
    need(conditional_margin(s1,low)>0
         and conditional_margin(s1,low+1)<=0,
         "E2_strict_frontier_not_isolated")
    joint_lo,joint_hi=0,U
    while joint_hi-joint_lo>1:
        mid=(joint_hi+joint_lo)//2
        if conditional_margin(s1*mid//U,s2*mid//U)>0:
            joint_lo=mid
        else:
            joint_hi=mid
    need(conditional_margin(s1*joint_lo//U,s2*joint_lo//U)>0
         and conditional_margin(s1*(joint_lo+1)//U,
                                s2*(joint_lo+1)//U)<=0,
         "joint_strict_angle_frontier_not_isolated")
    emit("Y137_CENTERED_JOIN_FRONTIER",
         fixed_E1_sine_upper_per_trillion=s1,
         current_E2_sine_upper_per_trillion=s2,
         sufficient_E2_sine_if_E1_unchanged_per_trillion=low,
         sufficient_equal_sine_scale_per_trillion=joint_lo,
         condition="STRONGER_EIGENDIRECTION_BOUND_REQUIRED",
         numerical_frontier="EXACT_INTEGER_ROOT_BISECTION",
         actual_first_excitation_Wilson_weight="HOLD")
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
    emit("Y137_CENTERED_JOIN_INPUT",
         original_source_dual="PR281_HOSTED_CENTERED_FIXED_FLAT_TRUE_WINDOWS",
         original_full_Q_dual_weight_ppb_floor=ppb,
         source_stage_E="PR234_SOURCE_CONDITIONAL_SIGNED_MU3",
         source_flat_angle="PR277_STAGE_E_PROJECTION",
         source_original_M="PR282_CENTERED_HOSTED_64_ENTRIES_AS_INTEGER_O2",
         E1_sine_per_trillion=s1,E2_sine_per_trillion=s2,
         sample_positive_amplitude_lower_per_trillion=sample_lo)
    emit("Y137_CENTERED_JOIN_BUDGET",
         deflated_Mu1_upper_per_trillion=z1,
         deflated_Mstaru2_upper_per_trillion=z2,
         full_Q_matrix_entry_inflation_per_trillion=err,
         effective_operator_norm_upper_per_trillion=op,
         signal_lower_per_trillion=signal,
         full_contamination_upper_per_trillion=C,
         strict_signed_margin_per_trillion=margin,
         angular_false_control="PASS")
    emit("Y137_CENTERED_JOIN_VERDICT",
         actual_original_true_transition_equals_half_centered_O2="EXACT_EIGENSTATE_ORTHOGONALITY",
         original_fixed_flat_transition="POSITIVE_SOURCE_CONDITIONAL",
         projector_transfer=
           "CANDIDATE_FOR_INDEPENDENT_REVIEW" if margin>0 else "HOLD",
         exact_full_state_normalizations="POSITIVE_FINITE_BY_Q_FLOOR",
         quantitative_normalized_weight_lower="NOT_COMPUTED",
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
    need(sig>penalty and isqrt(4232581*U0*U0//1000000000)>0,
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
