#!/usr/bin/env python3
"""Independent pure-integer Wilson improvement from original matched action
and source-conditional E1/E2 projector-angle receipts.

Consumes *unchanged* archived original #315 matched same-Q Wilson source,
source-conditional #319 true E1/E2 branch/angle receipts, and the frozen
sample directions. No original producer modules are imported.
Original physical full-Q/whole Perron provenance and mathematical acceptance
remain FORMAL HOLD.
"""
import copy
import hashlib
import json
import os
import sys
from fractions import Fraction as F
from math import isqrt

sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import replay_interval as checks

U=10**12
B=10**9
PS=10**6
E1V=(1000000000,997998757,997000845,39006811,38860510,2944164,80455,80455)
E2V=(112491544,-39124838,-114340075,1000000000,978089453,221700078,5301152,5301152)
ORIGINAL_S=(2362700330,5047836049)
GAPS=(24158613444000000,24118766116000000)

def need(ok,msg):
    if not ok:raise ValueError(msg)
def num(x):
    a=int(x);need(str(a)==x,"noncanonical_integer")
    return a
def ceildiv(n,d):
    need(d>0 and n>=0,"positive_integer_division")
    return (n+d-1)//d
def fields(raw):
    kept={}
    tags=("Y137_MATCHED_ACTION_BOUND","Y137_MATCHED_ACTION_INPUT",
          "Y137_MATCHED_PAIR","Y137_MATCHED_ACTION_GRAPH")
    for line in raw.splitlines():
        name=line.split("|",1)[0]
        if name not in tags:continue
        need(name not in kept,"duplicate_source_record")
        row={}
        for part in line.split("|")[1:]:
            k,sep,v=part.partition("=")
            need(k and sep and k not in row,"invalid_source_key")
            row[k]=v
        need(row.pop("json",None)=="0","invalid_source_terminator")
        kept[name]=row
    need(set(kept)==set(tags),"missing_original_matched_action_source")
    return kept

def ceil_sine(rho,delta):
    need(rho>=0 and delta>0,"angular_certificate_domain")
    target=rho*rho/(rho*rho+delta*delta)
    lo,hi=0,U
    while lo+1<hi:
        m=(lo+hi)//2
        if F(m*m,U*U)<target:lo=m
        else:hi=m
    need(F(hi*hi,U*U)>=target and
         (hi==0 or F((hi-1)**2,U*U)<target),
         "strict_integer_angular_root_bracket")
    return hi

def action(amp,adj,forw,op,s1,s2):
    need(0<=s1<U and 0<=s2<U,"sine_domain")
    c1=isqrt(U*U-s1*s1);c2=isqrt(U*U-s2*s2)
    signal=amp*c1*c2//(U*U)
    p1=ceildiv(s1*adj,U)
    p2=ceildiv(s2*forw,U)
    cross=ceildiv(s1*s2*op,U*U)
    return (signal-p1-p2-cross,signal,p1,p2,cross)

def physical(margin):
    g1,g2=GAPS
    numerator=margin*margin*g1*g1*g2*g2
    denominator=4*U*U*(g1*g1+72*B*B*PS*PS)*(g2*g2+72*B*B*PS*PS)
    return numerator,denominator,numerator*U//denominator,numerator*B//denominator

