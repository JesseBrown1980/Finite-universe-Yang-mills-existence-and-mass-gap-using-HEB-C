#!/usr/bin/env python3
"""Independent integer audit of source-specific O2-9G direct same-Q dual receipt.
No import of producer or the original S3 Hamiltonian implementation.
"""
import hashlib
import sys


def require(cond,why):
    if not cond:
        raise ValueError(why)


def parsed(data):
    allowed={"Y137_DUAL_WINDOW_TOY","Y137_DUAL_WINDOW_SOURCE",
             "Y137_DUAL_WINDOW_SIGNED","Y137_JOINT_DUAL_AUDIT",
             "Y137_JOINT_DUAL_VERDICT","Y137_MATCHED_PAIR","Y137_MATCHED_PROJECTOR_BOUND"}
    rows={}
    for ln in data.splitlines():
        tag=ln.split("|",1)[0]
        require(tag in allowed and tag not in rows,"unexpected_or_duplicate_row")
        z={}
        for cell in ln.split("|")[1:]:
            k,sep,v=cell.partition("=")
            require(sep and k not in z and k,"bad_kv")
            z[k]=v
        require(z.pop("json",None)=="0","bad_terminator")
        rows[tag]=z
    require(set(rows)==allowed,"missing_original_dual_receipt")
    return rows


def exact_int(x):
    y=int(x)
    require(str(y)==x,"noncanonical_int")
    return y


def sha(x):
    return hashlib.sha256(str(x).encode("ascii")).hexdigest()


def verify(data):
    r=parsed(data)
    toy=r["Y137_DUAL_WINDOW_TOY"]
    require(toy=={"signed_dual_identity":"PASS",
                  "quadratic_error_term":"RETAINED",
                  "original_Wilson_weight":"HOLD"},"toy_source")
    src=r["Y137_DUAL_WINDOW_SOURCE"]
    require(src["original_Wilson"]=="TWICE_ORIGINAL_SEVEN_LOOP_MINUS_16_TIMES_IDENTITY" and
            exact_int(src["source_operator_norm_cap"])==30 and
            src["centered_rational_mu"]=="8/1" and
            exact_int(src["source_Q"])==155378 and
            exact_int(src["source_exterior"])==1985218 and
            src["original_fixed_flat_vectors"]=="STAGEE_MATCHED_BOTH_E1_E2" and
            src["true_window_E1_lo"]=="69909429421" and
            src["true_window_E1_hi"]=="69909586556" and
            src["true_window_E2_lo"]=="69949264147" and
            src["true_window_E2_hi"]=="69949433884" and
            src["Q_residuals"]=="ORIGINAL_S3_COMPLETE_SHELL4" and
            src["two_source_duals"]=="EXACT_ORIGINAL_JACOBI_WITH_SHELL4_RESIDUAL" and
            src["BstarB"]=="EXACT_72_IDENTITY","source_physical_scope")
    pair=r["Y137_MATCHED_PAIR"]
    require(pair["source"]=="SIGNED_ORIGINAL_MU3_FOUR_MOMENT_SCHUR" and
            pair["two_witness_Wilson_dual"]=="FRESH_REQUIRED" and
            pair["original_first_Wilson_weight"]=="HOLD" and
            exact_int(pair["matched_E1_Wflat_sine_upper_per_trillion"])==2362700330 and
            exact_int(pair["matched_E2_Wflat_sine_upper_per_trillion"])==5047836049 and
            exact_int(pair["matched_E1_full_distance_upper_per_trillion"])==2229193756 and
            exact_int(pair["matched_E2_full_distance_upper_per_trillion"])==4761738647,
            "matched_source_scope")
    v1=tuple(exact_int(z) for z in pair["original_E1_recenter_v"].split(","))
    v2=tuple(exact_int(z) for z in pair["original_E2_recenter_v"].split(","))
    require(len(v1)==8 and len(v2)==8 and
            v1==(1000000000,997998757,997000845,39006811,38860510,2944164,80455,80455),
            "original_matched_E1_vector_not_sealed")
    for k,v in (("original_E1_recenter_sha256",v1),
                ("original_E2_recenter_sha256",v2)):
        require(pair[k]==hashlib.sha256(",".join(str(t) for t in v).encode("ascii")).hexdigest(),
                "matched_source_vector_sha")
    original_v2=(111045317,-38181375,-112233220,1000000000,979217930,216249666,4169404,4169404)
    W=(1,3,2,3,3,2,2,2)
    n0=sum(W[i]*original_v2[i]*original_v2[i] for i in range(8))
    n2=sum(W[i]*v2[i]*v2[i] for i in range(8))
    d=sum(W[i]*original_v2[i]*v2[i] for i in range(8))
    require(n0>0 and n2>0 and d>0 and d*d<=n0*n2 and
            0<(n0*n2-d*d)*1000000000000000000000000//(n0*n2)<10000000000**2,
            "original_matched_E2_source_relation")
    projected=r["Y137_MATCHED_PROJECTOR_BOUND"]
    require(projected=={
        "source_true_E1_sine_upper_per_trillion":"2362700330",
        "source_true_E2_sine_upper_per_trillion":"5047836049",
        "source_contracted_action":"NOT_YET_CERTIFIED_MATCHED",
        "source_direct_joint_Q_dual":"COMPUTED",
        "true_first_Wilson_positive":"HOLD"},"matched_projector_final_gate")
    aud=r["Y137_JOINT_DUAL_AUDIT"]
    require(exact_int(aud["physical_shift_c_num"])==9 and
            exact_int(aud["physical_shift_c_den"])==1 and
            aud["O2_integer_source"]=="TWO_ORIGINAL_O_MINUS_16_I" and
            aud["same_Q_two_trial_residuals"]=="ORIGINAL_K3_AND_SHELL4" and
            aud["full_spectral_Gram_identity"]=="TRUE_E1_E2_ORTHOGONALITY" and
            aud["original_Wilson_weight"]=="HOLD","shared_Q_Gram_identity")
    overlap=exact_int(aud["source_trial_nonorthogonal_overlap_num"])
    require(overlap!=0 and aud["source_trial_overlap_sha256"]==sha(overlap),
            "sample_overlap_nonzero")
    center=exact_int(aud["endpoint_signed_center_num"])
    err=exact_int(aud["endpoint_dual_error_num"])
    drift=exact_int(aud["true_energy_drift_num"])
    margin=exact_int(aud["true_windows_signed_margin_num"])
    n1=exact_int(aud["norm1_upper_num"])
    n2=exact_int(aud["norm2_upper_num"])
    ppb=exact_int(aud["fixed_shifted_weight_ppb_floor"])
    require(err>=0 and drift>=0 and n1>0 and n2>0 and
            margin==abs(center)-err-drift,"joint_same_Q_window_arithmetic")
    computed=max(0,margin)**2*1000000000//(
               1000000000000000000*n1*n1*n2*n2)
    require(computed==ppb,"shifted_original_normalized_weight")
    sig=r["Y137_DUAL_WINDOW_SIGNED"]
    require(sig["endpoint_dual_center_num_sha256"]==sha(center) and
            sig["endpoint_dual_error_num_sha256"]==sha(err) and
            exact_int(sig["endpoint_margin_scaled"])==abs(center)-err and
            exact_int(sig["physical_energy_drift_scaled"])==drift and
            exact_int(sig["all_true_energy_window_signed_margin_scaled"])==margin and
            exact_int(sig["original_directional_positive"])==int(margin>0) and
            sig["signed_source_trial_overlap_sha256"]==sha(overlap) and
            sig["original_observable_shift_defect"]=="EXACT_RETAINED",
            "dual_signed_pair")
    for k in ("dual_pair21_sha256","dual_pair12_sha256","error21_sha256",
              "error12_sha256","errorcross_sha256","flat_signed_sha256",
              "nonflat_trial_signed_sha256"):
        require(len(sig[k])==64 and all(c in "0123456789abcdef" for c in sig[k]),
                "signed_original_Q_hash")
    verdict=r["Y137_JOINT_DUAL_VERDICT"]
    require(verdict=={
        "original_seven_loop_shifted_Q_operator":"DIRECT_SHARED_Q",
        "source_fixed_flat_true_energy_windows":"POSITIVE" if margin>0 else "HOLD",
        "true_E1_E2_eigendirection_projectors":"NOT_CERTIFIED",
        "orthogonality_removes_shift_for_TRUE_states":"EXACT",
        "actual_original_first_excitation_Wilson_weight":"HOLD",
        "issue_137":"OPEN"},"scoped_true_Wilson_verdict")
    return margin,ppb


