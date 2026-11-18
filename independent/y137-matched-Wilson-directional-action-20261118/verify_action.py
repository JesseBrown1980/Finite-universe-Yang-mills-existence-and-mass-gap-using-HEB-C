#!/usr/bin/env python3
"""Independent integer replay of original matched Wilson directional projector-action gate.

Arithmetic/receipt independence: reads HBP and reconstructs every outward
bound, 8-flat W contraction, source residual action and true-state margin.
Original physical-Q graph correctness remains separately source-certified.
"""
import sys
from math import isqrt

U=1000000000000
B=1000000000
PS=1000000
T=1000000000000
WF=(1,3,2,3,3,2,2,2)
CAP=30
S1=2362700330
S2=5047836049


def need(ok,msg):
    if not ok: raise ValueError(msg)


def intval(x):
    a=int(x)
    need(str(a)==x,"noncanonical_integer")
    return a


def ceildiv(a,b):
    need(a>=0 and b>0,"ceil_div_domain")
    return (a+b-1)//b


def ceilroot(n):
    need(n>=0,"sqrt_negative")
    a=isqrt(n)
    return a+(a*a!=n)


def upperroot(num,den):
    need(den>0 and num>=0,"squared_fraction_domain")
    return ceilroot(ceildiv(num*U*U,den))


def records(data):
    rows={}
    for line in data.splitlines():
        tag=line.split("|",1)[0]
        if tag not in ("Y137_MATCHED_PAIR","Y137_JOINT_DUAL_AUDIT",
                       "Y137_MATCHED_ACTION_INPUT","Y137_MATCHED_ACTION_BOUND",
                       "Y137_MATCHED_ACTION_GRAPH"):
            continue
        need(tag not in rows,"duplicate_action_row")
        row={}
        for part in line.split("|")[1:]:
            k,sep,v=part.partition("=")
            need(k and sep and k not in row,"malformed_HBP")
            row[k]=v
        need(row.pop("json",None)=="0","bad_HBP_end")
        rows[tag]=row
    need(len(rows)==5,"missing_original_source_action_inputs")
    return rows


def vector(v):
    arr=tuple(intval(x) for x in v.split(","))
    need(len(arr)==8,"invalid_flat_vector_dimension")
    return arr


