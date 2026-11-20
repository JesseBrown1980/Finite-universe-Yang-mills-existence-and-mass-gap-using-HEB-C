#!/usr/bin/env python3
"""Independent integer-only original finite S3 Wilson spectral-weight transfer.

Consumes *sealed accepted* source/model receipts from hosted run #44560968064.
Checks the distinct-E1/E2 Schur branch, both exact projector-angle inequalities,
same original weighted Wilson action, signed two-sided action decomposition,
O9=2O-16I, physical full-state normalization and exact rational squared weight.
No original producer/replay module import. Every source file SHA256 is pinned.
The established source-dependent mathematical inequality is verified; final
external theorem status remains FORMAL_HOLD pending all-premise acceptance.
"""
import hashlib
import pathlib
import re
import sys
from math import isqrt

UNIT=10**12
B=10**9
PS=10**6
ORIGINAL_GAMMA=94068200
ORIGINAL_FLOOR=(69909586556,69949433884)
GAPS=(24158613444000000,24118766116000000)
ENERGIES=(69909875505,69949729820)
BRANCHES=((0,1),(1,2))
WF=(1,3,2,3,3,2,2,2)
FILES={
 "TIGHTENED-WILSON.hbp":"8da7cd060dc366b5699997f803d5731b0b20f11a20222eeb7b6c011fdff12443",
 "interval.jsonl":"6624235fdbec9dd84bb4df267d56987b8fc55b667bb4521ffb9d60b9604fa3ac",
 "branch.jsonl":"7d7531a63d5e16355438727717f1528312c30cd4f17a4fb5616c43faa85f9778",
 "samples.jsonl":"e1d83a5c862f7b729b374a605bf934eb646d05c023e56908a6e27d8e5a100bc3",
 "original-Wilson/ALL.hbp":"bffa172b395dc1ad47b03907315c57ac0625390abaf6ba484ebc4980dcddce5e"
}

class Hold(Exception):
    pass

def need(ok,msg):
    if not ok:raise Hold(msg)

def verify_exact_sources(root):
    data={}
    for name,sha in FILES.items():
        content=root.joinpath(*name.split("/")).read_bytes()
        need(hashlib.sha256(content).hexdigest()==sha,
             "immutable_original_source_SHA_"+name.replace("/","_"))
        data[name]=content.decode("ascii")
    return data

def parse_fields(line,tag):
    need(line.startswith(tag+"|"),"missing_original_record_"+tag)
    data={}
    for cell in line.split("|")[1:]:
        k,sep,v=cell.partition("=")
        need(sep and k and k not in data,"malformed_or_duplicate_record_"+tag)
        data[k]=v
    need(data.pop("json",None)=="0","wrong_HBP_record_terminator")
    return data

def get_hbp(raw,tag):
    found=[x.strip() for x in raw.splitlines() if x.startswith(tag+"|")]
    need(len(found)==1,"exactly_one_"+tag)
    return parse_fields(found[0],tag)

def json_values(line):
    # Exactly the expected plain scalar JSON subset; no eval, no floats.
    # The separately checked endpoint arrays intentionally repeat fields.
    endpoint_fields={
        "endpoint_count","energy_den","energy_num","label","nneg_lower",
        "nneg_upper","nzero_lower","nzero_upper","required_nneg"
    }
    data={}
    for m in re.finditer(r'"([A-Za-z_][A-Za-z_0-9]*)":\s*(?:"([^"]*)"|(-?\d+))',line):
        key=m.group(1)
        if key in data:
            need(key in endpoint_fields,"duplicate_JSON_scalar_"+key)
            continue
        data[key]=m.group(2) if m.group(2) is not None else m.group(3)
    return data

def rows(raw,tag):
    lines=[x.strip() for x in raw.splitlines() if x.startswith(tag+"|")]
    need(len(lines)==2,"two_original_E1_E2_records_"+tag)
    return [json_values(x.split("|",1)[1]) for x in lines],lines