def verify(raw,intervals,branches,samples):
    src=fields(raw)
    pair=src["Y137_MATCHED_PAIR"]
    inp=src["Y137_MATCHED_ACTION_INPUT"]
    bound=src["Y137_MATCHED_ACTION_BOUND"]
    graph=src["Y137_MATCHED_ACTION_GRAPH"]
    need(tuple(map(int,pair["original_E1_recenter_v"].split(",")))==E1V and
         tuple(map(int,pair["original_E2_recenter_v"].split(",")))==E2V,
         "original_same_Q_matched_vector_pins")
    need(num(pair["matched_E1_Wflat_sine_upper_per_trillion"])==ORIGINAL_S[0] and
         num(pair["matched_E2_Wflat_sine_upper_per_trillion"])==ORIGINAL_S[1],
         "original_matched_sine_source")
    need(inp["source_original_flat_W"]=="1,3,2,3,3,2,2,2" and
         graph["original_PQ_edges"]=="264" and
         graph["matched_E1_forward_independent_flat_row"]=="PASS" and
         graph["matched_E2_adjoint_independent_flat_row"]=="PASS" and
         graph["physical_weighted_PQ_adjoint"]=="PASS",
         "original_weighted_Wilson_graph")
    need(num(inp["gap1_num"])==GAPS[0] and num(inp["gap2_num"])==GAPS[1] and
         num(inp["e1_window_width_num"])==157135 and
         num(inp["e2_window_width_num"])==169737,
         "original_Q_floor_and_energy_windows")
    amp=num(bound["matched_fixed_amp_lower_per_trillion"])
    adj=num(bound["adjoint_source_action_upper_per_trillion"])
    forw=num(bound["forward_source_action_upper_per_trillion"])
    op=num(bound["physical_effective_M9_norm_upper_per_trillion"])
    need(amp==62164467342 and adj==12385435982884 and
         forw==6428635065074 and op==33707034776107,
         "frozen_source_action_coefficients")
    need(bound["mixed_projector_cosine_upper"]=="ONE_EXACT" and
         bound["actual_first_Wilson_weight"]=="HOLD",
         "original_source_review_boundary")
    old=action(amp,adj,forw,op,*ORIGINAL_S)
    need(old[0]==47724563 and
         all(num(bound[k])==v for k,v in zip((
             "signed_true_flat_transition_margin_per_trillion",
             "phase_cosine_signal_lower_per_trillion",
             "E1_directional_penalty_per_trillion",
             "E2_directional_penalty_per_trillion",
             "two_angles_penalty_per_trillion"),old)),
         "historical_positive_451ppt_replay")
    oldnum,oldden,oldppt,oldppb=physical(old[0])
    need(oldnum==num(bound["original_weight_rational_num"]) and
         oldden==num(bound["original_weight_rational_den"]) and
         oldppt==num(bound["original_physical_weight_ppt_lower"])==451 and
         oldppb==num(bound["original_physical_weight_ppb_lower"])==0,
         "historical_Wilson_normalization")
    need(len(intervals)==len(branches)==len(samples)==2,"two_original_true_eigenstates")
    tightened=[]
    for i in range(2):
        checks.test_one(i,intervals[i],branches[i])
        sample=samples[i]
        need(sample.get("sample_num")==checks.SAMPLES[i] and
             sample.get("source_selected_k","MISSING")==4 if False else True,
             "source_sample") # selected fraction checked explicitly below
        need(sample.get("sample_num")==checks.SAMPLES[i] and
             sample.get("selected_fraction_num")==4 and
             sample.get("selected_fraction_den")==4,"sample_matched_k4")
        v=tuple(map(int,sample["source_matched_direction"].split(",")))
        need(v==tuple(4*t for t in (E1V,E2V)[i]),
             "same_original_eigenvector_as_Wilson_action")
        rho=checks.frac(intervals[i]["interval_projected_residual_upper"])
        delta=checks.frac(intervals[i]["interval_compressed_singular_lower"])
        s=ceil_sine(rho,delta)
        need(s<ORIGINAL_S[i],"new_projector_bound_improves_original")
        tightened.append(s)
    new=action(amp,adj,forw,op,*tightened)
    n,d,ppt,ppb=physical(new[0])
    need(new[0]>old[0] and ppt>oldppt and n>0,
         "strict_source_conditional_improvement")
    digest=hashlib.sha256((str(n)+"/"+str(d)).encode("ascii")).hexdigest()
    return {"source":"IMMUTABLE_ORIGINAL_MATCHED_WILSON_ACTION",
            "original_old_margin":old[0],
            "original_old_weight_ppt_floor":oldppt,
            "new_E1_projector_sine_per_trillion":tightened[0],
            "new_E2_projector_sine_per_trillion":tightened[1],
            "new_signal_lower_per_trillion":new[1],
            "new_E1_penalty_upper_per_trillion":new[2],
            "new_E2_penalty_upper_per_trillion":new[3],
            "new_mixed_penalty_upper_per_trillion":new[4],
            "new_signed_O9_margin_lower_per_trillion":new[0],
            "new_original_Wilson_squared_weight_ppt_floor":ppt,
            "new_original_Wilson_squared_weight_ppb_floor":ppb,
            "new_weight_rational_SHA256":digest,
            "same_original_8flat_witnesses":"PASS",
            "original_source_conditional":"PASS",
            "first_Wilson_formal":"HOLD",
            "continuum_4D":"OPEN"}

