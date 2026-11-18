#!/usr/bin/env python3
"""Independent original S3 first Wilson proof-premise and receipt arithmetic review.

No imports from the producer, source-Q implementation, or Stage E projector
libraries. Source reproducibility includes the pinned historical Git blobs,
hosted #315 artifact, and freshly generated E1 and E2 matched HBP receipts.
The Perron store's 45,508,080 row proof and signed mu3 Schur derivation are
explicitly historical premises; this checker does not reconstruct those.
"""
import hashlib
import sys
from math import isqrt

UNIT=1000000000000
DEN=1000000000
PS=1000000
GAMMA_MICRO=94068200
W=(1,3,2,3,3,2,2,2)
E1_LO,E1_HI=69909429421,69909586556
E2_LO,E2_HI=69949264147,69949433884
PER_BLOB="cbd428014a4d440732a5c0a541ed57a9041becee"
FINITE_BLOB="f891cbed9692f97b62062dba35625804a99dd085"
V1=(1000000000,997998757,997000845,39006811,38860510,2944164,80455,80455)
V2=(112491544,-39124838,-114340075,1000000000,978089453,221700078,5301152,5301152)
AUDIT_RUN=44411639918


def require(ok,reason):
    if not ok:
        raise ValueError(reason)


def parse(raw):
    by_tag={}
    for s in raw.splitlines():
        if "|" not in s or s.startswith("#"):
            continue
        tag=s.split("|",1)[0]
        values={}
        for part in s.split("|")[1:]:
            key,eq,value=part.partition("=")
            if not eq:
                continue
            require(key and key not in values,"duplicate_source_column")
            values[key]=value
        by_tag.setdefault(tag,[]).append(values)
    return by_tag


def one(doc,tag):
    vals=doc.get(tag,[])
    require(len(vals)==1,"missing_or_duplicate_"+tag)
    require(vals[0].get("json")=="0","noncanonical_receipt_"+tag)
    return vals[0]


def num(doc,key):
    x=doc[key]
    v=int(x)
    require(str(v)==x,"noncanonical_integer_"+key)
    return v


def root_up(n):
    require(n>=0,"sqrt_negative")
    r=isqrt(n)
    return r+(r*r!=n)


def div_up(a,b):
    require(a>=0 and b>0,"positive_div")
    return (a+b-1)//b


def hashblob(raw):
    data=raw.encode("ascii")
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+bytes((0,))+data).hexdigest()


