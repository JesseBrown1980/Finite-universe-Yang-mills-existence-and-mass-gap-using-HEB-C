#!/usr/bin/env python3
"""Separate exact-Fraction replay of accepted original E1/E2 interval receipts.

This checks interval inequalities, source-specific Q norm transport, monotone
resolvent derivative, 8x8 width ceilings, compression drift, two endpoint
inertia transitions, and ten negative controls. No original source-generating
code is imported; source provenance remains a distinct obligation.
"""
import copy
import json
import sys
from fractions import Fraction as F

UNIT=10**12
DEN=10**9
FLOOR=94068200000
BNORM_UP=8485281374239
SAMPLES=(69909875505,69949729820)
WINDOWS=((69909429421,69909586556),(69949264147,69949433884))
TARGETS=(F(236270033,10**11),F(5047836049,10**12))
BASE_Q_UP=(259788930946,254910334285)
MOVEMENT=(949209145,3693022069)

def need(ok,reason):
    if not ok:raise ValueError(reason)

def frac(x):
    need(not isinstance(x,float) and not isinstance(x,bool),"float_or_bool_forbidden")
    return F(str(x))

def read(path,prefix):
    rows=[]
    with open(path,encoding="utf-8") as h:
        for line in h:
            line=line.strip()
            if not line.startswith(prefix+"|"):
                continue
            data=json.loads(line.split("|",1)[1],
                parse_float=lambda _: (_ for _ in ()).throw(ValueError("JSON_float_forbidden")),
                parse_constant=lambda _: (_ for _ in ()).throw(ValueError("JSON_nonfinite_forbidden")))
            need(isinstance(data,dict),"receipt_not_object")
            rows.append(data)
    need(len(rows)==2,"exact_two_receipts")
    return rows

def test_one(i,r,b):
    z=SAMPLES[i];a,h=WINDOWS[i]
    need(r.get("sample_num")==z and b.get("sample")==z and b.get("level")==i+1,
         "wrong_source_energy_or_level")
    need(r.get("source")=="PINNED_HISTORICAL_PREMISES","source_label")
    need(r.get("Wilson_true_first_weight")=="FORMAL_HOLD","Wilson_status_regression")
    need(r.get("source_weight_metric")=="1,3,2,3,3,2,2,2","original_flat_metric")
    need(frac(r["physical_S_denominator"])==F(10**33),"original_S_unit")
    need(frac(r["interval_lo"])==F(a,DEN) and frac(r["interval_hi"])==F(h,DEN),
         "original_energy_windows")
    need(r.get("source_selected_k")==4 and r.get("exact_singular_bisection_steps")==12,
         "frozen_matched_witness_or_singular_search")
    need(r.get("exact_width_spectral_bisection_steps")==14,"width_spectral_search")
    need(r.get("source_moved_flat_distance_per_trillion")==str(MOVEMENT[i]),
         "original_selected_witness_movement")
    gap=F(FLOOR-z,DEN)
    moved=MOVEMENT[i]
    spread=(BNORM_UP*moved*DEN+UNIT*(FLOOR-z)-1)//(UNIT*(FLOOR-z))
    q=F(BASE_Q_UP[i]+spread,UNIT)
    need(frac(r["source_Q_norm_upper"])==q,"moved_witness_Q_norm")
    directional_derivative=F(BNORM_UP,UNIT)*q/gap
    need(frac(r["directional_Q_derivative_upper"])==directional_derivative,
         "directional_derivative")
    drift=F(max(z-a,z-h),DEN)
    projected=directional_derivative*drift
    need(frac(r["projected_Q_drift_upper"])==projected,"projected_Q_drift")
    global_derivative=F(72)/gap**2
    need(directional_derivative<=global_derivative,"Q_derivative_weaker_than_global")
    need(frac(r["global_Q_drift_comparison"])==global_derivative*drift,
         "global_Q_drift")
    full=(1+global_derivative)*drift
    need(frac(r["full_schur_drift_upper"])==full,"full_Schur_drift")
    frob=frac(r["width_frobenius_upper"])
    width=frac(r["width_spectral_upper"])
    need(0<width<=frob+F(1,10**12),"spectral_width_bound")
    residual=frac(r["residual_mid_upper"])
    directional=frac(r["directional_width_error_upper"])
    rho=frac(r["interval_projected_residual_upper"])
    delta=frac(r["interval_compressed_singular_lower"])
    singular=frac(r["sample_compressed_singular_lower"])
    need(rho==residual+directional+projected,"exact_projected_residual_sum")
    need(delta==singular-width/2-full,"exact_compressed_gap_difference")
    target=frac(r["target_sine"])
    need(target==TARGETS[i],"original_sine_target")
    need(rho>=0 and delta>0 and 0<target<1,"positive_projector_margin_data")
    lhs=rho*rho*(1-target*target)
    rhs=target*target*delta*delta
    need(lhs<=rhs and r.get("conditional_interval_angle")=="PASS",
         "exact_projector_angle_inequality")
    need(b.get("conditional_branch")=="PASS" and len(b.get("endpoints",[]))==2,
         "two_true_branch_endpoints")
    for k,point in enumerate(b["endpoints"]):
        expected=i+k; endpoint=(a,h)[k]
        need(point.get("energy_num")==endpoint and point.get("energy_den")==DEN,
             "wrong_true_energy_endpoint")
        need(point.get("endpoint_count")=="PASS" and
             point.get("nneg_lower")==expected and
             point.get("nneg_upper")==expected and
             point.get("nzero_lower")==point.get("nzero_upper")==0,
             "endpoint_inertia_source_condition")
    return {"level":i+1,"source_sample":z,"sine_certificate":"PASS",
            "branch_endpoint":"PASS","rho_upper":str(rho),
            "delta_lower":str(delta),"squared_margin":str(rhs-lhs),
            "exact_source_condition":"PINNED_PREMISES",
            "Wilson_formal":"HOLD"}