def verify(data):
    r=records(data)
    pair=r["Y137_MATCHED_PAIR"]
    v1=vector(pair["original_E1_recenter_v"])
    v2=vector(pair["original_E2_recenter_v"])
    need(v1==(1000000000,997998757,997000845,39006811,38860510,2944164,80455,80455) and
         v2==(112491544,-39124838,-114340075,1000000000,978089453,221700078,5301152,5301152),
         "original_matched_signed_source_vector_pin")
    for k,val in (("matched_E1_Wflat_sine_upper_per_trillion",S1),
                  ("matched_E2_Wflat_sine_upper_per_trillion",S2)):
        need(intval(pair[k])==val,"signed_mu3_projector_accepted_sine")
    graph=r["Y137_MATCHED_ACTION_GRAPH"]
    need(graph=={
        "original_PQ_edges":"264",
        "matched_E1_forward_independent_flat_row":"PASS",
        "matched_E2_adjoint_independent_flat_row":"PASS",
        "physical_weighted_PQ_adjoint":"PASS",
        "first_original_Wilson_weight":"HOLD"},
        "original_264_weighted_PQ_graph_crossroute")
    src=r["Y137_JOINT_DUAL_AUDIT"]
    inp=r["Y137_MATCHED_ACTION_INPUT"]
    bound=r["Y137_MATCHED_ACTION_BOUND"]
    need(inp["source_original_flat_W"]=="1,3,2,3,3,2,2,2","physical_orbit_W")
    n1=sum(WF[i]*v1[i]*v1[i] for i in range(8))
    n2=sum(WF[i]*v2[i]*v2[i] for i in range(8))
    ppb=intval(src["fixed_shifted_weight_ppb_floor"])
    need(ppb>=0 and intval(inp["n1"])==n1 and intval(inp["n2"])==n2 and
         intval(inp["amp_source_ppb"])==ppb,"source_flat_norm_and_margin")
    raw1=vector(inp["forward_raw"])
    raw2=vector(inp["adjoint_raw"])
    val1=sum(v2[i]*raw1[i] for i in range(8))
    val2=sum(v1[i]*raw2[i] for i in range(8))
    need(intval(inp["forward_W_bilinear"])==val1 and
         intval(inp["adjoint_W_bilinear"])==val2,
         "weighted_coupling_bilinears")
    fnum=n2*sum((6//WF[i])*raw1[i]*raw1[i] for i in range(8))-6*val1*val1
    anum=n1*sum((6//WF[i])*raw2[i]*raw2[i] for i in range(8))-6*val2*val2
    need(fnum>=0 and anum>=0,"weighted_deflated_projection_Cauchy")
    f_nom=upperroot(fnum,6*n2*n1*T*T)
    a_nom=upperroot(anum,6*n1*n2*T*T)
    g1,g2,d21,d12=(intval(inp[x]) for x in (
        "g1_residual_norm2_scaled","g2_residual_norm2_scaled",
        "d21_residual_norm2_scaled","d12_residual_norm2_scaled"))
    need(min(g1,g2,d21,d12)>=0,"source_residual_norm2_nonnegative")
    gap1=intval(inp["gap1_num"]);gap2=intval(inp["gap2_num"])
    w1=intval(inp["e1_window_width_num"]);w2=intval(inp["e2_window_width_num"])
    need(gap1==B*94068200-69909586556*PS and
         gap2==B*94068200-69949433884*PS and
         w1==69909586556-69909429421 and
         w2==69949433884-69949264147,
         "exact_source_E1_E2_true_window_and_Qfloor")
    eps21=ceildiv(ceilroot(d21)*PS,gap2)
    eps12=ceildiv(ceilroot(d12)*PS,gap1)
    epsq1=ceildiv(CAP*ceilroot(g1)*B*PS*PS,gap1*gap2)
    epsq2=ceildiv(CAP*ceilroot(g2)*B*PS*PS,gap1*gap2)
    fer=upperroot(72*(eps21+epsq1)**2,n1*T*T)
    aer=upperroot(72*(eps12+epsq2)**2,n2*T*T)
    drift=ceildiv(72*CAP*B*B*PS*PS*PS*U*
                  (w1*gap2+w2*gap1),gap1*gap1*gap2*gap2)
    ftotal=f_nom+fer+drift
    atotal=a_nom+aer+drift
    op=CAP*U+ceildiv(CAP*72*B*B*PS*PS*U,gap1*gap2)
    c1=isqrt(U*U-S1*S1);c2=isqrt(U*U-S2*S2)
    amp=isqrt(ppb*U*U//1000000000)
    sig=amp*c1*c2//(U*U)
    # Upper mixed-angle factor is one; the hosted source cosine c_i
    # is a lower bound that cannot upper-bound cross-angle errors.
    pe1=ceildiv(S1*atotal,U)
    pe2=ceildiv(S2*ftotal,U)
    cross=ceildiv(S1*S2*op,U*U)
    margin=sig-pe1-pe2-cross
    per={
       "nominal_forward_deflated_per_trillion":f_nom,
       "nominal_adjoint_deflated_per_trillion":a_nom,
       "forward_direct_dual_Q_error_per_trillion":fer,
       "adjoint_direct_dual_Q_error_per_trillion":aer,
       "true_energy_matrix_drift_per_trillion":drift,
       "forward_source_action_upper_per_trillion":ftotal,
       "adjoint_source_action_upper_per_trillion":atotal,
       "physical_effective_M9_norm_upper_per_trillion":op,
       "matched_fixed_amp_lower_per_trillion":amp,
       "phase_cosine_signal_lower_per_trillion":sig,
       "E1_directional_penalty_per_trillion":pe1,
       "E2_directional_penalty_per_trillion":pe2,
       "two_angles_penalty_per_trillion":cross,
       "signed_true_flat_transition_margin_per_trillion":margin,
    }
    for k,v in per.items():
        need(intval(bound[k])==v,"independent_outward_replay_"+k)
    physical_num=max(0,margin)**2*gap1**2*gap2**2
    physical_den=4*U*U*(gap1*gap1+72*B*B*PS*PS)*(gap2*gap2+72*B*B*PS*PS)
    ppbfloor=physical_num*1000000000//physical_den
    pptfloor=physical_num*1000000000000//physical_den
    need(intval(bound["original_physical_weight_ppt_lower"])==pptfloor and
         intval(bound["original_weight_rational_num"])==physical_num and
         intval(bound["original_weight_rational_den"])==physical_den and
         intval(bound["strict_positive_weight_rational"])==int(physical_num>0) and
         bound["mixed_projector_cosine_upper"]=="ONE_EXACT" and
         intval(bound["original_physical_weight_ppb_lower"])==ppbfloor and
         bound["source_acceptance"]==
          ("CANDIDATE_INDEPENDENT_MATH_REVIEW" if margin>0 else "HOLD") and
         bound["actual_first_Wilson_weight"]=="HOLD",
         "original_true_first_Wilson_weight_HOLD")
    return margin


def tamper(data):
    margin=verify(data)
    for a,b in (
       ("|source_original_flat_W=1,3,2,3,3,2,2,2|",
        "|source_original_flat_W=1,1,1,1,1,1,1,1|"),
       ("|forward_W_bilinear=","|forward_W_bilinear=77"),
       ("|nominal_forward_deflated_per_trillion=",
        "|nominal_forward_deflated_per_trillion=99"),
       ("|forward_direct_dual_Q_error_per_trillion=",
        "|forward_direct_dual_Q_error_per_trillion=99"),
       ("|matched_fixed_amp_lower_per_trillion=",
        "|matched_fixed_amp_lower_per_trillion=99"),
       ("|signed_true_flat_transition_margin_per_trillion=",
        "|signed_true_flat_transition_margin_per_trillion=99"),
       ("|original_physical_weight_ppt_lower=",
        "|original_physical_weight_ppt_lower=0"),
       ("|mixed_projector_cosine_upper=ONE_EXACT|",
        "|mixed_projector_cosine_upper=LOWER_COSINE|"),
       ("|matched_E2_adjoint_independent_flat_row=PASS|",
        "|matched_E2_adjoint_independent_flat_row=FAIL|"),
       ("|actual_first_Wilson_weight=HOLD|",
        "|actual_first_Wilson_weight=PASS|"),
       ("|matched_E2_Wflat_sine_upper_per_trillion=5047836049|",
        "|matched_E2_Wflat_sine_upper_per_trillion=0|")
    ):
        altered=data.replace(a,b,1)
        need(altered!=data,"adversarial_fixture_not_found")
        try: verify(altered)
        except ValueError: pass
        else: raise AssertionError("forged_original_true_action_receipt_accepted")
    print("Y137_MATCHED_ACTION_REPLAY|signed_margin="+str(margin)+
          "|tamper_controls=11_REJECTED|true_original_Wilson_weight=HOLD|json=0")


if __name__=="__main__":
    need(len(sys.argv)==2,"usage_ACTION_RESULT_HBP")
    with open(sys.argv[1],encoding="ascii") as stream: tamper(stream.read())