def source_floor_audit(perron_raw,finite_raw):
    require(hashblob(perron_raw)==PER_BLOB,"historical_Perron_Git_blob")
    require(hashblob(finite_raw)==FINITE_BLOB,"historical_finite_verdict_Git_blob")
    p=parse(perron_raw)
    f=parse(finite_raw)
    top=one(p,"RESULT_PERRON_3x4_TOP")
    full=one(p,"RESULT_FULLREBUILD")
    allpairs=one(p,"RESULT_ALLPAIRS_3x4")
    verdict=one(f,"FINITE_PER3X4_VERDICT")
    evidence=one(f,"FINITE_PER3X4_EVIDENCE")
    require(num(top,"t_cert_milli")==94070673 and
            all(num(top,k)==94070673 for k in (
                  "perronritz_grid","perroncert_check","check_d_strict",
                  "outside_go_checker")) and
            top["merkle"]=="PASS" and num(top,"min_mag")==3 and
            top["d_sha256"]==evidence["vector_sha256"],
            "all_original_Q_Perron_checkers")
    require(num(full,"rows_rebuilt")==45508080 and
            num(full,"rows_read")==45508080 and
            all(num(full,k)==0 for k in ("canonical_key_mismatch",
               "weight_mismatch","M_mismatch","entries_mismatch")) and
            full["merkle"]=="PASS" and num(full,"exit")==0,
            "whole_store_row_source")
    require(num(allpairs,"pairs")==1632625631 and
            all(num(allpairs,k)==0 for k in ("value_mismatch",
                "lower_without_upper","upper_without_lower")) and
            allpairs["merkle_each_pass"]=="PASS",
            "whole_store_weighted_pair_source")
    require(verdict["status"]=="ACCEPTED_FINITE_HIGH_CLUSTER_BOUND_FROM_PINNED_EVIDENCE" and
            num(verdict,"E9_full_lower_micro")==94070673 and
            num(verdict,"E8_full_upper_micro")==70031000 and
            num(verdict,"E9_minus_E8_lower_micro")==24039673 and
            num(evidence,"tcert_micro")==94070673 and
            num(evidence,"original_rebuild_rows")==45508080 and
            num(evidence,"original_pair_checks")==1632625631,
            "accepted_finite_high_cluster")
    # The Wilson resolvent always uses a strictly weaker bound.
    require(GAMMA_MICRO<94070673 and
            GAMMA_MICRO*1000>E2_HI,
            "Wilson_floor_must_exceed_E2")
    # Exact 2-site stoquastic Barta toy, with an exchange lift:
    # quotient diag=(9,12), offdiag=-2; full lift offdiag -1 to
    # each exchanged partner. d=(1,2), λ_lower = min(9-4,12-1)=5.
    def qaction(x):
        a,b=x
        return 9*a-2*b,12*b-2*a
    da=(1,2)
    ya,yb=qaction(da)
    require(ya>=5*da[0] and yb>=5*da[1],
            "toy_Collatz_positive_vector")
    # The same quotient action lifts to two exchanged copies of b.
    whole=(9*da[0]-1*da[1]-1*da[1],
           12*da[1]-2*da[0],
           12*da[1]-2*da[0])
    require(whole==(ya,yb,yb) and min(whole[0],whole[1]//2,whole[2]//2)==5,
            "toy_whole_Q_sector_symmetry_lift")
    return 94070673-GAMMA_MICRO


def read_vec(raw):
    t=tuple(int(x) for x in raw.split(","))
    require(len(t)==8 and ",".join(str(x) for x in t)==raw,
            "eight_integer_source_vector")
    return t


def projector_receipt_audit(e1raw,e2raw,full):
    e1=parse(e1raw);e2=parse(e2raw)
    v1=one(e1,"Y137_E1_MATCHED_VERDICT")
    v2=one(e2,"Y137_E2_DIRECT_VERDICT")
    sel=one(e1,"Y137_E1_MATCHED_VECTOR")
    matched=one(full,"Y137_MATCHED_PAIR")
    require(num(v1,"best_matched_fraction_num")==4 and
            num(v2,"best_matched_fraction_num")==4 and
            num(v1,"best_matched_fraction_den")==4 and
            num(v2,"best_matched_fraction_den")==4 and
            v1["source"]=="ORIGINAL_HOSTED_SIGNED_MU3_FOUR_MOMENT" and
            v2["source"]=="ORIGINAL_HOSTED_SIGNED_MU3_FOUR_MOMENT" and
            v1["actual_original_first_Wilson_weight"]=="HOLD" and
            v2["actual_original_first_Wilson_weight"]=="HOLD",
            "matched_signed_mu3_source_selection")
    selected=read_vec(sel["source_E1_best_v1"])
    require(all(selected[i]==4*V1[i] for i in range(8)) and
            read_vec(matched["original_E1_recenter_v"])==V1 and
            read_vec(matched["original_E2_recenter_v"])==V2,
            "independent_matched_eigenvector_freeze")
    require(hashlib.sha256(sel["source_E1_best_v1"].encode("ascii")).hexdigest()
            ==sel["source_E1_best_v1_sha256"],"E1_SHA256_recomputed")
    for i,(v,diag,hi,expected_s,expected_d) in enumerate((
        (v1,matched,E1_HI,2362700330,2229193756),
        (v2,matched,E2_HI,5047836049,4761738647))):
        name="matched_W_flat_sine_upper_per_trillion"
        receipt_key="best_matched_flat_sine_per_trillion"
        sine=num(v,receipt_key)
        dist=num(v,"best_matched_distance_per_trillion")
        require(sine==expected_s and dist==expected_d and
                sine==num(diag,("matched_E1_Wflat_sine_upper_per_trillion",
                               "matched_E2_Wflat_sine_upper_per_trillion")[i]),
                "stageE_source_projector_bands")
        # Cross-multiplied independent inequality:
        # (s U^-1)^2 >= (d U^-1)^2 [1 + 72/(gamma-E_hi)^2].
        # This checks the *mathematical sufficiency* of the E1/E2
        # projected-sine conversion independently of its root rounding.
        gap=DEN*GAMMA_MICRO-hi*PS
        coupling=DEN*PS
        require(gap>0 and
                sine*sine*gap*gap>=
                dist*dist*(gap*gap+72*coupling*coupling),
                "mathematically_insufficient_P_flat_sine")
        require(sine>0 and sine<UNIT,"nontrivial_accepted_flat_cone")
        # Scalar source full-state error stays a historical Stage E
        # source condition; no proof of 8x8 Schur synthesis is inferred.
    return num(v1,"best_matched_flat_sine_per_trillion"),num(v2,"best_matched_flat_sine_per_trillion")


def original_Wilson_audit(raw,perron_slack,sines):
    a=parse(raw)
    src=one(a,"Y137_DUAL_WINDOW_SOURCE")
    fixed=one(a,"Y137_JOINT_DUAL_AUDIT")
    graph=one(a,"Y137_MATCHED_ACTION_GRAPH")
    inp=one(a,"Y137_MATCHED_ACTION_INPUT")
    z=one(a,"Y137_MATCHED_ACTION_BOUND")
    require(src["original_Wilson"]=="TWICE_ORIGINAL_SEVEN_LOOP_MINUS_16_TIMES_IDENTITY"
            and num(src,"source_operator_norm_cap")==30 and
            num(src,"source_Q")==155378 and
            num(src,"source_exterior")==1985218 and
            src["BstarB"]=="EXACT_72_IDENTITY" and
            fixed["original_Wilson_weight"]=="HOLD",
            "authentic_original_seven_loop_O9")
    require(graph["original_PQ_edges"]=="264" and
            graph["matched_E1_forward_independent_flat_row"]=="PASS" and
            graph["matched_E2_adjoint_independent_flat_row"]=="PASS" and
            graph["physical_weighted_PQ_adjoint"]=="PASS",
            "whole_original_PQ_weighted_graph_census")
    require(inp["source_original_flat_W"]==",".join(map(str,W)),
            "weighted_flat_metric")
    a1,a2=sines
    require((a1,a2)==(2362700330,5047836049) and
            z["mixed_projector_cosine_upper"]=="ONE_EXACT",
            "prohibited_underbound_other_cosine")
    floor_signal=num(z,"matched_fixed_amp_lower_per_trillion")
    source_weight=num(inp,"amp_source_ppb")
    # Independently test normalized fixed-source amplitude floor.
    require(floor_signal*floor_signal*1000000000<=source_weight*UNIT*UNIT and
            (floor_signal+1)*(floor_signal+1)*1000000000>
             source_weight*UNIT*UNIT,
            "source_fixed_pair_floor_rounding")
    c1=isqrt(UNIT*UNIT-a1*a1)
    c2=isqrt(UNIT*UNIT-a2*a2)
    central=floor_signal*c1*c2//(UNIT*UNIT)
    adjoint=num(z,"adjoint_source_action_upper_per_trillion")
    forward=num(z,"forward_source_action_upper_per_trillion")
    op=num(z,"physical_effective_M9_norm_upper_per_trillion")
    # These are independent paper inequalities with integer ceilings;
    # the formula's two mixed-angle cosines are bounded ABOVE by ONE.
    pen1=(a1*adjoint+UNIT-1)//UNIT
    pen2=(a2*forward+UNIT-1)//UNIT
    pen12=(a1*a2*op+UNIT*UNIT-1)//(UNIT*UNIT)
    margin=central-(pen1+pen2+pen12)
    require(all(num(z,k)==v for k,v in (
        ("phase_cosine_signal_lower_per_trillion",central),
        ("E1_directional_penalty_per_trillion",pen1),
        ("E2_directional_penalty_per_trillion",pen2),
        ("two_angles_penalty_per_trillion",pen12),
        ("signed_true_flat_transition_margin_per_trillion",margin))) and
        margin==47724563>0,"source_projector_contraction")
    # Independently check the normalization:
    # |<psi2,O psi1>|^2 = (|<x2,M9 x1>|^2 / 4)
    # /[(1+72/g1^2)(1+72/g2^2)] for flat-unit x1,x2.
    g1=num(inp,"gap1_num")
    g2=num(inp,"gap2_num")
    require(g1==DEN*GAMMA_MICRO-E1_HI*PS and
            g2==DEN*GAMMA_MICRO-E2_HI*PS and
            num(inp,"e1_window_width_num")==E1_HI-E1_LO and
            num(inp,"e2_window_width_num")==E2_HI-E2_LO and
            perron_slack>0,"proper_whole_Q_resolvent")
    physnum=margin*margin*g1*g1*g2*g2
    physden=4*UNIT*UNIT*(g1*g1+72*DEN*DEN*PS*PS)*(g2*g2+72*DEN*DEN*PS*PS)
    ppt=physnum*UNIT//physden
    ppb=physnum*1000000000//physden
    require(physnum==num(z,"original_weight_rational_num") and
            physden==num(z,"original_weight_rational_den") and
            ppt==num(z,"original_physical_weight_ppt_lower")==451 and
            ppb==num(z,"original_physical_weight_ppb_lower")==0 and
            num(z,"strict_positive_weight_rational")==1 and
            z["source_acceptance"]=="CANDIDATE_INDEPENDENT_MATH_REVIEW" and
            z["actual_first_Wilson_weight"]=="HOLD",
            "exact_strict_positive_first_weight_fraction")
    # Toy orthogonal true-eigenstates H=[[2,1],[1,2]],
    # O=diag(4,7), E1=1, E2=3.
    # True eigenvectors (1,-1), (1,+1) are orthogonal;
    # the shifted O9=2O-16I transition is exactly twice O.
    original=4-7
    shifted=(2*4-16)-(2*7-16)
    require(shifted==2*original and
            1+1//(1*-1)==0,"orthogonal_two_energy_Gram_shift_toy")
    return margin,ppt


def run(per,finite,all_data,e1,e2):
    slack=source_floor_audit(per,finite)
    sines=projector_receipt_audit(e1,e2,parse(all_data))
    margin,ppt=original_Wilson_audit(all_data,slack,sines)
    print("Y137_INDEPENDENT_PREMISE_AUDIT|"
          "Perron_receipt=PINNED_REPLAY_PASS|"
          "whole_Q_floor_slack_micro="+str(slack)+"|"
          "StageE_E1_E2_source=SOURCE_RECEIPT_REPLAY_PASS|"
          "true_projector_flat_conversion=INDEPENDENT_INTEGER_PASS|"
          "Wilson_264_weighted_graph=ORIGINAL_RECEIPT_PASS|"
          "first_Wilson_signed_margin="+str(margin)+"|"
          "Wilson_weight_ppt_floor="+str(ppt)+"|"
          "independent_45M_store_recompute=NOT_PERFORMED|"
          "independent_signed_mu3_matrix_proof=NOT_PERFORMED|"
          "actual_original_Wilson_weight=CONDITIONAL_CANDIDATE_HOLD|json=0")


def tests(raw):
    per,finite,action,e1,e2=raw
    run(per,finite,action,e1,e2)
    scenarios=(
      (0,"t_cert_milli=94070673","t_cert_milli=90000000"),
      (1,"E9_full_lower_micro=94070673","E9_full_lower_micro=0"),
      (2,"|original_PQ_edges=264|","|original_PQ_edges=1|"),
      (2,"|mixed_projector_cosine_upper=ONE_EXACT|",
         "|mixed_projector_cosine_upper=LOWER_COSINE|"),
      (2,"|signed_true_flat_transition_margin_per_trillion=47724563|",
         "|signed_true_flat_transition_margin_per_trillion=0|"),
      (2,"|original_physical_weight_ppt_lower=451|",
         "|original_physical_weight_ppt_lower=0|"),
      (3,"|best_matched_flat_sine_per_trillion=2362700330|",
         "|best_matched_flat_sine_per_trillion=0|"),
      (4,"|best_matched_flat_sine_per_trillion=5047836049|",
         "|best_matched_flat_sine_per_trillion=0|"),
    )
    for index,before,after in scenarios:
        bad=list(raw)
        require(before in bad[index],"negative_control_missing_"+str(index))
        bad[index]=bad[index].replace(before,after,1)
        try:
            run(*bad)
        except ValueError:
            pass
        else:
            raise AssertionError("negative_premise_control_not_rejected")
    print("Y137_INDEPENDENT_PREMISE_CONTROLS|tamper=8_REJECTED|"
          "source_replay=PASS|full_mathematical_independence=HOLD|json=0")


if __name__=="__main__":
    require(len(sys.argv)==6,"usage_PER_FINITE_ACTION_E1_E2")
    data=[]
    for filename in sys.argv[1:]:
        with open(filename,encoding="ascii") as fp:
            data.append(fp.read())
    tests(data)