def reject(r,b):
    try:test_one(0,r,b)
    except (ValueError,KeyError,TypeError,IndexError,ZeroDivisionError):return
    raise ValueError("forged_receipt_accepted")

def controls(r,b):
    tests=[]
    def add(mut):
        x,y=copy.deepcopy(r),copy.deepcopy(b)
        mut(x,y);tests.append((x,y))
    add(lambda x,y:x.update({"interval_projected_residual_upper":"1/2"}))
    add(lambda x,y:x.update({"interval_compressed_singular_lower":"1/10000"}))
    add(lambda x,y:x.update({"target_sine":"1/100000"}))
    add(lambda x,y:x.update({"interval_lo":"0"}))
    add(lambda x,y:x.update({"source_Q_norm_upper":"1"}))
    add(lambda x,y:x.update({"directional_Q_derivative_upper":"1"}))
    add(lambda x,y:x.update({"source":"UNVERIFIED"}))
    add(lambda x,y:x.update({"width_spectral_upper":"1"}))
    add(lambda x,y:y["endpoints"][0].update({"nneg_upper":100}))
    add(lambda x,y:y["endpoints"][1].update({"nzero_lower":1}))
    for x,y in tests:reject(x,y)
    return len(tests)

def main():
    need(len(sys.argv)==3,"usage: replay_interval.py interval.jsonl branch.jsonl")
    rs=read(sys.argv[1],"Y137_SCHUR_INTERVAL_DIRECTIONAL")
    bs=read(sys.argv[2],"Y137_ENDPOINT_BRANCH")
    for i in range(2):
        print("Y137_INDEPENDENT_INTERVAL_REPLAY|"+json.dumps(test_one(i,rs[i],bs[i]),
             sort_keys=True),flush=True)
    k=controls(rs[0],bs[0])
    need(k==10,"negative_control_count")
    print("Y137_INDEPENDENT_INTERVAL_VERDICT|two_original_projector_angles=PASS"+
          "|two_true_eigenbranches=PASS|tamper_controls=10_REJECTED"+
          "|source_evidence=PINNED_PREMISES|first_Wilson_weight=FORMAL_HOLD"+
          "|continuum_4D=OPEN|json=0",flush=True)

if __name__=="__main__":
    try:main()
    except (ValueError,KeyError,TypeError,IndexError,ZeroDivisionError) as exc:
        print("Y137_INDEPENDENT_INTERVAL_REFUSE|reason="+str(exc)+"|json=0",flush=True)
        raise SystemExit(2)