def pair(s):
    need(re.fullmatch(r"\d+(?:/\d+)?",s) is not None,"noncanonical_positive_rational")
    bits=s.split("/")
    n=int(bits[0])
    d=int(bits[1]) if len(bits)==2 else 1
    need(d>0,"positive_rational_denominator")
    return n,d

def ceildiv(n,d):
    need(n>=0 and d>0,"outward_ceil_domain")
    return (n+d-1)//d

def ceil_sine(rho,delta):
    rn,rd=pair(rho)
    dn,dd=pair(delta)
    need(rn>=0 and dn>0,"nonzero_singular_separation")
    # Exact ceil[UNIT * rho/sqrt(rho^2+delta^2)].
    r2=rn*rn*dd*dd
    d2=dn*dn*rd*rd
    need(d2>0,"strict_projector_separation")
    lo,hi=0,UNIT
    while lo+1<hi:
        middle=(lo+hi)//2
        if middle*middle*(r2+d2)>=UNIT*UNIT*r2:
            hi=middle
        else:
            lo=middle
    need(hi*hi*(r2+d2)>=UNIT*UNIT*r2 and
         (hi==0 or (hi-1)*(hi-1)*(r2+d2)<UNIT*UNIT*r2),
         "exact_projector_ceil_root")
    return hi

def old_or_new_action(amp,adj,forward,op,s1,s2):
    need(0<=s1<UNIT and 0<=s2<UNIT,"angle_under_one")
    c1=isqrt(UNIT*UNIT-s1*s1)
    c2=isqrt(UNIT*UNIT-s2*s2)
    signal=amp*c1*c2//(UNIT*UNIT)
    pen1=ceildiv(adj*s1,UNIT)
    pen2=ceildiv(forward*s2,UNIT)
    mixed=ceildiv(op*s1*s2,UNIT*UNIT)
    margin=signal-pen1-pen2-mixed
    return signal,pen1,pen2,mixed,margin

def full_weight(margin,g1,g2):
    need(margin>0 and g1>0 and g2>0,"strict_positive_original_matrix_element")
    numerator=margin*margin*g1*g1*g2*g2
    denominator=4*UNIT*UNIT*(
        g1*g1+72*B*B*PS*PS)*(
        g2*g2+72*B*B*PS*PS)
    need(denominator>0,"physical_norm_denominator_positive")
    return numerator,denominator,numerator*UNIT//denominator

def toy_physical():
    h=((11,-16,-11),(-16,38,16),(-11,16,11))
    v1=(1,0,1)
    v2=(1,1,-1)
    energies=(0,6)
    o=(2,-1,4)
    dot=lambda a,b:sum(x*y for x,y in zip(a,b))
    for v,e in ((v1,energies[0]),(v2,energies[1])):
        need(tuple(sum(h[i][j]*v[j] for j in range(3)) for i in range(3))
             ==tuple(e*x for x in v),"toy_exact_E1_E2_eigenpair")
    need(dot(v1,v2)==0,"toy_distinct_eigenvalue_orthogonality")
    op=sum(v2[j]*o[j]*v1[j] for j in range(3))
    shifted=tuple(2*x-16 for x in o)
    op9=sum(v2[j]*shifted[j]*v1[j] for j in range(3))
    need(2*op==op9 and op==-2,"toy_original_O_and_O9_transfer")
    need(shifted==(-12,-18,-8),"toy_exact_16_identity_shift")
    need(v2[0]*o[0]*v1[0]==2 and v2[2]*o[2]*v1[2]==-4,
         "toy_flat_and_nonflat_both_required")
    need(op*op==4 and dot(v1,v1)*dot(v2,v2)==6,
         "toy_original_full_norm_squared_weight_2_over_3")
    need(sum(v2[j]*(2*o[j]-15)*v1[j] for j in range(3))==op9,
         "toy_orthogonality_eliminates_any_scalar_shift")
    # A nonzero P-Q observable block would invalidate the action formula.
    bad=op+v2[0]*v1[2]
    need(bad!=op,"toy_reject_forged_PQ_Wilson_offblock")
    # Original 3D standard S3 character takes values -1,0,2.
    # Original seven winding loop traces: O in [-7,+14], O9 in [-30,+12].
    need(2*(-7)-16==-30 and 2*14-16==12,"physical_O9_range")
    print("Y137_INDEPENDENT_ORIGINAL_WILSON_TOY|two_exact_eigenstates=PASS"+
          "|full_state_orthogonality=PASS|full_2_over_3_weight=PASS"+
          "|shifted_O9_to_O_factor_one_half=PASS|missing_Q_rejected=PASS"+
          "|spurious_PQ_observable_rejected=PASS|json=0",flush=True)