def tamper(data):
    margin,ppb=verify(data)
    for a,b in (
        ("|physical_shift_c_num=9|","|physical_shift_c_num=8|"),
        ("|source_operator_norm_cap=30|","|source_operator_norm_cap=21|"),
        ("|source_Q=155378|","|source_Q=0|"),
        ("|original_Wilson_weight=HOLD|","|original_Wilson_weight=PASS|"),
        ("|true_windows_signed_margin_num=","|true_windows_signed_margin_num=777"),
        ("|actual_original_first_excitation_Wilson_weight=HOLD|",
         "|actual_original_first_excitation_Wilson_weight=PASS|"),
        ("|original_E1_recenter_sha256=","|original_E1_recenter_sha256=bad"),
        ("|matched_E2_Wflat_sine_upper_per_trillion=5047836049|",
         "|matched_E2_Wflat_sine_upper_per_trillion=0|"),
    ):
        altered=data.replace(a,b,1)
        require(altered!=data,"bad_control")
        try:verify(altered)
        except ValueError:pass
        else:raise AssertionError("forged_receipt_accepted")
    print("Y137_JOINT_REPLAY|same_Q_dual=MATCHED_PAIR_PASS|tamper=8_REJECTED|"
          "signed_margin="+str(margin)+"|fixed_ppb="+str(ppb)+
          "|actual_original_Wilson_weight=HOLD|json=0")


if __name__=="__main__":
    require(len(sys.argv)==2,"usage_RESULT_HBP")
    with open(sys.argv[1],encoding="ascii") as f:tamper(f.read())