def negatives(raw,intervals,branches,samples):
    def reject(r,irs,bs,ss):
        try:verify(r,irs,bs,ss)
        except (ValueError,KeyError,IndexError,ZeroDivisionError,TypeError):return
        raise ValueError("forged_Wilson_positivity_receipt_accepted")
    tests=[]
    def alter(a,b):
        need(a in raw,"negative_source_key_missing")
        tests.append((raw.replace(a,b,1),copy.deepcopy(intervals),copy.deepcopy(branches),copy.deepcopy(samples)))
    alter("|original_PQ_edges=264|","|original_PQ_edges=1|")
    alter("|signed_true_flat_transition_margin_per_trillion=47724563|",
          "|signed_true_flat_transition_margin_per_trillion=1|")
    alter("|matched_fixed_amp_lower_per_trillion=62164467342|",
          "|matched_fixed_amp_lower_per_trillion=1|")
    alter("|original_physical_weight_ppt_lower=451|",
          "|original_physical_weight_ppt_lower=0|")
    alter("|mixed_projector_cosine_upper=ONE_EXACT|",
          "|mixed_projector_cosine_upper=LOWER|")
    x,y,z=copy.deepcopy(intervals),copy.deepcopy(branches),copy.deepcopy(samples)
    x[0]["interval_projected_residual_upper"]="1/3";tests.append((raw,x,y,z))
    x,y,z=copy.deepcopy(intervals),copy.deepcopy(branches),copy.deepcopy(samples)
    x[1]["target_sine"]="1/100000";tests.append((raw,x,y,z))
    x,y,z=copy.deepcopy(intervals),copy.deepcopy(branches),copy.deepcopy(samples)
    y[0]["endpoints"][1]["nneg_upper"]=9;tests.append((raw,x,y,z))
    x,y,z=copy.deepcopy(intervals),copy.deepcopy(branches),copy.deepcopy(samples)
    z[1]["source_matched_direction"]="1,1,1,1,1,1,1,1";tests.append((raw,x,y,z))
    for args in tests:reject(*args)
    return len(tests)

def main():
    need(len(sys.argv)==5,
         "usage: replay_tightened_wilson.py ALL.hbp interval.jsonl branch.jsonl samples.jsonl")
    raw=open(sys.argv[1],encoding="ascii").read()
    interval=checks.read(sys.argv[2],"Y137_SCHUR_INTERVAL_DIRECTIONAL")
    branch=checks.read(sys.argv[3],"Y137_ENDPOINT_BRANCH")
    samples=checks.read(sys.argv[4],"Y137_SCHUR_SAMPLE_DIAGNOSTIC")
    result=verify(raw,interval,branch,samples)
    print("Y137_TIGHTENED_ORIGINAL_WILSON|"+json.dumps(result,sort_keys=True),flush=True)
    controls=negatives(raw,interval,branch,samples)
    need(controls==9,"negative_control_count")
    print("Y137_TIGHTENED_ORIGINAL_WILSON_VERDICT|matched_original_source=PASS"+
          "|two_true_projector_angles=SOURCE_CONDITIONAL_PASS"+
          "|strict_positive_weight=SOURCE_CONDITIONAL_PASS"+
          "|tamper_controls=9_REJECTED|formal_acceptance=HOLD"+
          "|continuum_4D=OPEN|json=0",flush=True)
if __name__=="__main__":
    try:main()
    except (ValueError,KeyError,TypeError,IndexError,ZeroDivisionError) as exc:
        print("Y137_TIGHTENED_ORIGINAL_WILSON_REFUSE|reason="+str(exc)+"|json=0",flush=True)
        raise SystemExit(2)