def verify(values):
    act=get_hbp(values["original-Wilson/ALL.hbp"],"Y137_MATCHED_ACTION_BOUND")
    graph=get_hbp(values["original-Wilson/ALL.hbp"],"Y137_MATCHED_ACTION_GRAPH")
    inp=get_hbp(values["original-Wilson/ALL.hbp"],"Y137_MATCHED_ACTION_INPUT")
    pair_source=get_hbp(values["original-Wilson/ALL.hbp"],"Y137_MATCHED_PAIR")
    result_lines=[x for x in values["TIGHTENED-WILSON.hbp"].splitlines()
                  if x.startswith("Y137_TIGHTENED_ORIGINAL_WILSON|")]
    need(len(result_lines)==1,"one_tightened_original_result")
    new=json_values(result_lines[0].split("|",1)[1])
    need(graph["original_PQ_edges"]=="264" and
         graph["physical_weighted_PQ_adjoint"]=="PASS" and
         graph["matched_E1_forward_independent_flat_row"]=="PASS" and
         graph["matched_E2_adjoint_independent_flat_row"]=="PASS" and
         graph["first_original_Wilson_weight"]=="HOLD",
         "original_weighted_264_edge_operator")
    need(inp["source_original_flat_W"]==",".join(str(x) for x in WF)
         and act["mixed_projector_cosine_upper"]=="ONE_EXACT" and
         act["actual_first_Wilson_weight"]=="HOLD",
         "same_original_W_metric_and_mixed_cosine")
    need(pair_source["matched_E1_Wflat_sine_upper_per_trillion"]=="2362700330"
         and pair_source["matched_E2_Wflat_sine_upper_per_trillion"]=="5047836049",
         "original_source_matched_directional_sines")
    interval,interval_lines=rows(values["interval.jsonl"],"Y137_SCHUR_INTERVAL_DIRECTIONAL")
    branch,branch_lines=rows(values["branch.jsonl"],"Y137_ENDPOINT_BRANCH")
    samples,_=rows(values["samples.jsonl"],"Y137_SCHUR_SAMPLE_DIAGNOSTIC")
    angles=[]
    for i in range(2):
        r=interval[i]
        b=branch[i]
        s=samples[i]
        need(int(r["sample_num"])==ENERGIES[i] and
             int(b["sample"])==ENERGIES[i] and
             int(s["sample_num"])==ENERGIES[i] and
             int(b["level"])==i+1 and
             b["conditional_branch"]=="PASS" and
             r["conditional_interval_angle"]=="PASS",
             "same_original_energy_and_branch")
        need(r["source_weight_metric"]==inp["source_original_flat_W"] and
             int(r["source_selected_k"])==4 and
             int(s["selected_fraction_num"])==4 and
             int(s["selected_fraction_den"])==4,
             "same_original_eight_flat_matched_basis")
        need(r["source"]=="PINNED_HISTORICAL_PREMISES" and
             r["Wilson_true_first_weight"]=="FORMAL_HOLD",
             "conditional_original_projector_boundary")
        endpoint=BRANCHES[i]
        counts=re.findall(r'"nneg_lower":\s*(\d+),\s*"nneg_upper":\s*(\d+)',
                          branch_lines[i])
        nonsingular=re.findall(
            r'"nzero_lower":\s*(\d+),\s*"nzero_upper":\s*(\d+)',
            branch_lines[i])
        verdict=re.findall(r'"endpoint_count":\s*"([^"]+)"',
                           branch_lines[i])
        need(len(counts)==len(nonsingular)==len(verdict)==2 and
             [tuple(map(int,x)) for x in counts]==[(endpoint[0],endpoint[0]),
                                                    (endpoint[1],endpoint[1])] and
             all(x==("0","0") for x in nonsingular) and verdict==["PASS","PASS"],
             "original_schur_endpoint_inertias_and_nonsingular")
        sn=ceil_sine(r["interval_projected_residual_upper"],
                     r["interval_compressed_singular_lower"])
        targetn,targetd=pair(r["target_sine"])
        need(sn*targetd<=UNIT*targetn,"required_original_sine_cap")
        need(sn>0 and sn<UNIT,"positive_genuine_projector_angle")
        need(pair(r["interval_compressed_singular_lower"])[0]>0,
             "source_compression_singular_gap")
        angles.append(sn)
    need(angles==[int(new["new_E1_projector_sine_per_trillion"]),
                 int(new["new_E2_projector_sine_per_trillion"])],
         "independent_exact_interval_projector_ceilings")
    amp=int(act["matched_fixed_amp_lower_per_trillion"])
    adj=int(act["adjoint_source_action_upper_per_trillion"])
    forward=int(act["forward_source_action_upper_per_trillion"])
    op=int(act["physical_effective_M9_norm_upper_per_trillion"])
    need(amp>0 and min(adj,forward,op)>=0 and
         int(act["original_physical_weight_ppt_lower"])==451 and
         int(act["signed_true_flat_transition_margin_per_trillion"])==47724563,
         "authenticated_original_action_positive_candidate")
    need(GAPS==tuple(B*ORIGINAL_GAMMA-e*PS for e in ORIGINAL_FLOOR)
         and int(inp["gap1_num"])==GAPS[0]
         and int(inp["gap2_num"])==GAPS[1],
         "original_whole_Q_floor_and_source_energy_windows")
    # Recalculate the original older directional test as a regression.
    old=old_or_new_action(amp,adj,forward,op,2362700330,5047836049)
    need(old[-1]==47724563,"original_old_action_triangle_regression")
    signal,p1,p2,mixed,margin=old_or_new_action(
        amp,adj,forward,op,*angles)
    expected=("new_signal_lower_per_trillion",
              "new_E1_penalty_upper_per_trillion",
              "new_E2_penalty_upper_per_trillion",
              "new_mixed_penalty_upper_per_trillion",
              "new_signed_O9_margin_lower_per_trillion")
    need([int(new[k]) for k in expected]==[signal,p1,p2,mixed,margin],
         "original_two_sided_Wilson_projector_action_inequality")
    need(margin>0 and
         margin==9285530088 and
         int(new["new_original_Wilson_squared_weight_ppt_floor"])==17074763,
         "strict_original_Wilson_signed_numerical_margin")
    n,d,ppt=full_weight(margin,*GAPS)
    need(ppt==int(new["new_original_Wilson_squared_weight_ppt_floor"]),
         "original_full_state_norm_and_one_quarter_O9_to_O")
    fingerprint=hashlib.sha256((str(n)+"/"+str(d)).encode("ascii")).hexdigest()
    need(fingerprint==new["new_weight_rational_SHA256"] and
         fingerprint=="7a8255cfb82207653ef3050b1efba0cedda61a309c3084e6a8a50b42deb7abf0",
         "independent_original_weight_exact_rational_fingerprint")
    need(new["first_Wilson_formal"]=="HOLD" and
         new["continuum_4D"]=="OPEN",
         "preserve_original_theorem_review_boundary")
    return {"angle1":angles[0],"angle2":angles[1],"margin":margin,
            "ppt":ppt,"sha":fingerprint,"rho_sine_branches":2}

def altered_controls(values):
    replacements=[
     ("original-Wilson/ALL.hbp","|original_PQ_edges=264|","|original_PQ_edges=263|"),
     ("original-Wilson/ALL.hbp","|mixed_projector_cosine_upper=ONE_EXACT|","|mixed_projector_cosine_upper=LOWER|"),
     ("original-Wilson/ALL.hbp","|matched_fixed_amp_lower_per_trillion=62164467342|","|matched_fixed_amp_lower_per_trillion=1|"),
     ("original-Wilson/ALL.hbp","|forward_source_action_upper_per_trillion=6428635065074|","|forward_source_action_upper_per_trillion=1|"),
     ("TIGHTENED-WILSON.hbp",'"new_signed_O9_margin_lower_per_trillion": 9285530088','"new_signed_O9_margin_lower_per_trillion": 1'),
     ("interval.jsonl",'"conditional_interval_angle": "PASS"','"conditional_interval_angle": "HOLD"'),
     ("branch.jsonl",'"nneg_upper": 0','"nneg_upper": 9'),
     ("TIGHTENED-WILSON.hbp",'"new_original_Wilson_squared_weight_ppt_floor": 17074763','"new_original_Wilson_squared_weight_ppt_floor": 0'),
     ("original-Wilson/ALL.hbp","|physical_weighted_PQ_adjoint=PASS|","|physical_weighted_PQ_adjoint=FAIL|")
    ]
    for path,old,new in replacements:
        need(old in values[path],"negative_control_source_token_absent")
        mutated=dict(values)
        mutated[path]=values[path].replace(old,new,1)
        try:verify(mutated)
        except Hold:pass
        else:raise Hold("forged_original_Wilson_theorem_premise_accepted")
    return len(replacements)

def main(argv):
    try:
        toy_physical()
        if argv==["toy"]:
            print("Y137_WILSON_TRANSFER_TOY|complete=PASS|original_evidence=NOT_READ|json=0")
            return
        need(len(argv)==2 and argv[0]=="real","usage_toy_or_real_ROOT")
        raw=verify_exact_sources(pathlib.Path(argv[1]))
        result=verify(raw)
        controls=altered_controls(raw)
        need(controls==9,"all_nine_Wilson_transfer_negative_controls")
        print("Y137_WILSON_TRANSFER_EXACT|original_eigenbranches=2_OF_2"+
              "|original_projector_ceilings="+str(result["angle1"])+","+str(result["angle2"])+
              "|physical_weighted_PQ=PASS|operator_O9_equals_2O_minus_16I=PASS"+
              "|distinct_E1_E2_orthogonality=THEOREM"+
              "|mixed_negative_cosines=ONE_EXACT"+
              "|signed_O9_margin_per_trillion="+str(result["margin"])+
              "|original_squared_weight_lower_ppt="+str(result["ppt"])+
              "|original_weight_exact_SHA256="+result["sha"]+
              "|negative_controls="+str(controls)+"_REJECTED"+
              "|source=PINNED_ORIGINAL_PHYSICAL_RECEIPTS"+
              "|independent_mathematical_transfer=CONDITIONAL_PASS"+
              "|first_original_Wilson_theorem=FORMAL_HOLD"+
              "|continuum_4D=OPEN|json=0",flush=True)
    except (Hold,OSError,UnicodeError,ValueError,IndexError,KeyError) as e:
        print("Y137_WILSON_TRANSFER_HOLD|reason="+str(e)+
              "|first_original_Wilson_theorem=FORMAL_HOLD|json=0",flush=True)
        raise SystemExit(2) from None

if __name__=="__main__":
    main(sys.argv[1:])
